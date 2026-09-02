import { relativeTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";
import FilePanel from "./FilePanel.jsx";
import FileRow from "./FileRow.jsx";
import ModelPicker from "./ModelPicker.jsx";
import ModePicker from "./ModePicker.jsx";
import Skeleton from "./Skeleton.jsx";
import SkillPicker from "./SkillPicker.jsx";

export default function ProjectScreen({
  project,
  chats = [],
  files = [],
  loadingChats,
  loadingFiles,
  chatsError,
  filesError,
  reading,
  deleting,
  skill,
  skillsOpen,
  onToggleSkills,
  onSkillChange,
  model,
  modelOpen,
  onToggleModel,
  onModelChange,
  mode,
  modeOpen,
  onToggleMode,
  onModeChange,
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
    <div className={reading?.name ? "screen-layout screen-layout--reading" : "screen-layout"}>
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
            /* The same order as the chat screen. This is where the first sentence of a chat is
               written, so it is where the choices governing it have to be reachable -- and no chat
               exists yet, so both belong to the session rather than to a record. */
            foot={
              <>
                <ModePicker
                  mode={mode}
                  open={modeOpen}
                  onToggle={onToggleMode}
                  onChange={onModeChange}
                />
                <SkillPicker
                  skill={skill}
                  open={skillsOpen}
                  onToggle={onToggleSkills}
                  onChange={onSkillChange}
                />
                <ModelPicker
                  model={model}
                  open={modelOpen}
                  onToggle={onToggleModel}
                  onChange={onModelChange}
                />
              </>
            }
            onSubmit={onSend}
          />

          {/* Reading drops the grid to one column, because the column it would have held is the one
              the panel is already showing: the same list twice is not two things. */}
          <div className={reading?.name ? "project-grid project-grid--reading" : "project-grid"}>
            <div>
              {/* No empty-state line here on purpose: the composer sits right above and already
                  says what to do. The file column gets one because the user cannot fill it
                  themselves. */}
              <h2 className="column__title">Chats</h2>
              <div className="chat-list">
                {loadingChats ? <Skeleton rows={3} /> : null}
                {/* This column used to empty in silence, which was the quieter of the two lies. */}
                {chatsError ? <p className="list-error">{chatsError}</p> : null}
                {/* A box holding buttons, like the file row and the sidebar's: a clickable box has
                    no tab stop and no Enter, and the × cannot sit inside a button. */}
                {chats.map((chat) => (
                  <div key={chat.id} className="chat-row" title={chat.title}>
                    <button
                      type="button"
                      className="chat-row__open"
                      onClick={() => onOpenChat(chat.id)}
                    >
                      <span className="chat-row__title">{chat.title}</span>
                      <span className="chat-row__when">{relativeTime(chat.lastActivity)}</span>
                    </button>
                    {onDeleteChat ? (
                      <button
                        type="button"
                        className="row-x"
                        title={`Delete ${chat.title}`}
                        aria-label={`Delete ${chat.title}`}
                        onClick={() => onDeleteChat(chat.id)}
                      >
                        ×
                      </button>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
            {/* Gone while the panel is open, and the row's × goes with it: there is no row left to
                delete. The chat rail keeps its list in the same situation for the opposite reason --
                there the reader is the rail widened, so the list is its neighbour, not its copy. */}
            {reading?.name ? null : (
              <div>
                <h2 className="column__title">Files QueenAgent created</h2>
                {/* No offer to bring anything back, but a refusal is still worth a line. */}
                {deleting?.error ? <p className="list-error">{deleting.error}</p> : null}
                <div className="file-list">
                  {/* The teaching line waits for the answer: until the list has arrived, "no files
                      yet" is a guess and not a fact -- and if no answer came, not even that. */}
                  {loadingFiles ? <Skeleton rows={3} /> : null}
                  {filesError ? <p className="list-error">{filesError}</p> : null}
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
                  {!loadingFiles && !filesError && !files.length ? (
                    <p className="file-list__empty">
                      No files yet — start a chat and QueenAgent will create one.
                    </p>
                  ) : null}
                </div>
              </div>
            )}
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
