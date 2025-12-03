"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import type {
  UserLLMConfigCreate,
  UserLLMConfigResponse,
} from "@/lib/api-client/types.gen";

export function useLLMConfigs() {
  const [configs, setConfigs] = useState<UserLLMConfigResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { authFetch } = useAuthFetch();

  const fetchConfigs = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await authFetch("/api/user/llm-configs");
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to view LLM configs");
        }
        throw new Error("Failed to fetch LLM configs");
      }
      const data = await response.json();
      setConfigs(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, [authFetch]);

  useEffect(() => {
    fetchConfigs();
  }, [fetchConfigs]);

  const addConfig = async (data: UserLLMConfigCreate) => {
    const response = await authFetch("/api/user/llm-configs", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to add LLM config");
      }
      if (response.status === 409) {
        throw new Error("LLM config for this provider already exists");
      }
      throw new Error("Failed to add LLM config");
    }
    const newConfig = await response.json();
    setConfigs((prev) => [...prev, newConfig]);
    return newConfig;
  };

  const deleteConfig = async (id: string) => {
    const response = await authFetch(`/api/user/llm-configs/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to delete LLM config");
      }
      throw new Error("Failed to delete LLM config");
    }
    setConfigs((prev) => prev.filter((config) => config.id !== id));
  };

  return {
    configs,
    isLoading,
    error,
    addConfig,
    deleteConfig,
    refetch: fetchConfigs,
  };
}
