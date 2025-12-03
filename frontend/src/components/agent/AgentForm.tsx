import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { AgentCreate } from "@/lib/api-client/types.gen";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import { useEffect } from "react";

const agentSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  system_prompt: z.string().min(1, "System prompt is required"),
  llm_provider: z.enum(["claude", "openai", "bedrock"]),
  llm_model: z.string().min(1, "Model is required"),
  is_public: z.boolean().default(false),
});

type AgentFormValues = z.infer<typeof agentSchema>;

interface AgentFormProps {
  initialData?: Partial<AgentCreate>;
  onSubmit: (data: AgentCreate) => void;
  onCancel: () => void;
  isLoading?: boolean;
  className?: string;
}

const LLM_MODELS = {
  claude: [
    { value: "claude-3-5-sonnet-20241022", label: "Claude 3.5 Sonnet" },
    { value: "claude-3-opus-20240229", label: "Claude 3 Opus" },
    { value: "claude-3-haiku-20240307", label: "Claude 3 Haiku" },
  ],
  openai: [
    { value: "gpt-4o", label: "GPT-4o" },
    { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
    { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
  ],
  bedrock: [
    { value: "anthropic.claude-3-5-sonnet-20241022-v2:0", label: "Claude 3.5 Sonnet (Bedrock)" },
    { value: "anthropic.claude-3-haiku-20240307-v1:0", label: "Claude 3 Haiku (Bedrock)" },
  ],
};

export function AgentForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
  className,
}: AgentFormProps) {
  const {
    register,
    handleSubmit,
    control,
    setValue,
    getValues,
    formState: { errors },
  } = useForm<AgentFormValues>({
    resolver: zodResolver(agentSchema),
    defaultValues: {
      name: initialData?.name || "",
      description: initialData?.description || "",
      system_prompt: initialData?.system_prompt || "",
      llm_provider: (initialData?.llm_provider as "claude" | "openai" | "bedrock") || "claude",
      llm_model: initialData?.llm_model || LLM_MODELS.claude[0].value,
      is_public: initialData?.is_public || false,
    },
  });

  const selectedProvider = useWatch({ control, name: "llm_provider" });

  // Update model when provider changes
  useEffect(() => {
    const models = LLM_MODELS[selectedProvider];
    if (models && models.length > 0) {
      // Only reset if the current model is not valid for the new provider
      const currentModel = getValues("llm_model");
      const isValid = models.some((m) => m.value === currentModel);
      if (!isValid) {
        setValue("llm_model", models[0].value);
      }
    }
  }, [selectedProvider, setValue, getValues]);

  const availableModels = LLM_MODELS[selectedProvider] || [];

  return (
    <form
      onSubmit={handleSubmit((data) => onSubmit(data as AgentCreate))}
      className={cn("space-y-6", className)}
    >
      <div className="space-y-2">
        <label htmlFor="name" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100">
          名前
        </label>
        <input
          id="name"
          {...register("name")}
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-blue-600"
          placeholder="マイエージェント"
        />
        {errors.name && (
          <p className="text-sm text-red-500">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <label htmlFor="description" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100">
          説明
        </label>
        <input
          id="description"
          {...register("description")}
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-blue-600"
          placeholder="説明（任意）"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100">
            プロバイダー
          </label>
          <select
            {...register("llm_provider")}
            className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:focus-visible:ring-blue-600"
          >
            <option value="claude">Anthropic (Claude)</option>
            <option value="openai">OpenAI</option>
            <option value="bedrock">AWS Bedrock</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100">
            モデル
          </label>
          <select
            {...register("llm_model")}
            className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:focus-visible:ring-blue-600"
          >
            {availableModels.map((model) => (
              <option key={model.value} value={model.value}>
                {model.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="system_prompt" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100">
          システムプロンプト
        </label>
        <textarea
          id="system_prompt"
          {...register("system_prompt")}
          rows={5}
          className="flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-blue-600"
          placeholder="あなたは役に立つアシスタントです..."
        />
        {errors.system_prompt && (
          <p className="text-sm text-red-500">{errors.system_prompt.message}</p>
        )}
      </div>

      <div className="flex items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-800">
        <div className="space-y-0.5">
          <label
            htmlFor="is_public"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100"
          >
            公開設定
          </label>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            他のユーザーがこのエージェントをワークフローで利用できます
          </p>
        </div>
        <input
          id="is_public"
          type="checkbox"
          {...register("is_public")}
          className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900"
        />
      </div>

      <div className="flex justify-end gap-4">
        <Button type="button" variant="secondary" onClick={onCancel}>
          キャンセル
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "保存中..." : "エージェントを保存"}
        </Button>
      </div>
    </form>
  );
}
