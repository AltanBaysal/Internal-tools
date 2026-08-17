import Skeleton from "./Skeleton.jsx";
import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";

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
// Its rows do one thing: open a file. Deleting lives on the project screen, where the list is the
// subject rather than something standing beside a conversation.

function railClass(reading, collapsed) {
  if (reading?.name) return "rail rail--open";
  return collapsed ? "rail rail--collapsed" : "rail";
}

function FileList({ files, loading, reading }) {
  return (
    <div className="file-list">
      {/* The teaching line waits for the answer: until the list has arrived, "no files yet" is a
          guess and not a fact. */}
      {loading ? <Skeleton rows={3} /> : null}
      {!loading && files.length
        ? files.map((file) => (
            <FileRow
              key={file.name}
              file={file}
              selected={file.name === reading?.name}
              onOpen={reading?.open}
            />
          ))
        : null}
      {!loading && !files.length ? (
        <p className="file-list__empty">
          No files yet — send a message and QueenAgent will create one.
        </p>
      ) : null}
    </div>
  );
}

export default function FileRail({ files = [], loading, reading, collapsed, onToggle }) {
  if (reading?.name) {
    return (
      <aside className={railClass(reading, collapsed)} data-testid="file-rail">
        <div className="rail__list">
          <div className="rail__head rail__head--still">
            <span className="rail__label">Project files</span>
            <span className="rail__count">{files.length}</span>
          </div>
          <FileList files={files} loading={loading} reading={reading} />
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
    <aside className={railClass(reading, collapsed)} data-testid="file-rail">
      <button type="button" className="rail__head" aria-expanded={!collapsed} onClick={onToggle}>
        <span className="rail__label">Project files</span>
        <span className="rail__count">{files.length}</span>
        <span className="rail__chevron">{collapsed ? "‹" : "›"}</span>
      </button>
      {/* Not merely hidden: folded, there is no list, and the strip is what stands in its place. */}
      {collapsed ? null : <FileList files={files} loading={loading} reading={reading} />}
    </aside>
  );
}
