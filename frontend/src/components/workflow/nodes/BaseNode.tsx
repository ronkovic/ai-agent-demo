"use client";

import { Handle, Position } from "@xyflow/react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface BaseNodeProps {
  label: string;
  icon: ReactNode;
  children?: ReactNode;
  selected?: boolean;
  variant?: "trigger" | "agent" | "condition" | "transform" | "tool" | "output";
  hasInput?: boolean;
  hasOutput?: boolean;
  outputHandles?: { id: string; label: string; position?: number }[];
}

const variantStyles: Record<NonNullable<BaseNodeProps["variant"]>, string> = {
  trigger: "border-green-500/50 bg-green-50/80 dark:bg-green-950/30",
  agent: "border-blue-500/50 bg-blue-50/80 dark:bg-blue-950/30",
  condition: "border-amber-500/50 bg-amber-50/80 dark:bg-amber-950/30",
  transform: "border-purple-500/50 bg-purple-50/80 dark:bg-purple-950/30",
  tool: "border-cyan-500/50 bg-cyan-50/80 dark:bg-cyan-950/30",
  output: "border-rose-500/50 bg-rose-50/80 dark:bg-rose-950/30",
};

const variantIconStyles: Record<NonNullable<BaseNodeProps["variant"]>, string> =
  {
    trigger: "bg-green-500 text-white shadow-sm",
    agent: "bg-blue-500 text-white shadow-sm",
    condition: "bg-amber-500 text-white shadow-sm",
    transform: "bg-purple-500 text-white shadow-sm",
    tool: "bg-cyan-500 text-white shadow-sm",
    output: "bg-rose-500 text-white shadow-sm",
  };

export function BaseNode({
  label,
  icon,
  children,
  selected,
  variant = "agent",
  hasInput = true,
  hasOutput = true,
  outputHandles,
}: BaseNodeProps) {
  return (
    <div
      className={cn(
        "min-w-[180px] rounded-xl border bg-white/50 shadow-lg backdrop-blur-md transition-all duration-200 hover:scale-[1.02] hover:shadow-xl dark:bg-gray-900/50",
        variantStyles[variant],
        selected && "ring-2 ring-primary ring-offset-2 ring-offset-transparent"
      )}
    >
      {hasInput && (
        <Handle
          type="target"
          position={Position.Top}
          className="!h-3 !w-3 !border-2 !border-background !bg-muted-foreground"
        />
      )}

      <div className="flex items-center gap-2 border-b px-3 py-2">
        <div
          className={cn(
            "flex h-6 w-6 items-center justify-center rounded",
            variantIconStyles[variant]
          )}
        >
          {icon}
        </div>
        <span className="text-sm font-medium">{label}</span>
      </div>

      {children && <div className="px-3 py-2">{children}</div>}

      {hasOutput && !outputHandles && (
        <Handle
          type="source"
          position={Position.Bottom}
          className="!h-3 !w-3 !border-2 !border-background !bg-muted-foreground"
        />
      )}

      {outputHandles?.map((handle, index) => (
        <Handle
          key={handle.id}
          type="source"
          position={Position.Bottom}
          id={handle.id}
          className="!h-3 !w-3 !border-2 !border-background !bg-muted-foreground"
          style={{
            left: `${((index + 1) / (outputHandles.length + 1)) * 100}%`,
          }}
        />
      ))}
    </div>
  );
}
