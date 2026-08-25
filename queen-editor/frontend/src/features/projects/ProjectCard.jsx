import { formatModified } from "../../shared/date.js";
import { navigate, projectPath } from "../../shared/router.js";
import { Btn, Hand, Icon, Mono } from "../../vendor/kit.jsx";

// Red text, red border, no fill -- the app-wide destructive standard. The design's own texts
// disagreed here: the rules document counts project delete among its examples, the card drawing
// shows a bare icon. The difference list's first decision settled it for the rules document.
const DANGER = { color: "var(--danger)", borderColor: "var(--danger)", background: "none" };

// The card opens the project screen; a real <button> so the keyboard can open it too, with the
// wf-card look kept by resetting the button's own chrome. The trash is a sibling rather than a
// child: a button inside a button is invalid HTML, and keeping them apart is also what stops a
// click meant for deleting from opening the project.
export default function ProjectCard({ name, modifiedAt, onDelete, onRename }) {
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
      {/* Two icon buttons, 4px apart (Fark 5). The bin wears the destructive standard and the
          pencil wears ghost -- a transparent line rather than no line, so the two keep the same box
          and sit level; border:none took a pixel off every side and shifted them against each
          other. The pencil stays bare on purpose (karar 43): a red frame is a mark, and it only
          marks while what sits beside it has none. Renaming takes nothing away (Fark 3). Neither
          carries a word -- the one the standard asks for is on the delete confirm, where there is
          room for it (madde 9). */}
      <div style={{ position: "absolute", top: 10, right: 10, display: "flex", gap: 4 }}>
        <Btn sm icon ghost aria-label="Projeyi yeniden adlandır" onClick={onRename}>
          <Icon.Pencil />
        </Btn>
        <Btn sm icon aria-label="Projeyi sil" onClick={onDelete} style={DANGER}>
          <Icon.Trash />
        </Btn>
      </div>
    </div>
  );
}
