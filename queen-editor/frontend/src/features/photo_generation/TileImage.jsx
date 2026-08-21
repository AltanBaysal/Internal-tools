import { useEffect, useRef, useState } from "react";

import { fileUrl } from "../../shared/api.js";
import { imageQueue } from "../../shared/image_queue.js";
import { shownPictures } from "../../shared/shown_pictures.js";

// How far ahead of the viewport a tile starts asking. Judgement, not measurement: too narrow and a
// tile shows up empty before it fills, too wide and pictures nobody scrolled to eat the ceiling.
const MARGIN = "300px";

export function TileImage({ project, file, ...rest }) {
  const url = fileUrl(project, file);
  // Has this picture been on screen already? Read once, when the tile is built: a tile coming back
  // to a gallery it was already in skips both gates below, because that waiting is exactly what
  // coming back must not do twice (İstek 1.2).
  const [held] = useState(() => shownPictures.has(url));
  // A browser with no observer cannot be asked, and calling new on an absent constructor throws
  // where it stands and takes the gallery with it. Near is what the browser assumed before the
  // queue existed, so it is the safe answer. jsdom is one such browser.
  const [near, setNear] = useState(() => held || typeof IntersectionObserver === "undefined");
  const [granted, setGranted] = useState(held);
  const picture = useRef(null);
  const ticket = useRef(null);

  useEffect(() => {
    if (held || typeof IntersectionObserver === "undefined") return undefined;
    const watcher = new IntersectionObserver(
      (entries) => setNear(entries[entries.length - 1].isIntersecting),
      { rootMargin: MARGIN });
    watcher.observe(picture.current);
    return () => watcher.disconnect();
  }, [held]);

  useEffect(() => {
    if (held || !near) return undefined;
    ticket.current = imageQueue.ask(() => setGranted(true));
    // Scrolling away and being unmounted are the same answer to the queue: this tile is done
    // waiting. The ticket takes a second release without giving back a second slot.
    return () => ticket.current.done();
  }, [held, near]);

  // Loaded and failed are also the same answer: the slot is what is being returned, not a verdict
  // on the file. One broken photo must not take a permanent bite out of a ceiling of two.
  const release = () => ticket.current?.done();

  return (
    <img ref={picture} alt={file}
         src={granted ? url : undefined}
         // Only a picture that really arrived is remembered: a broken one has nothing to keep, and
         // the next tile that asks for it should get to try again.
         onLoad={() => { shownPictures.add(url); release(); }}
         onError={release}
         {...rest} />
  );
}
