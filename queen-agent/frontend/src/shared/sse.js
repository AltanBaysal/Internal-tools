import { failureFrom } from "./failure.js";

// EventSource can only GET, and the answer endpoint is a POST, so the stream is read straight off
// the response body instead.

export function parseFrame(frame) {
  let event = null;
  let data = "";
  for (const line of frame.split("\n")) {
    if (line.startsWith("event: ")) event = line.slice(7);
    else if (line.startsWith("data: ")) data += line.slice(6);
  }
  if (!event) return null;
  try {
    return { event, data: JSON.parse(data) };
  } catch {
    // One malformed frame must not bring the whole answer down.
    return null;
  }
}

export async function streamEvents(path, onEvent) {
  const response = await fetch(path, { method: "POST" });
  if (!response.ok) throw await failureFrom(response);

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const parsed = parseFrame(buffer.slice(0, boundary));
      buffer = buffer.slice(boundary + 2);
      if (parsed) onEvent(parsed);
      boundary = buffer.indexOf("\n\n");
    }
  }
}
