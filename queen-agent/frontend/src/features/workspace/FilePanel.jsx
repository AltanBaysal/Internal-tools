import { useState } from "react";

import { relativeTime } from "../../shared/time.js";
import Markdown from "./Markdown.jsx";

// Three parts, and only the middle one moves: the name of what is being read and the line saying
// where it came from are worth as much on page four as on page one.
//
// `back` is what the two callers differ by. The rail's panel is the rail widened, so it is come back
// from; the project screen's panel is a surface standing beside the grid, so it closes. One
// component either way -- splitting it would copy the header, the Download and its waiting state.
function isDocument(name) {
  return /\.md$/i.test(name);
}

export default function FilePanel({ name, file, missing, error, back, onClose, onDownload }) {
  const [preparing, setPreparing] = useState(false);
  const [failed, setFailed] = useState(null);

  const download = async () => {
    setPreparing(true);
    setFailed(null);
    try {
      await onDownload?.();
    } catch (failure) {
      setFailed(failure.message);
    } finally {
      setPreparing(false);
    }
  };

  return (
    <div className="reader">
      <header className="reader__head">
        {back ? (
          <button type="button" className="back back--inline" onClick={onClose}>
            ←
          </button>
        ) : null}
        <span className="reader__name">{file ? file.name : name}</span>
        {/* The width is fixed so the label can change inside it without moving the button. */}
        <button
          type="button"
          className="ghost reader__download"
          onClick={download}
          disabled={preparing}
        >
          {preparing ? "preparing…" : "Download"}
        </button>
        {back ? null : (
          <button type="button" className="reader__close" title="Close" onClick={onClose}>
            ×
          </button>
        )}
      </header>

      {missing ? <p className="reader__note">That file is gone.</p> : null}
      {error ? <p className="reader__error">{error}</p> : null}
      {failed ? <p className="reader__error">{failed}</p> : null}

      {/* A document is parsed -- the same parser the answers use, at the container's own scale.
          Anything else is read as it was written: Markdown eats a JSON file's indentation and turns
          a Python comment into a heading. The decision comes off the name rather than the chip,
          whose three letters say "jso" and are not an extension. */}
      {file ? (
        <div className="reader__body">
          {isDocument(file.name) ? (
            <Markdown text={file.text} />
          ) : (
            <pre className="reader__code">{file.text}</pre>
          )}
        </div>
      ) : null}
      {file ? (
        <p className="reader__meta" data-testid="file-meta">
          {/* Not what the file measures -- when it was written. Whose file it is was here too and
              left: it read the same under every file, and the screen is full with one open. */}
          {relativeTime(file.modifiedAt)}
        </p>
      ) : null}
    </div>
  );
}
