import { describe, it, expect } from "vitest";
import {
  activeMention,
  createFile,
  deleteFile,
  filesOf,
  findFile,
  matchFiles,
  mentionedFiles,
  normaliseName,
  replaceActiveMention,
  writeFile,
} from "./files.js";

describe("normaliseName", () => {
  it("adds .md when there is no extension", () => {
    expect(normaliseName("plan")).toBe("plan.md");
  });

  it("leaves an extension the user typed alone", () => {
    expect(normaliseName("notlar.txt")).toBe("notlar.txt");
  });

  it("trims the surrounding space before deciding", () => {
    expect(normaliseName("  plan  ")).toBe("plan.md");
  });
});

describe("createFile", () => {
  it("adds an empty file to the project and reports its id", () => {
    const { files, id } = createFile([], 1, "plan");
    expect(files).toEqual([{ id: 1, projectId: 1, name: "plan.md", content: "" }]);
    expect(id).toBe(1);
  });

  it("numbers ids across every project, never per project", () => {
    const { files } = createFile([{ id: 4, projectId: 9, name: "a.md", content: "" }], 1, "b");
    expect(files.at(-1).id).toBe(5);
  });

  it("refuses a name already used in the same project", () => {
    const { files } = createFile([], 1, "plan");
    expect(() => createFile(files, 1, "plan.md")).toThrow(/zaten var/);
  });

  it("allows the same name in a different project", () => {
    const { files } = createFile([], 1, "plan");
    expect(() => createFile(files, 2, "plan")).not.toThrow();
  });

  it("refuses an empty name", () => {
    expect(() => createFile([], 1, "   ")).toThrow(/boş olamaz/);
  });
});

describe("filesOf", () => {
  it("keeps one project's files out of another's", () => {
    const a = createFile([], 1, "a").files;
    const b = createFile(a, 2, "b").files;
    expect(filesOf(b, 1).map((f) => f.name)).toEqual(["a.md"]);
  });
});

describe("writeFile", () => {
  it("replaces the content of one file and leaves the rest untouched", () => {
    const { files } = createFile(createFile([], 1, "a").files, 1, "b");
    const after = writeFile(files, 1, "yeni metin");
    expect(after[0].content).toBe("yeni metin");
    expect(after[1].content).toBe("");
  });
});

describe("deleteFile", () => {
  it("drops the file by id", () => {
    const { files } = createFile([], 1, "a");
    expect(deleteFile(files, 1)).toEqual([]);
  });
});

describe("findFile", () => {
  it("finds a file by name inside its project", () => {
    const files = createFile([], 1, "plan").files;
    expect(findFile(files, 1, "plan.md").id).toBe(1);
  });

  it("does not reach into another project", () => {
    const files = createFile([], 1, "plan").files;
    expect(findFile(files, 2, "plan.md")).toBeNull();
  });
});

const PROJE = [
  { id: 1, projectId: 1, name: "plan.md", content: "PLAN İÇERİĞİ" },
  { id: 2, projectId: 1, name: "sahneler.md", content: "SAHNE İÇERİĞİ" },
];

describe("mentionedFiles", () => {
  it("finds a name that really exists", () => {
    expect(mentionedFiles("@plan.md ilk maddeyi açıkla", PROJE)).toEqual(["plan.md"]);
  });

  it("finds a mention in the middle of a sentence", () => {
    expect(mentionedFiles("şu @plan.md dosyasına bak", PROJE)).toEqual(["plan.md"]);
  });

  it("keeps the order they appear in", () => {
    expect(mentionedFiles("@sahneler.md ve @plan.md", PROJE)).toEqual(["sahneler.md", "plan.md"]);
  });

  it("reports a repeated name once", () => {
    expect(mentionedFiles("@plan.md ve yine @plan.md", PROJE)).toEqual(["plan.md"]);
  });

  it("ignores an @ that matches no file, because @ occurs in ordinary writing", () => {
    expect(mentionedFiles("@herkes bakabilir, ali@example.com", PROJE)).toEqual([]);
  });

  it("needs the extension, so a bare stem is not a call", () => {
    expect(mentionedFiles("@plan bir şey", PROJE)).toEqual([]);
  });

  it("returns an empty list for text with no @ at all", () => {
    expect(mentionedFiles("sıradan bir cümle", PROJE)).toEqual([]);
  });
});

describe("activeMention", () => {
  it("is open while a name is being typed at the end", () => {
    expect(activeMention("bak şu @pla")).toBe("pla");
  });

  it("is open on a bare @, so the whole list shows", () => {
    expect(activeMention("@")).toBe("");
  });

  it("closes once a space follows the name", () => {
    expect(activeMention("@plan.md ")).toBeNull();
  });

  it("is closed for text without an @", () => {
    expect(activeMention("selam")).toBeNull();
  });

  it("is closed for an empty draft", () => {
    expect(activeMention("")).toBeNull();
  });
});

describe("replaceActiveMention", () => {
  it("swaps the half-typed name for the full one and adds a space", () => {
    expect(replaceActiveMention("bak şu @pla", "plan.md")).toBe("bak şu @plan.md ");
  });

  it("works on a bare @", () => {
    expect(replaceActiveMention("@", "plan.md")).toBe("@plan.md ");
  });
});

describe("matchFiles", () => {
  it("lists everything for an empty query", () => {
    expect(matchFiles(PROJE, "")).toHaveLength(2);
  });

  it("matches anywhere in the name and ignores case", () => {
    expect(matchFiles(PROJE, "SAHNE").map((f) => f.name)).toEqual(["sahneler.md"]);
  });
});
