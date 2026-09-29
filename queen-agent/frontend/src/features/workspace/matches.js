// Case and accents do not count, as in the design's data.js and shell.js: "cafe" finds "Café". One
// rule for every search in the app -- All projects and Search chats -- so the two cannot drift.
const fold = (text) => text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

// An empty query is everything.
export function matches(text, query) {
  return fold(text).includes(fold(query.trim()));
}
