"""Agent Card生成.

AgentモデルからA2A AgentCardを生成する。
"""

from typing import TYPE_CHECKING, Any

from ..core.config import settings

if TYPE_CHECKING:
    from ..db import Agent


def generate_agent_card(agent: "Agent") -> dict[str, Any]:
    """AgentモデルからA2A AgentCardを生成する.

    Args:
        agent: 内部Agentデータベースモデル

    Returns:
        A2Aプロトコル準拠のAgentCard辞書
    """
    # エージェントのツールからスキルを構築
    skills: list[dict[str, Any]] = []

    # ツールをスキルに変換
    if agent.tools:
        tool_list = agent.tools if isinstance(agent.tools, list) else []
        for tool_name in tool_list:
            if isinstance(tool_name, str):
                skills.append(
                    {
                        "id": tool_name,
                        "name": tool_name.replace("_", " ").title(),
                        "description": f"Tool capability: {tool_name}",
                        "tags": [tool_name],
                    }
                )

    # デフォルトの会話スキルを追加
    skills.append(
        {
            "id": "conversation",
            "name": "Conversation",
            "description": agent.description or f"Conversational AI: {agent.name}",
            "tags": ["conversation", "chat", "general"],
        }
    )

    # 機能設定
    capabilities = {
        "streaming": True,  # SSEストリーミング対応
        "pushNotifications": False,  # Phase 5では未実装
        "stateTransitionHistory": False,
    }

    # Agent Card構築
    base_url = settings.a2a_base_url.rstrip("/")

    return {
        "name": agent.name,
        "description": agent.description or f"AI Agent: {agent.name}",
        "url": f"{base_url}/a2a/agents/{agent.id}",
        "version": "1.0.0",
        "protocolVersion": "0.3.0",
        "capabilities": capabilities,
        "skills": skills,
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "provider": {
            "organization": settings.app_name,
        },
    }


def generate_agent_card_json(agent: "Agent") -> dict[str, Any]:
    """AgentCardをJSON形式で生成する.

    データベース保存用のラッパー関数。

    Args:
        agent: 内部Agentデータベースモデル

    Returns:
        AgentCard辞書
    """
    return generate_agent_card(agent)
