# prompt-chat Sohbet Listesi Uygulama Planı

> **Uygulandı ve kapandı.** Bu belge yapılan işin kaydıdır; içindeki metin blokları o gün yazılan
> hâlleridir, bugünkü dosyalar değil. **Aracın tanımı sonradan düzeldi:** burada geçen "tezgâh" ve
> "bu araç düşer" ifadeleri yanlıştır. prompt-chat kullanılan ve kalan bir araçtır; Queen Editor'la
> birleştirmek bir seçenek, karar değil. Güncel tanım:
> [spec](../specs/2026-08-08-prompt-chat-sohbet-listesi-design.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tek sohbetlik tezgâhı, sohbetleri saklayan ve aralarında gezilen bir araca çevirmek; görünüşü Queen Editor'a yaklaştırmak.

**Architecture:** Sohbet listesi `localStorage`'da yaşar, saf liste işlemleri `storage.js`'te, okuma/yazma `usePersisted.js`'teki iki kancada. `Sidebar.jsx` sol kolonu çizer ve hiçbir şey saklamaz — aldığı geri çağrıları çağırır. `App.jsx` ikisini birleştirir, açık sohbeti seçer ve isteği yürütür. `chat.js`, `api.js`, `Message.jsx` hiç değişmez.

**Tech Stack:** React 18.3 + Vite 5.4 + Vitest 3.2 + jsdom + Testing Library (mevcut kurulum, yeni bağımlılık yok).

**Spec:** [2026-08-08-prompt-chat-sohbet-listesi-design.md](../specs/2026-08-08-prompt-chat-sohbet-listesi-design.md)
**Önceki spec:** [2026-08-08-prompt-chat-design.md](../specs/2026-08-08-prompt-chat-design.md) — backend yok, system prompt yok, ham hata metni, Kopyala kararları aynen geçerli.

## Global Constraints

- **Yeni bağımlılık yok.** `package.json` değişmez; her şey mevcut React/Vitest/Testing Library ile yazılır.
- **`storage.js` saftır:** `localStorage` yok, React yok, `fetch` yok. Her fonksiyon girdiyi değiştirmez, yeni liste döndürür.
- **`Sidebar.jsx` durum saklamaz** — tek istisnası ayarların açık/kapalı olması, ki o da ekrana ait bir şey.
- **Sohbetin adı saklanmaz**, `titleOf(messages)` ile türetilir.
- **`id` deterministiktir:** en büyük + 1, boş listede 1. `crypto` / `Math.random` / `Date.now` **kullanılmaz** — testler tarayıcısız ve tekrarlanabilir kalsın diye.
- **Uygulamada her zaman açık bir sohbet vardır.** Hiç sohbet yoksa ya da açık olan silinmişse uygulama kendi kurar/seçer.
- **Bozuk `localStorage` beyaz ekran vermez** — okunamayan JSON boş duruma düşer.
- **Aynı anda tek istek uçar;** cevap **isteği gönderen sohbete** yazılır, o an ekranda durana değil.
- **Taslak sohbete aittir** (`chat.draft`) ve `chats` ile birlikte saklanır.
- **Silme `window.confirm` ile onay ister.**
- **Dil ayrımı (repo kuralı):** kod yorumları ve commit mesajları **İngilizce**; ekranda görünen her metin ve test adları **Türkçe**.
- **`jest-dom` yok** — `expect(el.value).toBe(...)`, `expect(btn.disabled).toBe(true)` gibi düz DOM iddiaları.
- **Commit izni ayrıdır.** Commit adımları **kendiliğinden yetki değildir** — kullanıcı deneyip "commit et" diyene kadar hiçbir şey commit edilmez.

---

### Task 1: `storage.js` — saf sohbet mantığı

Listeyi değiştiren her işlem ve başlık türetimi. Ağ yok, React yok, tarayıcı yok.

**Files:**
- Create: `prompt-chat/src/storage.js`
- Test: `prompt-chat/src/storage.test.js`

**Interfaces:**
- Consumes: —
- Produces (sohbet kaydı: `{ id: number, messages: Array<{role, content}>, draft: string }`):
  - `nextId(chats)` → `number`
  - `createChat(chats)` → `{ chats: Array, id: number }`
  - `deleteChat(chats, id)` → `Array`
  - `replaceMessages(chats, id, messages)` → `Array`
  - `setDraft(chats, id, draft)` → `Array`
  - `titleOf(messages)` → `string`
  - Task 3 `titleOf`'u, Task 4 hepsini kullanır.

- [ ] **Step 1: Düşen testi yaz — `prompt-chat/src/storage.test.js`**

```js
import { describe, it, expect } from "vitest";
import { nextId, createChat, deleteChat, replaceMessages, setDraft, titleOf } from "./storage.js";

const chat = (id, messages = [], draft = "") => ({ id, messages, draft });

describe("nextId", () => {
  it("boş listede 1 verir", () => {
    expect(nextId([])).toBe(1);
  });

  it("en büyüğün bir fazlasını verir", () => {
    expect(nextId([chat(1), chat(4), chat(2)])).toBe(5);
  });
});

describe("createChat", () => {
  it("sonuna boş sohbet ekler ve id'sini söyler", () => {
    const { chats, id } = createChat([chat(1)]);
    expect(id).toBe(2);
    expect(chats).toHaveLength(2);
    expect(chats[1]).toEqual({ id: 2, messages: [], draft: "" });
  });

  it("verilen listeyi değiştirmez", () => {
    const before = [chat(1)];
    createChat(before);
    expect(before).toHaveLength(1);
  });
});

describe("deleteChat", () => {
  it("yalnız o sohbeti çıkarır", () => {
    const after = deleteChat([chat(1), chat(2), chat(3)], 2);
    expect(after.map((c) => c.id)).toEqual([1, 3]);
  });

  it("verilen listeyi değiştirmez", () => {
    const before = [chat(1), chat(2)];
    deleteChat(before, 1);
    expect(before).toHaveLength(2);
  });
});

describe("replaceMessages", () => {
  it("yalnız hedef sohbetin mesajlarını değiştirir", () => {
    const after = replaceMessages([chat(1), chat(2)], 2, [{ role: "user", content: "selam" }]);
    expect(after[0].messages).toEqual([]);
    expect(after[1].messages).toEqual([{ role: "user", content: "selam" }]);
  });

  it("taslağa dokunmaz", () => {
    const after = replaceMessages([chat(1, [], "yarım")], 1, [{ role: "user", content: "a" }]);
    expect(after[0].draft).toBe("yarım");
  });
});

describe("setDraft", () => {
  it("yalnız hedef sohbetin taslağını değiştirir", () => {
    const after = setDraft([chat(1, [], "a"), chat(2, [], "b")], 2, "yeni");
    expect(after[0].draft).toBe("a");
    expect(after[1].draft).toBe("yeni");
  });

  it("mesajlara dokunmaz", () => {
    const msgs = [{ role: "user", content: "selam" }];
    const after = setDraft([chat(1, msgs)], 1, "yarım");
    expect(after[0].messages).toBe(msgs);
  });
});

describe("titleOf", () => {
  it("hiç mesaj yoksa Yeni sohbet der", () => {
    expect(titleOf([])).toBe("Yeni sohbet");
  });

  it("yalnız cevap varsa da Yeni sohbet der", () => {
    expect(titleOf([{ role: "assistant", content: "merhaba" }])).toBe("Yeni sohbet");
  });

  it("kısa mesajı olduğu gibi verir", () => {
    expect(titleOf([{ role: "user", content: "kanlı dövüş" }])).toBe("kanlı dövüş");
  });

  it("uzun mesajı 40 karakterde kırpar ve … ekler", () => {
    const uzun = "a".repeat(60);
    const title = titleOf([{ role: "user", content: uzun }]);
    expect(title).toBe("a".repeat(40) + "…");
  });

  it("satır sonlarını boşluğa çevirir", () => {
    expect(titleOf([{ role: "user", content: "birinci\nikinci" }])).toBe("birinci ikinci");
  });

  it("ilk kullanıcı mesajını alır, sonrakini değil", () => {
    const title = titleOf([
      { role: "user", content: "ilk" },
      { role: "assistant", content: "cevap" },
      { role: "user", content: "ikinci" },
    ]);
    expect(title).toBe("ilk");
  });
});
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Failed to resolve import "./storage.js"`.

- [ ] **Step 3: `prompt-chat/src/storage.js`'i yaz**

```js
// A chat is { id, messages, draft }. Every function returns a new list and never mutates its input:
// React only re-renders on a changed reference, and a mutated list would also desync from what was
// last written to storage.

export function nextId(chats) {
  return chats.reduce((max, c) => Math.max(max, c.id), 0) + 1;
}

export function createChat(chats) {
  const id = nextId(chats);
  return { chats: [...chats, { id, messages: [], draft: "" }], id };
}

export function deleteChat(chats, id) {
  return chats.filter((c) => c.id !== id);
}

export function replaceMessages(chats, id, messages) {
  return chats.map((c) => (c.id === id ? { ...c, messages } : c));
}

export function setDraft(chats, id, draft) {
  return chats.map((c) => (c.id === id ? { ...c, draft } : c));
}

const TITLE_MAX = 40;

// The first user message is what actually tells two chats apart in this tool: it is either the WAN
// instruction or the scene brief.
export function titleOf(messages) {
  const first = messages.find((m) => m.role === "user");
  const line = first ? first.content.replace(/\s+/g, " ").trim() : "";
  if (!line) return "Yeni sohbet";
  return line.length > TITLE_MAX ? line.slice(0, TITLE_MAX) + "…" : line;
}
```

- [ ] **Step 4: Testin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 16 yeni test, toplam 44.

- [ ] **Step 5: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/storage.js prompt-chat/src/storage.test.js
git commit -m "feat(prompt-chat): chat list operations and title derivation"
```

---

### Task 2: `usePersisted.js` — kalıcılık kancaları

`App.jsx`'in içindeki kanca kendi dosyasına çıkar ve yanına JSON sürümü gelir. Bozuk kayıt beyaz ekran vermez.

**Files:**
- Create: `prompt-chat/src/usePersisted.js`
- Modify: `prompt-chat/src/App.jsx` — içindeki `usePersisted` tanımı silinir, import edilir
- Test: `prompt-chat/src/usePersisted.test.js`

**Interfaces:**
- Consumes: —
- Produces:
  - `usePersisted(storageKey, fallback)` → `[string, (v: string) => void]`
  - `usePersistedJson(storageKey, fallback)` → `[any, (v: any) => void]` — `setValue` React'in kendi ayarlayıcısıdır, fonksiyon biçimi (`setValue(prev => …)`) çalışır
  - Task 4 ikisini de kullanır.

- [ ] **Step 1: Düşen testi yaz — `prompt-chat/src/usePersisted.test.js`**

```js
import { renderHook, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { usePersisted, usePersistedJson } from "./usePersisted.js";

describe("usePersisted", () => {
  it("kayıt yoksa verilen varsayılanı döndürür", () => {
    const { result } = renderHook(() => usePersisted("k", "varsayilan"));
    expect(result.current[0]).toBe("varsayilan");
  });

  it("kayıtlı değeri okur", () => {
    localStorage.setItem("k", "kayitli");
    const { result } = renderHook(() => usePersisted("k", "varsayilan"));
    expect(result.current[0]).toBe("kayitli");
  });

  it("değişince localStorage'a yazar", () => {
    const { result } = renderHook(() => usePersisted("k", ""));
    act(() => result.current[1]("yeni"));
    expect(localStorage.getItem("k")).toBe("yeni");
  });
});

describe("usePersistedJson", () => {
  it("kayıtlı JSON'u çözer", () => {
    localStorage.setItem("liste", JSON.stringify([{ id: 1 }]));
    const { result } = renderHook(() => usePersistedJson("liste", []));
    expect(result.current[0]).toEqual([{ id: 1 }]);
  });

  it("bozuk JSON'da varsayılana düşer, patlamaz", () => {
    localStorage.setItem("liste", "{yarim");
    const { result } = renderHook(() => usePersistedJson("liste", []));
    expect(result.current[0]).toEqual([]);
  });

  it("değişince JSON olarak yazar", () => {
    const { result } = renderHook(() => usePersistedJson("liste", []));
    act(() => result.current[1]([{ id: 7 }]));
    expect(JSON.parse(localStorage.getItem("liste"))).toEqual([{ id: 7 }]);
  });

  it("fonksiyon biçimli güncellemeyi kabul eder", () => {
    const { result } = renderHook(() => usePersistedJson("liste", [1]));
    act(() => result.current[1]((prev) => [...prev, 2]));
    expect(result.current[0]).toEqual([1, 2]);
  });
});
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Failed to resolve import "./usePersisted.js"`.

- [ ] **Step 3: `prompt-chat/src/usePersisted.js`'i yaz**

```js
import { useEffect, useState } from "react";

// The key, the model name and the chats outlive the page; nothing else does.
export function usePersisted(storageKey, fallback) {
  const [value, setValue] = useState(() => localStorage.getItem(storageKey) ?? fallback);
  useEffect(() => {
    localStorage.setItem(storageKey, value);
  }, [storageKey, value]);
  return [value, setValue];
}

export function usePersistedJson(storageKey, fallback) {
  const [value, setValue] = useState(() => readJson(storageKey, fallback));
  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(value));
  }, [storageKey, value]);
  return [value, setValue];
}

