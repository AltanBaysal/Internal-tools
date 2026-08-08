// The screen keeps error rows so the user can see what happened, but xAI rejects any role it does
// not know, so they are dropped on the way out. Only role and content travel: anything the screen
// adds to a message stays on the screen.
export function toRequestBody(messages, model) {
  return {
    model,
    messages: messages
      .filter((m) => m.role === "user" || m.role === "assistant")
      .map((m) => ({ role: m.role, content: m.content })),
  };
}

// The service's own words: a 401 is equally a bad key and a bad model id, so naming one cause here
// would send the reader down the wrong path.
export function formatHttpError(status, body) {
  return `HTTP ${status} — ${body}`;
}
