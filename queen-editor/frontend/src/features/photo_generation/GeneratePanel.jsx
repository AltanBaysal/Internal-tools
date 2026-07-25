import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";

const RAW_ERROR = {
  color: "var(--ink-3)",
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 3,
  padding: "6px 8px",
  maxWidth: 520,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

// Part 4 is one prompt and one photo: no negative box, no variants, no Stop (Part 5).
export default function GeneratePanel({ job, error, onGenerate }) {
  const [prompt, setPrompt] = useState("");
  const running = job.status === "running";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 520 }}>
      <Mono size={11} style={{ color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" }}>
        Prompt
      </Mono>
      <textarea
        className="wf-input"
        rows={4}
        value={prompt}
        disabled={running}
        onChange={(e) => setPrompt(e.target.value)}
        style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 12.5 }}
      />
      <Btn hl disabled={!prompt.trim() || running} onClick={() => onGenerate(prompt)}
           style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
        <Icon.Sparkle /> {running ? "üretiliyor…" : "Üret"}
      </Btn>

      {running && <Mono size={11} style={{ color: "var(--accent)" }}>ComfyUI çalışıyor — 1-2 dakika sürebilir</Mono>}
      {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
      {job.status === "error" && (
        <>
          <span style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
            <Icon.Warn />
            <Note size={13} style={{ color: "var(--danger)", fontWeight: 500 }}>Üretim başarısız</Note>
          </span>
          {/* The server's own error text -- we never guess the cause. */}
          <Mono size={11} style={RAW_ERROR}>{job.error}</Mono>
        </>
      )}
    </div>
  );
}
