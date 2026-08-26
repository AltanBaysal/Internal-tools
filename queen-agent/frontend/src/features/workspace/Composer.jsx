import { useState } from "react";

// The two marks the one button wears. Written here rather than inline: the running state picks
// between them, and a reader should see both at once to know they are a pair.
const SEND = "↑";
const STOP = "⏹";

// The draft lives here rather than in App: it is the box's momentary state, not something a screen
// keeps. Only the finished text leaves, through onSubmit.
// `foot` is what stands to the left of the button. karar 1 settled that order -- Skills · model ·
// send -- and the box holds the room without knowing what goes in it.
//
// `running` says an answer is on its way, and it turns the one action button into a stop. There is
// nothing to send while one is running, so the button that sends is the one free to stop -- and a
// control with two states keeps both of them here, where the button already lives.
export default function Composer({ rows, placeholder, action, foot, running, onStop, onSubmit }) {
  const [draft, setDraft] = useState("");
  const ready = draft.trim().length > 0;
  // An empty draft is what blocks sending; blocking a stop with it would kill the control in the
  // very case it exists for. The accent follows: while an answer runs, stopping is the only action
  // there is, so it is the primary one.
  const live = running || ready;

  const submit = async () => {
    // onSubmit is optional: this component owns the draft rules, and where a message goes is
    // decided in Madde 10.
    if (!ready || !onSubmit) return;
    const text = draft.trim();
    // Cleared straight away, because the design wants the bubble to appear immediately. If the
    // message is refused the sentence comes back -- losing it would lose work the user did.
    setDraft("");
    try {
      await onSubmit(text);
    } catch {
      // Unless they have started writing something else in the meantime, which is theirs now.
      setDraft((current) => current || text);
    }
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
        {foot}
        <button
          type="button"
          className={live ? "composer__send composer__send--ready" : "composer__send"}
          disabled={!live}
          /* The word is gone from the face, so the name is written where it can still be read:
             aria-label for a screen reader, title for a mouse resting on it. With aria-label set
             the name is not computed from what is inside, so the mark cannot leak into it. */
          aria-label={running ? "Stop" : action}
          title={running ? "Stop" : action}
          /* Split above submit rather than inside it: submit owns the draft's rules and has no
             reason to learn about stopping. */
          onClick={running ? onStop : submit}
        >
          {running ? STOP : SEND}
        </button>
      </div>
    </div>
  );
}
