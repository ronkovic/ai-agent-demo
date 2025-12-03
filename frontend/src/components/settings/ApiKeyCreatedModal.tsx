"use client";

import { useState } from "react";
import { Copy, Check, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import type { UserApiKeyCreated } from "@/lib/api-client/types.gen";

interface ApiKeyCreatedModalProps {
  apiKey: UserApiKeyCreated;
  onClose: () => void;
}

export function ApiKeyCreatedModal({ apiKey, onClose }: ApiKeyCreatedModalProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(apiKey.key);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black/50"
        onClick={onClose}
      />
      <div className="relative z-50 w-full max-w-lg rounded-lg bg-white p-6 shadow-xl dark:bg-gray-950">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              APIキーが作成されました
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              このキーは二度と表示されません。今すぐコピーして安全な場所に保存してください。
            </p>
          </div>
        </div>

        <div className="mb-4 space-y-2">
          <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {apiKey.name}
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={apiKey.key}
              readOnly
              className="flex-1 rounded-md border border-gray-300 bg-gray-50 px-3 py-2 font-mono text-sm dark:border-gray-700 dark:bg-gray-900"
            />
            <Button
              type="button"
              variant="secondary"
              onClick={handleCopy}
              className="shrink-0"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={onClose}>
            完了
          </Button>
        </div>
      </div>
    </div>
  );
}
