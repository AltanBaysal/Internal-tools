import { useEffect, useState } from "react";

// The key, the model name and the chats outlive the page; nothing else does.
export function usePersisted(storageKey, fallback) {
  const [value, setValue] = useState(() => localStorage.getItem(storageKey) ?? fallback);
  useEffect(() => {
    localStorage.setItem(storageKey, value);
  }, [storageKey, value]);
  return [value, setValue];
}

export function usePersistedJson(storageKey, fallback) {
  const [value, setValue] = useState(() => readJson(storageKey, fallback));
  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(value));
  }, [storageKey, value]);
  return [value, setValue];
}

// A hand-edited or half-written entry must not leave the user staring at a blank page: fall back to
// the empty state and let the app write a good one over it.
function readJson(storageKey, fallback) {
  const raw = localStorage.getItem(storageKey);
  if (raw === null) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}
