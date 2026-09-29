import { useEffect, useRef, useState } from "react";

// Long enough to be read without looking away, short enough that the button is a button again
// before it is next needed.
const SAID_MS = 2500;

// The app's one Copy (Madde 193, 364): the open file's header and the project list that did not
// come both hand their text to it, so the two can never answer a press differently. What it copies
// is the caller's; where it stands and how wide it is, the caller's class.
//
// Its own component because it has its own state -- what it last said, and the timer that takes
// that back.
//
// The precedent is queen-editor's RawOutput and PhotoDetail; the two tools share no code, so what
// travels is the reasoning.
export default function CopyButton({ text, className }) {
  const [said, setSaid] = useState(null);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  const copy = () => {
    clearTimeout(fade.current);
    // Written straight from the press rather than a microtask after it: the clipboard is granted to
    // a user gesture, and a browser may refuse a write that arrives even a tick late.
    //
    // The try is for the other half: with no clipboard object at all the call throws where it
    // stands, while a refused permission rejects instead, and the user needs the same answer either
    // way.
    let landing;
    try {
      landing = navigator.clipboard.writeText(text);
    } catch (absent) {
      landing = Promise.reject(absent);
    }
    Promise.resolve(landing)
      .then(() => setSaid("Copied"))
      .catch(() => setSaid("Could not copy"))
      .finally(() => {
        fade.current = setTimeout(() => setSaid(null), SAID_MS);
      });
  };

  return (
    // The answer is the button's own word and colour, written where Copy was: a word appearing
    // beside it would push what stands under it down, which is the page moving while it is being
    // read. Dimmed rather than gone while there is nothing to copy -- a button that came and went as
    // the text loaded would make its row twitch, and a button that copies nothing and says it did is
    // the other half of the same lie.
    <button
      type="button"
      className={`ghost ${className}`}
      disabled={!text}
      data-said={said === "Copied" ? "yes" : said ? "no" : undefined}
      onClick={copy}
    >
      {said ?? "Copy"}
    </button>
  );
}
