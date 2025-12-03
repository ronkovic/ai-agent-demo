"use client";

import type { NodeProps } from "@xyflow/react";
import { GitBranch } from "lucide-react";

import { BaseNode } from "./BaseNode";

export interface ConditionNodeData {
  label?: string;
  conditions?: Array<{
    field: string;
    operator: "eq" | "ne" | "gt" | "lt" | "contains" | "exists";
    value?: string | number | boolean;
  }>;
  logic?: "and" | "or";
}

const operatorLabels: Record<string, string> = {
  eq: "=",
  ne: "≠",
  gt: ">",
  lt: "<",
  contains: "含む",
  exists: "存在",
};

export function ConditionNode({ data, selected }: NodeProps) {
  const nodeData = data as ConditionNodeData;
  const conditions = nodeData.conditions || [];
  const logic = nodeData.logic || "and";

  return (
    <BaseNode
      label={nodeData.label || "条件分岐"}
      icon={<GitBranch className="h-4 w-4" />}
      variant="condition"
      selected={selected}
      outputHandles={[
        { id: "true", label: "True" },
        { id: "false", label: "False" },
      ]}
    >
      <div className="space-y-1 text-xs">
        {conditions.length === 0 ? (
          <div className="text-muted-foreground">条件未設定</div>
        ) : (
          <div className="space-y-0.5">
            {conditions.map((cond, i) => (
              <div key={i} className="font-mono text-muted-foreground">
                {i > 0 && (
                  <span className="text-amber-600">
                    {logic === "and" ? " && " : " || "}
                  </span>
                )}
                {cond.field} {operatorLabels[cond.operator]}{" "}
                {cond.value !== undefined ? String(cond.value) : ""}
              </div>
            ))}
          </div>
        )}
        <div className="flex justify-between pt-1 text-muted-foreground">
          <span className="text-green-600">True ↓</span>
          <span className="text-red-600">False ↓</span>
        </div>
      </div>
    </BaseNode>
  );
}
