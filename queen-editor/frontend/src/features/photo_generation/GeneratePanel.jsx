import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";
import VariantPicker from "./VariantPicker.jsx";

const LABEL = {
  color: "var(--ink-2)",
  letterSpacing: ".08em",
  textTransform: "uppercase",
};

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

// Artboard 03: the prompt LIST (pasted as a Python list), one shared negative, variants, Üret.
export default function GeneratePanel({ job, error, busyElsewhere, onGenerate }) {
  const [prompts, setPrompts] = useState("");
  const [negative, setNegative] = useState("");
  const [variants, setVariants] = useState(4);

  const summary = {
    done: `bitti — ${job.done}/${job.total}`,
    stopped: `durduruldu — ${job.done}/${job.total}`,
  }[job.status];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {summary && <Mono size={11} style={{ color: "var(--ink-2)" }}>{summary}</Mono>}

      <Mono size={11} style={LABEL}>Prompt listesi</Mono>
      <textarea
        className="wf-input"
        rows={10}
        value={prompts}
        placeholder={PLACEHOLDER}
        onChange={(e) => setPrompts(e.target.value)}
        style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 12.5 }}
      />

      <Mono size={11} style={LABEL}>Negatif (hepsine)</Mono>
      <textarea
        className="wf-input"
        rows={3}
        value={negative}
        onChange={(e) => setNegative(e.target.value)}
        style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 12.5 }}
      />

      <VariantPicker value={variants} onChange={setVariants} />

      <Btn hl disabled={!prompts.trim() || busyElsewhere}
           onClick={() => onGenerate({ prompts, negative, variants })}
           style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
        <Icon.Sparkle /> Üret
      </Btn>

      {busyElsewhere && (
        <Note size={12} style={{ color: "var(--ink-3)" }}>
          Üretim sürüyor: {job.project} — bitmesini bekle.
        </Note>
      )}
      {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
      {job.status === "error" && (
        <>
          <span style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
            <Icon.Warn />
            <Note size={13} style={{ color: "var(--danger)", fontWeight: 500 }}>Üretim durdu</Note>
          </span>
          {/* The server's own error text -- we never guess the cause. */}
          <Mono size={11} style={RAW_ERROR}>{job.error}</Mono>
        </>
      )}
    </div>
  );
}
