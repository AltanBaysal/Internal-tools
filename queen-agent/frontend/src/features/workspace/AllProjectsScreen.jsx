import { useState } from "react";

import { relativeTime } from "../../shared/time.js";
import { countOf } from "./countOf.js";

// The screen the app opens on (the design's items 135, 142, 167), and the one Exit project comes
// back to. No sidebar stands beside it: no project is open here. The order is the server's
// (list_projects.py) -- pinned first, then the most recently used -- and this screen only splits it
// where the pins end.
//
// The search is this screen's own state: what is shown while typing is the UI's (FOUNDATION,
// Decision 4), so it reaches neither the server nor the address.
//
// The row's ⋯ and the Archived tab are items of their own (360, 363), and so are the spinner and
// the sentence a failed list gets (364).

// Case and accents do not count, as in the design's data.js: "cafe" finds "Café".
const fold = (text) => text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

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

function ProjectList({ projects, query, onOpenProject }) {
  // Asked first: with nothing to search, "no match" would be the wrong news.
  if (!projects.length) return <p className="all-projects__empty">No projects yet.</p>;
  const asked = query.trim();
  const found = projects.filter((project) => fold(project.name).includes(fold(asked)));
  if (!found.length) return <p className="all-projects__empty">{`No projects match "${asked}".`}</p>;
  return (
    <>
      <Section
        label="Pinned"
        projects={found.filter((project) => project.pinned)}
        onOpenProject={onOpenProject}
      />
      <Section
        label="Recent"
        projects={found.filter((project) => !project.pinned)}
        onOpenProject={onOpenProject}
      />
    </>
  );
}

export default function AllProjectsScreen({
  projects = [],
  loading,
  error,
  onNewProject,
  onOpenProject,
}) {
  const [query, setQuery] = useState("");

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
        <div className="all-projects__tools">
          {/* Focused as the screen opens (the design's 142), even while the list is on its way:
              handing it over again once the list comes could pull it from where the user went. */}
          <input
            type="text"
            className="all-projects__search"
            placeholder="Search projects"
            aria-label="Search projects"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            autoFocus
          />
        </div>
        {/* Until the list has come, "no projects yet" is a guess and not a fact. */}
        {loading ? null : (
          <ProjectList projects={projects} query={query} onOpenProject={onOpenProject} />
        )}
      </div>
    </div>
  );
}
