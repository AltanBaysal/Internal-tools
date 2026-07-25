import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";
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

const RAW_ERROR = {
  color: "var(--ink-3)",
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 3,
  padding: "6px 8px",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

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

// Artboard 03: prompt list, one shared negative, variant count, Üret. Artboard 04 keeps all three
// fields on screen and swaps only the block underneath them.
export default function GeneratePanel({ job, error, busyElsewhere, onGenerate, onStop }) {
  const [prompts, setPrompts] = useState("");
  const [negative, setNegative] = useState("");
  // Text, not a number: the field has to survive being cleared while typing. Whatever is not a
  // whole number goes to the server as null and comes back with the server's own message.
  const [variants, setVariants] = useState("4");

  const running = job.status === "running" && !busyElsewhere;
  const count = countPrompts(prompts);
  const perPrompt = Number(variants);
  const planned = count !== null && Number.isInteger(perPrompt) && perPrompt > 0
    ? count * perPrompt
    : null;
  const summary = {
    done: `bitti — ${job.done}/${job.total}`,
    stopped: `durduruldu — ${job.done}/${job.total}`,
  }[job.status];

  return (
    <div style={PANEL}>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
        <Mono size={11} style={LABEL}>Prompt listesi</Mono>
        <textarea
          className="wf-input"
          rows={11}
          value={prompts}
          placeholder={PLACEHOLDER}
          onChange={(e) => setPrompts(e.target.value)}
          style={{ fontSize: 11.5, flex: 1, fontFamily: "IBM Plex Mono, monospace" }}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Negatif prompt</Mono>
        <input
          className="wf-input"
          value={negative}
          onChange={(e) => setNegative(e.target.value)}
          style={{ fontSize: 12.5 }}
        />
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Mono size={11} style={{ ...LABEL, flex: 1 }}>Varyant</Mono>
        <input
          className="wf-input"
          type="number"
          min={1}
          max={26}
          value={variants}
          onChange={(e) => setVariants(e.target.value)}
          style={{ width: 56, textAlign: "center", fontSize: 13 }}
        />
      </div>

      {running ? (
        <ProgressPanel job={job} onStop={onStop} />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Btn hl disabled={!prompts.trim() || busyElsewhere}
               onClick={() => onGenerate({
                 prompts,
                 negative,
                 variants: Number.isInteger(perPrompt) && variants.trim() !== ""
                   ? perPrompt
                   : null,
               })}
               style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
            <Icon.Sparkle /> Üret
          </Btn>

          {planned !== null && (
            <Mono size={11} style={{ color: "var(--ink-3)", textAlign: "center" }}>
              {count} prompt × {perPrompt} varyant = <span style={{ color: "var(--accent)" }}>{planned} foto</span>
            </Mono>
          )}
          {summary && (
            <Mono size={11} style={{ color: "var(--ink-2)", textAlign: "center" }}>{summary}</Mono>
          )}
          {busyElsewhere && (
            <Note size={12} style={{ color: "var(--ink-3)" }}>
              Üretim sürüyor: {job.project} — bitmesini bekle.
            </Note>
          )}
          {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
          {job.status === "error" && (
            <div className="wf-stroke" style={{ padding: 12, display: "flex",
                                                flexDirection: "column", gap: 8,
                                                borderColor: "var(--danger)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
                <Icon.Warn />
                <Note size={13} style={{ color: "var(--danger)", fontWeight: 500 }}>Üretim durdu</Note>
              </div>
              <Note size={12} style={{ color: "var(--ink-2)" }}>
                {job.done}/{job.total} tamamlandı — üretilenler kaydedildi.
              </Note>
              {/* The server's own error text -- we never guess the cause. */}
              <Mono size={10} style={RAW_ERROR}>{job.error}</Mono>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
