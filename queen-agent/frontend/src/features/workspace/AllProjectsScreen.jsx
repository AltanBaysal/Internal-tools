import { useRef, useState } from "react";

import ProjectRow from "./ProjectRow.jsx";
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

function ProjectList({ any, found, archivedTab, query, row }) {
  // Asked first: with nothing to search, "no match" would be the wrong news -- and on either tab.
  if (!any) return <p className="all-projects__empty">No projects yet.</p>;
  const asked = query.trim();
  if (!found.length) {
    let none = archivedTab ? "No archived projects." : "Every project is archived.";
    if (asked) none = `No projects match "${asked}".`;
    return <p className="all-projects__empty">{none}</p>;
  }
  // The archive is one list with no heading, as the design draws it (190, 191): the server never
  // lists an archived project as pinned (Madde 384), and a row still on its way keeps its place in
  // that order.
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
  onDeleteProject,
}) {
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState("projects");
  // The projects Archive has taken while the server is still asked: they leave Projects at once
  // (the design's 217), since an archive takes its time (Madde 446). Each is drawn archived until
  // its own answer, the list read again, says where it stands -- on Archived, or back on Projects
  // with the refusal's words over the list. Until then it keeps its place in the server's order,
  // so a project that was pinned stands at the top of Archived and moves once the answer comes.
  const [leaving, setLeaving] = useState([]);
  const column = useRef(null);
  const search = useRef(null);

  const listed = projects.map((project) =>
    leaving.includes(project.id) ? { ...project, archived: true } : project,
  );
  const archived = listed.filter((project) => project.archived);
  const open = listed.filter((project) => !project.archived);
  const shown = tab === "archived" ? archived : open;
  // What the list draws, and what the search's Enter opens the first of (the design's 218): one
  // reckoning, so the two cannot part. The server lists the pinned first, so the first found is the
  // first row drawn on either tab.
  const found = shown.filter((project) => matches(project.name, query));
  // An archived project opens as any other (Madde 443), so Enter is the same on both tabs. While the
  // list loads the spinner stands in its place, and there is no first row to open.
  const openFirst = (event) => {
    if (event.key !== "Enter" || loading || !found.length) return;
    onOpenProject?.(found[0].id);
  };

  // The pressed ⋯ leaves with its row, so the keyboard goes to the ⋯ that comes to stand in its
  // place -- the next one down the list as drawn, searched or not -- or to the search where none
  // does (the design's 217). Handed over before the row goes, while the next one is still drawn.
  const handOverFrom = (id) => {
    const mores = [...column.current.querySelectorAll("[data-project]")];
    const next = mores[mores.findIndex((more) => more.dataset.project === id) + 1];
    // The next ⋯ moves into the place being looked at, so the window stays; the search may be
    // far above a long list's last row, and the keyboard is not left off the screen.
    if (next) next.focus({ preventScroll: true });
    else search.current.focus();
  };
  const archive = async (id, toArchive) => {
    if (!toArchive) {
      onArchiveProject?.(id, false);
      return;
    }
    handOverFrom(id);
    setLeaving((ids) => [...ids, id]);
    await onArchiveProject?.(id, true);
    setLeaving((ids) => ids.filter((one) => one !== id));
  };

  // Built once here rather than handed down as eight props through the list and its sections.
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
      <div className="screen__column" ref={column}>
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
            ref={search}
            type="text"
            className="all-projects__search"
            placeholder="Search projects"
            aria-label="Search projects"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={openFirst}
            autoFocus
          />
          <div className="all-projects__tabs">
            {tabs.map(([name, label, count]) => (
              <button
                key={name}
                type="button"
                className={`all-projects__tab${tab === name ? " is-on" : ""}`}
                onClick={() => setTab(name)}
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
            found={found}
            archivedTab={tab === "archived"}
            query={query}
            row={row}
          />
        )}
      </div>
    </div>
  );
}
