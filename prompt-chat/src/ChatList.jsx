import { chatsOf, titleOf } from "./storage.js";

export default function ChatList({ chats, projectId, activeId, on }) {
  return (
    <div className="list">
      <div className="group">sohbetler</div>
      {chatsOf(chats, projectId).map((chat) => {
        const title = titleOf(chat.messages);
        return (
          <div key={chat.id} className={chat.id === activeId ? "row active" : "row"}>
            <button className="row-open" onClick={() => on.openChat(chat.id)}>
              {title}
            </button>
            <button
              className="row-delete"
              aria-label={`${title} sohbetini sil`}
              onClick={() => on.deleteChat(chat.id)}
            >
              ×
            </button>
          </div>
        );
      })}
      <button className="add" onClick={on.newChat}>
        + Yeni sohbet
      </button>
    </div>
  );
}
