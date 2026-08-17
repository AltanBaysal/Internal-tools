import { useEffect, useId, useRef } from "react";

// The app's only confirmation language. It knows nothing about what is being deleted -- every
// sentence arrives from the caller -- which is what lets one pattern serve a project, a chat and a
// file without any of them borrowing the browser's box.
//
// It registers no key listener: Escape belongs to App's single listener, so the order of what
// closes first stays in one place.

export default function ConfirmDialog({ title, body, confirmLabel, onConfirm, onCancel }) {
  const named = useId();
  const cancel = useRef(null);

  // A destructive question should not have Enter land on the destructive answer.
  useEffect(() => {
    cancel.current?.focus();
  }, []);

  return (
    <div className="dialog" onClick={onCancel}>
      {/* Reading the sentence should not dismiss the question, so the card keeps the click. */}
      <div
        className="dialog__card"
        role="dialog"
        aria-modal="true"
        aria-labelledby={named}
        onClick={(event) => event.stopPropagation()}
      >
        <h2 className="dialog__title" id={named}>
          {title}
        </h2>
        <p className="dialog__body">{body}</p>
        <div className="dialog__actions">
          <button type="button" className="ghost" ref={cancel} onClick={onCancel}>
            Cancel
          </button>
          <button type="button" className="dialog__confirm" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
