import { useEffect, useState } from "react";

import { clockTime } from "../../shared/time.js";

// A thousand and up loses its exact digits. The number answers "was this turn expensive", and four
// significant figures do not help with that question.
function shorten(count) {
  return count < 1000 ? String(count) : `${(count / 1000).toFixed(1)}k`;
}

// The notes that close a message, on one row: when it was said, and -- for an answer that was
// measured -- what it sent; then whatever the message hands over, which under a question is its
// versions and its pencil (Madde 348, design item 139). Under the message rather than over it,
// because a note about a thing is read after it. One row rather than two, and no name in it: the
// sidebar carries the name, and which side a message sits on says who wrote it.
//
// What it sent, in two parts (Madde 354, design items 189 and 192): what the service already had
// and what it did not. A cached token costs about a fiftieth of one that missed, so the one total
// this used to draw priced the two alike and said nothing about the bill. Missed is the rest of
// `sent`, because `cached` is a part of it rather than an addition to it. What the model wrote is
// not drawn: the owner asked for the two and nothing else. The counts drop when nothing was sent --
// an answer from before this existed reads back as zero, and a number there would claim a
// measurement nobody took. The time never drops: it was said at a time either way.
export default function Stamp({ at, usage, children }) {
  // The wait is stamped by an effect, so the first draw of a pending box has no time yet. Nothing
  // rather than an empty line.
  if (!at) return null;
  return (
    <div className="msg__stamp">
      {/* An element of their own, so the row's gap parts the words from the arrows and the pencil,
          and never a word from a glyph. */}
      <span>
        {clockTime(at)}
        {usage?.sent ? (
          <>
            {" · "}
            {/* A word beside each colour, so the two are told apart without it. */}
            <span className="msg__stamp-cached">{`${shorten(usage.cached)} cached`}</span>
            {" · "}
            <span className="msg__stamp-missed">{`${shorten(usage.sent - usage.cached)} missed`}</span>
          </>
        ) : null}
      </span>
      {children}
    </div>
  );
}

// Madde 194. What a turn says about itself while it is still running, in the stamp's own place and
// wearing its class: when the turn ends the strip goes and the record's stamp arrives, and two
// different-looking things trading places would jump on the page.
//
// A gerund that is deliberately not a description. Deriving one from the tool name was asked
// against, and the reason holds up: the two pieces beside it carry every fact there is, and a word
// that tried to compete with them would only be wrong more often.
const WORDS = [
  "Ideating",
  "Percolating",
  "Ruminating",
  "Noodling",
  "Marinating",
  "Conjuring",
  "Puzzling",
  "Tinkering",
  "Wrangling",
  "Brewing",
  "Pondering",
  "Scheming",
  "Whirring",
  "Cogitating",
  "Finagling",
  "Simmering",
];

const WORD_MS = 3000;

export function LiveStrip({ at, round, of, tokens }) {
  // Somewhere in the list rather than the top of it: the same first word on every turn reads like a
  // fixed label, which is the one thing this is not.
  const [word, setWord] = useState(() => Math.floor(Math.random() * WORDS.length));
  useEffect(() => {
    const tick = setInterval(() => setWord((next) => (next + 1) % WORDS.length), WORD_MS);
    return () => clearInterval(tick);
  }, []);
  // The time the wait was stamped leads, where the record's time will stand (Madde 348). The first
  // draw of a pending box has none yet, and then the row starts with the round.
  const when = at ? `${clockTime(at)} · ` : "";
  return (
    <div className="msg__stamp msg__stamp--live" data-testid="live-strip">
      {/* The two facts lead and the moving part trails (user, 7 September). The trailing space is
          the sentence's, not the layout's: a flex item's own end-space is collapsed away and the
          gap draws the distance, so what is read here and what is seen there are one line. */}
      <span>{`${when}round ${round}/${of} · ${shorten(tokens)} tokens · `}</span>
      {/* The one thing that must never stall, so the stylesheet turns it and not JavaScript: a busy
          React has its intervals waiting too, and that is exactly the moment the screen has to look
          alive. The number can sit still for thirty seconds; this cannot. */}
      <span className="msg__spinner" aria-hidden="true" />
      {/* An element rather than a bare text node, so where the spinner stands is sayable at all:
          it draws nothing of its own, and only its neighbours can place it. */}
      <span>{`${WORDS[word]}…`}</span>
    </div>
  );
}
