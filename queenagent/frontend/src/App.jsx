import "./shared/app.css";
import "./features/workspace/workspace.css";

import { useEffect, useState } from "react";

import ChatScreen from "./features/workspace/ChatScreen.jsx";
import NoProjectsScreen from "./features/workspace/NoProjectsScreen.jsx";
import OfflineStrip from "./features/workspace/OfflineStrip.jsx";
import ProjectScreen from "./features/workspace/ProjectScreen.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import { useChat } from "./features/workspace/useChat.js";
import {
  deleteChat,
  startChatInProject,
  useProjectChats,
} from "./features/workspace/useChatLists.js";
import { useFile } from "./features/workspace/useFile.js";
import { useFiles } from "./features/workspace/useFiles.js";
import { useProjects } from "./features/workspace/useProjects.js";
import { useOnline } from "./shared/useOnline.js";
import { useRoute } from "./shared/useRoute.js";

// A draft has the shape of a chat so the screen needs no second mode: an empty conversation with a
// title of its own. It is never sent anywhere -- the first message creates the real one.
const DRAFT = { id: null, title: "New chat", messages: [] };

export default function App() {
  const { route, navigate } = useRoute();
  const online = useOnline();
  const { projects, error, loading, createProject, editProject, reloadProjects } = useProjects();
  const { projectChats, reloadProjectChats, loadingChats } = useProjectChats(route.projectId);
  // A chat is born with its first message, so "New chat" has nothing to create yet. The draft has
  // an address all the same -- a reload must not throw the user out of what they were typing.
  const drafting = route.view === "chat" && route.chatId === "new";
  const { files, reloadFiles, loadingFiles, deleting } = useFiles(
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

  const openProject = (id) => navigate(`/p/${id}`);
  const openChat = (projectId, chatId, options) =>
    navigate(`/p/${projectId}/c/${chatId}`, options);
  const openDraft = () => navigate(`/p/${route.projectId}/c/new`);

  // "/" is a fork, not a screen. It is read once the list has arrived -- an empty array cannot tell
  // "there is none" from "not here yet", and deciding early shows the wrong screen for a moment.
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
      // Escape closes what is open and never steps backwards.
      if (reading.name) reading.close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [reading.name, reading.close]);

  // The screen reads its project out of the list the app already holds; asking the server a second
  // time would be asking for an answer we have.
  const project = projects.find((candidate) => candidate.id === route.projectId) ?? null;

  const askForName = () => {
    const answer = window.prompt("Project name", project?.name);
    // An empty answer cancels -- the design's rule. The server refuses an empty name anyway, so
    // this is a convenience rather than the guarantee.
    if (answer && answer.trim()) editProject(route.projectId, { name: answer });
  };

  const removeFile = (name) => {
    // Reading something that is no longer there is not reading, so the panel goes first.
    if (reading.name === name) reading.close();
    return deleting.remove(name);
  };

  const removeChat = async (chatId) => {
    // The browser's own dialog, as with Rename: a second dialog language is not something the
    // design asks for. The sentence says what goes and what stays.
    if (!window.confirm("Delete this chat? Its files stay in the project.")) return;
    await deleteChat(route.projectId, chatId);
    await Promise.all([reloadProjectChats(), reloadProjects()]);
  };

  // The draft address is not a place to come back to, so the chat that replaces it does exactly
  // that; starting one from the project screen is an ordinary step and is pushed.
  const startChat = async (text) => {
    const started = await startChatInProject(route.projectId, text);
    await Promise.all([reloadProjectChats(), reloadProjects()]);
    openChat(route.projectId, started.id, { replace: drafting });
  };

  return (
    <div className="app-shell" data-testid="app-shell">
      <Sidebar
        projects={projects}
        chats={projectChats}
        activeProjectId={route.projectId}
        activeChatId={route.chatId}
        onNewChat={openDraft}
        onNewProject={createProject}
        onOpenProject={openProject}
        onOpenChat={(chatId) => openChat(route.projectId, chatId)}
      />
      <main className="main">
        {/* Above the content and not over it: the sidebar keeps working and so does the composer. */}
        <OfflineStrip online={online} />

        {/* The fork draws nothing while it is still deciding, and hands over to the empty screen
            only once the server has said there is nothing to open. */}
        {atFork && !landing && (!loading || error) ? (
          <NoProjectsScreen error={error} onNewProject={createProject} />
        ) : null}

        {route.view === "project" ? (
          <ProjectScreen
            project={project}
            chats={projectChats}
            files={files}
            loadingChats={loadingChats}
            loadingFiles={loadingFiles}
            reading={reading}
            deleting={{ ...deleting, remove: removeFile }}
            onRename={askForName}
            onSend={startChat}
            onOpenChat={(chatId) => openChat(route.projectId, chatId)}
            onDeleteChat={removeChat}
          />
        ) : null}

        {route.view === "chat" ? (
          <ChatScreen
            project={project}
            chat={drafting ? DRAFT : chat.chat}
            files={files}
            loadingFiles={loadingFiles}
            reading={reading}
            deleting={{ ...deleting, remove: removeFile }}
            error={chat.error}
            missing={chat.missing}
            thinking={chat.thinking}
            streamingText={chat.streamingText}
            creatingFile={chat.creatingFile}
            createdFiles={chat.createdFiles}
            onBack={() => openProject(route.projectId)}
            onSend={drafting ? startChat : chat.send}
            onRetry={chat.retry}
          />
        ) : null}
      </main>
    </div>
  );
}