// A hand-edited or half-written entry must not leave the user staring at a blank page: fall back to
// the empty state and let the app write a good one over it.
function readJson(storageKey, fallback) {
  const raw = localStorage.getItem(storageKey);
  if (raw === null) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}
```

- [ ] **Step 4: `App.jsx`'ten kanca tanımını çıkar**

`App.jsx`'in başındaki şu blok **silinir**:

```jsx
// The key and the model name outlive the page; the conversation deliberately does not.
function usePersisted(storageKey, fallback) {
  const [value, setValue] = useState(() => localStorage.getItem(storageKey) ?? fallback);
  useEffect(() => {
    localStorage.setItem(storageKey, value);
  }, [storageKey, value]);
  return [value, setValue];
}
```

ve import satırları şununla değiştirilir:

```jsx
import { useEffect, useRef, useState } from "react";
import Message from "./Message.jsx";
import { sendChat } from "./api.js";
import { usePersisted } from "./usePersisted.js";
```

- [ ] **Step 5: Testlerin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 7 yeni test, toplam 51. Mevcut `App.test.jsx` testleri de yeşil kalır (davranış değişmedi, kanca yer değiştirdi).

- [ ] **Step 6: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/usePersisted.js prompt-chat/src/usePersisted.test.js prompt-chat/src/App.jsx
git commit -m "feat(prompt-chat): persistence hooks with corrupt-JSON fallback"
```

