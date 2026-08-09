import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";

// Always open, never a toggle: the rail sits beside the composer so the user can see what already
// exists while they are asking for more. Reading a file widens it rather than covering the chat.
export default function FileRail({ files = [], reading }) {
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
          <div className="file-list">
            {files.length ? (
              files.map((file) => <FileRow key={file.name} file={file} onOpen={reading?.open} />)
            ) : (
              <p className="file-list__empty">
                No files yet — send a message and Mira will create one.
              </p>
            )}
          </div>
        </>
      )}
    </aside>
  );
}
