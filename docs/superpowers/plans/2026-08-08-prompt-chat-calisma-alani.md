# prompt-chat Çalışma Alanı — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** prompt-chat'e proje ve dosya kazandırmak — dosyaları kullanıcı yazar, `@ad` ile sohbete
çağırır.

**Architecture:** Üç katman korunur. Proje ve dosya kuralları saf katmanda iki yeni modülde
(`projects.js`, `files.js`), `localStorage` sahipliği tek bir io hook'unda (`useWorkspace.js`),
`@` açılımı ise zaten var olan saf `toRequestBody`'de — `/skill` ile aynı iskelet. Agent, araç ve
döngü yok: dosyaya yazan tek şey kullanıcının klavyesi.

**Tech Stack:** React 18.3 · Vite 5.4 · Vitest 3.2 + jsdom · bağımlılık eklenmez.

**Spec:** [2026-08-08-prompt-chat-calisma-alani-design.md](../specs/2026-08-08-prompt-chat-calisma-alani-design.md)

## Global Constraints

- **Yeni bağımlılık yok.** `package.json` değişmez — markdown biçimleyici dahil. Dosya içeriği ham
  metin olarak gösterilir.
- **Katman kuralları (CODE-STANDARD):** `fetch` yalnız `api.js`'te, `localStorage` yalnız
  `usePersisted.js`'te. Saf katman ağ, React ve `localStorage` bilmez.
- **`id` üretimi `max + 1`.** `crypto.randomUUID`, `Date.now`, `Math.random` yok — saf katman
  stub'sız test edilebilir kalır.
- **Dil:** kod yorumları, docstring'ler ve **test adları İngilizce**; ekranda görünen metin Türkçe.
- **Agent yok.** Bu planın hiçbir görevinde araç, tool calling ya da döngü yazılmaz.
- **Commit yok** — kullanıcı `npm run dev` ile deneyip onaylamadan hiçbir görev commit'lenmez.

---

## Dosya yapısı

| Dosya | Sorumluluk | Durum |
|---|---|---|
| `src/files.js` | **saf** — ad normalleştirme, dosya CRUD, `@` anışları | yeni |
| `src/projects.js` | **saf** — proje CRUD, silme onayının sayacağı içerik | yeni |
| `src/useWorkspace.js` | **io** — projeler/dosyalar/sohbetler + açık olanlar, boş hâl onarımı | yeni |
| `src/ProjectTree.jsx` | **ekran** — iki kademeli sol ağaç | yeni |
| `src/FileView.jsx` | **ekran** — sağdaki düzenleyici | yeni |
| `src/MentionPicker.jsx` | **ekran** — `/` ve `@` listelerinin ortak gövdesi | `SkillPicker.jsx`'ten |
| `src/storage.js` | **saf** — sohbetler projeye bağlanır | değişir |
| `src/chat.js` | **saf** — dosya açılımı, ilk-anış kuralı | değişir |
| `src/api.js` | **io** — `files`'ı taşır | değişir |
| `src/App.jsx` | **ekran** — bağlama | değişir |
| `src/Sidebar.jsx` | **ekran** — ağacı barındırır, ayarları tutar | değişir |
| `src/app.css` | üç sütunlu yerleşim, ağaç, düzenleyici | değişir |

---

## Task 1: `files.js` — ad kuralı ve dosya işlemleri

**Files:**
- Create: `prompt-chat/src/files.js`
- Test: `prompt-chat/src/files.test.js`

**Interfaces:**
- Consumes: yok.
- Produces:
  - `normaliseName(raw) -> string`
  - `filesOf(files, projectId) -> file[]`
  - `createFile(files, projectId, rawName) -> { files, id }`; boş ya da yinelenen adda `Error`
  - `writeFile(files, id, content) -> file[]`
  - `deleteFile(files, id) -> file[]`
  - `findFile(files, projectId, name) -> file | null`
  - Dosya şekli: `{ id: number, projectId: number, name: string, content: string }`

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/files.test.js` oluştur:

```js
import { describe, it, expect } from "vitest";
import { createFile, deleteFile, filesOf, findFile, normaliseName, writeFile } from "./files.js";

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
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/files.test.js`
Beklenen: FAIL — `Failed to resolve import "./files.js"`.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/files.js` oluştur:

```js
const DEFAULT_EXTENSION = ".md";

// Everything this app writes is markdown, so typing the extension is friction with no payoff. A
// name that already has a dot is left alone: the user meant something by it.
export function normaliseName(raw) {
  const trimmed = raw.trim();
  return trimmed.includes(".") ? trimmed : trimmed + DEFAULT_EXTENSION;
}

export function filesOf(files, projectId) {
  return files.filter((file) => file.projectId === projectId);
}

// Ids are unique across the whole store, not per project: a file is looked up by id everywhere
// except in `@ad`, and per-project numbering would make two files share one.
export function createFile(files, projectId, rawName) {
  if (!rawName.trim()) throw new Error("dosya adı boş olamaz");
  const name = normaliseName(rawName);
  if (filesOf(files, projectId).some((file) => file.name === name)) {
    throw new Error(`"${name}" adında bir dosya zaten var`);
  }
  const id = files.reduce((max, file) => Math.max(max, file.id), 0) + 1;
  return { files: [...files, { id, projectId, name, content: "" }], id };
}

export function writeFile(files, id, content) {
  return files.map((file) => (file.id === id ? { ...file, content } : file));
}

export function deleteFile(files, id) {
  return files.filter((file) => file.id !== id);
}

// Name lookup is scoped to a project because `@ad` is written inside one: the same name may exist
// elsewhere and must not be reachable from here.
export function findFile(files, projectId, name) {
  return filesOf(files, projectId).find((file) => file.name === name) ?? null;
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/files.test.js`
Beklenen: PASS — 12 test.

---

## Task 2: `files.js` — `@` anışları

**Files:**
- Modify: `prompt-chat/src/files.js`
- Test: `prompt-chat/src/files.test.js`

**Interfaces:**
- Consumes: `filesOf` (Task 1).
- Produces:
  - `mentionedFiles(text, projectFiles) -> string[]` — metinde geçen ve gerçekten var olan dosya
    adları, göründükleri sırayla, yinelenmeden
  - `activeMention(draft) -> string | null` — liste açıksa arama metni
  - `replaceActiveMention(draft, name) -> string`
  - `matchFiles(projectFiles, query) -> file[]`

