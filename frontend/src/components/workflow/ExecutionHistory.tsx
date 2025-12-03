"use client";

import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  XCircle,
} from "lucide-react";

import type { WorkflowExecutionResponse } from "@/lib/api-client/types.gen";
import { cn } from "@/lib/utils";

interface ExecutionHistoryProps {
  executions: WorkflowExecutionResponse[];
  selectedId?: string;
  onSelect: (execution: WorkflowExecutionResponse) => void;
  isLoading?: boolean;
}

const statusConfig = {
  pending: {
    icon: Clock,
    label: "待機中",
    className: "text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30",
  },
  running: {
    icon: Loader2,
    label: "実行中",
    className: "text-blue-600 bg-blue-100 dark:bg-blue-900/30",
    iconClassName: "animate-spin",
  },
  completed: {
    icon: CheckCircle2,
    label: "完了",
    className: "text-green-600 bg-green-100 dark:bg-green-900/30",
  },
  failed: {
    icon: XCircle,
    label: "失敗",
    className: "text-red-600 bg-red-100 dark:bg-red-900/30",
  },
  cancelled: {
    icon: AlertCircle,
    label: "キャンセル",
    className: "text-gray-600 bg-gray-100 dark:bg-gray-800",
  },
};

export function ExecutionHistory({
  executions,
  selectedId,
  onSelect,
  isLoading,
}: ExecutionHistoryProps) {
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleString("ja-JP", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const formatDuration = (
    startedAt: string | null | undefined,
    completedAt: string | null | undefined
  ) => {
    if (!startedAt || !completedAt) return "-";
    const start = new Date(startedAt).getTime();
    const end = new Date(completedAt).getTime();
    const durationMs = end - start;

    if (durationMs < 1000) return `${durationMs}ms`;
    if (durationMs < 60000) return `${(durationMs / 1000).toFixed(1)}s`;
    return `${Math.floor(durationMs / 60000)}m ${Math.floor((durationMs % 60000) / 1000)}s`;
  };

  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (executions.length === 0) {
    return (
      <div className="flex h-48 flex-col items-center justify-center text-center">
        <Clock className="mb-2 h-8 w-8 text-muted-foreground" />
        <p className="text-muted-foreground">実行履歴がありません</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {executions.map((execution) => {
        const status = statusConfig[execution.status as keyof typeof statusConfig] || statusConfig.pending;
        const Icon = status.icon;

        return (
          <button
            key={execution.id}
            onClick={() => onSelect(execution)}
            className={cn(
              "flex w-full items-center gap-4 rounded-lg border p-4 text-left transition-colors hover:bg-accent",
              selectedId === execution.id && "border-primary bg-accent"
            )}
          >
            <div
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-full",
                status.className
              )}
            >
              <Icon
                className={cn(
                  "h-5 w-5",
                  (status as { iconClassName?: string }).iconClassName
                )}
              />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-muted-foreground">
                  {execution.id.slice(0, 8)}
                </span>
                <span
                  className={cn(
                    "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                    status.className
                  )}
                >
                  {status.label}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-4 text-xs text-muted-foreground">
                <span>開始: {formatDate(execution.started_at)}</span>
                <span>
                  所要時間:{" "}
                  {formatDuration(execution.started_at, execution.completed_at)}
                </span>
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
