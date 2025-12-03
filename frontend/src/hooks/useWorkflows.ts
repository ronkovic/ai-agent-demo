"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import type {
  WorkflowCreate,
  WorkflowResponse,
  WorkflowUpdate,
} from "@/lib/api-client/types.gen";

export function useWorkflows() {
  const [workflows, setWorkflows] = useState<WorkflowResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { authFetch } = useAuthFetch();

  const fetchWorkflows = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await authFetch("/api/workflows");
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to view workflows");
        }
        throw new Error("Failed to fetch workflows");
      }
      const data = await response.json();
      setWorkflows(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, [authFetch]);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  const createWorkflow = async (data: WorkflowCreate) => {
    const response = await authFetch("/api/workflows", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to create workflows");
      }
      throw new Error("Failed to create workflow");
    }
    const newWorkflow = await response.json();
    setWorkflows((prev) => [...prev, newWorkflow]);
    return newWorkflow as WorkflowResponse;
  };

  const updateWorkflow = async (id: string, data: WorkflowUpdate) => {
    const response = await authFetch(`/api/workflows/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to update workflows");
      }
      throw new Error("Failed to update workflow");
    }
    const updatedWorkflow = await response.json();
    setWorkflows((prev) =>
      prev.map((workflow) => (workflow.id === id ? updatedWorkflow : workflow))
    );
    return updatedWorkflow as WorkflowResponse;
  };

  const deleteWorkflow = async (id: string) => {
    const response = await authFetch(`/api/workflows/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to delete workflows");
      }
      throw new Error("Failed to delete workflow");
    }
    setWorkflows((prev) => prev.filter((workflow) => workflow.id !== id));
  };

  return {
    workflows,
    isLoading,
    error,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
    refetch: fetchWorkflows,
  };
}
