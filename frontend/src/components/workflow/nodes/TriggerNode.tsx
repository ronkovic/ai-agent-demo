"use client";

import type { NodeProps } from "@xyflow/react";
import { Calendar, MousePointer, Webhook } from "lucide-react";

import { BaseNode } from "./BaseNode";

export interface TriggerNodeData {
  label?: string;
  trigger_type: "manual" | "schedule" | "webhook";
  schedule_cron?: string;
  webhook_path?: string;
}

const triggerIcons = {
  manual: MousePointer,
  schedule: Calendar,
  webhook: Webhook,
};

const triggerLabels = {
  manual: "手動実行",
  schedule: "スケジュール",
  webhook: "Webhook",
};

export function TriggerNode({ data, selected }: NodeProps) {
  const nodeData = data as TriggerNodeData;
  const triggerType = nodeData.trigger_type || "manual";
  const Icon = triggerIcons[triggerType];

  return (
    <BaseNode
      label={nodeData.label || triggerLabels[triggerType]}
      icon={<Icon className="h-4 w-4" />}
      variant="trigger"
      selected={selected}
      hasInput={false}
    >
      <div className="text-xs text-muted-foreground">
        {triggerType === "manual" && "クリックで実行開始"}
        {triggerType === "schedule" && (
          <span>Cron: {nodeData.schedule_cron || "未設定"}</span>
        )}
        {triggerType === "webhook" && (
          <span>Path: {nodeData.webhook_path || "未設定"}</span>
        )}
      </div>
    </BaseNode>
  );
}
