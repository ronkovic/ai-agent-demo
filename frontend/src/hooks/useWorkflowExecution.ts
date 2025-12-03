"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import type {
  WorkflowExecutionCreate,
  WorkflowExecutionResponse,
} from "@/lib/api-client/types.gen";

export function useWorkflowExecution(workflowId: string) {
  const [executions, setExecutions] = useState<WorkflowExecutionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { authFetch } = useAuthFetch();

  const fetchExecutions = useCallback(async () => {
    if (!workflowId) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const response = await authFetch(
        `/api/workflows/${workflowId}/executions`
      );
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to view executions");
        }
        if (response.status === 404) {
          throw new Error("Workflow not found");
        }
        throw new Error("Failed to fetch executions");
      }
      const data = await response.json();
      setExecutions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, [authFetch, workflowId]);

  useEffect(() => {
    fetchExecutions();
  }, [fetchExecutions]);

  const executeWorkflow = async (data?: WorkflowExecutionCreate) => {
    const response = await authFetch(`/api/workflows/${workflowId}/execute`, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to execute workflows");
      }
      if (response.status === 404) {
        throw new Error("Workflow not found");
      }
      throw new Error("Failed to execute workflow");
    }
    const execution = await response.json();
    setExecutions((prev) => [execution, ...prev]);
    return execution as WorkflowExecutionResponse;
  };

  const getExecution = async (executionId: string) => {
    const response = await authFetch(
      `/api/workflows/${workflowId}/executions/${executionId}`
    );
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to view execution");
      }
      if (response.status === 404) {
        throw new Error("Execution not found");
      }
      throw new Error("Failed to fetch execution");
    }
    return (await response.json()) as WorkflowExecutionResponse;
  };

  return {
    executions,
    isLoading,
    error,
    executeWorkflow,
    getExecution,
    refetch: fetchExecutions,
  };
}
