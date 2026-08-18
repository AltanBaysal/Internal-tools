import { useCallback, useEffect, useState } from "react";

// The address bar is the source of truth for which screen is open, so a reload does not lose the
// user's place. Four shapes are all we have, so this stays a hook rather than a routing
// dependency.
export function parsePath(pathname) {
  const parts = pathname.split("/").filter(Boolean);
  // The app's own screen, so it hangs off the root rather than off a project.
  if (parts[0] === "settings" && !parts[1]) {
    return { view: "settings", projectId: null, chatId: null };
  }
  if (parts[0] === "p" && parts[1]) {
    if (parts[2] === "c" && parts[3]) {
      return { view: "chat", projectId: parts[1], chatId: parts[3] };
    }
    return { view: "project", projectId: parts[1], chatId: null };
  }
  return { view: "root", projectId: null, chatId: null };
}

export function useRoute() {
  const [pathname, setPathname] = useState(() => window.location.pathname);

  useEffect(() => {
    const onPop = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  // "/" is a fork rather than a place: the app reads it, picks a screen and moves on. Left in the
  // history it would catch the back button and throw the user forward again, so that one step
  // replaces instead of pushing.
  const navigate = useCallback((next, { replace = false } = {}) => {
    if (replace) window.history.replaceState(null, "", next);
    else window.history.pushState(null, "", next);
    setPathname(next);
  }, []);

  return { route: parsePath(pathname), navigate };
}
