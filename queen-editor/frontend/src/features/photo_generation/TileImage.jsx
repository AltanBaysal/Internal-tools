import { useEffect, useRef, useState } from "react";

import { fileUrl } from "../../shared/api.js";
import { imageQueue } from "../../shared/image_queue.js";

// How far ahead of the viewport a tile starts asking. Judgement, not measurement: too narrow and a
// tile shows up empty before it fills, too wide and pictures nobody scrolled to eat the ceiling.
const MARGIN = "300px";

export function TileImage({ project, file, ...rest }) {
  // A browser with no observer cannot be asked, and calling new on an absent constructor throws
  // where it stands and takes the gallery with it. Near is what the browser assumed before the
  // queue existed, so it is the safe answer. jsdom is one such browser.
  const [near, setNear] = useState(() => typeof IntersectionObserver === "undefined");
  const [granted, setGranted] = useState(false);
  const picture = useRef(null);
  const ticket = useRef(null);

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return undefined;
    const watcher = new IntersectionObserver(
      (entries) => setNear(entries[entries.length - 1].isIntersecting),
      { rootMargin: MARGIN });
    watcher.observe(picture.current);
    return () => watcher.disconnect();
  }, []);

  useEffect(() => {
    if (!near) return undefined;
    ticket.current = imageQueue.ask(() => setGranted(true));
    // Scrolling away and being unmounted are the same answer to the queue: this tile is done
    // waiting. The ticket takes a second release without giving back a second slot.
    return () => ticket.current.done();
  }, [near]);

  // Loaded and failed are also the same answer: the slot is what is being returned, not a verdict
  // on the file. One broken photo must not take a permanent bite out of a ceiling of two.
  const release = () => ticket.current?.done();

  return (
    <img ref={picture} alt={file}
         src={granted ? fileUrl(project, file) : undefined}
         onLoad={release} onError={release}
         {...rest} />
  );
}
