import { useEffect } from "react";

import { Btn, Note } from "../../vendor/kit.jsx";

// The design's delete confirm, worded for one photo. Written for this screen alone -- Part 12
// brings three more confirms, and that is when a shared component earns its place.
export default function PhotoDeleteModal({ onCancel, onConfirm, busy }) {
  useEffect(() => {
    // While the delete is in flight the modal must not pretend to cancel: the server is already
    // removing the photo.
    const onKey = (e) => { if (e.key === "Escape" && !busy) onCancel(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, busy]);

  return (
    <div className="wf-scrim" onClick={busy ? undefined : onCancel}>
      <div className="wf-card wf-card--shadow" onClick={(e) => e.stopPropagation()}
           style={{ width: 320, padding: 18, display: "flex", flexDirection: "column", gap: 10 }}>
        <Note size={14}>Bu fotoğraf silinsin mi?</Note>
        <Note size={12} style={{ color: "var(--ink-2)" }}>Bu işlem geri alınamaz.</Note>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
          <Btn sm ghost onClick={onCancel} disabled={busy}>Vazgeç</Btn>
          <Btn sm onClick={onConfirm} disabled={busy}
               style={{ background: "var(--danger)", borderColor: "var(--danger)", color: "#fff" }}>
            {busy ? "Siliniyor…" : "Sil"}
          </Btn>
        </div>
      </div>
    </div>
  );
}
