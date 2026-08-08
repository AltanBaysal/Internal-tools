import { filesOf } from "./files.js";
import { projectContents } from "./projects.js";
import { chatsOf, titleOf } from "./storage.js";

// Only the open project unfolds. Two projects' files on screen at once is exactly the confusion
// this two-level tree exists to prevent.
export default function ProjectTree({ projects, files, chats, active, on }) {
  return (
    <div className="tree">
      {projects.map((project) => {
        const open = project.id === active.projectId;
        return (
          <div key={project.id} className={open ? "project open" : "project"}>
            <div className={open ? "row active" : "row"}>
              <button className="row-open" onClick={() => on.openProject(project.id)}>
                {open ? "▾" : "▸"} {project.name}
              </button>
              <button
                className="row-delete"
                aria-label={`${project.name} projesini sil`}
                onClick={() =>
                  on.deleteProject(project.id, projectContents(project.id, files, chats))
                }
              >
                ×
              </button>
            </div>

            {open && (
              <div className="project-body">
                <div className="group">dosyalar</div>
                {filesOf(files, project.id).map((file) => (
                  <div key={file.id} className={file.id === active.fileId ? "row active" : "row"}>
                    <button className="row-open" onClick={() => on.openFile(file.id)}>
                      {file.name}
                    </button>
                    <button
                      className="row-delete"
                      aria-label={`${file.name} dosyasını sil`}
                      onClick={() => on.deleteFile(file.id)}
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button className="add" onClick={on.newFile}>
                  + Yeni dosya
                </button>

                <div className="group">sohbetler</div>
                {chatsOf(chats, project.id).map((chat) => {
                  const title = titleOf(chat.messages);
                  return (
                    <div key={chat.id} className={chat.id === active.chatId ? "row active" : "row"}>
                      <button className="row-open" onClick={() => on.openChat(chat.id)}>
                        {title}
                      </button>
                      <button
                        className="row-delete"
                        aria-label={`${title} sohbetini sil`}
                        onClick={() => on.deleteChat(chat.id)}
                      >
                        ×
                      </button>
                    </div>
                  );
                })}
                <button className="add" onClick={on.newChat}>
                  + Yeni sohbet
                </button>
              </div>
            )}
          </div>
        );
      })}

      <button className="add new-project" onClick={on.newProject}>
        + Yeni proje
      </button>
    </div>
  );
}
