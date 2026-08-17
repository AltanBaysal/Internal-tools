import { useCallback, useEffect, useState } from "react";

// The address bar is the source of truth for which screen is open: a reload must not lose the
// user's place, and the search results of Faz 13 need somewhere to jump to. Three shapes are all we
// have, so this stays a hook rather than a routing dependency.
export function parsePath(pathname) {
  const parts = pathname.split("/").filter(Boolean);
  if (parts[0] === "p" && parts[1]) {
    if (parts[2] === "c" && parts[3]) {
      return { view: "chat", projectId: parts[1], chatId: parts[3] };
    }
    return { view: "project", projectId: parts[1], chatId: null };
  }
  return { view: "home", projectId: null, chatId: null };
}

export function useRoute() {
  const [pathname, setPathname] = useState(() => window.location.pathname);

  useEffect(() => {
    const onPop = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = useCallback((next) => {
    window.history.pushState(null, "", next);
    setPathname(next);
  }, []);

  return { route: parsePath(pathname), navigate };
}
