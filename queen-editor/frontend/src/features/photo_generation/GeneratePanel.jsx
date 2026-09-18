import { useEffect, useRef, useState } from "react";

import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Mono, Note } from "../../vendor/kit.jsx";
import InstallCard from "../producers/InstallCard.jsx";
import { PhotoGlyph } from "./glyphs.jsx";

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };

const PLACEHOLDER = '["ilk prompt", "ikinci prompt"]';

const MAX_VARIANTS = 26;
// What the box starts at in a project that has never saved a count. Two rather than four (İstek 8):
// four was the number the app was born with, and fewer variants of one prompt is what the work
// actually looks like. A name rather than a bare string inside the initial state, because "why this
// number" is the whole of what this line says.
const FIRST_VARIANTS = "2";
// Long enough to still be there when the eyes come back from the gallery, short enough to be gone
// before the next batch is typed. The design named two different numbers; this one is the user's.
const CONFIRM_MS = 10000;

// What each project's boxes were last holding. Opening a frame's detail replaces the whole project
// screen, so this panel is torn down and built again on every step in and out; without this the
// boxes would come back on what was last sent, and everything typed since would be gone (madde 35).
// Keyed by project: half-written work belongs to one project, never to the app.
//
// Memory only, like the seven stores before it: a reload fills the boxes from the record again.
const REMEMBERED = new Map();

/** What the boxes open with.
 *
 * A draft the user left behind wins over the project's record. The record is only written when the
 * queue button is pressed, so a draft is by definition the newer of the two -- it is exactly what
 * was typed after the last send.
 *
 * This is also the one place the record's shape becomes the boxes' shape: the boxes carry text, the
 * record carries a number that may be null, and a model and a lora that may be empty -- an empty
 * box is filled with the server's first row once the list is here.
 */
function opening(project, settings) {
  const draft = REMEMBERED.get(project);
  if (draft) return draft;
  return {
    prompts: settings.prompts,
    negative: settings.negative,
    model: settings.model || "",
    lora: settings.lora || "",
    variants: settings.variants === null ? FIRST_VARIANTS : String(settings.variants),
  };
}

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

/** The label the red box needs: the head of the server's sentence, or nothing.
 *
 * The server writes a field's message as "<short> — <detail>", so the box takes the head and the
 * full sentence goes under the button. A sentence with no dash has no shorter form: the box then
 * says nothing and only turns red -- writing the same words twice adds nothing.
 */
function boxLabel(message) {
  const cut = message.indexOf(" — ");
  return cut === -1 ? null : message.slice(0, cut);
}

