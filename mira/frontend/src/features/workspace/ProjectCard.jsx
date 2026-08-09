import ProjectDot from "./ProjectDot.jsx";

function counted(value, singular) {
  return `${value} ${value === 1 ? singular : `${singular}s`}`;
}

export default function ProjectCard({ project, onOpen }) {
  return (
    <button type="button" className="card" onClick={onOpen}>
      <ProjectDot hue={project.hue} />
      <span className="card__name">{project.name}</span>
      <span className="card__desc">{project.desc}</span>
      <span className="card__meta">
        {counted(project.chats, "chat")} · {counted(project.files, "file")}
      </span>
    </button>
  );
}
