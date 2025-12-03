"use client";

import { useState, useCallback } from "react";
import { Search, Globe } from "lucide-react";
import { PublicAgentCard } from "@/components/agent/PublicAgentCard";
import { usePublicAgents } from "@/hooks/usePublicAgents";

export default function ExploreAgentsPage() {
  const [query, setQuery] = useState("");
  const { agents, isLoading, error, search } = usePublicAgents();

  const handleSearch = useCallback(
    (value: string) => {
      setQuery(value);
      // Debounce search - only trigger after user stops typing
      const timeoutId = setTimeout(() => {
        search(value);
      }, 300);
      return () => clearTimeout(timeoutId);
    },
    [search]
  );

  return (
    <div className="container mx-auto max-w-6xl py-8 px-4">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <Globe className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            公開エージェントを探す
          </h1>
        </div>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          他のユーザーが公開しているエージェントを検索して、ワークフローで活用できます
        </p>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="エージェントを検索..."
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white pl-10 pr-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
        />
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-600 dark:border-red-900 dark:bg-red-950 dark:text-red-400">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
        </div>
      ) : agents.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Globe className="h-12 w-12 text-gray-300 dark:text-gray-700" />
          <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
            公開エージェントが見つかりません
          </h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {query
              ? "別のキーワードで検索してみてください"
              : "まだ公開されているエージェントはありません"}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <PublicAgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}
    </div>
  );
}
