// The file list's notice line. Its first job is the undo offer: no timer, so it goes when Undo is
// pressed, when another delete replaces it, or when the project is left -- what expires is the
// offer, never the file, which stays in the trash. It is also where a failed rename says so, since
// a list that quietly refuses to change is worse than one that explains itself.
export default function FileStrip({ deleted, error, onUndo }) {
  if (!deleted && !error) return null;
  return (
    <div className="strip">
      {deleted ? (
        <div className="strip__row">
          <span className="strip__line">File deleted.</span>
          <button type="button" className="strip__undo" onClick={onUndo}>
            Undo
          </button>
        </div>
      ) : null}
      {error ? <span className="strip__detail">{error}</span> : null}
    </div>
  );
}
