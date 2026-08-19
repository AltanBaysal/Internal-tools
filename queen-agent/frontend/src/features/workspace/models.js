// Every text model xAI documents, read from docs.x.ai/docs/models on 2026-08-18, in the order the
// documentation lists them. Which of these a chat that picked nothing answers with is the server's
// setting and arrives from GET /api/model; the names and the prices are text, and text lives here.
//
// The design wrote a sentence under each name, but those names -- Grok 4 Fast, Heavy, Code -- do not
// exist, and the documentation describes only one of the real models. So each row says what it
// costs instead: true for all of them, and the thing the choice is actually about.
//
// Prices are per million tokens, input / output, for a prompt under 200k. Above that they double.
export const MODELS = [
  { id: "grok-4.6", name: "Grok 4.6", detail: "$2 / $6 per 1M · 500k" },
  { id: "grok-4.5", name: "Grok 4.5", detail: "$2 / $6 per 1M · 500k" },
  { id: "grok-4.3", name: "Grok 4.3", detail: "$1.25 / $2.50 per 1M · 1M" },
  {
    id: "grok-4.20-0309-reasoning",
    name: "Grok 4.20 (Reasoning)",
    detail: "$1.25 / $2.50 per 1M · 1M",
  },
  {
    id: "grok-4.20-0309-non-reasoning",
    name: "Grok 4.20 (Non-Reasoning)",
    detail: "$1.25 / $2.50 per 1M · 1M",
  },
  {
    id: "grok-4.20-multi-agent-0309",
    name: "Grok 4.20 Multi-Agent",
    detail: "$1.25 / $2.50 per 1M · 1M",
  },
  { id: "grok-build-0.1", name: "Grok Build", detail: "$1 / $2 per 1M · 256k" },
];

// XAI_MODEL can be set to anything at all, so an id this list does not know is shown as it is -- a
// button saying nothing would be worse than one saying a raw id.
export function modelName(id) {
  if (!id) return "Model";
  return MODELS.find((model) => model.id === id)?.name ?? id;
}
