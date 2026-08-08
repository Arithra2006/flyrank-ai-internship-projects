import { NextRequest, NextResponse } from "next/server";
import { v4 as uuidv4 } from "uuid";
import { inngest } from "@/inngest/client";
import { getDecision } from "@/lib/openai";
import type {
  WorkflowGraph,
  ExecutionLogEntry,
  WorkflowRunResult,
  DecisionAnswer,
} from "@/lib/types";

/**
 * POST /api/workflow/run
 *
 * Body: { graph: WorkflowGraph }
 *
 * This route does two things:
 *   1. Sends a "workflow/run.requested" event to Inngest so the run shows
 *      up in the Inngest dashboard / dev server as a durable, retryable
 *      background job (inngest.workflow.ts owns that execution).
 *   2. Executes the same traversal logic directly in this request handler
 *      and returns the result synchronously, so the UI can render the
 *      path/logs immediately without needing to poll Inngest's run API
 *      (which requires a signing key setup this project doesn't assume).
 *
 * If you wire up Inngest's REST API with a signing key later, you can
 * replace step 2 with a poll against the run status instead.
 */
export async function POST(req: NextRequest) {
  let body: { graph?: WorkflowGraph };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON body" },
      { status: 400 }
    );
  }

  const graph = body.graph;
  if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
    return NextResponse.json(
      { error: "Request body must include a valid `graph`" },
      { status: 400 }
    );
  }

  const runId = uuidv4();

  // Fire-and-forget event to Inngest for observability / durability.
  // Failures here should not block returning a result to the user.
  try {
    await inngest.send({
      name: "workflow/run.requested",
      data: { graph, runId },
    });
  } catch (err) {
    console.error("Failed to send Inngest event:", err);
  }

  try {
    const result = await executeWorkflow(graph, runId);
    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json(
      { runId, status: "failed", error: message },
      { status: 500 }
    );
  }
}

async function executeWorkflow(
  graph: WorkflowGraph,
  runId: string
): Promise<WorkflowRunResult> {
  const logs: ExecutionLogEntry[] = [];
  const path: string[] = [];
  const edgesTaken: string[] = [];
  const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));

  if (!graph.startNodeId || !nodeById.has(graph.startNodeId)) {
    return {
      runId,
      status: "failed",
      path,
      edgesTaken,
      logs: [
        {
          timestamp: new Date().toISOString(),
          nodeId: "",
          nodeLabel: "",
          prompt: "",
          status: "failed",
          message: "Workflow has no valid start node.",
          error: "NO_START_NODE",
        },
      ],
      finalNodeId: null,
      error: "Workflow has no valid start node. Mark a node as the start node.",
    };
  }

  logs.push({
    timestamp: new Date().toISOString(),
    nodeId: "",
    nodeLabel: "",
    prompt: "",
    status: "running",
    message: "Workflow started",
  });

  let currentNodeId: string | null = graph.startNodeId;
  let safetyCounter = 0;
  const MAX_STEPS = 100;

  while (currentNodeId && safetyCounter < MAX_STEPS) {
    safetyCounter += 1;
    const node = nodeById.get(currentNodeId);

    if (!node) {
      logs.push({
        timestamp: new Date().toISOString(),
        nodeId: currentNodeId,
        nodeLabel: "unknown",
        prompt: "",
        status: "failed",
        message: `Node ${currentNodeId} not found in graph`,
        error: "NODE_NOT_FOUND",
      });
      break;
    }

    path.push(node.id);

    let answer: DecisionAnswer | undefined;
    let error: string | undefined;
    try {
      answer = await getDecision(node.prompt);
    } catch (err) {
      error = err instanceof Error ? err.message : "Unknown error";
    }

    if (error || !answer) {
      logs.push({
        timestamp: new Date().toISOString(),
        nodeId: node.id,
        nodeLabel: node.label,
        prompt: node.prompt,
        status: "failed",
        message: `Node "${node.label}" failed to produce a decision`,
        error: error || "UNKNOWN_ERROR",
      });

      return {
        runId,
        status: "failed",
        path,
        edgesTaken,
        logs,
        finalNodeId: node.id,
        error: error || "Unknown error",
      };
    }

    logs.push({
      timestamp: new Date().toISOString(),
      nodeId: node.id,
      nodeLabel: node.label,
      prompt: node.prompt,
      answer,
      status: "completed",
      message: `Node "${node.label}" executed — AI response: ${answer}`,
    });

    const outgoingEdge = graph.edges.find(
      (e) => e.source === node.id && e.branch === answer
    );

    if (!outgoingEdge) {
      logs.push({
        timestamp: new Date().toISOString(),
        nodeId: node.id,
        nodeLabel: node.label,
        prompt: "",
        status: "completed",
        message: `No outgoing "${answer}" edge from "${node.label}" — workflow ending`,
      });
      currentNodeId = null;
      break;
    }

    edgesTaken.push(outgoingEdge.id);
    logs.push({
      timestamp: new Date().toISOString(),
      nodeId: node.id,
      nodeLabel: node.label,
      prompt: "",
      status: "completed",
      message: `Following ${answer} path to next node`,
    });

    currentNodeId = outgoingEdge.target;
  }

  if (safetyCounter >= MAX_STEPS) {
    logs.push({
      timestamp: new Date().toISOString(),
      nodeId: "",
      nodeLabel: "",
      prompt: "",
      status: "failed",
      message: "Workflow exceeded maximum step count (possible cycle)",
      error: "MAX_STEPS_EXCEEDED",
    });
    return {
      runId,
      status: "failed",
      path,
      edgesTaken,
      logs,
      finalNodeId: path.length ? path[path.length - 1] : null,
      error: "Workflow exceeded maximum step count (possible cycle in graph)",
    };
  }

  logs.push({
    timestamp: new Date().toISOString(),
    nodeId: "",
    nodeLabel: "",
    prompt: "",
    status: "completed",
    message: "Workflow completed",
  });

  return {
    runId,
    status: "completed",
    path,
    edgesTaken,
    logs,
    finalNodeId: path.length ? path[path.length - 1] : null,
  };
}
