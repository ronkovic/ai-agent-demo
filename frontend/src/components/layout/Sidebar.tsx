import { AgentResponse } from "@/lib/api-client/types.gen";
import { Plus, Bot } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";

interface SidebarProps {
  agents: AgentResponse[];
  selectedAgentId?: string;
  onSelectAgent: (id: string) => void;
  onCreateNew: () => void;
  className?: string;
}

export function Sidebar({
  agents,
  selectedAgentId,
  onSelectAgent,
  onCreateNew,
  className,
}: SidebarProps) {
  return (
    <div
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
      </div>

      <div className="border-t p-4">
        {/* User profile or settings could go here */}
      </div>
    </div>
  );
}
