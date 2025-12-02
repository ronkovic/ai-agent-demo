import ReactMarkdown from "react-markdown";
import { User, Bot } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  ToolCallDisplay,
  type ToolCallData,
  type ToolResultData,
} from "./ToolCall";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
  // Tool support
  toolCalls?: ToolCallData[];
  toolResult?: ToolResultData;
  isToolExecuting?: boolean;
}

export function ChatMessage({
  role,
  content,
  timestamp,
  isStreaming,
  toolCalls,
  toolResult,
  isToolExecuting,
}: ChatMessageProps) {
  const isUser = role === "user";
  const hasToolCalls = toolCalls && toolCalls.length > 0;

  return (
    <div
      className={cn(
        "flex w-full gap-4 p-4",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border",
          isUser
            ? "bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400"
            : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
        )}
      >
        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </div>

      <div
        className={cn(
          "flex max-w-[80%] flex-col gap-2",
          isUser ? "items-end" : "items-start"
        )}
      >
        {/* Tool calls display */}
        {hasToolCalls ? (
          <div className="w-full">
            {toolCalls.map((toolCall) => (
              <ToolCallDisplay
                key={toolCall.id}
                toolCall={toolCall}
                result={toolResult}
                isExecuting={isToolExecuting}
              />
            ))}
          </div>
        ) : (
          <div
            className={cn(
              "rounded-lg px-4 py-2 text-sm",
              isUser
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100"
            )}
          >
            {isUser ? (
              <div className="whitespace-pre-wrap">{content}</div>
            ) : (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            )}
            {isStreaming && (
              <span className="ml-1 inline-block h-2 w-2 animate-pulse rounded-full bg-current" />
            )}
          </div>
        )}
        {timestamp && (
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {timestamp}
          </span>
        )}
      </div>
    </div>
  );
}
