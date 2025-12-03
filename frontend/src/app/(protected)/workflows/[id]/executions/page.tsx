"use client";

import { ArrowLeft, Play, RefreshCw } from "lucide-react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { ExecutionDetail } from "@/components/workflow/ExecutionDetail";
import { ExecutionHistory } from "@/components/workflow/ExecutionHistory";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useWorkflowExecution } from "@/hooks/useWorkflowExecution";
import type { WorkflowExecutionResponse, WorkflowResponse } from "@/lib/api-client/types.gen";

export default function WorkflowExecutionsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const workflowId = params.id as string;
  const highlightId = searchParams.get("highlight");

  const { authFetch } = useAuthFetch();
  const { executions, isLoading, executeWorkflow, refetch } =
    useWorkflowExecution(workflowId);

  const [workflow, setWorkflow] = useState<WorkflowResponse | null>(null);
  const [selectedExecution, setSelectedExecution] =
    useState<WorkflowExecutionResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  // Fetch workflow info
  useEffect(() => {
    const fetchWorkflow = async () => {
      try {
        const response = await authFetch(`/api/workflows/${workflowId}`);
        if (response.ok) {
          const data = await response.json();
          setWorkflow(data);
        }
      } catch {
        // Ignore errors
      }
    };
    fetchWorkflow();
  }, [workflowId, authFetch]);

  // Auto-select highlighted execution
  useEffect(() => {
    if (highlightId && executions.length > 0) {
      const execution = executions.find((e) => e.id === highlightId);
      if (execution) {
        setSelectedExecution(execution);
      }
    }
  }, [highlightId, executions]);

  const handleExecute = async () => {
    try {
      setIsExecuting(true);
      const execution = await executeWorkflow();
      setSelectedExecution(execution);
    } catch {
      alert("ワークフローの実行に失敗しました");
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header title={workflow ? `${workflow.name} - 実行履歴` : "実行履歴"}>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            onClick={() => router.push(`/workflows/${workflowId}`)}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            エディタに戻る
          </Button>
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            更新
          </Button>
          <Button onClick={handleExecute} disabled={isExecuting}>
            <Play className="mr-2 h-4 w-4" />
            {isExecuting ? "実行中..." : "実行"}
          </Button>
        </div>
      </Header>

      <div className="flex flex-1 overflow-hidden">
        {/* Execution List */}
        <div className="w-96 flex-shrink-0 overflow-y-auto border-r bg-background p-4">
          <h2 className="mb-4 text-sm font-semibold text-muted-foreground">
            実行履歴
          </h2>
          <ExecutionHistory
            executions={executions}
            selectedId={selectedExecution?.id}
            onSelect={setSelectedExecution}
            isLoading={isLoading}
          />
        </div>

        {/* Execution Detail */}
        <div className="flex-1 overflow-y-auto p-6">
          {selectedExecution ? (
            <ExecutionDetail execution={selectedExecution} />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              実行を選択してください
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
