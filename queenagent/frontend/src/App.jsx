import "./shared/app.css";
import "./features/workspace/workspace.css";

import { useEffect, useState } from "react";

import ChatScreen from "./features/workspace/ChatScreen.jsx";
import ConfirmDialog from "./features/workspace/ConfirmDialog.jsx";
import NoProjectsScreen from "./features/workspace/NoProjectsScreen.jsx";
import OfflineStrip from "./features/workspace/OfflineStrip.jsx";
import ProjectScreen from "./features/workspace/ProjectScreen.jsx";
import SettingsScreen from "./features/settings/SettingsScreen.jsx";
import { useSettings } from "./features/settings/useSettings.js";
import Sidebar from "./features/workspace/Sidebar.jsx";
import Skeleton from "./features/workspace/Skeleton.jsx";
import { useChat } from "./features/workspace/useChat.js";
import {
  deleteChat,
  startChatInProject,
  useProjectChats,
} from "./features/workspace/useChatLists.js";
import { useFile } from "./features/workspace/useFile.js";
import { useFiles } from "./features/workspace/useFiles.js";
import { useProjects } from "./features/workspace/useProjects.js";
import { getJson } from "./shared/api.js";
import { useOnline } from "./shared/useOnline.js";
import { useRoute } from "./shared/useRoute.js";
import { useShellWidth } from "./shared/useShellWidth.js";

// A draft has the shape of a chat so the screen needs no second mode: an empty conversation with a
// title of its own. It is never sent anywhere -- the first message creates the real one.
const DRAFT = { id: null, title: "New chat", messages: [] };

