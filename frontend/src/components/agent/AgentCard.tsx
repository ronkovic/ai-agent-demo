import { AgentResponse } from "@/lib/api-client/types.gen";
import { MoreVertical, Edit, Trash, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface AgentCardProps {
  agent: AgentResponse;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  className?: string;
}

export function AgentCard({
  agent,
  onClick,
  onEdit,
  onDelete,
  className,
}: AgentCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div
      className={cn(
        "group relative flex flex-col justify-between rounded-lg border bg-white p-6 shadow-sm transition-all hover:shadow-md dark:border-gray-800 dark:bg-gray-950",
        className
      )}
    >
      <div className="mb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400">
              <MessageSquare className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                {agent.name}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {agent.llm_provider} / {agent.llm_model}
              </p>
            </div>
          </div>
          <div className="relative">
            <Button
              variant="secondary"
              size="sm"
              className="h-8 w-8 p-0"
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
            {showMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 z-20 mt-2 w-32 rounded-md border bg-white py-1 shadow-lg dark:border-gray-800 dark:bg-gray-950">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowMenu(false);
                      onEdit?.();
                    }}
                    className="flex w-full items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                  >
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowMenu(false);
                      onDelete?.();
                    }}
                    className="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                  >
                    <Trash className="mr-2 h-4 w-4" />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
        <p className="mt-2 line-clamp-2 text-sm text-gray-600 dark:text-gray-300">
          {agent.description || "No description provided."}
        </p>
      </div>
      <Button onClick={onClick} className="w-full">
        Chat with Agent
      </Button>
    </div>
  );
}
