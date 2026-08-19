import { useEffect, useRef } from "react";

import Skeleton from "./Skeleton.jsx";
import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";
import { DEFAULT_RAIL_WIDTH } from "./railWidth.js";

// The rail sits beside the composer so the user can see what already exists while they are asking
// for more. It has three states and the list is present in two of them:
//
//   folded   -- a strip that still says how many files there are
//   open     -- the list
//   reading  -- the list beside the reader, so another file can be reached without closing this one
//
// The heading is the control when there is something to fold, because "the header folds it" and
// "one click on the strip opens it" are one sentence. While a document is being read there is
// nothing to fold, so the heading is a label again.
//
// Its rows open a file and, when the caller hands one over, offer a way to delete it -- the same
// question the project screen asks. The row being read is the exception: deleting a file out from
// under the reader leaves the user looking at nothing.
//
// Madde 50 gave the open list a grip on its left edge. What travels back up is the width that was
// asked for, not a decision: whether that is a width at all, or is narrow enough to mean closing,
// belongs with the folded state, which is App's (railWidth.js).

function railClass(reading, collapsed) {
  if (reading?.name) return "rail rail--open";
  return collapsed ? "rail rail--collapsed" : "rail";
}

// The rail's own width is only its own while it is a list. Folded it is the design's strip, and
// while a document is open the width belongs to the document -- the dragged one comes back after.
function railStyle(reading, collapsed, width) {
  if (reading?.name || collapsed || !width) return undefined;
  return { width: `${width}px` };
}

// Dragging leftwards widens: the rail's edge is its left one, so the distance the pointer travels is
// subtracted from where it started. The window is what listens, not the grip -- the pointer leaves a
// 6px strip on the first frame of any real drag.
function Grip({ width, onResize }) {
  const drag = useRef(null);

  useEffect(() => {
    const move = (event) => {
      if (drag.current) onResize(drag.current.width + (drag.current.x - event.clientX));
    };
    const stop = () => {
      drag.current = null;
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
    };
  }, [onResize]);

  return (
    <div
      className="rail__grip"
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize the file list"
      onMouseDown={(event) => {
        // Nothing dragged yet means the stylesheet's width is the one on screen, so that is where
        // this drag starts from.
        drag.current = { x: event.clientX, width: width ?? DEFAULT_RAIL_WIDTH };
      }}
    />
  );
}

function FileList({ files, loading, error, reading, deleting }) {
  return (
    <div className="file-list">
      {/* The teaching line waits for the answer: until the list has arrived, "no files yet" is a
          guess and not a fact -- and if the answer never came, it is not even a guess. */}
      {loading ? <Skeleton rows={3} /> : null}
      {error ? <p className="list-error">{error}</p> : null}
      {/* A delete that failed has to be said where it was asked for, or the user walks away
          believing the file is gone. */}
      {deleting?.error ? <p className="list-error">{deleting.error}</p> : null}
      {!loading && files.length
        ? files.map((file) => (
            <FileRow
              key={file.name}
              file={file}
              selected={file.name === reading?.name}
              onOpen={reading?.open}
              onDelete={file.name === reading?.name ? undefined : deleting?.remove}
            />
          ))
        : null}
      {!loading && !error && !files.length ? (
        <p className="file-list__empty">
          No files yet — send a message and QueenAgent will create one.
        </p>
      ) : null}
    </div>
  );
}

export default function FileRail({
  files = [],
  loading,
  error,
  reading,
  deleting,
  collapsed,
  foldedByWidth,
  width,
  onResize,
  onToggle,
}) {
  const style = railStyle(reading, collapsed, width);

  if (reading?.name) {
    return (
      <aside className={railClass(reading, collapsed)} style={style} data-testid="file-rail">
        <div className="rail__list">
          <div className="rail__head rail__head--still">
            <span className="rail__label">Project files</span>
            <span className="rail__count">{files.length}</span>
          </div>
          <FileList
            files={files}
            loading={loading}
            error={error}
            reading={reading}
            deleting={deleting}
          />
        </div>
        {/* Come back from rather than closed: this panel is the rail widened, and the list it
            widened away from is still standing beside it. */}
        <FilePanel
          back
          name={reading.name}
          file={reading.file}
          missing={reading.missing}
          error={reading.error}
          onClose={reading.close}
          onDownload={reading.download}
        />
      </aside>
    );
  }

  return (
    <aside className={railClass(reading, collapsed)} style={style} data-testid="file-rail">
      {/* Folded because the shell has no room for both, the strip has nowhere to open into, so its
          heading is a label -- the same sentence the rail says while it is showing a document. A
          button that opened nothing would be a lie. */}
      {foldedByWidth ? (
        <div className="rail__head rail__head--still">
          <span className="rail__label">Project files</span>
          <span className="rail__count">{files.length}</span>
        </div>
      ) : (
        <button type="button" className="rail__head" aria-expanded={!collapsed} onClick={onToggle}>
          <span className="rail__label">Project files</span>
          <span className="rail__count">{files.length}</span>
          <span className="rail__chevron">{collapsed ? "‹" : "›"}</span>
        </button>
      )}
      {/* Not merely hidden: folded, there is no list, and the strip is what stands in its place. */}
      {collapsed ? null : (
        <>
          {onResize ? <Grip width={width} onResize={onResize} /> : null}
          <FileList
            files={files}
            loading={loading}
            error={error}
            reading={reading}
            deleting={deleting}
          />
        </>
      )}
    </aside>
  );
}
