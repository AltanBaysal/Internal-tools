import { formatModified } from "../../shared/date.js";
import { navigate, projectPath } from "../../shared/router.js";
import { Btn, Hand, Icon, Mono } from "../../vendor/kit.jsx";

// The card opens the project screen; a real <button> so the keyboard can open it too, with the
// wf-card look kept by resetting the button's own chrome. The trash is a sibling rather than a
// child: a button inside a button is invalid HTML, and keeping them apart is also what stops a
// click meant for deleting from opening the project.
export default function ProjectCard({ name, modifiedAt, onDelete }) {
  return (
    <div style={{ position: "relative" }}>
      <button
        type="button"
        className="wf-card"
        onClick={() => navigate(projectPath(name))}
        style={{
          aspectRatio: "4/3",
          padding: 14,
          cursor: "pointer",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          boxSizing: "border-box",
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
      <Btn sm ghost aria-label="Projeyi sil" onClick={onDelete}
           style={{ position: "absolute", top: 10, right: 10, color: "var(--danger)",
                    padding: "4px 8px" }}>
        <Icon.Trash />
      </Btn>
    </div>
  );
}