export default function App() {
  const { route, navigate } = useRoute();
  const online = useOnline();
  // Which layout step holds is the shell's own width, measured -- not the window's.
  const { shell, steps } = useShellWidth();
  // The engine's key. Held here rather than only on the settings screen, because the failure card
  // has to know whether there is one -- and asking the error text would be reading tea leaves.
  const { apiKey, save: saveApiKey } = useSettings();
  const { projects, error, loading, createProject, editProject, removeProject, reloadProjects } =
    useProjects();
  // Both live here rather than inside the sidebar, because App's one listener owns Escape and it
  // can only close what it can see.
  const [menuFor, setMenuFor] = useState(null);
  const [confirming, setConfirming] = useState(null);
  // The rail's folded state lasts the session and crosses chats and projects, so it cannot live in
  // a component that is rebuilt every time the address changes.
  const [railCollapsed, setRailCollapsed] = useState(false);
  // The last model picked, and what the next chat is born with. Held for the session rather than
  // written to disk: a chat's own choice is on the server, and this is only the starting point.
  // Empty until the server says what it is set to.
  const [lastModel, setLastModel] = useState("");
  // The same rule for the skill: the chat's own is on the server, this is where the next one starts.
  const [lastSkill, setLastSkill] = useState("");
  // Which picker is open, "model" | "skills" | null. Here rather than inside a picker, because
  // Escape closes them in a fixed order and one has to close the other.
  const [picker, setPicker] = useState(null);
  const { projectChats, reloadProjectChats, loadingChats, chatsError } = useProjectChats(
    route.projectId,
  );
  // A chat is born with its first message, so "New chat" has nothing to create yet. The draft has
  // an address all the same -- a reload must not throw the user out of what they were typing.
  const drafting = route.view === "chat" && route.chatId === "new";
  const { files, reloadFiles, loadingFiles, filesError, deleting } = useFiles(
    route.projectId,
    reloadProjects,
  );
  // One reader for both screens: the chat widens its rail into it, the project screen opens it as a
  // panel. What is being read belongs to the project, so it survives moving between the two.
  const reading = useFile(route.projectId);
  // A file that has just been born changes two answers at once: the list itself, and the count on
  // the project's card.
  const chat = useChat(
    route.projectId,
    drafting ? null : route.chatId,
    () => Promise.all([reloadFiles(), reloadProjects()]),
    online,
  );

  // Which model a chat that picked nothing answers with is a setting, and only the server knows it.
  // Asked once: it cannot change while the app is open.
  useEffect(() => {
    let cancelled = false;
    getJson("/api/model")
      .then((answer) => {
        // Only as a starting point: a pick made in the meantime is the newer answer.
        if (!cancelled && answer?.default) setLastModel((picked) => picked || answer.default);
      })
      // A default nobody could fetch is not worth a message on the screen: the chat's own record
      // carries a resolved name anyway, and only a draft is left saying "Model".
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const openProject = (id) => navigate(`/p/${id}`);
  const openChat = (projectId, chatId, options) =>
    navigate(`/p/${projectId}/c/${chatId}`, options);
  const openDraft = () => navigate(`/p/${route.projectId}/c/new`);

  // "/" is a fork, not a screen. It is read once the list has arrived -- an empty array cannot tell
  // "there is none" from "not here yet", and deciding early shows the wrong screen for a moment.
  // The first answer has not come back yet, so which screen this is cannot be known. A failure ends
  // it too: the empty screen is what carries the server's words.
  const firstLoad = loading && !error;
  const atFork = route.view === "root";
  const landing = atFork && !loading && !error && projects.length > 0 ? projects[0].id : null;
  useEffect(() => {
    if (landing) navigate(`/p/${landing}`, { replace: true });
  }, [landing, navigate]);

  useEffect(() => {
    // One listener owns the keyboard. Two of them could not agree on an order: they hang off the
    // same window event, and stopping propagation does not stop a sibling.
    const onKey = (event) => {
      if (event.key !== "Escape") return;
      // Escape closes what is open, innermost first, and never steps backwards.
      if (menuFor) setMenuFor(null);
      else if (confirming) setConfirming(null);
      // The design's order, fark 67: project menu → confirm box → Skills → model → open panel.
      else if (picker === "skills") setPicker(null);
      else if (picker === "model") setPicker(null);
      else if (reading.name) reading.close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuFor, confirming, picker, reading.name, reading.close]);

  // The screen reads its project out of the list the app already holds; asking the server a second
  // time would be asking for an answer we have.
  const project = projects.find((candidate) => candidate.id === route.projectId) ?? null;

  // The id is asked for rather than assumed: the sidebar menu can rename a project the user is not
  // standing in.
  const askForName = (id) => {
    const named = projects.find((candidate) => candidate.id === id);
    const answer = window.prompt("Project name", named?.name);
    // An empty answer cancels -- the design's rule. The server refuses an empty name anyway, so
    // this is a convenience rather than the guarantee.
    if (answer && answer.trim()) editProject(id, { name: answer });
  };

  // The counts come from the list the app already holds. One of a thing is one of it, not one of
  // them -- the design writes the sentence out that way.
  const countOf = (many, word) => `${many} ${word}${many === 1 ? "" : "s"}`;

  const askToDelete = (id) => {
    const doomed = projects.find((candidate) => candidate.id === id);
    if (!doomed) return;
    setConfirming({
      title: `Delete "${doomed.name}"?`,
      body: `The ${countOf(doomed.chats ?? 0, "chat")} and ${countOf(
        doomed.files ?? 0,
        "file",
      )} in this project are deleted with it. This can't be undone.`,
      confirmLabel: "Delete project",
      onConfirm: () => deleteProject(id),
    });
  };

  // Where to go afterwards is a question only about the project being left: another project's
  // deletion has no business moving the screen the user is on.
  const deleteProject = async (id) => {
    setConfirming(null);
    if (!(await removeProject(id))) return;
    if (route.projectId !== id) return;
    const left = projects.filter((candidate) => candidate.id !== id);
    // "/" rather than a guess: the fork picks the first project, or the empty screen if none is
    // left, and it is the only place that rule is written.
    navigate(left.length ? `/p/${left[0].id}` : "/", { replace: true });
  };

  // One rule, one place: opening something must never be a way of hiding it. Madde 22 adds a second
  // caller -- the card in the transcript -- and will not write the rule again.
  const openFile = (name) => {
    setRailCollapsed(false);
    reading.open(name);
  };

  // Every deletion in the app comes through the same slot: ask, then do. A fourth one would know
  // where to ask without being told.
  //
  // The panel is never open when this is reached: the only way to ask is the row's ×, and the row
  // stands in the column the panel replaces.
  const askToDeleteFile = (name) => {
    setConfirming({
      title: `Delete "${name}"?`,
      body: "The file is moved out of the project. This can't be undone.",
      confirmLabel: "Delete file",
      onConfirm: () => {
        setConfirming(null);
        deleting.remove(name);
      },
    });
  };

  const askToDeleteChat = (chatId) => {
    setConfirming({
      title: "Delete this chat?",
      body: "Its files stay in the project.",
      confirmLabel: "Delete chat",
      onConfirm: async () => {
        setConfirming(null);
        await deleteChat(route.projectId, chatId);
        await Promise.all([reloadProjectChats(), reloadProjects()]);
      },
    });
  };

  // The draft address is not a place to come back to, so the chat that replaces it does exactly
  // that; starting one from the project screen is an ordinary step and is pushed.
  // A chat's own choices live on the server; the last ones made also become what the next chat
  // starts from, and that much is the session's.
  const chooseModel = async (model) => {
    setLastModel(model);
    setPicker(null);
    await chat.choose({ model });
  };

  const chooseSkill = async (skill) => {
    setLastSkill(skill);
    setPicker(null);
    await chat.choose({ skill });
  };

  // One value, two menus: opening either closes whatever was open, and pressing the open one shuts
  // it. "Two menus close each other" needs no rule of its own.
  const togglePicker = (which) => setPicker((open) => (open === which ? null : which));

  const startChat = async (text) => {
    const started = await startChatInProject(route.projectId, text, lastModel, lastSkill);
    await Promise.all([reloadProjectChats(), reloadProjects()]);
    openChat(route.projectId, started.id, { replace: drafting });
  };

  return (
    <div ref={shell} className={`app-shell ${steps}`.trim()} data-testid="app-shell">
      <Sidebar
        projects={projects}
        chats={projectChats}
        activeProjectId={route.projectId}
        activeChatId={route.chatId}
        onNewChat={openDraft}
        onNewProject={createProject}
        onOpenProject={openProject}
        onOpenChat={(chatId) => openChat(route.projectId, chatId)}
        menuFor={menuFor}
        onOpenMenu={setMenuFor}
        onCloseMenu={() => setMenuFor(null)}
        onRenameProject={askForName}
        onDeleteProject={askToDelete}
        onOpenSettings={() => navigate("/settings")}
      />
      <main className="main">
        {/* Above the content and not over it: the sidebar keeps working and so does the composer. */}
        <OfflineStrip online={online} />

        {/* Until the first answer, the whole content area is one skeleton and no screen is drawn.
            Two wrongs close with it: the fork used to sit empty, and an address typed straight into
            a project answered "does not exist" about a list nobody had answered yet. The sidebar
            stays live so navigation is never locked. */}
        {firstLoad && route.view !== "settings" ? <Skeleton variant="screen" rows={3} /> : null}

        {/* The fork draws nothing while it is still deciding, and hands over to the empty screen
            only once the server has said there is nothing to open. */}
        {!firstLoad && atFork && !landing ? (
          <NoProjectsScreen error={error} onNewProject={createProject} />
        ) : null}

        {route.view === "settings" ? (
          <SettingsScreen apiKey={apiKey} onSave={saveApiKey} />
        ) : null}

        {!firstLoad && route.view === "project" ? (
          <ProjectScreen
            project={project}
            chats={projectChats}
            files={files}
            loadingChats={loadingChats}
            loadingFiles={loadingFiles}
            chatsError={chatsError}
            filesError={filesError}
            reading={{ ...reading, open: openFile }}
            deleting={{ ...deleting, remove: askToDeleteFile }}
            onRename={() => askForName(route.projectId)}
            onDelete={() => askToDelete(route.projectId)}
            onSend={startChat}
            onOpenChat={(chatId) => openChat(route.projectId, chatId)}
            onDeleteChat={askToDeleteChat}
          />
        ) : null}

        {!firstLoad && route.view === "chat" ? (
          <ChatScreen
            project={project}
            /* A draft has no record yet, so the choices it would be born with are the session's. */
            chat={drafting ? { ...DRAFT, model: lastModel, skill: lastSkill } : chat.chat}
            files={files}
            loadingFiles={loadingFiles}
            filesError={filesError}
            reading={{ ...reading, open: openFile }}
            deleting={{ ...deleting, remove: askToDeleteFile }}
            railCollapsed={railCollapsed}
            onToggleRail={() => setRailCollapsed((folded) => !folded)}
            error={chat.error}
            refused={chat.refused}
            missing={chat.missing}
            thinking={chat.thinking}
            streamingText={chat.streamingText}
            creatingFile={chat.creatingFile}
            createdFiles={chat.createdFiles}
            onBack={() => openProject(route.projectId)}
            picker={picker}
            onPicker={togglePicker}
            missingKey={!apiKey}
            onSettings={() => navigate("/settings")}
            /* The skill goes with the message: what governed a turn is settled when it is sent. */
            onSend={drafting ? startChat : (text) => chat.send(text, lastSkill)}
            /* A draft has nothing to write to yet, so picking only moves the session's own. */
            onModelChange={
              drafting
                ? (model) => {
                    setLastModel(model);
                    setPicker(null);
                  }
                : chooseModel
            }
            onSkillChange={
              drafting
                ? (skill) => {
                    setLastSkill(skill);
                    setPicker(null);
                  }
                : chooseSkill
            }
            onRetry={chat.retry}
          />
        ) : null}
      </main>

      {/* Outside main so the darkened screen covers the sidebar too. */}
      {confirming ? (
        <ConfirmDialog {...confirming} onCancel={() => setConfirming(null)} />
      ) : null}
    </div>
  );
}
