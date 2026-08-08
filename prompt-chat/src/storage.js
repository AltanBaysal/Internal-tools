// A chat is { id, messages, draft }. Every function returns a new list and never mutates its input:
// React only re-renders on a changed reference, and a mutated list would also desync from what was
// last written to storage.

export function nextId(chats) {
  return chats.reduce((max, c) => Math.max(max, c.id), 0) + 1;
}

export function createChat(chats) {
  const id = nextId(chats);
  return { chats: [...chats, { id, messages: [], draft: "" }], id };
}

export function deleteChat(chats, id) {
  return chats.filter((c) => c.id !== id);
}

export function replaceMessages(chats, id, messages) {
  return chats.map((c) => (c.id === id ? { ...c, messages } : c));
}

export function setDraft(chats, id, draft) {
  return chats.map((c) => (c.id === id ? { ...c, draft } : c));
}

const TITLE_MAX = 40;

// The first user message is what actually tells two chats apart: it is where the question or the
// instruction lands, and everything after it is a follow-up.
export function titleOf(messages) {
  const first = messages.find((m) => m.role === "user");
  const line = first ? first.content.replace(/\s+/g, " ").trim() : "";
  if (!line) return "Yeni sohbet";
  return line.length > TITLE_MAX ? line.slice(0, TITLE_MAX) + "…" : line;
}
