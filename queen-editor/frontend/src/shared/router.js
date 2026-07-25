import { useEffect, useState } from "react";

// Two screens, so two paths -- a router library would be more code than this file.
// Flask already serves index.html for any path (SPA fallback), so a reload keeps the screen.
export function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export function useRoute() {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  return path;
}

// Project names carry spaces and Turkish letters, so the path segment is encoded.
export function projectFromPath(path) {
  const match = path.match(/^\/projects\/(.+)$/);
  return match ? decodeURIComponent(match[1]) : null;
}
