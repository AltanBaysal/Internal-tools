import { useState } from "react";

// A message being corrected in its own place (Madde 197). The draft lives here for the reason the
// composer's does: it is the field's momentary state, not something the chat keeps -- and only the
// finished sentence leaves, through onConfirm.
//
// The keys are the composer's: enter confirms, shift-enter opens a line, escape gives up. Two
// writable areas asking for two different keys is how both of them get used wrongly.
export default function EditMessage({ text, onConfirm, onCancel }) {
  const [draft, setDraft] = useState(text);
  const ready = draft.trim().length > 0;
  const confirm = () => {
    if (ready) onConfirm(draft.trim());
  };
  return (
    <div className="msg__editing">
      <textarea
        className="msg__editing-input"
        rows={2}
        value={draft}
        autoFocus
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Escape") onCancel();
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            confirm();
          }
        }}
      />
      <div className="msg__editing-actions">
        {/* Icons rather than words (user, 8 September), and their names are written where they can
            still be read: a control with no name is invisible to the keyboard and to a test. */}
        <button
          type="button"
          className="msg__editing-cancel"
          aria-label="Cancel edit"
          title="Cancel edit"
          onClick={onCancel}
        >
          ✕
        </button>
        <button
          type="button"
          className="msg__editing-confirm"
          aria-label="Confirm edit"
          title="Confirm edit"
          disabled={!ready}
          onClick={confirm}
        >
          ✓
        </button>
      </div>
    </div>
  );
}