// Artboard 04: a pure form -- prompt list, one shared negative, variant count, and the button that
// puts them at the end of the queue. What the run has to say is not here: progress, pauses,
// failures and the finish card all live in the queue panel (QueuePanel.jsx).
export default function GeneratePanel({ job, error, errorField, busyElsewhere, settings, project,
                                        models = null, loras = null, modelsError = null,
                                        producer = null, onGenerate, onClearError, onInstall }) {
  // Read at mount and never again: the store lives at module level, and asking it on every render
  // would make the render itself impure. One question, four answers.
  const [boxes] = useState(() => opening(project, settings));
  // Initial values only: nothing is synced afterwards, so typing is never overwritten. The boxes
  // all carry text -- the variant one has to survive being cleared while it is typed in.
  const [prompts, setPrompts] = useState(boxes.prompts);
  const [negative, setNegative] = useState(boxes.negative);
  const [model, setModel] = useState(boxes.model);
  const [lora, setLora] = useState(boxes.lora);
  const [variants, setVariants] = useState(boxes.variants);
  const [submitting, setSubmitting] = useState(false);
  // How many frames the last submission added, straight from the server; null once it has faded.
  const [added, setAdded] = useState(null);
  const [refused, setRefused] = useState(false);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  // Whatever the boxes hold is what a later mount starts from. One effect rather than a write in
  // each of the setters: the model and lora boxes have a second writer -- each fills itself from
  // the server's list when nothing was saved -- and a store written in six places would be six
  // chances to forget one.
  useEffect(() => {
    REMEMBERED.set(project, { prompts, negative, model, lora, variants });
  }, [project, prompts, negative, model, lora, variants]);

  // Nothing saved yet: the field has to show a real choice rather than a blank, so the first row
  // the server lists is taken. Only ever fills an empty box -- a saved choice is never moved.
  useEffect(() => {
    if (!model && models && models.length) setModel(models[0].value);
  }, [models, model]);

  // The same for the lora, and the first row is the default by the server's order (madde 238):
  // what the box shows is then what is sent. Boş is a value of its own, so a pick of it stays.
  useEffect(() => {
    if (!lora && loras && loras.length) setLora(loras[0].value);
  }, [loras, lora]);

  const loadingModels = models === null;
  // A saved pick the server no longer offers stays selected: quietly sliding the user onto
  // another row would mean the next batch renders with one they never picked. Compared by value,
  // because a row's label is what the user reads and its value is what the frame stores.
  const gone = Boolean(model) && Boolean(models) && models.length > 0
    && !models.some((row) => row.value === model);
  // The lost pick is drawn under its own value: an id is a poor label, and inventing a
  // prettier one for a row nobody offers any more would be inventing what it used to be called.
  const options = gone ? [{ value: model, label: model }, ...models] : (models || []);
  // The lora box on the model box's terms, without its note: whether a lost pick is still good is
  // the server's to say when the batch is sent (the user's call, madde 238).
  const loadingLoras = loras === null;
  const loraGone = Boolean(lora) && Boolean(loras) && loras.length > 0
    && !loras.some((row) => row.value === lora);
  const loraOptions = loraGone ? [{ value: lora, label: lora }, ...loras] : (loras || []);

  const perPrompt = Number(variants);
  // What the server blamed, if it blamed anything. A named field means the request never reached
  // the queue: the answer is that field's own sentence, and saying "Kuyruğa eklenemedi" on top of
  // it would tell one event twice with two different causes.
  const fieldError = errorField ? error : null;
  // Only the prompt box turns red; the variant box has no error state by design.
  const promptError = errorField === "prompts" ? error : null;
  const promptLabel = promptError ? boxLabel(promptError) : null;

  // Typing is the start of the next attempt: both the field's own error and the queue's refusal
  // belong to the try that just ended, and leaving either behind would put a stale answer under a
  // button that is about to be pressed again.
  function clearAnswers() {
    setRefused(false);
    if (errorField) onClearError();
  }

  function edit(setter) {
    return (e) => {
      setter(e.target.value);
      clearAnswers();
    };
  }

  function editVariants(e) {
    if (!acceptsVariants(e.target.value)) return;
    setVariants(e.target.value);
    clearAnswers();
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
      lora,
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

  // Nothing to queue while the engine that would do it is not here. The card says so and takes
  // itself away once the group has landed.
  const missing = Boolean(producer) && !producer.installed;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1, minHeight: 0 }}>
      <InstallCard producer={producer} onInstall={onInstall} />

      {/* The panel's first field, as it has been in the design since v1. A row is a checkpoint by
          its id, so the label is read and the value sent. */}
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Model</Mono>
        <select className="wf-input" aria-label="Model" value={model}
                disabled={loadingModels || !options.length}
                onChange={(e) => setModel(e.target.value)}
                style={{ fontSize: 12.5, color: "var(--ink)", cursor: "pointer" }}>
          {loadingModels ? (
            <option value="">yükleniyor…</option>
          ) : options.length ? (
            options.map((row) => <option key={row.value} value={row.value}>{row.label}</option>)
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

      {/* Under the model, because it finishes what the model box started: one lora laid over the
          checkpoint, or Boş. One pick and no more, the user's words (madde 237). A list that could
          not be read leaves the button alone: the pick the box holds goes as it is, and the server
          says whether it is good (madde 238). */}
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>LoRA</Mono>
        <select className="wf-input" aria-label="LoRA" value={lora}
                disabled={loadingLoras || !loraOptions.length}
                onChange={(e) => setLora(e.target.value)}
                style={{ fontSize: 12.5, color: "var(--ink)", cursor: "pointer" }}>
          {loadingLoras ? (
            <option value="">yükleniyor…</option>
          ) : loraOptions.length ? (
            loraOptions.map((row) => <option key={row.value} value={row.value}>{row.label}</option>)
          ) : (
            <option value="">liste okunamadı</option>
          )}
        </select>
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
        {promptLabel && <Note size={12} style={{ color: "var(--danger)" }}>{promptLabel}</Note>}
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
          disabled={!prompts.trim() || busyElsewhere || submitting || missing}
          onClick={handleAdd}
          style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}
        >
          {submitting
            ? <><span className="qe-spinner" aria-hidden="true" /> Ekleniyor…</>
            : <><PhotoGlyph size={14} /> Kuyruğa ekle</>}
        </button>

        {added !== null ? (
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            {/* Two parts, not one sentence: the mark carries the answer at a glance and does not
                wrap onto the text's second line. */}
            <Note size={12} style={{ color: "var(--ok)" }}>✓</Note>
            <Note size={12} style={{ color: "var(--ok)" }}>{added} kare kuyruğa eklendi</Note>
          </div>
        ) : fieldError ? (
          <Note size={12} style={{ color: "var(--danger)", textAlign: "center" }}>
            {fieldError}
          </Note>
        ) : refused ? (
          <Note size={12} style={{ color: "var(--danger)", textAlign: "center" }}>
            Kuyruğa eklenemedi — tekrar dene
          </Note>
        ) : busyElsewhere ? (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Üretim sürüyor: {job.project} — bitmesini bekle.
          </Note>
        ) : null}
      </div>
    </div>
  );
}
