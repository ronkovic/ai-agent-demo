"use client";

import { usePersonalAgents } from "@/hooks/usePersonalAgents";
import { PersonalAgentCard } from "@/components/personal-agent/PersonalAgentCard";
import { Button } from "@/components/ui/Button";
import { Plus, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { useState } from "react";

export default function PersonalAgentListPage() {
  const { personalAgents, isLoading, deletePersonalAgent } = usePersonalAgents();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredAgents = personalAgents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (agent.description &&
        agent.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleDelete = async (id: string) => {
    if (confirm("このパーソナルエージェントを削除しますか？")) {
      await deletePersonalAgent(id);
    }
  };

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header title="パーソナルエージェント" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-5xl space-y-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative max-w-md flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500 dark:text-gray-400" />
              <input
                type="text"
                placeholder="エージェントを検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex h-10 w-full rounded-md border border-gray-300 bg-white py-2 pl-10 pr-3 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-blue-600"
              />
            </div>
            <Button onClick={() => router.push("/personal-agents/new")}>
              <Plus className="mr-2 h-4 w-4" />
              新規作成
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
          ) : filteredAgents.length === 0 ? (
            <div className="flex h-64 flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center dark:border-gray-700 dark:bg-gray-950">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                パーソナルエージェントがありません
              </h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                新しいパーソナルエージェントを作成してください。
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredAgents.map((agent) => (
                <PersonalAgentCard
                  key={agent.id}
                  agent={agent}
                  onClick={() => router.push(`/personal-agents/${agent.id}`)}
                  onEdit={() => router.push(`/personal-agents/${agent.id}/settings`)}
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
