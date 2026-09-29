// A chat lives inside a project, so the two chat sections follow the selected one: with none
// selected they are absent rather than empty or disabled.
const MOST_CHATS = 8;

// One button, never a drag: claude.ai's behaviour rather than the rail's, and the user asked for it
// by that name. It stands in the sidebar's own last row, open and folded alike, so a press never
// moves out from under the pointer (design 187, Claude Code's place for it). Folded, the sidebar is
// not hidden: an icon column stands where it was, + for New chat above and this fold at its foot
// (design 174); the rows are names and titles, and have no icon forms to fold into.
function Fold({ collapsed, onToggle }) {
  return (
    <div className="sidebar__foot">
      <button
        type="button"
        className="sidebar__fold"
        aria-label={collapsed ? "Show the sidebar" : "Hide the sidebar"}
        onClick={onToggle}
      >
        {/* Drawn in CSS, as .dot is: the app carries no icon files. */}
        <span className="sidebar__panel-icon" />
      </button>
    </div>
  );
}

export default function Sidebar({
  projects,
  chats = [],
  activeProjectId,
  activeChatId,
  onNewChat,
  onNewProject,
  onOpenProject,
  onOpenChat,
  collapsed,
  onToggle,
}) {
  if (collapsed) {
    return (
      <aside className="sidebar sidebar--collapsed">
        {activeProjectId ? (
          <button
            type="button"
            className="sidebar__new-chat sidebar__new-chat--icon"
            aria-label="New chat"
            onClick={onNewChat}
          >
            <span className="sidebar__plus">+</span>
          </button>
        ) : null}
        <Fold collapsed onToggle={onToggle} />
      </aside>
    );
  }

  return (
    <aside className="sidebar">
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
        {/* A row only opens its project: what is done to a project is done from its All projects
            row, never from inside it (Madde 360, the design's 161). */}
        {projects.map((project) => (
          <button
            key={project.id}
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
                project.files ? "sidebar__row-badge" : "sidebar__row-badge sidebar__row-badge--none"
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

      <Fold onToggle={onToggle} />
    </aside>
  );
}
