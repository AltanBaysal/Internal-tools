import { useState } from "react";

import { relativeTime } from "../../shared/time.js";
import Markdown from "./Markdown.jsx";

// Three parts, and only the middle one moves: the name of what is being read and the line saying
// where it came from are worth as much on page four as on page one.
//
// `back` is what the two callers differ by. The rail's panel is the rail widened, so it is come back
// from; the project screen's panel is a surface standing beside the grid, so it closes. One
// component either way -- splitting it would copy the header, the Download and its waiting state.
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

      {/* The same parser the answers use. The scale is the container's: this one is a document. */}
      {file ? (
        <div className="reader__body">
          <Markdown text={file.text} />
        </div>
      ) : null}
      {file ? (
        <p className="reader__meta" data-testid="file-meta">
          {/* Not what the file measures -- when it was written, and that it belongs to the project
              rather than to the chat that asked for it. */}
          {`${relativeTime(file.modifiedAt)} · project file`}
        </p>
      ) : null}
    </div>
  );
}
