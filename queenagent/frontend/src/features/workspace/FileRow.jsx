import { relativeTime } from "../../shared/time.js";

export default function FileRow({ file, onOpen, onRename, onDelete }) {
  // Both buttons sit inside the row, and neither of them is a way of opening the file.
  const only = (act) => (event) => {
    event.stopPropagation();
    act(file.name);
  };

  return (
    <div className="file-row" title={file.name} onClick={() => onOpen?.(file.name)}>
      <span className="file-chip">{file.ext}</span>
      <span className="file-row__name">{file.name}</span>
      <span className="file-row__when">{relativeTime(file.modifiedAt)}</span>
      {onRename ? (
        <button
          type="button"
          className="row-act"
          aria-label={`Rename ${file.name}`}
          onClick={only(onRename)}
        >
          name
        </button>
      ) : null}
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
