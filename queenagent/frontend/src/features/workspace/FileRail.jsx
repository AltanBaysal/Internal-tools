import Skeleton from "./Skeleton.jsx";
import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";

// The rail sits beside the composer so the user can see what already exists while they are asking
// for more. Reading a file widens it rather than covering the chat, and folding it away leaves a
// strip that says how much is in there.
//
// The heading is the control in both states -- the header when it is open, the strip when it is
// folded -- because "the header folds it" and "one click on the strip opens it" are one sentence.
function railClass(reading, collapsed) {
  if (reading?.name) return "rail rail--open";
  return collapsed ? "rail rail--collapsed" : "rail";
}

export default function FileRail({ files = [], loading, reading, deleting, collapsed, onToggle }) {
  return (
    <aside className={railClass(reading, collapsed)} data-testid="file-rail">
      {reading?.name ? (
        <FilePanel
          name={reading.name}
          file={reading.file}
          missing={reading.missing}
          error={reading.error}
          onClose={reading.close}
          onDownload={reading.download}
        />
      ) : (
        <>
          <button
            type="button"
            className="rail__head"
            aria-expanded={!collapsed}
            onClick={onToggle}
          >
            <span className="rail__label">Project files</span>
            <span className="rail__count">{files.length}</span>
            <span className="rail__chevron">{collapsed ? "‹" : "›"}</span>
          </button>
          {/* No offer to bring anything back, but a refusal is still worth a line. */}
          {deleting?.error && !collapsed ? (
            <p className="file-list__error">{deleting.error}</p>
          ) : null}
          {/* Not merely hidden: folded, there is no list, and the strip is what stands in its
              place. */}
          {collapsed ? null : (
          <div className="file-list">
            {/* The teaching line waits for the answer: until the list has arrived, "no files yet"
                is a guess and not a fact. */}
            {loading ? <Skeleton rows={3} /> : null}
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
            {!loading && !files.length ? (
              <p className="file-list__empty">
                No files yet — send a message and QueenAgent will create one.
              </p>
            ) : null}
          </div>
          )}
        </>
      )}
    </aside>
  );
}
