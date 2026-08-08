import { renderHook, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { useWorkspace } from "./useWorkspace.js";
import { deleteChat, replaceMessages } from "./storage.js";

// Every one of these repairs used to be proved only through the whole App. On its own the hook says
// what it guarantees: there is always a project, always a chat inside it, and never a stale id.
describe("useWorkspace", () => {
  it("creates a project on a first visit so nothing is ever project-less", () => {
    const { result } = renderHook(() => useWorkspace());
    expect(result.current.projects).toHaveLength(1);
    expect(result.current.project.name).toBe("Genel");
  });

  it("opens a chat inside that project", () => {
    const { result } = renderHook(() => useWorkspace());
    expect(result.current.chat).toBeTruthy();
    expect(result.current.chat.projectId).toBe(result.current.project.id);
  });

  it("adopts chats stored before projects existed", () => {
    localStorage.setItem("chats", JSON.stringify([{ id: 1, messages: [], draft: "" }]));
    localStorage.setItem("active_chat", "1");
    const { result } = renderHook(() => useWorkspace());
    expect(result.current.chats[0].projectId).toBe(result.current.project.id);
    expect(result.current.chat.id).toBe(1);
  });

  it("falls back to a real project when the stored id points at nothing", () => {
    localStorage.setItem("projects", JSON.stringify([{ id: 1, name: "Genel" }]));
    localStorage.setItem("active_project", "99");
    const { result } = renderHook(() => useWorkspace());
    expect(result.current.project.id).toBe(1);
  });

  // Emptiness is the assertion, not the id: ids are max + 1, so deleting the only chat frees id 1
  // for the replacement to take again.
  it("opens a fresh chat when the last one is deleted", () => {
    const { result } = renderHook(() => useWorkspace());
    act(() => {
      result.current.setChats(
        replaceMessages(result.current.chats, result.current.chat.id, [
          { role: "user", content: "silinecek" },
        ])
      );
    });

    act(() => {
      result.current.setChats(deleteChat(result.current.chats, result.current.chat.id));
    });

    expect(result.current.chat).toBeTruthy();
    expect(result.current.chat.messages).toEqual([]);
    expect(result.current.chat.projectId).toBe(result.current.project.id);
  });

  it("closes a file belonging to a project that is not open", () => {
    localStorage.setItem(
      "projects",
      JSON.stringify([
        { id: 1, name: "Genel" },
        { id: 2, name: "Kampanya" },
      ])
    );
    localStorage.setItem("active_project", "1");
    localStorage.setItem(
      "files",
      JSON.stringify([{ id: 7, projectId: 2, name: "baska.md", content: "" }])
    );
    localStorage.setItem("active_file", "7");
    const { result } = renderHook(() => useWorkspace());
    expect(result.current.file).toBeNull();
  });
});
