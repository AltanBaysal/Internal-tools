import { useRef, useState } from "react";

import ProjectsFailure from "./ProjectsFailure.jsx";
import Spinner from "./Spinner.jsx";

// Every + New project asks for the name first (the design's items 135, 153, 169): a project is
// born under the name the user chose, never one they would have to change afterwards. Where Cancel
// and Escape go is App's, since only App knows where the user came from.
export default function NameProjectScreen({ first, loading, error, onRetry, onCreate }) {
  const [name, setName] = useState("");
  // What the server said when it would not make the project. The screen's own, so it stands beside
  // the name it refused and goes with the screen.
  const [refused, setRefused] = useState(null);
  // A ref rather than state: a double Enter is two presses that can land before a re-render, and
  // each would be a project of its own.
  const sending = useRef(false);

  // Whether this is the first project is not known until the list comes, so there is no frame to
  // keep: the ring stands alone in empty's centring (the design's 173). A wait comes before a
  // failure, so Try again shows it too.
  if (loading) {
    return (
      <div className="empty">
        <Spinner />
      </div>
    );
  }
  if (error) return <ProjectsFailure error={error} onRetry={onRetry} />;

  const create = () => {
    const trimmed = name.trim();
    // A blank field does nothing, as the design's does; the server refuses one anyway.
    if (!trimmed || sending.current) return;
    sending.current = true;
    Promise.resolve(onCreate(trimmed))
      // The name is the user's work (FOUNDATION, principle 1): a refusal is said under it and the
      // field keeps it, ready to send again.
      .catch((failure) => setRefused(failure.message))
      .finally(() => {
        sending.current = false;
      });
  };

  return (
    <div className="empty">
      <div className="empty__box">
        {/* The title is the field's own label: no separate "Project name" text stands beside it. */}
        <label className="empty__title" htmlFor="project-name">
          {first ? "Name your first project" : "Name your project"}
        </label>
        <p className="empty__line">
          Chats live inside a project, and the files they create stay there.
        </p>
        <div className="empty__row">
          <input
            id="project-name"
            type="text"
            className="empty__field"
            placeholder="Project name"
            autoComplete="off"
            autoFocus
            value={name}
            onChange={(event) => setName(event.target.value)}
            onKeyDown={(event) => {
              if (event.key !== "Enter" || event.shiftKey) return;
              event.preventDefault();
              create();
            }}
          />
          <button type="button" className="empty__action" onClick={create}>
            Create project
          </button>
        </div>
        {refused ? <p className="empty__refused">{refused}</p> : null}
      </div>
    </div>
  );
}
