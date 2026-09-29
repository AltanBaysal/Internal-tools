import "./shared/app.css";
import "./features/workspace/workspace.css";

import { useEffect, useState } from "react";

import AllProjectsScreen from "./features/workspace/AllProjectsScreen.jsx";
import Bar from "./features/workspace/Bar.jsx";
import ChatScreen from "./features/workspace/ChatScreen.jsx";
import ConfirmDialog from "./features/workspace/ConfirmDialog.jsx";
import NameProjectScreen from "./features/workspace/NameProjectScreen.jsx";
import OfflineStrip from "./features/workspace/OfflineStrip.jsx";
import OpenProject from "./features/workspace/OpenProject.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import { countOf } from "./features/workspace/countOf.js";
import { useChat } from "./features/workspace/useChat.js";
import { useProjectChats } from "./features/workspace/useChatLists.js";
import { useFile } from "./features/workspace/useFile.js";
import { useFiles } from "./features/workspace/useFiles.js";
import { DEFAULT_MODE, EDIT } from "./features/workspace/modes.js";
import { useProjects } from "./features/workspace/useProjects.js";
import { DEFAULT_RAIL_WIDTH, railFitsIn, railWidthFor } from "./features/workspace/railWidth.js";
import { useRememberedMap } from "./shared/remembered.js";
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
  const { shell, width: shellWidth, steps } = useShellWidth();
  const { projects, error, loading, createProject, editProject, removeProject, reloadProjects } =
    useProjects();
  // Both live here rather than inside the screens that open them, because App's one listener owns
  // Escape and it can only close what it can see.
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
  // The selection is the chat's own since Madde 105 -- one browser key, an entry per chat, so what
  // is picked in one chat never stands in another. Remembered for the reason Madde 100 gave: a
  // five-step flow that loses its skill on a reload sends the next turn with no instruction.
  const [chatSkills, rememberChatSkill] = useRememberedMap("chat-skills");
  // What the next chat is born with. The draft's picker holds a chat that does not exist yet; the
  // birth writes the value into the newborn's entry and lets it go, so the next draft starts with
  // nothing.
  const [draftSkill, setDraftSkill] = useState("");
  // The last mode picked, and what the next turn is sent in. Held for the session like the skill,
  // and unlike it never written anywhere: nothing on the server reads a mode back.
  const [lastMode, setLastMode] = useState(DEFAULT_MODE);
  // Which picker is open, if any: null, "skills" or "mode". One value rather than a boolean each,
  // because booleans can both be true and then menus stand over the same corner of the screen. Here
  // rather than inside a picker, because App's one listener owns Escape and it can only close what
  // it can see.
  const [pickerOpen, setPickerOpen] = useState(null);
  const { projectChats, reloadProjectChats } = useProjectChats(route.projectId);
  // A chat is born with its first message, so "New chat" has nothing to create yet. The draft has
  // an address all the same -- a reload must not throw the user out of what they were typing.
  const drafting = route.view === "chat" && route.chatId === "new";
  // One value on the screen and in the request, Madde 86's rule at the chat's boundary.
  const skillInForce = drafting ? draftSkill : (chatSkills[route.chatId] ?? "");
  const changeSkill = (value) => {
    if (drafting) setDraftSkill(value);
    else rememberChatSkill(route.chatId, value);
  };
  const { files, reloadFiles, loadingFiles, filesError, deleting } = useFiles(
    route.projectId,
    reloadProjects,
  );
  // The chat widens its rail into the reader. What is being read belongs to the project, so it
  // survives moving between the project's chats.
  const reading = useFile(route.projectId);
  // Madde 192: everything about files that can have gone stale, in one action. Two of them, and
  // they stale differently -- a late list hides a name, a late panel shows the wrong text under the
  // right one. One button rather than two, so the user never has to work out which they are fixing.
  //
  // reloadProjects is not in here: what moves a project card's count is a file being born, and
  // onFileCreated below already answers that.
  const refresh = () => Promise.all([reloadFiles(), reading.reload()]);
  // A step, and pushed; OpenProject writes the chat it opens over it.
  const openProject = (id) => navigate(`/p/${id}`);
  const openChat = (projectId, chatId, options) =>
    navigate(`/p/${projectId}/c/${chatId}`, options);
  const openDraft = () => navigate(`/p/${route.projectId}/c/new`);
  // Where the naming screen was reached from, so Cancel and Escape go back there (Madde 361). Held
  // here because the address is the only other memory, and /new says nothing about it; reached by
  // its address or reloaded, there is no screen it came from, and All projects is where it opens.
  const [namingFrom, setNamingFrom] = useState("/");
  // Every + New project comes here: a project is born under a name the user chose.
  const askForNewProject = () => {
    setNamingFrom(window.location.pathname);
    navigate("/new");
  };
  // Both ways off the naming screen write over it, so the back button never lands there to make a
  // second project.
  const leaveNaming = () => navigate(namingFrom, { replace: true });
  // Opened where a new project has something to do: its draft.
  const createNamed = async (name) => {
    const created = await createProject(name);
    if (created) navigate(`/p/${created.id}/c/new`, { replace: true });
  };

  const chat = useChat(
    route.projectId,
    drafting ? null : route.chatId,
    () => Promise.all([reloadFiles(), reloadProjects()]),
    // Madde 88: the stream's first frame names its chat. When that is a chat this screen was not
    // on, it has just been born -- the address follows it while the answer is still arriving, and
    // the lists that count chats are out of date.
    (id) => {
      // The skill that governed the birth becomes the newborn's own selection, and the draft lets
      // it go -- Madde 105.
      if (draftSkill) rememberChatSkill(id, draftSkill);
      setDraftSkill("");
      openChat(route.projectId, id, { replace: true });
      return Promise.all([reloadProjectChats(), reloadProjects()]);
    },
    // A turn is the usual writer, so its end is the usual moment for both to be out of date.
    refresh,
  );

  useEffect(() => {
    // One listener owns the keyboard. Two of them could not agree on an order: they hang off the
    // same window event, and stopping propagation does not stop a sibling.
    const onKey = (event) => {
      // Ctrl + . folds the sidebar and brings it back from anywhere, the composer included (Madde
      // 351, claude.ai's key). Held with Ctrl a key types nothing into a field, and taking the
      // default leaves the browser nothing else to do with it.
      if (event.ctrlKey && event.key === ".") {
        event.preventDefault();
        setSidebarCollapsed((folded) => !folded);
        return;
      }
      if (event.key !== "Escape") return;
      // Escape closes what is open, innermost first, and never steps backwards.
      if (menuFor) setMenuFor(null);
      else if (confirming) setConfirming(null);
      // The design's order, fark 67: project menu → confirm box → the open picker → open panel.
      // It named Skills and the model; the mode is a picker since Madde 91 and the model is not one
      // since Madde 358. Only one can be open at a time, so they take one place in the order.
      else if (pickerOpen) setPickerOpen(null);
      else if (reading.name) reading.close();
      // The naming screen's Escape is its Cancel, and like Cancel it is there only while a project
      // exists to go back to (the design's 195).
      else if (route.view === "new" && projects.length) navigate(namingFrom, { replace: true });
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [
    menuFor,
    confirming,
    pickerOpen,
    reading.name,
    reading.close,
    route.view,
    projects.length,
    namingFrom,
    navigate,
  ]);

  // The screen reads its project out of the list the app already holds; asking the server a second
  // time would be asking for an answer we have.
  const project = projects.find((candidate) => candidate.id === route.projectId) ?? null;

  // The counts come from the list the app already holds. A project is deleted only from its All
  // projects row (Madde 360), where none is open, so there is no screen to leave afterwards.
  const askToDelete = (id) => {
    const doomed = projects.find((candidate) => candidate.id === id);
    if (!doomed) return;
    setConfirming({
      title: `Delete "${doomed.name}"?`,
      body: `The ${countOf(doomed.chats ?? 0, "chat")} and ${countOf(
        doomed.files ?? 0,
        "file",
      )} in this project are deleted with it. This can't be undone.`,
      // The design's All projects answers its own row's Delete in the same word.
      confirmLabel: "Delete",
      onConfirm: () => {
        setConfirming(null);
        removeProject(id);
      },
    });
  };

  // One rule, one place: opening something must never be a way of hiding it. Madde 22 adds a second
  // caller -- the card in the transcript -- and will not write the rule again.
  const openFile = (name) => {
    setRailCollapsed(false);
    reading.open(name);
  };

  // Every deletion in the app comes through the same slot: ask, then do. A third one would know
  // where to ask without being told.
  //
  // The reader is never open when this is reached: the only way to ask is the row's ×, and the row
  // stands in the rail the reader takes over.
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

  // Opening one picker closes the other, by construction rather than by remembering to.
  const togglePicker = (which) => setPickerOpen((open) => (open === which ? null : which));

  return (
    <div ref={shell} className={`app-shell ${steps}`.trim()} data-testid="app-shell">
      {/* "/" is All projects, where the app opens. */}
      {route.view === "new" ? (
        <Bar exit={projects.length ? "Cancel" : null} onExit={leaveNaming} />
      ) : (
        <Bar project={project} onExit={() => navigate("/")} />
      )}
      <div className="app-shell__body">
        {/* Not on All projects or the naming screen: no project is open on either (the design's
            items 135, 167, 169). */}
        {route.view === "root" || route.view === "new" ? null : (
          <Sidebar
            projects={projects}
            chats={projectChats}
            activeProjectId={route.projectId}
            activeChatId={route.chatId}
            onNewChat={openDraft}
            onNewProject={askForNewProject}
            onOpenProject={openProject}
            onOpenChat={(chatId) => openChat(route.projectId, chatId)}
            collapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed((folded) => !folded)}
          />
        )}
        <main className="main">
          {/* Above the content and not over it: the sidebar keeps working and so does the composer. */}
          <OfflineStrip online={online} />

          {route.view === "root" ? (
            <AllProjectsScreen
              projects={projects}
              loading={loading}
              error={error}
              onNewProject={askForNewProject}
              onOpenProject={openProject}
              menuFor={menuFor}
              onOpenMenu={setMenuFor}
              onCloseMenu={() => setMenuFor(null)}
              onRenameProject={(id, name) => editProject(id, { name })}
              onPinProject={(id, pinned) => editProject(id, { pinned })}
              onDeleteProject={askToDelete}
            />
          ) : null}

          {route.view === "new" ? (
            <NameProjectScreen
              first={!projects.length}
              loading={loading}
              error={error}
              onCreate={createNamed}
            />
          ) : null}

          {/* Keyed, so a failure to read one project's chats does not stand over the next one's. */}
          {route.view === "project" && project ? (
            <OpenProject key={project.id} projectId={project.id} navigate={navigate} />
          ) : null}
          {/* The address bar is something a person can type into, so a wrong id has to be
              survivable -- and "does not exist" is only said once the list has answered. */}
          {route.view === "project" && !project && !loading ? (
            <div className="screen">
              <div className="screen__column">
                <p className="screen__missing">That project does not exist.</p>
              </div>
            </div>
          ) : null}

          {route.view === "chat" ? (
            <ChatScreen
              chat={drafting ? DRAFT : chat.chat}
              /* Before the record comes, the chat is called what its sidebar row calls it. */
              loadingTitle={projectChats.find((row) => row.id === route.chatId)?.title}
              files={files}
              loadingFiles={loadingFiles}
              filesError={filesError}
              reading={{ ...reading, open: openFile }}
              deleting={{ ...deleting, remove: askToDeleteFile }}
              onRefresh={refresh}
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
              progress={chat.progress}
              onBack={() => navigate("/")}
              /* The selection is the chat's own since Madde 105; the draft holds the birth value
                 instead. What governed a turn is still settled when the message is sent. */
              skill={skillInForce}
              skillsOpen={pickerOpen === "skills"}
              onToggleSkills={() => togglePicker("skills")}
              mode={lastMode}
              modeOpen={pickerOpen === "mode"}
              onToggleMode={() => togglePicker("mode")}
              onModeChange={setLastMode}
              /* The second argument is where an edit starts from, and it is the screen's: which
                 message is being replaced is a state of the transcript, not of the session. */
              onSend={(text, from) => chat.send(text, skillInForce, lastMode, from)}
              onVersion={chat.version}
              /* A full chat's two ways on: the notice's New chat is the sidebar's own. */
              onNewChat={openDraft}
              onContinue={chat.trim}
              onSkillChange={changeSkill}
              onStop={chat.stop}
              /* The question is the hook's; the mode is the session's, and the session is here.
                 One button moves both, and useChat never learns there is such a thing as a mode. */
              permission={chat.permission}
              onAllow={() => {
                chat.answer(true, "");
                /* The answer settles this one call; the picker settles the next turn. Left on
                   ask, the very next message would raise the same question again. */
                setLastMode(EDIT);
              }}
              onDeny={(reason) => chat.answer(false, reason)}
              onRetry={chat.retry}
            />
          ) : null}
        </main>
      </div>

      {/* Outside main so the darkened screen covers the sidebar too. */}
      {confirming ? (
        <ConfirmDialog {...confirming} onCancel={() => setConfirming(null)} />
      ) : null}
    </div>
  );
}
