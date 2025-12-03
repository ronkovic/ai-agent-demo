"""Workflow Engine Service - DAG実行エンジン."""

import re
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import jmespath
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import WorkflowExecutionRepository
from ..db.models import Workflow, WorkflowExecution


class WorkflowContext:
    """ワークフロー実行コンテキスト.

    ノード間でデータを受け渡すためのコンテキストオブジェクト。
    """

    def __init__(self, trigger_data: dict[str, Any] | None = None):
        """Initialize context with optional trigger data."""
        self.trigger_data = trigger_data or {}
        self._results: dict[str, Any] = {}

    def set_result(self, node_id: str, result: Any) -> None:
        """ノード実行結果を保存."""
        self._results[node_id] = result

    def get_result(self, node_id: str) -> Any:
        """ノード実行結果を取得."""
        return self._results.get(node_id)

    def to_dict(self) -> dict[str, Any]:
        """コンテキスト全体を辞書として取得（テンプレート解決用）."""
        return {
            "trigger": self.trigger_data,
            **self._results,
        }


class WorkflowEngine:
    """ワークフロー実行エンジン.

    DAGを構築し、トポロジカルソートで実行順序を決定し、
    各ノードを順次実行する。
    """

    def __init__(
        self,
        db: AsyncSession,
        execution_repo: WorkflowExecutionRepository | None = None,
    ):
        """Initialize workflow engine."""
        self.db = db
        self.execution_repo = execution_repo or WorkflowExecutionRepository()

    async def execute(
        self,
        workflow: Workflow,
        trigger_data: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """ワークフローを実行.

        Args:
            workflow: 実行するワークフロー
            trigger_data: トリガーから渡されるデータ

        Returns:
            実行結果を含むWorkflowExecution
        """
        # 1. 実行レコード作成
        execution = await self.execution_repo.create(
            self.db,
            workflow_id=workflow.id,
            trigger_data=trigger_data,
        )

        # 実行開始
        execution.status = "running"
        execution.started_at = datetime.now(UTC)
        await self.db.flush()

        context = WorkflowContext(trigger_data)

        try:
            # 2. DAG構築
            nodes = workflow.nodes or []
            edges = workflow.edges or []
            dag = self._build_dag(nodes, edges)

            # 3. トポロジカルソート
            sorted_node_ids = self._topological_sort(dag, nodes)

            # 4. ノード順次実行
            node_map = {node["id"]: node for node in nodes}
            node_results: dict[str, Any] = {}

            for node_id in sorted_node_ids:
                node = node_map.get(node_id)
                if not node:
                    continue

                try:
                    result = await self._execute_node(node, context)
                    context.set_result(node_id, result)
                    node_results[node_id] = {
                        "status": "completed",
                        "result": result,
                    }
                except Exception as e:
                    node_results[node_id] = {
                        "status": "failed",
                        "error": str(e),
                    }
                    raise

            # 5. 完了
            execution.status = "completed"
            execution.node_results = node_results
            execution.completed_at = datetime.now(UTC)

        except Exception as e:
            # エラーハンドリング
            execution.status = "failed"
            execution.node_results = context._results
            execution.error = str(e)
            execution.completed_at = datetime.now(UTC)

        return execution

    def _build_dag(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, list[str]]:
        """DAGを構築.

        Args:
            nodes: ノードリスト
            edges: エッジリスト

        Returns:
            隣接リスト形式のDAG {node_id: [依存ノードID, ...]}
        """
        dag: dict[str, list[str]] = defaultdict(list)

        # 全ノードをDAGに追加
        for node in nodes:
            if node["id"] not in dag:
                dag[node["id"]] = []

        # エッジから依存関係を構築
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                # target は source に依存
                if source not in dag[target]:
                    dag[target].append(source)

        return dict(dag)

    def _topological_sort(
        self,
        dag: dict[str, list[str]],
        nodes: list[dict[str, Any]],
    ) -> list[str]:
        """カーンのアルゴリズムでトポロジカルソート.

        Args:
            dag: 隣接リスト形式のDAG
            nodes: ノードリスト

        Returns:
            実行順序のノードIDリスト

        Raises:
            ValueError: 循環依存が検出された場合
        """
        # 入次数を計算
        in_degree: dict[str, int] = {node_id: len(deps) for node_id, deps in dag.items()}

        # 入次数0のノードをキューに追加
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result: list[str] = []

        while queue:
            # 入次数0のノードを取り出し
            current = queue.pop(0)
            result.append(current)

            # 依存しているノードの入次数を減らす
            for node_id, deps in dag.items():
                if current in deps:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)

        # 循環依存チェック
        if len(result) != len(dag):
            raise ValueError("Circular dependency detected in workflow")

        return result

    async def _execute_node(
        self,
        node: dict[str, Any],
        context: WorkflowContext,
    ) -> Any:
        """ノードを実行.

        Args:
            node: ノード定義
            context: 実行コンテキスト

        Returns:
            ノード実行結果
        """
        node_type = node.get("type")
        data = node.get("data", {})

        if node_type == "trigger":
            return await self._execute_trigger_node(data, context)
        elif node_type == "agent":
            return await self._execute_agent_node(data, context)
        elif node_type == "condition":
            return await self._execute_condition_node(data, context)
        elif node_type == "transform":
            return await self._execute_transform_node(data, context)
        elif node_type == "tool":
            return await self._execute_tool_node(data, context)
        elif node_type == "output":
            return await self._execute_output_node(data, context)
        else:
            return {"message": f"Unknown node type: {node_type}"}

    async def _execute_trigger_node(
        self,
        data: dict[str, Any],
        context: WorkflowContext,
    ) -> dict[str, Any]:
        """トリガーノード実行."""
        trigger_type = data.get("trigger_type", "manual")
        return {
            "trigger_type": trigger_type,
            "trigger_data": context.trigger_data,
        }

    async def _execute_agent_node(
        self,
        data: dict[str, Any],
        context: WorkflowContext,
    ) -> dict[str, Any]:
        """エージェントノード実行.

        Note: 実際のエージェント実行は今後実装。
        現時点ではプレースホルダー。
        """
        agent_id = data.get("agent_id")
        input_mapping = data.get("input_mapping", {})

        # 入力マッピングを解決
        resolved_inputs = {}
        for key, template in input_mapping.items():
            resolved_inputs[key] = self._resolve_template(template, context)

        # TODO: 実際のエージェント呼び出し
        return {
            "agent_id": agent_id,
            "inputs": resolved_inputs,
            "output": f"Agent {agent_id} executed (placeholder)",
        }

    async def _execute_condition_node(
        self,
        data: dict[str, Any],
        context: WorkflowContext,
    ) -> dict[str, Any]:
        """条件分岐ノード実行."""
        conditions = data.get("conditions", [])
        logic = data.get("logic", "and")

        results = []
        for condition in conditions:
            field = condition.get("field", "")
            operator = condition.get("operator", "eq")
            value = condition.get("value")

            # フィールド値を取得
            field_value = self._resolve_template(f"{{{{{field}}}}}", context)

            # 条件評価
            result = self._evaluate_condition(field_value, operator, value)
            results.append(result)

        # ロジックに基づいて最終結果を決定
        if logic == "and":
            final_result = all(results) if results else True
        else:  # or
            final_result = any(results) if results else False

        return {
            "result": final_result,
            "conditions_evaluated": results,
        }

    def _evaluate_condition(
        self,
        field_value: Any,
        operator: str,
        compare_value: Any,
    ) -> bool:
        """条件を評価."""
        if operator == "eq":
            return field_value == compare_value
        elif operator == "ne":
            return field_value != compare_value
        elif operator == "gt":
            return field_value > compare_value
        elif operator == "lt":
            return field_value < compare_value
        elif operator == "contains":
            return compare_value in str(field_value)
        elif operator == "exists":
            return field_value is not None
        else:
            return False

    async def _execute_transform_node(
        self,
        data: dict[str, Any],
        context: WorkflowContext,
    ) -> Any:
        """データ変換ノード実行."""
        transform_type = data.get("transform_type", "jmespath")
        expression = data.get("expression", "")

        context_dict = context.to_dict()

        if transform_type == "jmespath":
            # JMESPath変換
            try:
                result = jmespath.search(expression, context_dict)
                return result
            except Exception as e:
                return {"error": f"JMESPath error: {e!s}"}
        elif transform_type == "template":
            # テンプレート変換
            return self._resolve_template(expression, context)
        else:
            return {"error": f"Unknown transform type: {transform_type}"}

    async def _execute_tool_node(
        self,
        data: dict[str, Any],
        context: WorkflowContext,
    ) -> dict[str, Any]:
        """ツールノード実行.

        Note: 実際のツール実行は今後実装。
        現時点ではプレースホルダー。
        """
        tool_name = data.get("tool_name")
        tool_config = data.get("tool_config", {})

        # 設定内のテンプレートを解決
        resolved_config = {}
        for key, value in tool_config.items():
            if isinstance(value, str):
                resolved_config[key] = self._resolve_template(value, context)
            else:
                resolved_config[key] = value

        # TODO: 実際のツール呼び出し
        return {
            "tool_name": tool_name,
            "config": resolved_config,
            "output": f"Tool {tool_name} executed (placeholder)",
        }

    async def _execute_output_node(
        self,
        data: dict[str, Any],
        context: WorkflowContext,
    ) -> dict[str, Any]:
        """出力ノード実行."""
        output_type = data.get("output_type", "return")
        output_config = data.get("output_config", {})

        if output_type == "return":
            # コンテキスト全体を返す
            return {
                "type": "return",
                "data": context.to_dict(),
            }
        elif output_type == "webhook":
            # TODO: Webhook送信実装
            webhook_url = output_config.get("webhook_url", "")
            return {
                "type": "webhook",
                "url": webhook_url,
                "status": "not_implemented",
            }
        elif output_type == "store":
            # TODO: データ保存実装
            store_key = output_config.get("store_key", "")
            return {
                "type": "store",
                "key": store_key,
                "status": "not_implemented",
            }
        else:
            return {"type": output_type, "status": "unknown"}

    def _resolve_template(
        self,
        template: str,
        context: WorkflowContext,
    ) -> Any:
        """テンプレート文字列を解決.

        {{node_id.path.to.value}} 形式のテンプレートを実際の値に置換。

        Args:
            template: テンプレート文字列
            context: 実行コンテキスト

        Returns:
            解決された値
        """
        if not isinstance(template, str):
            return template

        # {{...}} パターンを検索
        pattern = r"\{\{([^}]+)\}\}"
        matches = re.findall(pattern, template)

        if not matches:
            return template

        context_dict = context.to_dict()

        # 単一マッチで文字列全体がテンプレートの場合は値をそのまま返す
        if len(matches) == 1 and template == f"{{{{{matches[0]}}}}}":
            path = matches[0].strip()
            try:
                return jmespath.search(path, context_dict)
            except Exception:
                return None

        # 複数マッチまたは部分マッチの場合は文字列置換
        result = template
        for match in matches:
            path = match.strip()
            try:
                value = jmespath.search(path, context_dict)
                result = result.replace(f"{{{{{match}}}}}", str(value) if value is not None else "")
            except Exception:
                result = result.replace(f"{{{{{match}}}}}", "")

        return result
