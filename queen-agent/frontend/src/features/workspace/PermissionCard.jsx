import { useState } from "react";

// The question Madde 99 raises, seen. It stands in the transcript while the turn is paused, and the
// two buttons are the only way past it apart from Stop -- which is the send button, already there.
//
// The reason lives here rather than in App: it is the box's momentary state, the way the composer's
// draft is, and only the finished sentence leaves.
export default function PermissionCard({ tool, args, onAllow, onDeny }) {
  const [reason, setReason] = useState("");

  return (
    <div className="permission" data-testid="permission">
      <span className="permission__line">QueenAgent wants to run {tool}</span>
      {/* Raw and unparsed. run_tool is the one reader of these and a second one here would drift
          from it on the first change to either -- while approving a write nobody can see is
          approving nothing at all. */}
      <pre className="permission__args">{args}</pre>
      <div className="permission__row">
        {/* Called rather than handed over: onClick={onAllow} would send a click event up, and an
            approval has nothing to carry. */}
        <button type="button" className="permission__allow" onClick={() => onAllow?.()}>
          Allow
        </button>
        <button type="button" className="permission__deny" onClick={() => onDeny?.(reason.trim())}>
          Deny
        </button>
        {/* Beside Deny because that is the button that needs it: an approval has nothing to add,
            and a refusal with nothing written on it is a wall the model walks into again. */}
        <input
          type="text"
          className="permission__reason"
          placeholder="Why not? (optional)"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
      </div>
    </div>
  );
}