- [ ] **Step 1: Write the failing test**

`files.test.js`'in sonuna ekle (üstteki `import` satırına da bu dördünü ekle):

```js
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
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/files.test.js`
Beklenen: FAIL — `mentionedFiles is not a function`.

- [ ] **Step 3: Write the implementation**

`files.js`'in sonuna ekle:

```js
// An @ followed by a whole file name is a call; an @ followed by anything else is ordinary text.
// The name must exist in the project, because @ turns up in prose and addresses all the time and
// treating every one as a call would raise false alarms on `@herkes` and `ali@example.com`.
export function mentionedFiles(text, projectFiles) {
  const names = new Set(projectFiles.map((file) => file.name));
  const found = [];
  for (const [, candidate] of text.matchAll(/@([^\s@]+)/g)) {
    if (names.has(candidate) && !found.includes(candidate)) found.push(candidate);
  }
  return found;
}

// The list belongs to the moment a name is being typed. Splitting on whitespace and looking at the
// last piece is enough for that, and it works mid-sentence because what you are typing is always
// the last piece. Moving the caret back into finished text does not reopen it — tracking the caret
// is more machinery than the gain is worth.
export function activeMention(draft) {
  const last = draft.split(/\s/).at(-1);
  return last && last.startsWith("@") ? last.slice(1) : null;
}

export function replaceActiveMention(draft, name) {
  return `${draft.slice(0, draft.lastIndexOf("@"))}@${name} `;
}

export function matchFiles(projectFiles, query) {
  const wanted = query.toLowerCase();
  return projectFiles.filter((file) => file.name.toLowerCase().includes(wanted));
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/files.test.js`
Beklenen: PASS — 28 test.

---

## Task 3: `projects.js` — proje işlemleri

**Files:**
- Create: `prompt-chat/src/projects.js`
- Test: `prompt-chat/src/projects.test.js`

**Interfaces:**
- Consumes: yok.
- Produces:
  - `createProject(projects, rawName) -> { projects, id }` — boş ad `"Yeni proje"` olur
  - `deleteProject(projects, id) -> project[]`
  - `projectContents(projectId, files, chats) -> { files: number, chats: number }`
  - Proje şekli: `{ id: number, name: string }`

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/projects.test.js` oluştur:

```js
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
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/projects.test.js`
Beklenen: FAIL — `Failed to resolve import "./projects.js"`.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/projects.js` oluştur:

```js
const PLACEHOLDER = "Yeni proje";

// A project's name is stored, not derived: unlike a chat title there is nothing in a project to
// derive it from, and the person who made it is the one who knows what it is for.
export function createProject(projects, rawName) {
  const name = rawName.trim() || PLACEHOLDER;
  const id = projects.reduce((max, project) => Math.max(max, project.id), 0) + 1;
  return { projects: [...projects, { id, name }], id };
}

export function deleteProject(projects, id) {
  return projects.filter((project) => project.id !== id);
}

// Deleting a project takes its files with it and cannot be undone, which is why the confirmation
// counts them out loud instead of asking "are you sure".
export function projectContents(projectId, files, chats) {
  return {
    files: files.filter((file) => file.projectId === projectId).length,
    chats: chats.filter((chat) => chat.projectId === projectId).length,
  };
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/projects.test.js`
Beklenen: PASS — 6 test.

---

## Task 4: `storage.js` — sohbetler projeye bağlanır

**Files:**
- Modify: `prompt-chat/src/storage.js`
- Modify: `prompt-chat/src/storage.test.js`

**Interfaces:**
- Consumes: yok.
- Produces:
  - `createChat(chats, projectId) -> { chats, id }` — yeni sohbet `projectId` taşır
  - `chatsOf(chats, projectId) -> chat[]`
  - `adoptOrphanChats(chats, projectId) -> chat[]` — `projectId`'si olmayanları verilene bağlar
  - `deleteChat` · `replaceMessages` · `setDraft` · `titleOf` değişmez

- [ ] **Step 1: Write the failing test**

`storage.test.js`'te `createChat` describe bloğunu bul ve içindeki çağrıları `createChat(chats, 1)`
olacak şekilde güncelle; yeni sohbetin `projectId: 1` taşıdığını iddia et. Sonra dosyanın sonuna
ekle:

```js
import { adoptOrphanChats, chatsOf } from "./storage.js";

describe("chatsOf", () => {
  it("keeps one project's chats out of another's", () => {
    const chats = [
      { id: 1, projectId: 1, messages: [], draft: "" },
      { id: 2, projectId: 2, messages: [], draft: "" },
    ];
    expect(chatsOf(chats, 1).map((c) => c.id)).toEqual([1]);
  });

  it("gives an empty list for a project with no chats", () => {
    expect(chatsOf([], 3)).toEqual([]);
  });
});

describe("adoptOrphanChats", () => {
  // Chats stored before projects existed have no projectId. They are adopted rather than dropped:
  // nothing a person typed disappears without them asking.
  it("attaches a chat with no project to the given one", () => {
    const chats = [{ id: 1, messages: [], draft: "" }];
    expect(adoptOrphanChats(chats, 5)[0].projectId).toBe(5);
  });

  it("leaves a chat that already belongs somewhere alone", () => {
    const chats = [{ id: 1, projectId: 2, messages: [], draft: "" }];
    expect(adoptOrphanChats(chats, 5)[0].projectId).toBe(2);
  });

  it("returns the very same array when there is nothing to adopt", () => {
    const chats = [{ id: 1, projectId: 2, messages: [], draft: "" }];
    // Identity matters: a new array every render would restart the effect that calls this.
    expect(adoptOrphanChats(chats, 5)).toBe(chats);
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/storage.test.js`
Beklenen: FAIL — `chatsOf is not a function`, ve `createChat` yeni sohbete `projectId` koymuyor.

- [ ] **Step 3: Write the implementation**

`storage.js`'te `createChat`'i değiştir ve iki fonksiyon ekle:

