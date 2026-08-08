# AI Decision Flow

A visual workflow builder where each node sends a prompt to an LLM, gets back
YES or NO, and the workflow branches to the next node accordingly. Built with
Next.js, React Flow (`@xyflow/react`), Inngest, the OpenAI SDK, and shadcn-style
UI components.

## ⚠️ Important: this project was generated without network access

This codebase was written directly (no `npm install` / `create-next-app` was run,
and no build or test was executed) because the environment it was built in has
no internet access. That means:

- **No dependency has been installed or version-resolved.** `package.json`
  lists versions I believe are reasonable, but I have not confirmed they
  exist or are mutually compatible.
- **No code here has been compiled, type-checked, or run.** There may be
  typos or minor API mismatches, especially around React Flow v12 and the
  Inngest SDK, both of which have changed their APIs across versions.
- **Model name**: a web search I ran while building this indicated that
  `gpt-4o-mini` was retired from OpenAI's lineup in February 2026 and that
  `gpt-5-mini` is the suggested replacement — the default model is set to
  `gpt-5-mini` accordingly, but please confirm current model availability at
  https://platform.openai.com/docs/models before running this.

**Before treating this as done: run `npm install`, then `npm run dev`, and
fix any errors that surface.** Given the scope of this project (multiple
files, three external SDKs), some iteration is normal and expected — this is
a strong first draft, not a guaranteed-working build.

## Setup

```bash
npm install
cp .env.local.example .env.local
# edit .env.local and add your real OPENAI_API_KEY
npm run dev
```

Open http://localhost:3000.

### Running Inngest locally (optional but recommended)

To see workflow runs in the Inngest dev dashboard:

```bash
npx inngest-cli@latest dev
```

Then follow its instructions to point it at `http://localhost:3000/api/inngest`.
Verify this command and flow against https://www.inngest.com/docs/dev-server
since the CLI has changed over time.

## How it works

- **`components/flow/flow-editor.tsx`** — the React Flow canvas: add nodes,
  connect YES/NO handles, edit prompts, run the workflow, save/load, export/
  import JSON.
- **`components/flow/decision-node.tsx`** — custom node UI showing prompt,
  status (pending/running/completed/failed), and the AI's answer.
- **`app/api/workflow/run/route.ts`** — receives the serialized graph, sends
  an event to Inngest for durable/observable execution, and also runs the
  same traversal synchronously so the UI gets an immediate result without
  needing Inngest's signed REST API for polling.
- **`inngest/workflow.ts`** — the Inngest function (`runDecisionWorkflow`)
  that performs the same graph traversal as a durable background job, with
  each node's AI call wrapped in its own `step.run` for retry/observability.
- **`lib/openai.ts`** — sends each node's prompt to the LLM with a system
  prompt constraining it to answer only YES or NO, with one retry if the
  response can't be normalized.

## Known gaps / things to verify yourself

1. **Inngest event delivery without a dev server running**: `inngest.send()`
   in the API route will fail silently (caught and logged) if you haven't
   got the Inngest dev server or a configured Inngest Cloud connection
   running. The workflow will still execute and return results either way,
   since the API route runs the logic directly — Inngest is there for
   durability/observability, not as the only path to a result.
2. **No polling of Inngest run status** was implemented, since that requires
   an Inngest signing key and REST API setup this project doesn't assume.
   If you want the UI driven entirely by Inngest's run state instead, that's
   a reasonable next step — see Inngest's REST API docs.
3. **Retry logic** for failed nodes is not wired into the UI (the Inngest
   function has `retries: 1` at the function level, which retries the whole
   run, not a single failed node in-place). A per-node "Retry" button in the
   UI would need to re-invoke just that node's prompt.
4. Package versions in `package.json` are unverified — run `npm install` and
   resolve any conflicts.

## Project structure

```
app/
  api/inngest/route.ts       Inngest serve endpoint
  api/workflow/run/route.ts  Trigger + synchronously execute a workflow run
  page.tsx                   Renders the FlowEditor
  layout.tsx, globals.css
components/
  flow/flow-editor.tsx       Main canvas + toolbar
  flow/decision-node.tsx     Custom React Flow node
  flow/node-editor-dialog.tsx
  flow/execution-logs.tsx
  ui/                        shadcn-style primitives (button, dialog, etc.)
inngest/
  client.ts                  Inngest client instance
  workflow.ts                Durable workflow execution function
lib/
  types.ts                   Shared TypeScript types
  openai.ts                  YES/NO decision helper
  utils.ts                   cn() classname helper
```
