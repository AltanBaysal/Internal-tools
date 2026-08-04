import { formatModified } from "../../shared/date.js";
import { navigate } from "../../shared/router.js";
import { Hand, Mono } from "../../vendor/kit.jsx";

// The card opens the project screen. A real <button> so the keyboard can open it too; the
// wf-card look is kept by resetting the button's own chrome.
export default function ProjectCard({ name, modifiedAt }) {
  return (
    <button
      type="button"
      className="wf-card"
      onClick={() => navigate(`/projects/${encodeURIComponent(name)}`)}
      style={{
        aspectRatio: "4/3",
        padding: 14,
        cursor: "pointer",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
        position: "relative",
        font: "inherit",
        color: "inherit",
        textAlign: "left",
        width: "100%",
      }}
    >
      <Hand size={16} style={{ alignSelf: "flex-start" }}>{name}</Hand>
      <Mono size={11} style={{ color: "var(--ink-3)", alignSelf: "flex-end" }}>
        {formatModified(modifiedAt)}
      </Mono>
    </button>
  );
}
