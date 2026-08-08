import { useState } from "react";
import { titleOf } from "./storage.js";

export default function Sidebar({
  chats,
  activeId,
  onSelect,
  onNew,
  onDelete,
  apiKey,
  onApiKey,
  model,
  onModel,
}) {
  // With no key there is nothing to do but enter one, so the panel opens itself on a first visit
  // and stays out of the way afterwards.
  const [settingsOpen, setSettingsOpen] = useState(() => apiKey === "");

  function remove(id) {
    if (window.confirm("Bu sohbet silinecek. Emin misin?")) onDelete(id);
  }

  return (
    <aside className="sidebar">
      <button className="new-chat" aria-label="Yeni sohbet ekle" onClick={onNew}>
        + Yeni sohbet
      </button>

      <ul className="chat-list">
        {chats.map((c) => {
          const title = titleOf(c.messages);
          return (
            <li key={c.id} className={c.id === activeId ? "chat-row active" : "chat-row"}>
              <button className="chat-open" onClick={() => onSelect(c.id)}>
                {title}
              </button>
              <button
                className="chat-delete"
                aria-label={`${title} sohbetini sil`}
                onClick={() => remove(c.id)}
              >
                ×
              </button>
            </li>
          );
        })}
      </ul>

      <div className="settings">
        {settingsOpen && (
          <div className="settings-body">
            <input
              type="password"
              placeholder="xAI API anahtarı"
              autoComplete="off"
              value={apiKey}
              onChange={(e) => onApiKey(e.target.value)}
            />
            <input
              placeholder="model"
              autoComplete="off"
              value={model}
              onChange={(e) => onModel(e.target.value)}
            />
          </div>
        )}
        <button className="settings-toggle" onClick={() => setSettingsOpen((v) => !v)}>
          ⚙ Ayarlar
        </button>
      </div>
    </aside>
  );
}
