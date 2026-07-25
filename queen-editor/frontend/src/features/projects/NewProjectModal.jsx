import { useEffect, useState } from "react";

import { Btn, Hand, Mono, Note } from "../../vendor/kit.jsx";

// The server owns the name rules; this modal only forwards the message it gets back, so no rule
// is duplicated here. "Oluştur" is disabled while the box is empty or a request is in flight
// (Drive can take a moment over FUSE -- no double create).
export default function NewProjectModal({ onCancel, onCreate }) {
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  function submit() {
    setBusy(true);
    setError(null);
    onCreate(name).catch((err) => {
      setError(err.message);
      setBusy(false);
    });
  }

  return (
    <div className="wf-scrim" onClick={onCancel}>
      <div
        className="wf-card wf-card--shadow"
        onClick={(e) => e.stopPropagation()}
        style={{ width: 380, padding: 20, display: "flex", flexDirection: "column", gap: 12 }}
      >
        <Hand size={17}>Yeni proje</Hand>
        <Mono
          size={11}
          style={{ color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" }}
        >
          Proje adı
        </Mono>
        <input
          className="wf-input"
          autoFocus
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setError(null);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && name && !busy) submit();
          }}
          style={error ? { borderColor: "var(--danger)" } : undefined}
        />
        {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
          <Btn ghost onClick={onCancel} disabled={busy}>Vazgeç</Btn>
          <Btn hl onClick={submit} disabled={!name || busy}>
            {busy ? "Oluşturuluyor…" : "Oluştur"}
          </Btn>
        </div>
      </div>
    </div>
  );
}
