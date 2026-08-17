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
  useRecentChats,
} from "./features/workspace/useChatLists.js";
import { useFile } from "./features/workspace/useFile.js";
import { useFiles } from "./features/workspace/useFiles.js";
import { useProjects } from "./features/workspace/useProjects.js";
import { useOnline } from "./shared/useOnline.js";
import { useRoute } from "./shared/useRoute.js";

export default function App() {
  const { route, navigate } = useRoute();
  const online = useOnline();
  const { projects, error, loading, createProject, editProject, reloadProjects } = useProjects();
  const { recentChats, reloadRecentChats } = useRecentChats();
  const { projectChats, reloadProjectChats, loadingChats } = useProjectChats(route.projectId);
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
    route.chatId,
    () => Promise.all([reloadFiles(), reloadProjects()]),
    online,
  );

  const openProject = (id) => navigate(`/p/${id}`);
  const openChat = (projectId, chatId) => navigate(`/p/${projectId}/c/${chatId}`);
  // What "New chat" does is Madde 6's decision. Until then it opens the project screen, where a
  // chat is started; the control is only drawn when there is a project, so there is always one.
  const openNewChat = () => openProject(route.projectId ?? projects[0].id);

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

  const afterStart = async (started) => {
    // The counts on the cards and both chat lists have all moved, so they are read again.
    await Promise.all([reloadProjects(), reloadRecentChats()]);
    openChat(started.projectId, started.chatId);
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
    await Promise.all([reloadProjectChats(), reloadRecentChats(), reloadProjects()]);
  };

  const sendFromProject = async (text) => {
    const started = await startChatInProject(route.projectId, text);
    await reloadProjectChats();
    await afterStart({ projectId: route.projectId, chatId: started.id });
  };

  return (
    <div className="app-shell" data-testid="app-shell">
      <Sidebar
        projects={projects}
        recentChats={recentChats}
        activeProjectId={route.projectId}
        activeChatId={route.chatId}
        onNewChat={openNewChat}
        onNewProject={createProject}
        onOpenProject={openProject}
        onOpenChat={openChat}
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
            onSend={sendFromProject}
            onOpenChat={(chatId) => openChat(route.projectId, chatId)}
            onDeleteChat={removeChat}
          />
        ) : null}

        {route.view === "chat" ? (
          <ChatScreen
            project={project}
            chat={chat.chat}
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
            onSend={chat.send}
            onRetry={chat.retry}
          />
        ) : null}
      </main>
    </div>
  );
}
