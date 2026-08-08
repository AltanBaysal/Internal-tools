import { useEffect } from "react";
import { usePersistedJson } from "./usePersisted.js";
import { createProject } from "./projects.js";
import { adoptOrphanChats, chatsOf, createChat } from "./storage.js";

const DEFAULT_PROJECT = "Genel";

// One place owns the store and repairs it, so no screen has to guard against a missing project, a
// chat belonging to nobody, or an id pointing at something that was deleted.
export function useWorkspace() {
  const [projects, setProjects] = usePersistedJson("projects", []);
  const [files, setFiles] = usePersistedJson("files", []);
  const [chats, setChats] = usePersistedJson("chats", []);
  const [projectId, setProjectId] = usePersistedJson("active_project", null);
  const [chatId, setChatId] = usePersistedJson("active_chat", null);
  const [fileId, setFileId] = usePersistedJson("active_file", null);

  // There is never a moment without a project and an open chat: not on a first visit, not after the
  // open one is deleted, and not for chats stored before projects existed. All of it is repaired
  // here rather than guarded at every use. Each pass fixes at most one thing and returns, so the
  // effect cannot chase its own writes.
  useEffect(() => {
    if (projects.length === 0) {
      const { projects: withOne, id } = createProject(projects, DEFAULT_PROJECT);
      setProjects(withOne);
      setProjectId(id);
      return;
    }

    const open = projects.some((p) => p.id === projectId) ? projectId : projects[0].id;
    if (open !== projectId) {
      setProjectId(open);
      return;
    }

    const adopted = adoptOrphanChats(chats, open);
    if (adopted !== chats) {
      setChats(adopted);
      return;
    }

    const mine = chatsOf(chats, open);
    if (mine.length === 0) {
      const { chats: withOne, id } = createChat(chats, open);
      setChats(withOne);
      setChatId(id);
      return;
    }
    if (!mine.some((c) => c.id === chatId)) {
      setChatId(mine[0].id);
      return;
    }

    // An open file belonging to another project would make it unclear which project you are in.
    if (fileId !== null && !files.some((f) => f.id === fileId && f.projectId === open)) {
      setFileId(null);
    }
  }, [
    projects, chats, files, projectId, chatId, fileId,
    setProjects, setChats, setProjectId, setChatId, setFileId,
  ]);

  return {
    projects,
    files,
    chats,
    project: projects.find((p) => p.id === projectId) ?? null,
    chat: chats.find((c) => c.id === chatId) ?? null,
    file: files.find((f) => f.id === fileId) ?? null,
    setProjects,
    setFiles,
    setChats,
    setProject: setProjectId,
    setChat: setChatId,
    setFile: setFileId,
  };
}
