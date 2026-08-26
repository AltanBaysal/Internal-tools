// Madde 92. A gauge, not a control: it is read and never pressed, which is why it sits at the far
// end of the composer's foot from the three things that are.
//
// The share is settled here and the drawing is left to one CSS rule. Not for testability -- for
// truth: how full the circle is, is a number, and an arc is only one way of saying it.
export default function ContextGauge({ sent, ceiling }) {
  // Nothing measured yet, so there is nothing to read. An empty circle would be a mark that is
  // always there and says nothing -- the gauge is born when the first answer comes back.
  if (!sent || !ceiling) return null;
  // A circle cannot fill past full, and drawing the excess would draw a lie.
  const filled = Math.min(sent / ceiling, 1);
  const share = `${Math.round(filled * 100)}% of the context ceiling`;
  return (
    <span
      className="context-gauge"
      style={{ "--filled": String(filled) }}
      /* Drawn rather than written, so it needs a name -- and the same sentence serves a mouse
         resting on it and a screen reader reaching it. */
      role="img"
      title={share}
      aria-label={share}
    />
  );
}