```js
export function createChat(chats, projectId) {
  const id = nextId(chats);
  return { chats: [...chats, { id, projectId, messages: [], draft: "" }], id };
}

export function chatsOf(chats, projectId) {
  return chats.filter((chat) => chat.projectId === projectId);
}

// Chats stored before projects existed carry no projectId. They are adopted, never dropped. The
// untouched array is returned as-is on purpose: the effect that calls this writes its result back
// to storage, and a fresh array every render would loop.
export function adoptOrphanChats(chats, projectId) {
  if (chats.every((chat) => chat.projectId !== undefined)) return chats;
  return chats.map((chat) =>
    chat.projectId === undefined ? { ...chat, projectId } : chat
  );
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/storage.test.js`
Beklenen: PASS.

---

## Task 5: `chat.js` — dosya açılımı

**Files:**
- Modify: `prompt-chat/src/chat.js`
- Modify: `prompt-chat/src/chat.test.js`
- Modify: `prompt-chat/src/api.js`
- Modify: `prompt-chat/src/api.test.js`

**Interfaces:**
- Consumes: `findSkill` (mevcut).
- Produces:
  - `toRequestBody(messages, model, skills = [], files = []) -> { model, messages }`
  - `sendChat({ key, model, messages, skills, files })`
  - Mesajdaki `files: string[]` alanı, `skill` ile aynı mantıkta açılır. Sıra: **skill gövdesi →
    dosya blokları → kullanıcının metni.** Bir dosya konuşmada yalnız **ilk anıldığı** yerde açılır.

- [ ] **Step 1: Write the failing test**

`chat.test.js`'in sonuna ekle:

```js
const DOSYALAR = [
  { id: 1, projectId: 1, name: "plan.md", content: "PLAN İÇERİĞİ" },
  { id: 2, projectId: 1, name: "sahneler.md", content: "SAHNE İÇERİĞİ" },
];

describe("toRequestBody with files", () => {
  it("puts the file content in front of what the user typed", () => {
    const body = toRequestBody(
      [{ role: "user", content: "@plan.md açıkla", files: ["plan.md"] }],
      "grok-4.3",
      [],
      DOSYALAR
    );
    expect(body.messages[1].content).toBe(
      "`@plan.md` dosyasının içeriği:\n---\nPLAN İÇERİĞİ\n---\n\n@plan.md açıkla"
    );
  });

  it("opens a file once in a conversation, at its first mention", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "@plan.md açıkla", files: ["plan.md"] },
        { role: "assistant", content: "şöyle" },
        { role: "user", content: "@plan.md ikinciyi de", files: ["plan.md"] },
      ],
      "grok-4.3",
      [],
      DOSYALAR
    );
    expect(body.messages[1].content).toContain("PLAN İÇERİĞİ");
    expect(body.messages[3]).toEqual({ role: "user", content: "@plan.md ikinciyi de" });
  });

  it("keeps two different files apart", () => {
    const body = toRequestBody(
      [{ role: "user", content: "iki", files: ["sahneler.md", "plan.md"] }],
      "grok-4.3",
      [],
      DOSYALAR
    );
    expect(body.messages[1].content.indexOf("SAHNE İÇERİĞİ")).toBeLessThan(
      body.messages[1].content.indexOf("PLAN İÇERİĞİ")
    );
  });

  it("sends the text alone when the named file was deleted", () => {
    const body = toRequestBody(
      [{ role: "user", content: "@silinmis.md ne", files: ["silinmis.md"] }],
      "grok-4.3",
      [],
      DOSYALAR
    );
    expect(body.messages[1]).toEqual({ role: "user", content: "@silinmis.md ne" });
  });

  it("puts the skill instruction before the file, and both before the request", () => {
    const body = toRequestBody(
      [{ role: "user", content: "yap", skill: "plan-yazma", files: ["plan.md"] }],
      "grok-4.3",
      [{ name: "plan-yazma", description: "Adımlara böler.", body: "PLAN TALİMATI" }],
      DOSYALAR
    );
    const sent = body.messages[1].content;
    expect(sent.indexOf("PLAN TALİMATI")).toBeLessThan(sent.indexOf("PLAN İÇERİĞİ"));
    expect(sent.indexOf("PLAN İÇERİĞİ")).toBeLessThan(sent.indexOf("yap"));
  });
});
```

`api.test.js`'in sonuna ekle:

```js
  it("expands a file mention before the request leaves", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({
      key: "k",
      model: "grok-4.3",
      messages: [{ role: "user", content: "@plan.md ne", files: ["plan.md"] }],
      files: [{ id: 1, projectId: 1, name: "plan.md", content: "PLAN İÇERİĞİ" }],
    });
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body).messages[1].content).toContain("PLAN İÇERİĞİ");
  });
```

- [ ] **Step 2: Run them and watch them fail**

Çalıştır: `cd prompt-chat && npx vitest run src/chat.test.js src/api.test.js`
Beklenen: FAIL — dosya bloğu eklenmiyor, içerik gitmiyor.

- [ ] **Step 3: Write the implementation**

`chat.js`'te `toRequestBody` ve `expand`'i değiştir:

