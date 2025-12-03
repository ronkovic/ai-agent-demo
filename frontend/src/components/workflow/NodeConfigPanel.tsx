"use client";

import type { Node } from "@xyflow/react";
import { X } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

import type { AgentNodeData } from "./nodes/AgentNode";
import type { ConditionNodeData } from "./nodes/ConditionNode";
import type { OutputNodeData } from "./nodes/OutputNode";
import type { ToolNodeData } from "./nodes/ToolNode";
import type { TransformNodeData } from "./nodes/TransformNode";
import type { TriggerNodeData } from "./nodes/TriggerNode";

type NodeData =
  | TriggerNodeData
  | AgentNodeData
  | ConditionNodeData
  | TransformNodeData
  | ToolNodeData
  | OutputNodeData;

interface NodeConfigPanelProps {
  node: Node | null;
  onClose: () => void;
  onUpdate: (nodeId: string, data: Partial<NodeData>) => void;
  className?: string;
}

export function NodeConfigPanel({
  node,
  onClose,
  onUpdate,
  className,
}: NodeConfigPanelProps) {
  if (!node) return null;

  const handleChange = (key: string, value: unknown) => {
    onUpdate(node.id, { [key]: value });
  };

  const renderConfig = () => {
    switch (node.type) {
      case "trigger":
        return <TriggerConfig data={node.data as TriggerNodeData} onChange={handleChange} />;
      case "agent":
        return <AgentConfig data={node.data as AgentNodeData} onChange={handleChange} />;
      case "condition":
        return <ConditionConfig data={node.data as ConditionNodeData} onChange={handleChange} />;
      case "transform":
        return <TransformConfig data={node.data as TransformNodeData} onChange={handleChange} />;
      case "tool":
        return <ToolConfig data={node.data as ToolNodeData} onChange={handleChange} />;
      case "output":
        return <OutputConfig data={node.data as OutputNodeData} onChange={handleChange} />;
      default:
        return <div className="text-muted-foreground">設定なし</div>;
    }
  };

  return (
    <div
      className={cn(
        "flex w-80 flex-col border-l bg-background",
        className
      )}
    >
      <div className="flex items-center justify-between border-b p-4">
        <h2 className="text-sm font-semibold">ノード設定</h2>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground">
            ラベル
          </label>
          <input
            type="text"
            value={(node.data as { label?: string }).label || ""}
            onChange={(e) => handleChange("label", e.target.value)}
            className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            placeholder="ノード名"
          />
        </div>
        {renderConfig()}
      </div>
    </div>
  );
}

// Configuration components for each node type

function TriggerConfig({
  data,
  onChange,
}: {
  data: TriggerNodeData;
  onChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          トリガータイプ
        </label>
        <select
          value={data.trigger_type || "manual"}
          onChange={(e) => onChange("trigger_type", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        >
          <option value="manual">手動実行</option>
          <option value="schedule">スケジュール</option>
          <option value="webhook">Webhook</option>
        </select>
      </div>
      {data.trigger_type === "schedule" && (
        <div>
          <label className="text-xs font-medium text-muted-foreground">
            Cron式
          </label>
          <input
            type="text"
            value={data.schedule_cron || ""}
            onChange={(e) => onChange("schedule_cron", e.target.value)}
            className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            placeholder="0 0 * * *"
          />
        </div>
      )}
      {data.trigger_type === "webhook" && (
        <div>
          <label className="text-xs font-medium text-muted-foreground">
            Webhookパス
          </label>
          <input
            type="text"
            value={data.webhook_path || ""}
            onChange={(e) => onChange("webhook_path", e.target.value)}
            className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            placeholder="/webhook/my-workflow"
          />
        </div>
      )}
    </div>
  );
}

function AgentConfig({
  data,
  onChange,
}: {
  data: AgentNodeData;
  onChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          エージェントID
        </label>
        <input
          type="text"
          value={data.agent_id || ""}
          onChange={(e) => onChange("agent_id", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          placeholder="エージェントを選択..."
        />
      </div>
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          出力キー
        </label>
        <input
          type="text"
          value={data.output_key || ""}
          onChange={(e) => onChange("output_key", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          placeholder="agent_result"
        />
      </div>
    </div>
  );
}

function ConditionConfig({
  data,
  onChange,
}: {
  data: ConditionNodeData;
  onChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          ロジック
        </label>
        <select
          value={data.logic || "and"}
          onChange={(e) => onChange("logic", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        >
          <option value="and">すべて一致 (AND)</option>
          <option value="or">いずれか一致 (OR)</option>
        </select>
      </div>
      <div className="text-xs text-muted-foreground">
        条件の詳細設定は今後実装予定
      </div>
    </div>
  );
}

function TransformConfig({
  data,
  onChange,
}: {
  data: TransformNodeData;
  onChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          変換タイプ
        </label>
        <select
          value={data.transform_type || "jmespath"}
          onChange={(e) => onChange("transform_type", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        >
          <option value="jmespath">JMESPath</option>
          <option value="template">テンプレート</option>
        </select>
      </div>
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          {data.transform_type === "jmespath" ? "JMESPath式" : "テンプレート"}
        </label>
        <textarea
          value={data.expression || ""}
          onChange={(e) => onChange("expression", e.target.value)}
          className="mt-1 flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          placeholder={
            data.transform_type === "jmespath"
              ? "data.items[*].name"
              : "{{node_id.result}}"
          }
        />
      </div>
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          出力キー
        </label>
        <input
          type="text"
          value={data.output_key || ""}
          onChange={(e) => onChange("output_key", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          placeholder="transformed"
        />
      </div>
    </div>
  );
}

function ToolConfig({
  data,
  onChange,
}: {
  data: ToolNodeData;
  onChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          ツール名
        </label>
        <input
          type="text"
          value={data.tool_name || ""}
          onChange={(e) => onChange("tool_name", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          placeholder="ツールを選択..."
        />
      </div>
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          出力キー
        </label>
        <input
          type="text"
          value={data.output_key || ""}
          onChange={(e) => onChange("output_key", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          placeholder="tool_result"
        />
      </div>
    </div>
  );
}

function OutputConfig({
  data,
  onChange,
}: {
  data: OutputNodeData;
  onChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-medium text-muted-foreground">
          出力タイプ
        </label>
        <select
          value={data.output_type || "return"}
          onChange={(e) => onChange("output_type", e.target.value)}
          className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        >
          <option value="return">結果を返す</option>
          <option value="webhook">Webhook送信</option>
          <option value="store">データ保存</option>
        </select>
      </div>
      {data.output_type === "webhook" && (
        <div>
          <label className="text-xs font-medium text-muted-foreground">
            Webhook URL
          </label>
          <input
            type="text"
            value={data.output_config?.webhook_url || ""}
            onChange={(e) =>
              onChange("output_config", {
                ...data.output_config,
                webhook_url: e.target.value,
              })
            }
            className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            placeholder="https://..."
          />
        </div>
      )}
      {data.output_type === "store" && (
        <div>
          <label className="text-xs font-medium text-muted-foreground">
            保存キー
          </label>
          <input
            type="text"
            value={data.output_config?.store_key || ""}
            onChange={(e) =>
              onChange("output_config", {
                ...data.output_config,
                store_key: e.target.value,
              })
            }
            className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm font-mono shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            placeholder="workflow_result"
          />
        </div>
      )}
    </div>
  );
}
