"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Key, Trash, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useApiKeys } from "@/hooks/useApiKeys";
import type { UserApiKeyCreated, UserApiKeyResponse } from "@/lib/api-client/types.gen";
import { ApiKeyCreatedModal } from "./ApiKeyCreatedModal";

const createKeySchema = z.object({
  name: z.string().min(1, "名前を入力してください"),
  scopes: z.array(z.string()),
  rate_limit: z.number().min(1).max(100000),
});

type CreateKeyFormValues = z.infer<typeof createKeySchema>;

const AVAILABLE_SCOPES = [
  { value: "agents:read", label: "エージェント読み取り" },
  { value: "agents:execute", label: "エージェント実行" },
  { value: "personal-agents:read", label: "パーソナルエージェント読み取り" },
  { value: "personal-agents:execute", label: "パーソナルエージェント実行" },
];

export function ApiKeyManager() {
  const { apiKeys, isLoading, error, createApiKey, deleteApiKey } =
    useApiKeys();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [createdKey, setCreatedKey] = useState<UserApiKeyCreated | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateKeyFormValues>({
    resolver: zodResolver(createKeySchema),
    defaultValues: {
      name: "",
      scopes: [],
      rate_limit: 1000,
    },
  });

  const onSubmit = async (data: CreateKeyFormValues) => {
    try {
      setIsSubmitting(true);
      const result = await createApiKey({
        name: data.name,
        scopes: data.scopes,
        rate_limit: data.rate_limit,
      });
      setCreatedKey(result);
      reset();
      setShowCreateForm(false);
    } catch (err) {
      console.error("Failed to create API key:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (key: UserApiKeyResponse) => {
    if (!confirm(`APIキー「${key.name}」を削除しますか？`)) return;
    try {
      setDeleteId(key.id);
      await deleteApiKey(key.id);
    } catch (err) {
      console.error("Failed to delete API key:", err);
    } finally {
      setDeleteId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-600 dark:bg-red-900/20 dark:text-red-400">
        {error.message}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            APIキー
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            外部からAPIにアクセスするためのキーを管理します
          </p>
        </div>
        {!showCreateForm && (
          <Button onClick={() => setShowCreateForm(true)} size="sm">
            <Plus className="mr-2 h-4 w-4" />
            新しいキー
          </Button>
        )}
      </div>

      {showCreateForm && (
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="rounded-lg border bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900"
        >
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
                名前
              </label>
              <input
                {...register("name")}
                className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 dark:border-gray-800 dark:bg-gray-950"
                placeholder="My API Key"
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
                スコープ
              </label>
              <div className="space-y-2">
                {AVAILABLE_SCOPES.map((scope) => (
                  <div key={scope.value} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={scope.value}
                      value={scope.value}
                      {...register("scopes")}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                    />
                    <label
                      htmlFor={scope.value}
                      className="text-sm text-gray-700 dark:text-gray-300"
                    >
                      {scope.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
                レート制限（リクエスト/時間）
              </label>
              <input
                type="number"
                {...register("rate_limit", { valueAsNumber: true })}
                className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 dark:border-gray-800 dark:bg-gray-950"
              />
            </div>
          </div>

          <div className="mt-4 flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                reset();
                setShowCreateForm(false);
              }}
            >
              キャンセル
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  作成中...
                </>
              ) : (
                "作成"
              )}
            </Button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {apiKeys.length === 0 ? (
          <div className="rounded-lg border border-dashed p-8 text-center dark:border-gray-800">
            <Key className="mx-auto h-8 w-8 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              APIキーがまだ作成されていません
            </p>
          </div>
        ) : (
          apiKeys.map((key) => (
            <div
              key={key.id}
              className="flex items-center justify-between rounded-lg border bg-white p-4 dark:border-gray-800 dark:bg-gray-950"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400">
                  <Key className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {key.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">
                      {key.key_prefix}
                    </code>
                    {key.last_used_at && (
                      <span className="ml-2">
                        最終使用:{" "}
                        {new Date(key.last_used_at).toLocaleDateString("ja-JP")}
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleDelete(key)}
                disabled={deleteId === key.id}
              >
                {deleteId === key.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash className="h-4 w-4 text-red-500" />
                )}
              </Button>
            </div>
          ))
        )}
      </div>

      {createdKey && (
        <ApiKeyCreatedModal
          apiKey={createdKey}
          onClose={() => setCreatedKey(null)}
        />
      )}
    </div>
  );
}
