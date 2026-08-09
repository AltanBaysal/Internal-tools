import { relativeTime } from "../../shared/time.js";

export default function FileRow({ file }) {
  return (
    <div className="file-row" title={file.name}>
      <span className="file-chip">{file.ext}</span>
      <span className="file-row__name">{file.name}</span>
      <span className="file-row__when">{relativeTime(file.modifiedAt)}</span>
    </div>
  );
}
