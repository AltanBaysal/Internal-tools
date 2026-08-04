import { useEffect, useState } from "react";

// Three screens, so three shapes of path -- a router library would still be more code than this.
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

// Project names carry spaces and Turkish letters, so every segment is encoded. Matching a single
// segment matters: with a greedy ".+" the photo path's whole tail would read as a project name.
export function routeFromPath(path) {
  const photo = path.match(/^\/projects\/([^/]+)\/photos\/([^/]+)$/);
  if (photo) {
    return { project: decodeURIComponent(photo[1]), photo: decodeURIComponent(photo[2]) };
  }
  const project = path.match(/^\/projects\/([^/]+)$/);
  return { project: project ? decodeURIComponent(project[1]) : null, photo: null };
}

export function projectPath(project) {
  return `/projects/${encodeURIComponent(project)}`;
}

export function photoPath(project, file) {
  return `${projectPath(project)}/photos/${encodeURIComponent(file)}`;
}
