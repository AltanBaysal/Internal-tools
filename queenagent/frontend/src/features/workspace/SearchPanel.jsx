import { useEffect, useRef } from "react";

function keyOf(hit) {
  return `${hit.kind}-${hit.projectId}-${hit.chatId}-${hit.fileName}`;
}

export default function SearchPanel({ query, hits = [], searched, onQuery, onPick, onClose }) {
  const input = useRef(null);

  useEffect(() => {
    input.current?.focus();
  }, []);

  return (
    <div className="overlay" onClick={onClose} data-testid="search">
      {/* The panel is not the backdrop: a click inside it must not count as a click outside. */}
      <div className="palette" onClick={(event) => event.stopPropagation()}>
        <input
          ref={input}
          className="palette__input"
          value={query}
          placeholder="Search projects, chats and files..."
          onChange={(event) => onQuery(event.target.value)}
        />

        {hits.length ? (
          <div className="palette__hits">
            {hits.map((hit) => (
              <button key={keyOf(hit)} type="button" className="hit" onClick={() => onPick(hit)}>
                <span className="file-chip">{hit.kind}</span>
                <span className="hit__label">{hit.label}</span>
                {/* Eight results can come from eight projects, and "which one is this in?" is
                    asked before the click rather than after it. */}
                {hit.projectName ? <span className="hit__where">{hit.projectName}</span> : null}
              </button>
            ))}
          </div>
        ) : null}

        {searched && !hits.length ? <p className="palette__empty">No results.</p> : null}
      </div>
    </div>
  );
}
