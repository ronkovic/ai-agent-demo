import { useState } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export function useChat(agentId: string, initialConversationId?: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null
  );

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_id: agentId,
          conversation_id: conversationId,
          message: content,
        }),
      });

      if (!response.ok) throw new Error("Failed to send message");

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
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      // Handle error (e.g. show toast)
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  return {
    messages,
    isLoading,
    isStreaming,
    sendMessage,
    conversationId,
    setMessages, // Exposed for initial loading if needed
  };
}
