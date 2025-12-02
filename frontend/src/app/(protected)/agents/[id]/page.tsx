"use client";

import { useChat } from "@/hooks/useChat";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { Header } from "@/components/layout/Header";
import { useParams, useRouter } from "next/navigation";
import { useAgents } from "@/hooks/useAgents";
import { Button } from "@/components/ui/Button";
import { Settings } from "lucide-react";

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const agentId = params?.id as string;
  
  const { agents } = useAgents();
  const agent = agents.find((a) => a.id === agentId) || null;

  const { messages, isLoading, isStreaming, sendMessage } = useChat(agentId);

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header
        title={agent ? `Chat with ${agent.name}` : "Chat"}
        showBackButton
        onBack={() => router.push("/agents")}
      />
      <div className="relative flex-1 overflow-hidden">
         {/* Settings Button Overlay */}
        <div className="absolute right-4 top-4 z-10">
            <Button
                variant="secondary"
                size="sm"
                onClick={() => router.push(`/agents/${agentId}/settings`)}
                className="shadow-sm"
            >
                <Settings className="mr-2 h-4 w-4" />
                Settings
            </Button>
        </div>
        
        <ChatContainer
          messages={messages}
          onSendMessage={sendMessage}
          isLoading={isLoading}
          isStreaming={isStreaming}
          className="h-full"
        />
      </div>
    </div>
  );
}
