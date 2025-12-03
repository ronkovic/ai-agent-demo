"use client";

import { Bot, Cpu } from "lucide-react";
import type { PublicAgentResponse } from "@/lib/api-client/types.gen";

interface PublicAgentCardProps {
  agent: PublicAgentResponse;
}

const PROVIDER_LABELS: Record<string, string> = {
  claude: "Claude",
  openai: "OpenAI",
  bedrock: "Bedrock",
};

export function PublicAgentCard({ agent }: PublicAgentCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-gray-800 dark:bg-gray-950">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300">
          <Bot className="h-5 w-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold text-gray-900 dark:text-gray-100">
            {agent.name}
          </h3>
          {agent.description && (
            <p className="mt-1 line-clamp-2 text-sm text-gray-500 dark:text-gray-400">
              {agent.description}
            </p>
          )}
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
          <Cpu className="h-3 w-3" />
          {PROVIDER_LABELS[agent.llm_provider] || agent.llm_provider}
        </span>
      </div>

      <div className="mt-3 text-xs text-gray-400 dark:text-gray-500">
        作成日:{" "}
        {new Date(agent.created_at).toLocaleDateString("ja-JP", {
          year: "numeric",
          month: "short",
          day: "numeric",
        })}
      </div>
    </div>
  );
}
