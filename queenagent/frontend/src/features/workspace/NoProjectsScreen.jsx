// The only thing "/" ever draws: with a project to show, the app has already moved into it.
export default function NoProjectsScreen({ error, onNewProject }) {
  if (error) {
    // A failed list means the count is unknown, not zero. Offering to create the first project here
    // would be telling the user something the server never said.
    return (
      <div className="empty">
        <p className="empty__error">{error}</p>
      </div>
    );
  }

  return (
    <div className="empty">
      <h1 className="empty__title">No projects yet</h1>
      <p className="empty__line">
        Chats live inside a project, and the files they create stay there. Create a project to start.
      </p>
      <button type="button" className="empty__action" onClick={onNewProject}>
        + New project
      </button>
    </div>
  );
}
