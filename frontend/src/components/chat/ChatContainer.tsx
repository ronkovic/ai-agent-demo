import { useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { cn } from "@/lib/utils";
import type { ToolCallData, ToolResultData } from "./ToolCall";

interface Message {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  timestamp?: string;
  // Tool support
  toolCalls?: ToolCallData[];
  toolResult?: ToolResultData;
  isToolExecuting?: boolean;
}

interface ChatContainerProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  isStreaming?: boolean;
  className?: string;
}

export function ChatContainer({
  messages,
  onSendMessage,
  isLoading,
  isStreaming,
  className,
}: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  return (
    <div className={cn("flex h-full flex-col", className)}>
      <div className="flex-1 overflow-y-auto p-4">
        <div className="mx-auto max-w-3xl space-y-4">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center text-gray-500">
              <p className="text-lg font-semibold">Welcome!</p>
              <p>Start a conversation with your agent.</p>
            </div>
          ) : (
            messages
              .filter((msg) => msg.role !== "tool")
              .map((msg) => (
                <ChatMessage
                  key={msg.id}
                  role={msg.role as "user" | "assistant"}
                  content={msg.content}
                  timestamp={msg.timestamp}
                  isStreaming={isStreaming && msg.id === messages[messages.length - 1].id}
                  toolCalls={msg.toolCalls}
                  toolResult={msg.toolResult}
                  isToolExecuting={msg.isToolExecuting}
                />
              ))
          )}
          {isLoading && (
            <div className="flex justify-start">
               <div className="flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                 <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-0" />
                 <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-150" />
                 <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-300" />
               </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="border-t bg-white p-4 dark:bg-gray-950">
        <div className="mx-auto max-w-3xl">
          <ChatInput onSend={onSendMessage} disabled={isLoading || isStreaming} />
        </div>
      </div>
    </div>
  );
}
