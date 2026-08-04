import { useEffect } from "react";

import { Btn, Note } from "../vendor/kit.jsx";

// The design writes its three confirms out three times; here they are one component, because the
// only things that differ are the words, the width and whether the action destroys something.
// Destructive confirms get the filled red button, everything else the accent one.
export default function ConfirmModal({ title, body, confirmLabel, busyLabel, danger, busy,
                                       width = 320, onCancel, onConfirm }) {
  useEffect(() => {
    // While the action is in flight the modal must not pretend to cancel: the server is already
    // doing the thing.
    const onKey = (e) => { if (e.key === "Escape" && !busy) onCancel(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, busy]);

  return (
    <div className="wf-scrim" onClick={busy ? undefined : onCancel}>
      <div className="wf-card wf-card--shadow" onClick={(e) => e.stopPropagation()}
           style={{ width, padding: 18, display: "flex", flexDirection: "column", gap: 10 }}>
        <Note size={14}>{title}</Note>
        {body && <Note size={12} style={{ color: "var(--ink-2)" }}>{body}</Note>}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
          <Btn sm ghost onClick={onCancel} disabled={busy}>Vazgeç</Btn>
          <Btn sm hl={!danger} onClick={onConfirm} disabled={busy}
               style={danger
                 ? { background: "var(--danger)", borderColor: "var(--danger)", color: "#fff" }
                 : undefined}>
            {busy && busyLabel ? busyLabel : confirmLabel}
          </Btn>
        </div>
      </div>
    </div>
  );
}
