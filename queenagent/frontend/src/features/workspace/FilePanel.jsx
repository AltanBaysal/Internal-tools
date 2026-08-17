import { useState } from "react";

import { relativeTime } from "../../shared/time.js";

const KB = 1024;

function formatSize(bytes) {
  if (bytes < KB) return `${bytes} B`;
  if (bytes < KB * KB) return `${(bytes / KB).toFixed(1)} KB`;
  return `${(bytes / KB / KB).toFixed(1)} MB`;
}

export default function FilePanel({ name, file, missing, error, onClose, onDownload }) {
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
        <button type="button" className="back back--inline" onClick={onClose}>
          ←
        </button>
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
      </header>

      {missing ? <p className="screen__missing">That file is gone.</p> : null}
      {error ? <p className="reader__error">{error}</p> : null}
      {failed ? <p className="reader__error">{failed}</p> : null}

      {/* Plain text, not rendered markdown: create_file writes text and the panel shows text. */}
      {file ? <div className="reader__body">{file.text}</div> : null}
      {file ? (
        <p className="reader__meta" data-testid="file-meta">
          {`${file.ext} · ${formatSize(file.size)} · ${relativeTime(file.modifiedAt)}`}
        </p>
      ) : null}
    </div>
  );
}
