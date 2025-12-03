"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Key, Trash, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useLLMConfigs } from "@/hooks/useLLMConfigs";
import type { UserLLMConfigResponse } from "@/lib/api-client/types.gen";

const LLM_PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google" },
  { value: "bedrock", label: "AWS Bedrock" },
];

const addKeySchema = z.object({
  provider: z.string().min(1, "プロバイダーを選択してください"),
  api_key: z.string().min(1, "APIキーを入力してください"),
  is_default: z.boolean(),
});

type AddKeyFormValues = z.infer<typeof addKeySchema>;

export function LLMKeyManager() {
  const { configs, isLoading, error, addConfig, deleteConfig } =
    useLLMConfigs();
  const [showAddForm, setShowAddForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AddKeyFormValues>({
    resolver: zodResolver(addKeySchema),
    defaultValues: {
      provider: "",
      api_key: "",
      is_default: false,
    },
  });

  const onSubmit = async (data: AddKeyFormValues) => {
    try {
      setIsSubmitting(true);
      await addConfig(data);
      reset();
      setShowAddForm(false);
    } catch (err) {
      console.error("Failed to add LLM config:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (config: UserLLMConfigResponse) => {
    if (!confirm(`${config.provider}のAPIキーを削除しますか？`)) return;
    try {
      setDeleteId(config.id);
      await deleteConfig(config.id);
    } catch (err) {
      console.error("Failed to delete LLM config:", err);
    } finally {
      setDeleteId(null);
    }
  };

  const usedProviders = configs.map((c) => c.provider);

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
            LLM APIキー
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            各LLMプロバイダーのAPIキーを管理します
          </p>
        </div>
        {!showAddForm && (
          <Button onClick={() => setShowAddForm(true)} size="sm">
            <Plus className="mr-2 h-4 w-4" />
            キーを追加
          </Button>
        )}
      </div>

      {showAddForm && (
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="rounded-lg border bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900"
        >
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
                プロバイダー
              </label>
              <select
                {...register("provider")}
                className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 dark:border-gray-800 dark:bg-gray-950"
              >
                <option value="">選択してください</option>
                {LLM_PROVIDERS.filter(
                  (p) => !usedProviders.includes(p.value)
                ).map((provider) => (
                  <option key={provider.value} value={provider.value}>
                    {provider.label}
                  </option>
                ))}
              </select>
              {errors.provider && (
                <p className="text-sm text-red-500">{errors.provider.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
                APIキー
              </label>
              <input
                type="password"
                {...register("api_key")}
                className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 dark:border-gray-800 dark:bg-gray-950"
                placeholder="sk-..."
              />
              {errors.api_key && (
                <p className="text-sm text-red-500">{errors.api_key.message}</p>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_default"
                {...register("is_default")}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
              />
              <label
                htmlFor="is_default"
                className="text-sm text-gray-700 dark:text-gray-300"
              >
                デフォルトとして設定
              </label>
            </div>
          </div>

          <div className="mt-4 flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                reset();
                setShowAddForm(false);
              }}
            >
              キャンセル
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  保存中...
                </>
              ) : (
                "保存"
              )}
            </Button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {configs.length === 0 ? (
          <div className="rounded-lg border border-dashed p-8 text-center dark:border-gray-800">
            <Key className="mx-auto h-8 w-8 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              APIキーがまだ登録されていません
            </p>
          </div>
        ) : (
          configs.map((config) => (
            <div
              key={config.id}
              className="flex items-center justify-between rounded-lg border bg-white p-4 dark:border-gray-800 dark:bg-gray-950"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400">
                  <Key className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {LLM_PROVIDERS.find((p) => p.value === config.provider)
                      ?.label || config.provider}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    登録日:{" "}
                    {new Date(config.created_at).toLocaleDateString("ja-JP")}
                    {config.is_default && (
                      <span className="ml-2 rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                        デフォルト
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleDelete(config)}
                disabled={deleteId === config.id}
              >
                {deleteId === config.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash className="h-4 w-4 text-red-500" />
                )}
              </Button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
