import { useState, useEffect, useCallback } from "react";
import { AgentResponse, AgentCreate, AgentUpdate } from "@/lib/api-client/types.gen";

export function useAgents() {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/agents");
      if (!response.ok) throw new Error("Failed to fetch agents");
      const data = await response.json();
      setAgents(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const createAgent = async (data: AgentCreate) => {
    const response = await fetch("/api/agents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to create agent");
    const newAgent = await response.json();
    setAgents((prev) => [...prev, newAgent]);
    return newAgent;
  };

  const updateAgent = async (id: string, data: AgentUpdate) => {
    const response = await fetch(`/api/agents/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to update agent");
    const updatedAgent = await response.json();
    setAgents((prev) =>
      prev.map((agent) => (agent.id === id ? updatedAgent : agent))
    );
    return updatedAgent;
  };

  const deleteAgent = async (id: string) => {
    const response = await fetch(`/api/agents/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete agent");
    setAgents((prev) => prev.filter((agent) => agent.id !== id));
  };

  return {
    agents,
    isLoading,
    error,
    createAgent,
    updateAgent,
    deleteAgent,
    refetch: fetchAgents,
  };
}
