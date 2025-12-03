import type { NodeTypes } from "@xyflow/react";

import { AgentNode } from "./AgentNode";
import { ConditionNode } from "./ConditionNode";
import { OutputNode } from "./OutputNode";
import { ToolNode } from "./ToolNode";
import { TransformNode } from "./TransformNode";
import { TriggerNode } from "./TriggerNode";

export const nodeTypes: NodeTypes = {
  trigger: TriggerNode,
  agent: AgentNode,
  condition: ConditionNode,
  transform: TransformNode,
  tool: ToolNode,
  output: OutputNode,
};

export { AgentNode } from "./AgentNode";
export { BaseNode } from "./BaseNode";
export { ConditionNode } from "./ConditionNode";
export { OutputNode } from "./OutputNode";
export { ToolNode } from "./ToolNode";
export { TransformNode } from "./TransformNode";
export { TriggerNode } from "./TriggerNode";

// Node type definitions for palette
export const nodeDefinitions = [
  {
    type: "trigger",
    label: "トリガー",
    description: "ワークフローの開始点",
    category: "control",
  },
  {
    type: "agent",
    label: "エージェント",
    description: "AIエージェントを実行",
    category: "action",
  },
  {
    type: "condition",
    label: "条件分岐",
    description: "条件に基づいて分岐",
    category: "control",
  },
  {
    type: "transform",
    label: "データ変換",
    description: "データを変換・加工",
    category: "action",
  },
  {
    type: "tool",
    label: "ツール実行",
    description: "外部ツールを実行",
    category: "action",
  },
  {
    type: "output",
    label: "出力",
    description: "結果を出力",
    category: "control",
  },
] as const;

export type NodeType = (typeof nodeDefinitions)[number]["type"];
