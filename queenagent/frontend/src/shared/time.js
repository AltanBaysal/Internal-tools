// The server sends an ISO stamp and the browser makes it readable. It has to be this way round:
// "2h ago" goes stale where it is written, and only the browser re-renders.

const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;
const WEEK = 7 * DAY;

export function clockTime(iso) {
  return new Date(iso).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

export function relativeTime(iso, now = Date.now()) {
  const elapsed = now - new Date(iso).getTime();
  if (elapsed < MINUTE) return "just now";
  if (elapsed < HOUR) return `${Math.floor(elapsed / MINUTE)}m ago`;
  if (elapsed < DAY) return `${Math.floor(elapsed / HOUR)}h ago`;
  if (elapsed < 2 * DAY) return "yesterday";
  if (elapsed < WEEK) return `${Math.floor(elapsed / DAY)} days ago`;
  // Past a week a count stops helping and a date starts.
  return new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}