```js
export function toRequestBody(messages, model, skills = [], files = []) {
  // One file opens once per conversation. Walking in order and remembering what has been opened
  // keeps the cost tied to how many files were used, not to how many times they were named.
  const opened = new Set();
  return {
    model,
    messages: [
      { role: "system", content: systemMessage(skills) },
      ...messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role, content: expand(m, skills, files, opened) })),
    ],
  };
}

// Instruction first, material second, request last: that is the order a person would put them in,
// and the model reads it the same way. Neither the skill nor the file is stored with the message —
// only their names are — so both are folded in here, on the way out.
function expand(message, skills, files, opened) {
  const parts = [];

  if (message.skill) {
    const skill = findSkill(skills, message.skill);
    if (skill) parts.push(skill.body);
  }

  for (const name of message.files ?? []) {
    if (opened.has(name)) continue;
    const file = files.find((f) => f.name === name);
    // A deleted file leaves the mention in the text and adds no block: an old chat must stay
    // sendable.
    if (!file) continue;
    opened.add(name);
    parts.push(`\`@${name}\` dosyasının içeriği:\n---\n${file.content}\n---`);
  }

  parts.push(message.content);
  return parts.join("\n\n");
}
```

`api.js`'te imzayı genişlet:

```js
export async function sendChat({ key, model, messages, skills = [], files = [] }) {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${key.trim()}`,
    },
    body: JSON.stringify(toRequestBody(messages, model.trim(), skills, files)),
  });
```

- [ ] **Step 4: Run them and watch them pass**

Çalıştır: `cd prompt-chat && npx vitest run src/chat.test.js src/api.test.js`
Beklenen: PASS.

---

## Task 6: `MentionPicker.jsx` — iki listenin ortak gövdesi

**Files:**
- Create: `prompt-chat/src/MentionPicker.jsx`
- Create: `prompt-chat/src/MentionPicker.test.jsx`
- Delete: `prompt-chat/src/SkillPicker.jsx`
- Delete: `prompt-chat/src/SkillPicker.test.jsx`
- Modify: `prompt-chat/src/app.css`

**Interfaces:**
- Consumes: yok — süzme çağıranın işi (`matchSkills` ya da `matchFiles`).
- Produces: `<MentionPicker prefix items onPick />`. `items`, `{ name, description? }` taşıyan
  **süzülmüş** bir dizidir; boşsa hiçbir şey çizilmez. `onPick(name)` çağrılır.

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/MentionPicker.test.jsx` oluştur:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import MentionPicker from "./MentionPicker.jsx";

const SKILLS = [
  { name: "netlestirme", description: "Soruları çıkarır." },
  { name: "plan-yazma", description: "Adımlara böler." },
];

describe("MentionPicker", () => {
  it("shows each item behind the prefix it is called with", () => {
    render(<MentionPicker prefix="/" items={SKILLS} onPick={() => {}} />);
    expect(screen.getByText("/plan-yazma")).toBeTruthy();
    expect(screen.getByText("Adımlara böler.")).toBeTruthy();
  });

  it("uses the same body for file mentions", () => {
    render(<MentionPicker prefix="@" items={[{ name: "plan.md" }]} onPick={() => {}} />);
    expect(screen.getByText("@plan.md")).toBeTruthy();
  });

  it("leaves out the description line when an item has none", () => {
    const { container } = render(
      <MentionPicker prefix="@" items={[{ name: "plan.md" }]} onPick={() => {}} />
    );
    expect(container.querySelector(".mention-desc")).toBeNull();
  });

  it("draws nothing at all for an empty list", () => {
    const { container } = render(<MentionPicker prefix="/" items={[]} onPick={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  it("hands the bare name to onPick, without the prefix", () => {
    const onPick = vi.fn();
    render(<MentionPicker prefix="@" items={[{ name: "plan.md" }]} onPick={onPick} />);
    fireEvent.click(screen.getByText("@plan.md"));
    expect(onPick).toHaveBeenCalledWith("plan.md");
  });
});
```

`SkillPicker.jsx` ve `SkillPicker.test.jsx` dosyalarını sil.

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/MentionPicker.test.jsx`
Beklenen: FAIL — `Failed to resolve import "./MentionPicker.jsx"`.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/MentionPicker.jsx` oluştur:

```jsx
// One body for both lists. `/` and `@` differ in where they are allowed and what they resolve to,
// but on screen they are the same thing: a list that appears while you type, narrows as you go,
// and writes its choice back into the draft. Filtering is the caller's job, so this file has no
// idea whether it is showing skills or files.
export default function MentionPicker({ prefix, items, onPick }) {
  if (items.length === 0) return null;

  return (
    <ul className="mention-picker">
      {items.map((item) => (
        <li key={item.name}>
          <button type="button" onClick={() => onPick(item.name)}>
            <span className="mention-name">
              {prefix}
              {item.name}
            </span>
            {item.description && <span className="mention-desc">{item.description}</span>}
          </button>
        </li>
      ))}
    </ul>
  );
}
```

`app.css`'te `.skill-picker`, `.skill-picker button`, `.skill-picker button:hover`,
`.skill-picker-name`, `.skill-picker-desc` seçicilerini sırasıyla `.mention-picker`,
`.mention-picker button`, `.mention-picker button:hover`, `.mention-name`, `.mention-desc` yap.
`.skill-picker, .skill-error { flex-basis: 100%; }` satırı `.mention-picker, .skill-error` olur.

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/MentionPicker.test.jsx`
Beklenen: PASS — 5 test.

---

## Task 7: `FileView.jsx` — sağdaki düzenleyici

**Files:**
- Create: `prompt-chat/src/FileView.jsx`
- Create: `prompt-chat/src/FileView.test.jsx`
- Modify: `prompt-chat/src/app.css`

**Interfaces:**
- Consumes: yok.
- Produces: `<FileView file onChange onClose />`. `onChange(content)` her tuşta çağrılır.

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/FileView.test.jsx` oluştur:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FileView from "./FileView.jsx";

const DOSYA = { id: 1, projectId: 1, name: "plan.md", content: "ilk satır" };

describe("FileView", () => {
  it("shows the name and the raw content", () => {
    render(<FileView file={DOSYA} onChange={() => {}} onClose={() => {}} />);
    expect(screen.getByText("plan.md")).toBeTruthy();
    expect(screen.getByRole("textbox").value).toBe("ilk satır");
  });

  it("reports every keystroke, because there is no save button", () => {
    const onChange = vi.fn();
    render(<FileView file={DOSYA} onChange={onChange} onClose={() => {}} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "yeni" } });
    expect(onChange).toHaveBeenCalledWith("yeni");
  });

  it("offers the file as a download link named after it", () => {
    render(<FileView file={DOSYA} onChange={() => {}} onClose={() => {}} />);
    const link = screen.getByText("İndir").closest("a");
    expect(link.getAttribute("download")).toBe("plan.md");
    expect(decodeURIComponent(link.getAttribute("href"))).toContain("ilk satır");
  });

  it("closes on the × without touching the content", () => {
    const onClose = vi.fn();
    const onChange = vi.fn();
    render(<FileView file={DOSYA} onChange={onChange} onClose={onClose} />);
    fireEvent.click(screen.getByRole("button", { name: "Dosyayı kapat" }));
    expect(onClose).toHaveBeenCalled();
    expect(onChange).not.toHaveBeenCalled();
  });

  it("copies the whole content", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    render(<FileView file={DOSYA} onChange={() => {}} onClose={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /Kopyala/ }));
    expect(await screen.findByRole("button", { name: "Kopyalandı" })).toBeTruthy();
    expect(writeText).toHaveBeenCalledWith("ilk satır");
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/FileView.test.jsx`
Beklenen: FAIL — `Failed to resolve import "./FileView.jsx"`.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/FileView.jsx` oluştur:

```jsx
import { useState } from "react";

// A data: URL rather than a Blob and an object URL: the browser needs no script to save this, the
// anchor does it on its own, and jsdom can read it back in a test.
function downloadHref(content) {
  return `data:text/markdown;charset=utf-8,${encodeURIComponent(content)}`;
}

export default function FileView({ file, onChange, onClose }) {
  const [label, setLabel] = useState("Kopyala");

  async function copy() {
    try {
      await navigator.clipboard.writeText(file.content);
      setLabel("Kopyalandı");
    } catch (err) {
      // Clipboard access needs a secure context. http://localhost is one, so this should not fire
      // in normal use; if it does, the browser's own reason is more useful than a guess.
      setLabel(`Kopyalanamadı: ${err.message}`);
    }
    setTimeout(() => setLabel("Kopyala"), 1500);
  }

  return (
    <aside className="file-view">
      <header>
        <span className="file-name">{file.name}</span>
        <a href={downloadHref(file.content)} download={file.name}>
          İndir
        </a>
        <button type="button" onClick={copy}>
          {label}
        </button>
        <button type="button" aria-label="Dosyayı kapat" onClick={onClose}>
          ×
        </button>
      </header>
      {/* Raw text, never rendered markdown: rendering means a markdown library, and this app has no
          dependencies to spend. You see what you wrote. */}
      <textarea value={file.content} onChange={(e) => onChange(e.target.value)} />
    </aside>
  );
}
```

`app.css`'in sonuna ekle:

```css
/* ---- file view ---- */

.file-view {
  display: flex;
  flex-direction: column;
  width: 420px;
  border-left: 1px solid var(--border);
  background: var(--bg-2);
}
.file-view header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}
.file-view .file-name {
  flex: 1;
  font: 13px "IBM Plex Mono", ui-monospace, monospace;
  color: var(--ink-2);
}
.file-view header a, .file-view header button {
  padding: 4px 8px;
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  background: none;
  color: var(--ink-3);
  font-size: 12px;
  text-decoration: none;
  cursor: pointer;
}
.file-view header a:hover, .file-view header button:hover {
  color: var(--ink);
  border-color: var(--border);
}
.file-view textarea {
  flex: 1;
  padding: 12px;
  border: 0;
  resize: none;
  background: var(--bg);
  color: var(--ink);
  font: 13px/1.7 "IBM Plex Mono", ui-monospace, monospace;
}
.file-view textarea:focus { outline: none; }
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/FileView.test.jsx`
Beklenen: PASS — 5 test.

---

## Task 8: `ProjectTree.jsx` — iki kademeli ağaç

**Files:**
- Create: `prompt-chat/src/ProjectTree.jsx`
- Create: `prompt-chat/src/ProjectTree.test.jsx`
- Modify: `prompt-chat/src/app.css`

**Interfaces:**
- Consumes: `filesOf` (Task 1), `chatsOf` · `titleOf` (Task 4 / mevcut), `projectContents` (Task 3).
- Produces: `<ProjectTree projects files chats active on />`
  - `active` = `{ projectId, chatId, fileId }`
  - `on` = `{ openProject, newProject, deleteProject, openFile, newFile, deleteFile, openChat, newChat, deleteChat }`

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/ProjectTree.test.jsx` oluştur:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ProjectTree from "./ProjectTree.jsx";

const PROJECTS = [
  { id: 1, name: "Kış çekimi" },
  { id: 2, name: "Yaz kampanyası" },
];
const FILES = [
  { id: 1, projectId: 1, name: "plan.md", content: "" },
  { id: 2, projectId: 2, name: "baska.md", content: "" },
];
const CHATS = [
  { id: 1, projectId: 1, messages: [{ role: "user", content: "kar manzarası" }], draft: "" },
  { id: 2, projectId: 2, messages: [], draft: "" },
];

function draw(overrides = {}) {
  const on = {
    openProject: vi.fn(), newProject: vi.fn(), deleteProject: vi.fn(),
    openFile: vi.fn(), newFile: vi.fn(), deleteFile: vi.fn(),
    openChat: vi.fn(), newChat: vi.fn(), deleteChat: vi.fn(),
    ...overrides,
  };
  render(
    <ProjectTree
      projects={PROJECTS}
      files={FILES}
      chats={CHATS}
      active={{ projectId: 1, chatId: 1, fileId: null }}
      on={on}
    />
  );
  return on;
}

describe("ProjectTree", () => {
  it("lists every project", () => {
    draw();
    expect(screen.getByText("Kış çekimi")).toBeTruthy();
    expect(screen.getByText("Yaz kampanyası")).toBeTruthy();
  });

  it("shows the open project's files and chats, and nobody else's", () => {
    draw();
    expect(screen.getByText("plan.md")).toBeTruthy();
    expect(screen.queryByText("baska.md")).toBeNull();
    expect(screen.getByText("kar manzarası")).toBeTruthy();
  });

  it("opens a project when its name is clicked", () => {
    const on = draw();
    fireEvent.click(screen.getByText("Yaz kampanyası"));
    expect(on.openProject).toHaveBeenCalledWith(2);
  });

  it("opens a file and a chat by their rows", () => {
    const on = draw();
    fireEvent.click(screen.getByText("plan.md"));
    expect(on.openFile).toHaveBeenCalledWith(1);
    fireEvent.click(screen.getByText("kar manzarası"));
    expect(on.openChat).toHaveBeenCalledWith(1);
  });

  it("names what a delete would take, so the two lists never mix up", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "plan.md dosyasını sil" }));
    expect(on.deleteFile).toHaveBeenCalledWith(1);
    fireEvent.click(screen.getByRole("button", { name: /kar manzarası sohbetini sil/ }));
    expect(on.deleteChat).toHaveBeenCalledWith(1);
  });

  it("counts out loud what deleting a project would cost", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "Kış çekimi projesini sil" }));
    expect(on.deleteProject).toHaveBeenCalledWith(1, { files: 1, chats: 1 });
  });

  it("offers a way to add each of the three", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: /Yeni proje/ }));
    fireEvent.click(screen.getByRole("button", { name: /Yeni dosya/ }));
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet/ }));
    expect(on.newProject).toHaveBeenCalled();
    expect(on.newFile).toHaveBeenCalled();
    expect(on.newChat).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/ProjectTree.test.jsx`
Beklenen: FAIL — `Failed to resolve import "./ProjectTree.jsx"`.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/ProjectTree.jsx` oluştur:

```jsx
import { filesOf } from "./files.js";
import { projectContents } from "./projects.js";
import { chatsOf, titleOf } from "./storage.js";

// Only the open project unfolds. Two projects' files on screen at once is exactly the confusion
// this two-level tree exists to prevent.
export default function ProjectTree({ projects, files, chats, active, on }) {
  return (
    <div className="tree">
      {projects.map((project) => {
        const open = project.id === active.projectId;
        return (
          <div key={project.id} className={open ? "project open" : "project"}>
            <div className="row">
              <button className="row-open" onClick={() => on.openProject(project.id)}>
                {open ? "▾" : "▸"} {project.name}
              </button>
              <button
                className="row-delete"
                aria-label={`${project.name} projesini sil`}
                onClick={() => on.deleteProject(project.id, projectContents(project.id, files, chats))}
              >
                ×
              </button>
            </div>

            {open && (
              <>
                <div className="group">dosyalar</div>
                {filesOf(files, project.id).map((file) => (
                  <div key={file.id} className={file.id === active.fileId ? "row active" : "row"}>
                    <button className="row-open" onClick={() => on.openFile(file.id)}>
                      {file.name}
                    </button>
                    <button
                      className="row-delete"
                      aria-label={`${file.name} dosyasını sil`}
                      onClick={() => on.deleteFile(file.id)}
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button className="add" onClick={on.newFile}>
                  + Yeni dosya
                </button>

                <div className="group">sohbetler</div>
                {chatsOf(chats, project.id).map((chat) => {
                  const title = titleOf(chat.messages);
                  return (
                    <div key={chat.id} className={chat.id === active.chatId ? "row active" : "row"}>
                      <button className="row-open" onClick={() => on.openChat(chat.id)}>
                        {title}
                      </button>
                      <button
                        className="row-delete"
                        aria-label={`${title} sohbetini sil`}
                        onClick={() => on.deleteChat(chat.id)}
                      >
                        ×
                      </button>
                    </div>
                  );
                })}
                <button className="add" onClick={on.newChat}>
                  + Yeni sohbet
                </button>
              </>
            )}
          </div>
        );
      })}

      <button className="add new-project" onClick={on.newProject}>
        + Yeni proje
      </button>
    </div>
  );
}
```

`app.css`'te `.chat-list`, `.chat-row`, `.chat-open`, `.chat-delete`, `.new-chat` seçicilerini
bul ve sırasıyla `.tree`, `.row`, `.row-open`, `.row-delete`, `.add` olarak yeniden adlandır
(kurallar aynen kalır). Sonra sonuna ekle:

```css
.project.open { padding-bottom: 6px; }
.group {
  padding: 8px 12px 2px;
  font-size: 11px;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--ink-3);
}
.project .row, .project .add { padding-left: 22px; }
.new-project { padding-left: 12px; }
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/ProjectTree.test.jsx`
Beklenen: PASS — 7 test.

---

## Task 9: `useWorkspace.js` ve `App.jsx` — hepsini bağla

**Files:**
- Create: `prompt-chat/src/useWorkspace.js`
- Modify: `prompt-chat/src/App.jsx`
- Modify: `prompt-chat/src/App.test.jsx`
- Modify: `prompt-chat/src/Sidebar.jsx`
- Modify: `prompt-chat/src/Sidebar.test.jsx`
- Modify: `prompt-chat/src/app.css`

**Interfaces:**
- Consumes: her şey.
- Produces: son davranış. `useWorkspace()` şunu döner:
  `{ projects, files, chats, project, chat, file, setProject, setChat, setFile, setProjects, setFiles, setChats }`
  — `project`/`chat`/`file` açık olan nesnelerdir, `file` `null` olabilir.

- [ ] **Step 1: Write the failing test**

`App.test.jsx`'in sonuna ekle. Var olan `withKey`, `write`, `composer`, `sendButton`, `inChat`
yardımcıları kullanılır; `vi.mock("./skillSource.js", …)` dosyanın başında zaten duruyor.

```jsx
const newFileButton = () => screen.getByRole("button", { name: /Yeni dosya/ });
const editor = () => document.querySelector(".file-view textarea");

describe("the workspace", () => {
  it("opens with one project so the screen is never empty", () => {
    withKey();
    render(<App />);
    expect(screen.getByText("Genel")).toBeTruthy();
    expect(composer()).toBeTruthy();
  });

  it("adopts a chat stored before projects existed", () => {
    withKey();
    localStorage.setItem(
      "chats",
      JSON.stringify([{ id: 1, messages: [{ role: "user", content: "eski mesaj" }], draft: "" }])
    );
    localStorage.setItem("active_chat", "1");
    render(<App />);
    expect(screen.getByText("eski mesaj")).toBeTruthy();
  });

  it("creates a file, names it, and opens it on the right", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    expect(screen.getByText("plan.md")).toBeTruthy();
    expect(editor()).toBeTruthy();
  });

  it("keeps what is typed into a file", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    fireEvent.change(editor(), { target: { value: "birinci madde" } });
    expect(editor().value).toBe("birinci madde");
  });

  it("refuses a second file with the same name and says why", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    fireEvent.click(newFileButton());
    expect(screen.getByText(/zaten var/)).toBeTruthy();
  });

  it("opens the file list on @ and writes the choice into the draft", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());

    write("bak şu @");
    fireEvent.click(screen.getByText("@plan.md"));
    expect(composer().value).toBe("bak şu @plan.md ");
  });

  it("sends the file content with the message", async () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    const fetchMock = vi.fn().mockResolvedValue(ok("okudum"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    fireEvent.click(newFileButton());
    fireEvent.change(editor(), { target: { value: "birinci madde" } });

    write("@plan.md ne yazıyor");
    fireEvent.click(sendButton());

    expect(await screen.findByText("okudum")).toBeTruthy();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1].content).toContain("birinci madde");
  });

  it("treats an @ that matches no file as ordinary text", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("tamam"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("@herkes bakabilir");
    fireEvent.click(sendButton());

    expect(await screen.findByText("tamam")).toBeTruthy();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1]).toEqual({ role: "user", content: "@herkes bakabilir" });
  });

  it("keeps one project's files away from another and closes the open file on the way", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    expect(editor()).toBeTruthy();

    vi.stubGlobal("prompt", vi.fn(() => "İkinci proje"));
    fireEvent.click(screen.getByRole("button", { name: /Yeni proje/ }));

    expect(screen.queryByText("plan.md")).toBeNull();
    expect(editor()).toBeNull();
  });

  it("says what deleting a project would cost before doing it", () => {
    withKey();
    const confirmMock = vi.fn(() => false);
    vi.stubGlobal("confirm", confirmMock);
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());

    fireEvent.click(screen.getByRole("button", { name: "Genel projesini sil" }));
    expect(confirmMock.mock.calls[0][0]).toMatch(/1 dosya/);
    expect(screen.getByText("Genel")).toBeTruthy();
  });
});
```

`Sidebar.test.jsx`'te sohbet listesine dayanan testler artık `ProjectTree`'nin işi. O testleri
sil; `Sidebar.test.jsx`'te yalnız ayarlar paneline (anahtar, model, bozuk skill listesi) ait olanlar
kalsın.

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/App.test.jsx`
Beklenen: FAIL — proje yok, "+ Yeni dosya" yok, düzenleyici yok.

