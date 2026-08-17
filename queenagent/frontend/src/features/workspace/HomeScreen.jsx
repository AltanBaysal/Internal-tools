import Composer from "./Composer.jsx";
import ProjectCard from "./ProjectCard.jsx";
import Skeleton from "./Skeleton.jsx";

// The design's three prompts. They only fill the draft; they never send.
const SUGGESTIONS = [
  "Summarize this week's notes",
  "Draft a meeting agenda",
  "Turn my sources into a table",
];

export default function HomeScreen({
  projects,
  error,
  loading,
  onNewProject,
  onOpenProject,
  onSend,
}) {
  return (
    <div className="home">
      <div className="home__column">
        <h1 className="home__greeting">Hi</h1>

        {/* No mono target label here: what a message from home is aimed at is decided in Madde 11,
            and naming a target before that decision would be answering it from the wrong place. */}
        <Composer
          rows={3}
          placeholder="Ask anything — QueenAgent saves the answer to your project as a file."
          action="Send"
          suggestions={SUGGESTIONS}
          onSubmit={onSend}
        />

        <div className="home__head">
          <h2 className="home__section">Projects</h2>
          <button type="button" className="ghost" onClick={onNewProject}>
            New project
          </button>
        </div>

        {error ? <p className="home__error">{error}</p> : null}

        <div className="home__grid">
          {loading ? (
            <Skeleton rows={4} variant="card" />
          ) : (
            projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onOpen={() => onOpenProject(project.id)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
