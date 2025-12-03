"use client";

import { use } from "react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { Settings } from "lucide-react";
import { useRouter } from "next/navigation";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function PersonalAgentChatPage({ params }: PageProps) {
  const { id } = use(params);
  const router = useRouter();

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header
        title="パーソナルエージェント"
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={() => router.push(`/personal-agents/${id}/settings`)}
          >
            <Settings className="mr-2 h-4 w-4" />
            設定
          </Button>
        }
      />
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="text-center">
          <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            チャット機能は開発中です
          </h2>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            パーソナルエージェントとのチャット機能は今後のアップデートで追加されます。
          </p>
        </div>
      </div>
    </div>
  );
}
