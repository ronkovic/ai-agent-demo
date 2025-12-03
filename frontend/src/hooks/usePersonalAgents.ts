"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import type {
  PersonalAgentCreate,
  PersonalAgentResponse,
  PersonalAgentUpdate,
} from "@/lib/api-client/types.gen";

export function usePersonalAgents() {
  const [personalAgents, setPersonalAgents] = useState<PersonalAgentResponse[]>(
    []
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { authFetch } = useAuthFetch();

  const fetchPersonalAgents = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await authFetch("/api/personal-agents");
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to view personal agents");
        }
        throw new Error("Failed to fetch personal agents");
      }
      const data = await response.json();
      setPersonalAgents(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, [authFetch]);

  useEffect(() => {
    fetchPersonalAgents();
  }, [fetchPersonalAgents]);

  const createPersonalAgent = async (data: PersonalAgentCreate) => {
    const response = await authFetch("/api/personal-agents", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to create personal agents");
      }
      throw new Error("Failed to create personal agent");
    }
    const newAgent = await response.json();
    setPersonalAgents((prev) => [...prev, newAgent]);
    return newAgent;
  };

  const updatePersonalAgent = async (id: string, data: PersonalAgentUpdate) => {
    const response = await authFetch(`/api/personal-agents/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to update personal agents");
      }
      throw new Error("Failed to update personal agent");
    }
    const updatedAgent = await response.json();
    setPersonalAgents((prev) =>
      prev.map((agent) => (agent.id === id ? updatedAgent : agent))
    );
    return updatedAgent;
  };

  const deletePersonalAgent = async (id: string) => {
    const response = await authFetch(`/api/personal-agents/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to delete personal agents");
      }
      throw new Error("Failed to delete personal agent");
    }
    setPersonalAgents((prev) => prev.filter((agent) => agent.id !== id));
  };

  return {
    personalAgents,
    isLoading,
    error,
    createPersonalAgent,
    updatePersonalAgent,
    deletePersonalAgent,
    refetch: fetchPersonalAgents,
  };
}
