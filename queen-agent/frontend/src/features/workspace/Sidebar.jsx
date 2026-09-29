// Inside a project the sidebar is the project's own (design 151, 152, 168): a filled + New chat
// first, then every chat it holds. Projects are listed on All projects, and the open one's name
// stands in the bar, so none is listed here. App draws the sidebar only with a project open.

// One button, never a drag: claude.ai's behaviour rather than the rail's, and the user asked for it
// by that name. It stands in the sidebar's own last row, open and folded alike, so a press never
// moves out from under the pointer (design 187, Claude Code's place for it). Folded, the sidebar is
// not hidden: an icon column stands where it was, + for New chat above and this fold at its foot
// (design 174); the rows are titles, and have no icon forms to fold into.
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
        <Fold collapsed onToggle={onToggle} />
      </aside>
    );
  }

  return (
    <aside className="sidebar">
      <button type="button" className="sidebar__new-chat" onClick={onNewChat}>
        <span className="sidebar__plus">+</span>
        New chat
      </button>

      <div className="sidebar__chats">
        {chats.length ? (
          chats.map((chat) => (
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
          <p className="sidebar__empty">No chats yet.</p>
        )}
      </div>

      <Fold onToggle={onToggle} />
    </aside>
  );
}
