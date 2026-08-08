import { useEffect, useRef, useState } from "react";
import Sidebar from "./Sidebar.jsx";
import Message from "./Message.jsx";
import MentionPicker from "./MentionPicker.jsx";
import FilePane from "./FilePane.jsx";
import { sendChat } from "./api.js";
import { usePersisted } from "./usePersisted.js";
import { useWorkspace } from "./useWorkspace.js";
import { createChat, deleteChat, replaceMessages, setDraft } from "./storage.js";
import { createProject, deleteProject } from "./projects.js";
import {
  activeMention,
  createFile,
  deleteFile,
  filesOf,
  matchFiles,
  mentionedFiles,
  replaceActiveMention,
  writeFile,
} from "./files.js";
import { skills } from "./skillSource.js";
import { findSkill, matchSkills, splitSkillPrefix } from "./skills.js";

const DEFAULT_MODEL = "grok-4.3";
const EMPTY_CHAT = { id: null, messages: [], draft: "" };

export default function App() {
  const [apiKey, setApiKey] = usePersisted("xai_key", "");
  const [model, setModel] = usePersisted("xai_model", DEFAULT_MODEL);
  const ws = useWorkspace();
  const [pending, setPending] = useState(false);
  const [notice, setNotice] = useState(null);
  const chatRef = useRef(null);

  const chat = ws.chat ?? EMPTY_CHAT;
  const projectId = ws.project?.id ?? null;
  const projectFiles = filesOf(ws.files, projectId);

  useEffect(() => {
    const el = chatRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [chat.messages]);

  async function send() {
    const typed = chat.draft.trim();
    if (!typed || pending) return;

    const { name, content } = splitSkillPrefix(typed);
    if (name && !findSkill(skills, name)) {
      const available = skills.map((s) => `/${s.name}`).join(", ");
      setNotice(`"/${name}" bulunamadı. Mevcut skill'ler: ${available}`);
      return;
    }
    // A name with nothing after it is a half-typed message, not a request.
    if (!content) return;
    setNotice(null);

    // The reply belongs to the chat that asked for it, so its id is captured before the await: the
    // user may well be looking at a different chat by the time the answer lands.
    const askedIn = chat.id;
    const named = mentionedFiles(content, projectFiles);
    const question = { role: "user", content };
    if (name) question.skill = name;
    if (named.length > 0) question.files = named;
    const asked = [...chat.messages, question];

    ws.setChats((cs) => setDraft(replaceMessages(cs, askedIn, asked), askedIn, ""));
    setPending(true);
    try {
      const reply = await sendChat({
        key: apiKey,
        model,
        messages: asked,
        skills,
        files: projectFiles,
      });
      ws.setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "assistant", content: reply }])
      );
    } catch (err) {
      // Covers a non-200 response and a request that never left: network, CORS, unparsable body.
      ws.setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "error", content: err.message }])
      );
    }
    setPending(false);
  }

  // Two lists, one moment: a skill is called at the very start of a message, a file anywhere in it.
  // Only one can be open, and the skill call wins because it can only ever be the whole draft.
  const skillQuery = /^\/[A-Za-z0-9-]*$/.test(chat.draft) ? chat.draft.slice(1) : null;
  const fileQuery = skillQuery === null ? activeMention(chat.draft) : null;

  function writeDraft(text) {
    ws.setChats((cs) => setDraft(cs, chat.id, text));
  }

  function newProject() {
    const { projects, id } = createProject(ws.projects, window.prompt("Proje adı") ?? "");
    ws.setProjects(projects);
    ws.setProject(id);
    ws.setFile(null);
  }

  function removeProject(id, counts) {
    const project = ws.projects.find((p) => p.id === id);
    const question = `${project.name} — ${counts.files} dosya ve ${counts.chats} sohbet silinecek. Emin misin?`;
    if (!window.confirm(question)) return;
    ws.setFiles(ws.files.filter((f) => f.projectId !== id));
    ws.setChats(ws.chats.filter((c) => c.projectId !== id));
    ws.setProjects(deleteProject(ws.projects, id));
  }

  function newFile() {
    const asked = window.prompt("Dosya adı") ?? "";
    if (!asked.trim()) return;
    try {
      const { files, id } = createFile(ws.files, projectId, asked);
      ws.setFiles(files);
      ws.setFile(id);
      setNotice(null);
    } catch (err) {
      setNotice(err.message);
    }
  }

  function removeFile(id) {
    const file = ws.files.find((f) => f.id === id);
    if (!window.confirm(`${file.name} silinecek. Emin misin?`)) return;
    ws.setFiles(deleteFile(ws.files, id));
  }

  function removeChat(id) {
    if (!window.confirm("Bu sohbet silinecek. Emin misin?")) return;
    ws.setChats(deleteChat(ws.chats, id));
  }

  function newChat() {
    const { chats, id } = createChat(ws.chats, projectId);
    ws.setChats(chats);
    ws.setChat(id);
  }

  return (
    <div className="layout">
      <Sidebar
        projects={ws.projects}
        files={ws.files}
        chats={ws.chats}
        active={{ projectId, chatId: chat.id }}
        on={{
          openProject: (id) => {
            ws.setProject(id);
            ws.setFile(null);
          },
          newProject,
          deleteProject: removeProject,
          openChat: ws.setChat,
          newChat,
          deleteChat: removeChat,
        }}
        apiKey={apiKey}
        onApiKey={setApiKey}
        model={model}
        onModel={setModel}
      />

      <main className="main">
        <div className="chat" ref={chatRef}>
          {chat.messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} skill={m.skill} />
          ))}
        </div>

        <footer>
          {skillQuery !== null && (
            <MentionPicker
              prefix="/"
              items={matchSkills(skills, skillQuery)}
              onPick={(picked) => writeDraft(`/${picked} `)}
            />
          )}
          {fileQuery !== null && (
            <MentionPicker
              prefix="@"
              items={matchFiles(projectFiles, fileQuery)}
              onPick={(picked) => writeDraft(replaceActiveMention(chat.draft, picked))}
            />
          )}
          {notice && <div className="skill-error">{notice}</div>}
          <textarea
            placeholder="Mesaj yaz — Enter gönderir, Shift+Enter alt satıra geçer"
            value={chat.draft}
            onChange={(e) => writeDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
          />
          <button onClick={send} disabled={pending}>
            {pending ? "…" : "Gönder"}
          </button>
        </footer>
      </main>

      <FilePane
        files={ws.files}
        projectId={projectId}
        file={ws.file}
        on={{
          openFile: ws.setFile,
          newFile,
          deleteFile: removeFile,
          closeFile: () => ws.setFile(null),
        }}
        onChange={(content) => ws.setFiles(writeFile(ws.files, ws.file.id, content))}
      />
    </div>
  );
}
