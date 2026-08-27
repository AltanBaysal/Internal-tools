import "./shared/app.css";
import "./features/workspace/workspace.css";

import { useEffect, useState } from "react";

import ChatScreen from "./features/workspace/ChatScreen.jsx";
import ConfirmDialog from "./features/workspace/ConfirmDialog.jsx";
import NoProjectsScreen from "./features/workspace/NoProjectsScreen.jsx";
import OfflineStrip from "./features/workspace/OfflineStrip.jsx";
import ProjectScreen from "./features/workspace/ProjectScreen.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import Skeleton from "./features/workspace/Skeleton.jsx";
import { useChat } from "./features/workspace/useChat.js";
import {
  deleteChat,
  useProjectChats,
} from "./features/workspace/useChatLists.js";
import { useFile } from "./features/workspace/useFile.js";
import { useFiles } from "./features/workspace/useFiles.js";
import { DEFAULT_MODE, EDIT } from "./features/workspace/modes.js";
import { useProjects } from "./features/workspace/useProjects.js";
import { DEFAULT_RAIL_WIDTH, railFitsIn, railWidthFor } from "./features/workspace/railWidth.js";
import { getJson } from "./shared/api.js";
import { useRemembered } from "./shared/remembered.js";
import { useOnline } from "./shared/useOnline.js";
import { parsePath, useRoute } from "./shared/useRoute.js";
import { useShellWidth } from "./shared/useShellWidth.js";

// A draft has the shape of a chat so the screen needs no second mode: an empty conversation with a
// title of its own. It is never sent anywhere -- the first message creates the real one.
const DRAFT = { id: null, title: "New chat", messages: [] };

