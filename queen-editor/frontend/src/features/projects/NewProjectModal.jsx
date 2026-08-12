import { useEffect, useRef, useState } from "react";

import { checkProjectName } from "../../shared/api.js";
import { Btn, Hand, Mono, Note } from "../../vendor/kit.jsx";

// Long enough that the request goes once the typing stops rather than once per key, short enough
// that the warning still feels like it belongs to what was typed.
const CHECK_MS = 300;

// The server owns the name rules; this modal never keeps a copy. It warns as the name is typed by
// asking the server whether the name would be accepted and printing whatever sentence comes back --
// and "Oluştur" is disabled while the box is empty, while a warning stands, or while a request is
// in flight (Drive can take a moment over FUSE -- no double create).
export default function NewProjectModal({ onCancel, onCreate }) {
  const [name, setName] = useState("");
  // Two different things, one place on screen: what the server says the name WOULD be, and what it
  // said when the project was actually asked for.
  const [warning, setWarning] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  // A box nobody has touched is not a mistake: the design's warning appears once a name has been
  // entered, so opening the modal must not greet the user with "Proje adı boş olamaz."
  const touched = useRef(false);

  useEffect(() => {
    if (!touched.current) return undefined;
    let current = true;
    const timer = setTimeout(() => {
      checkProjectName(name)
        .then((body) => { if (current) setWarning(body?.error || null); })
        // A preview must never stand in the way: an unreachable server is not a broken name, and
        // pressing Oluştur still goes through the real rules.
        .catch(() => { if (current) setWarning(null); });
    }, CHECK_MS);
    // Cancels both the pending request's effect and its answer: only the newest name's verdict is
    // allowed on screen, however the replies happen to come back.
    return () => { current = false; clearTimeout(timer); };
  }, [name]);

  useEffect(() => {
    const onKey = (e) => {
      // While the create request is in flight the modal must not pretend to cancel -- the
      // server is still creating the project (spec §1B).
      if (e.key === "Escape" && !busy) onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, busy]);

  const blocked = !name || busy || Boolean(warning) || Boolean(error);

  function submit() {
    setBusy(true);
    setError(null);
    onCreate(name).catch((err) => {
      setError(err.message);
      setBusy(false);
    });
  }

  const said = warning || error;

  return (
    <div className="wf-scrim" onClick={busy ? undefined : onCancel}>
      <div
        className="wf-card wf-card--shadow"
        onClick={(e) => e.stopPropagation()}
        // 400: the widest of the plain windows, because the name box carries a rule line under it
        // and a warning that must not wrap mid-word (madde 105).
        style={{ width: 400, padding: 20, display: "flex", flexDirection: "column", gap: 12 }}
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
            touched.current = true;
            setName(e.target.value);
            setError(null);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !blocked) submit();
          }}
          style={said ? { borderColor: "var(--danger)" } : undefined}
        />
        {said && <Note size={12} style={{ color: "var(--danger)" }}>{said}</Note>}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
          <Btn ghost onClick={onCancel} disabled={busy}>Vazgeç</Btn>
          <Btn hl onClick={submit} disabled={blocked}>
            {busy ? "Oluşturuluyor…" : "Oluştur"}
          </Btn>
        </div>
      </div>
    </div>
  );
}
