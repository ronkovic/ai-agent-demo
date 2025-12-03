"use client";

import type { NodeProps } from "@xyflow/react";
import { Bot } from "lucide-react";

import { BaseNode } from "./BaseNode";

export interface AgentNodeData {
  label?: string;
  agent_id?: string;
  agent_name?: string;
  input_mapping?: Record<string, string>;
  output_key?: string;
}

export function AgentNode({ data, selected }: NodeProps) {
  const nodeData = data as AgentNodeData;

  return (
    <BaseNode
      label={nodeData.label || "エージェント"}
      icon={<Bot className="h-4 w-4" />}
      variant="agent"
      selected={selected}
    >
      <div className="space-y-1 text-xs">
        <div className="text-muted-foreground">
          {nodeData.agent_name || "エージェント未選択"}
        </div>
        {nodeData.output_key && (
          <div className="text-muted-foreground">
            出力: <span className="font-mono">{nodeData.output_key}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}