export default function App() {
  const { route, navigate } = useRoute();
  const online = useOnline();
  // Which layout step holds is the shell's own width, measured -- not the window's.
  const { shell, width: shellWidth, steps } = useShellWidth();
  const { projects, error, loading, createProject, editProject, removeProject, reloadProjects } =
    useProjects();
  // Both live here rather than inside the sidebar, because App's one listener owns Escape and it
  // can only close what it can see.
  const [menuFor, setMenuFor] = useState(null);
  const [confirming, setConfirming] = useState(null);
  // The rail's folded state lasts the session and crosses chats and projects, so it cannot live in
  // a component that is rebuilt every time the address changes. Its width is held for the same
  // reason and in the same place.
  const [railCollapsed, setRailCollapsed] = useState(false);
  const [railWidth, setRailWidth] = useState(DEFAULT_RAIL_WIDTH);
  // The sidebar's own fold, held here for the same reason and outliving every address.
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  // One rule, two reasons. A shell too narrow for both folds the rail without writing it down, so
  // widening the window brings back exactly what the user left -- overwriting their choice would
  // hand them back a folded rail nobody folded.
  const railFoldedByWidth = !railFitsIn(shellWidth);
  // The rail measures the drag; the decision is here, where the folded state is. Pulled in past its
  // minimum it is not a narrower rail, it is a closed one.
  const resizeRail = (desired) => {
    const next = railWidthFor(desired);
    if (next === null) setRailCollapsed(true);
    else setRailWidth(next);
  };
  // The last skill picked, and what the next chat is born with. Remembered by the browser since
  // Madde 100: a five-step flow that loses its skill on a reload sends the next turn with no
  // instruction, and nothing on screen says so.
  const [lastSkill, setLastSkill] = useRemembered("skill", "");
  // The last mode picked, and what the next turn is sent in. Held for the session like the skill,
  // and unlike it never written anywhere: nothing on the server reads a mode back.
  const [lastMode, setLastMode] = useState(DEFAULT_MODE);
  // Which picker is open, if either: null, "skills" or "mode". One value rather than a boolean
  // each, because two booleans can both be true and then two menus stand over the same corner of
  // the screen. Here rather than inside a picker, because App's one listener owns Escape and it
  // can only close what it can see.
  const [pickerOpen, setPickerOpen] = useState(null);
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
  const openProject = (id) => navigate(`/p/${id}`);
  const openChat = (projectId, chatId, options) =>
    navigate(`/p/${projectId}/c/${chatId}`, options);
  const openDraft = () => navigate(`/p/${route.projectId}/c/new`);

  const chat = useChat(
    route.projectId,
    drafting ? null : route.chatId,
    () => Promise.all([reloadFiles(), reloadProjects()]),
    // Madde 88: the stream's first frame names its chat. When that is a chat this screen was not
    // on, it has just been born -- the address follows it while the answer is still arriving, and
    // the lists that count chats are out of date.
    (id) => {
      openChat(route.projectId, id, { replace: true });
      return Promise.all([reloadProjectChats(), reloadProjects()]);
    },
  );

  // "/" is a fork, not a screen. It is read once the list has arrived -- an empty array cannot tell
  // "there is none" from "not here yet", and deciding early shows the wrong screen for a moment.
  // The first answer has not come back yet, so which screen this is cannot be known. A failure ends
  // it too: the empty screen is what carries the server's words.
  const firstLoad = loading && !error;
  const atFork = route.view === "root";
  const landing = atFork && !loading && !error && projects.length > 0 ? projects[0].id : null;
  useEffect(() => {
    // The address the browser has now, not the one this render was built from. An effect carries the
    // values of the commit that scheduled it, so a list arriving in the same batch as a move would
    // have the fork deciding for someone who has already left -- and replacing where they went.
    // Asked of the address rather than of the literal "/": every unrecognised path parses to the
    // fork too, and one of them used to be a screen. Deleting that screen without widening this
    // question would have left /settings redirecting nowhere and drawing nothing.
    if (landing && parsePath(window.location.pathname).view === "root") {
      // The project screen. It was sent to the draft chat for a while, because the pickers lived
      // only on the chat composer and a skill could not be chosen until a message had been sent --
      // which moved the landing instead of fixing the screen. The pickers are here now.
      navigate(`/p/${landing}`, { replace: true });
    }
  }, [landing, navigate]);

  useEffect(() => {
    // One listener owns the keyboard. Two of them could not agree on an order: they hang off the
    // same window event, and stopping propagation does not stop a sibling.
    const onKey = (event) => {
      if (event.key !== "Escape") return;
      // Escape closes what is open, innermost first, and never steps backwards.
      if (menuFor) setMenuFor(null);
      else if (confirming) setConfirming(null);
      // The design's order, fark 67: project menu → confirm box → the open picker → open panel.
      // It named two pickers, Madde 82 took one out and Madde 91 put another back; only one of
      // them can be open at a time, so they take one place in the order between them.
      else if (pickerOpen) setPickerOpen(null);
      else if (reading.name) reading.close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuFor, confirming, pickerOpen, reading.name, reading.close]);

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
  // Opening one closes the other, by construction rather than by remembering to.
  const togglePicker = (which) => setPickerOpen((open) => (open === which ? null : which));

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
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((folded) => !folded)}
      />
      <main className="main">
        {/* Above the content and not over it: the sidebar keeps working and so does the composer. */}
        <OfflineStrip online={online} />

        {/* Until the first answer, the whole content area is one skeleton and no screen is drawn.
            Two wrongs close with it: the fork used to sit empty, and an address typed straight into
            a project answered "does not exist" about a list nobody had answered yet. The sidebar
            stays live so navigation is never locked. */}
        {firstLoad ? <Skeleton variant="screen" rows={3} /> : null}

        {/* The fork draws nothing while it is still deciding, and hands over to the empty screen
            only once the server has said there is nothing to open. */}
        {!firstLoad && atFork && !landing ? (
          <NoProjectsScreen error={error} onNewProject={createProject} />
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
            /* No chat here to write a choice to, so it is the session's -- the same value the
               draft chat is born with, and the same one startChat already sends. */
            skill={lastSkill}
            skillsOpen={pickerOpen === "skills"}
            onToggleSkills={() => togglePicker("skills")}
            onSkillChange={setLastSkill}
            mode={lastMode}
            modeOpen={pickerOpen === "mode"}
            onToggleMode={() => togglePicker("mode")}
            onModeChange={setLastMode}
            onRename={() => askForName(route.projectId)}
            onDelete={() => askToDelete(route.projectId)}
            onSend={(text) => chat.send(text, lastSkill, lastMode)}
            onOpenChat={(chatId) => openChat(route.projectId, chatId)}
            onDeleteChat={askToDeleteChat}
          />
        ) : null}

        {!firstLoad && route.view === "chat" ? (
          <ChatScreen
            project={project}
            chat={drafting ? DRAFT : chat.chat}
            files={files}
            loadingFiles={loadingFiles}
            filesError={filesError}
            reading={{ ...reading, open: openFile }}
            deleting={{ ...deleting, remove: askToDeleteFile }}
            railCollapsed={railCollapsed || railFoldedByWidth}
            railFoldedByWidth={railFoldedByWidth}
            railWidth={railWidth}
            onResizeRail={resizeRail}
            onToggleRail={() => setRailCollapsed((folded) => !folded)}
            error={chat.error}
            refused={chat.refused}
            missing={chat.missing}
            thinking={chat.thinking}
            streamingText={chat.streamingText}
            creatingFile={chat.creatingFile}
            createdFiles={chat.createdFiles}
            streamingCalls={chat.streamingCalls}
            onBack={() => openProject(route.projectId)}
            /* The selection is the session's since Madde 86: one value, and both screens are
               handed it. What governed a turn is settled when the message is sent. */
            skill={lastSkill}
            skillsOpen={pickerOpen === "skills"}
            onToggleSkills={() => togglePicker("skills")}
            mode={lastMode}
            modeOpen={pickerOpen === "mode"}
            onToggleMode={() => togglePicker("mode")}
            onModeChange={setLastMode}
            onSend={(text) => chat.send(text, lastSkill, lastMode)}
            onSkillChange={setLastSkill}
            onStop={chat.stop}
            /* The question is the hook's; the mode is the session's, and the session is here. One
               button moves both, and useChat never learns there is such a thing as a mode. */
            permission={chat.permission}
            onAllow={() => {
              chat.answer(true, "");
              /* The answer settles this one call; the picker settles the next turn. Left on ask,
                 the very next message would raise the same question again. */
              setLastMode(EDIT);
            }}
            onDeny={(reason) => chat.answer(false, reason)}
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
