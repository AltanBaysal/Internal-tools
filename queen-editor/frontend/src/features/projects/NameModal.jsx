import { useEffect, useRef, useState } from "react";

import { checkProjectName } from "../../shared/api.js";
import { Btn, Hand, Mono, Note } from "../../vendor/kit.jsx";

// Long enough that the request goes once the typing stops rather than once per key, short enough
// that the warning still feels like it belongs to what was typed.
const CHECK_MS = 300;

// A window that asks for a project name -- to open one with, or to give one another. Both are the
// same window, so it is written once and its heading, its opening value, its words and its measure
// come from whoever opened it.
//
// The server owns the name rules; this modal never keeps a copy. It warns as the name is typed by
// asking the server whether the name would be accepted and printing whatever sentence comes back --
// and the button is disabled while the box is empty, while a warning stands, or while a request is
// in flight (Drive can take a moment over FUSE -- no double press).
//
// A name already taken is a clash rather than a broken rule and the live check knows nothing about
// the disk, so that one only appears once the button is pressed and the server refuses.
export default function NameModal({ title, value = "", submitLabel, busyLabel, width = 400,
                                    onCancel, onSubmit }) {
  const [name, setName] = useState(value);
  // Two different things, one place on screen: what the server says the name WOULD be, and what it
  // said when the name was actually sent.
  const [warning, setWarning] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  // A box nobody has touched is not a mistake: the design's warning appears once a name has been
  // entered, so opening the modal must not greet the user with "Proje adı boş olamaz."
  const touched = useRef(false);
  const box = useRef(null);

  // Opened on a name that is already there: the whole of it is selected, so one keystroke replaces
  // it and nobody has to clear the box by hand.
  useEffect(() => { if (value) box.current?.select(); }, [value]);

  useEffect(() => {
    if (!touched.current) return undefined;
    let current = true;
    const timer = setTimeout(() => {
      checkProjectName(name)
        .then((body) => { if (current) setWarning(body?.error || null); })
        // A preview must never stand in the way: an unreachable server is not a broken name, and
        // pressing the button still goes through the real rules.
        .catch(() => { if (current) setWarning(null); });
    }, CHECK_MS);
    // Cancels both the pending request's effect and its answer: only the newest name's verdict is
    // allowed on screen, however the replies happen to come back.
    return () => { current = false; clearTimeout(timer); };
  }, [name]);

  useEffect(() => {
    const onKey = (e) => {
      // While the request is in flight the modal must not pretend to cancel -- the server is still
      // working on it (spec §1B).
      if (e.key === "Escape" && !busy) onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, busy]);

  const blocked = !name || busy || Boolean(warning) || Boolean(error);

  function submit() {
    setBusy(true);
    setError(null);
    onSubmit(name).catch((err) => {
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
        style={{ width, padding: 20, display: "flex", flexDirection: "column", gap: 12 }}
      >
        <Hand size={17}>{title}</Hand>
        <Mono
          size={11}
          style={{ color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" }}
        >
          Proje adı
        </Mono>
        <input
          className="wf-input"
          ref={box}
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
            {busy ? busyLabel : submitLabel}
          </Btn>
        </div>
      </div>
    </div>
  );
}
