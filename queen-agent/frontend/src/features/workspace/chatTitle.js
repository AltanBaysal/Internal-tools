// The server's own naming rule, mirrored: chat_title in chat.py trims a chat's first message to 42
// and marks only a message that lost something. The rule stands in two places because Python and
// the browser share no module; this copy exists for one window -- the record stood up while a
// draft's first turn runs -- and each side pins the rule with its own test, so drifting apart
// turns one of the two suites red.
const TITLE_LIMIT = 42;

export function chatTitle(text) {
  const trimmed = text.trim();
  if (trimmed.length <= TITLE_LIMIT) return trimmed;
  return trimmed.slice(0, TITLE_LIMIT) + "…";
}
