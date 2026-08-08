"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Loader2, CheckCircle2, XCircle, Circle, Play } from "lucide-react";
import type { DecisionNodeData } from "@/lib/types";

/**
 * NOTE: `NodeProps<T>` and the `Handle`/`Position` imports reflect the
 * @xyflow/react (React Flow v12) API as I understand it. Please verify the
 * generic signature of NodeProps against the installed package's types —
 * this changed between React Flow v11 and v12.
 */
function DecisionNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as unknown as DecisionNodeData;
  const status = nodeData.status ?? "pending";

  const statusConfig: Record<
    string,
    { icon: React.ReactNode; badge: "outline" | "info" | "success" | "destructive" }
  > = {
    pending: { icon: <Circle className="h-3.5 w-3.5 text-muted-foreground" />, badge: "outline" },
    running: { icon: <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-600" />, badge: "info" },
    completed: { icon: <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />, badge: "success" },
    failed: { icon: <XCircle className="h-3.5 w-3.5 text-red-600" />, badge: "destructive" },
  };

  const cfg = statusConfig[status] ?? statusConfig.pending;

  return (
    <div
      className={cn(
        "min-w-[220px] max-w-[260px] rounded-xl border-2 bg-white shadow-md transition-all",
        selected ? "border-indigo-500 shadow-lg" : "border-slate-200",
        status === "running" && "border-indigo-400 ring-4 ring-indigo-100",
        status === "completed" && "border-green-300",
        status === "failed" && "border-red-300"
      )}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!h-2.5 !w-2.5 !bg-slate-400"
      />

      <div className="flex items-center justify-between gap-2 rounded-t-[10px] bg-slate-50 px-3 py-2">
        <div className="flex items-center gap-1.5 min-w-0">
          <Play className="h-3 w-3 shrink-0 text-slate-400" />
          <span className="truncate text-xs font-semibold text-slate-700">
            {nodeData.label || "Decision Node"}
          </span>
        </div>
        {cfg.icon}
      </div>

      <div className="px-3 py-2.5">
        <p className="line-clamp-3 text-xs text-slate-600">
          {nodeData.prompt || "No prompt set — double-click to edit"}
        </p>

        {nodeData.answer && (
          <Badge variant={cfg.badge} className="mt-2">
            AI answered: {nodeData.answer}
          </Badge>
        )}
        {nodeData.error && (
          <p className="mt-2 text-[11px] text-red-600">{nodeData.error}</p>
        )}
      </div>

      <div className="flex justify-between rounded-b-[10px] border-t border-slate-100 px-3 py-1.5 text-[10px] font-medium">
        <span className="text-green-600">YES ↓</span>
        <span className="text-red-500">NO ↓</span>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        id="yes"
        style={{ left: "25%" }}
        className="!h-2.5 !w-2.5 !bg-green-500"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="no"
        style={{ left: "75%" }}
        className="!h-2.5 !w-2.5 !bg-red-500"
      />
    </div>
  );
}

export const DecisionNode = memo(DecisionNodeComponent);
