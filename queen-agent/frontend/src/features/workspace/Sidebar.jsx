import { useRef } from "react";

import Menu from "./Menu.jsx";

// A chat lives inside a project, so the two chat sections follow the selected one: with none
// selected they are absent rather than empty or disabled.
const MOST_CHATS = 8;

// One button, never a drag: claude.ai's behaviour rather than the rail's, and the user asked for it
// by that name. Folded, the sidebar is not hidden -- a strip stands where it was, carrying the one
// thing that brings it back. Nothing else survives the fold: every row here is a name or a title,
// and inventing icons for them is a different decision from this one.
function Fold({ collapsed, onToggle }) {
  return (
    <button
      type="button"
      className="sidebar__fold"
      aria-label={collapsed ? "Show the sidebar" : "Hide the sidebar"}
      onClick={onToggle}
    >
      {collapsed ? "›" : "‹"}
    </button>
  );
}

export default function Sidebar({
  projects,
  chats = [],
  activeProjectId,
  activeChatId,
  menuFor,
  onNewChat,
  onNewProject,
  onOpenProject,
  onOpenChat,
  onOpenMenu,
  onCloseMenu,
  onRenameProject,
  onDeleteProject,
  collapsed,
  onToggle,
}) {
  // Only one menu is ever open, so one ref holds whichever ⋯ opened it.
  const trigger = useRef(null);

  if (collapsed) {
    return (
      <aside className="sidebar sidebar--collapsed">
        <Fold collapsed onToggle={onToggle} />
      </aside>
    );
  }

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__wordmark">QueenAgent</span>
        <Fold onToggle={onToggle} />
      </div>

      {activeProjectId ? (
        <button type="button" className="sidebar__new-chat" onClick={onNewChat}>
          <span className="sidebar__plus">+</span>
          New chat
        </button>
      ) : null}

      <div className="sidebar__projects">
        <div className="sidebar__head">
          <span className="sidebar__label">Projects</span>
          <button
            type="button"
            className="sidebar__add"
            onClick={onNewProject}
            aria-label="New project"
          >
            +
          </button>
        </div>
        {/* The row is a box rather than a button: a menu button cannot live inside another button.
            What it looks like is unchanged; what it is made of is not. */}
        {projects.map((project) => (
          <div key={project.id} className="sidebar__row">
            <button
              type="button"
              className={
                project.id === activeProjectId
                  ? "sidebar__row-open sidebar__row--active"
                  : "sidebar__row-open"
              }
              onClick={() => onOpenProject(project.id)}
            >
              <span className="dot" />
              <span className="sidebar__row-name">{project.name}</span>
              {/* A zero is drawn and made transparent rather than left out: the first file to land
                  must not push the name sideways. */}
              <span
                className={
                  project.files
                    ? "sidebar__row-badge"
                    : "sidebar__row-badge sidebar__row-badge--none"
                }
              >
                {project.files ?? 0}
              </span>
            </button>
            <button
              type="button"
              className="sidebar__row-more"
              aria-label={`More for ${project.name}`}
              onClick={(event) => {
                // Which button the menu hangs off is a matter of where it is drawn, so it stays
                // here rather than travelling up to App with the id.
                trigger.current = event.currentTarget;
                onOpenMenu?.(project.id);
              }}
            >
              ⋯
            </button>
            {menuFor === project.id ? (
              <Menu
                anchor={trigger.current}
                onClose={onCloseMenu}
                items={[
                  { label: "Rename", onChoose: () => onRenameProject?.(project.id) },
                  {
                    label: "Delete project",
                    danger: true,
                    onChoose: () => onDeleteProject?.(project.id),
                  },
                ]}
              />
            ) : null}
          </div>
        ))}
      </div>

      {activeProjectId ? (
        <div className="sidebar__chats">
          <span className="sidebar__label">Recent chats</span>
          {chats.slice(0, MOST_CHATS).map((chat) => (
            <button
              key={chat.id}
              type="button"
              className={
                chat.id === activeChatId ? "sidebar__chat sidebar__chat--active" : "sidebar__chat"
              }
              onClick={() => onOpenChat(chat.id)}
              title={chat.title}
            >
              {chat.title}
            </button>
          ))}
        </div>
      ) : null}

    </aside>
  );
}
