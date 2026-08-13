import { useEffect, useRef, useState } from "react";

import { Btn, Mono } from "../vendor/kit.jsx";

// About five lines of it: enough for the line that usually carries the answer, short enough that a
// sixty line failure cannot push what is under it off the panel.
// display: block is load-bearing and no test can see it -- the kit's Mono is a span, and max-height
// and overflow do not apply to an inline box at all. Without it the style is written, the browser
// ignores it, and the suite stays green while the box grows without end.
const BOX = { display: "block", maxHeight: 90, overflowY: "auto", overflowX: "hidden",
              whiteSpace: "pre-wrap", wordBreak: "break-word", color: "var(--ink-3)" };
// Long enough to be read without looking away, short enough that the button is a button again
// before it is next needed.
const SAID_MS = 2500;

/** The service's own output, folded rather than cut.
 *
 * The repo rule is that an error prints what the command or the service actually said, and a sixty
 * line answer is what that sometimes means. Nothing is dropped: the whole text is here, inside its
 * own ceiling, and one press puts it on the clipboard.
 */
export function RawOutput({ text }) {
  const [said, setSaid] = useState(null);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  function copy() {
    clearTimeout(fade.current);
    // Written straight from the press, not from a microtask after it: the clipboard is granted to
    // a user gesture, and a browser may refuse a write that arrives even a tick late. The try is
    // for the other half -- with no clipboard object at all the call throws where it stands, while
    // a refused permission rejects instead, and the user needs the same answer either way.
    let landing;
    try {
      landing = navigator.clipboard.writeText(text);
    } catch (absent) {
      landing = Promise.reject(absent);
    }
    Promise.resolve(landing)
      .then(() => setSaid("Kopyalandı"))
      .catch(() => setSaid("Kopyalanamadı"))
      .finally(() => { fade.current = setTimeout(() => setSaid(null), SAID_MS); });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <Mono data-raw size={10} style={BOX}>{text}</Mono>
      <Btn sm onClick={copy} style={{ alignSelf: "flex-start" }}>{said || "Kopyala"}</Btn>
    </div>
  );
}
