"use client";

import { useCallback, useState } from "react";

import { useAuth } from "@/contexts/AuthContext";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export function usePersonalAgentChat(agentId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { getAccessToken } = useAuth();

  const getAuthHeaders = useCallback(async () => {
    const token = await getAccessToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }, [getAccessToken]);

  const sendMessage = useCallback(
    async (content: string) => {
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const headers = await getAuthHeaders();
        const response = await fetch(`/api/personal-agents/${agentId}/chat/stream`, {
          method: "POST",
          headers,
          body: JSON.stringify({
            conversation_id: conversationId,
            message: content,
          }),
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error("ログインしてください");
          }
          if (response.status === 400) {
            const data = await response.json();
            throw new Error(data.detail || "リクエストエラーが発生しました");
          }
          throw new Error("メッセージの送信に失敗しました");
        }

        setIsLoading(false);
        setIsStreaming(true);

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        const assistantMessageId = (Date.now() + 1).toString();
        let assistantContent = "";

        // Initialize assistant message
        setMessages((prev) => [
          ...prev,
          {
            id: assistantMessageId,
            role: "assistant",
            content: "",
            timestamp: new Date().toLocaleTimeString(),
          },
        ]);

        if (!reader) return;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.conversation_id && !conversationId) {
                  setConversationId(data.conversation_id);
                }

                if (data.content) {
                  assistantContent += data.content;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: assistantContent }
                        : msg
                    )
                  );
                }
              } catch {
                // Simple content chunk (old format)
                if (line.slice(6).trim()) {
                  assistantContent += line.slice(6);
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: assistantContent }
                        : msg
                    )
                  );
                }
              }
            }
          }
        }
      } catch (err) {
        console.error("Chat error:", err);
        const errorMessage = err instanceof Error ? err.message : "エラーが発生しました";
        setError(errorMessage);
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: "assistant",
            content: errorMessage,
            timestamp: new Date().toLocaleTimeString(),
          },
        ]);
      } finally {
        setIsLoading(false);
        setIsStreaming(false);
      }
    },
    [agentId, conversationId, getAuthHeaders]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    isStreaming,
    sendMessage,
    conversationId,
    clearMessages,
    error,
  };
}
