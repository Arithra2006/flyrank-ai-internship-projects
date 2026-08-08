"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type Connection,
  type NodeMouseHandler,
  MarkerType,
  BackgroundVariant,
} from "@xyflow/react";
import { v4 as uuidv4 } from "uuid";

import { DecisionNode } from "./decision-node";
import { NodeEditorDialog } from "./node-editor-dialog";
import { ExecutionLogs } from "./execution-logs";
import { Button } from "@/components/ui/button";
import {
  Plus,
  Play,
  Download,
  Upload,
  Save,
  FolderOpen,
  AlertTriangle,
} from "lucide-react";
import type {
  DecisionNodeData,
  WorkflowGraph,
  ExecutionLogEntry,
  NodeExecutionStatus,
  DecisionAnswer,
} from "@/lib/types";

/**
 * NOTE ON REACT FLOW API: This component uses `useNodesState`/`useEdgesState`,
 * `addEdge`, and the `<ReactFlow>` / `<ReactFlowProvider>` components from
 * @xyflow/react (React Flow v12). This is the pattern documented at
 * https://reactflow.dev/learn as of my training, but please diff against the
 * current docs after installing — hook return shapes and prop names have
 * shifted between major React Flow versions before.
 */

const STORAGE_KEY = "ai-decision-flow-workflow-v1";

const nodeTypes = { decision: DecisionNode };

let idCounter = 1;
function nextNodeId() {
  return `node-${idCounter++}-${uuidv4().slice(0, 4)}`;
}

const initialNodes: Node[] = [
  {
    id: "node-start",
    type: "decision",
    position: { x: 250, y: 50 },
    data: {
      label: "Is this a support request?",
      prompt: "Is this message related to technical support?",
      status: "pending",
    } satisfies DecisionNodeData,
  },
];

const initialEdges: Edge[] = [];