---

### Task 3: `Sidebar.jsx` — sol kolon

Liste, **Yeni sohbet**, silme onayı ve açılır kapanır **Ayarlar**. Hiçbir şey saklamaz, aldığı geri çağrıları çağırır.

**Files:**
- Create: `prompt-chat/src/Sidebar.jsx`
- Test: `prompt-chat/src/Sidebar.test.jsx`

**Interfaces:**
- Consumes: Task 1'in `titleOf(messages)` fonksiyonu.
- Produces: `Sidebar` (default export). Props:
  `{ chats, activeId, onSelect(id), onNew(), onDelete(id), apiKey, onApiKey(value), model, onModel(value) }`.
  Task 4 bunu bağlar.

- [ ] **Step 1: Düşen testi yaz — `prompt-chat/src/Sidebar.test.jsx`**

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Sidebar from "./Sidebar.jsx";

const msg = (content) => ({ role: "user", content });

const chats = [
  { id: 1, messages: [msg("kanlı dövüş sahnesi")], draft: "" },
  { id: 2, messages: [], draft: "" },
];

function show(extra = {}) {
  const props = {
    chats,
    activeId: 1,
    onSelect: vi.fn(),
    onNew: vi.fn(),
    onDelete: vi.fn(),
    apiKey: "xai-123",
    onApiKey: vi.fn(),
    model: "grok-4.3",
    onModel: vi.fn(),
    ...extra,
  };
  render(<Sidebar {...props} />);
  return props;
}

