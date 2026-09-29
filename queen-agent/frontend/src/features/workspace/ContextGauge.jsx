// Madde 92. A gauge, not a control: it is read and never pressed, which is why it sits at the far
// end of the composer's foot from the three things that are.
//
// The share is settled here and the drawing is left to one CSS rule. Not for testability -- for
// truth: how full the circle is, is a number, and an arc is only one way of saying it.
//
// Madde 343 gave it its words (design items 146 and 182): the circle's sentence, and from four fifths
// of the ceiling the share written beside it, so a chat says it is filling before it is full.

// Four fifths, in percent. A share of the ceiling the server sends with the number, not a second copy
// of it, and it decides only what is shown: whether a chat may take a turn is the server's rule.
const NEARLY_FULL = 80;

export default function ContextGauge({ sent, ceiling }) {
  // Nothing measured yet, so there is nothing to read. An empty circle would be a mark that is
  // always there and says nothing -- the gauge is born when the first answer comes back.
  if (!sent || !ceiling) return null;
  // A circle cannot fill past full, and drawing the excess would draw a lie.
  const filled = Math.min(sent / ceiling, 1);
  // In whole numbers, and rounded down: it says 100 only once the chat is full and 80 only once it
  // is nearly full. At least 1, since a circle that is drawn has something in it. Multiplied before
  // dividing, because 0.82 * 100 in floating point can land a hair under 82.
  const percent = Math.min(100, Math.max(1, Math.floor((sent * 100) / ceiling)));
  const said = percent === 100 ? "This chat is full" : `This chat is ${percent}% full`;
  return (
    <>
      <span
        className="context-gauge"
        style={{ "--filled": String(filled) }}
        /* Drawn rather than written, so it needs a name -- and the same sentence serves a mouse
           resting on it and a screen reader reaching it. */
        role="img"
        title={said}
        aria-label={said}
      />
      {/* The circle's sentence again, so a screen reader skips it. A full chat has none: what it
          says is its own notice's. */}
      {percent >= NEARLY_FULL && percent < 100 ? (
        <span className="context-gauge__words" aria-hidden="true">{`${percent}% full`}</span>
      ) : null}
    </>
  );
}
