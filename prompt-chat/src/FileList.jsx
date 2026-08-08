import { filesOf } from "./files.js";

// No row is ever marked open: this list leaves the screen the moment a file is opened, so there is
// nothing left to mark.
export default function FileList({ files, projectId, on }) {
  return (
    <div className="list">
      <div className="group">dosyalar</div>
      {filesOf(files, projectId).map((file) => (
        <div key={file.id} className="row">
          <button className="row-open" onClick={() => on.openFile(file.id)}>
            {file.name}
          </button>
          <button
            className="row-delete"
            aria-label={`${file.name} dosyasını sil`}
            onClick={() => on.deleteFile(file.id)}
          >
            ×
          </button>
        </div>
      ))}
      <button className="add" onClick={on.newFile}>
        + Yeni dosya
      </button>
    </div>
  );
}
