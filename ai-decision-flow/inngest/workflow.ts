import { inngest } from "./client";
import { getDecision } from "@/lib/openai";
import type {
  WorkflowGraph,
  ExecutionLogEntry,
  WorkflowRunResult,
  DecisionAnswer,
} from "@/lib/types";

interface WorkflowRunEventData {
  graph: WorkflowGraph;
  runId: string;
}

/**
 * Executes an AI decision workflow graph.
 *
 * For each node visited:
 *   1. Run the node's prompt through the LLM as its own Inngest step
 *      (step.run gives per-node retry + observability in the Inngest
 *      dashboard, and memoizes the result if the function replays).
 *   2. Look up the outgoing edge matching the YES/NO answer.
 *   3. Move to that edge's target node, or stop if there is none.
 *
 * NOTE ON API SHAPE: `inngest.createFunction({ id, ... }, { event: "..." }, handler)`
 * and `step.run(name, fn)` reflect the Inngest SDK pattern I'm most familiar
 * with, but I have not executed this against a live install in this
 * environment. Please confirm the exact signature (especially whether your
 * installed version uses `id` or the older `name` field, and the event
 * trigger syntax) against https://www.inngest.com/docs/reference before
 * deploying.
 */
export const runDecisionWorkflow = inngest.createFunction(
  { id: "run-decision-workflow", retries: 1 },
  { event: "workflow/run.requested" },
  async ({ event, step }) => {
    const { graph, runId } = event.data as WorkflowRunEventData;
    const logs: ExecutionLogEntry[] = [];
    const path: string[] = [];
    const edgesTaken: string[] = [];

    const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));

    const pushLog = (entry: ExecutionLogEntry) => {
      logs.push(entry);
    };

    if (!graph.startNodeId || !nodeById.has(graph.startNodeId)) {
      const result: WorkflowRunResult = {
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
        error: "Workflow has no valid start node.",
      };
      return result;
    }

    pushLog({
      timestamp: new Date().toISOString(),
      nodeId: "",
      nodeLabel: "",
      prompt: "",
      status: "running",
      message: "Workflow started",
    });

    let currentNodeId: string | null = graph.startNodeId;
    let safetyCounter = 0;
    const MAX_STEPS = 100; // guard against cyclic graphs looping forever

    while (currentNodeId && safetyCounter < MAX_STEPS) {
      safetyCounter += 1;
      const node = nodeById.get(currentNodeId);

      if (!node) {
        pushLog({
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

      // Each node's AI decision runs as its own durable Inngest step.
      const stepResult = await step.run(
        `decide-${node.id}`,
        async (): Promise<{ answer?: DecisionAnswer; error?: string }> => {
          try {
            const answer = await getDecision(node.prompt);
            return { answer };
          } catch (err) {
            return {
              error: err instanceof Error ? err.message : "Unknown error",
            };
          }
        }
      );

      if (stepResult.error || !stepResult.answer) {
        pushLog({
          timestamp: new Date().toISOString(),
          nodeId: node.id,
          nodeLabel: node.label,
          prompt: node.prompt,
          status: "failed",
          message: `Node "${node.label}" failed to produce a decision`,
          error: stepResult.error || "UNKNOWN_ERROR",
        });

        const result: WorkflowRunResult = {
          runId,
          status: "failed",
          path,
          edgesTaken,
          logs,
          finalNodeId: node.id,
          error: stepResult.error || "Unknown error",
        };
        return result;
      }

      const answer = stepResult.answer;

      pushLog({
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
        pushLog({
          timestamp: new Date().toISOString(),
          nodeId: node.id,
          nodeLabel: node.label,
          prompt: node.prompt,
          status: "completed",
          message: `No outgoing "${answer}" edge from "${node.label}" — workflow ending`,
        });
        currentNodeId = null;
        break;
      }

      edgesTaken.push(outgoingEdge.id);
      pushLog({
        timestamp: new Date().toISOString(),
        nodeId: node.id,
        nodeLabel: node.label,
        prompt: "",
        status: "completed",
        message: `Following ${answer} path to next node`,
      });

      currentNodeId = outgoingEdge.target;
    }

    pushLog({
      timestamp: new Date().toISOString(),
      nodeId: "",
      nodeLabel: "",
      prompt: "",
      status: "completed",
      message: "Workflow completed",
    });

    const result: WorkflowRunResult = {
      runId,
      status: "completed",
      path,
      edgesTaken,
      logs,
      finalNodeId: path.length ? path[path.length - 1] : null,
    };
    return result;
  }
);