describe("sohbet listesi", () => {
  it("sohbetleri adlarıyla çizer", () => {
    show();
    expect(screen.getByText("kanlı dövüş sahnesi")).toBeTruthy();
    expect(screen.getByText("Yeni sohbet")).toBeTruthy();
  });

  it("bir sohbete tıklayınca id'siyle haber verir", () => {
    const props = show();
    fireEvent.click(screen.getByText("Yeni sohbet"));
    expect(props.onSelect).toHaveBeenCalledWith(2);
  });

  it("Yeni sohbet düğmesi haber verir", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet ekle/ }));
    expect(props.onNew).toHaveBeenCalled();
  });
});

describe("silme", () => {
  // Every row has its own delete button, so the label has to name the chat -- a bare
  // /sohbetini sil/ would match both rows and the query would throw.
  const deleteFirst = () =>
    screen.getByRole("button", { name: "kanlı dövüş sahnesi sohbetini sil" });

  it("onaylanırsa siler", () => {
    vi.stubGlobal("confirm", vi.fn(() => true));
    const props = show();
    fireEvent.click(deleteFirst());
    expect(props.onDelete).toHaveBeenCalledWith(1);
  });

  it("iptal edilirse silmez", () => {
    vi.stubGlobal("confirm", vi.fn(() => false));
    const props = show();
    fireEvent.click(deleteFirst());
    expect(props.onDelete).not.toHaveBeenCalled();
  });

  it("silmeden önce sorar", () => {
    const ask = vi.fn(() => false);
    vi.stubGlobal("confirm", ask);
    show();
    fireEvent.click(deleteFirst());
    expect(ask).toHaveBeenCalled();
  });
});

