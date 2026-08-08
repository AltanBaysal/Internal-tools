# prompt-chat — üç kolonlu yerleşim / uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sol kolondaki iki seviyeli ağacı üç kolona böl — solda seçili projenin sohbetleri, ortada
açık sohbet, sağda projenin dosyaları — ve dosyayı sağ kolonun içinde aç.

**Architecture:** Sadece çizim katmanı değişir. `ProjectTree.jsx` üç küçük liste bileşenine
(`ProjectList`, `ChatList`, `FileList`) bölünür. `Sidebar` sol kolonun iki hâli arasında geçiş
yapar, yeni `FilePane` sağ kolonunkini yapar. Hiçbir mantık dosyasına dokunulmaz.

**Tech Stack:** React 18, Vite 5.4, Vitest 3.2 + jsdom, `@testing-library/react` 16.3
(`jest-dom` **yok** — düz DOM iddiaları).

**Spec:** [2026-08-08-prompt-chat-uc-kolon-design.md](../specs/2026-08-08-prompt-chat-uc-kolon-design.md)

## Global Constraints

- **Mantık dosyalarına dokunulmaz.** `chat.js`, `files.js`, `skills.js`, `skillSource.js`,
  `storage.js`, `projects.js`, `useWorkspace.js`, `api.js`, `usePersisted.js` — hiçbiri
  değişmez. Bir tanesini değiştirmek gerekiyorsa **dur ve sor**.
- **Şu test dosyaları tek satır değişmeden geçer:** `chat.test.js`, `files.test.js`,
  `skills.test.js`, `skillSource.test.js`, `storage.test.js`, `projects.test.js`, `api.test.js`,
  `usePersisted.test.js`, `Message.test.jsx`, `MentionPicker.test.jsx`.
- **Dil:** ekranda görünen metin Türkçe; kod yorumları, docstring'ler ve **test adları** İngilizce.
- **Yorum NİYE'yi anlatır, NE'yi değil.** Geçmiş davranışa dair iddia (`# OLD:` / "eskiden") yasak.
- **Yeni bağımlılık yok.** `package.json` değişmez.
- **Bu metinler harfiyen korunur** (testler ve kas hafızası onlara bağlı):
  `+ Yeni proje`, `+ Yeni sohbet`, `+ Yeni dosya`, `Gönder`, `İndir`, `Kopyala`, `⚙ Ayarlar`,
  `xAI API anahtarı`, `model`, `Mesaj yaz — Enter gönderir, Shift+Enter alt satıra geçer`.
- **Bu `aria-label`'lar harfiyen korunur:** `${ad} projesini sil`, `${ad} dosyasını sil`,
  `${başlık} sohbetini sil`.
- **Sabit genişlikler:** sol kolon 260px, sağ kolon 300px, dosya açıkken sağ kolon 460px.
- **Her görevden sonra `cd prompt-chat && npm test` koşulur.** Kırmızıysa sonraki göreve geçilmez.
- **Commit yok.** Kullanıcı test edip "commit et" diyene kadar hiçbir görev commit atmaz.

---

## Dosya haritası

| Dosya | Durum | Sorumluluk |
|---|---|---|
| `src/ProjectList.jsx` | **yeni** | `PROJELER` etiketi, proje satırları, `+ Yeni proje` |
| `src/ChatList.jsx` | **yeni** | `SOHBETLER` etiketi, sohbet satırları, `+ Yeni sohbet` |
| `src/FileList.jsx` | **yeni** | `DOSYALAR` etiketi, dosya satırları, `+ Yeni dosya` |
| `src/FilePane.jsx` | **yeni** | Sağ kolon: liste hâli ↔ dosya hâli |
| `src/FileView.jsx` | değişir | Başlıkta `×` yerine `‹` geri oku; kök `aside` → `div` |
| `src/Sidebar.jsx` | değişir | Sol kolon: `‹ <proje>` başlığı, iki hâl, ayarlar |
| `src/App.jsx` | değişir | Üç kolonu bağlar |
| `src/app.css` | değişir | Üç kolonlu düzen; `.tree` / `.project-body` gider |
| `src/ProjectTree.jsx` | **silinir** | — |
| `src/ProjectTree.test.jsx` | **silinir** | Yerini üç yeni test dosyası alır |
| `src/useWorkspace.test.jsx` | **yeni** | Onarım davranışı `App.test.jsx`'ten buraya taşınır |

---

