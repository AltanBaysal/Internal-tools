import { relativeTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";
import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";

export default function ProjectScreen({
  project,
  chats = [],
  files = [],
  reading,
  onBack,
  onRename,
  onDescribe,
  onSend,
  onOpenChat,
}) {
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
    <div className="screen-layout">
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

          <Composer
            rows={2}
            placeholder="Start a new chat in this project..."
            note="the answer is saved as a file"
            action="Start"
            onSubmit={onSend}
          />

          {/* Reading drops the grid to one column: the panel takes the width the files column had,
              and the chats it pushes down are still all there. */}
          <div className={reading?.name ? "project-grid project-grid--reading" : "project-grid"}>
            <div>
              {/* No empty-state line here on purpose: the composer sits right above and already
                  says what to do. The file column gets one because the user cannot fill it
                  themselves. */}
              <h2 className="column__title">Chats</h2>
              <div className="chat-list">
                {chats.map((chat) => (
                  <div
                    key={chat.id}
                    className="chat-row"
                    onClick={() => onOpenChat(chat.id)}
                    title={chat.title}
                  >
                    <span className="chat-row__title">{chat.title}</span>
                    <span className="chat-row__when">{relativeTime(chat.lastActivity)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h2 className="column__title">Files Mira created</h2>
              <div className="file-list">
                {files.length ? (
                  files.map((file) => (
                    <FileRow key={file.name} file={file} onOpen={reading?.open} />
                  ))
                ) : (
                  <p className="file-list__empty">
                    No files yet — start a chat and Mira will create one.
                  </p>
                )}
              </div>
              <p className="file-list__note">
                Chats create the files; you just open and read them.
              </p>
            </div>
          </div>
        </div>
      </div>

      {reading?.name ? (
        <aside className="panel">
          <FilePanel
            name={reading.name}
            file={reading.file}
            missing={reading.missing}
            error={reading.error}
            onClose={reading.close}
            onDownload={reading.download}
          />
        </aside>
      ) : null}
    </div>
  );
}
