"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import type {
  ScheduleTriggerCreate,
  ScheduleTriggerResponse,
  WebhookTriggerCreate,
  WebhookTriggerResponse,
} from "@/lib/api-client/types.gen";

// =============================================================================
// Schedule Triggers
// =============================================================================

export function useScheduleTriggers(workflowId: string) {
  const [triggers, setTriggers] = useState<ScheduleTriggerResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { authFetch } = useAuthFetch();

  const fetchTriggers = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await authFetch(
        `/api/workflows/${workflowId}/triggers/schedules`
      );
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to view triggers");
        }
        throw new Error("Failed to fetch schedule triggers");
      }
      const data = await response.json();
      setTriggers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, [authFetch, workflowId]);

  useEffect(() => {
    if (workflowId) {
      fetchTriggers();
    }
  }, [fetchTriggers, workflowId]);

  const createTrigger = async (data: ScheduleTriggerCreate) => {
    const response = await authFetch(
      `/api/workflows/${workflowId}/triggers/schedules`,
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to create triggers");
      }
      if (response.status === 400) {
        throw new Error("Invalid cron expression");
      }
      throw new Error("Failed to create schedule trigger");
    }
    const newTrigger = await response.json();
    setTriggers((prev) => [...prev, newTrigger]);
    return newTrigger as ScheduleTriggerResponse;
  };

  const deleteTrigger = async (triggerId: string) => {
    const response = await authFetch(
      `/api/workflows/${workflowId}/triggers/schedules/${triggerId}`,
      {
        method: "DELETE",
      }
    );
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to delete triggers");
      }
      throw new Error("Failed to delete schedule trigger");
    }
    setTriggers((prev) => prev.filter((t) => t.id !== triggerId));
  };

  const toggleTrigger = async (triggerId: string, isActive: boolean) => {
    const response = await authFetch(
      `/api/workflows/${workflowId}/triggers/schedules/${triggerId}/toggle`,
      {
        method: "PATCH",
        body: JSON.stringify({ is_active: isActive }),
      }
    );
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to toggle triggers");
      }
      throw new Error("Failed to toggle schedule trigger");
    }
    const updatedTrigger = await response.json();
    setTriggers((prev) =>
      prev.map((t) => (t.id === triggerId ? updatedTrigger : t))
    );
    return updatedTrigger as ScheduleTriggerResponse;
  };

  return {
    triggers,
    isLoading,
    error,
    createTrigger,
    deleteTrigger,
    toggleTrigger,
    refetch: fetchTriggers,
  };
}

// =============================================================================
// Webhook Triggers
// =============================================================================

export function useWebhookTriggers(workflowId: string) {
  const [triggers, setTriggers] = useState<WebhookTriggerResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { authFetch } = useAuthFetch();

  const fetchTriggers = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await authFetch(
        `/api/workflows/${workflowId}/triggers/webhooks`
      );
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to view triggers");
        }
        throw new Error("Failed to fetch webhook triggers");
      }
      const data = await response.json();
      setTriggers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setIsLoading(false);
    }
  }, [authFetch, workflowId]);

  useEffect(() => {
    if (workflowId) {
      fetchTriggers();
    }
  }, [fetchTriggers, workflowId]);

  const createTrigger = async (data: WebhookTriggerCreate) => {
    const response = await authFetch(
      `/api/workflows/${workflowId}/triggers/webhooks`,
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to create triggers");
      }
      if (response.status === 409) {
        throw new Error("Webhook path already exists");
      }
      throw new Error("Failed to create webhook trigger");
    }
    const newTrigger = await response.json();
    setTriggers((prev) => [...prev, newTrigger]);
    return newTrigger as WebhookTriggerResponse;
  };

  const deleteTrigger = async (triggerId: string) => {
    const response = await authFetch(
      `/api/workflows/${workflowId}/triggers/webhooks/${triggerId}`,
      {
        method: "DELETE",
      }
    );
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to delete triggers");
      }
      throw new Error("Failed to delete webhook trigger");
    }
    setTriggers((prev) => prev.filter((t) => t.id !== triggerId));
  };

  const regenerateSecret = async (triggerId: string) => {
    const response = await authFetch(
      `/api/workflows/${workflowId}/triggers/webhooks/${triggerId}/regenerate-secret`,
      {
        method: "POST",
      }
    );
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Please sign in to regenerate secret");
      }
      throw new Error("Failed to regenerate secret");
    }
    const data = await response.json();
    return data.secret as string;
  };

  return {
    triggers,
    isLoading,
    error,
    createTrigger,
    deleteTrigger,
    regenerateSecret,
    refetch: fetchTriggers,
  };
}
