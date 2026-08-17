import { useState } from "react";

// The draft lives here rather than in App: it is the box's momentary state, not something a screen
// keeps. Only the finished text leaves, through onSubmit.
export default function Composer({ rows, placeholder, action, onSubmit }) {
  const [draft, setDraft] = useState("");
  const ready = draft.trim().length > 0;

  const submit = () => {
    // onSubmit is optional: this component owns the draft rules, and where a message goes is
    // decided in Madde 10.
    if (!ready || !onSubmit) return;
    onSubmit(draft.trim());
    setDraft("");
  };

  const onKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="composer">
      <textarea
        className="composer__input"
        rows={rows}
        placeholder={placeholder}
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={onKeyDown}
      />
      <div className="composer__foot">
        <button
          type="button"
          className={ready ? "composer__send composer__send--ready" : "composer__send"}
          disabled={!ready}
          onClick={submit}
        >
          {action}
        </button>
      </div>
    </div>
  );
}
