import "./shared/app.css";
import "./features/workspace/workspace.css";

import { useEffect, useState } from "react";

import ChatScreen from "./features/workspace/ChatScreen.jsx";
import HomeScreen from "./features/workspace/HomeScreen.jsx";
import ProjectScreen from "./features/workspace/ProjectScreen.jsx";
import SearchPanel from "./features/workspace/SearchPanel.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import { useChat } from "./features/workspace/useChat.js";
import {
  deleteChat,
  renameChat,
  startChatInNewProject,
  startChatInProject,
  useProjectChats,
  useRecentChats,
} from "./features/workspace/useChatLists.js";
import { useFile } from "./features/workspace/useFile.js";
import { useFiles } from "./features/workspace/useFiles.js";
import { useProjects } from "./features/workspace/useProjects.js";
import { useSearch } from "./features/workspace/useSearch.js";
import { useRoute } from "./shared/useRoute.js";

export default function App() {
  const { route, navigate } = useRoute();
  const { projects, error, createProject, editProject, reloadProjects } = useProjects();
  const { recentChats, reloadRecentChats } = useRecentChats();
  const { projectChats, reloadProjectChats } = useProjectChats(route.projectId);
  const { files, reloadFiles, rename, deleting } = useFiles(route.projectId, reloadProjects);
  // One reader for both screens: the chat widens its rail into it, the project screen opens it as a
  // panel. What is being read belongs to the project, so it survives moving between the two.
  const reading = useFile(route.projectId);
  // A file that has just been born changes two answers at once: the list itself, and the count on
  // the project's card.
  const chat = useChat(route.projectId, route.chatId, () =>
    Promise.all([reloadFiles(), reloadProjects()]),
  );

  const [searching, setSearching] = useState(false);
  const search = useSearch();

  const goHome = () => navigate("/");
  const openProject = (id) => navigate(`/p/${id}`);
  const openChat = (projectId, chatId) => navigate(`/p/${projectId}/c/${chatId}`);

  useEffect(() => {
    // One listener owns the keyboard. Two of them could not agree on an order: they hang off the
    // same window event, and stopping propagation does not stop a sibling.
    const onKey = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearching((open) => !open);
        return;
      }
      if (event.key !== "Escape") return;
      // Search first, the reading panel second, and never a step backwards.
      if (searching) setSearching(false);
      else if (reading.name) reading.close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [searching, reading.name, reading.close]);

  const pickHit = (hit) => {
    setSearching(false);
    search.setQuery("");
    if (hit.kind === "chat") openChat(hit.projectId, hit.chatId);
    else openProject(hit.projectId);
    // The file may live in a project we are only now navigating to, so it says which one.
    if (hit.kind === "file") reading.open(hit.fileName, hit.projectId);
  };

  // The screen reads its project out of the list the app already holds; asking the server a second
  // time would be asking for an answer we have.
  const project = projects.find((candidate) => candidate.id === route.projectId) ?? null;

  const ask = (question, current, field) => {
    const answer = window.prompt(question, current);
    // An empty answer cancels -- the design's rule. The server refuses an empty name anyway, so
    // this is a convenience rather than the guarantee.
    if (answer && answer.trim()) editProject(route.projectId, { [field]: answer });
  };

  const afterStart = async (started) => {
    // The counts on the cards and both chat lists have all moved, so they are read again.
    await Promise.all([reloadProjects(), reloadRecentChats()]);
    openChat(started.projectId, started.chatId);
  };

  const sendFromHome = async (text) => {
    const started = await startChatInNewProject(text);
    await afterStart({ projectId: started.project.id, chatId: started.chat.id });
  };

  const removeFile = (name) => {
    // Reading something that is no longer there is not reading, so the panel goes first.
    if (reading.name === name) reading.close();
    return deleting.remove(name);
  };

  const renameFile = async (name) => {
    const wanted = window.prompt("File name", name);
    if (!wanted || !wanted.trim()) return;
    const renamed = await rename(name, wanted);
    // The file is still there under another name, so the panel follows it rather than closing.
    if (renamed && reading.name === name) reading.open(renamed.name);
  };

  const retitleChat = async (chatId) => {
    const current = projectChats.find((candidate) => candidate.id === chatId);
    const title = window.prompt("Chat title", current?.title);
    if (!title || !title.trim()) return;
    await renameChat(route.projectId, chatId, title);
    // Two lists show a title, and neither of them is the other's copy.
    await Promise.all([reloadProjectChats(), reloadRecentChats()]);
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
        onNewChat={goHome}
        onNewProject={createProject}
        onOpenProject={openProject}
        onOpenChat={openChat}
        onSearch={() => setSearching(true)}
      />
      <main className="main">
        {/* Creating a project keeps the user on home: what this item has to show is the project
            appearing in both lists at once. */}
        {route.view === "home" ? (
          <HomeScreen
            projects={projects}
            error={error}
            onNewProject={createProject}
            onOpenProject={openProject}
            onSend={sendFromHome}
          />
        ) : null}

        {route.view === "project" ? (
          <ProjectScreen
            project={project}
            chats={projectChats}
            files={files}
            reading={reading}
            deleting={{ ...deleting, remove: removeFile }}
            onBack={goHome}
            onRename={() => ask("Project name", project?.name, "name")}
            onDescribe={() => ask("Project description", project?.desc, "desc")}
            onSend={sendFromProject}
            onOpenChat={(chatId) => openChat(route.projectId, chatId)}
            onRenameChat={retitleChat}
            onDeleteChat={removeChat}
            onRenameFile={renameFile}
          />
        ) : null}

        {route.view === "chat" ? (
          <ChatScreen
            project={project}
            chat={chat.chat}
            files={files}
            reading={reading}
            deleting={{ ...deleting, remove: removeFile }}
            onRenameFile={renameFile}
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

      {searching ? (
        <SearchPanel
          query={search.query}
          hits={search.hits}
          searched={search.searched}
          onQuery={search.setQuery}
          onPick={pickHit}
          onClose={() => setSearching(false)}
        />
      ) : null}
    </div>
  );
}
