import FileStrip from "./FileStrip.jsx";
import Skeleton from "./Skeleton.jsx";
import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";

// Always open, never a toggle: the rail sits beside the composer so the user can see what already
// exists while they are asking for more. Reading a file widens it rather than covering the chat.
export default function FileRail({ files = [], loading, reading, deleting, onRenameFile }) {
  return (
    <aside className={reading?.name ? "rail rail--open" : "rail"} data-testid="file-rail">
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
          <h2 className="column__title">Project files</h2>
          <FileStrip
            deleted={deleting?.deleted}
            error={deleting?.error}
            onUndo={deleting?.undo}
          />
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
                    onRename={onRenameFile}
                    onDelete={deleting?.remove}
                  />
                ))
              : null}
            {!loading && !files.length ? (
              <p className="file-list__empty">
                No files yet — send a message and Mira will create one.
              </p>
            ) : null}
          </div>
        </>
      )}
    </aside>
  );
}
