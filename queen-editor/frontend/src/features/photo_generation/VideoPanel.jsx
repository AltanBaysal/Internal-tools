import { useEffect, useRef, useState } from "react";

import { Btn, Mono, Note } from "../../vendor/kit.jsx";
import InstallCard from "../producers/InstallCard.jsx";
import { VideoGlyph } from "./glyphs.jsx";

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };
// Long enough to be read after the eyes have moved to the gallery (the same number the photo
// panel's card uses).
const CONFIRM_MS = 10000;

// Every video is five seconds and there is no setting for it in this version (madde 28).
const SECONDS = 5;

const MAX_VARIANTS = 26;

const SCOPES = [
  { id: "missing", label: "Videosu olmayanlar" },
  { id: "selected", label: "Seçili kareler" },
];

/** A frame can carry a video once its photo has landed. Read off the gallery, which already says
 *  what each frame holds -- the server decides the same way. */
function produced(frames) {
  return (frames || []).filter((frame) => frame.status === "done");
}

/** What the variant box may hold while it is being typed in -- the photo panel's rule, for the same
 *  reason: a value outside the range is simply not taken, so there is no error state to design. */
function acceptsVariants(text) {
  if (text === "") return true;
  if (!/^\d+$/.test(text)) return false;
  return Number(text) >= 1 && Number(text) <= MAX_VARIANTS;
}

function ScopeRow({ scope, count, active, disabled, onPick }) {
  return (
    <button type="button" onClick={() => onPick(scope.id)} disabled={disabled}
            className="wf-stroke"
            style={{ display: "flex", alignItems: "center", justifyContent: "space-between",
                     padding: "8px 10px", background: "none", cursor: disabled ? "default" : "pointer",
                     borderColor: active ? "var(--accent)" : "var(--border)",
                     opacity: disabled ? 0.4 : active ? 1 : 0.4, width: "100%" }}>
      <Note size={12} style={{ color: "var(--ink-2)" }}>{scope.label}</Note>
      <Mono size={12} style={{ color: active ? "var(--accent)" : "var(--ink-3)" }}>{count}</Mono>
    </button>
  );
}

// Artboard: the photo panel's shape with a different subject. What it does not ask for is the
// point -- the prompt is written by a language model when the job's turn comes, and the length is
// fixed, so the only questions left are which frames and how the queue should take them.
export default function VideoPanel({ frames, selected, producer, onQueue, onInstall }) {
  const [scope, setScope] = useState("missing");
  // Text, not a number: the field has to survive being cleared while typing.
  const [variants, setVariants] = useState("1");
  const [submitting, setSubmitting] = useState(false);
  const [added, setAdded] = useState(null);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  const chosen = selected || [];
  const done = produced(frames);
  // The scope row's own name decides this: "Videosu olmayanlar" leaves out the frames that have
  // one, while picking frames by hand says "these ones" -- and that is how a second video is asked
  // for, since it is born as a copy frame rather than written over the first.
  const missing = done.filter((frame) => !(frame.layers || {}).video);
  const inSelection = done.filter((frame) => chosen.includes(frame.file));
  // The gallery's selection is what the panel follows: picking frames over there is a way of
  // saying "these ones", and the radio would be arguing with the user to stay where it was.
  useEffect(() => { setScope(chosen.length ? "selected" : "missing"); }, [chosen.length]);

  const counts = { missing: missing.length, selected: inSelection.length };
  const scoped = scope === "selected" ? inSelection : missing;
  // What the queue would take: every frame in scope, once per variant.
  const owed = scoped.length * (Number(variants) || 0);
  const missingProducer = Boolean(producer) && !producer.installed;

  function handleAdd() {
    setSubmitting(true);
    setAdded(null);
    clearTimeout(fade.current);
    onQueue(scope === "selected" ? inSelection.map((frame) => frame.file) : null, Number(variants))
      .then((body) => {
        if (body && typeof body.added === "number") {
          setAdded(body.added);
          fade.current = setTimeout(() => setAdded(null), CONFIRM_MS);
        }
      })
      .finally(() => setSubmitting(false));
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1, minHeight: 0 }}>
      <InstallCard producer={producer} onInstall={onInstall} />

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Model</Mono>
        <Note size={12} style={{ color: "var(--ink-3)" }}>WAN 2.2 I2V</Note>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Kapsam</Mono>
        {SCOPES.map((row) => (
          <ScopeRow key={row.id} scope={row} count={counts[row.id]} active={scope === row.id}
                    disabled={row.id === "selected" && !chosen.length} onPick={setScope} />
        ))}
      </div>

      {/* The design's own order: scope, then how many of each, then the button. */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Mono size={11} style={{ ...LABEL, flex: 1 }}>Varyant</Mono>
        <input
          className="wf-input"
          type="number"
          min={1}
          max={MAX_VARIANTS}
          value={variants}
          onChange={(e) => { if (acceptsVariants(e.target.value)) setVariants(e.target.value); }}
          onBlur={() => { if (variants === "") setVariants("1"); }}
          style={{ width: 56, textAlign: "center", fontSize: 13 }}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Süre</Mono>
        <Note size={12} style={{ color: "var(--ink-3)" }}>
          Her video {SECONDS} saniye — bu sürümde sabit.
        </Note>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <button type="button" className="wf-btn wf-btn--hl"
                disabled={!owed || submitting || missingProducer} onClick={handleAdd}
                style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
          {submitting
            ? <><span className="qe-spinner" aria-hidden="true" /> Ekleniyor…</>
            : <><VideoGlyph size={14} /> Kuyruğa ekle</>}
        </button>

        {added !== null ? (
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            <Note size={12} style={{ color: "var(--ok)" }}>✓</Note>
            <Note size={12} style={{ color: "var(--ok)" }}>{added} video kuyruğa eklendi</Note>
          </div>
        ) : owed ? (
          <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
            {owed} video üretilecek — her kare kendi videosunu alır.
          </Note>
        ) : (
          // Nothing left to do is a result, not a fault: no danger colour anywhere in this line.
          <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
            Tüm karelerin videosu var — üretilecek bir şey yok.
          </Note>
        )}
      </div>

      <Note size={11} style={{ color: "var(--ink-4)", marginTop: "auto" }}>
        Video prompt'u otomatik: LLM her fotonun kendi prompt'undan yazar. Detayda okunur,
        düzenlenir.
      </Note>
    </div>
  );
}
