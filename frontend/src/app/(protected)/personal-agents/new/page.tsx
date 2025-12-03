"use client";

import { PersonalAgentForm } from "@/components/personal-agent/PersonalAgentForm";
import { usePersonalAgents } from "@/hooks/usePersonalAgents";
import { Header } from "@/components/layout/Header";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { PersonalAgentCreate } from "@/lib/api-client/types.gen";

export default function NewPersonalAgentPage() {
  const { createPersonalAgent } = usePersonalAgents();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: PersonalAgentCreate) => {
    try {
      setIsLoading(true);
      const agent = await createPersonalAgent(data);
      router.push(`/personal-agents/${agent.id}`);
    } catch (error) {
      console.error("Failed to create personal agent:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header title="新規パーソナルエージェント" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-2xl">
          <div className="rounded-lg border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
            <PersonalAgentForm
              onSubmit={handleSubmit}
              onCancel={() => router.push("/personal-agents")}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
