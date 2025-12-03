"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuthFetch } from "./useAuthFetch";
import type { PublicAgentResponse } from "@/lib/api-client/types.gen";

export function usePublicAgents() {
  const { authFetch, isLoading: isAuthLoading } = useAuthFetch();
  const [agents, setAgents] = useState<PublicAgentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    if (isAuthLoading) return;

    setIsLoading(true);
    setError(null);
    try {
      const res = await authFetch("/api/agents/public");
      if (!res.ok) {
        throw new Error("公開エージェントの取得に失敗しました");
      }
      const data = await res.json();
      setAgents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  }, [authFetch, isAuthLoading]);

  const search = useCallback(
    async (query: string) => {
      if (!query.trim()) {
        fetchAgents();
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const res = await authFetch(
          `/api/agents/public/search?q=${encodeURIComponent(query)}`
        );
        if (!res.ok) {
          throw new Error("検索に失敗しました");
        }
        const data = await res.json();
        setAgents(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "エラーが発生しました");
      } finally {
        setIsLoading(false);
      }
    },
    [authFetch, fetchAgents]
  );

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return { agents, isLoading, error, search, refetch: fetchAgents };
}
