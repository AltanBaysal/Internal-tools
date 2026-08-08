import { describe, it, expect } from "vitest";
import { createProject, deleteProject, projectContents } from "./projects.js";

describe("createProject", () => {
  it("adds a named project and reports its id", () => {
    const { projects, id } = createProject([], "Kış çekimi");
    expect(projects).toEqual([{ id: 1, name: "Kış çekimi" }]);
    expect(id).toBe(1);
  });

  it("falls back to a placeholder rather than an empty name", () => {
    expect(createProject([], "   ").projects[0].name).toBe("Yeni proje");
  });

  it("keeps numbering above the highest id in the list", () => {
    expect(createProject([{ id: 7, name: "eski" }], "yeni").id).toBe(8);
  });
});

describe("deleteProject", () => {
  it("drops the project by id", () => {
    const { projects } = createProject([], "a");
    expect(deleteProject(projects, 1)).toEqual([]);
  });
});

describe("projectContents", () => {
  // The delete confirmation says what will be lost out loud, so it needs the counts.
  it("counts the files and chats that would go with it", () => {
    const files = [
      { id: 1, projectId: 1, name: "a.md", content: "" },
      { id: 2, projectId: 1, name: "b.md", content: "" },
      { id: 3, projectId: 2, name: "c.md", content: "" },
    ];
    const chats = [
      { id: 1, projectId: 1, messages: [], draft: "" },
      { id: 2, projectId: 2, messages: [], draft: "" },
    ];
    expect(projectContents(1, files, chats)).toEqual({ files: 2, chats: 1 });
  });

  it("reports zeroes for an empty project", () => {
    expect(projectContents(9, [], [])).toEqual({ files: 0, chats: 0 });
  });
});
