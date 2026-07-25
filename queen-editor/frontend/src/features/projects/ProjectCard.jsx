import { formatModified } from "../../shared/date.js";
import { Hand, Mono } from "../../vendor/kit.jsx";

// Deliberately NOT clickable: the project screen lands in Part 4, so nothing here promises a
// click (no pointer cursor, no hover lift). Part 4 adds one onClick.
export default function ProjectCard({ name, modifiedAt }) {
  return (
    <div
      className="wf-card"
      style={{
        aspectRatio: "4/3",
        padding: 14,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
      }}
    >
      <Hand size={16} style={{ alignSelf: "flex-start" }}>{name}</Hand>
      <Mono size={11} style={{ color: "var(--ink-3)", alignSelf: "flex-end" }}>
        {formatModified(modifiedAt)}
      </Mono>
    </div>
  );
}
