import { useEffect, useRef, useState } from "react";

import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Icon, Mono, Note } from "../../vendor/kit.jsx";

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };

const PLACEHOLDER = '["ilk prompt", "ikinci prompt"]';

const MAX_VARIANTS = 26;
// Long enough to read, short enough to be out of the way before the next batch is typed.
const CONFIRM_MS = 4000;

/** What the box may hold while it is being typed in.
 *
 * The design's rule: a value outside the range cannot be written at all -- the keystroke is simply
 * not taken, so there is no error state to design. Empty is allowed while the field has focus,
 * because otherwise the number could never be replaced; leaving it empty is settled on blur.
 */
function acceptsVariants(text) {
  if (text === "") return true;
  if (!/^\d+$/.test(text)) return false;
  const value = Number(text);
  return value >= 1 && value <= MAX_VARIANTS;
}

// Artboard 04: a pure form -- prompt list, one shared negative, variant count, and the button that
// puts them at the end of the queue. What the run has to say is not here: progress, pauses,
// failures and the finish card all live in the queue panel (QueuePanel.jsx).
export default function GeneratePanel({ job, error, errorField, busyElsewhere, settings,
                                        models = null, modelsError = null,
                                        onGenerate, onClearError }) {
  // Initial values only: the screen mounts after the settings have loaded, so there is nothing to
  // sync afterwards and typing is never overwritten.
  const [prompts, setPrompts] = useState(settings.prompts);
  const [negative, setNegative] = useState(settings.negative);
  const [model, setModel] = useState(settings.model || "");
  // Text, not a number: the field has to survive being cleared while typing.
  const [variants, setVariants] = useState(
    settings.variants === null ? "4" : String(settings.variants),
  );
  const [submitting, setSubmitting] = useState(false);
  // How many frames the last submission added, straight from the server; null once it has faded.
  const [added, setAdded] = useState(null);
  const [refused, setRefused] = useState(false);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  // Nothing saved yet: the field has to show a real choice rather than a blank, so the first model
  // the renderer lists is taken. Only ever fills an empty box -- a saved choice is never moved.
  useEffect(() => {
    if (!model && models && models.length) setModel(models[0]);
  }, [models, model]);

  const loadingModels = models === null;
  // A saved model the renderer no longer lists stays selected: quietly sliding the user onto
  // another model would mean the next batch renders with one they never picked.
  const gone = Boolean(model) && Boolean(models) && models.length > 0 && !models.includes(model);
  const options = gone ? [model, ...models] : (models || []);

  const perPrompt = Number(variants);
  // Only the prompt box has an error state; the variant box has none by design, and anything else
  // the server refuses is reported as "Kuyruğa eklenemedi".
  const promptError = errorField === "prompts" ? error : null;

  function edit(setter) {
    return (e) => {
      setter(e.target.value);
      if (errorField) onClearError();     // typing is the answer to "Format hatası"
    };
  }

  function editVariants(e) {
    if (!acceptsVariants(e.target.value)) return;
    setVariants(e.target.value);
    if (errorField) onClearError();
  }

  function handleAdd() {
    setSubmitting(true);
    setAdded(null);
    setRefused(false);
    clearTimeout(fade.current);
    onGenerate({
      prompts,
      negative,
      variants: Number.isInteger(perPrompt) && variants.trim() !== "" ? perPrompt : null,
      model,
    })
      .then((result) => {
        if (result && typeof result.added === "number") {
          setAdded(result.added);
          fade.current = setTimeout(() => setAdded(null), CONFIRM_MS);
        } else {
          setRefused(true);
        }
      })
      // The list is deliberately not cleared: what the user typed must not disappear beyond
      // recall, and the green card is what makes a second accidental add visible.
      .finally(() => setSubmitting(false));
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1, minHeight: 0 }}>
      {/* The panel's first field, as it has been in the design since v1. The list is the
          renderer's answer, so what can be picked is exactly what the graph can load. */}
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Model</Mono>
        <select className="wf-input" value={model} disabled={loadingModels || !options.length}
                onChange={(e) => setModel(e.target.value)}
                style={{ fontSize: 12.5, color: "var(--ink)", cursor: "pointer" }}>
          {loadingModels ? (
            <option value="">yükleniyor…</option>
          ) : options.length ? (
            options.map((name) => <option key={name} value={name}>{name}</option>)
          ) : (
            <option value="">model bulunamadı</option>
          )}
        </select>
        {gone && (
          <Note size={12} style={{ color: "var(--danger)" }}>Bu model artık kurulu değil.</Note>
        )}
        {/* Not a separate screen and not a blocker: the list failed, the queue has not. */}
        {modelsError && <StatusErrorCard text="Model listesi okunamadı" raw={modelsError} />}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
        <Mono size={11} style={LABEL}>Prompt listesi</Mono>
        <textarea
          className="wf-input"
          rows={11}
          value={prompts}
          placeholder={PLACEHOLDER}
          onChange={edit(setPrompts)}
          style={{ fontSize: 11.5, flex: 1, fontFamily: "IBM Plex Mono, monospace",
                   ...(promptError ? { borderColor: "var(--danger)" } : {}) }}
        />
        {promptError && <Note size={12} style={{ color: "var(--danger)" }}>{promptError}</Note>}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Negatif prompt</Mono>
        <input className="wf-input" value={negative} onChange={edit(setNegative)}
               style={{ fontSize: 12.5 }} />
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Mono size={11} style={{ ...LABEL, flex: 1 }}>Varyant</Mono>
        <input
          className="wf-input"
          type="number"
          min={1}
          max={MAX_VARIANTS}
          value={variants}
          onChange={editVariants}
          onBlur={() => { if (variants === "") setVariants("1"); }}
          style={{ width: 56, textAlign: "center", fontSize: 13 }}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {/* Not the kit's Btn: the spinner has to sit inside the button while it is held. */}
        <button
          type="button"
          className="wf-btn wf-btn--hl"
          disabled={!prompts.trim() || busyElsewhere || submitting}
          onClick={handleAdd}
          style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}
        >
          {submitting
            ? <><span className="qe-spinner" aria-hidden="true" /> Ekleniyor…</>
            : <><Icon.Plus /> Üretime ekle</>}
        </button>

        {added !== null ? (
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            <Note size={12} style={{ color: "var(--ok)" }}>✓ {added} kare kuyruğa eklendi</Note>
          </div>
        ) : refused ? (
          <Note size={12} style={{ color: "var(--danger)" }}>Kuyruğa eklenemedi</Note>
        ) : busyElsewhere ? (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Üretim sürüyor: {job.project} — bitmesini bekle.
          </Note>
        ) : null}
      </div>
    </div>
  );
}
