export type DecisionAnswer = "YES" | "NO";

export type NodeExecutionStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

/** Data payload stored on each React Flow decision node */
export interface DecisionNodeData {
  label: string;
  prompt: string;
  status?: NodeExecutionStatus;
  answer?: DecisionAnswer;
  error?: string;
  [key: string]: unknown;
}

/** A single node in the serialized workflow graph sent to Inngest */
export interface WorkflowNode {
  id: string;
  label: string;
  prompt: string;
}

/** A single edge in the serialized workflow graph. `branch` selects
 * whether this edge is taken on a YES or NO answer from the source node. */
export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  branch: DecisionAnswer;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  startNodeId: string | null;
}

/** One entry in the execution log / history returned by the workflow run */
export interface ExecutionLogEntry {
  timestamp: string;
  nodeId: string;
  nodeLabel: string;
  prompt: string;
  answer?: DecisionAnswer;
  status: NodeExecutionStatus;
  message: string;
  error?: string;
}

export interface WorkflowRunResult {
  runId: string;
  status: "completed" | "failed";
  path: string[]; // ordered list of node ids visited
  edgesTaken: string[]; // ordered list of edge ids traversed
  logs: ExecutionLogEntry[];
  finalNodeId: string | null;
  error?: string;
}
