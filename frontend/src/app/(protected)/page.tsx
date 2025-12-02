"use client";

import { useAgents } from "@/hooks/useAgents";
import { AgentCard } from "@/components/agent/AgentCard";
import { Button } from "@/components/ui/Button";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/layout/Header";

export default function DashboardPage() {
  const { agents, isLoading, deleteAgent } = useAgents();
  const router = useRouter();

  const handleDelete = async (id: string) => {
    if (confirm("このエージェントを削除してもよろしいですか？")) {
      await deleteAgent(id);
    }
  };

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header title="ダッシュボード" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-5xl space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
                おかえりなさい
              </h2>
              <p className="text-gray-500 dark:text-gray-400">
                AIエージェントを管理し、会話を始めましょう。
              </p>
            </div>
            <Button onClick={() => router.push("/agents/new")}>
              <Plus className="mr-2 h-4 w-4" />
              エージェント作成
            </Button>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-48 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-800"
                />
              ))}
            </div>
          ) : agents.length === 0 ? (
            <div className="flex h-64 flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center dark:border-gray-700 dark:bg-gray-950">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                エージェントがまだありません
              </h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                最初のAIエージェントを作成して始めましょう。
              </p>
              <Button
                onClick={() => router.push("/agents/new")}
                className="mt-4"
                variant="secondary"
              >
                エージェント作成
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onClick={() => router.push(`/agents/${agent.id}`)}
                  onEdit={() => router.push(`/agents/${agent.id}/settings`)}
                  onDelete={() => handleDelete(agent.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
