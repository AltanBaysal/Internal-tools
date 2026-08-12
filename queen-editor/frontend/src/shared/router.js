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
    return { project: decodeURIComponent(photo[1]), photo: decodeURIComponent(photo[2]),
             exporting: false };
  }
  // The export screen is a place of its own, so it has an address of its own: the back button
  // returns to the gallery and a reload keeps the screen.
  const exporting = path.match(/^\/projects\/([^/]+)\/export$/);
  if (exporting) {
    return { project: decodeURIComponent(exporting[1]), photo: null, exporting: true };
  }
  const project = path.match(/^\/projects\/([^/]+)$/);
  return { project: project ? decodeURIComponent(project[1]) : null, photo: null,
           exporting: false };
}

export function projectPath(project) {
  return `/projects/${encodeURIComponent(project)}`;
}

// The segment is the frame's identity, not its file: a copy frame shares its source's picture, so
// a file name would take two frames to one address. The word "photos" stays -- it is the area's
// name, the same reason the server's file route keeps it.
export function photoPath(project, frame) {
  return `${projectPath(project)}/photos/${encodeURIComponent(frame)}`;
}

export function exportPath(project) {
  return `${projectPath(project)}/export`;
}
