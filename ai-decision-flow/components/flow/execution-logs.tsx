"use client";

import { useEffect, useRef } from "react";
import type { ExecutionLogEntry } from "@/lib/types";
import { cn } from "@/lib/utils";
import { CheckCircle2, XCircle, Loader2, Terminal } from "lucide-react";

interface ExecutionLogsProps {
  logs: ExecutionLogEntry[];
  isRunning: boolean;
}

export function ExecutionLogs({ logs, isRunning }: ExecutionLogsProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs.length]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b px-4 py-2.5">
        <Terminal className="h-4 w-4 text-slate-500" />
        <h2 className="text-sm font-semibold text-slate-700">Execution Logs</h2>
        {isRunning && (
          <span className="ml-auto flex items-center gap-1.5 text-xs text-indigo-600">
            <Loader2 className="h-3 w-3 animate-spin" />
            Running
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3 font-mono text-xs">
        {logs.length === 0 ? (
          <p className="text-slate-400">
            No execution yet. Click &quot;Run Workflow&quot; to start.
          </p>
        ) : (
          <ul className="space-y-1.5">
            {logs.map((log, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-0.5 shrink-0">
                  {log.status === "failed" ? (
                    <XCircle className="h-3.5 w-3.5 text-red-500" />
                  ) : log.status === "completed" ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                  ) : (
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-500" />
                  )}
                </span>
                <div className="min-w-0">
                  <p
                    className={cn(
                      "break-words",
                      log.status === "failed" ? "text-red-600" : "text-slate-700"
                    )}
                  >
                    {log.message}
                  </p>
                  {log.error && (
                    <p className="break-words text-[11px] text-red-500">
                      {log.error}
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
