"use client";

import { use, useEffect, useState } from "react";
import { PersonalAgentForm } from "@/components/personal-agent/PersonalAgentForm";
import { usePersonalAgents } from "@/hooks/usePersonalAgents";
import { Header } from "@/components/layout/Header";
import { useRouter } from "next/navigation";
import type {
  PersonalAgentCreate,
  PersonalAgentResponse,
} from "@/lib/api-client/types.gen";
import { Loader2 } from "lucide-react";
import { useAuthFetch } from "@/hooks/useAuthFetch";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function PersonalAgentSettingsPage({ params }: PageProps) {
  const { id } = use(params);
  const { updatePersonalAgent } = usePersonalAgents();
  const router = useRouter();
  const { authFetch } = useAuthFetch();
  const [agent, setAgent] = useState<PersonalAgentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const fetchAgent = async () => {
      try {
        const response = await authFetch(`/api/personal-agents/${id}`);
        if (response.ok) {
          const data = await response.json();
          setAgent(data);
        }
      } catch (error) {
        console.error("Failed to fetch personal agent:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAgent();
  }, [id, authFetch]);

  const handleSubmit = async (data: PersonalAgentCreate) => {
    try {
      setIsSaving(true);
      await updatePersonalAgent(id, data);
      router.push(`/personal-agents/${id}`);
    } catch (error) {
      console.error("Failed to update personal agent:", error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
        <Header title="設定" />
        <div className="flex flex-1 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
        <Header title="設定" />
        <div className="flex flex-1 items-center justify-center">
          <p className="text-gray-500 dark:text-gray-400">
            エージェントが見つかりません
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header title={`${agent.name} - 設定`} />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-2xl">
          <div className="rounded-lg border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
            <PersonalAgentForm
              initialData={agent}
              onSubmit={handleSubmit}
              onCancel={() => router.push(`/personal-agents/${id}`)}
              isLoading={isSaving}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