- [ ] **Step 3: Write `useWorkspace.js`**

```js
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
  // here rather than guarded at every use.
  useEffect(() => {
    if (projects.length === 0) {
      const { projects: withOne, id } = createProject(projects, DEFAULT_PROJECT);
      setProjects(withOne);
      setProjectId(id);
      return;
    }

    const open = projects.some((p) => p.id === projectId) ? projectId : projects[0].id;
    if (open !== projectId) setProjectId(open);

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
    } else if (!mine.some((c) => c.id === chatId)) {
      setChatId(mine[0].id);
    }

    // An open file belonging to another project would make it unclear which project you are in.
    if (fileId !== null && !files.some((f) => f.id === fileId && f.projectId === open)) {
      setFileId(null);
    }
  }, [projects, chats, files, projectId, chatId, fileId,
      setProjects, setChats, setProjectId, setChatId, setFileId]);

  const project = projects.find((p) => p.id === projectId) ?? null;
  const chat = chats.find((c) => c.id === chatId) ?? null;
  const file = files.find((f) => f.id === fileId) ?? null;

  return {
    projects, files, chats, project, chat, file,
    setProjects, setFiles, setChats,
    setProject: setProjectId, setChat: setChatId, setFile: setFileId,
  };
}
```

- [ ] **Step 4: Rewrite `App.jsx`**

