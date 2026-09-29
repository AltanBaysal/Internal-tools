import { useRef, useState } from "react";

import { relativeTime } from "../../shared/time.js";
import Menu from "./Menu.jsx";
import { countOf } from "./countOf.js";

// One All projects row (the design's items 135, 161, 167): the button that opens the project, and
// the ⋯ that holds everything done to it -- done from here and never from inside the project.
// Whether the menu is open is App's, whose one listener owns Escape; whether the name is being
// edited is the row's own, since nothing else closes it.

// The name corrected in the row's own place rather than in the browser's box (the design's 170).
// The draft is the field's, as a message edit's is (EditMessage): only the finished name leaves.
function RenameField({ name, onDone }) {
  const [draft, setDraft] = useState(name);
  // Enter closes the field, and a field that goes can take its focus with it -- a blur that must
  // not save the same name a second time.
  const done = useRef(false);
  const finish = (save) => {
    if (done.current) return;
    done.current = true;
    onDone(save ? draft.trim() : "");
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

export default function ProjectRow({
  project,
  menuOpen,
  onOpen,
  onOpenMenu,
  onCloseMenu,
  onRename,
  onPin,
  onDelete,
}) {
  const more = useRef(null);
  const [renaming, setRenaming] = useState(false);

  return (
    <div className="all-projects__row">
      {renaming ? (
        <RenameField
          name={project.name}
          onDone={(name) => {
            setRenaming(false);
            // An empty name, or one given up on, asks the server nothing.
            if (name) onRename?.(project.id, name);
          }}
        />
      ) : (
        <button
          type="button"
          className="all-projects__row-open"
          title={project.name}
          onClick={() => onOpen?.(project.id)}
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
        onClick={() => onOpenMenu?.(project.id)}
      >
        ⋯
      </button>
      {menuOpen ? (
        <Menu
          anchor={more.current}
          onClose={onCloseMenu}
          items={[
            { label: "Rename", onChoose: () => setRenaming(true) },
            project.pinned
              ? { label: "Unpin", onChoose: () => onPin?.(project.id, false) }
              : { label: "Pin", onChoose: () => onPin?.(project.id, true) },
            {
              label: "Delete",
              danger: true,
              divided: true,
              onChoose: () => onDelete?.(project.id),
            },
          ]}
        />
      ) : null}
    </div>
  );
}
