import { useRef } from "react";

import Menu from "./Menu.jsx";

// A chat lives inside a project, so the two chat sections follow the selected one: with none
// selected they are absent rather than empty or disabled.
const MOST_CHATS = 8;

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
  onOpenSettings,
}) {
  // Only one menu is ever open, so one ref holds whichever ⋯ opened it.
  const trigger = useRef(null);

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__wordmark">QueenAgent</span>
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

      {/* At the foot, under everything: it belongs to the app rather than to any project in it, and
          it is the one row that is there whether a project is selected or not. */}
      <div className="sidebar__foot">
        <button type="button" className="sidebar__settings" onClick={onOpenSettings}>
          Settings
        </button>
      </div>
    </aside>
  );
}
