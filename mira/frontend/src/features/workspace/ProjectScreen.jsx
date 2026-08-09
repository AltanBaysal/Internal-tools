import ComposerShell from "./ComposerShell.jsx";

export default function ProjectScreen({ project, onBack, onRename, onDescribe }) {
  if (!project) {
    // The address bar is something a person can type into, so a wrong id has to be survivable.
    return (
      <div className="screen">
        <div className="screen__column">
          <button type="button" className="back" onClick={onBack}>
            ← back
          </button>
          <p className="screen__missing">That project does not exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="screen">
      <div className="screen__column">
        <button type="button" className="back" onClick={onBack}>
          ← back
        </button>

        <div className="screen__title-row">
          <h1 className="screen__title">{project.name}</h1>
          <button type="button" className="ghost" onClick={onRename}>
            Rename
          </button>
        </div>

        {/* Every new project is born saying "Click to add a description.", so clicking has to do
            something -- otherwise the app instructs the user and then ignores them. */}
        <p className="screen__desc" onClick={onDescribe}>
          {project.desc}
        </p>

        <ComposerShell
          rows={2}
          placeholder="Start a new chat in this project..."
          note="the answer is saved as a file"
          action="Start"
        />

        <div className="project-grid">
          <div>
            {/* No empty-state line here on purpose: the composer sits right above and already says
                what to do. The file column gets one because the user cannot fill it themselves. */}
            <h2 className="column__title">Chats</h2>
          </div>
          <div>
            <h2 className="column__title">Files Mira created</h2>
            <div className="file-list">
              <p className="file-list__empty">
                No files yet — start a chat and Mira will create one.
              </p>
            </div>
            <p className="file-list__note">Chats create the files; you just open and read them.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
