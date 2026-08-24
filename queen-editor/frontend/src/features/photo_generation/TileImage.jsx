import { useEffect, useRef, useState } from "react";

import { fileUrl } from "../../shared/api.js";
import { imageQueue } from "../../shared/image_queue.js";
import { shownPictures } from "../../shared/shown_pictures.js";
import { Rendering } from "./frame_status.jsx";

// How long a tile waits for its picture before it lets the queue move on. An img download has no
// timeout of its own -- the ten second abort in api.js belongs to fetch -- so a request that hangs
// answers neither load nor error, and with a single slot that is the whole gallery stopped behind
// it. Judgement rather than measurement: long enough that a slow photo is never given up on early.
const PATIENCE = 30000;

// The picture is in the page from the start, because a hidden image is downloaded and an absent one
// is not. Hidden rather than merely empty: an img with nothing to draw writes its alt text across
// the card, and the alt text is the file name.
const HIDDEN = { display: "none" };

export function TileImage({ project, file, style, ...rest }) {
  const url = fileUrl(project, file);
  // Has this picture been on screen already? Read once, when the tile is built: a tile coming back
  // to a gallery it was already in draws at once, because that waiting is exactly what coming back
  // must not do twice (İstek 1.2).
  const [held] = useState(() => shownPictures.has(url));
  const [granted, setGranted] = useState(held);
  // waiting until the browser answers, then here or gone. A picture that never arrived keeps the
  // holder and loses the ring: nothing is coming, and a ring that turns forever says otherwise.
  const [state, setState] = useState(held ? "here" : "waiting");
  const ticket = useRef(null);

  useEffect(() => {
    if (held) return undefined;
    // No viewport to wait for: every tile asks as soon as it is built, so the order the gallery
    // downloads in is the order its frames are in, whichever way the page is scrolled.
    ticket.current = imageQueue.ask(() => setGranted(true));
    // Being taken off the screen is an answer to the queue: this tile is done waiting. The ticket
    // takes a second release without giving back a second slot.
    return () => ticket.current.done();
  }, [held]);

  useEffect(() => {
    if (!granted || state !== "waiting") return undefined;
    const timer = setTimeout(() => ticket.current?.done(), PATIENCE);
    return () => clearTimeout(timer);
  }, [granted, state]);

  // Loaded and failed are the same answer to the queue: what is being returned is the slot, not a
  // verdict on the file. One broken photo must not take a permanent bite out of a ceiling of one.
  const settle = (how) => {
    setState(how);
    ticket.current?.done();
  };

  return (
    <>
      {state !== "here" && (granted && state === "waiting"
        // Only the tile that holds the slot turns. Every tile is in the queue from the moment it
        // is built, so a ring on each of them would be a gallery of rings saying nothing.
        ? <Rendering style={style} />
        : <div className="wf-img" style={style} />)}
      <img alt={file} src={granted ? url : undefined}
           style={state === "here" ? style : HIDDEN}
           // Only a picture that really arrived is remembered: a broken one has nothing to keep,
           // and the next tile that asks for it should get to try again.
           onLoad={() => { shownPictures.add(url); settle("here"); }}
           onError={() => settle("gone")}
           {...rest} />
    </>
  );
}
