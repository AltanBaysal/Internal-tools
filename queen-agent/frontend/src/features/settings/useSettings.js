import { useCallback, useEffect, useState } from "react";

import { getJson, patchJson } from "../../shared/api.js";

// The app's own settings, which is a different question from anything a project holds -- so it has
// its own road to the server and nothing here knows about projects, chats or files.
export function useSettings() {
  const [apiKey, setApiKey] = useState("");

  useEffect(() => {
    let cancelled = false;
    getJson("/api/settings")
      .then((settings) => {
        if (!cancelled) setApiKey(settings.apiKey ?? "");
      })
      // Nothing is guessed from a failure: an unreadable answer leaves the box empty, and the
      // screen's own save will report whatever the server says next.
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  // What comes back replaces what was sent: the server trims the key, and the screen should show
  // what is actually stored rather than what was typed.
  const save = useCallback(async (key) => {
    const saved = await patchJson("/api/settings", { apiKey: key });
    setApiKey(saved.apiKey ?? "");
  }, []);

  return { apiKey, save };
}
