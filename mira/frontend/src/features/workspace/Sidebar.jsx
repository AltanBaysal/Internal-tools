import ProjectDot from "./ProjectDot.jsx";

export default function Sidebar({
  projects,
  activeProjectId,
  onNewChat,
  onNewProject,
  onOpenProject,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__mark" />
        <span className="sidebar__wordmark">Mira</span>
      </div>

      {/* Opens nothing yet -- the search panel is Madde 28. */}
      <button type="button" className="sidebar__search">
        <span className="sidebar__search-label">Search</span>
        <span className="sidebar__shortcut">⌘K</span>
      </button>

      <button type="button" className="sidebar__new-chat" onClick={onNewChat}>
        <span className="sidebar__plus">+</span>
        New chat
      </button>

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
      </div>
    </aside>
  );
}
