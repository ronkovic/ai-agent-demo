import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { PersonalAgentCreate } from "@/lib/api-client/types.gen";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const personalAgentSchema = z.object({
  name: z.string().min(1, "名前は必須です"),
  description: z.string().optional(),
  system_prompt: z.string().min(1, "システムプロンプトは必須です"),
  is_public: z.boolean(),
});

type PersonalAgentFormValues = z.infer<typeof personalAgentSchema>;

interface PersonalAgentFormProps {
  initialData?: Partial<PersonalAgentCreate>;
  onSubmit: (data: PersonalAgentCreate) => void;
  onCancel: () => void;
  isLoading?: boolean;
  className?: string;
}

export function PersonalAgentForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
  className,
}: PersonalAgentFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PersonalAgentFormValues>({
    resolver: zodResolver(personalAgentSchema),
    defaultValues: {
      name: initialData?.name || "",
      description: initialData?.description || "",
      system_prompt: initialData?.system_prompt || "",
      is_public: initialData?.is_public || false,
    },
  });

  return (
    <form
      onSubmit={handleSubmit((data) => onSubmit(data as PersonalAgentCreate))}
      className={cn("space-y-6", className)}
    >
      <div className="space-y-2">
        <label
          htmlFor="name"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100"
        >
          名前
        </label>
        <input
          id="name"
          {...register("name")}
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-blue-600"
          placeholder="マイパーソナルエージェント"
        />
        {errors.name && (
          <p className="text-sm text-red-500">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <label
          htmlFor="description"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100"
        >
          説明
        </label>
        <input
          id="description"
          {...register("description")}
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-blue-600"
          placeholder="説明（任意）"
        />
      </div>

      <div className="space-y-2">
        <label
          htmlFor="system_prompt"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-900 dark:text-gray-100"
        >
          システムプロンプト
        </label>
        <textarea
          id="system_prompt"
          {...register("system_prompt")}
          rows={8}
          className="flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-blue-600"
          placeholder="あなたは私の個人アシスタントです。私のタスク管理、スケジュール調整、情報検索を手伝ってください..."
        />
        {errors.system_prompt && (
          <p className="text-sm text-red-500">{errors.system_prompt.message}</p>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="is_public"
          {...register("is_public")}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600 dark:border-gray-700 dark:bg-gray-900"
        />
        <label
          htmlFor="is_public"
          className="text-sm font-medium text-gray-900 dark:text-gray-100"
        >
          公開する（他のユーザーがこのエージェントを利用できます）
        </label>
      </div>

      <div className="flex justify-end gap-4">
        <Button type="button" variant="secondary" onClick={onCancel}>
          キャンセル
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "保存中..." : "パーソナルエージェントを保存"}
        </Button>
      </div>
    </form>
  );
}