function FlowEditorInner() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>(initialEdges);
  const [startNodeId, setStartNodeId] = useState<string | null>("node-start");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [logs, setLogs] = useState<ExecutionLogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId) ?? null,
    [nodes, selectedNodeId]
  );

  // ---------- Node CRUD ----------

  const addNode = useCallback(() => {
    const id = nextNodeId();
    const newNode: Node = {
      id,
      type: "decision",
      position: {
        x: 150 + Math.random() * 300,
        y: 150 + nodes.length * 120,
      },
      data: {
        label: "New Decision",
        prompt: "",
        status: "pending",
      } satisfies DecisionNodeData,
    };
    setNodes((nds) => [...nds, newNode]);
  }, [nodes.length, setNodes]);

  const onNodeDoubleClick: NodeMouseHandler = useCallback((_, node) => {
    setSelectedNodeId(node.id);
    setEditorOpen(true);
  }, []);

  const saveNodeEdit = useCallback(
    (label: string, prompt: string) => {
      if (!selectedNodeId) return;
      setNodes((nds) =>
        nds.map((n) =>
          n.id === selectedNodeId
            ? { ...n, data: { ...n.data, label, prompt } }
            : n
        )
      );
    },
    [selectedNodeId, setNodes]
  );

  const deleteSelectedNode = useCallback(() => {
    if (!selectedNodeId) return;
    setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId));
    setEdges((eds) =>
      eds.filter(
        (e) => e.source !== selectedNodeId && e.target !== selectedNodeId
      )
    );
    if (startNodeId === selectedNodeId) setStartNodeId(null);
    setEditorOpen(false);
    setSelectedNodeId(null);
  }, [selectedNodeId, setNodes, setEdges, startNodeId]);

  const setSelectedAsStart = useCallback(() => {
    if (!selectedNodeId) return;
    setStartNodeId(selectedNodeId);
  }, [selectedNodeId]);

  // ---------- Edges ----------

  const onConnect = useCallback(
    (connection: Connection) => {
      // sourceHandle is "yes" or "no" from the DecisionNode's two source handles
      const branch: DecisionAnswer =
        connection.sourceHandle === "no" ? "NO" : "YES";
      const color = branch === "YES" ? "#16a34a" : "#ef4444";

      setEdges((eds) =>
        addEdge(
          {
            ...connection,
            id: `edge-${uuidv4()}`,
            label: branch,
            style: { stroke: color, strokeWidth: 2 },
            labelStyle: { fill: color, fontWeight: 600, fontSize: 11 },
            markerEnd: { type: MarkerType.ArrowClosed, color },
            data: { branch },
          },
          eds
        )
      );
    },
    [setEdges]
  );

  // ---------- Graph serialization ----------

  const toWorkflowGraph = useCallback((): WorkflowGraph => {
    return {
      nodes: nodes.map((n) => ({
        id: n.id,
        label: (n.data as unknown as DecisionNodeData).label,
        prompt: (n.data as unknown as DecisionNodeData).prompt,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        branch:
          ((e.data as { branch?: DecisionAnswer } | undefined)?.branch) ??
          (e.sourceHandle === "no" ? "NO" : "YES"),
      })),
      startNodeId,
    };
  }, [nodes, edges, startNodeId]);

  // ---------- Run workflow ----------

  const resetNodeStatuses = useCallback(
    (status: NodeExecutionStatus = "pending") => {
      setNodes((nds) =>
        nds.map((n) => ({
          ...n,
          data: { ...n.data, status, answer: undefined, error: undefined },
        }))
      );
      setEdges((eds) =>
        eds.map((e) => ({
          ...e,
          className: undefined,
        }))
      );
    },
    [setNodes, setEdges]
  );

  const runWorkflow = useCallback(async () => {
    if (!startNodeId) {
      setRunError("Set a start node before running the workflow (double-click a node → Set as start).");
      return;
    }

    setRunError(null);
    setIsRunning(true);
    setLogs([]);
    resetNodeStatuses("pending");

    const graph = toWorkflowGraph();

    // Mark the start node as running immediately for visual feedback.
    setNodes((nds) =>
      nds.map((n) =>
        n.id === startNodeId ? { ...n, data: { ...n.data, status: "running" } } : n
      )
    );

    try {
      const res = await fetch("/api/workflow/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ graph }),
      });

      const result = await res.json();

      if (!res.ok) {
        throw new Error(result?.error || "Workflow run failed");
      }

      setLogs(result.logs ?? []);

      // Apply per-node status/answer from the logs
      const answerByNode = new Map<string, DecisionAnswer>();
      const errorByNode = new Map<string, string>();
      for (const entry of result.logs as ExecutionLogEntry[]) {
        if (entry.nodeId && entry.answer) answerByNode.set(entry.nodeId, entry.answer);
        if (entry.nodeId && entry.error) errorByNode.set(entry.nodeId, entry.error);
      }

      const visitedSet = new Set<string>(result.path ?? []);
      const failedNodeId =
        result.status === "failed" && result.finalNodeId ? result.finalNodeId : null;

      setNodes((nds) =>
        nds.map((n) => {
          if (!visitedSet.has(n.id)) {
            return { ...n, data: { ...n.data, status: "pending" } };
          }
          const status: NodeExecutionStatus =
            n.id === failedNodeId ? "failed" : "completed";
          return {
            ...n,
            data: {
              ...n.data,
              status,
              answer: answerByNode.get(n.id),
              error: errorByNode.get(n.id),
            },
          };
        })
      );

      const takenEdgeIds = new Set<string>(result.edgesTaken ?? []);
      setEdges((eds) =>
        eds.map((e) => ({
          ...e,
          className: takenEdgeIds.has(e.id) ? "edge-taken" : undefined,
        }))
      );

      if (result.status === "failed") {
        setRunError(result.error || "Workflow failed");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setRunError(message);
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          nodeId: "",
          nodeLabel: "",
          prompt: "",
          status: "failed",
          message: "Workflow run request failed",
          error: message,
        },
      ]);
    } finally {
      setIsRunning(false);
    }
  }, [startNodeId, toWorkflowGraph, resetNodeStatuses, setNodes, setEdges]);

  // ---------- Save / load / export / import ----------

  const saveToLocalStorage = useCallback(() => {
    const payload = { nodes, edges, startNodeId };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, [nodes, edges, startNodeId]);

  const loadFromLocalStorage = useCallback(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      setRunError("No saved workflow found in this browser.");
      return;
    }
    try {
      const payload = JSON.parse(raw);
      setNodes(payload.nodes ?? []);
      setEdges(payload.edges ?? []);
      setStartNodeId(payload.startNodeId ?? null);
      setLogs([]);
      setRunError(null);
    } catch {
      setRunError("Saved workflow data is corrupted.");
    }
  }, [setNodes, setEdges]);

  const exportJson = useCallback(() => {
    const payload = { nodes, edges, startNodeId };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ai-decision-flow-workflow.json";
    a.click();
    URL.revokeObjectURL(url);
  }, [nodes, edges, startNodeId]);

  const triggerImport = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleImportFile = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const payload = JSON.parse(reader.result as string);
          setNodes(payload.nodes ?? []);
          setEdges(payload.edges ?? []);
          setStartNodeId(payload.startNodeId ?? null);
          setLogs([]);
          setRunError(null);
        } catch {
          setRunError("Could not parse the imported JSON file.");
        }
      };
      reader.readAsText(file);
      e.target.value = "";
    },
    [setNodes, setEdges]
  );

  return (
    <div className="flex h-screen w-full flex-col bg-slate-50">
      {/* Toolbar */}
      <header className="flex items-center gap-2 border-b bg-white px-4 py-2.5 shadow-sm">
        <h1 className="mr-4 text-sm font-bold text-slate-800">
          AI Decision Flow
        </h1>

        <Button size="sm" variant="outline" onClick={addNode}>
          <Plus className="h-3.5 w-3.5" />
          Add Node
        </Button>

        <div className="mx-2 h-5 w-px bg-slate-200" />

        <Button size="sm" variant="outline" onClick={saveToLocalStorage}>
          <Save className="h-3.5 w-3.5" />
          Save
        </Button>
        <Button size="sm" variant="outline" onClick={loadFromLocalStorage}>
          <FolderOpen className="h-3.5 w-3.5" />
          Load
        </Button>
        <Button size="sm" variant="outline" onClick={exportJson}>
          <Download className="h-3.5 w-3.5" />
          Export JSON
        </Button>
        <Button size="sm" variant="outline" onClick={triggerImport}>
          <Upload className="h-3.5 w-3.5" />
          Import JSON
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept="application/json"
          className="hidden"
          onChange={handleImportFile}
        />

        <div className="ml-auto flex items-center gap-2">
          {runError && (
            <span className="flex items-center gap-1 text-xs text-red-600">
              <AlertTriangle className="h-3.5 w-3.5" />
              {runError}
            </span>
          )}
          <Button size="sm" onClick={runWorkflow} disabled={isRunning}>
            <Play className="h-3.5 w-3.5" />
            {isRunning ? "Running..." : "Run Workflow"}
          </Button>
        </div>
      </header>

      {/* Canvas + Logs */}
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeDoubleClick={onNodeDoubleClick}
            nodeTypes={nodeTypes}
            fitView
            defaultEdgeOptions={{ animated: false }}
          >
            <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
            <Controls />
            <MiniMap pannable zoomable className="!bg-white" />
          </ReactFlow>
        </div>

        <aside className="w-[320px] shrink-0 border-l bg-white">
          <ExecutionLogs logs={logs} isRunning={isRunning} />
        </aside>
      </div>

      {selectedNode && (
        <NodeEditorDialog
          open={editorOpen}
          initialLabel={(selectedNode.data as unknown as DecisionNodeData).label}
          initialPrompt={(selectedNode.data as unknown as DecisionNodeData).prompt}
          isStartNode={selectedNode.id === startNodeId}
          onOpenChange={setEditorOpen}
          onSave={saveNodeEdit}
          onDelete={deleteSelectedNode}
          onSetStart={setSelectedAsStart}
        />
      )}
    </div>
  );
}

export function FlowEditor() {
  return (
    <ReactFlowProvider>
      <FlowEditorInner />
    </ReactFlowProvider>
  );
}
