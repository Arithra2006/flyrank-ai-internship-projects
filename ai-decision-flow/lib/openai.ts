import OpenAI from "openai";
import type { DecisionAnswer } from "./types";

let client: OpenAI | null = null;

function getClient(): OpenAI {
  if (!client) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error(
        "OPENAI_API_KEY is not set. Add it to your .env.local file."
      );
    }
    client = new OpenAI({ apiKey });
  }
  return client;
}

const SYSTEM_PROMPT = `You are a strict binary decision engine used inside an automated workflow.
You will be given a prompt describing a condition to evaluate.
You must respond with EXACTLY one word: either "YES" or "NO".
Do not include punctuation, explanation, reasoning, or any other text.
If you are uncertain, make your best judgment and still answer only YES or NO.`;

/**
 * Normalizes a raw LLM text response into a strict YES/NO value.
 * Throws if the response cannot be confidently normalized.
 */
export function normalizeDecision(raw: string): DecisionAnswer {
  const cleaned = raw.trim().toUpperCase().replace(/[.!"']/g, "");
  if (cleaned === "YES" || cleaned.startsWith("YES")) return "YES";
  if (cleaned === "NO" || cleaned.startsWith("NO")) return "NO";
  throw new Error(`Could not normalize model response into YES/NO: "${raw}"`);
}

/**
 * Sends a single decision prompt to the model and returns a normalized
 * YES/NO answer. Retries once with a stricter instruction if the first
 * response can't be normalized.
 *
 * NOTE: I'm using the Chat Completions API shape (openai.chat.completions.create)
 * which has been stable in the OpenAI Node SDK, but I have not executed this
 * against a live SDK version here — verify the method name and parameters
 * against the installed `openai` package version's docs/types before relying
 * on it in production.
 */
export async function getDecision(
  prompt: string,
  model: string = process.env.OPENAI_MODEL || "gpt-5-mini"
): Promise<DecisionAnswer> {
  const openai = getClient();

  const attempt = async (strict: boolean): Promise<string> => {
    const completion = await openai.chat.completions.create({
      model,
      temperature: 0,
      max_tokens: 5,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        {
          role: "user",
          content: strict
            ? `${prompt}\n\nRespond with exactly one word: YES or NO.`
            : prompt,
        },
      ],
    });

    const text = completion.choices[0]?.message?.content ?? "";
    return text;
  };

  const first = await attempt(false);
  try {
    return normalizeDecision(first);
  } catch {
    const second = await attempt(true);
    return normalizeDecision(second); // will throw if still invalid
  }
}
