"use client";

import type { NodeProps } from "@xyflow/react";
import { Database, FileOutput, Send } from "lucide-react";

import { BaseNode } from "./BaseNode";

export interface OutputNodeData {
  label?: string;
  output_type: "return" | "webhook" | "store";
  output_config?: {
    webhook_url?: string;
    store_key?: string;
  };
}

const outputIcons = {
  return: FileOutput,
  webhook: Send,
  store: Database,
};

const outputLabels = {
  return: "結果を返す",
  webhook: "Webhook送信",
  store: "データ保存",
};

export function OutputNode({ data, selected }: NodeProps) {
  const nodeData = data as OutputNodeData;
  const outputType = nodeData.output_type || "return";
  const Icon = outputIcons[outputType];
  const config = nodeData.output_config || {};

  return (
    <BaseNode
      label={nodeData.label || outputLabels[outputType]}
      icon={<Icon className="h-4 w-4" />}
      variant="output"
      selected={selected}
      hasOutput={false}
    >
      <div className="text-xs text-muted-foreground">
        {outputType === "return" && "ワークフロー結果として出力"}
        {outputType === "webhook" && (
          <span className="truncate">
            URL: {config.webhook_url || "未設定"}
          </span>
        )}
        {outputType === "store" && (
          <span>Key: {config.store_key || "未設定"}</span>
        )}
      </div>
    </BaseNode>
  );
}
