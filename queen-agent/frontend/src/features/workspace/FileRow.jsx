import { relativeTime } from "../../shared/time.js";

// One row for both lists, and what it can do is decided by what it is given: the rail hands it no
// way to delete, the project screen does. Which row is open is the caller's answer too -- neither
// list owns the reader.
//
// A box holding buttons rather than a clickable box: a row that only listens for a click has no tab
// stop, no Enter and no focus ring, and opening a file without a mouse was impossible. The × is a
// sibling because a button inside a button is not valid HTML.
export default function FileRow({ file, selected, onOpen, onDelete }) {
  return (
    <div className={selected ? "file-row file-row--selected" : "file-row"} title={file.name}>
      <button type="button" className="file-row__open" onClick={() => onOpen?.(file.name)}>
        <span className="file-chip">{file.ext}</span>
        <span className="file-row__text">
          <span className="file-row__name">{file.name}</span>
          <span className="file-row__meta">project file · {relativeTime(file.modifiedAt)}</span>
        </span>
      </button>
      {onDelete ? (
        <button
          type="button"
          className="row-x"
          title={`Delete ${file.name}`}
          aria-label={`Delete ${file.name}`}
          onClick={() => onDelete(file.name)}
        >
          ×
        </button>
      ) : null}
    </div>
  );
}
