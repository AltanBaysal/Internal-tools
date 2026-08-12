// How a frame's state is drawn. One mould for every layer: the pill says "<layer> <state>", so the
// video and audio rows below are the whole of what Blok 5-6 has to add here.
//
// The words are the design's; the keys are the server's own (layers.PHOTO / VIDEO / AUDIO), so a
// job's type can be handed straight to the pill without a translation table in between.
const LAYER_WORD = { photo: "foto", video: "video", audio: "ses" };
const STATE = {
  pending: { word: "kuyrukta", color: "var(--ink-3)", alive: false },
  running: { word: "üretiliyor", color: "var(--accent)", alive: true },
  failed: { word: "hata", color: "var(--danger)", alive: false },
};

const PILL = {
  position: "absolute", top: 6, left: 6, zIndex: 2,
  display: "flex", alignItems: "center", gap: 4,
  background: "rgba(10,8,7,.75)", borderRadius: 3, padding: "2px 5px",
  fontSize: 9, lineHeight: 1.4,
  // The corner is part of the card: a label must not turn it into a dead spot for drag or click.
  pointerEvents: "none",
};

/** The state pill, or nothing at all.
 *
 * A produced frame has no pill: the photo itself is the answer, and what it owns is said by the
 * badges in the opposite corner.
 */
export function StatusPill({ layer, state }) {
  const shown = STATE[state];
  if (!shown) return null;
  return (
    <span data-pill className="qe-pill wf-mono" style={{ ...PILL, color: shown.color }}>
      {shown.alive && (
        <span aria-hidden="true" className="qe-dot qe-dot--alive"
              style={{ background: "currentColor", width: 5, height: 5 }} />
      )}
      {LAYER_WORD[layer]} {shown.word}
    </span>
  );
}

/** The kit's loading holder without its word.
 *
 * vendor/ is never hand-edited, and the kit's own version writes "Çalışıyor" across the middle of
 * the card -- which is exactly what the design takes away. Same classes, same spinner, no words.
 */
export function Rendering({ style }) {
  return (
    <div className="wf-img wf-img--loading" style={style}>
      <span className="wf-spinner" style={{ position: "relative", zIndex: 1 }} />
    </div>
  );
}
