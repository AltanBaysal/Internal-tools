import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import ProgressPanel from "./ProgressPanel.jsx";

const PANEL = {
  width: 320,
  flexShrink: 0,
  borderLeft: "1px solid var(--border)",
  padding: 16,
  display: "flex",
  flexDirection: "column",
  gap: 14,
  overflow: "hidden",
  boxSizing: "border-box",
};

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };

const PLACEHOLDER = '["ilk prompt", "ikinci prompt"]';

/** api.js prefixes an unreachable-server message with "Sunucuya ulaşılamadı" (see shared/api.js);
 * anything else is a request the server itself rejected. The headline names which one happened so
 * a dead tunnel doesn't read as a bad request, and the raw line drops the now-redundant Turkish
 * prefix so it shows the underlying browser detail instead of repeating the headline.
 */
function describeError(text) {
  if (text.startsWith("Sunucuya ulaşılamadı")) {
    const nl = text.indexOf("\n");
    return { headline: "Sunucuya ulaşılamıyor", raw: nl >= 0 ? text.slice(nl + 1) : text };
  }
  return { headline: "İstek reddedildi", raw: text };
}

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

// Artboard 03: prompt list, one shared negative, variant count, Üret. Artboard 04 keeps all three
// fields on screen and swaps only the block underneath them.
export default function GeneratePanel({ job, error, errorField, busyElsewhere, settings, project,
                                        stopping, queue, onGenerate, onStop, onResume, onCancel,
                                        onClearError }) {
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
  // Another project's finished batch must not talk into this panel (state leaks across projects
  // otherwise -- the worker is global but the words on screen are this project's).
  const mine = job.project === project;
  const count = countPrompts(prompts);
  const perPrompt = Number(variants);
  const planned = count !== null && Number.isInteger(perPrompt) && perPrompt > 0
    ? count * perPrompt
    : null;
  // A field error belongs under its own box, not in the status card: the two error patterns never
  // show the same thing twice (spec Part 7 §4).
  const fieldError = errorField ? error : null;
  const errorInfo = error && !errorField ? describeError(error) : null;
  const paused = mine && job.status === "paused";
  const owed = queue?.pending?.length || 0;
  // Two ways a run can be left unfinished: it died in front of us (the server still knows why), or
  // it died with the session (Drive remembers the queue, nobody remembers the reason).
  const halted = mine && job.status === "error";
  const abandoned = !halted && !paused && job.status !== "running" && owed > 0;
  const unfinished = halted || abandoned;

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
    <div className={locked ? "wf-panel wf-panel--locked" : "wf-panel"} style={PANEL}>
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

      {unfinished ? (
        // Artboard 13: the same shape as the finished card -- big button, status card under it.
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Btn hl onClick={onResume}
               style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
            <Icon.Regen /> Kaldığı yerden devam et
          </Btn>
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", flexDirection: "column", gap: 6,
                        borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
              <Icon.Warn />
              <Note size={12} style={{ color: "var(--danger)", fontWeight: 500 }}>
                {halted
                  ? `Üretim durdu — ${job.done}/${job.total} tamamlandı`
                  : `Üretim yarım kaldı — ${queue.total - owed}/${queue.total} tamamlandı`}
              </Note>
            </div>
            {/* Only when the reason is known. A run that died with the session left no reason
                behind, and inventing one is worse than saying nothing. */}
            {halted && job.error && (
              <Mono size={10} style={{ color: "var(--ink-3)" }}>{job.error}</Mono>
            )}
          </div>
        </div>
      ) : paused ? (
        // Artboard 12: the way back on top, what happened under it, and the way out at the bottom.
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Btn hl onClick={onResume}
               style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
            <Icon.Regen /> Devam et
          </Btn>
          <div className="wf-stroke" style={{ padding: "8px 10px" }}>
            <Note size={12} style={{ color: "var(--ink-2)", display: "block" }}>
              Üretim duraklatıldı — {job.done}/{job.total} tamamlandı
            </Note>
          </div>
          <Btn ghost onClick={onCancel}
               style={{ justifyContent: "center", color: "var(--ink-3)" }}>İptal et</Btn>
          {errorInfo && <StatusErrorCard text={errorInfo.headline} raw={errorInfo.raw} />}
        </div>
      ) : running ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {/* While polls fail, the bar shows the LAST KNOWN state, not the present — dim it so a
              frozen counter cannot read as live progress, and let the card carry the last-known
              numbers ("the screen never claims what it does not know"). */}
          <div style={errorInfo ? { opacity: 0.45 } : undefined}>
            <ProgressPanel job={job} stopping={stopping} onStop={onStop} />
          </div>
          {errorInfo && (
            <StatusErrorCard
              text={`${errorInfo.headline} — son bilinen: ${job.done ?? 0}/${job.total || "?"}`}
              raw={errorInfo.raw}
            />
          )}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Btn hl disabled={!prompts.trim() || busyElsewhere || submitting}
               onClick={handleGenerate}
               style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
            {submitting ? "Başlatılıyor…" : <><Icon.Sparkle /> Üret</>}
          </Btn>

          {errorInfo ? (
            <StatusErrorCard text={errorInfo.headline} raw={errorInfo.raw} />
          ) : mine && job.status === "error" ? (
            <StatusErrorCard text={`Üretim durdu — ${job.done}/${job.total} tamamlandı`}
                             raw={job.error} />
          ) : mine && job.status === "done" ? (
            <div className="wf-stroke"
                 style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                          borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
              <Mono size={13} style={{ color: "var(--ok)" }}>✓</Mono>
              <Note size={12} style={{ color: "var(--ok)" }}>
                {job.done} / {job.total} üretildi — tamamlandı
              </Note>
            </div>
          ) : busyElsewhere ? (
            <Note size={12} style={{ color: "var(--ink-3)" }}>
              Üretim sürüyor: {job.project} — bitmesini bekle.
            </Note>
          ) : planned !== null ? (
            <Mono size={11} style={{ color: "var(--ink-3)", textAlign: "center" }}>
              {count} prompt × {perPrompt} varyant = <span style={{ color: "var(--accent)" }}>{planned} foto</span>
            </Mono>
          ) : null}
        </div>
      )}
    </div>
  );
}
