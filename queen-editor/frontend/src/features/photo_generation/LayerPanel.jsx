import { useEffect, useRef, useState } from "react";

import { Mono, Note } from "../../vendor/kit.jsx";
import InstallCard from "../producers/InstallCard.jsx";
import { SoundGlyph, VideoGlyph } from "./glyphs.jsx";
import { LINKED, LOOP, MODES, STANDARD, nounOf } from "./production_modes.js";

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };
// Long enough to be read after the eyes have moved to the gallery (the same number the photo
// panel's card uses).
const CONFIRM_MS = 10000;

const MAX_VARIANTS = 26;

// What each layer calls itself. The panel is one component because the design asks for one --
// "video panelinin birebir aynısı" -- so only these words and the scope rule differ between them.
const WORDS = {
  video: {
    model: "WAN 2.2 I2V",
    missing: "Videosu olmayan kareler",
    // The bare noun for counting, and the possessive the estimate line needs -- Turkish does not
    // build one from the other.
    noun: "video",
    own: "videosunu",
    // The adjective for a frame that already carries this layer. Only the copy warning needs it,
    // and the two panels say it differently enough that neither can be built from the other.
    held: "videolu",
    // Why a press found nothing to do. Three of them, because the panel can be empty for three
    // different reasons and one sentence for all of them is what sent the user here (İstek 4.3).
    // noBase is what this layer hangs on: for a video that is the frame's own picture.
    noBase: "Henüz üretilmiş kare yok.",
    chosenNoBase: "Seçili karelerin fotoğrafı henüz üretilmedi.",
    allHeld: "Tüm karelerin videosu var.",
    Glyph: VideoGlyph,
  },
  audio: {
    model: "MMAudio v2",
    missing: "Videosu olup sesi olmayan kareler",
    noun: "ses",
    own: "sesini",
    held: "sesi olan",
    // A sound hangs on a video, not on a photo -- so an empty project reads this one here, and it
    // is the nearer thing that is missing.
    noBase: "Videosu olan kare yok.",
    chosenNoBase: "Seçili karelerin videosu henüz üretilmedi.",
    allHeld: "Tüm karelerin sesi var.",
    Glyph: SoundGlyph,
  },
};

/** What a mode promises about what it makes.
 *
 * No row for the plain mode: its promise is the layer's own line, built from the layer's own words.
 * The noun each mode uses lives with the modes themselves (nounOf) -- two screens say it now, and
 * this table is only about the half nobody else says.
 */
const MODE_TAIL = {
  [LOOP]: "her video kendine döner.",
  [LINKED]: "her video sıradaki karede biter.",
};

/** The frames this layer can be hung on.
 *
 * The server decides the same way; this is the panel's own count, not a second rule. Sound needs a
 * video under it -- a frame without one is never in its scope (madde 31) -- while a video needs
 * only the photo the frame already is.
 */
function eligible(frames, layer) {
  return (frames || []).filter((frame) => {
    if (frame.status !== "done") return false;
    const held = frame.layers || {};
    if (layer === "audio" && (!held.video || (frame.failed || []).includes("video"))) return false;
    return true;
  });
}

/** What the variant box may hold while it is being typed in -- the photo panel's rule, for the same
 *  reason: a value outside the range is simply not taken, so there is no error state to design. */
function acceptsVariants(text) {
  if (text === "") return true;
  if (!/^\d+$/.test(text)) return false;
  return Number(text) >= 1 && Number(text) <= MAX_VARIANTS;
}

// The one reason that belongs to no layer: the box is on both panels and says the same thing.
const NO_VARIANTS = "Varyant sayısı girilmedi — en az 1 yaz.";

/** Why this press cannot go to the queue, or null when it can.
 *
 * Read in the order a person would: the box in front of them first, then whether the project holds
 * anything this layer could ever hang on, then what they picked, then the scope's own answer.
 *
 * `can` is every frame this layer could be hung on at all -- empty means the layer underneath is
 * missing, which is a different sentence from "they all have one already". That difference is the
 * whole point: one sentence for every empty scope is what made the panel blame frames for having
 * videos when what they were missing was pictures (İstek 4.3).
 *
 * No dead branch: for a video `can` is the produced frames themselves, so its noBase is exactly
 * "nothing is produced yet"; for a sound it is the frames holding a video, and its noBase says so.
 */
