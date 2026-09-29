import { useEffect, useRef, useState } from "react";

import { matches } from "./matches.js";

// Inside a project the sidebar is the project's own (design 151, 152, 168): a filled + New chat
// first, then Search chats, then every chat it holds. Projects are listed on All projects, and the
// open one's name stands in the bar, so none is listed here. App draws the sidebar only with a
// project open.

// One button, never a drag: claude.ai's behaviour rather than the rail's, and the user asked for it
// by that name. It stands in the sidebar's own last row, open and folded alike, so a press never
// moves out from under the pointer (design 187, Claude Code's place for it). Folded, the sidebar is
// not hidden: an icon column stands where it was, + for New chat and the search above and this
// fold at its foot (design 174); the rows are titles, and have no icon forms to fold into.
function Fold({ collapsed, onToggle }) {
  return (
    <div className="sidebar__foot">
      <button
        type="button"
        className="sidebar__fold"
        aria-label={collapsed ? "Show the sidebar" : "Hide the sidebar"}
        onClick={onToggle}
      >
        {/* Drawn in CSS: the app carries no icon files. */}
        <span className="sidebar__panel-icon" />
      </button>
    </div>
  );
}

export default function Sidebar({
  chats = [],
  activeChatId,
  onNewChat,
  onOpenChat,
  collapsed,
  onToggle,
}) {
  // What is shown while typing is the screen's own (FOUNDATION, Decision 4): the query reaches
  // neither the server nor the address. Held here, it outlives a fold and a move between chats --
  // the sidebar stays mounted through both -- and goes when the project is left.
  const [query, setQuery] = useState("");
  const search = useRef(null);
  // The folded column's search asks for the box, and the box only exists once App has unfolded the
  // sidebar -- so the ask waits here for that render. The fold and Ctrl + . never ask.
  const seeking = useRef(false);
  useEffect(() => {
    if (collapsed || !seeking.current) return;
    seeking.current = false;
    // A press never scrolls the page (the design's 155).
    search.current.focus({ preventScroll: true });
  }, [collapsed]);

  if (collapsed) {
    return (
      <aside className="sidebar sidebar--collapsed">
        <button
          type="button"
          className="sidebar__new-chat sidebar__new-chat--icon"
          aria-label="New chat"
          onClick={onNewChat}
        >
          <span className="sidebar__plus">+</span>
        </button>
        <button
          type="button"
          className="sidebar__search-toggle"
          aria-label="Search chats"
          onClick={() => {
            seeking.current = true;
            onToggle();
          }}
        >
          {/* A magnifier drawn in CSS, as the panel icon is. */}
          <span className="sidebar__search-icon" />
        </button>
        <Fold collapsed onToggle={onToggle} />
      </aside>
    );
  }

  const asked = query.trim();
  const shown = chats.filter((chat) => matches(chat.title, query));

  // The keys are the design's: Enter opens the first match -- the server lists the most recent
  // first -- and hands its reply box the focus; Escape empties the box. Escape is the field's own,
  // as a message being edited has it.
  const onKeyDown = (event) => {
    if (event.key === "Enter") {
      if (shown.length) onOpenChat(shown[0].id, { focusReply: true });
    } else if (event.key === "Escape") setQuery("");
  };

  return (
    <aside className="sidebar">
      <button type="button" className="sidebar__new-chat" onClick={onNewChat}>
        <span className="sidebar__plus">+</span>
        New chat
      </button>

      {/* Off: the browser's own suggestions would stand over the list being narrowed. */}
      <input
        ref={search}
        type="text"
        className="sidebar__search"
        placeholder="Search chats"
        aria-label="Search chats"
        autoComplete="off"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={onKeyDown}
      />

      <div className="sidebar__chats">
        {shown.length ? (
          shown.map((chat) => (
            <button
              key={chat.id}
              type="button"
              className={
                chat.id === activeChatId ? "sidebar__chat sidebar__chat--active" : "sidebar__chat"
              }
              onClick={() => onOpenChat(chat.id)}
              title={chat.title}
            >
              {chat.title}
            </button>
          ))
        ) : (
          // Asked about the query first, as the design's sidebar does: something typed and nothing
          // found is the news, whether or not the project has chats.
          <p className="sidebar__empty">{asked ? `No chats match "${asked}".` : "No chats yet."}</p>
        )}
      </div>

      <Fold onToggle={onToggle} />
    </aside>
  );
}
