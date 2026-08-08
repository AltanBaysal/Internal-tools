import { projectContents } from "./projects.js";

// Reached only from the project header. Switching projects is rare next to picking a chat, so this
// list borrows the column instead of standing next to the one used all day.
export default function ProjectList({ projects, files, chats, activeId, on }) {
  return (
    <div className="list">
      <div className="group">projeler</div>
      {projects.map((project) => (
        <div key={project.id} className={project.id === activeId ? "row active" : "row"}>
          <button className="row-open" onClick={() => on.openProject(project.id)}>
            {project.name}
          </button>
          <button
            className="row-delete"
            aria-label={`${project.name} projesini sil`}
            onClick={() => on.deleteProject(project.id, projectContents(project.id, files, chats))}
          >
            ×
          </button>
        </div>
      ))}
      <button className="add" onClick={on.newProject}>
        + Yeni proje
      </button>
    </div>
  );
}
