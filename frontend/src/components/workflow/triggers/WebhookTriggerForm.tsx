"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { WebhookTriggerResponse } from "@/lib/api-client/types.gen";

interface WebhookTriggerFormProps {
  onSubmit: (webhookPath: string) => Promise<WebhookTriggerResponse>;
  onCancel: () => void;
}

export function WebhookTriggerForm({
  onSubmit,
  onCancel,
}: WebhookTriggerFormProps) {
  const [webhookPath, setWebhookPath] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdTrigger, setCreatedTrigger] =
    useState<WebhookTriggerResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!webhookPath.trim()) {
      setError("Webhookパスを入力してください");
      return;
    }

    // パスのバリデーション
    if (!/^[a-zA-Z0-9_-]+$/.test(webhookPath)) {
      setError("パスには英数字、ハイフン、アンダースコアのみ使用できます");
      return;
    }

    setIsSubmitting(true);
    try {
      const trigger = await onSubmit(webhookPath);
      setCreatedTrigger(trigger);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Webhookの作成に失敗しました"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // 作成成功後の表示
  if (createdTrigger) {
    return (
      <div className="space-y-4 rounded-lg border p-4">
        <div className="bg-success/10 text-success rounded-md p-3">
          <p className="font-medium">Webhookトリガーを作成しました</p>
        </div>

        <div className="space-y-2">
          <Label>Webhook URL</Label>
          <div className="bg-muted flex items-center gap-2 rounded-md p-2">
            <code className="flex-1 break-all text-sm">
              {createdTrigger.webhook_url}
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                navigator.clipboard.writeText(createdTrigger.webhook_url);
              }}
            >
              コピー
            </Button>
          </div>
        </div>

        {createdTrigger.secret && (
          <div className="space-y-2">
            <Label>シークレットキー（この画面でのみ表示されます）</Label>
            <div className="bg-muted flex items-center gap-2 rounded-md p-2">
              <code className="flex-1 break-all text-sm">
                {createdTrigger.secret}
              </code>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (createdTrigger.secret) {
                    navigator.clipboard.writeText(createdTrigger.secret);
                  }
                }}
              >
                コピー
              </Button>
            </div>
            <p className="text-muted-foreground text-xs">
              署名検証用のシークレットです。安全な場所に保存してください。
            </p>
          </div>
        )}

        <Button onClick={onCancel} className="w-full">
          閉じる
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <div className="space-y-2">
        <Label htmlFor="webhookPath">Webhookパス</Label>
        <Input
          id="webhookPath"
          placeholder="例: my-workflow-trigger"
          value={webhookPath}
          onChange={(e) => setWebhookPath(e.target.value)}
        />
        <p className="text-muted-foreground text-xs">
          Webhook URL: {process.env.NEXT_PUBLIC_API_URL || ""}/webhooks/
          {webhookPath || "..."}
        </p>
      </div>

      {error && <p className="text-destructive text-sm">{error}</p>}

      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          作成
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          キャンセル
        </Button>
      </div>
    </form>
  );
}
