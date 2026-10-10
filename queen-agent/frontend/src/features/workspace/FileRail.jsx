import { useEffect, useRef, useState } from "react";

import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";
import Spinner from "./Spinner.jsx";
import { DEFAULT_RAIL_WIDTH } from "./railWidth.js";

// The rail sits beside the composer so the user can see what already exists while they are asking
// for more. It has three states and the list is present in exactly one of them:
//
//   folded   -- a strip that still says how many files there are
//   open     -- the list
//   reading  -- the document, and nothing else
//
// The heading is the control when there is something to fold, because "the header folds it" and
// "one click on the strip opens it" are one sentence.
//
// Reading used to keep the list standing beside the reader, so another file could be reached
// without closing this one. Madde 63 gave the document the whole rail instead: the list was taking
// 200 of 560 pixels to offer something the back arrow already offers.
//
// Its rows open a file and, when the caller hands one over, offer a way to delete it -- through the
// app's one confirmation.
//
// Madde 50 gave the rail a grip on its left edge, and Madde 356 (the design's items 158 and 177) gave
// it to the open file too: the list and the document are one width. What travels back up is the
// width that was asked for, not a decision: whether that is a width at all, or is narrow enough to
// mean closing, belongs with the folded state, which is App's (railWidth.js).

function railClass(reading, collapsed, dragging) {
  // Said out loud because the stylesheet has to hear it: the width easing is for folding and opening,
  // and a rail following the pointer has to arrive with it -- the list's and the document's alike.
  const drag = dragging ? " rail--dragging" : "";
  if (reading?.name) return `rail rail--open${drag}`;
  if (collapsed) return "rail rail--collapsed";
  return `rail${drag}`;
}

// The list and the open file are one width (Madde 356), so the held width is written for either.
// Folded, the design's strip stands instead -- but only once nothing is being read: a document pulled
// under the minimum stays at its width, and the fold shows when it closes.
function railStyle(reading, collapsed, width) {
  if (!width || (collapsed && !reading?.name)) return undefined;
  return { width: `${width}px` };
}

// Dragging leftwards widens: the rail's edge is its left one, so the distance the pointer travels is
// subtracted from where it started. The window is what listens, not the grip -- the pointer leaves a
// 6px strip on the first frame of any real drag.
function Grip({ width, onResize, onDrag }) {
  const drag = useRef(null);

  useEffect(() => {
    const move = (event) => {
      if (drag.current) onResize(drag.current.width + (drag.current.x - event.clientX));
    };
    const stop = () => {
      if (!drag.current) return;
      drag.current = null;
      onDrag(false);
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
    };
  }, [onResize, onDrag]);

  return (
    <div
      className="rail__grip"
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize the file list"
      onMouseDown={(event) => {
        // The browser's own answer to a press-and-drag is to select every text the pointer crosses,
        // and a selection only ever starts on the press -- refused here, none starts for the whole
        // drag, wherever the pointer goes or is let go (Madde 381).
        event.preventDefault();
        // Nothing dragged yet means the stylesheet's width is the one on screen, so that is where
        // this drag starts from.
        drag.current = { x: event.clientX, width: width ?? DEFAULT_RAIL_WIDTH };
        onDrag(true);
      }}
    />
  );
}

// Madde 192 gave the list a Refresh; Madde 350 (the design's items 154 and 175) wrote it out, framed
// like the reader's, and put it on the heading's row. Beside the heading rather than inside it: the
// heading is the fold control, and a button cannot stand inside a button.
function RefreshFiles({ onRefresh }) {
  return (
    <button type="button" className="ghost file-list__refresh" onClick={onRefresh}>
      Refresh
    </button>
  );
}

function FileList({ files, loading, error, reading, deleting }) {
  return (
    <div className="file-list">
      {/* The teaching line waits for the answer: until the list has arrived, "no files yet" is a
          guess and not a fact -- and if the answer never came, it is not even a guess. */}
      {loading ? (
        <div className="file-list__spinner">
          <Spinner />
        </div>
      ) : null}
      {error ? <p className="list-error">{error}</p> : null}
      {/* A delete that failed has to be said where it was asked for, or the user walks away
          believing the file is gone. */}
      {deleting?.error ? <p className="list-error">{deleting.error}</p> : null}
      {!loading && files.length
        ? files.map((file) => (
            <FileRow
              key={file.name}
              file={file}
              onOpen={reading?.open}
              onDelete={deleting?.remove}
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
  onRefresh,
}) {
  // Only the stylesheet cares, and only for as long as the pointer is down, so it lives here rather
  // than travelling up with the width.
  const [dragging, setDragging] = useState(false);
  const style = railStyle(reading, collapsed, width);
  // Before the project's list has come there is nothing to count, and a 0 would say it has no files.
  const count = loading ? null : <span className="rail__count">{files.length}</span>;

  if (reading?.name) {
    return (
      <aside
        className={railClass(reading, collapsed, dragging)}
        style={style}
        data-testid="file-rail"
      >
        {onResize ? <Grip width={width} onResize={onResize} onDrag={setDragging} /> : null}
        <FilePanel
          name={reading.name}
          file={reading.file}
          missing={reading.missing}
          error={reading.error}
          onClose={reading.close}
          onRefresh={onRefresh}
        />
      </aside>
    );
  }

  return (
    <aside
      className={railClass(reading, collapsed, dragging)}
      style={style}
      data-testid="file-rail"
    >
      {/* Folded, there is no list on screen for Refresh to be about, so the row is the heading
          alone -- and the click that opens the rail brings it back. */}
      <div className="rail__bar">
        {/* Folded because the shell has no room for both, the strip has nowhere to open into, so
            its heading is a label -- the same sentence the rail says while it is showing a
            document. A button that opened nothing would be a lie. */}
        {foldedByWidth ? (
          <div className="rail__head rail__head--still">
            <span className="rail__label">Project files</span>
            {count}
          </div>
        ) : (
          <button type="button" className="rail__head" aria-expanded={!collapsed} onClick={onToggle}>
            <span className="rail__label">Project files</span>
            {count}
            <span className="rail__chevron">{collapsed ? "‹" : "›"}</span>
          </button>
        )}
        {collapsed ? null : <RefreshFiles onRefresh={onRefresh} />}
      </div>
      {/* Not merely hidden: folded, there is no list, and the strip is what stands in its place. */}
      {collapsed ? null : (
        <>
          {onResize ? <Grip width={width} onResize={onResize} onDrag={setDragging} /> : null}
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
