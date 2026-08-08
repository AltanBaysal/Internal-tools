import { toRequestBody, formatHttpError } from "./chat.js";

const ENDPOINT = "https://api.x.ai/v1/chat/completions";

// The only place in the app that touches the network. Reaching xAI straight from the browser works
// because it allows cross-origin requests; a proxy here would add a second thing to run and solve
// nothing.
export async function sendChat({ key, model, messages }) {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${key.trim()}`,
    },
    body: JSON.stringify(toRequestBody(messages, model.trim())),
  });

  const raw = await res.text();
  if (!res.ok) throw new Error(formatHttpError(res.status, raw));
  return JSON.parse(raw).choices[0].message.content;
}
