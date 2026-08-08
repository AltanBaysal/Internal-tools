import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };

const PLACEHOLDER = '["ilk prompt", "ikinci prompt"]';

/** Count for the "12 prompt × 4 varyant = 48 foto" line -- a preview, not a rule.
 *
 * The real parse and every error message live in the backend (domain/prompt_list.py). This only
 * decides whether we can show a number at all: anything it cannot read confidently hides the line,
 * so a wrong count can never be displayed. Trailing commas are stripped because a list pasted out
 * of a notebook usually has one and JSON does not allow it.
 */
function countPrompts(text) {
  const body = text.trim().replace(/^[A-Za-z_]\w*\s*=\s*/, "").replace(/,(\s*\])/g, "$1");
  try {
    const value = JSON.parse(body);
    if (!Array.isArray(value)) return null;
    return value.filter((item) => typeof item === "string" && item.trim()).length;
  } catch {
    return null;
  }
}

// Artboard 04: a pure form -- prompt list, one shared negative, variant count, and the button that
// sends them. What the run has to say is not here: progress, pauses, failures and the finish card
// all live in the queue panel (QueuePanel.jsx), which is what the icon rail is for.
export default function GeneratePanel({ job, error, errorField, busyElsewhere, settings,
                                        onGenerate, onClearError }) {
  // Initial values only: the screen mounts after the settings have loaded, so there is nothing to
  // sync afterwards and typing is never overwritten.
  const [prompts, setPrompts] = useState(settings.prompts);
  const [negative, setNegative] = useState(settings.negative);
  // Text, not a number: the field has to survive being cleared while typing. Whatever is not a
  // whole number goes to the server as null and comes back with the server's own message.
  const [variants, setVariants] = useState(
    settings.variants === null ? "4" : String(settings.variants),
  );
  const [submitting, setSubmitting] = useState(false);

  const running = job.status === "running" && !busyElsewhere;
  const locked = running || submitting;
  const count = countPrompts(prompts);
  const perPrompt = Number(variants);
  const planned = count !== null && Number.isInteger(perPrompt) && perPrompt > 0
    ? count * perPrompt
    : null;
  // A field error belongs under its own box; anything else is the run's business and shows up in
  // the queue panel instead (spec Part 7 §4).
  const fieldError = errorField ? error : null;

  function edit(setter) {
    return (e) => {
      setter(e.target.value);
      if (errorField) onClearError();     // typing is the answer to "Format hatası"
    };
  }

  function handleGenerate() {
    setSubmitting(true);
    onGenerate({
      prompts,
      negative,
      variants: Number.isInteger(perPrompt) && variants.trim() !== "" ? perPrompt : null,
    }).finally(() => setSubmitting(false));
  }

  return (
    // The lock dims the first four blocks (styles.css); app.css undims the fourth, which is the
    // action block -- so the button keeps working while the fields are held.
    <div className={locked ? "wf-panel--locked" : undefined}
         style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1, minHeight: 0 }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
        <Mono size={11} style={LABEL}>Prompt listesi</Mono>
        <textarea
          className="wf-input"
          rows={11}
          value={prompts}
          placeholder={PLACEHOLDER}
          disabled={locked}
          onChange={edit(setPrompts)}
          style={{ fontSize: 11.5, flex: 1, fontFamily: "IBM Plex Mono, monospace",
                   ...(errorField === "prompts" ? { borderColor: "var(--danger)" } : {}) }}
        />
        {errorField === "prompts" && (
          <Note size={12} style={{ color: "var(--danger)" }}>{fieldError}</Note>
        )}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Negatif prompt</Mono>
        <input
          className="wf-input"
          value={negative}
          disabled={locked}
          onChange={edit(setNegative)}
          style={{ fontSize: 12.5 }}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Mono size={11} style={{ ...LABEL, flex: 1 }}>Varyant</Mono>
          <input
            className="wf-input"
            type="number"
            min={1}
            max={26}
            value={variants}
            disabled={locked}
            onChange={edit(setVariants)}
            style={{ width: 56, textAlign: "center", fontSize: 13,
                     ...(errorField === "variants" ? { borderColor: "var(--danger)" } : {}) }}
          />
        </div>
        {errorField === "variants" && (
          <Note size={12} style={{ color: "var(--danger)" }}>{fieldError}</Note>
        )}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Btn hl disabled={!prompts.trim() || busyElsewhere || locked}
             onClick={handleGenerate}
             style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
          {submitting ? "Başlatılıyor…" : <><Icon.Sparkle /> Üret</>}
        </Btn>

        {busyElsewhere ? (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Üretim sürüyor: {job.project} — bitmesini bekle.
          </Note>
        ) : planned !== null ? (
          <Mono size={11} style={{ color: "var(--ink-3)", textAlign: "center" }}>
            {count} prompt × {perPrompt} varyant = <span style={{ color: "var(--accent)" }}>{planned} foto</span>
          </Mono>
        ) : null}
      </div>
    </div>
  );
}
