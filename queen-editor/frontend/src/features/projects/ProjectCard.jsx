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
// `busy` is the word to show while something is being done to this project, or null. The screen
// supplies it rather than the card: the screen is what knows which move is being made (madde 225).
export default function ProjectCard({ name, modifiedAt, onDelete, onRename, onArchive, onRestore,
                                      archived = false, busy = null }) {
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
        {/* In the date's place rather than under it: a third line would grow the card, and the date
            is the thing this work is about to change anyway. */}
        <Mono size={11} style={{ color: "var(--ink-3)", alignSelf: "flex-end" }}>
          {busy || formatModified(modifiedAt)}
        </Mono>
      </button>
      {/* Two icon buttons, 4px apart (Fark 5). The bin wears the destructive standard and the
          pencil wears ghost -- a transparent line rather than no line, so the two keep the same box
          and sit level; border:none took a pixel off every side and shifted them against each
          other. The pencil stays bare on purpose (karar 43): a red frame is a mark, and it only
          marks while what sits beside it has none. Renaming takes nothing away (Fark 3). Neither
          carries a word -- the one the standard asks for is on the delete confirm, where there is
          room for it (madde 9). */}
      {/* An archived card is an ordinary card (madde 227): archiving says which list the project is
          drawn in and takes nothing away, so nothing it could do before is missing here. Only the
          middle button changes hands -- putting away becomes taking back. */}
      {/* All three are closed while something is running, not just the one that was pressed: they
          all reach the same folder and the same mark, and none of them may slip in between. */}
      <div style={{ position: "absolute", top: 10, right: 10, display: "flex", gap: 4 }}>
        <Btn sm icon ghost disabled={!!busy} aria-label="Projeyi yeniden adlandır" onClick={onRename}>
          <Icon.Pencil />
        </Btn>
        {/* Ghost like the pencil: neither of these takes anything away, and the red frame only
            marks the bin while it is the only one wearing it. */}
        {archived ? (
          <Btn sm icon ghost disabled={!!busy} aria-label="Projeyi geri al" onClick={onRestore}>
            <Icon.Undo />
          </Btn>
        ) : (
          <Btn sm icon ghost disabled={!!busy} aria-label="Projeyi arşivle" onClick={onArchive}>
            <Icon.Archive />
          </Btn>
        )}
        <Btn sm icon disabled={!!busy} aria-label="Projeyi sil" onClick={onDelete} style={DANGER}>
          <Icon.Trash />
        </Btn>
      </div>
    </div>
  );
}
