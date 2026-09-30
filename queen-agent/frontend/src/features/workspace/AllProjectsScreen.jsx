import { useState } from "react";

import ProjectRow, { UndoRow } from "./ProjectRow.jsx";
import ProjectsFailure from "./ProjectsFailure.jsx";
import Spinner from "./Spinner.jsx";
import { matches } from "./matches.js";

// The screen the app opens on (the design's items 135, 142, 167), and the one Exit project comes
// back to. No sidebar stands beside it: no project is open here. The order is the server's
// (list_projects.py) -- pinned first, then the most recently used -- and this screen only splits it:
// where the pins end, and between the Projects tab and the Archived one (the design's 190, 191).
//
// The search and the tab are this screen's own state: what is shown while typing is the UI's
// (FOUNDATION, Decision 4), so they reach neither the server nor the address.

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

function ProjectList({ any, shown, archivedTab, query, row }) {
  // Asked first: with nothing to search, "no match" would be the wrong news -- and on either tab.
  if (!any) return <p className="all-projects__empty">No projects yet.</p>;
  const asked = query.trim();
  const found = shown.filter((project) => matches(project.name, query));
  if (!found.length) {
    let none = archivedTab ? "No archived projects." : "Every project is archived.";
    if (asked) none = `No projects match "${asked}".`;
    return <p className="all-projects__empty">{none}</p>;
  }
  // The archive is one list with no heading, as the design draws it: pinning sorts the projects in
  // use, and nothing archived is in use.
  if (archivedTab) return <div className="all-projects__list">{found.map(row)}</div>;
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
  writeError,
  onRetry,
  menuFor,
  onNewProject,
  onOpenProject,
  onOpenMenu,
  onCloseMenu,
  onRenameProject,
  onPinProject,
  onArchiveProject,
  onRestoreProject,
  onDeleteProject,
}) {
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState("projects");
  // The project Archive has just taken, while its Undo is on offer, and the pin it had then -- what
  // Undo asks for back, as the design's undoing = { id, pinnedAt } holds it. The archive lets the
  // pin go, but the server still lists the project where its pin had it (Madde 382), so where it
  // stood is where the list still has it; the pin it had says whether that is Pinned or Recent.
  const [undoing, setUndoing] = useState(null);

  const archived = projects.filter((project) => project.archived);
  const open = projects.filter((project) => !project.archived);
  const shown =
    tab === "archived"
      ? archived
      : projects
          .filter((project) => !project.archived || project.id === undoing?.id)
          .map((project) =>
            project.id === undoing?.id ? { ...project, pinned: undoing.pinned } : project,
          );

  // The offer lasts until the next thing is done, as the design's settleUndoing reads it: every
  // action on a row starts from its ⋯, and so does another Archive.
  const openMenu = (id) => {
    setUndoing(null);
    onOpenMenu?.(id);
  };
  const archive = (id, toArchive) => {
    if (toArchive) setUndoing({ id, pinned: projects.find((project) => project.id === id).pinned });
    onArchiveProject?.(id, toArchive);
  };
  const undo = async ({ id, pinned }) => {
    // Held until the list has come back: let go sooner, the project would vanish for a moment.
    await onRestoreProject?.(id, pinned);
    // Unless another project's offer began meanwhile.
    setUndoing((current) => (current?.id === id ? null : current));
  };
  const switchTab = (next) => {
    setUndoing(null);
    setTab(next);
  };

  // Built once here rather than handed down as eight props through the list and its sections.
  const row = (project) =>
    project.id === undoing?.id ? (
      <UndoRow key={project.id} name={project.name} onUndo={() => undo(undoing)} />
    ) : (
      <ProjectRow
        key={project.id}
        project={project}
        menuOpen={menuFor === project.id}
        onOpen={onOpenProject}
        onOpenMenu={openMenu}
        onCloseMenu={onCloseMenu}
        onRename={onRenameProject}
        onPin={onPinProject}
        onArchive={archive}
        onDelete={onDeleteProject}
      />
    );

  // A wait comes first: Try again shows the frame and its ring again (the design's 173).
  if (error && !loading) return <ProjectsFailure error={error} onRetry={onRetry} />;

  const tabs = [
    ["projects", "Projects", open.length],
    ["archived", "Archived", archived.length],
  ];

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
          <div className="all-projects__tabs">
            {tabs.map(([name, label, count]) => (
              <button
                key={name}
                type="button"
                className={`all-projects__tab${tab === name ? " is-on" : ""}`}
                onClick={() => switchTab(name)}
              >
                {/* Until the list has come, a count would be a guess and not a fact. */}
                {label} <span className="all-projects__count">{loading ? "" : count}</span>
              </button>
            ))}
          </div>
        </div>
        {/* A write that did not land leaves the list known, so its words stand over the list in
            the line every list uses; the next write takes them away. */}
        {writeError ? <p className="list-error">{writeError}</p> : null}
        {/* Until the list has come, "no projects yet" is a guess and not a fact: the ring turns in
            its place while everything above it stands (the design's 173). */}
        {loading ? (
          <div className="all-projects__spinner">
            <Spinner />
          </div>
        ) : (
          <ProjectList
            any={projects.length > 0}
            shown={shown}
            archivedTab={tab === "archived"}
            query={query}
            row={row}
          />
        )}
      </div>
    </div>
  );
}
