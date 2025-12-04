"use client";

import { Play, Plus, Search, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { useWorkflows } from "@/hooks/useWorkflows";
import { cn } from "@/lib/utils";

export default function WorkflowListPage() {
  const { workflows, isLoading, deleteWorkflow } = useWorkflows();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredWorkflows = workflows.filter(
    (workflow) =>
      workflow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (workflow.description &&
        workflow.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("このワークフローを削除しますか？")) {
      await deleteWorkflow(id);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="flex h-full flex-col">
      <Header title="ワークフロー" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-5xl space-y-8 animate-slide-up">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative max-w-md flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500 dark:text-gray-400" />
              <input
                type="text"
                placeholder="ワークフローを検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex h-10 w-full rounded-xl border border-white/20 bg-white/50 dark:bg-gray-900/50 pl-10 pr-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-white/10 dark:placeholder:text-gray-400 dark:focus-visible:ring-primary backdrop-blur-sm transition-all duration-200"
              />
            </div>
            <Button onClick={() => router.push("/workflows/new")} className="shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-all duration-200">
              <Plus className="mr-2 h-4 w-4" />
              新規作成
            </Button>
          </div>

          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-24 animate-pulse rounded-xl bg-white/20 dark:bg-white/5 border border-white/10"
                />
              ))}
            </div>
          ) : filteredWorkflows.length === 0 ? (
            <div className="glass-card flex h-64 flex-col items-center justify-center p-8 text-center">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                ワークフローがありません
              </h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                新しいワークフローを作成してください。
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredWorkflows.map((workflow) => (
                <div
                  key={workflow.id}
                  onClick={() => router.push(`/workflows/${workflow.id}`)}
                  className="glass-card cursor-pointer p-6 hover:scale-[1.01] transition-all duration-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                          {workflow.name}
                        </h3>
                        <span
                          className={cn(
                            "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                            workflow.is_active
                              ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                              : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400"
                          )}
                        >
                          {workflow.is_active ? "有効" : "無効"}
                        </span>
                      </div>
                      {workflow.description && (
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                          {workflow.description}
                        </p>
                      )}
                      <div className="mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>ノード数: {workflow.nodes?.length || 0}</span>
                        <span>更新: {formatDate(workflow.updated_at)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/workflows/${workflow.id}/executions`);
                        }}
                        title="実行履歴"
                        className="hover:bg-white/20 dark:hover:bg-white/10"
                      >
                        <Play className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => handleDelete(workflow.id, e)}
                        title="削除"
                        className="hover:bg-red-100 dark:hover:bg-red-900/20 text-red-500"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
