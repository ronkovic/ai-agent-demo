"use client";

import { formatDistanceToNow } from "date-fns";
import { ja } from "date-fns/locale";
import { Copy, EyeOff, Link2, RefreshCw, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import type { WebhookTriggerResponse } from "@/lib/api-client/types.gen";

interface WebhookTriggerListProps {
  triggers: WebhookTriggerResponse[];
  onDelete: (triggerId: string) => Promise<void>;
  onRegenerateSecret: (triggerId: string) => Promise<string>;
}

export function WebhookTriggerList({
  triggers,
  onDelete,
  onRegenerateSecret,
}: WebhookTriggerListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [regeneratingId, setRegeneratingId] = useState<string | null>(null);
  const [visibleSecrets, setVisibleSecrets] = useState<Record<string, string>>(
    {}
  );
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleDelete = async (triggerId: string) => {
    if (!confirm("このWebhookトリガーを削除しますか？")) return;
    setDeletingId(triggerId);
    try {
      await onDelete(triggerId);
    } finally {
      setDeletingId(null);
    }
  };

  const handleRegenerateSecret = async (triggerId: string) => {
    if (
      !confirm(
        "シークレットを再生成しますか？\n既存のシークレットは無効になります。"
      )
    )
      return;
    setRegeneratingId(triggerId);
    try {
      const newSecret = await onRegenerateSecret(triggerId);
      setVisibleSecrets((prev) => ({ ...prev, [triggerId]: newSecret }));
    } finally {
      setRegeneratingId(null);
    }
  };

  const toggleSecretVisibility = (triggerId: string) => {
    if (visibleSecrets[triggerId]) {
      setVisibleSecrets((prev) => {
        const next = { ...prev };
        delete next[triggerId];
        return next;
      });
    }
  };

  const copyToClipboard = async (text: string, triggerId: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(triggerId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (triggers.length === 0) {
    return (
      <div className="text-muted-foreground py-8 text-center text-sm">
        Webhookトリガーがありません
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {triggers.map((trigger) => (
        <div
          key={trigger.id}
          className="bg-muted/50 rounded-lg border p-4 space-y-3"
        >
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Link2 className="text-muted-foreground h-5 w-5" />
              <code className="text-sm font-mono">{trigger.webhook_path}</code>
            </div>
            <Button
              variant="ghost"
              size="icon"
              disabled={deletingId === trigger.id}
              onClick={() => handleDelete(trigger.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>

          {/* Webhook URL */}
          <div className="space-y-1">
            <label className="text-muted-foreground text-xs">
              Webhook URL
            </label>
            <div className="bg-background flex items-center gap-2 rounded border p-2">
              <code className="flex-1 truncate text-xs">
                {trigger.webhook_url}
              </code>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 shrink-0"
                onClick={() =>
                  copyToClipboard(trigger.webhook_url, `url-${trigger.id}`)
                }
              >
                <Copy className="h-3 w-3" />
              </Button>
              {copiedId === `url-${trigger.id}` && (
                <span className="text-muted-foreground text-xs">
                  コピーしました
                </span>
              )}
            </div>
          </div>

          {/* Secret */}
          <div className="space-y-1">
            <label className="text-muted-foreground text-xs">
              シークレット（署名検証用）
            </label>
            <div className="bg-background flex items-center gap-2 rounded border p-2">
              {visibleSecrets[trigger.id] ? (
                <>
                  <code className="flex-1 truncate text-xs">
                    {visibleSecrets[trigger.id]}
                  </code>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 shrink-0"
                    onClick={() =>
                      copyToClipboard(
                        visibleSecrets[trigger.id],
                        `secret-${trigger.id}`
                      )
                    }
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 shrink-0"
                    onClick={() => toggleSecretVisibility(trigger.id)}
                  >
                    <EyeOff className="h-3 w-3" />
                  </Button>
                </>
              ) : (
                <>
                  <span className="text-muted-foreground flex-1 text-xs">
                    ••••••••••••••••
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 shrink-0 text-xs"
                    disabled={regeneratingId === trigger.id}
                    onClick={() => handleRegenerateSecret(trigger.id)}
                  >
                    <RefreshCw
                      className={`mr-1 h-3 w-3 ${
                        regeneratingId === trigger.id ? "animate-spin" : ""
                      }`}
                    />
                    再生成
                  </Button>
                </>
              )}
              {copiedId === `secret-${trigger.id}` && (
                <span className="text-muted-foreground text-xs">
                  コピーしました
                </span>
              )}
            </div>
          </div>

          {/* Meta info */}
          <div className="text-muted-foreground flex gap-3 text-xs">
            {trigger.last_triggered_at && (
              <span>
                最終実行:{" "}
                {formatDistanceToNow(new Date(trigger.last_triggered_at), {
                  addSuffix: true,
                  locale: ja,
                })}
              </span>
            )}
            <span>
              作成:{" "}
              {formatDistanceToNow(new Date(trigger.created_at), {
                addSuffix: true,
                locale: ja,
              })}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
