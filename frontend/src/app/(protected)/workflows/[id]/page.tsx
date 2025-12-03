"use client";

import { ArrowLeft, History, Play, Save, Settings } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { WorkflowEditor } from "@/components/workflow/WorkflowEditor";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useWorkflowExecution } from "@/hooks/useWorkflowExecution";
import { useWorkflows } from "@/hooks/useWorkflows";
import type {
  WorkflowEdge,
  WorkflowNode,
  WorkflowResponse,
} from "@/lib/api-client/types.gen";
import { cn } from "@/lib/utils";

export default function EditWorkflowPage() {
  const params = useParams();
  const router = useRouter();
  const workflowId = params.id as string;
  const { authFetch } = useAuthFetch();
  const { updateWorkflow } = useWorkflows();
  const { executeWorkflow } = useWorkflowExecution(workflowId);

  const [workflow, setWorkflow] = useState<WorkflowResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [edges, setEdges] = useState<WorkflowEdge[]>([]);
  const [isActive, setIsActive] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  // Fetch workflow
  useEffect(() => {
    const fetchWorkflow = async () => {
      try {
        setIsLoading(true);
        const response = await authFetch(`/api/workflows/${workflowId}`);
        if (!response.ok) {
          throw new Error("Workflow not found");
        }
        const data = await response.json();
        setWorkflow(data);
        setName(data.name);
        setDescription(data.description || "");
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
        setIsActive(data.is_active);
      } catch {
        alert("ワークフローの取得に失敗しました");
        router.push("/workflows");
      } finally {
        setIsLoading(false);
      }
    };

    fetchWorkflow();
  }, [workflowId, authFetch, router]);

  const handleChange = useCallback(
    (newNodes: WorkflowNode[], newEdges: WorkflowEdge[]) => {
      setNodes(newNodes);
      setEdges(newEdges);
      setHasChanges(true);
    },
    []
  );

  const handleSave = async () => {
    if (!name.trim()) {
      alert("ワークフロー名を入力してください");
      return;
    }

    try {
      setIsSaving(true);
      await updateWorkflow(workflowId, {
        name: name.trim(),
        description: description.trim() || undefined,
        nodes,
        edges,
        is_active: isActive,
      });
      setHasChanges(false);
    } catch {
      alert("ワークフローの保存に失敗しました");
    } finally {
      setIsSaving(false);
    }
  };

  const handleExecute = async () => {
    if (hasChanges) {
      if (!confirm("未保存の変更があります。保存してから実行しますか？")) {
        return;
      }
      await handleSave();
    }

    try {
      setIsExecuting(true);
      const execution = await executeWorkflow();
      router.push(
        `/workflows/${workflowId}/executions?highlight=${execution.id}`
      );
    } catch {
      alert("ワークフローの実行に失敗しました");
    } finally {
      setIsExecuting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground">読み込み中...</div>
      </div>
    );
  }

  if (!workflow) {
    return null;
  }

  return (
    <div className="flex h-full flex-col">
      <Header title="ワークフロー編集">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push("/workflows")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            戻る
          </Button>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setHasChanges(true);
              }}
              placeholder="ワークフロー名"
              className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>

          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowSettings(!showSettings)}
            className={cn(showSettings && "bg-accent")}
          >
            <Settings className="h-4 w-4" />
          </Button>

          <Button
            variant="outline"
            onClick={() =>
              router.push(`/workflows/${workflowId}/executions`)
            }
          >
            <History className="mr-2 h-4 w-4" />
            履歴
          </Button>

          <Button
            variant="outline"
            onClick={handleExecute}
            disabled={isExecuting}
          >
            <Play className="mr-2 h-4 w-4" />
            {isExecuting ? "実行中..." : "実行"}
          </Button>

          <Button onClick={handleSave} disabled={isSaving || !hasChanges}>
            <Save className="mr-2 h-4 w-4" />
            {isSaving ? "保存中..." : hasChanges ? "保存" : "保存済み"}
          </Button>
        </div>
      </Header>

      {showSettings && (
        <div className="border-b bg-background p-4">
          <div className="mx-auto flex max-w-2xl items-center gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium">説明</label>
              <input
                type="text"
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                  setHasChanges(true);
                }}
                placeholder="ワークフローの説明"
                className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              />
            </div>
            <div>
              <label className="text-sm font-medium">ステータス</label>
              <div className="mt-1">
                <Button
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  onClick={() => {
                    setIsActive(!isActive);
                    setHasChanges(true);
                  }}
                >
                  {isActive ? "有効" : "無効"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1">
        <WorkflowEditor
          initialNodes={nodes}
          initialEdges={edges}
          onChange={handleChange}
        />
      </div>
    </div>
  );
}
