import { serve } from "inngest/next";
import { inngest } from "@/inngest/client";
import { runDecisionWorkflow } from "@/inngest/workflow";

// NOTE: `serve({ client, functions })` from "inngest/next" is the documented
// App Router integration pattern I recall, but please verify the exact
// export name/shape against https://www.inngest.com/docs/learn/serving-inngest-functions
// for the installed SDK version — the framework-adapter API has changed
// across major versions.
export const { GET, POST, PUT } = serve({
  client: inngest,
  functions: [runDecisionWorkflow],
});
