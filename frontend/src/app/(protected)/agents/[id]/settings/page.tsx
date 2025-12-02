"use client";

import { useAgents } from "@/hooks/useAgents";
import { AgentForm } from "@/components/agent/AgentForm";
import { Header } from "@/components/layout/Header";
import { useRouter, useParams } from "next/navigation";
import { AgentCreate, AgentResponse } from "@/lib/api-client/types.gen";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Trash } from "lucide-react";

export default function AgentSettingsPage() {
  const params = useParams();
  const router = useRouter();
  const agentId = params?.id as string;
  
  const { agents, updateAgent, deleteAgent } = useAgents();
  const [agent, setAgent] = useState<AgentResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (agents.length > 0 && agentId) {
      const found = agents.find((a) => a.id === agentId);
      if (found) setAgent(found);
    }
  }, [agents, agentId]);

  const handleSubmit = async (data: AgentCreate) => {
    try {
      setIsSubmitting(true);
      await updateAgent(agentId, data);
      router.push(`/agents/${agentId}`);
    } catch (error) {
      console.error("Failed to update agent:", error);
      alert("Failed to update agent. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete this agent? This action cannot be undone.")) {
      try {
        await deleteAgent(agentId);
        router.push("/agents");
      } catch (error) {
        console.error("Failed to delete agent:", error);
        alert("Failed to delete agent.");
      }
    }
  };

  if (!agent) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-500">Loading agent...</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header
        title="Agent Settings"
        showBackButton
        onBack={() => router.push(`/agents/${agentId}`)}
      />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-2xl space-y-8">
          <div className="rounded-lg border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
            <h2 className="mb-6 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Edit Agent
            </h2>
            <AgentForm
              initialData={agent}
              onSubmit={handleSubmit}
              onCancel={() => router.back()}
              isLoading={isSubmitting}
            />
          </div>

          <div className="rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-900/50 dark:bg-red-900/10">
            <h3 className="text-lg font-medium text-red-900 dark:text-red-200">
              Danger Zone
            </h3>
            <p className="mt-2 text-sm text-red-700 dark:text-red-300">
              Deleting this agent will permanently remove it and all associated conversations.
            </p>
            <Button
              onClick={handleDelete}
              className="mt-4 bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600"
            >
              <Trash className="mr-2 h-4 w-4" />
              Delete Agent
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
