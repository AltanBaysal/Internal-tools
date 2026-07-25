// "22 Tem 2026 · 14:32" -- month names come from the browser, so no hand-kept Turkish table.
const DAY = new Intl.DateTimeFormat("tr-TR", { day: "numeric", month: "short", year: "numeric" });
const TIME = new Intl.DateTimeFormat("tr-TR", { hour: "2-digit", minute: "2-digit" });

export function formatModified(epochSeconds) {
  const date = new Date(epochSeconds * 1000);
  return `${DAY.format(date)} · ${TIME.format(date)}`;
}
