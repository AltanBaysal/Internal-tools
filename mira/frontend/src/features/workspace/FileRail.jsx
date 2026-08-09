import FileRow from "./FileRow.jsx";

// Always open, never a toggle: the rail sits beside the composer so the user can see what already
// exists while they are asking for more.
export default function FileRail({ files = [] }) {
  return (
    <aside className="rail" data-testid="file-rail">
      <h2 className="column__title">Project files</h2>
      <div className="file-list">
        {files.length ? (
          files.map((file) => <FileRow key={file.name} file={file} />)
        ) : (
          <p className="file-list__empty">
            No files yet — send a message and Mira will create one.
          </p>
        )}
      </div>
    </aside>
  );
}
