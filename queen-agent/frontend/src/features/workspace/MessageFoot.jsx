// Which of the versions standing in one place is showing, and the way to the ones beside it
// (Madde 195). Drawn only where there is more than one: every message carries the field, and arrows
// under a sentence with nothing beside it offer to step through one thing.
function Versions({ standing, onVersion }) {
  if (!standing || standing.of < 2) return null;
  const step = (by) => onVersion?.(standing.versions[standing.index + by]);
  return (
    <div className="versions">
      <button
        type="button"
        className="versions__step"
        aria-label="Previous version"
        title="Previous version"
        disabled={standing.index === 0}
        onClick={() => step(-1)}
      >
        ‹
      </button>
      <span className="versions__count">
        {standing.index + 1}/{standing.of}
      </span>
      <button
        type="button"
        className="versions__step"
        aria-label="Next version"
        title="Next version"
        disabled={standing.index === standing.of - 1}
        onClick={() => step(1)}
      >
        ›
      </button>
    </div>
  );
}

// The line under a bubble (Madde 199): which version is showing, and the way to correct the
// sentence. .msg is a column, so the strip and the pencil put separately there each took a line of
// their own; here they stand beside each other, the note first and the way to change it after it.
//
// The pencil is there when the caller hands one over. Whether this message can be edited at all,
// and whether it is being edited right now, are already decided where the message is drawn -- and
// a second place deciding the same thing is how the two answers drift apart.
//
// Nothing to hold is no row: the strip draws nothing where a message stands alone, and an empty
// div would only widen the column's gap under every answer in the chat.
export default function MessageFoot({ standing, onVersion, onEdit }) {
  if (!onEdit && !(standing?.of > 1)) return null;
  return (
    <div className="msg__foot">
      <Versions standing={standing} onVersion={onVersion} />
      {onEdit ? (
        <button
          type="button"
          className="msg__edit"
          aria-label="Edit message"
          title="Edit message"
          onClick={onEdit}
        >
          ✎
        </button>
      ) : null}
    </div>
  );
}
