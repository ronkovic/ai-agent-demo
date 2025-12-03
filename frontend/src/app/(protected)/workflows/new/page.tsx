"use client";

import { ArrowLeft, Save } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { WorkflowEditor } from "@/components/workflow/WorkflowEditor";
import { useWorkflows } from "@/hooks/useWorkflows";
import type { WorkflowEdge, WorkflowNode } from "@/lib/api-client/types.gen";

export default function NewWorkflowPage() {
  const router = useRouter();
  const { createWorkflow } = useWorkflows();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [edges, setEdges] = useState<WorkflowEdge[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  const handleChange = useCallback(
    (newNodes: WorkflowNode[], newEdges: WorkflowEdge[]) => {
      setNodes(newNodes);
      setEdges(newEdges);
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
      const workflow = await createWorkflow({
        name: name.trim(),
        description: description.trim() || undefined,
        nodes,
        edges,
        trigger_config: {},
      });
      router.push(`/workflows/${workflow.id}`);
    } catch {
      alert("ワークフローの作成に失敗しました");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <Header title="新規ワークフロー">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.push("/workflows")}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            戻る
          </Button>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="ワークフロー名"
              className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="説明（任意）"
              className="flex h-9 w-48 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
          <Button onClick={handleSave} disabled={isSaving}>
            <Save className="mr-2 h-4 w-4" />
            {isSaving ? "保存中..." : "保存"}
          </Button>
        </div>
      </Header>
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
