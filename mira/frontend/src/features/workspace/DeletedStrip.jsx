// No timer. The strip goes when Undo is pressed, when another delete replaces it, or when the
// project is left -- what expires is the offer, never the file, which stays in the trash.
export default function DeletedStrip({ deleted, error, onUndo }) {
  if (!deleted) return null;
  return (
    <div className="strip">
      <div className="strip__row">
        <span className="strip__line">File deleted.</span>
        <button type="button" className="strip__undo" onClick={onUndo}>
          Undo
        </button>
      </div>
      {error ? <span className="strip__detail">{error}</span> : null}
    </div>
  );
}
