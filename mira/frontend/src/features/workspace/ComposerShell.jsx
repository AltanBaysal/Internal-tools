// The composer's frame, shared by home and the project screen. It has no behaviour yet: the draft
// rules are Madde 8 and sending is Faz 5.
export default function ComposerShell({ rows, placeholder, note, action }) {
  return (
    <div className="composer">
      <textarea className="composer__input" rows={rows} placeholder={placeholder} />
      <div className="composer__foot">
        {note ? <span className="composer__note">{note}</span> : null}
        <button type="button" className="composer__send" disabled>
          {action}
        </button>
      </div>
    </div>
  );
}