### Task 1: `ProjectList` — projeler hâlinin listesi

**Files:**
- Create: `prompt-chat/src/ProjectList.jsx`
- Test: `prompt-chat/src/ProjectList.test.jsx`

**Interfaces:**
- Consumes: `projectContents(projectId, files, chats)` from `./projects.js` → `{files, chats}`
- Produces: `<ProjectList projects files chats activeId on />` where
  `on = { openProject(id), newProject(), deleteProject(id, counts) }`

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/ProjectList.test.jsx`:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ProjectList from "./ProjectList.jsx";

const PROJECTS = [
  { id: 1, name: "Kış çekimi" },
  { id: 2, name: "Yaz kampanyası" },
];
const FILES = [{ id: 1, projectId: 1, name: "plan.md", content: "" }];
const CHATS = [{ id: 1, projectId: 1, messages: [], draft: "" }];

function draw() {
  const on = { openProject: vi.fn(), newProject: vi.fn(), deleteProject: vi.fn() };
  render(<ProjectList projects={PROJECTS} files={FILES} chats={CHATS} activeId={1} on={on} />);
  return on;
}

describe("ProjectList", () => {
  it("lists every project", () => {
    draw();
    expect(screen.getByText("Kış çekimi")).toBeTruthy();
    expect(screen.getByText("Yaz kampanyası")).toBeTruthy();
  });

  it("marks the open one so switching is a deliberate act", () => {
    draw();
    expect(screen.getByText("Kış çekimi").closest(".row").className).toContain("active");
    expect(screen.getByText("Yaz kampanyası").closest(".row").className).not.toContain("active");
  });

  it("opens a project by its name", () => {
    const on = draw();
    fireEvent.click(screen.getByText("Yaz kampanyası"));
    expect(on.openProject).toHaveBeenCalledWith(2);
  });

  it("counts out loud what deleting a project would cost", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "Kış çekimi projesini sil" }));
    expect(on.deleteProject).toHaveBeenCalledWith(1, { files: 1, chats: 1 });
  });

  it("offers a way to add one", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni proje" }));
    expect(on.newProject).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd prompt-chat && npx vitest run src/ProjectList.test.jsx`
Expected: FAIL — `Failed to resolve import "./ProjectList.jsx"`

- [ ] **Step 3: Write the component**

`prompt-chat/src/ProjectList.jsx`:

```jsx
import { projectContents } from "./projects.js";

// Reached only from the project header. Switching projects is rare next to picking a chat, so this
// list borrows the column instead of standing next to the one used all day.
export default function ProjectList({ projects, files, chats, activeId, on }) {
  return (
    <div className="list">
      <div className="group">projeler</div>
      {projects.map((project) => (
        <div key={project.id} className={project.id === activeId ? "row active" : "row"}>
          <button className="row-open" onClick={() => on.openProject(project.id)}>
            {project.name}
          </button>
          <button
            className="row-delete"
            aria-label={`${project.name} projesini sil`}
            onClick={() => on.deleteProject(project.id, projectContents(project.id, files, chats))}
          >
            ×
          </button>
        </div>
      ))}
      <button className="add" onClick={on.newProject}>
        + Yeni proje
      </button>
    </div>
  );
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `cd prompt-chat && npx vitest run src/ProjectList.test.jsx`
Expected: PASS — 5 tests

---

### Task 2: `ChatList` — sohbetler hâlinin listesi

**Files:**
- Create: `prompt-chat/src/ChatList.jsx`
- Test: `prompt-chat/src/ChatList.test.jsx`

**Interfaces:**
- Consumes: `chatsOf(chats, projectId)` and `titleOf(messages)` from `./storage.js`
- Produces: `<ChatList chats projectId activeId on />` where
  `on = { openChat(id), newChat(), deleteChat(id) }`

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/ChatList.test.jsx`:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ChatList from "./ChatList.jsx";

const CHATS = [
  { id: 1, projectId: 1, messages: [{ role: "user", content: "kar manzarası" }], draft: "" },
  { id: 2, projectId: 1, messages: [], draft: "" },
  { id: 3, projectId: 2, messages: [{ role: "user", content: "başka proje" }], draft: "" },
];

function draw() {
  const on = { openChat: vi.fn(), newChat: vi.fn(), deleteChat: vi.fn() };
  render(<ChatList chats={CHATS} projectId={1} activeId={1} on={on} />);
  return on;
}

