import ProjectDot from "./ProjectDot.jsx";

export default function Sidebar({
  projects,
  recentChats = [],
  activeProjectId,
  activeChatId,
  onNewChat,
  onNewProject,
  onOpenProject,
  onOpenChat,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__mark" />
        <span className="sidebar__wordmark">QueenAgent</span>
      </div>

      {/* Hidden, not disabled: a chat needs a project to live in, and a control that cannot act is
          worse than no control at all. */}
      {projects.length > 0 ? (
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
        {projects.map((project) => (
          <button
            key={project.id}
            type="button"
            className={
              project.id === activeProjectId ? "sidebar__row sidebar__row--active" : "sidebar__row"
            }
            onClick={() => onOpenProject(project.id)}
          >
            <ProjectDot hue={project.hue} />
            <span className="sidebar__row-name">{project.name}</span>
            <span className="sidebar__row-badge">{project.files || ""}</span>
          </button>
        ))}
      </div>

      <div className="sidebar__chats">
        <span className="sidebar__label">Recent chats</span>
        {recentChats.map((chat) => (
          <button
            key={chat.id}
            type="button"
            className={
              chat.id === activeChatId ? "sidebar__chat sidebar__chat--active" : "sidebar__chat"
            }
            onClick={() => onOpenChat(chat.projectId, chat.id)}
            title={chat.title}
          >
            {chat.title}
          </button>
        ))}
      </div>
    </aside>
  );
}
