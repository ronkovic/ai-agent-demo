import { Code2, Globe, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ToolCallData {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface ToolResultData {
  toolCallId: string;
  success: boolean;
  output: unknown;
  error?: string;
}

interface ToolCallDisplayProps {
  toolCall: ToolCallData;
  result?: ToolResultData;
  isExecuting?: boolean;
}

const TOOL_ICONS: Record<string, typeof Code2> = {
  execute_code: Code2,
  web_search: Globe,
};

const TOOL_LABELS: Record<string, string> = {
  execute_code: "Code Execution",
  web_search: "Web Search",
};

export function ToolCallDisplay({
  toolCall,
  result,
  isExecuting,
}: ToolCallDisplayProps) {
  const Icon = TOOL_ICONS[toolCall.name] || Code2;
  const label = TOOL_LABELS[toolCall.name] || toolCall.name;

  return (
    <div className="my-2 rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-gray-200 px-3 py-2 dark:border-gray-700">
        <Icon className="h-4 w-4 text-gray-500 dark:text-gray-400" />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </span>
        {isExecuting && (
          <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
        )}
        {result && !isExecuting && (
          <>
            {result.success ? (
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
          </>
        )}
      </div>

      {/* Arguments */}
      <div className="px-3 py-2">
        <div className="text-xs font-medium text-gray-500 dark:text-gray-400">
          Arguments
        </div>
        <pre className="mt-1 max-h-32 overflow-auto rounded bg-gray-100 p-2 text-xs text-gray-700 dark:bg-gray-900 dark:text-gray-300">
          {JSON.stringify(toolCall.arguments, null, 2)}
        </pre>
      </div>

      {/* Result */}
      {result && (
        <div className="border-t border-gray-200 px-3 py-2 dark:border-gray-700">
          <div
            className={cn(
              "text-xs font-medium",
              result.success
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            )}
          >
            {result.success ? "Result" : "Error"}
          </div>
          <pre
            className={cn(
              "mt-1 max-h-48 overflow-auto rounded p-2 text-xs",
              result.success
                ? "bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-300"
                : "bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-300"
            )}
          >
            {result.success
              ? typeof result.output === "string"
                ? result.output
                : JSON.stringify(result.output, null, 2)
              : result.error}
          </pre>
        </div>
      )}
    </div>
  );
}

// Compact version for inline display
interface ToolCallBadgeProps {
  toolCall: ToolCallData;
  result?: ToolResultData;
  isExecuting?: boolean;
  onClick?: () => void;
}

export function ToolCallBadge({
  toolCall,
  result,
  isExecuting,
  onClick,
}: ToolCallBadgeProps) {
  const Icon = TOOL_ICONS[toolCall.name] || Code2;
  const label = TOOL_LABELS[toolCall.name] || toolCall.name;

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium transition-colors",
        "border border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100",
        "dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700",
        result?.success === false &&
          "border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400",
        result?.success === true &&
          "border-green-200 bg-green-50 text-green-700 dark:border-green-800 dark:bg-green-900/20 dark:text-green-400"
      )}
    >
      {isExecuting ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : (
        <Icon className="h-3 w-3" />
      )}
      <span>{label}</span>
      {result && !isExecuting && (
        <>
          {result.success ? (
            <CheckCircle2 className="h-3 w-3" />
          ) : (
            <XCircle className="h-3 w-3" />
          )}
        </>
      )}
    </button>
  );
}