describe("ayarlar", () => {
  it("anahtar kayıtlıysa kapalı gelir", () => {
    show();
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("anahtar yoksa açık gelir", () => {
    show({ apiKey: "" });
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();
  });

  it("düğme açıp kapatır", () => {
    show();
    fireEvent.click(screen.getByRole("button", { name: /Ayarlar/ }));
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: /Ayarlar/ }));
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("anahtar yazılınca haber verir", () => {
    const props = show({ apiKey: "" });
    fireEvent.change(screen.getByPlaceholderText("xAI API anahtarı"), {
      target: { value: "xai-yeni" },
    });
    expect(props.onApiKey).toHaveBeenCalledWith("xai-yeni");
  });

  it("model yazılınca haber verir", () => {
    const props = show({ apiKey: "" });
    fireEvent.change(screen.getByPlaceholderText("model"), { target: { value: "grok-5" } });
    expect(props.onModel).toHaveBeenCalledWith("grok-5");
  });

  it("anahtar ekranda okunmaz", () => {
    show({ apiKey: "" });
    expect(screen.getByPlaceholderText("xAI API anahtarı").type).toBe("password");
  });
});
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Failed to resolve import "./Sidebar.jsx"`.

- [ ] **Step 3: `prompt-chat/src/Sidebar.jsx`'i yaz**

```jsx
import { useState } from "react";
import { titleOf } from "./storage.js";

export default function Sidebar({
  chats,
  activeId,
  onSelect,
  onNew,
  onDelete,
  apiKey,
  onApiKey,
  model,
  onModel,
}) {
  // With no key there is nothing to do but enter one, so the panel opens itself on a first visit
  // and stays out of the way afterwards.
  const [settingsOpen, setSettingsOpen] = useState(() => apiKey === "");

  function remove(id) {
    if (window.confirm("Bu sohbet silinecek. Emin misin?")) onDelete(id);
  }

  return (
    <aside className="sidebar">
      <button className="new-chat" aria-label="Yeni sohbet ekle" onClick={onNew}>
        + Yeni sohbet
      </button>

      <ul className="chat-list">
        {chats.map((c) => {
          const title = titleOf(c.messages);
          return (
            <li key={c.id} className={c.id === activeId ? "chat-row active" : "chat-row"}>
              <button className="chat-open" onClick={() => onSelect(c.id)}>
                {title}
              </button>
              <button
                className="chat-delete"
                aria-label={`${title} sohbetini sil`}
                onClick={() => remove(c.id)}
              >
                ×
              </button>
            </li>
          );
        })}
      </ul>

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

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 12 yeni test, toplam 63.

- [ ] **Step 5: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/Sidebar.jsx prompt-chat/src/Sidebar.test.jsx
git commit -m "feat(prompt-chat): sidebar with chat list, delete confirm and settings panel"
```

---

### Task 4: `App.jsx` — sohbetleri bağla

Tek sohbetlik durum, sohbet listesine dönüşür: açık sohbet seçilir, taslak sohbete yazılır, cevap isteği gönderene düşer.

**Files:**
- Modify: `prompt-chat/src/App.jsx` — tamamı yeniden yazılır
- Test: `prompt-chat/src/App.test.jsx` — tamamı yeniden yazılır

**Interfaces:**
- Consumes: Task 1'in `createChat/deleteChat/replaceMessages/setDraft`, Task 2'nin `usePersisted/usePersistedJson`, Task 3'ün `Sidebar`, ve değişmeyen `sendChat({key, model, messages})` ile `Message({role, content})`.
- Produces: `App` (default export). Ekranda yeni CSS sınıfları: `.layout`, `.main`.

- [ ] **Step 1: Düşen testi yaz — `App.test.jsx`'in tamamını değiştir**

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App.jsx";

const ok = (content) => ({
  ok: true,
  status: 200,
  text: async () => JSON.stringify({ choices: [{ message: { content } }] }),
});

const composer = () => screen.getByPlaceholderText(/Mesaj yaz/);
const sendButton = () => screen.getByRole("button", { name: /Gönder|…/ });
const newChatButton = () => screen.getByRole("button", { name: /Yeni sohbet ekle/ });

function write(text) {
  fireEvent.change(composer(), { target: { value: text } });
}

// A stored key keeps the settings panel closed, which is the everyday state; tests that need the
// fields open leave it unset.
function withKey() {
  localStorage.setItem("xai_key", "xai-kayitli");
}

describe("açılış", () => {
  it("hiç sohbet yokken boş bir sohbetle açılır", () => {
    render(<App />);
    expect(composer().value).toBe("");
    expect(screen.getByText("Yeni sohbet")).toBeTruthy();
  });

  it("anahtar yoksa ayarlar açık gelir", () => {
    render(<App />);
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();
  });

  it("anahtar varsa ayarlar kapalı gelir", () => {
    withKey();
    render(<App />);
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("bozuk kayıt beyaz ekran vermez", () => {
    localStorage.setItem("chats", "{yarim");
    render(<App />);
    expect(composer()).toBeTruthy();
  });

  it("kayıtlı sohbetler geri gelir", () => {
    localStorage.setItem(
      "chats",
      JSON.stringify([{ id: 1, messages: [{ role: "user", content: "eski mesaj" }], draft: "" }])
    );
    localStorage.setItem("active_chat", "1");
    render(<App />);
    expect(screen.getByText("eski mesaj")).toBeTruthy();
  });
});

describe("sohbet gönderme", () => {
  it("mesaj açık sohbete yazılır ve cevap düşer", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("merhaba")).toBeTruthy();
    expect(screen.getByText("selam")).toBeTruthy();
  });

  it("hata, servisin kendi metniyle görünür", async () => {
    withKey();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 401, text: async () => "kim bu" })
    );
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("HTTP 401 — kim bu")).toBeTruthy();
  });

  it("cevap beklenirken gönderme kapalıdır", async () => {
    withKey();
    let release;
    const held = new Promise((resolve) => {
      release = resolve;
    });
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(held));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByRole("button", { name: "…" })).toBeTruthy();
    expect(sendButton().disabled).toBe(true);

    release(ok("merhaba"));
    await screen.findByText("merhaba");
    expect(sendButton().disabled).toBe(false);
  });

  it("boş mesaj gönderilmez", () => {
    withKey();
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    write("   ");
    fireEvent.click(sendButton());
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("Enter gönderir, Shift+Enter göndermez", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("merhaba"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("selam");
    fireEvent.keyDown(composer(), { key: "Enter", shiftKey: true });
    expect(fetchMock).not.toHaveBeenCalled();

    fireEvent.keyDown(composer(), { key: "Enter" });
    await screen.findByText("merhaba");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("hatadan sonra sohbet çalışmaya devam eder", async () => {
    withKey();
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({ ok: false, status: 500, text: async () => "patladı" })
        .mockResolvedValueOnce(ok("yine buradayım"))
    );
    render(<App />);

    write("bir");
    fireEvent.click(sendButton());
    await screen.findByText("HTTP 500 — patladı");

    write("iki");
    fireEvent.click(sendButton());
    expect(await screen.findByText("yine buradayım")).toBeTruthy();
  });

  it("kayıtlı anahtar isteğe gider", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("merhaba"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    await screen.findByText("merhaba");
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer xai-kayitli");
  });
});

describe("sohbetler arasında gezinme", () => {
  it("yeni sohbet boş açılır, eski listede kalır", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("kanlı dövüş");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    fireEvent.click(newChatButton());
    expect(screen.queryByText("merhaba")).toBeNull();
    expect(screen.getByText("kanlı dövüş")).toBeTruthy(); // listedeki başlık
  });

  it("eski sohbete dönünce mesajları geri gelir", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("kanlı dövüş");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    fireEvent.click(newChatButton());
    fireEvent.click(screen.getByText("kanlı dövüş"));
    expect(screen.getByText("merhaba")).toBeTruthy();
  });

  it("her sohbet kendi taslağını taşır", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);

    // The title comes from the messages, not from the draft. Without a sent message both rows would
    // read "Yeni sohbet" and there would be no way to click back to this one.
    write("ilk sohbet");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    write("yarım kalan metin");
    fireEvent.click(newChatButton());
    expect(composer().value).toBe("");

    fireEvent.click(screen.getByText("ilk sohbet"));
    expect(composer().value).toBe("yarım kalan metin");
  });

  it("gönderince o sohbetin taslağı boşalır", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    await screen.findByText("merhaba");
    expect(composer().value).toBe("");
  });

  it("beklerken sohbet değişse bile cevap isteyen sohbete düşer", async () => {
    withKey();
    let release;
    const held = new Promise((resolve) => {
      release = resolve;
    });
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(held));
    render(<App />);
    write("ilk sohbetin sorusu");
    fireEvent.click(sendButton());

    fireEvent.click(newChatButton());
    release(ok("ilk sohbete ait cevap"));

    // Ekranda duran yeni sohbete bulaşmadı...
    await screen.findByRole("button", { name: "Gönder" });
    expect(screen.queryByText("ilk sohbete ait cevap")).toBeNull();

    // ...isteyen sohbete yazıldı.
    fireEvent.click(screen.getByText("ilk sohbetin sorusu"));
    expect(screen.getByText("ilk sohbete ait cevap")).toBeTruthy();
  });
});

describe("silme", () => {
  it("silinen sohbet listeden gider", async () => {
    withKey();
    vi.stubGlobal("confirm", vi.fn(() => true));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("silinecek");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    fireEvent.click(newChatButton());
    fireEvent.click(screen.getByRole("button", { name: /silinecek sohbetini sil/ }));
    expect(screen.queryByText("silinecek")).toBeNull();
  });

  it("açık sohbet silinince ekran boş kalmaz", () => {
    withKey();
    vi.stubGlobal("confirm", vi.fn(() => true));
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet sohbetini sil/ }));
    expect(composer()).toBeTruthy();
  });
});
```

- [ ] **Step 2: Testlerin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Unable to find an accessible element with the role "button" and name /Yeni sohbet ekle/`.

- [ ] **Step 3: `App.jsx`'in tamamını değiştir**

```jsx
import { useEffect, useRef, useState } from "react";
import Sidebar from "./Sidebar.jsx";
import Message from "./Message.jsx";
import { sendChat } from "./api.js";
import { usePersisted, usePersistedJson } from "./usePersisted.js";
import { createChat, deleteChat, replaceMessages, setDraft } from "./storage.js";

const DEFAULT_MODEL = "grok-4.3";
const EMPTY = { id: null, messages: [], draft: "" };

export default function App() {
  const [apiKey, setApiKey] = usePersisted("xai_key", "");
  const [model, setModel] = usePersisted("xai_model", DEFAULT_MODEL);
  const [chats, setChats] = usePersistedJson("chats", []);
  const [activeId, setActiveId] = usePersistedJson("active_chat", null);
  const [pending, setPending] = useState(false);
  const chatRef = useRef(null);

  // There is never a moment without an open chat: not on a first visit, and not after the open one
  // is deleted. Both cases are repaired here rather than guarded at every use.
  useEffect(() => {
    if (chats.length === 0) {
      const { chats: withOne, id } = createChat(chats);
      setChats(withOne);
      setActiveId(id);
    } else if (!chats.some((c) => c.id === activeId)) {
      setActiveId(chats[0].id);
    }
  }, [chats, activeId, setChats, setActiveId]);

  const active = chats.find((c) => c.id === activeId) ?? chats[0] ?? EMPTY;

  useEffect(() => {
    const el = chatRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [active.messages]);

  async function send() {
    const text = active.draft.trim();
    if (!text || pending) return;

    // The reply belongs to the chat that asked for it, so its id is captured before the await: the
    // user may well be looking at a different chat by the time the answer lands.
    const askedIn = active.id;
    const asked = [...active.messages, { role: "user", content: text }];

    setChats((cs) => setDraft(replaceMessages(cs, askedIn, asked), askedIn, ""));
    setPending(true);
    try {
      const reply = await sendChat({ key: apiKey, model, messages: asked });
      setChats((cs) => replaceMessages(cs, askedIn, [...asked, { role: "assistant", content: reply }]));
    } catch (err) {
      // Covers a non-200 response and a request that never left: network, CORS, unparsable body.
      setChats((cs) => replaceMessages(cs, askedIn, [...asked, { role: "error", content: err.message }]));
    }
    setPending(false);
  }

  function newChat() {
    const { chats: next, id } = createChat(chats);
    setChats(next);
    setActiveId(id);
  }

  return (
    <div className="layout">
      <Sidebar
        chats={chats}
        activeId={active.id}
        onSelect={setActiveId}
        onNew={newChat}
        onDelete={(id) => setChats(deleteChat(chats, id))}
        apiKey={apiKey}
        onApiKey={setApiKey}
        model={model}
        onModel={setModel}
      />

      <main className="main">
        <div className="chat" ref={chatRef}>
          {active.messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} />
          ))}
        </div>

        <footer>
          <textarea
            placeholder="Mesaj yaz — Enter gönderir, Shift+Enter alt satıra geçer"
            value={active.draft}
            onChange={(e) => {
              const value = e.target.value;
              setChats((cs) => setDraft(cs, active.id, value));
            }}
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
    </div>
  );
}
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 19 test `App.test.jsx`'te, toplam 69.

- [ ] **Step 5: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/App.jsx prompt-chat/src/App.test.jsx
git commit -m "feat(prompt-chat): multiple chats with per-chat drafts and persisted history"
```

---

### Task 5: Görünüş — Queen Editor token'ları ve iki kolonlu yerleşim

Palet, tipografi ve sol kolonun CSS'i. Test yok: görülecek şey ekranda.

**Files:**
- Modify: `prompt-chat/index.html` — IBM Plex `<link>`
- Modify: `prompt-chat/src/app.css` — tamamı yeniden yazılır

**Interfaces:**
- Consumes: Task 3 ve 4'ün CSS sınıfları — `.layout`, `.sidebar`, `.new-chat`, `.chat-list`, `.chat-row`, `.chat-row.active`, `.chat-open`, `.chat-delete`, `.settings`, `.settings-body`, `.settings-toggle`, `.main`, `.chat`, `.msg`, `.role`, `.body`, `.copy`.
- Produces: —

- [ ] **Step 1: `index.html`'e yazı tipini ekle**

`<title>prompt-chat</title>` satırının altına:

```html
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

- [ ] **Step 2: `src/app.css`'in tamamını değiştir**

```css
/* Tokens copied from queen-editor/frontend/src/vendor/styles.css so the two tools read as one
   family. Only the tokens travel -- the component kit stays where it is. */
:root {
  --bg: #0f0f10;
  --bg-2: #17171a;
  --bg-3: #202024;
  --bg-hover: #1c1c1f;

  --border: #2b2b2f;
  --border-strong: #45454c;

  --ink: #ececee;
  --ink-2: #9a9aa0;
  --ink-3: #6a6a70;

  --accent: #a78bfa;
  --danger: #c97064;

  --r-sm: 4px;
  --r-md: 8px;
  --r-lg: 12px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 15px/1.6 "IBM Plex Sans", -apple-system, system-ui, sans-serif;
}

input, textarea, button {
  font: inherit;
  color: var(--ink);
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 8px 10px;
}
input:focus, textarea:focus { outline: 1px solid var(--accent); }

/* ---- layout ---- */

.layout { height: 100vh; display: flex; }

.sidebar {
  width: 260px;
  flex: 0 0 260px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: var(--bg-2);
  border-right: 1px solid var(--border);
}

.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }

/* ---- sidebar ---- */

.new-chat { cursor: pointer; text-align: left; }
.new-chat:hover { border-color: var(--border-strong); }

.chat-list {
  flex: 1;
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chat-row { display: flex; align-items: center; border-radius: var(--r-sm); }
.chat-row:hover { background: var(--bg-hover); }
.chat-row.active { background: var(--bg-3); }

.chat-open {
  flex: 1;
  min-width: 0;
  text-align: left;
  background: transparent;
  border: none;
  padding: 7px 8px;
  color: var(--ink-2);
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.chat-row.active .chat-open { color: var(--ink); }

/* Hidden until the row is hovered: a delete button on every row at all times reads as clutter and
   invites the misclick the confirm exists to catch. */
.chat-delete {
  visibility: hidden;
  background: transparent;
  border: none;
  padding: 4px 8px;
  color: var(--ink-3);
  cursor: pointer;
}
.chat-row:hover .chat-delete { visibility: visible; }
.chat-delete:hover { color: var(--danger); }

.settings { display: flex; flex-direction: column; gap: 8px; }
.settings-body { display: flex; flex-direction: column; gap: 8px; }
.settings-toggle {
  text-align: left;
  background: transparent;
  border: none;
  color: var(--ink-3);
  cursor: pointer;
  padding: 6px 8px;
}
.settings-toggle:hover { color: var(--ink-2); }

/* ---- chat ---- */

.chat {
  flex: 1;
  overflow-y: auto;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.msg { width: 100%; max-width: 720px; margin: 0 auto; }
.role {
  font-size: 11px;
  color: var(--ink-3);
  margin-bottom: 4px;
  letter-spacing: .02em;
}

/* Raw text: the copied prompt must match what the model wrote, line breaks included. */
.body {
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 10px 12px;
  border-radius: var(--r-md);
}
.user .body { background: var(--bg-2); border: 1px solid var(--border); }
.assistant .body { background: transparent; padding-left: 0; }
.error .body { color: var(--danger); border: 1px solid var(--danger); }

/* Overrides the shared button styling above -- this is a quiet link, not a control. */
.copy {
  margin-top: 6px;
  padding: 3px 8px;
  font-size: 12px;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  color: var(--ink-3);
  cursor: pointer;
}
.copy:hover { color: var(--ink); border-color: var(--border); }

/* ---- composer ---- */

footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border);
}
footer textarea { flex: 1; resize: none; height: 80px; background: var(--bg-2); }
footer button { min-width: 92px; cursor: pointer; }
footer button:hover:not(:disabled) { border-color: var(--border-strong); }
footer button:disabled { opacity: .5; cursor: default; }
```

- [ ] **Step 3: Testlerin hâlâ geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 67 test. CSS testleri etkilemez; bu adım yalnızca hiçbir şeyin kırılmadığını doğrular.

- [ ] **Step 4: Tarayıcı kontrolü**

Run: `cd prompt-chat && npm run dev`

Beklenen: solda 260px'lik koyu kolon, üstte **+ Yeni sohbet**, altta **⚙ Ayarlar**; sağda sohbet. Bir sohbet satırının üstüne gel → sağında `×` beliriyor, başka yerdeyken görünmüyor. Yazı tipi IBM Plex Sans.

- [ ] **Step 5: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/index.html prompt-chat/src/app.css
git commit -m "feat(prompt-chat): queen-editor palette, IBM Plex and two-column layout"
```

---

### Task 6: README ve CLAUDE.md — artık kalıcı

İki doküman da "hiçbir şey saklanmıyor" diyor. Bu artık **yanlış**; kod değişince onlar da değişir.

**Files:**
- Modify: `prompt-chat/README.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Task 1-5'in bitmiş uygulaması.
- Produces: —

- [ ] **Step 1: `README.md`'nin "Kullanım" bölümünü değiştir**

Şu blok:

```markdown
Enter gönderir, Shift+Enter alt satıra geçer. Her cevabın altındaki **Kopyala** metnin
tamamını panoya alır; oradan `api.ipynb`'nin `PROMPTS` listesine yapıştırırsın.

Sohbet bellekte durur: sayfayı yenilersen sıfırlanır. Anahtar ve model adı kalır.

System prompt yoktur — talimatını ilk mesaj olarak sen yapıştırırsın. Böylece talimatı
değiştirmek için kodu açman gerekmez; denenen şey modelin yanı sıra talimatın kendisi de.
```

şununla değiştirilir:

```markdown
Enter gönderir, Shift+Enter alt satıra geçer. Her cevabın altındaki **Kopyala** metnin
tamamını panoya alır; oradan `api.ipynb`'nin `PROMPTS` listesine yapıştırırsın.

Solda sohbet listesi var: **+ Yeni sohbet** bir tane açar, satırın üstüne gelince çıkan `×`
onay sorup siler. Sohbetler, hangisinde olduğun ve yarım bıraktığın metinler tarayıcının
`localStorage`'ında durur — sekmeyi kapatıp yarın açsan kaldığın yerdesin.

System prompt yoktur — talimatını ilk mesaj olarak sen yapıştırırsın. Talimatı bir kez
yazdığın sohbet durduğu için her denemede yeniden yapıştırman gerekmez: o sohbete dönüp
devam edersin. Denenen şey modelin yanı sıra talimatın kendisi de.

Anahtar ve model adı sol alttaki **⚙ Ayarlar** içinde. Anahtar kayıtlıyken kapalı gelir,
kayıtlı değilken kendiliğinden açılır.
```

- [ ] **Step 2: `README.md`'nin "Sınırlar" bölümünü değiştir**

Şu blok:

```markdown
Bu bir tezgâh, ürün değil: tek kullanıcı, `localhost`, kalıcılık yok, deploy yok.
`dist/` repo'ya girmez. Grok'un çıktısı yeterince iyiyse aynı mantık Queen Editor'ın içine
yazılır ve bu araç düşer.
```

şununla değiştirilir:

```markdown
Bu bir tezgâh, ürün değil: tek kullanıcı, `localhost`, deploy yok. `dist/` repo'ya girmez.

Kalıcılık tek tarayıcının `localStorage`'ıdır — sunucu yok, yedek yok, senkron yok. Tarayıcı
verisini silersen sohbetler gider. Silmenin geri alması da yok, onun için silme onay ister.
Cevap beklerken sayfayı kapatırsan mesajın kalır, cevap gelmez; tekrar gönderirsin.

Grok'un çıktısı yeterince iyiyse aynı mantık Queen Editor'ın içine yazılır ve bu araç düşer.
```

- [ ] **Step 3: `CLAUDE.md`'nin prompt-chat bölümünü güncelle**

Şu paragraf:

```markdown
**A bench, not a product.** One user, `localhost`, nothing persisted, never deployed. It shares no
code or folder with any other tool here. If Grok's output proves good enough, the same logic gets
written into Queen Editor and this tool goes away — which is why it uses Queen Editor's exact
frontend stack and versions (React 18.3 / Vite 5.4 / Vitest 3.2): that move should be a copy, not a
rewrite.
```

şununla değiştirilir:

```markdown
**A bench, not a product.** One user, `localhost`, never deployed. It shares no code or folder with
any other tool here. If Grok's output proves good enough, the same logic gets written into Queen
Editor and this tool goes away — which is why it borrows Queen Editor's exact frontend stack and
versions (React 18.3 / Vite 5.4 / Vitest 3.2) and its colour and type tokens: that move should be a
copy, not a rewrite. Only the tokens are borrowed — `vendor/kit` is not.

**The browser is the whole store.** Chats, which one is open, each chat's half-typed draft, the key
and the model all live in `localStorage` — no server, no backup, no sync. Clearing browser data
loses the chats, which is why deleting one asks for confirmation. A reply in flight when the page
closes is simply lost; nothing tries to resume it.
```

- [ ] **Step 4: `CLAUDE.md`'nin katman satırını güncelle**

Şu cümle:

```markdown
Layering: `chat.js` is pure (no network, no React), `api.js` holds the only `fetch`, `App.jsx` and
`Message.jsx` only render. `npm test` runs Vitest against jsdom with `fetch` stubbed. Design
decisions:
[docs/superpowers/specs/2026-08-08-prompt-chat-design.md](docs/superpowers/specs/2026-08-08-prompt-chat-design.md).
```

şununla değiştirilir:

```markdown
Layering: `chat.js` and `storage.js` are pure (no network, no React, no `localStorage`), `api.js`
holds the only `fetch`, `usePersisted.js` holds the only storage access, and `App.jsx` /
`Sidebar.jsx` / `Message.jsx` only render. `npm test` runs Vitest against jsdom with `fetch`
stubbed. Design decisions:
[the first spec](docs/superpowers/specs/2026-08-08-prompt-chat-design.md) and
[the chat list that superseded two of its decisions](docs/superpowers/specs/2026-08-08-prompt-chat-sohbet-listesi-design.md).
```

- [ ] **Step 5: Kontrol**

`prompt-chat/README.md`'yi baştan sona oku ve yazdığı her adımı sırayla uygula. Her cümle gerçekle uyuşuyor mu? Uyuşmayan varsa **README düzeltilir**, kod değil. `CLAUDE.md`'de artık "nothing persisted" geçmediğini ve linklerin çalıştığını doğrula.

- [ ] **Step 6: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/README.md CLAUDE.md
git commit -m "docs(prompt-chat): chats are persisted now"
```

---

## Bitince: spec'in elle doğrulama listesi

69 otomatik test yeşil olsa bile üç şeyi görmezler: gerçek ağ, gerçek pano, gerçek tarayıcı oturumu.
Spec'in [9. bölümündeki](../specs/2026-08-08-prompt-chat-sohbet-listesi-design.md) on madde baştan
sona geçilir. En kritik ikisi, çünkü ikisi de "kaybolan iş" ile ilgili:

- **9. madde:** A sohbetinde yarım metin yaz, B'ye geç, A'ya dön → metnin duruyor. Sekmeyi kapatıp
  aç → hâlâ duruyor.
- **7. madde:** açık olan sohbeti sil → ekran boş kalmıyor, başka bir sohbet açılıyor.
