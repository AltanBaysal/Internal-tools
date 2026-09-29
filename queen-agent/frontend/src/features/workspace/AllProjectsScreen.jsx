import { relativeTime } from "../../shared/time.js";
import { countOf } from "./countOf.js";

// The screen the app opens on (the design's items 135, 142, 167), and the one Exit project comes
// back to. No sidebar stands beside it: no project is open here. The order is the server's
// (list_projects.py) -- pinned first, then the most recently used -- and this screen only splits it
// where the pins end.
//
// The search, the row's ⋯ and the Archived tab are items of their own (359, 360, 363), and so are
// the spinner and the sentence a failed list gets (364).

function Section({ label, projects, onOpenProject }) {
  // A heading over nothing would be a promise of rows that are not there.
  if (!projects.length) return null;
  return (
    <div className="all-projects__section">
      {/* Written as the design writes it; the stylesheet sets it in capitals. */}
      <div className="all-projects__label">{label}</div>
      <div className="all-projects__list">
        {projects.map((project) => (
          <div key={project.id} className="all-projects__row">
            <button
              type="button"
              className="all-projects__row-open"
              title={project.name}
              onClick={() => onOpenProject?.(project.id)}
            >
              <span className="all-projects__row-name">{project.name}</span>
              <span className="all-projects__row-meta">
                {`${countOf(project.chats ?? 0, "chat")} · ${countOf(project.files ?? 0, "file")}`}
              </span>
              <span className="all-projects__row-when">{relativeTime(project.lastActivity)}</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AllProjectsScreen({
  projects = [],
  loading,
  error,
  onNewProject,
  onOpenProject,
}) {
  if (error) {
    // A failed list means the count is unknown, not zero: offering the list's frame over it would be
    // telling the user something the server never said.
    return (
      <div className="empty">
        <p className="empty__error">{error}</p>
      </div>
    );
  }

  return (
    <div className="screen">
      <div className="screen__column">
        <div className="all-projects__head">
          <h1 className="screen__title">All projects</h1>
          <button type="button" className="empty__action" onClick={onNewProject}>
            + New project
          </button>
        </div>
        {/* Until the list has come, "no projects yet" is a guess and not a fact. */}
        {loading ? null : projects.length ? (
          <>
            <Section
              label="Pinned"
              projects={projects.filter((project) => project.pinned)}
              onOpenProject={onOpenProject}
            />
            <Section
              label="Recent"
              projects={projects.filter((project) => !project.pinned)}
              onOpenProject={onOpenProject}
            />
          </>
        ) : (
          <p className="all-projects__empty">No projects yet.</p>
        )}
      </div>
    </div>
  );
}
