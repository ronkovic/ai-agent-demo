"use client";

import {
  Bot,
  Calendar,
  Database,
  FileOutput,
  GitBranch,
  MousePointer,
  Send,
  Wand2,
  Webhook,
  Wrench,
} from "lucide-react";
import type { DragEvent } from "react";

import { cn } from "@/lib/utils";

interface NodeItem {
  type: string;
  subType?: string;
  label: string;
  icon: React.ElementType;
  color: string;
}

interface NodeCategory {
  name: string;
  nodes: NodeItem[];
}

const nodeCategories: NodeCategory[] = [
  {
    name: "トリガー",
    nodes: [
      {
        type: "trigger",
        subType: "manual",
        label: "手動実行",
        icon: MousePointer,
        color: "bg-green-500",
      },
      {
        type: "trigger",
        subType: "schedule",
        label: "スケジュール",
        icon: Calendar,
        color: "bg-green-500",
      },
      {
        type: "trigger",
        subType: "webhook",
        label: "Webhook",
        icon: Webhook,
        color: "bg-green-500",
      },
    ],
  },
  {
    name: "アクション",
    nodes: [
      {
        type: "agent",
        label: "エージェント",
        icon: Bot,
        color: "bg-blue-500",
      },
      {
        type: "tool",
        label: "ツール実行",
        icon: Wrench,
        color: "bg-cyan-500",
      },
      {
        type: "transform",
        label: "データ変換",
        icon: Wand2,
        color: "bg-purple-500",
      },
    ],
  },
  {
    name: "制御",
    nodes: [
      {
        type: "condition",
        label: "条件分岐",
        icon: GitBranch,
        color: "bg-amber-500",
      },
    ],
  },
  {
    name: "出力",
    nodes: [
      {
        type: "output",
        subType: "return",
        label: "結果を返す",
        icon: FileOutput,
        color: "bg-rose-500",
      },
      {
        type: "output",
        subType: "webhook",
        label: "Webhook送信",
        icon: Send,
        color: "bg-rose-500",
      },
      {
        type: "output",
        subType: "store",
        label: "データ保存",
        icon: Database,
        color: "bg-rose-500",
      },
    ],
  },
];

interface NodePaletteProps {
  className?: string;
}

export function NodePalette({ className }: NodePaletteProps) {
  const onDragStart = (
    event: DragEvent,
    nodeType: string,
    subType?: string
  ) => {
    const data = { type: nodeType, subType };
    event.dataTransfer.setData("application/reactflow", JSON.stringify(data));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div
      className={cn(
        "flex w-64 flex-col border-r border-white/20 bg-white/30 p-4 backdrop-blur-md dark:bg-gray-900/30",
        className
      )}
    >
      <h2 className="mb-4 text-sm font-semibold text-gray-900 dark:text-gray-100">
        ノードパレット
      </h2>

      <div className="space-y-4 overflow-y-auto">
        {nodeCategories.map((category) => (
          <div key={category.name}>
            <h3 className="mb-2 text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
              {category.name}
            </h3>
            <div className="space-y-1">
              {category.nodes.map((node) => {
                const Icon = node.icon;
                return (
                  <div
                    key={`${node.type}-${node.subType || ""}`}
                    draggable
                    onDragStart={(e) => onDragStart(e, node.type, node.subType)}
                    className="flex cursor-grab items-center gap-2 rounded-lg border border-white/20 bg-white/50 p-2 transition-all hover:bg-white/80 hover:shadow-md active:cursor-grabbing dark:bg-gray-800/50 dark:border-white/10 dark:hover:bg-gray-800/80"
                  >
                    <div
                      className={cn(
                        "flex h-6 w-6 items-center justify-center rounded text-white shadow-sm",
                        node.color
                      )}
                    >
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="text-sm text-gray-700 dark:text-gray-200">{node.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
