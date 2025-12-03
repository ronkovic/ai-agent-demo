"use client";

import type { NodeProps } from "@xyflow/react";
import { Wrench } from "lucide-react";

import { BaseNode } from "./BaseNode";

export interface ToolNodeData {
  label?: string;
  tool_name?: string;
  tool_config?: Record<string, unknown>;
  output_key?: string;
}

export function ToolNode({ data, selected }: NodeProps) {
  const nodeData = data as ToolNodeData;

  return (
    <BaseNode
      label={nodeData.label || "ツール実行"}
      icon={<Wrench className="h-4 w-4" />}
      variant="tool"
      selected={selected}
    >
      <div className="space-y-1 text-xs">
        <div className="text-muted-foreground">
          {nodeData.tool_name || "ツール未選択"}
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
