import "./shared/app.css";
import "./features/workspace/workspace.css";

import ChatScreen from "./features/workspace/ChatScreen.jsx";
import HomeScreen from "./features/workspace/HomeScreen.jsx";
import ProjectScreen from "./features/workspace/ProjectScreen.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import { useChat } from "./features/workspace/useChat.js";
import {
  startChatInNewProject,
  startChatInProject,
  useProjectChats,
  useRecentChats,
} from "./features/workspace/useChatLists.js";
import { useFile } from "./features/workspace/useFile.js";
import { useFiles } from "./features/workspace/useFiles.js";
import { useProjects } from "./features/workspace/useProjects.js";
import { useRoute } from "./shared/useRoute.js";

export default function App() {
  const { route, navigate } = useRoute();
  const { projects, error, createProject, editProject, reloadProjects } = useProjects();
  const { recentChats, reloadRecentChats } = useRecentChats();
  const { projectChats, reloadProjectChats } = useProjectChats(route.projectId);
  const { files, reloadFiles } = useFiles(route.projectId);
  // One reader for both screens: the chat widens its rail into it, the project screen opens it as a
  // panel. What is being read belongs to the project, so it survives moving between the two.
  const reading = useFile(route.projectId);
  // A file that has just been born changes two answers at once: the list itself, and the count on
  // the project's card.
  const chat = useChat(route.projectId, route.chatId, () =>
    Promise.all([reloadFiles(), reloadProjects()]),
  );

  const goHome = () => navigate("/");
  const openProject = (id) => navigate(`/p/${id}`);
  const openChat = (projectId, chatId) => navigate(`/p/${projectId}/c/${chatId}`);

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
            onBack={goHome}
            onRename={() => ask("Project name", project?.name, "name")}
            onDescribe={() => ask("Project description", project?.desc, "desc")}
            onSend={sendFromProject}
            onOpenChat={(chatId) => openChat(route.projectId, chatId)}
          />
        ) : null}

        {route.view === "chat" ? (
          <ChatScreen
            project={project}
            chat={chat.chat}
            files={files}
            reading={reading}
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