describe("ChatList", () => {
  it("shows only the open project's chats", () => {
    draw();
    expect(screen.getByText("kar manzarası")).toBeTruthy();
    expect(screen.queryByText("başka proje")).toBeNull();
  });

  it("titles a chat that has no messages yet", () => {
    draw();
    expect(screen.getByText("Yeni sohbet")).toBeTruthy();
  });

  it("marks the open one", () => {
    draw();
    expect(screen.getByText("kar manzarası").closest(".row").className).toContain("active");
  });

  it("opens a chat by its title", () => {
    const on = draw();
    fireEvent.click(screen.getByText("kar manzarası"));
    expect(on.openChat).toHaveBeenCalledWith(1);
  });

  it("names the chat a delete would take", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "kar manzarası sohbetini sil" }));
    expect(on.deleteChat).toHaveBeenCalledWith(1);
  });

  it("offers a way to add one", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni sohbet" }));
    expect(on.newChat).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd prompt-chat && npx vitest run src/ChatList.test.jsx`
Expected: FAIL — `Failed to resolve import "./ChatList.jsx"`

- [ ] **Step 3: Write the component**

`prompt-chat/src/ChatList.jsx`:

```jsx
import { chatsOf, titleOf } from "./storage.js";

export default function ChatList({ chats, projectId, activeId, on }) {
  return (
    <div className="list">
      <div className="group">sohbetler</div>
      {chatsOf(chats, projectId).map((chat) => {
        const title = titleOf(chat.messages);
        return (
          <div key={chat.id} className={chat.id === activeId ? "row active" : "row"}>
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
    </div>
  );
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `cd prompt-chat && npx vitest run src/ChatList.test.jsx`
Expected: PASS — 6 tests

---

### Task 3: `FileList` — sağ kolonun liste hâli

**Files:**
- Create: `prompt-chat/src/FileList.jsx`
- Test: `prompt-chat/src/FileList.test.jsx`

**Interfaces:**
- Consumes: `filesOf(files, projectId)` from `./files.js`
- Produces: `<FileList files projectId on />` where
  `on = { openFile(id), newFile(), deleteFile(id) }`

`activeId` **yok**: bir dosya açıkken bu liste ekranda değildir, işaretleyecek satır kalmaz.

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/FileList.test.jsx`:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FileList from "./FileList.jsx";

const FILES = [
  { id: 1, projectId: 1, name: "plan.md", content: "" },
  { id: 2, projectId: 2, name: "baska.md", content: "" },
];

function draw() {
  const on = { openFile: vi.fn(), newFile: vi.fn(), deleteFile: vi.fn() };
  render(<FileList files={FILES} projectId={1} on={on} />);
  return on;
}

describe("FileList", () => {
  it("shows only the open project's files", () => {
    draw();
    expect(screen.getByText("plan.md")).toBeTruthy();
    expect(screen.queryByText("baska.md")).toBeNull();
  });

  it("opens a file by its name", () => {
    const on = draw();
    fireEvent.click(screen.getByText("plan.md"));
    expect(on.openFile).toHaveBeenCalledWith(1);
  });

  it("names the file a delete would take", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "plan.md dosyasını sil" }));
    expect(on.deleteFile).toHaveBeenCalledWith(1);
  });

  it("offers a way to add one", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni dosya" }));
    expect(on.newFile).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd prompt-chat && npx vitest run src/FileList.test.jsx`
Expected: FAIL — `Failed to resolve import "./FileList.jsx"`

- [ ] **Step 3: Write the component**

`prompt-chat/src/FileList.jsx`:

```jsx
import { filesOf } from "./files.js";

export default function FileList({ files, projectId, on }) {
  return (
    <div className="list">
      <div className="group">dosyalar</div>
      {filesOf(files, projectId).map((file) => (
        <div key={file.id} className="row">
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
    </div>
  );
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `cd prompt-chat && npx vitest run src/FileList.test.jsx`
Expected: PASS — 4 tests

---

### Task 4: `FileView` — `×` gider, `‹` gelir

**Files:**
- Modify: `prompt-chat/src/FileView.jsx`
- Modify: `prompt-chat/src/FileView.test.jsx`

**Interfaces:**
- Produces: `<FileView file onChange onBack />` — `onClose` prop'u **`onBack`** olur.

- [ ] **Step 1: Change the failing test**

`FileView.test.jsx` içinde `onClose` geçen **her** yeri `onBack` yap ve kapatma testini
şununla değiştir:

```jsx
  it("goes back to the list without touching the content", () => {
    const onBack = vi.fn();
    const onChange = vi.fn();
    render(<FileView file={DOSYA} onChange={onChange} onBack={onBack} />);
    fireEvent.click(screen.getByRole("button", { name: "Dosya listesine dön" }));
    expect(onBack).toHaveBeenCalled();
    expect(onChange).not.toHaveBeenCalled();
  });
```

Kalan dört testte yalnız prop adı değişir, örneğin:

```jsx
    render(<FileView file={DOSYA} onChange={() => {}} onBack={() => {}} />);
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd prompt-chat && npx vitest run src/FileView.test.jsx`
Expected: FAIL — `Unable to find an accessible element with the role "button" and name "Dosya listesine dön"`

- [ ] **Step 3: Change the component**

`FileView.jsx`'te **üç şey** değişir: prop adı `onClose` → `onBack`, kök `<aside>` → `<div>`, ve
başlıktaki `×` düğmesi başa geçip `‹` olur. Dosyanın geri kalanı — `downloadHref()` yardımcısı,
`useState("Kopyala")`, `copy()` fonksiyonunun gövdesi ve yorumu, `<textarea>` — **tek karakter
değişmeden yerinde kalır**:

```jsx
export default function FileView({ file, onChange, onBack }) {
  const [label, setLabel] = useState("Kopyala");

  async function copy() {
    // gövdesi olduğu gibi kalır
  }

  return (
    <div className="file-view">
      <header>
        <button type="button" className="back" aria-label="Dosya listesine dön" onClick={onBack}>
          ‹
        </button>
        <span className="file-name">{file.name}</span>
        <a href={downloadHref(file.content)} download={file.name}>
          İndir
        </a>
        <button type="button" onClick={copy}>
          {label}
        </button>
      </header>
      {/* Raw text, never rendered markdown: rendering means a markdown library, and this app has no
          dependencies to spend. You see what you wrote. */}
      <textarea value={file.content} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}
```

Kök `<aside>` → `<div>`: kolonu ve kenarlığı artık `FilePane` taşır (Task 6).
`.file-view` sınıf adı **korunur** — `App.test.jsx` düzenleyiciyi `.file-view textarea` ile buluyor.

- [ ] **Step 4: Run it and watch it pass**

Run: `cd prompt-chat && npx vitest run src/FileView.test.jsx`
Expected: PASS — 5 tests

---

### Task 5: `FilePane` — sağ kolonun iki hâli

**Files:**
- Create: `prompt-chat/src/FilePane.jsx`
- Test: `prompt-chat/src/FilePane.test.jsx`

**Interfaces:**
- Consumes: `FileList` (Task 3), `FileView` (Task 4)
- Produces: `<FilePane files projectId file on onChange />` where
  `on = { openFile(id), newFile(), deleteFile(id), closeFile() }`; `file` açık dosya nesnesi
  ya da `null`.

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/FilePane.test.jsx`:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FilePane from "./FilePane.jsx";

const FILES = [{ id: 1, projectId: 1, name: "plan.md", content: "ilk satır" }];

function draw(file = null) {
  const on = { openFile: vi.fn(), newFile: vi.fn(), deleteFile: vi.fn(), closeFile: vi.fn() };
  render(<FilePane files={FILES} projectId={1} file={file} on={on} onChange={vi.fn()} />);
  return on;
}

describe("FilePane", () => {
  it("shows the list when no file is open", () => {
    draw();
    expect(screen.getByRole("button", { name: "+ Yeni dosya" })).toBeTruthy();
    expect(document.querySelector("textarea")).toBeNull();
  });

  it("shows the open file in place of the list", () => {
    draw(FILES[0]);
    expect(screen.getByRole("textbox").value).toBe("ilk satır");
    expect(screen.queryByRole("button", { name: "+ Yeni dosya" })).toBeNull();
  });

  it("hands the back arrow through", () => {
    const on = draw(FILES[0]);
    fireEvent.click(screen.getByRole("button", { name: "Dosya listesine dön" }));
    expect(on.closeFile).toHaveBeenCalled();
  });

  it("widens only while a file is open", () => {
    const { unmount } = render(
      <FilePane files={FILES} projectId={1} file={null} on={{}} onChange={vi.fn()} />
    );
    expect(document.querySelector(".file-pane").className).not.toContain("open");
    unmount();

    render(
      <FilePane files={FILES} projectId={1} file={FILES[0]} on={{}} onChange={vi.fn()} />
    );
    expect(document.querySelector(".file-pane").className).toContain("open");
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd prompt-chat && npx vitest run src/FilePane.test.jsx`
Expected: FAIL — `Failed to resolve import "./FilePane.jsx"`

- [ ] **Step 3: Write the component**

`prompt-chat/src/FilePane.jsx`:

```jsx
import FileList from "./FileList.jsx";
import FileView from "./FileView.jsx";

// The list and the open file share one column. Giving them a column each would push the
// conversation off centre, and the conversation is what the tool is for.
export default function FilePane({ files, projectId, file, on, onChange }) {
  return (
    <aside className={file ? "file-pane open" : "file-pane"}>
      {file ? (
        <FileView file={file} onChange={onChange} onBack={on.closeFile} />
      ) : (
        <FileList files={files} projectId={projectId} on={on} />
      )}
    </aside>
  );
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `cd prompt-chat && npx vitest run src/FilePane.test.jsx`
Expected: PASS — 4 tests

---

### Task 6: `Sidebar` — proje başlığı ve iki hâl

**Files:**
- Modify: `prompt-chat/src/Sidebar.jsx`
- Modify: `prompt-chat/src/Sidebar.test.jsx`

**Interfaces:**
- Consumes: `ProjectList` (Task 1), `ChatList` (Task 2)
- Produces: `<Sidebar projects files chats active on apiKey onApiKey model onModel />` where
  `active = { projectId, chatId }` and
  `on = { openProject(id), newProject(), deleteProject(id, counts), openChat(id), newChat(), deleteChat(id) }`

`active.fileId` ve dosya geri çağrıları `Sidebar`'dan **çıkar** — onlar artık `FilePane`'in.

- [ ] **Step 1: Write the failing test**

`Sidebar.test.jsx`'teki `show()` yardımcısını sadeleştir (dosya geri çağrıları gider,
`projects` çok projeli olur):

```jsx
function show(extra = {}) {
  const props = {
    projects: [
      { id: 1, name: "Genel" },
      { id: 2, name: "Kampanya" },
    ],
    files: [],
    chats: [{ id: 1, projectId: 1, messages: [], draft: "" }],
    active: { projectId: 1, chatId: 1 },
    on: {
      openProject: vi.fn(), newProject: vi.fn(), deleteProject: vi.fn(),
      openChat: vi.fn(), newChat: vi.fn(), deleteChat: vi.fn(),
    },
    apiKey: "xai-123",
    onApiKey: vi.fn(),
    model: "grok-4.3",
    onModel: vi.fn(),
    ...extra,
  };
  render(<Sidebar {...props} />);
  return props;
}
```

`describe("the settings panel", ...)` bloğu **olduğu gibi kalır**. Sondaki
`describe("the tree", ...)` bloğunu tamamen şununla değiştir:

```jsx
describe("the two lists", () => {
  it("starts on the open project's chats, under its name", () => {
    show();
    expect(screen.getByRole("button", { name: "‹ Genel" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "+ Yeni sohbet" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "+ Yeni proje" })).toBeNull();
  });

  it("swaps to the project list when the name is clicked", () => {
    show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    expect(screen.getByRole("button", { name: "+ Yeni proje" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "+ Yeni sohbet" })).toBeNull();
  });

  it("comes back to the chats once a project is picked", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    fireEvent.click(screen.getByText("Kampanya"));
    expect(props.on.openProject).toHaveBeenCalledWith(2);
    expect(screen.getByRole("button", { name: "+ Yeni sohbet" })).toBeTruthy();
  });

  it("comes back to the chats after adding a project", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni proje" }));
    expect(props.on.newProject).toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "+ Yeni sohbet" })).toBeTruthy();
  });

  it("stays on the project list after a delete, so more can follow", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    fireEvent.click(screen.getByRole("button", { name: "Kampanya projesini sil" }));
    expect(props.on.deleteProject).toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "+ Yeni proje" })).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd prompt-chat && npx vitest run src/Sidebar.test.jsx`
Expected: FAIL — `Unable to find an accessible element with the role "button" and name "‹ Genel"`

- [ ] **Step 3: Rewrite the component**

`prompt-chat/src/Sidebar.jsx`:

```jsx
import { useState } from "react";
import ProjectList from "./ProjectList.jsx";
import ChatList from "./ChatList.jsx";
import { errors } from "./skillSource.js";

export default function Sidebar({
  projects,
  files,
  chats,
  active,
  on,
  apiKey,
  onApiKey,
  model,
  onModel,
}) {
  // With no key there is nothing to do but enter one, so the panel opens itself on a first visit
  // and stays out of the way afterwards.
  const [settingsOpen, setSettingsOpen] = useState(() => apiKey === "");
  // Which of the two lists the column is showing. Deliberately not persisted: a reload lands on the
  // open project's chats, which is where the work happens.
  const [browsing, setBrowsing] = useState(false);

  const project = projects.find((p) => p.id === active.projectId);

  return (
    <aside className="sidebar">
      {browsing ? (
        <ProjectList
          projects={projects}
          files={files}
          chats={chats}
          activeId={active.projectId}
          on={{
            // Picking or adding a project means you came here to change project, so the column goes
            // back to what you actually work in. Deleting does not: more may follow.
            openProject: (id) => {
              on.openProject(id);
              setBrowsing(false);
            },
            newProject: () => {
              on.newProject();
              setBrowsing(false);
            },
            deleteProject: on.deleteProject,
          }}
        />
      ) : (
        <>
          <button className="project-header" onClick={() => setBrowsing(true)}>
            ‹ {project?.name ?? ""}
          </button>
          <ChatList chats={chats} projectId={active.projectId} activeId={active.chatId} on={on} />
        </>
      )}

      <div className="settings">
        {settingsOpen && (
          <div className="settings-body">
            <input
              type="password"
              placeholder="xAI API anahtarı"
              autoComplete="off"
              value={apiKey}
              onChange={(e) => onApiKey(e.target.value)}
            />
            <input
              placeholder="model"
              autoComplete="off"
              value={model}
              onChange={(e) => onModel(e.target.value)}
            />
            {/* A skill that failed to load is invisible everywhere else — it simply is not in the
                list — so the one place a user could go looking is where it says why. */}
            {errors.length > 0 && (
              <ul className="skill-errors">
                {errors.map((e) => (
                  <li key={e.path}>
                    {e.path} — {e.reason}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
        <button className="settings-toggle" onClick={() => setSettingsOpen((v) => !v)}>
          ⚙ Ayarlar
        </button>
      </div>
    </aside>
  );
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `cd prompt-chat && npx vitest run src/Sidebar.test.jsx`
Expected: PASS — 11 tests (6 settings + 5 lists)

---

### Task 7: `App` — üç kolonu bağla, `ProjectTree`'yi kaldır

**Files:**
- Modify: `prompt-chat/src/App.jsx:144-219` (the returned JSX and the `on` objects)
- Modify: `prompt-chat/src/App.test.jsx`
- Delete: `prompt-chat/src/ProjectTree.jsx`
- Delete: `prompt-chat/src/ProjectTree.test.jsx`

**Interfaces:**
- Consumes: `Sidebar` (Task 6), `FilePane` (Task 5)
- Produces: `.layout` with exactly three children — `.sidebar`, `.main`, `.file-pane`

`App.jsx`'in `send()`, `writeDraft()`, `newProject()`, `removeProject()`, `newFile()`,
`removeFile()`, `removeChat()`, `newChat()`, `skillQuery` / `fileQuery` satırları
**hiç değişmez**. Sadece `import` satırı ve `return` bloğu değişir.

- [ ] **Step 1: Repair the failing tests**

`App.test.jsx`'te dört şey değişir.

**(a)** `inTree()` yardımcısı gider, yerine sağ kolonu kapsayan bir tane gelir:

```jsx
// A file's name is in the list and, when it is open, in the file view header — never both, but the
// pane is the thing the assertion means either way.
const inFiles = () => within(document.querySelector(".file-pane"));
```

**(b)** Projeler hâline girmek için yeni bir yardımcı — `+ Yeni proje` ve proje silme artık
orada:

```jsx
// Projects live behind the header button now, so a test that touches them opens that list first.
function browseProjects() {
  fireEvent.click(screen.getByRole("button", { name: /^‹/ }));
}
```

**(c)** `inTree()` kullanan iki yer `inFiles()` olur:

```jsx
  it("creates a file, names it, and opens it on the right", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    expect(inFiles().getByText("plan.md")).toBeTruthy();
    expect(editor()).toBeTruthy();
  });
```

```jsx
  it("keeps one project's files away from another and closes the open file on the way", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    expect(editor()).toBeTruthy();

    vi.stubGlobal("prompt", vi.fn(() => "İkinci proje"));
    browseProjects();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni proje" }));

    expect(inFiles().queryByText("plan.md")).toBeNull();
    expect(editor()).toBeNull();
  });
```

**(d)** Proje silme testi de listeyi önce açar:

```jsx
  it("says what deleting a project would cost before doing it", () => {
    withKey();
    const confirmMock = vi.fn(() => false);
    vi.stubGlobal("confirm", confirmMock);
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());

    browseProjects();
    fireEvent.click(screen.getByRole("button", { name: "Genel projesini sil" }));
    expect(confirmMock.mock.calls[0][0]).toMatch(/1 dosya/);
    expect(screen.getByText("Genel")).toBeTruthy();
  });
```

Son satır artık `getByText("Genel")` — silme iptal edilince proje listesi ekranda kaldığı için
ad tam olarak satırda geçer, başlıktaki `‹ Genel` görünmez.

**(e)** Yeni bir test: dosyanın sohbete değil projeye ait olduğunu kanıtlar. `describe("the
workspace")` içine, proje ayrımı testinin hemen üstüne:

```jsx
  it("keeps the open file open across a chat switch, because it belongs to the project", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    fireEvent.change(editor(), { target: { value: "birinci madde" } });

    fireEvent.click(newChatButton());

    expect(editor()).toBeTruthy();
    expect(editor().value).toBe("birinci madde");
  });
```

`describe("the workspace")` içindeki şu iki test **silinir**, çünkü Task 8 onları
`useWorkspace.test.jsx`'e taşıyor:
`"opens with one project so the screen is never empty"` ve
`"adopts a chat stored before projects existed"`.

- [ ] **Step 2: Run it and watch it fail**

Run: `cd prompt-chat && npx vitest run src/App.test.jsx`
Expected: FAIL — `.file-pane` yok, `browseProjects` bir düğme bulamıyor

- [ ] **Step 3: Rewrite the JSX**

`App.jsx`'in en üstündeki import bloğunda `FileView` yerine `FilePane`:

```jsx
import FilePane from "./FilePane.jsx";
```

`return` bloğu:

```jsx
  return (
    <div className="layout">
      <Sidebar
        projects={ws.projects}
        files={ws.files}
        chats={ws.chats}
        active={{ projectId, chatId: chat.id }}
        on={{
          openProject: (id) => {
            ws.setProject(id);
            ws.setFile(null);
          },
          newProject,
          deleteProject: removeProject,
          openChat: ws.setChat,
          newChat,
          deleteChat: removeChat,
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

      <FilePane
        files={ws.files}
        projectId={projectId}
        file={ws.file}
        on={{
          openFile: ws.setFile,
          newFile,
          deleteFile: removeFile,
          closeFile: () => ws.setFile(null),
        }}
        onChange={(content) => ws.setFiles(writeFile(ws.files, ws.file.id, content))}
      />
    </div>
  );
```

- [ ] **Step 4: Delete the tree**

```
prompt-chat/src/ProjectTree.jsx
prompt-chat/src/ProjectTree.test.jsx
```

- [ ] **Step 5: Run the whole suite**

Run: `cd prompt-chat && npm test`
Expected: PASS — tüm dosyalar yeşil. Kırmızı kalan varsa **Global Constraints**'teki
"değişmeden geçer" listesini kontrol et: o dosyalardan biri kırıldıysa yerleşim mantığa sızmıştır.

---

### Task 8: `useWorkspace`'in onarım davranışını kendi dosyasına taşı

**Files:**
- Create: `prompt-chat/src/useWorkspace.test.jsx`

`useWorkspace.js` **değişmez** — bu görev sadece bugüne kadar `App.test.jsx` içinde kazara
korunan davranışı kendi yerine koyar.

**Interfaces:**
- Consumes: `useWorkspace()` from `./useWorkspace.js` →
  `{ projects, files, chats, project, chat, file, setProjects, setFiles, setChats, setProject, setChat, setFile }`
- Consumes: `deleteChat(chats, id)` from `./storage.js`

- [ ] **Step 1: Write the test**

`prompt-chat/src/useWorkspace.test.jsx`:

```jsx
import { renderHook, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { useWorkspace } from "./useWorkspace.js";
import { deleteChat } from "./storage.js";

// Every one of these repairs used to be proved only through the whole App. On its own the hook says
// what it guarantees: there is always a project, always a chat in it, and never a stale id.
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

  it("opens another chat when the last one is deleted", () => {
    const { result } = renderHook(() => useWorkspace());
    const first = result.current.chat.id;
    act(() => {
      result.current.setChats(deleteChat(result.current.chats, first));
    });
    expect(result.current.chat).toBeTruthy();
    expect(result.current.chat.id).not.toBe(first);
  });

  it("closes a file belonging to a project that is not open", () => {
    localStorage.setItem(
      "projects",
      JSON.stringify([{ id: 1, name: "Genel" }, { id: 2, name: "Kampanya" }])
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
```

- [ ] **Step 2: Run it**

Run: `cd prompt-chat && npx vitest run src/useWorkspace.test.jsx`
Expected: PASS — 6 tests. `useWorkspace.js` zaten bunları yapıyor; test onları yerinde tutmak
için var.

Kırmızıysa sebep büyük ihtimalle etkinin bir turda yerleşmemesidir; iddiadan hemen önce
`act(() => {})` ile bir tur daha çevirmek yeter. **`useWorkspace.js`'i düzeltme.**

---

### Task 9: `app.css` — üç kolonlu düzen

**Files:**
- Modify: `prompt-chat/src/app.css`

Testler DOM'a bakar, CSS'e değil; bu görevin doğrulaması gözle yapılır.

- [ ] **Step 1: Replace the sidebar block's tree rules**

`.tree` bloğunu (satır 65-74) şununla değiştir:

```css
.list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
```

- [ ] **Step 2: Replace the folded-tree rules with the project header**

`.project-body` ve `.new-project` kurallarını (satır 116-122) sil, yerine:

```css
/* The open project's name doubles as the way back to the project list, so it reads as a control
   rather than a caption. */
.project-header {
  text-align: left;
  padding: 8px;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  color: var(--ink);
  cursor: pointer;
}
.project-header:hover { color: var(--accent); }
```

`.group` kuralının üstündeki yorumu da düzelt — girintili ağaç kalmadı:

```css
/* Says which of the two lists the column is showing. */
```

- [ ] **Step 3: Add the right column**

`/* ---- file view ---- */` başlığının hemen altına:

```css
.file-pane {
  flex: 0 0 300px;
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: var(--bg-2);
  border-left: 1px solid var(--border);
}

/* A markdown file cannot be written in 300px, and an idle list does not deserve 460. */
.file-pane.open {
  flex-basis: 460px;
  width: 460px;
  padding: 0;
  gap: 0;
}
```

- [ ] **Step 4: Shrink `.file-view` to fill its column**

`.file-view` kuralını (satır 241-247) şununla değiştir — genişlik ve kenarlık artık
`.file-pane`'in:

```css
.file-view {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
```

`.back` düğmesi zaten `.file-view header button` kuralından biçim alıyor; ek kural yok.

- [ ] **Step 5: Look at it**

Run: `cd prompt-chat && npm run dev` → `http://localhost:5173`

Gözle doğrula:
1. Üç kolon yan yana; solda `‹ Genel` + `SOHBETLER`, ortada sohbet, sağda `DOSYALAR`.
2. `‹ Genel`'e bas → sol kolon `PROJELER`'e döner, `+ Yeni proje` görünür.
3. Bir dosya aç → sağ kolon genişler, `‹` ile listeye döner.
4. Sohbet değiştir → açık dosya kapanmaz. Proje değiştir → kapanır.

---

## Toplu doğrulama

- [ ] `cd prompt-chat && npm test` — hepsi yeşil.
- [ ] Şu dosyalar `git diff` çıktısında **hiç geçmiyor**: `chat.js`, `files.js`, `skills.js`,
      `skillSource.js`, `storage.js`, `projects.js`, `useWorkspace.js`, `api.js`,
      `usePersisted.js`, `Message.jsx`, `MentionPicker.jsx`, `package.json` ve bunların testleri.
- [ ] `npx vite build` hatasız (üretilen `dist/` **silinir** — prompt-chat derleme çıktısı
      commit'lemez).
- [ ] Elle: spec'in **Doğrulama** bölümündeki 9 madde tek tek denenir.
- [ ] Commit **atılmaz**; kullanıcı tarayıcıda deneyip "commit et" diyene kadar beklenir.