function refusalOf(words, can, scope, scoped, variants) {
  if (variants === "") return NO_VARIANTS;
  if (scoped.length) return null;
  if (!can.length) return words.noBase;
  if (scope === "selected") return words.chosenNoBase;
  return words.allHeld;
}

// Why linking closes when the chosen frames are scattered. Says the reason rather than the remedy:
// what to do about it is visible in the gallery, why it matters is not.
const SCATTERED_REASON = "Zincir ancak bitişik karelerde kapanır — arada seçilmemiş kare var.";

/** Do the chosen frames sit together in the gallery, with nothing unchosen between them?
 *
 * Measured against the whole gallery rather than the frames this layer could be hung on: the engine
 * reads a linked video's target from the gallery's own sequence, so a frame standing in between is
 * a real hole in the chain whatever state it is in.
 *
 * max - min + 1 === count, so no sorting: a run of positions with no gap is exactly as wide as it
 * is long. An id the gallery does not hold -- a frame deleted while it was selected -- contributes
 * no position and is not counted, so it cannot make a solid run look broken.
 */
function neighbours(frames, chosen) {
  const places = (frames || []).reduce(
    (found, frame, index) => (chosen.includes(frame.id) ? [...found, index] : found), []);
  if (places.length < 2) return true;   // one frame has nothing to skip over
  return Math.max(...places) - Math.min(...places) + 1 === places.length;
}

// What both row families share. One constant rather than the same object written twice: the design
// widened the row (Fark 31), and a measure given to only one of them would leave two heights in one
// panel -- ModeRow's own comment says it is drawn the way a scope row is drawn.
const ROW = { display: "flex", alignItems: "center", padding: "10px 12px", background: "none",
              width: "100%" };
// The radio the design puts at the head of a scope row: thick and accent-coloured on the chosen
// one, thin and grey on the other. Three long properties rather than the border shorthand, because
// a shorthand carrying var() cannot be read back out of the element again.
const DOT = { width: 12, height: 12, borderRadius: "50%", borderStyle: "solid", flexShrink: 0 };

function ScopeRow({ label, count, active, disabled, onPick }) {
  return (
    <button type="button" onClick={onPick} disabled={disabled}
            className="wf-stroke"
            style={{ ...ROW, justifyContent: "space-between", gap: 10,
                     cursor: disabled ? "default" : "pointer",
                     borderColor: active ? "var(--accent)" : "var(--border)",
                     opacity: disabled ? 0.4 : active ? 1 : 0.4 }}>
      <span style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
        {/* The row's own dim state is what makes an unpicked circle faint -- no second fading here,
            or the two would drift the day one of them is changed. */}
        <span data-dot style={{ ...DOT, borderWidth: active ? 2 : 1,
                                borderColor: active ? "var(--accent)" : "var(--ink-3)" }} />
        <Note size={12} style={{ color: "var(--ink-2)" }}>{label}</Note>
      </span>
      <Mono size={12} style={{ color: active ? "var(--accent)" : "var(--ink-3)" }}>{count}</Mono>
    </button>
  );
}

/** One production mode, drawn the way a scope row is drawn -- with nothing on the right.
 *
 * Not ScopeRow with an empty count: a mode has nothing to count, and saying so with a missing
 * argument would leave the reader deciding what an absent number means.
 */
function ModeRow({ label, active, disabled, onPick }) {
  return (
    <button type="button" onClick={onPick} disabled={disabled}
            className="wf-stroke"
            style={{ ...ROW, cursor: disabled ? "default" : "pointer",
                     borderColor: active ? "var(--accent)" : "var(--border)",
                     // Closed first: a closed row must not stay bright just because it was picked.
                     opacity: disabled ? 0.4 : active ? 1 : 0.4 }}>
      <Note size={12} style={{ color: "var(--ink-2)" }}>{label}</Note>
    </button>
  );
}

