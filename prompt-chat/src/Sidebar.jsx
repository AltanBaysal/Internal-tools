import { useState } from "react";
import ProjectList from "./ProjectList.jsx";
import ChatList from "./ChatList.jsx";
import { errors } from "./skillSource.js";

export default function Sidebar({
  projects,
  files,
  chats,
  active,
  on,
  apiKey,
  onApiKey,
  model,
  onModel,
}) {
  // With no key there is nothing to do but enter one, so the panel opens itself on a first visit
  // and stays out of the way afterwards.
  const [settingsOpen, setSettingsOpen] = useState(() => apiKey === "");
  // Which of the two lists the column is showing. Deliberately not persisted: a reload lands on the
  // open project's chats, which is where the work happens.
  const [browsing, setBrowsing] = useState(false);

  const project = projects.find((p) => p.id === active.projectId);

  return (
    <aside className="sidebar">
      {browsing ? (
        <ProjectList
          projects={projects}
          files={files}
          chats={chats}
          activeId={active.projectId}
          on={{
            // Picking or adding a project is why you came here, so the column goes back to what you
            // actually work in. Deleting does not: another one may follow.
            openProject: (id) => {
              on.openProject(id);
              setBrowsing(false);
            },
            newProject: () => {
              on.newProject();
              setBrowsing(false);
            },
            deleteProject: on.deleteProject,
          }}
        />
      ) : (
        <>
          <button className="project-header" onClick={() => setBrowsing(true)}>
            ‹ {project?.name ?? ""}
          </button>
          <ChatList chats={chats} projectId={active.projectId} activeId={active.chatId} on={on} />
        </>
      )}

      <div className="settings">
        {settingsOpen && (
          <div className="settings-body">
            <input
              type="password"
              placeholder="xAI API anahtarı"
              autoComplete="off"
              value={apiKey}
              onChange={(e) => onApiKey(e.target.value)}
            />
            <input
              placeholder="model"
              autoComplete="off"
              value={model}
              onChange={(e) => onModel(e.target.value)}
            />
            {/* A skill that failed to load is invisible everywhere else — it simply is not in the
                list — so the one place a user could go looking is where it says why. */}
            {errors.length > 0 && (
              <ul className="skill-errors">
                {errors.map((e) => (
                  <li key={e.path}>
                    {e.path} — {e.reason}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
        <button className="settings-toggle" onClick={() => setSettingsOpen((v) => !v)}>
          ⚙ Ayarlar
        </button>
      </div>
    </aside>
  );
}
