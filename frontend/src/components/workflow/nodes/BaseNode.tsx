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
  trigger: "border-green-500 bg-green-50 dark:bg-green-950/30",
  agent: "border-blue-500 bg-blue-50 dark:bg-blue-950/30",
  condition: "border-amber-500 bg-amber-50 dark:bg-amber-950/30",
  transform: "border-purple-500 bg-purple-50 dark:bg-purple-950/30",
  tool: "border-cyan-500 bg-cyan-50 dark:bg-cyan-950/30",
  output: "border-rose-500 bg-rose-50 dark:bg-rose-950/30",
};

const variantIconStyles: Record<NonNullable<BaseNodeProps["variant"]>, string> =
  {
    trigger: "bg-green-500 text-white",
    agent: "bg-blue-500 text-white",
    condition: "bg-amber-500 text-white",
    transform: "bg-purple-500 text-white",
    tool: "bg-cyan-500 text-white",
    output: "bg-rose-500 text-white",
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
        "min-w-[180px] rounded-lg border-2 bg-background shadow-md transition-shadow",
        variantStyles[variant],
        selected && "ring-2 ring-primary ring-offset-2"
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
