import { useEffect, useState } from "react";

import { getJson } from "../../shared/api.js";

export function useSearch() {
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState([]);
  // Which query these hits belong to. Without it, "No results." would flash between a keystroke
  // and its answer, saying something untrue for as long as the round trip takes.
  const [answered, setAnswered] = useState("");

  const needle = query.trim();

  useEffect(() => {
    if (!needle) {
      setHits([]);
      setAnswered("");
      return undefined;
    }
    let cancelled = false;
    getJson(`/api/search?q=${encodeURIComponent(needle)}`)
      .then((found) => {
        if (cancelled) return;
        setHits(found);
        setAnswered(needle);
      })
      .catch(() => {
        if (!cancelled) setHits([]);
      });
    // A late answer to a query the user has already changed never lands.
    return () => {
      cancelled = true;
    };
  }, [needle]);

  return { query, setQuery, hits, searched: Boolean(needle) && answered === needle };
}
