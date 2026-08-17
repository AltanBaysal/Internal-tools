// A chat lives inside a project, so the two chat sections follow the selected one: with none
// selected they are absent rather than empty or disabled.
const MOST_CHATS = 8;

export default function Sidebar({
  projects,
  chats = [],
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
        {projects.map((project) => (
          <button
            key={project.id}
            type="button"
            className={
              project.id === activeProjectId ? "sidebar__row sidebar__row--active" : "sidebar__row"
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
