"use client";

import { AgentResponse, PersonalAgentResponse } from "@/lib/api-client/types.gen";
import { Plus, Bot, Settings, User, Workflow, Globe } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { useRouter, usePathname } from "next/navigation";

interface SidebarProps {
  agents: AgentResponse[];
  personalAgents?: PersonalAgentResponse[];
  selectedAgentId?: string;
  onSelectAgent: (id: string) => void;
  onCreateNew: () => void;
  className?: string;
}

export function Sidebar({
  agents,
  personalAgents = [],
  selectedAgentId,
  onSelectAgent,
  onCreateNew,
  className,
}: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex h-full w-64 flex-col border-r bg-gray-50/50 dark:bg-gray-900/50",
        className
      )}
    >
      <div className="p-4">
        <Button
          onClick={onCreateNew}
          className="w-full justify-start gap-2"
          variant="primary"
        >
          <Plus className="h-4 w-4" />
          新規エージェント作成
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        {/* Workflows Section */}
        <div className="mb-4">
          <button
            onClick={() => router.push("/workflows")}
            className={cn(
              "flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm font-medium transition-colors hover:bg-gray-100 dark:hover:bg-gray-800",
              pathname.startsWith("/workflows")
                ? "bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400"
                : "text-gray-700 dark:text-gray-300"
            )}
          >
            <Workflow className="h-4 w-4" />
            <span>ワークフロー</span>
          </button>
        </div>

        {/* Personal Agents Section */}
        {personalAgents.length > 0 && (
          <>
            <div className="mb-2 px-2 text-xs font-semibold text-gray-500">
              パーソナルエージェント
            </div>
            <div className="mb-4 space-y-1">
              {personalAgents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => router.push(`/personal-agents/${agent.id}`)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm font-medium transition-colors hover:bg-gray-100 dark:hover:bg-gray-800",
                    pathname === `/personal-agents/${agent.id}`
                      ? "bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400"
                      : "text-gray-700 dark:text-gray-300"
                  )}
                >
                  <User className="h-4 w-4" />
                  <span className="truncate">{agent.name}</span>
                </button>
              ))}
            </div>
          </>
        )}

        {/* Agents Section */}
        <div className="mb-2 px-2 text-xs font-semibold text-gray-500">
          エージェント一覧
        </div>
        <div className="space-y-1">
          {agents.length === 0 ? (
            <div className="px-2 py-4 text-center text-sm text-gray-500">
              エージェントがいません
            </div>
          ) : (
            agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => onSelectAgent(agent.id)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm font-medium transition-colors hover:bg-gray-100 dark:hover:bg-gray-800",
                  selectedAgentId === agent.id
                    ? "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400"
                    : "text-gray-700 dark:text-gray-300"
                )}
              >
                <Bot className="h-4 w-4" />
                <span className="truncate">{agent.name}</span>
              </button>
            ))
          )}
        </div>

        {/* Public Agents Section */}
        <div className="mt-4">
          <button
            onClick={() => router.push("/agents/explore")}
            className={cn(
              "flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm font-medium transition-colors hover:bg-gray-100 dark:hover:bg-gray-800",
              pathname === "/agents/explore"
                ? "bg-teal-50 text-teal-600 dark:bg-teal-900/20 dark:text-teal-400"
                : "text-gray-700 dark:text-gray-300"
            )}
          >
            <Globe className="h-4 w-4" />
            <span>公開エージェント</span>
          </button>
        </div>
      </div>

      <div className="border-t p-4">
        <Button
          variant="secondary"
          className="w-full justify-start gap-2"
          onClick={() => router.push("/settings")}
        >
          <Settings className="h-4 w-4" />
          設定
        </Button>
      </div>
    </aside>
  );
}
