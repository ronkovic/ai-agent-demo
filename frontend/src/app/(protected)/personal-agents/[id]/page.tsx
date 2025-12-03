"use client";

import { use, useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { Settings, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { usePersonalAgentChat } from "@/hooks/usePersonalAgentChat";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import type { PersonalAgentResponse } from "@/lib/api-client/types.gen";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function PersonalAgentChatPage({ params }: PageProps) {
  const { id } = use(params);
  const router = useRouter();
  const { authFetch } = useAuthFetch();
  const [agent, setAgent] = useState<PersonalAgentResponse | null>(null);
  const [isLoadingAgent, setIsLoadingAgent] = useState(true);

  const {
    messages,
    isLoading,
    isStreaming,
    sendMessage,
    clearMessages,
    error,
  } = usePersonalAgentChat(id);

  useEffect(() => {
    const fetchAgent = async () => {
      try {
        const response = await authFetch(`/api/personal-agents/${id}`);
        if (response.ok) {
          const data = await response.json();
          setAgent(data);
        }
      } catch (err) {
        console.error("Failed to fetch agent:", err);
      } finally {
        setIsLoadingAgent(false);
      }
    };

    fetchAgent();
  }, [id, authFetch]);

  // Convert messages to ChatContainer format
  const chatMessages = messages.map((msg) => ({
    id: msg.id,
    role: msg.role as "user" | "assistant",
    content: msg.content,
    timestamp: msg.timestamp,
  }));

  if (isLoadingAgent) {
    return (
      <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
        <Header title="読み込み中..." />
        <div className="flex flex-1 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header
        title={agent?.name || "パーソナルエージェント"}
        actions={
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <Button
                variant="secondary"
                size="sm"
                onClick={clearMessages}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                クリア
              </Button>
            )}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => router.push(`/personal-agents/${id}/settings`)}
            >
              <Settings className="mr-2 h-4 w-4" />
              設定
            </Button>
          </div>
        }
      />
      {error && (
        <div className="mx-4 mt-2 rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-400">
          {error}
        </div>
      )}
      <ChatContainer
        messages={chatMessages}
        onSendMessage={sendMessage}
        isLoading={isLoading}
        isStreaming={isStreaming}
        className="flex-1"
      />
    </div>
  );
}
