import FileList from "./FileList.jsx";
import FileView from "./FileView.jsx";

// The list and the open file share one column. Giving them a column each would push the
// conversation off centre, and the conversation is what the tool is for.
export default function FilePane({ files, projectId, file, on, onChange }) {
  return (
    <aside className={file ? "file-pane open" : "file-pane"}>
      {file ? (
        <FileView file={file} onChange={onChange} onBack={on.closeFile} />
      ) : (
        <FileList files={files} projectId={projectId} on={on} />
      )}
    </aside>
  );
}
