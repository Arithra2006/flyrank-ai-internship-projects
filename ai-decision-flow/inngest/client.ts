import { Inngest } from "inngest";

// NOTE: `new Inngest({ id: ... })` is the shape I recall from the Inngest
// TypeScript SDK. I have not run this against a live install here — verify
// the constructor options (e.g. whether `id` vs `name` is expected in the
// version you install) against https://www.inngest.com/docs before relying
// on it.
export const inngest = new Inngest({
  id: "ai-decision-flow",
});
