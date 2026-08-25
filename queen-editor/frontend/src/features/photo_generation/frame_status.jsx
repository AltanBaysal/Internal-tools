// How a frame's state is drawn. One mould for every layer: the pill says "<layer> <state>", so the
// video and audio rows below are the whole of what Blok 5-6 has to add here.
//
// The words are the design's; the keys are the server's own (layers.PHOTO / VIDEO / AUDIO), so a
// job's type can be handed straight to the pill without a translation table in between.
const LAYER_WORD = { photo: "foto", video: "video", audio: "ses" };
const STATE = {
  // The palette's second grey, not its brightest ink: at 9px over a photograph the third one is a
  // label nobody can read, but this is the tone the ownership badge in the opposite corner already
  // carries at exactly this size (Fark 65). The other two carry meaning in their colour.
  pending: { word: "kuyrukta", color: "var(--ink-2)", alive: false },
  // The same debt, with the queue standing still: "kuyrukta" claims movement, and a run that
  // stopped has none. Same ink -- a frame nobody is working on is no less worth reading.
  waiting: { word: "bekliyor", color: "var(--ink-2)", alive: false },
  running: { word: "üretiliyor", color: "var(--accent)", alive: true },
  failed: { word: "hata", color: "var(--danger)", alive: false },
};

// Top left, the corner the design gives it (madde 57). It sat at the bottom for a while because
// the select ring owned this corner and appeared under the pointer, so the pill had to jump out of
// the way -- movement inside a card the user only pointed at. The ring moved to the opposite
// corner instead, and nothing here has to move again.
//
// The corner is the box rather than the pill's own position: a frame can be waiting for two layers
// at once, and the second label reads under the first (Fark 64).
const CORNER = {
  position: "absolute", top: 6, left: 6, zIndex: 2,
  display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 3,
  // The corner is part of the card: a label must not turn it into a dead spot for drag or click.
  pointerEvents: "none",
};

// One mould whatever the state says, and the measure is the mould's half: two labels standing one
// under the other on different grounds would read as a mistake. The colour is the caller's, because
// that is the half that means something (Fark 65).
const PILL = {
  display: "flex", alignItems: "center", gap: 4,
  // Dark enough to carry the words over any picture, bright or not.
  background: "rgba(10,8,7,.7)", borderRadius: 3, padding: "3px 7px",
  fontSize: 9, lineHeight: 1.4,
};

/** The corner the labels stand in: top left, one under another.
 *
 * Exported so a page with a single sentence of its own puts it in the same place rather than
 * wherever its own layout happens to drop it.
 */
export function Corner({ children }) {
  return <span data-corner style={CORNER}>{children}</span>;
}

/** The corner label itself, with whatever words the caller has.
 *
 * Exported so a page that has its own sentence to put in that corner gets the same label rather
 * than a second one that looks almost like it.
 */
export function Pill({ color, alive, children }) {
  return (
    <span data-pill className="qe-pill wf-mono" style={{ ...PILL, color }}>
      {alive && (
        <span aria-hidden="true" className="qe-dot qe-dot--alive"
              style={{ background: "currentColor", width: 5, height: 5 }} />
      )}
      {children}
    </span>
  );
}

/** The state pill, or nothing at all.
 *
 * A produced frame has no pill: the photo itself is the answer, and what it owns is said by the
 * badges in the opposite corner.
 */
export function StatusPill({ layer, state }) {
  const shown = STATE[state];
  if (!shown) return null;
  return (
    <Pill color={shown.color} alive={shown.alive}>{LAYER_WORD[layer]} {shown.word}</Pill>
  );
}

/** Every label a frame's state has earned, in the corner they belong in.
 *
 * An empty list draws no corner at all: a produced frame with nothing owed has the photo itself for
 * an answer, and what it owns is said by the badges in the corner below.
 */
export function StatusPills({ states }) {
  if (!states.length) return null;
  return (
    <Corner>
      {states.map(({ layer, state }) => <StatusPill key={layer} layer={layer} state={state} />)}
    </Corner>
  );
}

/** What the stage says while a layer is made over a picture that is already there.
 *
 * The picture stays under it (Fark 113): for the length of a render it is the one thing left to
 * look at, and swapping it for a spinner took that away. A photo being made has no picture to keep
 * -- that one still gets `Rendering`.
 */
export function Making({ layer }) {
  return (
    <span data-making className="wf-mono"
          style={{ position: "absolute", top: "50%", left: "50%",
                   transform: "translate(-50%,-50%)", zIndex: 1,
                   display: "flex", alignItems: "center", gap: 6,
                   background: "rgba(10,8,7,.72)", borderRadius: 4, padding: "8px 14px",
                   fontSize: 12, color: "var(--accent)" }}>
      <span aria-hidden="true" className="qe-dot qe-dot--alive"
            style={{ background: "currentColor", width: 6, height: 6 }} />
      {LAYER_WORD[layer]} üretiliyor…
    </span>
  );
}

/** The kit's loading holder without its word, and without its stripes.
 *
 * vendor/ is never hand-edited, and the kit's own version writes "Çalışıyor" across the middle of
 * the card -- which is exactly what the design takes away. The spinner is the kit's; the ground is
 * not, because the kit's loading class paints diagonal stripes and this holder must not.
 *
 * Stripes are how the gallery says there are no pixels here: a frame still queued, one that failed,
 * a picture that never came. A ring says the opposite -- something is on its way. Saying both at
 * once left the two states telling one difference through the ring alone (madde 36).
 *
 * The caller's style is written first and the centring after it, so no caller can take the ring out
 * of the middle. That is not a hypothetical: the gallery hands a tile the img's own style, and an
 * img's style says display block. Block is right for an img and wrong for this box -- it stops the
 * ring being a flex item, the ring falls back to inline, and width and height do not apply to an
 * inline span. The ring landed in the top left corner as a deformed arc.
 */
export function Rendering({ style }) {
  return (
    <div className="wf-img"
         style={{ ...style, backgroundImage: "none",
                  display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span className="wf-spinner" />
    </div>
  );
}
