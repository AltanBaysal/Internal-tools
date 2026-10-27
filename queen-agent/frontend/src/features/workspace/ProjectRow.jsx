import { useRef, useState } from "react";

import { relativeTime } from "../../shared/time.js";
import Menu from "./Menu.jsx";
import { countOf } from "./countOf.js";

// One All projects row (the design's items 135, 161, 167): the button that opens the project, and
// the ⋯ that holds everything done to it -- done from here and never from inside the project.
// Whether the menu is open is App's, whose one listener owns Escape; whether the name is being
// edited is the row's own, since nothing else closes it.
//
// An archived row (the design's 190, 191, 218) opens its project as any row does: the only
// difference is the list it stands in (Madde 443), and its ⋯, which holds the way back.
//
// The box at its start picks the project for the bar's actions on several at once (Madde 506).
// What is picked is All projects' to hold; the row only says how it was pressed.

// The name corrected in the row's own place rather than in the browser's box (the design's 170).
// The draft is the field's, as a message edit's is (EditMessage): only the finished name leaves.
// The field stays until the server has answered, and a refusal leaves the name where it was typed,
// ready to send again -- as the naming screen keeps the name it could not create (Madde 387).
function RenameField({ name, onSave, onClose }) {
  const [draft, setDraft] = useState(name);
  // Enter's field can take its focus with it, and a second press can come before the answer --
  // neither may send the same name a second time.
  const done = useRef(false);
  const finish = async (save) => {
    if (done.current) return;
    done.current = true;
    const typed = draft.trim();
    // An empty name, or one given up on, asks the server nothing.
    if (!save || !typed) {
      onClose();
      return;
    }
    if (await onSave(typed)) onClose();
    else done.current = false;
  };
  return (
    <input
      type="text"
      className="all-projects__rename"
      aria-label="Project name"
      value={draft}
      autoFocus
      onChange={(event) => setDraft(event.target.value)}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          finish(true);
        }
        if (event.key === "Escape") finish(false);
      }}
      // Pressing anywhere else keeps what was typed: a rename is never silently dropped.
      onBlur={() => finish(true)}
    />
  );
}

// A press with Ctrl (Cmd on a Mac) or Shift picks rather than opens (Madde 506), as a file list does
// in Windows: Ctrl one row, Shift a range in place of the picks, Ctrl+Shift a range added to them. A
// plain press on the row opens, as it always has.
function pickedBy(event) {
  const ctrl = event.ctrlKey || event.metaKey;
  if (event.shiftKey) return ctrl ? "add-range" : "range";
  return ctrl ? "one" : null;
}

// Shift on a press would otherwise stretch the page's text selection to it.
function keepTextSelection(event) {
  if (event.shiftKey) event.preventDefault();
}

export default function ProjectRow({
  project,
  menuOpen,
  picked,
  picking,
  onPick,
  onOpen,
  onOpenMenu,
  onCloseMenu,
  onRename,
  onPin,
  onArchive,
  onDelete,
}) {
  const more = useRef(null);
  const [renaming, setRenaming] = useState(false);

  const rename = { label: "Rename", onChoose: () => setRenaming(true) };
  const remove = {
    label: "Delete",
    danger: true,
    divided: true,
    onChoose: () => onDelete?.(project.id),
  };
  const items = project.archived
    ? [rename, { label: "Unarchive", onChoose: () => onArchive?.(project.id, false) }, remove]
    : [
        rename,
        project.pinned
          ? { label: "Unpin", onChoose: () => onPin?.(project.id, false) }
          : { label: "Pin", onChoose: () => onPin?.(project.id, true) },
        { label: "Archive", onChoose: () => onArchive?.(project.id, true) },
        remove,
      ];

  // While any row is picked every box stands; until then each waits for its row, as the ⋯ does.
  const state = `${picking ? " is-picking" : ""}${picked ? " is-picked" : ""}`;
  return (
    <div className={`all-projects__row${state}`}>
      <input
        type="checkbox"
        className="all-projects__row-pick"
        aria-label={`Select ${project.name}`}
        checked={Boolean(picked)}
        onMouseDown={keepTextSelection}
        // The box's own change is a click, and carries the click's keys; alone it picks one row.
        onChange={(event) => onPick?.(project.id, pickedBy(event.nativeEvent) ?? "one")}
      />
      {renaming ? (
        <RenameField
          name={project.name}
          onSave={(name) => onRename?.(project.id, name)}
          onClose={() => setRenaming(false)}
        />
      ) : (
        <button
          type="button"
          className="all-projects__row-open"
          title={project.name}
          onMouseDown={keepTextSelection}
          onClick={(event) => {
            const how = pickedBy(event);
            if (how) onPick?.(project.id, how);
            else onOpen?.(project.id);
          }}
        >
          <span className="all-projects__row-name">{project.name}</span>
          <span className="all-projects__row-meta">
            {`${countOf(project.chats ?? 0, "chat")} · ${countOf(project.files ?? 0, "file")}`}
          </span>
          <span className="all-projects__row-when">{relativeTime(project.lastActivity)}</span>
        </button>
      )}
      <button
        ref={more}
        type="button"
        className="all-projects__row-more"
        aria-label={`Actions for ${project.name}`}
        // Whose ⋯ this is: All projects finds by it the one that takes the keyboard once a row
        // has left (the design's 217).
        data-project={project.id}
        onClick={() => onOpenMenu?.(project.id)}
      >
        ⋯
      </button>
      {menuOpen ? (
        <Menu anchor={more.current} onClose={onCloseMenu} items={items} />
      ) : null}
    </div>
  );
}
