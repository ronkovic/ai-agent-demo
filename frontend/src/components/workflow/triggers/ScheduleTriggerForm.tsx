"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ScheduleTriggerFormProps {
  onSubmit: (cronExpression: string) => Promise<void>;
  onCancel: () => void;
}

// よく使うcronプリセット
const CRON_PRESETS = [
  { label: "毎分", value: "* * * * *" },
  { label: "毎時", value: "0 * * * *" },
  { label: "毎日 9:00", value: "0 9 * * *" },
  { label: "毎日 12:00", value: "0 12 * * *" },
  { label: "毎日 18:00", value: "0 18 * * *" },
  { label: "毎週月曜 9:00", value: "0 9 * * 1" },
  { label: "毎月1日 9:00", value: "0 9 1 * *" },
  { label: "カスタム", value: "custom" },
];

export function ScheduleTriggerForm({
  onSubmit,
  onCancel,
}: ScheduleTriggerFormProps) {
  const [selectedPreset, setSelectedPreset] = useState<string>("");
  const [customCron, setCustomCron] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cronExpression =
      selectedPreset === "custom" ? customCron : selectedPreset;

    if (!cronExpression) {
      setError("スケジュールを選択してください");
      return;
    }

    // 簡易バリデーション
    const parts = cronExpression.trim().split(/\s+/);
    if (parts.length !== 5) {
      setError("cron式は5つの要素が必要です (分 時 日 月 曜日)");
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(cronExpression);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "トリガーの作成に失敗しました"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <div className="space-y-2">
        <Label htmlFor="preset">スケジュール</Label>
        <Select value={selectedPreset} onValueChange={setSelectedPreset}>
          <SelectTrigger id="preset">
            <SelectValue placeholder="スケジュールを選択..." />
          </SelectTrigger>
          <SelectContent>
            {CRON_PRESETS.map((preset) => (
              <SelectItem key={preset.value} value={preset.value}>
                {preset.label}
                {preset.value !== "custom" && (
                  <span className="text-muted-foreground ml-2 text-xs">
                    ({preset.value})
                  </span>
                )}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedPreset === "custom" && (
        <div className="space-y-2">
          <Label htmlFor="customCron">cron式</Label>
          <Input
            id="customCron"
            placeholder="例: 0 9 * * * (毎日9時)"
            value={customCron}
            onChange={(e) => setCustomCron(e.target.value)}
          />
          <p className="text-muted-foreground text-xs">
            形式: 分 時 日 月 曜日 (例: 0 9 * * 1-5 は平日9時)
          </p>
        </div>
      )}

      {error && <p className="text-destructive text-sm">{error}</p>}

      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          追加
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          キャンセル
        </Button>
      </div>
    </form>
  );
}
