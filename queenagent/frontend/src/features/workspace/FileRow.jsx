import { relativeTime } from "../../shared/time.js";

export default function FileRow({ file, onOpen, onDelete }) {
  // The × sits inside the row, and it is not a way of opening the file.
  const only = (act) => (event) => {
    event.stopPropagation();
    act(file.name);
  };

  return (
    <div className="file-row" title={file.name} onClick={() => onOpen?.(file.name)}>
      <span className="file-chip">{file.ext}</span>
      <span className="file-row__text">
        <span className="file-row__name">{file.name}</span>
        <span className="file-row__meta">project file · {relativeTime(file.modifiedAt)}</span>
      </span>
      {onDelete ? (
        <button
          type="button"
          className="row-x"
          aria-label={`Delete ${file.name}`}
          onClick={only(onDelete)}
        >
          ×
        </button>
      ) : null}
    </div>
  );
}
