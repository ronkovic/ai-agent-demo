"use client";

import { useCallback, useState } from "react";

import { useAuth } from "@/contexts/AuthContext";

// ツール関連の型定義
export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface ToolResult {
  toolCallId: string;
  success: boolean;
  output: unknown;
  error?: string;
}

// メッセージの型定義
export interface Message {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  timestamp?: string;
  // ツール関連
  toolCalls?: ToolCall[];
  toolResult?: ToolResult;
  isToolExecuting?: boolean;
}

export function useChat(agentId: string, initialConversationId?: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const { getAccessToken } = useAuth();

  // 認証ヘッダーを取得
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

  // ツール対応のSSEストリーミング
  const sendMessageWithTools = useCallback(
    async (content: string) => {
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const headers = await getAuthHeaders();
        const response = await fetch("/api/chat/stream/tools", {
          method: "POST",
          headers,
          body: JSON.stringify({
            agent_id: agentId,
            conversation_id: conversationId,
            message: content,
          }),
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error("Please sign in to chat");
          }
          throw new Error("Failed to send message");
        }

        setIsLoading(false);
        setIsStreaming(true);

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        // 実行中のツール呼び出しを追跡
        const pendingToolCalls = new Map<string, Message>();

        // SSEデータの処理（この関数内でのみ使用）
        const processSSEData = (data: Record<string, unknown>) => {
          // Start event - conversation_id
          if (data.conversation_id && !conversationId) {
            setConversationId(data.conversation_id as string);
          }

          // Content event
          if (data.content !== undefined) {
            const contentStr = data.content as string;
            setMessages((prev) => {
              // Check if last message is assistant without tool calls
              const lastMsg = prev[prev.length - 1];
              if (lastMsg?.role === "assistant" && !lastMsg.toolCalls) {
                // Append to existing message
                return prev.map((msg, idx) =>
                  idx === prev.length - 1
                    ? { ...msg, content: msg.content + contentStr }
                    : msg
                );
              } else {
                // Create new assistant message
                return [
                  ...prev,
                  {
                    id: Date.now().toString(),
                    role: "assistant",
                    content: contentStr,
                    timestamp: new Date().toLocaleTimeString(),
                  },
                ];
              }
            });
          }

          // Tool call event
          if (data.id && data.name && data.arguments) {
            const toolCall: ToolCall = {
              id: data.id as string,
              name: data.name as string,
              arguments: data.arguments as Record<string, unknown>,
            };

            const toolMessage: Message = {
              id: `tool-${toolCall.id}`,
              role: "assistant",
              content: `Calling ${toolCall.name}...`,
              timestamp: new Date().toLocaleTimeString(),
              toolCalls: [toolCall],
              isToolExecuting: true,
            };

            pendingToolCalls.set(toolCall.id, toolMessage);
            setMessages((prev) => [...prev, toolMessage]);
          }

          // Tool result event
          if (data.tool_call_id !== undefined) {
            const result: ToolResult = {
              toolCallId: data.tool_call_id as string,
              success: data.success as boolean,
              output: data.output,
              error: data.error as string | undefined,
            };

            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.toolCalls?.some((tc) => tc.id === result.toolCallId)) {
                  return {
                    ...msg,
                    isToolExecuting: false,
                    toolResult: result,
                    content: result.success
                      ? `${msg.toolCalls[0].name} completed`
                      : `${msg.toolCalls[0].name} failed`,
                  };
                }
                return msg;
              })
            );

            pendingToolCalls.delete(result.toolCallId);
          }
        };

        if (!reader) return;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data:")) {
              try {
                const data = JSON.parse(line.slice(5).trim());
                processSSEData(data);
              } catch {
                // Parse error, might be partial data
              }
            }
          }
        }
      } catch (error) {
        console.error("Chat error:", error);
        // Add error message
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: "assistant",
            content:
              error instanceof Error
                ? error.message
                : "An error occurred. Please try again.",
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

  // シンプルなストリーミング（後方互換性）
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

      try {
        const headers = await getAuthHeaders();
        const response = await fetch("/api/chat/stream", {
          method: "POST",
          headers,
          body: JSON.stringify({
            agent_id: agentId,
            conversation_id: conversationId,
            message: content,
          }),
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error("Please sign in to chat");
          }
          throw new Error("Failed to send message");
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
      } catch (error) {
        console.error("Chat error:", error);
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: "assistant",
            content:
              error instanceof Error
                ? error.message
                : "An error occurred. Please try again.",
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

  // メッセージをクリア
  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
  }, []);

  return {
    messages,
    isLoading,
    isStreaming,
    sendMessage,
    sendMessageWithTools,
    conversationId,
    setMessages,
    clearMessages,
  };
}
