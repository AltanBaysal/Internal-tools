import { useLayoutEffect, useRef } from "react";

// Where each project's gallery was left, by project. Opening a frame's page replaces the whole
// project screen, so the scroll box is built again on every step in and out -- and a box built
// again starts at the top, which is where the pictures the user was looking at go missing
// (İstek 1.2).
//
// Memory only: what is wanted is standing still inside one visit, not a property of the project. A
// reload opens the gallery at the top, the same as opening it for the first time.
const KEPT = new Map();

/** The ref for the gallery's scroll box; attaching it is the whole contract.
 *
 * A layout effect rather than an ordinary one: the restore has to land before the browser paints,
 * or the gallery is drawn at the top for one frame and then jumps. The node is captured in the
 * effect's body, so the cleanup holds one whether or not React has cleared the ref by then -- and
 * the place is read on the way out rather than on every scroll event, which is one write a visit.
 */
export function useKeptScroll(project) {
  const box = useRef(null);
  useLayoutEffect(() => {
    const node = box.current;
    node.scrollTop = KEPT.get(project) || 0;
    return () => KEPT.set(project, node.scrollTop);
  }, [project]);
  return box;
}