```jsx
import { useEffect, useRef, useState } from "react";
import Sidebar from "./Sidebar.jsx";
import Message from "./Message.jsx";
import MentionPicker from "./MentionPicker.jsx";
import FileView from "./FileView.jsx";
import { sendChat } from "./api.js";
import { usePersisted } from "./usePersisted.js";
import { useWorkspace } from "./useWorkspace.js";
import { chatsOf, deleteChat, createChat, replaceMessages, setDraft } from "./storage.js";
import { createProject, deleteProject } from "./projects.js";
import {
  activeMention, createFile, deleteFile, filesOf, matchFiles,
  mentionedFiles, replaceActiveMention, writeFile,
} from "./files.js";
import { skills } from "./skillSource.js";
import { findSkill, matchSkills, splitSkillPrefix } from "./skills.js";

const DEFAULT_MODEL = "grok-4.3";
const EMPTY_CHAT = { id: null, messages: [], draft: "" };

export default function App() {
  const [apiKey, setApiKey] = usePersisted("xai_key", "");
  const [model, setModel] = usePersisted("xai_model", DEFAULT_MODEL);
  const ws = useWorkspace();
  const [pending, setPending] = useState(false);
  const [notice, setNotice] = useState(null);
  const chatRef = useRef(null);

  const chat = ws.chat ?? EMPTY_CHAT;
  const projectId = ws.project?.id ?? null;
  const projectFiles = filesOf(ws.files, projectId);

  useEffect(() => {
    const el = chatRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [chat.messages]);

  async function send() {
    const typed = chat.draft.trim();
    if (!typed || pending) return;

    const { name, content } = splitSkillPrefix(typed);
    if (name && !findSkill(skills, name)) {
      setNotice(`"/${name}" bulunamadı. Mevcut skill'ler: ${skills.map((s) => `/${s.name}`).join(", ")}`);
      return;
    }
    if (!content) return;
    setNotice(null);

    // The reply belongs to the chat that asked for it, so its id is captured before the await.
    const askedIn = chat.id;
    const named = mentionedFiles(content, projectFiles);
    const question = { role: "user", content };
    if (name) question.skill = name;
    if (named.length > 0) question.files = named;
    const asked = [...chat.messages, question];

    ws.setChats((cs) => setDraft(replaceMessages(cs, askedIn, asked), askedIn, ""));
    setPending(true);
    try {
      const reply = await sendChat({
        key: apiKey, model, messages: asked, skills, files: projectFiles,
      });
      ws.setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "assistant", content: reply }])
      );
    } catch (err) {
      // Covers a non-200 response and a request that never left: network, CORS, unparsable body.
      ws.setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "error", content: err.message }])
      );
    }
    setPending(false);
  }

  // Two lists, one moment: a skill is called at the very start of a message, a file anywhere in it.
  const skillQuery = /^\/[A-Za-z0-9-]*$/.test(chat.draft) ? chat.draft.slice(1) : null;
  const fileQuery = skillQuery === null ? activeMention(chat.draft) : null;

  function writeDraft(text) {
    ws.setChats((cs) => setDraft(cs, chat.id, text));
  }

  function newProject() {
    const { projects, id } = createProject(ws.projects, window.prompt("Proje adı") ?? "");
    ws.setProjects(projects);
    ws.setProject(id);
    ws.setFile(null);
  }

  function removeProject(id, counts) {
    const project = ws.projects.find((p) => p.id === id);
    const question =
      `${project.name} — ${counts.files} dosya ve ${counts.chats} sohbet silinecek. Emin misin?`;
    if (!window.confirm(question)) return;
    ws.setFiles(ws.files.filter((f) => f.projectId !== id));
    ws.setChats(ws.chats.filter((c) => c.projectId !== id));
    ws.setProjects(deleteProject(ws.projects, id));
  }

  function newFile() {
    const asked = window.prompt("Dosya adı") ?? "";
    if (!asked.trim()) return;
    try {
      const { files, id } = createFile(ws.files, projectId, asked);
      ws.setFiles(files);
      ws.setFile(id);
      setNotice(null);
    } catch (err) {
      setNotice(err.message);
    }
  }

  function removeFile(id) {
    const file = ws.files.find((f) => f.id === id);
    if (!window.confirm(`${file.name} silinecek. Emin misin?`)) return;
    ws.setFiles(deleteFile(ws.files, id));
  }

  function removeChat(id) {
    if (!window.confirm("Bu sohbet silinecek. Emin misin?")) return;
    ws.setChats(deleteChat(ws.chats, id));
  }

  function newChat() {
    const { chats, id } = createChat(ws.chats, projectId);
    ws.setChats(chats);
    ws.setChat(id);
  }

  return (
    <div className="layout">
      <Sidebar
        projects={ws.projects}
        files={ws.files}
        chats={ws.chats}
        active={{ projectId, chatId: chat.id, fileId: ws.file?.id ?? null }}
        on={{
          openProject: (id) => { ws.setProject(id); ws.setFile(null); },
          newProject, deleteProject: removeProject,
          openFile: ws.setFile, newFile, deleteFile: removeFile,
          openChat: ws.setChat, newChat, deleteChat: removeChat,
        }}
        apiKey={apiKey}
        onApiKey={setApiKey}
        model={model}
        onModel={setModel}
      />

      <main className="main">
        <div className="chat" ref={chatRef}>
          {chat.messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} skill={m.skill} />
          ))}
        </div>

        <footer>
          {skillQuery !== null && (
            <MentionPicker
              prefix="/"
              items={matchSkills(skills, skillQuery)}
              onPick={(picked) => writeDraft(`/${picked} `)}
            />
          )}
          {fileQuery !== null && (
            <MentionPicker
              prefix="@"
              items={matchFiles(projectFiles, fileQuery)}
              onPick={(picked) => writeDraft(replaceActiveMention(chat.draft, picked))}
            />
          )}
          {notice && <div className="skill-error">{notice}</div>}
          <textarea
            placeholder="Mesaj yaz — Enter gönderir, Shift+Enter alt satıra geçer"
            value={chat.draft}
            onChange={(e) => writeDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
          />
          <button onClick={send} disabled={pending}>
            {pending ? "…" : "Gönder"}
          </button>
        </footer>
      </main>

      {ws.file && (
        <FileView
          file={ws.file}
          onChange={(content) => ws.setFiles(writeFile(ws.files, ws.file.id, content))}
          onClose={() => ws.setFile(null)}
        />
      )}
    </div>
  );
}
```

- [ ] **Step 5: Update `Sidebar.jsx`**

`Sidebar` artık sohbet listesini kendi çizmiyor; ağacı barındırıyor ve ayarları tutuyor. `chats`,
`activeId`, `onSelect`, `onNew`, `onDelete` prop'ları gider; yerine `projects`, `files`, `chats`,
`active`, `on` gelir. Gövdedeki `+ Yeni sohbet` düğmesi ve `<ul className="chat-list">` bloğu
`<ProjectTree … />` ile değişir; `titleOf` importu kalkar, `ProjectTree` importu gelir. Ayarlar
bölümü (`settingsOpen`, iki `input`, bozuk skill listesi) **aynen kalır**.

- [ ] **Step 6: Add the three-column layout**

`app.css`'te `.layout` kuralını bul ve üçüncü sütuna izin ver:

```css
.layout { display: flex; height: 100vh; }
.main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
```

- [ ] **Step 7: Run the whole suite**

Çalıştır: `cd prompt-chat && npm test`
Beklenen: PASS — hepsi yeşil, toplam bugünkü 120'nin belirgin şekilde üstünde.

---

## Self-review notları

**Spec kapsamı.** Beş "ne çalışır" maddesinin karşılığı: (1) proje aç → Task 3 + 8 + 9;
(2) dosya yaz → Task 1 + 7 + 9; (3) `@ad` ile çağır → Task 2 + 5 + 9; (4) dosya projeye ait →
Task 4 + `useWorkspace`; (5) dışarı çıkar → Task 7. Proje değişince açık dosyanın kapanması Task 9'un
`useWorkspace` etkisinde ve testi var. Silme onaylarının sayı söylemesi Task 8 + 9.

**Bilerek dışarıda bırakılan.** Ad sorma `window.prompt` ile yapılıyor — kendi kipimizi çizmek üç
bileşen ve bir odak tuzağı demek, iki alan için fazla. Sohbet silme onayı bugünkü `window.confirm`
kalıbını sürdürüyor, yani üç silme de aynı yerden soruyor.

**Doğrulanmamış varsayım yok.** `data:` URL ile indirme jsdom'da okunabildiği için Task 7'nin testi
bunu doğrudan sınıyor; `URL.createObjectURL` gerekmiyor.

**Riskli yer.** `useWorkspace`'in onarım etkisi altı duruma birden bakıyor ve kendi yazdığını geri
okuyor. Erken `return`'ler bu yüzden var: her tur en fazla bir şeyi onarır, böylece etki kendi
kendini tetikleyip dönmez. Task 9'daki "adopts a chat stored before projects existed" testi tam
bunu sınıyor.

**Commit.** Bu plan hiçbir görevde commit atmaz. Kullanıcı deneyip onayladıktan sonra tek commit:
`feat(prompt-chat): projects, files and @mentions`.
