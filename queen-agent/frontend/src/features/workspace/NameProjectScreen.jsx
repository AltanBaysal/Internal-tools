import { useRef, useState } from "react";

// Every + New project asks for the name first (the design's items 135, 153, 169): a project is
// born under the name the user chose, never one they would have to change afterwards. Where Cancel
// and Escape go is App's, since only App knows where the user came from.
export default function NameProjectScreen({ first, loading, error, onCreate }) {
  const [name, setName] = useState("");
  // A ref rather than state: a double Enter is two presses that can land before a re-render, and
  // each would be a project of its own.
  const sending = useRef(false);

  // Whether this is the first project is not known until the list comes (the spinner is Madde 364's).
  if (loading) return null;
  if (error) {
    return (
      <div className="empty">
        <p className="empty__error">{error}</p>
      </div>
    );
  }

  const create = () => {
    const trimmed = name.trim();
    // A blank field does nothing, as the design's does; the server refuses one anyway.
    if (!trimmed || sending.current) return;
    sending.current = true;
    Promise.resolve(onCreate(trimmed)).finally(() => {
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
      </div>
    </div>
  );
}
