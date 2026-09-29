import CopyButton from "./CopyButton.jsx";

// A project list that could not be read, on All projects and on the naming screen alike (the
// design's 172). One plain sentence: what came back -- a Flask page is HTML, an unreachable server
// is the browser's words -- is no sentence to read, so Copy puts it on the clipboard exactly as it
// came, for pasting wherever the error is looked into. Nothing stands around it: with the list
// unknown, the count is unknown, not zero.
export default function ProjectsFailure({ error, onRetry }) {
  return (
    <div className="empty">
      <p className="empty__error">Couldn&apos;t load projects.</p>
      <div className="empty__actions">
        <button type="button" className="failure__retry" onClick={onRetry}>
          Try again
        </button>
        <CopyButton text={error} className="empty__copy" />
      </div>
    </div>
  );
}
