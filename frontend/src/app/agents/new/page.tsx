"use client";

import { useAgents } from "@/hooks/useAgents";
import { AgentForm } from "@/components/agent/AgentForm";
import { Header } from "@/components/layout/Header";
import { useRouter } from "next/navigation";
import { AgentCreate } from "@/lib/api-client/types.gen";
import { useState } from "react";

export default function CreateAgentPage() {
  const { createAgent } = useAgents();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: AgentCreate) => {
    try {
      setIsSubmitting(true);
      const newAgent = await createAgent(data);
      router.push(`/agents/${newAgent.id}`);
    } catch (error) {
      console.error("Failed to create agent:", error);
      alert("エージェントの作成に失敗しました。もう一度お試しください。");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header title="新規エージェント作成" showBackButton onBack={() => router.back()} />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-2xl rounded-lg border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
          <AgentForm
            onSubmit={handleSubmit}
            onCancel={() => router.back()}
            isLoading={isSubmitting}
          />
        </div>
      </div>
    </div>
  );
}
