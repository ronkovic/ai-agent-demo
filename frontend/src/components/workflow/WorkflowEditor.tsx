"use client";

import {
  addEdge,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type Node,
  type OnConnect,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useState, type DragEvent } from "react";

import type { WorkflowEdge, WorkflowNode } from "@/lib/api-client/types.gen";

import { NodeConfigPanel } from "./NodeConfigPanel";
import { NodePalette } from "./NodePalette";
import { nodeTypes } from "./nodes";

interface WorkflowEditorProps {
  initialNodes?: WorkflowNode[];
  initialEdges?: WorkflowEdge[];
  onChange?: (nodes: WorkflowNode[], edges: WorkflowEdge[]) => void;
  readOnly?: boolean;
}

// Convert API types to React Flow types
function toReactFlowNodes(apiNodes: WorkflowNode[]): Node[] {
  return apiNodes.map((node) => ({
    id: node.id,
    type: node.type,
    position: node.position,
    data: node.data,
  }));
}

function toReactFlowEdges(apiEdges: WorkflowEdge[]): Edge[] {
  return apiEdges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.sourceHandle ?? undefined,
    targetHandle: edge.targetHandle ?? undefined,
  }));
}

// Convert React Flow types back to API types
function toApiNodes(nodes: Node[]): WorkflowNode[] {
  return nodes.map((node) => ({
    id: node.id,
    type: node.type || "agent",
    position: node.position,
    data: node.data as Record<string, unknown>,
  }));
}

function toApiEdges(edges: Edge[]): WorkflowEdge[] {
  return edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.sourceHandle ?? null,
    targetHandle: edge.targetHandle ?? null,
  }));
}

let nodeId = 0;
function getNodeId() {
  return `node_${Date.now()}_${nodeId++}`;
}

export function WorkflowEditor({
  initialNodes = [],
  initialEdges = [],
  onChange,
  readOnly = false,
}: WorkflowEditorProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    toReactFlowNodes(initialNodes)
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    toReactFlowEdges(initialEdges)
  );
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Notify parent of changes
  const notifyChange = useCallback(
    (newNodes: Node[], newEdges: Edge[]) => {
      if (onChange) {
        onChange(toApiNodes(newNodes), toApiEdges(newEdges));
      }
    },
    [onChange]
  );

  // Handle connection between nodes
  const onConnect: OnConnect = useCallback(
    (connection: Connection) => {
      const newEdges = addEdge(
        {
          ...connection,
          id: `edge_${Date.now()}`,
        },
        edges
      );
      setEdges(newEdges);
      notifyChange(nodes, newEdges);
    },
    [edges, nodes, setEdges, notifyChange]
  );

  // Handle node changes
  const handleNodesChange = useCallback(
    (changes: Parameters<typeof onNodesChange>[0]) => {
      onNodesChange(changes);
      // Get updated nodes after change
      const updatedNodes = [...nodes];
      changes.forEach((change) => {
        if (change.type === "position" && change.position) {
          const idx = updatedNodes.findIndex((n) => n.id === change.id);
          if (idx !== -1) {
            updatedNodes[idx] = {
              ...updatedNodes[idx],
              position: change.position,
            };
          }
        }
        if (change.type === "remove") {
          const idx = updatedNodes.findIndex((n) => n.id === change.id);
          if (idx !== -1) {
            updatedNodes.splice(idx, 1);
          }
        }
      });
      notifyChange(updatedNodes, edges);
    },
    [nodes, edges, onNodesChange, notifyChange]
  );

  // Handle edge changes
  const handleEdgesChange = useCallback(
    (changes: Parameters<typeof onEdgesChange>[0]) => {
      onEdgesChange(changes);
      const updatedEdges = [...edges];
      changes.forEach((change) => {
        if (change.type === "remove") {
          const idx = updatedEdges.findIndex((e) => e.id === change.id);
          if (idx !== -1) {
            updatedEdges.splice(idx, 1);
          }
        }
      });
      notifyChange(nodes, updatedEdges);
    },
    [nodes, edges, onEdgesChange, notifyChange]
  );

  // Handle node selection
  const onSelectionChange = useCallback(
    ({ nodes: selectedNodes }: { nodes: Node[] }) => {
      if (selectedNodes.length === 1) {
        setSelectedNode(selectedNodes[0]);
      } else {
        setSelectedNode(null);
      }
    },
    []
  );

  // Handle dropping a node from the palette
  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const dataStr = event.dataTransfer.getData("application/reactflow");
      if (!dataStr) return;

      const { type, subType } = JSON.parse(dataStr);

      // Get the position relative to the canvas
      const reactFlowBounds = (
        event.target as HTMLElement
      ).getBoundingClientRect();
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };

      // Create node data based on type
      let data: Record<string, unknown> = {};
      if (type === "trigger" && subType) {
        data = { trigger_type: subType };
      } else if (type === "output" && subType) {
        data = { output_type: subType };
      } else if (type === "transform") {
        data = { transform_type: "jmespath" };
      }

      const newNode: Node = {
        id: getNodeId(),
        type,
        position,
        data,
      };

      const newNodes = [...nodes, newNode];
      setNodes(newNodes);
      notifyChange(newNodes, edges);
    },
    [nodes, edges, setNodes, notifyChange]
  );

  // Handle node data update from config panel
  const handleNodeUpdate = useCallback(
    (nodeId: string, data: Record<string, unknown>) => {
      const newNodes = nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: { ...node.data, ...data },
          };
        }
        return node;
      });
      setNodes(newNodes);
      notifyChange(newNodes, edges);

      // Update selected node
      const updated = newNodes.find((n) => n.id === nodeId);
      if (updated) {
        setSelectedNode(updated);
      }
    },
    [nodes, edges, setNodes, notifyChange]
  );

  return (
    <div className="flex h-full">
      {!readOnly && <NodePalette />}

      <div className="relative flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={readOnly ? undefined : handleNodesChange}
          onEdgesChange={readOnly ? undefined : handleEdgesChange}
          onConnect={readOnly ? undefined : onConnect}
          onSelectionChange={onSelectionChange}
          onDragOver={onDragOver}
          onDrop={onDrop}
          nodeTypes={nodeTypes}
          fitView
          deleteKeyCode={readOnly ? null : "Backspace"}
          selectionKeyCode={null}
          multiSelectionKeyCode={null}
          panOnScroll
          zoomOnScroll
          className="bg-gray-50 dark:bg-gray-900"
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          <Controls />
          <MiniMap
            nodeStrokeWidth={3}
            zoomable
            pannable
            className="!bg-background !border !border-border"
          />
        </ReactFlow>
      </div>

      {!readOnly && selectedNode && (
        <NodeConfigPanel
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          onUpdate={handleNodeUpdate}
        />
      )}
    </div>
  );
}
