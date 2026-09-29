import { useState } from "react";

import ProjectRow from "./ProjectRow.jsx";

// The screen the app opens on (the design's items 135, 142, 167), and the one Exit project comes
// back to. No sidebar stands beside it: no project is open here. The order is the server's
// (list_projects.py) -- pinned first, then the most recently used -- and this screen only splits it
// where the pins end.
//
// The search is this screen's own state: what is shown while typing is the UI's (FOUNDATION,
// Decision 4), so it reaches neither the server nor the address.
//
// The Archived tab is an item of its own (363), and so are the spinner and the sentence a failed
// list gets (364).

// Case and accents do not count, as in the design's data.js: "cafe" finds "Café".
const fold = (text) => text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

function Section({ label, projects, row }) {
  // A heading over nothing would be a promise of rows that are not there.
  if (!projects.length) return null;
  return (
    <div className="all-projects__section">
      {/* Written as the design writes it; the stylesheet sets it in capitals. */}
      <div className="all-projects__label">{label}</div>
      <div className="all-projects__list">{projects.map(row)}</div>
    </div>
  );
}

function ProjectList({ projects, query, row }) {
  // Asked first: with nothing to search, "no match" would be the wrong news.
  if (!projects.length) return <p className="all-projects__empty">No projects yet.</p>;
  const asked = query.trim();
  const found = projects.filter((project) => fold(project.name).includes(fold(asked)));
  if (!found.length) return <p className="all-projects__empty">{`No projects match "${asked}".`}</p>;
  return (
    <>
      <Section label="Pinned" projects={found.filter((project) => project.pinned)} row={row} />
      <Section label="Recent" projects={found.filter((project) => !project.pinned)} row={row} />
    </>
  );
}

export default function AllProjectsScreen({
  projects = [],
  loading,
  error,
  menuFor,
  onNewProject,
  onOpenProject,
  onOpenMenu,
  onCloseMenu,
  onRenameProject,
  onPinProject,
  onDeleteProject,
}) {
  const [query, setQuery] = useState("");
  // Built once here rather than handed down as seven props through the list and its sections.
  const row = (project) => (
    <ProjectRow
      key={project.id}
      project={project}
      menuOpen={menuFor === project.id}
      onOpen={onOpenProject}
      onOpenMenu={onOpenMenu}
      onCloseMenu={onCloseMenu}
      onRename={onRenameProject}
      onPin={onPinProject}
      onDelete={onDeleteProject}
    />
  );

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
          <ProjectList projects={projects} query={query} row={row} />
        )}
      </div>
    </div>
  );
}
