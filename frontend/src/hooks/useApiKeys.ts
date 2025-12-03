"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import type {
  UserApiKeyCreate,
  UserApiKeyCreated,
  UserApiKeyResponse,
} from "@/lib/api-client/types.gen";

export function useApiKeys() {
  const [apiKeys, setApiKeys] = useState<UserApiKeyResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { authFetch } = useAuthFetch();

  const fetchApiKeys = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await authFetch("/api/user/api-keys");
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to view API keys");
        }
        throw new Error("Failed to fetch API keys");
      }
      const data = await response.json();
      setApiKeys(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, [authFetch]);

  useEffect(() => {
    fetchApiKeys();
  }, [fetchApiKeys]);

  const createApiKey = async (
    data: UserApiKeyCreate
  ): Promise<UserApiKeyCreated> => {
    const response = await authFetch("/api/user/api-keys", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to create API key");
      }
      throw new Error("Failed to create API key");
    }
    const newKey: UserApiKeyCreated = await response.json();
    // Add to list (without the full key, just the response version)
    setApiKeys((prev) => [
      ...prev,
      {
        id: newKey.id,
        user_id: "", // Will be filled on refetch
        name: newKey.name,
        key_prefix: newKey.key_prefix,
        scopes: newKey.scopes,
        rate_limit: newKey.rate_limit,
        expires_at: newKey.expires_at,
        last_used_at: null,
        created_at: newKey.created_at,
      },
    ]);
    return newKey;
  };

  const deleteApiKey = async (id: string) => {
    const response = await authFetch(`/api/user/api-keys/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to delete API key");
      }
      throw new Error("Failed to delete API key");
    }
    setApiKeys((prev) => prev.filter((key) => key.id !== id));
  };

  return {
    apiKeys,
    isLoading,
    error,
    createApiKey,
    deleteApiKey,
    refetch: fetchApiKeys,
  };
}