// Artboard: the photo panel's shape with a different subject. What it does not ask for is the
// point -- the prompt is written by a language model when the job's turn comes, and the length is
// fixed, so the only questions left are which frames, and how many of each.
export default function LayerPanel({ layer, frames, selected, producer, onQueue, onInstall }) {
  const words = WORDS[layer];
  const [scope, setScope] = useState("missing");
  // Kept by both panels though only the video one shows the row: a sound ends nowhere, so it has
  // nothing to choose -- and one call shape means the server never asks where a request came from.
  const [mode, setMode] = useState(STANDARD);
  // Text, not a number: the field has to survive being cleared while typing.
  const [variants, setVariants] = useState("1");
  const [submitting, setSubmitting] = useState(false);
  // What the queue took and what it was told to make: both from the moment the request went out.
  // The card stands for ten seconds and the mode row is one click away, so reading the live mode
  // would let it report a run nobody asked for. null still means no card.
  const [added, setAdded] = useState(null);
  // Why the last press went nowhere, or null. The green card's opposite number, and it lives in the
  // same slot: one press, one answer.
  const [refused, setRefused] = useState(null);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  const chosen = selected || [];
  const can = eligible(frames, layer);
  // The scope row's own name decides this: it leaves out the frames that hold this layer already,
  // while picking frames by hand says "these ones" -- and that is how a second one is asked for,
  // since it is born as a copy frame rather than written over the first.
  const missing = can.filter((frame) => !(frame.layers || {})[layer]);
  // By identity, not by file name: asking for a second video makes a copy frame, and the copy
  // shows the same photo -- so a file name cannot tell two frames apart and the gallery keeps its
  // selection as identities for exactly that reason. What goes to the queue below is still the
  // file name; the two are three lines apart so neither can be changed without seeing the other.
  const inSelection = can.filter((frame) => chosen.includes(frame.id));
  // The gallery's selection is what the panel follows: picking frames over there is a way of
  // saying "these ones", and the radio would be arguing with the user to stay where it was.
  useEffect(() => { setScope(chosen.length ? "selected" : "missing"); }, [chosen.length]);

  const counts = { missing: missing.length, selected: inSelection.length };
  const scoped = scope === "selected" ? inSelection : missing;
  // What the queue would take: every frame in scope, once per variant.
  const owed = scoped.length * (Number(variants) || 0);
  // Frames in scope that already carry this layer. Production does not write over one -- it makes
  // a copy frame beside it -- and nothing on screen said so until now. Read from the scope rather
  // than the raw selection: Videosu olmayan kareler leaves those frames out by its own definition,
  // so the count is zero there without a second rule about which scope may warn.
  const copies = scoped.filter((frame) => (frame.layers || {})[layer]).length;
  const said = { noun: nounOf(mode, words.noun),
                 tail: MODE_TAIL[mode] || `her kare kendi ${words.own} alır.` };
  // Only on the selection's own scope: "Videosu olmayan kareler" is scattered by nature -- what
  // sits between its members already has a video -- and each of its frames still has a real next.
  const linkingClosed = scope === "selected" && !neighbours(frames, chosen);
  // A row nobody can click must not keep going to the queue. Written as an effect rather than a
  // correction during render: what changed is a prop from the gallery, and the panel never hears a
  // second click to put itself right. Not dependent on `mode` -- it would then re-run on the very
  // click that picks linking and take it straight back.
  useEffect(() => {
    if (linkingClosed) setMode((picked) => (picked === LINKED ? STANDARD : picked));
  }, [linkingClosed]);
  // A reason belongs to the press that produced it: the frames it counted, the scope it named and
  // the number it read. Move any of the three and it becomes a stale answer standing under a button
  // about to be pressed again. The gallery's selection is in here too -- picking other frames over
  // there is exactly such a move. A press changes none of the three, so the answer stays up.
  useEffect(() => { setRefused(null); }, [chosen, scope, variants]);
  const missingProducer = Boolean(producer) && !producer.installed;

  function handleAdd() {
    const why = refusalOf(words, can, scope, scoped, variants);
    if (why) {
      setAdded(null);
      clearTimeout(fade.current);
      setRefused(why);
      return;
    }
    setSubmitting(true);
    setAdded(null);
    clearTimeout(fade.current);
    const sent = mode;
    onQueue(scope === "selected" ? inSelection.map((frame) => frame.file) : null, Number(variants),
            sent)
      .then((body) => {
        if (body && typeof body.added === "number") {
          setAdded({ count: body.added, mode: sent });
          fade.current = setTimeout(() => setAdded(null), CONFIRM_MS);
        }
      })
      .finally(() => setSubmitting(false));
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1, minHeight: 0 }}>
      <InstallCard producer={producer} onInstall={onInstall} />

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} data-label style={LABEL}>Model</Mono>
        {/* The photo panel's own box, with the one option there is: a layer has a single model and
            the job that goes to the queue carries no model at all -- the engine picks it. The frame
            and the arrow are the design's (Fark 32); the choice is not invented, and the day a
            second model arrives the box is already here. */}
        <select className="wf-input" value={words.model} onChange={() => {}}
                style={{ fontSize: 12.5, color: "var(--ink)", cursor: "pointer" }}>
          <option value={words.model}>{words.model}</option>
        </select>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} data-label style={LABEL}>Kapsam</Mono>
        <ScopeRow label={words.missing} count={counts.missing} active={scope === "missing"}
                  onPick={() => setScope("missing")} />
        <ScopeRow label="Seçili kareler" count={counts.selected} active={scope === "selected"}
                  disabled={!chosen.length} onPick={() => setScope("selected")} />
      </div>

      {/* Only a video ends on a picture, so only the video panel has this to ask. */}
      {layer === "video" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Mono size={11} data-label style={LABEL}>Üretim modu</Mono>
          {MODES.map((one) => (
            <ModeRow key={one.id} label={one.label} active={mode === one.id}
                     disabled={one.id === LINKED && linkingClosed}
                     onPick={() => setMode(one.id)} />
          ))}
          {linkingClosed && (
            // Under the row it closed, in the ordinary ink: a closed option is a rule, not a fault.
            <Note size={12} style={{ color: "var(--ink-3)" }}>{SCATTERED_REASON}</Note>
          )}
        </div>
      )}

      {/* The design's own order: scope, then the mode, then how many of each, then the button. */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Mono size={11} data-label style={{ ...LABEL, flex: 1 }}>Varyant</Mono>
        <input
          className="wf-input"
          type="number"
          min={1}
          max={MAX_VARIANTS}
          value={variants}
          onChange={(e) => { if (acceptsVariants(e.target.value)) setVariants(e.target.value); }}
          /* Red while it is empty, and it stays empty: the silent reset to 1 on the way out is what
             kept the box from ever showing that (Fark 29). What the emptiness means is said when
             the button is pressed. */
          style={{ width: 56, textAlign: "center", fontSize: 13,
                   ...(variants === "" ? { borderColor: "var(--danger)" } : {}) }}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {/* Nothing the user could fill in locks this: an empty field is answered after the press,
            in the card below (Fark 27). What is left is one request in flight -- and the producer,
            which is the design's own exception: not a field but an engine that is not here yet, and
            the card at the top of the panel says so. */}
        <button type="button" className="wf-btn wf-btn--hl"
                disabled={submitting || missingProducer} onClick={handleAdd}
                style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
          {submitting
            ? <><span className="qe-spinner" aria-hidden="true" /> Ekleniyor…</>
            : <><words.Glyph size={14} /> Kuyruğa ekle</>}
        </button>

        {added !== null ? (
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            <Note size={12} style={{ color: "var(--ok)" }}>✓</Note>
            <Note size={12} style={{ color: "var(--ok)" }}>
              {added.count} {nounOf(added.mode, words.noun)} kuyruğa eklendi
            </Note>
          </div>
        ) : refused ? (
          // The green card's red twin: the same box in the same place, the other colour. The mark
          // is its own part for the reason the green one's is -- it carries the answer at a glance
          // and does not wrap onto the sentence's second line.
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
            <Note size={12} style={{ color: "var(--danger)" }}>✕</Note>
            <Note size={12} style={{ color: "var(--danger)" }}>{refused}</Note>
          </div>
        ) : owed ? (
          // The copy warning takes the mode's tail, never its head: the mode is already named in
          // what comes out, so what is given up is an echo of the marked row just above.
          <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
            {owed} {said.noun} üretilecek — {copies
              ? `${words.held} ${copies} kare için yeniler kopya kare olur, eskisi durur.`
              : said.tail}
          </Note>
        ) : null}
      </div>
    </div>
  );
}
