"use client";

import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  Loader2,
  XCircle,
} from "lucide-react";
import { useState } from "react";

import type { WorkflowExecutionResponse } from "@/lib/api-client/types.gen";
import { cn } from "@/lib/utils";

interface ExecutionDetailProps {
  execution: WorkflowExecutionResponse;
}

const statusConfig = {
  pending: {
    icon: Clock,
    label: "待機中",
    className: "text-yellow-600",
  },
  running: {
    icon: Loader2,
    label: "実行中",
    className: "text-blue-600",
    iconClassName: "animate-spin",
  },
  completed: {
    icon: CheckCircle2,
    label: "完了",
    className: "text-green-600",
  },
  failed: {
    icon: XCircle,
    label: "失敗",
    className: "text-red-600",
  },
  cancelled: {
    icon: AlertCircle,
    label: "キャンセル",
    className: "text-gray-600",
  },
};

export function ExecutionDetail({ execution }: ExecutionDetailProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  const status = statusConfig[execution.status as keyof typeof statusConfig] || statusConfig.pending;
  const Icon = status.icon;

  const toggleNode = (nodeId: string) => {
    const next = new Set(expandedNodes);
    if (next.has(nodeId)) {
      next.delete(nodeId);
    } else {
      next.add(nodeId);
    }
    setExpandedNodes(next);
  };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleString("ja-JP");
  };

  const nodeResults = execution.node_results || {};
  const nodeIds = Object.keys(nodeResults);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Icon
          className={cn(
            "h-8 w-8",
            status.className,
            (status as { iconClassName?: string }).iconClassName
          )}
        />
        <div>
          <h3 className="text-lg font-semibold">{status.label}</h3>
          <p className="font-mono text-sm text-muted-foreground">
            ID: {execution.id}
          </p>
        </div>
      </div>

      {/* Meta Info */}
      <div className="grid grid-cols-2 gap-4 rounded-lg border p-4">
        <div>
          <span className="text-xs text-muted-foreground">作成日時</span>
          <p className="text-sm">{formatDate(execution.created_at)}</p>
        </div>
        <div>
          <span className="text-xs text-muted-foreground">開始日時</span>
          <p className="text-sm">{formatDate(execution.started_at)}</p>
        </div>
        <div>
          <span className="text-xs text-muted-foreground">完了日時</span>
          <p className="text-sm">{formatDate(execution.completed_at)}</p>
        </div>
        <div>
          <span className="text-xs text-muted-foreground">ワークフローID</span>
          <p className="font-mono text-sm">{execution.workflow_id}</p>
        </div>
      </div>

      {/* Error */}
      {execution.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950/30">
          <h4 className="flex items-center gap-2 font-medium text-red-800 dark:text-red-400">
            <XCircle className="h-4 w-4" />
            エラー
          </h4>
          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-sm text-red-700 dark:text-red-300">
            {execution.error}
          </pre>
        </div>
      )}

      {/* Trigger Data */}
      {execution.trigger_data && Object.keys(execution.trigger_data).length > 0 && (
        <div>
          <h4 className="mb-2 font-medium">トリガーデータ</h4>
          <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-sm">
            {JSON.stringify(execution.trigger_data, null, 2)}
          </pre>
        </div>
      )}

      {/* Node Results */}
      <div>
        <h4 className="mb-2 font-medium">ノード実行結果</h4>
        {nodeIds.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            ノード結果がありません
          </p>
        ) : (
          <div className="space-y-2">
            {nodeIds.map((nodeId) => {
              const result = nodeResults[nodeId];
              const isExpanded = expandedNodes.has(nodeId);

              return (
                <div key={nodeId} className="rounded-lg border">
                  <button
                    onClick={() => toggleNode(nodeId)}
                    className="flex w-full items-center gap-2 p-3 text-left hover:bg-accent"
                  >
                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    )}
                    <span className="font-mono text-sm">{nodeId}</span>
                    {result?.status && (
                      <span
                        className={cn(
                          "ml-auto rounded-full px-2 py-0.5 text-xs",
                          result.status === "completed" && "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
                          result.status === "failed" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                          result.status === "running" && "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                        )}
                      >
                        {result.status}
                      </span>
                    )}
                  </button>
                  {isExpanded && (
                    <div className="border-t bg-muted/50 p-4">
                      <pre className="overflow-x-auto whitespace-pre-wrap text-sm">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
