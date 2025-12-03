"use client";

import type { NodeProps } from "@xyflow/react";
import { Wand2 } from "lucide-react";

import { BaseNode } from "./BaseNode";

export interface TransformNodeData {
  label?: string;
  transform_type: "jmespath" | "template";
  expression?: string;
  output_key?: string;
}

export function TransformNode({ data, selected }: NodeProps) {
  const nodeData = data as TransformNodeData;
  const transformType = nodeData.transform_type || "jmespath";

  return (
    <BaseNode
      label={nodeData.label || "データ変換"}
      icon={<Wand2 className="h-4 w-4" />}
      variant="transform"
      selected={selected}
    >
      <div className="space-y-1 text-xs">
        <div className="text-muted-foreground">
          {transformType === "jmespath" ? "JMESPath" : "テンプレート"}
        </div>
        {nodeData.expression && (
          <div className="max-w-[160px] truncate font-mono text-muted-foreground">
            {nodeData.expression}
          </div>
        )}
        {nodeData.output_key && (
          <div className="text-muted-foreground">
            出力: <span className="font-mono">{nodeData.output_key}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}
