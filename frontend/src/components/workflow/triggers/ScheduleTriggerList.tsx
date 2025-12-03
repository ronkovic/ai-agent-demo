"use client";

import { formatDistanceToNow } from "date-fns";
import { ja } from "date-fns/locale";
import { CalendarClock, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import type { ScheduleTriggerResponse } from "@/lib/api-client/types.gen";

interface ScheduleTriggerListProps {
  triggers: ScheduleTriggerResponse[];
  onDelete: (triggerId: string) => Promise<void>;
  onToggle: (triggerId: string, isActive: boolean) => Promise<void>;
}

export function ScheduleTriggerList({
  triggers,
  onDelete,
  onToggle,
}: ScheduleTriggerListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const handleDelete = async (triggerId: string) => {
    if (!confirm("このトリガーを削除しますか？")) return;
    setDeletingId(triggerId);
    try {
      await onDelete(triggerId);
    } finally {
      setDeletingId(null);
    }
  };

  const handleToggle = async (triggerId: string, currentState: boolean) => {
    setTogglingId(triggerId);
    try {
      await onToggle(triggerId, !currentState);
    } finally {
      setTogglingId(null);
    }
  };

  if (triggers.length === 0) {
    return (
      <div className="text-muted-foreground py-8 text-center text-sm">
        スケジュールトリガーがありません
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {triggers.map((trigger) => (
        <div
          key={trigger.id}
          className="bg-muted/50 flex items-center justify-between rounded-lg border p-3"
        >
          <div className="flex items-center gap-3">
            <CalendarClock className="text-muted-foreground h-5 w-5" />
            <div>
              <code className="text-sm font-mono">
                {trigger.cron_expression}
              </code>
              <div className="text-muted-foreground flex gap-2 text-xs">
                {trigger.next_run_at && (
                  <span>
                    次回:{" "}
                    {formatDistanceToNow(new Date(trigger.next_run_at), {
                      addSuffix: true,
                      locale: ja,
                    })}
                  </span>
                )}
                {trigger.last_run_at && (
                  <span>
                    前回:{" "}
                    {formatDistanceToNow(new Date(trigger.last_run_at), {
                      addSuffix: true,
                      locale: ja,
                    })}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Switch
              checked={trigger.is_active}
              disabled={togglingId === trigger.id}
              onCheckedChange={() =>
                handleToggle(trigger.id, trigger.is_active)
              }
            />
            <Button
              variant="ghost"
              size="icon"
              disabled={deletingId === trigger.id}
              onClick={() => handleDelete(trigger.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
