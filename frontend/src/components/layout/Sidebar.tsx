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
        "flex h-full w-64 flex-col border-r border-white/20 bg-white/30 dark:bg-gray-900/30 backdrop-blur-md",
        className
      )}
    >
      <div className="p-4">
        <Button
          onClick={onCreateNew}
          className="w-full justify-start gap-2 shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-all duration-200"
          variant="primary"
        >
          <Plus className="h-4 w-4" />
          新規エージェント作成
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 space-y-6">
        {/* Workflows Section */}
        <div>
          <button
            onClick={() => router.push("/workflows")}
            className={cn(
              "flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 group",
              pathname.startsWith("/workflows")
                ? "bg-white/40 dark:bg-white/10 text-primary shadow-sm"
                : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5 hover:translate-x-1"
            )}
          >
            <Workflow className={cn("h-4 w-4 transition-transform duration-200 group-hover:scale-110", pathname.startsWith("/workflows") && "text-primary")} />
            <span>ワークフロー</span>
          </button>
        </div>

        {/* Personal Agents Section */}
        {personalAgents.length > 0 && (
          <div className="animate-fade-in">
            <div className="mb-2 px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              パーソナルエージェント
            </div>
            <div className="space-y-1">
              {personalAgents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => router.push(`/personal-agents/${agent.id}`)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 group",
                    pathname === `/personal-agents/${agent.id}`
                      ? "bg-white/40 dark:bg-white/10 text-primary shadow-sm"
                      : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5 hover:translate-x-1"
                  )}
                >
                  <User className="h-4 w-4 transition-transform duration-200 group-hover:scale-110" />
                  <span className="truncate">{agent.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Agents Section */}
        <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
          <div className="mb-2 px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            エージェント一覧
          </div>
          <div className="space-y-1">
            {agents.length === 0 ? (
              <div className="px-3 py-4 text-center text-sm text-gray-500 dark:text-gray-400 bg-white/20 dark:bg-white/5 rounded-lg border border-dashed border-gray-300 dark:border-gray-700">
                エージェントがいません
              </div>
            ) : (
              agents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => onSelectAgent(agent.id)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 group",
                    selectedAgentId === agent.id
                      ? "bg-white/40 dark:bg-white/10 text-primary shadow-sm"
                      : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5 hover:translate-x-1"
                  )}
                >
                  <Bot className="h-4 w-4 transition-transform duration-200 group-hover:scale-110" />
                  <span className="truncate">{agent.name}</span>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Public Agents Section */}
        <div className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
          <button
            onClick={() => router.push("/agents/explore")}
            className={cn(
              "flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 group",
              pathname === "/agents/explore"
                ? "bg-white/40 dark:bg-white/10 text-primary shadow-sm"
                : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5 hover:translate-x-1"
            )}
          >
            <Globe className="h-4 w-4 transition-transform duration-200 group-hover:scale-110" />
            <span>公開エージェント</span>
          </button>
        </div>
      </div>

      <div className="border-t border-white/20 p-4 bg-white/10 dark:bg-black/10">
        <Button
          variant="ghost"
          className="w-full justify-start gap-2 hover:bg-white/20 dark:hover:bg-white/5"
          onClick={() => router.push("/settings")}
        >
          <Settings className="h-4 w-4" />
          設定
        </Button>
      </div>
    </aside>
  );
}
