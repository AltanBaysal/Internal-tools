import { relativeTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";
import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";
import FileStrip from "./FileStrip.jsx";
import Skeleton from "./Skeleton.jsx";

export default function ProjectScreen({
  project,
  chats = [],
  files = [],
  loadingChats,
  loadingFiles,
  reading,
  deleting,
  onRename,
  onDelete,
  onSend,
  onOpenChat,
  onDeleteChat,
}) {
  if (!project) {
    // The address bar is something a person can type into, so a wrong id has to be survivable.
    return (
      <div className="screen">
        <div className="screen__column">
          <p className="screen__missing">That project does not exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="screen-layout">
      <div className="screen">
        <div className="screen__column">
          <div className="screen__title-row">
            <h1 className="screen__title">{project.name}</h1>
            <button type="button" className="ghost" onClick={onRename}>
              Rename
            </button>
            {/* One of the two doors onto the same question. It opens it and nothing more. */}
            <button type="button" className="screen__delete" title="Delete project" onClick={onDelete}>
              Delete
            </button>
          </div>

          <Composer
            rows={2}
            placeholder="Start a new chat in this project..."
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
                {loadingChats ? <Skeleton rows={3} /> : null}
                {chats.map((chat) => (
                  <div
                    key={chat.id}
                    className="chat-row"
                    onClick={() => onOpenChat(chat.id)}
                    title={chat.title}
                  >
                    <span className="chat-row__title">{chat.title}</span>
                    <span className="chat-row__when">{relativeTime(chat.lastActivity)}</span>
                    {onDeleteChat ? (
                      <button
                        type="button"
                        className="row-x"
                        aria-label={`Delete ${chat.title}`}
                        onClick={(event) => {
                          event.stopPropagation();
                          onDeleteChat(chat.id);
                        }}
                      >
                        ×
                      </button>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h2 className="column__title">Files QueenAgent created</h2>
              <FileStrip
                deleted={deleting?.deleted}
                error={deleting?.error}
                onUndo={deleting?.undo}
              />
              <div className="file-list">
                {/* The teaching line waits for the answer: until the list has arrived, "no files
                    yet" is a guess and not a fact. */}
                {loadingFiles ? <Skeleton rows={3} /> : null}
                {!loadingFiles && files.length
                  ? files.map((file) => (
                      <FileRow
                        key={file.name}
                        file={file}
                        onOpen={reading?.open}
                        onDelete={deleting?.remove}
                      />
                    ))
                  : null}
                {!loadingFiles && !files.length ? (
                  <p className="file-list__empty">
                    No files yet — start a chat and QueenAgent will create one.
                  </p>
                ) : null}
              </div>
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
