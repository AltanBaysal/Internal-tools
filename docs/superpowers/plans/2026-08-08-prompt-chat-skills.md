# prompt-chat Skill'leri — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** prompt-chat'e, repoda duran talimat dosyalarını mesaj başına `/ad` ile çağırma yeteneği
kazandırmak.

**Architecture:** Üç katman korunur. Ayrıştırma ve seçim mantığı saf katmanda (`skills.js`), Vite'ın
build-time glob'u tek bir io dosyasında (`skillSource.js`), açılım ise zaten var olan saf
`toRequestBody`'de yapılır — skill metni kayda hiç girmez, gönderilirken eklenir. Araç yok, döngü
yok, dosya yazma yok.

**Tech Stack:** React 18.3 · Vite 5.4 · Vitest 3.2 + jsdom · bağımlılık eklenmez (YAML ayrıştırıcı
dahil).

**Spec:** [2026-08-08-prompt-chat-skills-design.md](../specs/2026-08-08-prompt-chat-skills-design.md)

## Global Constraints

- **Yeni bağımlılık yok.** `package.json` değişmez. YAML için kütüphane kurulmaz; `SKILL.md`
  frontmatter'ının bilerek daraltılmış bir alt kümesi elle ayrıştırılır.
- **Katman kuralları (CODE-STANDARD):** `fetch` yalnız `api.js`'te, `localStorage` yalnız
  `usePersisted.js`'te. Saf katman ağ, React ve `localStorage` bilmez.
- **Dil:** kod yorumları, docstring'ler ve **test adları İngilizce**; ekranda görünen metin Türkçe.
- **`name` kuralı (agentskills.io):** 1-64 karakter, yalnız küçük harf, rakam ve tire; başta/sonda
  tire yok, arka arkaya iki tire yok; **klasör adıyla birebir aynı**.
- **`description` kuralı:** 1-1024 karakter, boş olamaz.
- **`dist/` commit edilmez** (bu araç Colab'a gitmiyor).
- **Commit yok** — kullanıcı deneyip onaylamadan hiçbir görev commit'lenmez. Aşağıdaki commit
  adımları o onaydan sonra, tek seferde uygulanır.

---

## Dosya yapısı

| Dosya | Sorumluluk | Durum |
|---|---|---|
| `prompt-chat/skills/netlestirme/SKILL.md` | Belirsiz isteği soruya çevirir | yeni |
| `prompt-chat/skills/plan-yazma/SKILL.md` | Hedefi adımlara böler | yeni |
| `src/skills.js` | **saf** — frontmatter ayrıştırma, doğrulama, arama, `/ad` ayıklama | yeni |
| `src/skillSource.js` | **io** — `import.meta.glob`, uygulamadaki tek build-time dosya okuma | yeni |
| `src/SkillPicker.jsx` | **ekran** — `/` yazınca açılan liste | yeni |
| `src/chat.js` | **saf** — sistem mesajı + skill açılımı | değişir |
| `src/api.js` | **io** — `skills`'i `toRequestBody`'ye taşır | değişir |
| `src/Message.jsx` | **ekran** — skill etiketi | değişir |
| `src/App.jsx` | **ekran** — ayıklama, hata, gönderme | değişir |
| `src/Sidebar.jsx` | **ekran** — bozuk skill'leri ayarlarda gösterir | değişir |
| `src/app.css` | etiket, liste ve hata biçimleri | değişir |

---

## Task 1: `skills.js` — frontmatter ayrıştırma

**Files:**
- Create: `prompt-chat/src/skills.js`
- Test: `prompt-chat/src/skills.test.js`

**Interfaces:**
- Consumes: yok (ilk görev).
- Produces: `parseSkill(raw) -> { name: string, description: string, body: string }`; geçersiz
  girdide `Error` fırlatır ve mesajı doğrudan ekrana basılacak Türkçe bir sebeptir.

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/skills.test.js` oluştur:

```js
import { describe, it, expect } from "vitest";
import { parseSkill } from "./skills.js";

const gecerli = `---
name: plan-yazma
description: Hedefi adımlara böler.
---

Hedefi uygulanabilir adımlara böl.
`;

describe("parseSkill", () => {
  it("reads the two required fields and the body", () => {
    expect(parseSkill(gecerli)).toEqual({
      name: "plan-yazma",
      description: "Hedefi adımlara böler.",
      body: "Hedefi uygulanabilir adımlara böl.",
    });
  });

  it("joins a description wrapped over several lines", () => {
    const raw = `---
name: netlestirme
description: Belirsiz bir isteği alır
             ve soruları çıkarır.
---
gövde`;
    expect(parseSkill(raw).description).toBe("Belirsiz bir isteği alır ve soruları çıkarır.");
  });

  it("ignores fields the app does not use", () => {
    const raw = `---
name: ornek
description: Bir şey yapar.
license: Apache-2.0
---
gövde`;
    expect(parseSkill(raw)).toEqual({ name: "ornek", description: "Bir şey yapar.", body: "gövde" });
  });

  it("keeps blank lines and markdown inside the body", () => {
    const raw = `---
name: ornek
description: Bir şey yapar.
---
## Başlık

- madde`;
    expect(parseSkill(raw).body).toBe("## Başlık\n\n- madde");
  });

  it("refuses a file that does not open with a frontmatter fence", () => {
    expect(() => parseSkill("name: ornek\n")).toThrow(/frontmatter yok/);
  });

  it("refuses a frontmatter that is never closed", () => {
    expect(() => parseSkill("---\nname: ornek\n")).toThrow(/kapanmamış/);
  });

  it("refuses a name with characters the standard forbids", () => {
    for (const kotu of ["Plan-Yazma", "-plan", "plan-", "plan--yazma", "plan yazma", ""]) {
      const raw = `---\nname: ${kotu}\ndescription: Bir şey.\n---\ngövde`;
      expect(() => parseSkill(raw)).toThrow(/geçersiz name/);
    }
  });

  it("refuses a name longer than 64 characters", () => {
    const raw = `---\nname: ${"a".repeat(65)}\ndescription: Bir şey.\n---\ngövde`;
    expect(() => parseSkill(raw)).toThrow(/geçersiz name/);
  });

  it("refuses a missing or oversized description", () => {
    expect(() => parseSkill("---\nname: ornek\n---\ngövde")).toThrow(/geçersiz description/);
    const uzun = `---\nname: ornek\ndescription: ${"a".repeat(1025)}\n---\ngövde`;
    expect(() => parseSkill(uzun)).toThrow(/geçersiz description/);
  });

  it("names the offending value in the error, so the settings panel can show it", () => {
    const raw = `---\nname: Plan\ndescription: Bir şey.\n---\ngövde`;
    expect(() => parseSkill(raw)).toThrow(/"Plan"/);
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/skills.test.js`
Beklenen: FAIL — `Failed to resolve import "./skills.js"`.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/skills.js` oluştur:

```js
// A deliberately narrow slice of YAML: `key: value` plus indented continuation lines. Skills are
// hand-written files with two fields that matter, and a real parser would be a dependency this app
// otherwise does not need.
const NAME_RULE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const NAME_MAX = 64;
const DESCRIPTION_MAX = 1024;

export function parseSkill(raw) {
  const lines = raw.split(/\r?\n/);
  if (lines[0].trim() !== "---") {
    throw new Error("frontmatter yok — dosya --- satırıyla başlamalı");
  }
  const end = lines.findIndex((line, i) => i > 0 && line.trim() === "---");
  if (end === -1) {
    throw new Error("frontmatter kapanmamış — ikinci --- satırı yok");
  }

  const fields = {};
  let current = null;
  for (const line of lines.slice(1, end)) {
    const opened = line.match(/^([A-Za-z][\w-]*):\s*(.*)$/);
    if (opened) {
      current = opened[1];
      fields[current] = opened[2].trim();
    } else if (current && /^\s+\S/.test(line)) {
      fields[current] = `${fields[current]} ${line.trim()}`.trim();
    }
  }

  const name = fields.name ?? "";
  const description = fields.description ?? "";

  if (!NAME_RULE.test(name) || name.length > NAME_MAX) {
    throw new Error(
      `geçersiz name: "${name}" — yalnız küçük harf, rakam ve tek tire, en fazla ${NAME_MAX} karakter`
    );
  }
  if (!description || description.length > DESCRIPTION_MAX) {
    throw new Error(
      `geçersiz description — 1-${DESCRIPTION_MAX} karakter olmalı, şu an ${description.length}`
    );
  }

  return { name, description, body: lines.slice(end + 1).join("\n").trim() };
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/skills.test.js`
Beklenen: PASS — 9 test.

---

## Task 2: `skills.js` — dosya listesini skill listesine çevirme

**Files:**
- Modify: `prompt-chat/src/skills.js`
- Test: `prompt-chat/src/skills.test.js`

**Interfaces:**
- Consumes: `parseSkill(raw)` (Task 1).
- Produces: `loadSkills(files) -> { skills: Array<{name, description, body}>, errors: Array<{path, reason}> }`.
  `files`, `{ "<yol>/<klasör>/SKILL.md": "<ham metin>" }` biçiminde bir nesnedir. `skills` ada göre
  sıralı döner.

- [ ] **Step 1: Write the failing test**

`skills.test.js`'in sonuna ekle:

```js
import { loadSkills } from "./skills.js";

const dosya = (name) => `---\nname: ${name}\ndescription: ${name} yapar.\n---\n${name} gövdesi`;

describe("loadSkills", () => {
  it("returns one skill per folder, sorted by name", () => {
    const { skills } = loadSkills({
      "../skills/plan-yazma/SKILL.md": dosya("plan-yazma"),
      "../skills/netlestirme/SKILL.md": dosya("netlestirme"),
    });
    expect(skills.map((s) => s.name)).toEqual(["netlestirme", "plan-yazma"]);
    expect(skills[0].body).toBe("netlestirme gövdesi");
  });

  it("rejects a skill whose name disagrees with its folder", () => {
    const { skills, errors } = loadSkills({
      "../skills/plan-yazma/SKILL.md": dosya("baska-ad"),
    });
    expect(skills).toEqual([]);
    expect(errors[0].path).toBe("../skills/plan-yazma/SKILL.md");
    expect(errors[0].reason).toMatch(/klasör adı/);
  });

  it("drops only the broken file and keeps the rest working", () => {
    const { skills, errors } = loadSkills({
      "../skills/bozuk/SKILL.md": "frontmatter'sız metin",
      "../skills/plan-yazma/SKILL.md": dosya("plan-yazma"),
    });
    expect(skills.map((s) => s.name)).toEqual(["plan-yazma"]);
    expect(errors).toHaveLength(1);
    expect(errors[0].reason).toMatch(/frontmatter yok/);
  });

  it("gives two empty lists when there are no files at all", () => {
    expect(loadSkills({})).toEqual({ skills: [], errors: [] });
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/skills.test.js`
Beklenen: FAIL — `loadSkills is not a function`.

- [ ] **Step 3: Write the implementation**

`skills.js`'in sonuna ekle:

```js
// The folder is the skill's identity, so a file whose `name` disagrees with it is rejected rather
// than silently renamed: the two would drift and `/ad` would stop matching what the reader sees.
export function loadSkills(files) {
  const skills = [];
  const errors = [];

  for (const path of Object.keys(files).sort()) {
    const folder = path.split("/").at(-2);
    try {
      const skill = parseSkill(files[path]);
      if (skill.name !== folder) {
        throw new Error(`name "${skill.name}", klasör adı "${folder}" ile aynı değil`);
      }
      skills.push(skill);
    } catch (err) {
      // One hand-written file must not take the whole list down with it.
      errors.push({ path, reason: err.message });
    }
  }

  skills.sort((a, b) => a.name.localeCompare(b.name));
  return { skills, errors };
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/skills.test.js`
Beklenen: PASS — 13 test.

---

## Task 3: `skills.js` — arama ve `/ad` ayıklama

**Files:**
- Modify: `prompt-chat/src/skills.js`
- Test: `prompt-chat/src/skills.test.js`

**Interfaces:**
- Consumes: yok.
- Produces:
  - `findSkill(skills, name) -> skill | null`
  - `matchSkills(skills, query) -> skill[]` — ada göre büyük/küçük harf duyarsız **içerir** eşleşmesi
  - `splitSkillPrefix(text) -> { name: string | null, content: string }`

- [ ] **Step 1: Write the failing test**

`skills.test.js`'in sonuna ekle:

```js
import { findSkill, matchSkills, splitSkillPrefix } from "./skills.js";

const LISTE = [
  { name: "netlestirme", description: "Soruları çıkarır.", body: "A" },
  { name: "plan-yazma", description: "Adımlara böler.", body: "B" },
];

describe("findSkill", () => {
  it("finds an exact name", () => {
    expect(findSkill(LISTE, "plan-yazma").body).toBe("B");
  });

  it("returns null rather than undefined for an unknown name", () => {
    expect(findSkill(LISTE, "yok")).toBeNull();
  });
});

describe("matchSkills", () => {
  it("lists everything for an empty query", () => {
    expect(matchSkills(LISTE, "")).toHaveLength(2);
  });

  it("matches anywhere in the name, not only at the start", () => {
    expect(matchSkills(LISTE, "yazma").map((s) => s.name)).toEqual(["plan-yazma"]);
  });

  it("ignores case", () => {
    expect(matchSkills(LISTE, "PLAN").map((s) => s.name)).toEqual(["plan-yazma"]);
  });

  it("returns an empty list when nothing matches", () => {
    expect(matchSkills(LISTE, "zzz")).toEqual([]);
  });
});

describe("splitSkillPrefix", () => {
  it("splits a leading slash name from the rest", () => {
    expect(splitSkillPrefix("/plan-yazma hafta sonu taşınacağım")).toEqual({
      name: "plan-yazma",
      content: "hafta sonu taşınacağım",
    });
  });

  it("accepts a newline between the name and the text", () => {
    expect(splitSkillPrefix("/plan-yazma\nilk satır\nikinci")).toEqual({
      name: "plan-yazma",
      content: "ilk satır\nikinci",
    });
  });

  it("reports an empty body when only the name was typed", () => {
    expect(splitSkillPrefix("/plan-yazma")).toEqual({ name: "plan-yazma", content: "" });
  });

  it("leaves a slash in the middle of the text alone", () => {
    const cumle = "src/App.jsx dosyasına bak";
    expect(splitSkillPrefix(cumle)).toEqual({ name: null, content: cumle });
  });

  it("leaves a date written with slashes alone", () => {
    expect(splitSkillPrefix("8/8/2026 tarihinde")).toEqual({
      name: null,
      content: "8/8/2026 tarihinde",
    });
  });

  it("still recognises a wrongly-cased name, so the caller can say it does not exist", () => {
    expect(splitSkillPrefix("/Plan-Yazma bir şey")).toEqual({
      name: "Plan-Yazma",
      content: "bir şey",
    });
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/skills.test.js`
Beklenen: FAIL — `findSkill is not a function`.

- [ ] **Step 3: Write the implementation**

`skills.js`'in sonuna ekle:

```js
export function findSkill(skills, name) {
  return skills.find((skill) => skill.name === name) ?? null;
}

// Contains rather than starts-with: with a handful of skills there is no ambiguity to protect
// against, and `/yazma` finding `plan-yazma` is what someone half-remembering a name would expect.
export function matchSkills(skills, query) {
  const wanted = query.toLowerCase();
  return skills.filter((skill) => skill.name.includes(wanted));
}

// Only a whole name at the very start counts as a call. A slash anywhere else is ordinary text —
// file paths and dates would otherwise be swallowed. Upper case is matched on purpose although the
// standard forbids it: the caller can then say "no such skill" instead of silently sending `/Plan`
// as prose.
const CALL = /^\/([A-Za-z0-9-]+)(?:\s+([\s\S]*))?$/;

export function splitSkillPrefix(text) {
  const called = text.match(CALL);
  if (!called) return { name: null, content: text };
  return { name: called[1], content: (called[2] ?? "").trim() };
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/skills.test.js`
Beklenen: PASS — 25 test.

---

## Task 4: İki skill dosyası ve build-time yükleme

**Files:**
- Create: `prompt-chat/skills/netlestirme/SKILL.md`
- Create: `prompt-chat/skills/plan-yazma/SKILL.md`
- Create: `prompt-chat/src/skillSource.js`
- Test: `prompt-chat/src/skillSource.test.js`

**Interfaces:**
- Consumes: `loadSkills(files)` (Task 2).
- Produces: `skills` ve `errors` — `skillSource.js`'ten adlandırılmış iki dışa aktarım. Uygulamanın
  geri kalanı skill listesini **yalnız buradan** alır.

- [ ] **Step 1: Write the two skill files**

`prompt-chat/skills/netlestirme/SKILL.md`:

```markdown
---
name: netlestirme
description: Belirsiz bir isteği alır ve işe başlamadan önce cevaplanması gereken soruları çıkarır. Kullanıcı ne istediğinden emin değilken, bir işe nereden başlayacağını bilmiyorken ya da "şunu netleştirelim" dediğinde kullanılır.
---

Kullanıcının istediği işi **yapma**. Önce eksik olanı sor.

1. İsteği oku ve ne yapılacağının belirsiz kaldığı yerleri bul.
2. En fazla 7 soru yaz, numaralı. Az soru iyi sorudur: cevabı işi değiştirmeyecek soruyu sorma.
3. Her sorunun altına, cevap gelmezse hangi varsayımla devam edeceğini tek satırda yaz.
4. Soruları önem sırasına koy — en üstteki, cevabı işi en çok değiştiren olsun.

Soruları yazdıktan sonra dur. Kullanıcı cevaplamadan işi yapmaya başlama.
```

`prompt-chat/skills/plan-yazma/SKILL.md`:

```markdown
---
name: plan-yazma
description: Bir hedefi numaralı ve uygulanabilir adımlara böler, her adımda neyin gerektiğini yazar. Kullanıcı bir işi nasıl yapacağını, hangi sırayla ilerleyeceğini sorduğunda ya da "plan çıkar" dediğinde kullanılır.
---

Hedefi uygulanabilir adımlara böl.

1. Önce tek cümleyle hedefi yaz: iş bittiğinde ne doğru olacak.
2. Adımları numarala. Her adım **tek bir eylem** olsun ve bittiğinin nasıl anlaşılacağını yazsın.
3. Her adımın altına gerekenleri koy: kimden hangi bilgi, hangi araç, hangi ön koşul.
4. Sırayı bağımlılığa göre kur. Bir adım öncekini beklemiyorsa bunu açıkça yaz — paralel yapılabilir.
5. En sona **Riskler** başlığı ekle: planı bozabilecek en fazla üç şey ve her biri için ne yapılacağı.

Bilmediğin yeri uydurma. "Bu bilgi eksik" diye yaz ve plana onu öğrenme adımı koy.
```

- [ ] **Step 2: Write the failing test**

`prompt-chat/src/skillSource.test.js` oluştur:

```js
import { describe, it, expect } from "vitest";
import { skills, errors } from "./skillSource.js";

// This is the one test that reads the real files in the repo rather than a fixture: it is the only
// way to catch a glob pattern that silently matches nothing, or a shipped skill that stopped being
// valid.
describe("the skills shipped with the app", () => {
  it("loads every folder under skills/ with no errors", () => {
    expect(errors).toEqual([]);
    expect(skills.length).toBeGreaterThanOrEqual(2);
  });

  it("ships netlestirme and plan-yazma", () => {
    expect(skills.map((s) => s.name)).toEqual(
      expect.arrayContaining(["netlestirme", "plan-yazma"])
    );
  });

  it("gives every shipped skill a body worth sending", () => {
    for (const skill of skills) {
      expect(skill.body.length).toBeGreaterThan(80);
    }
  });
});
```

- [ ] **Step 3: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/skillSource.test.js`
Beklenen: FAIL — `Failed to resolve import "./skillSource.js"`.

- [ ] **Step 4: Write the implementation**

`prompt-chat/src/skillSource.js` oluştur:

```js
import { loadSkills } from "./skills.js";

// Vite inlines every SKILL.md at build time, which is what lets a page with no backend read files
// that live in the repo. `eager` keeps it synchronous, so the list is ready before the first
// render and no screen needs a loading state.
const files = import.meta.glob("../skills/*/SKILL.md", {
  query: "?raw",
  import: "default",
  eager: true,
});

export const { skills, errors } = loadSkills(files);
```

- [ ] **Step 5: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/skillSource.test.js`
Beklenen: PASS — 3 test.

Boş liste hatası alırsan glob deseni tutmamıştır: `skillSource.js` `src/` altında, skill'ler
`prompt-chat/skills/` altında, yani desendeki `../` şart.

---

## Task 5: `chat.js` — sistem mesajı ve skill açılımı

**Files:**
- Modify: `prompt-chat/src/chat.js`
- Modify: `prompt-chat/src/chat.test.js`
- Modify: `prompt-chat/src/api.js`
- Modify: `prompt-chat/src/api.test.js`

**Interfaces:**
- Consumes: `findSkill(skills, name)` (Task 3).
- Produces:
  - `systemMessage(skills) -> string`
  - `toRequestBody(messages, model, skills = []) -> { model, messages }` — mesaj dizisinin başına
    `{ role: "system", content }` ekler; `user` mesajındaki `skill` alanını gövdeyle genişletir.
  - `sendChat({ key, model, messages, skills })` — `skills` isteğe bağlı, varsayılan `[]`.

- [ ] **Step 1: Write the failing test**

`chat.test.js`'te **var olan `toRequestBody` describe bloğunu tamamen şununla değiştir** (sistem
mesajı artık her istekte gittiği için eski iddialar geçerli değil; `formatHttpError` bloğuna
dokunma):

```js
import { toRequestBody, systemMessage, formatHttpError } from "./chat.js";

const SKILLS = [
  { name: "plan-yazma", description: "Adımlara böler.", body: "PLAN TALİMATI" },
  { name: "netlestirme", description: "Soruları çıkarır.", body: "SORU TALİMATI" },
];

describe("systemMessage", () => {
  it("asks for Turkish even when there is no skill at all", () => {
    expect(systemMessage([])).toMatch(/Türkçe/);
  });

  it("lists every skill by call name and description", () => {
    const text = systemMessage(SKILLS);
    expect(text).toContain("/plan-yazma: Adımlara böler.");
    expect(text).toContain("/netlestirme: Soruları çıkarır.");
  });

  it("keeps the instruction bodies out, so an unused skill costs nothing", () => {
    expect(systemMessage(SKILLS)).not.toContain("PLAN TALİMATI");
  });
});

describe("toRequestBody", () => {
  it("carries the model and puts the system message first", () => {
    const body = toRequestBody([{ role: "user", content: "selam" }], "grok-4.3");
    expect(body.model).toBe("grok-4.3");
    expect(body.messages[0].role).toBe("system");
    expect(body.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("leaves error rows out", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "selam" },
        { role: "error", content: "HTTP 401 — nope" },
        { role: "assistant", content: "merhaba" },
      ],
      "grok-4.3"
    );
    expect(body.messages.slice(1)).toEqual([
      { role: "user", content: "selam" },
      { role: "assistant", content: "merhaba" },
    ]);
  });

  it("does not send fields the screen added", () => {
    const body = toRequestBody([{ role: "user", content: "selam", copied: true }], "grok-4.3");
    expect(body.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("sends only the system message for an empty chat", () => {
    const body = toRequestBody([], "grok-4.3");
    expect(body.messages).toHaveLength(1);
    expect(body.messages[0].role).toBe("system");
  });

  it("folds the skill body in front of what the user typed", () => {
    const body = toRequestBody(
      [{ role: "user", content: "taşınacağım", skill: "plan-yazma" }],
      "grok-4.3",
      SKILLS
    );
    expect(body.messages[1]).toEqual({
      role: "user",
      content: "PLAN TALİMATI\n\ntaşınacağım",
    });
  });

  it("keeps an earlier skill call in the transcript, so the instruction accumulates", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "taşınacağım", skill: "plan-yazma" },
        { role: "assistant", content: "1. kutu bul" },
        { role: "user", content: "ikinciyi açıkla" },
      ],
      "grok-4.3",
      SKILLS
    );
    expect(body.messages[1].content).toContain("PLAN TALİMATI");
    expect(body.messages[3]).toEqual({ role: "user", content: "ikinciyi açıkla" });
  });

  it("sends the user's own words alone when the named skill no longer exists", () => {
    const body = toRequestBody(
      [{ role: "user", content: "taşınacağım", skill: "silinmis" }],
      "grok-4.3",
      SKILLS
    );
    expect(body.messages[1]).toEqual({ role: "user", content: "taşınacağım" });
  });
});
```

`api.test.js`'te iki testi güncelle — gövde artık sistem mesajı taşıyor:

```js
  it("puts the model and the messages in the body", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({
      key: "k",
      model: " grok-4.3 ",
      messages: [{ role: "user", content: "selam" }],
    });
    const [, init] = fetchMock.mock.calls[0];
    const body = JSON.parse(init.body);
    expect(body.model).toBe("grok-4.3");
    expect(body.messages[0].role).toBe("system");
    expect(body.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("expands a skill call before the request leaves", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({
      key: "k",
      model: "grok-4.3",
      messages: [{ role: "user", content: "taşınacağım", skill: "plan-yazma" }],
      skills: [{ name: "plan-yazma", description: "Adımlara böler.", body: "PLAN TALİMATI" }],
    });
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body).messages[1].content).toBe("PLAN TALİMATI\n\ntaşınacağım");
  });
```

- [ ] **Step 2: Run them and watch them fail**

Çalıştır: `cd prompt-chat && npx vitest run src/chat.test.js src/api.test.js`
Beklenen: FAIL — `systemMessage is not a function`, ve `messages[0].role` `"user"` geliyor.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/chat.js`'i tamamen değiştir:

```js
import { findSkill } from "./skills.js";

const TURKISH = "Kullanıcıyla Türkçe konuş.";

// The model is told what exists, never what each one says: a skill's instructions arrive only when
// the user calls it, so ten unused skills cost about ten lines instead of ten documents. Knowing
// the list is what lets it answer "bunun için /plan-yazma kullanabilirsin".
export function systemMessage(skills) {
  if (skills.length === 0) return TURKISH;
  const list = skills.map((skill) => `- /${skill.name}: ${skill.description}`).join("\n");
  return `${TURKISH}\n\nKullanıcı mesajının başına /ad yazarak şu skill'lerden birini çağırabilir:\n${list}`;
}

// The screen keeps error rows so the user can see what happened, but xAI rejects any role it does
// not know, so they are dropped on the way out. Only role and content travel: anything the screen
// adds to a message stays on the screen.
export function toRequestBody(messages, model, skills = []) {
  return {
    model,
    messages: [
      { role: "system", content: systemMessage(skills) },
      ...messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role, content: expand(m, skills) })),
    ],
  };
}

// A skill's text is never stored with the message, only its name, so it is folded in here on the
// way out. Two consequences, both wanted: fixing a skill in the repo also fixes every old chat,
// and a skill that was deleted sends the user's own words alone rather than making the chat
// unsendable.
function expand(message, skills) {
  if (!message.skill) return message.content;
  const skill = findSkill(skills, message.skill);
  return skill ? `${skill.body}\n\n${message.content}` : message.content;
}

// The service's own words: a 401 is equally a bad key and a bad model id, so naming one cause here
// would send the reader down the wrong path.
export function formatHttpError(status, body) {
  return `HTTP ${status} — ${body}`;
}
```

`prompt-chat/src/api.js`'te `sendChat` imzasını ve gövde kurulumunu değiştir:

```js
export async function sendChat({ key, model, messages, skills = [] }) {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${key.trim()}`,
    },
    body: JSON.stringify(toRequestBody(messages, model.trim(), skills)),
  });
```

- [ ] **Step 4: Run them and watch them pass**

Çalıştır: `cd prompt-chat && npx vitest run src/chat.test.js src/api.test.js`
Beklenen: PASS.

---

## Task 6: `Message.jsx` — skill etiketi

**Files:**
- Modify: `prompt-chat/src/Message.jsx`
- Modify: `prompt-chat/src/Message.test.jsx`
- Modify: `prompt-chat/src/app.css`

**Interfaces:**
- Consumes: yok.
- Produces: `<Message role content skill />` — `skill` isteğe bağlı; verildiğinde `/ad` biçiminde
  bir etiket çizilir.

- [ ] **Step 1: Write the failing test**

`Message.test.jsx`'in sonuna ekle. Yeni içe aktarım gerekmiyor — `render` ve `screen` dosyanın
başında zaten var. `Message` burada tek başına çiziliyor, yani kenar çubuğu yok ve kapsamsız
`getByText` güvenli:

```jsx
describe("the skill tag", () => {
  it("shows the call name on a message that used a skill", () => {
    render(<Message role="user" content="taşınacağım" skill="plan-yazma" />);
    expect(screen.getByText("/plan-yazma")).toBeTruthy();
  });

  it("shows nothing on a message that did not", () => {
    render(<Message role="user" content="taşınacağım" />);
    expect(screen.queryByText(/^\//)).toBeNull();
  });

  it("shows what the user typed, never the instruction behind it", () => {
    render(<Message role="user" content="taşınacağım" skill="plan-yazma" />);
    expect(screen.getByText("taşınacağım")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/Message.test.jsx`
Beklenen: FAIL — `Unable to find an element with the text: /plan-yazma`.

- [ ] **Step 3: Write the implementation**

`Message.jsx`'te imzayı ve gövdeyi güncelle:

```jsx
export default function Message({ role, content, skill }) {
  const [label, setLabel] = useState("Kopyala");
```

`role` satırının hemen altına ekle:

```jsx
      <div className="role">{ROLE_LABEL[role]}</div>
      {/* The instruction itself is folded in on the way out, so the screen shows only its name:
          three thousand words of skill text would bury the sentence the user actually wrote. */}
      {skill && <div className="skill-tag">/{skill}</div>}
      <div className="body">{content}</div>
```

`app.css`'in sonuna ekle:

```css
.skill-tag {
  display: inline-block;
  margin-bottom: 6px;
  padding: 2px 8px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-3);
  color: var(--accent);
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px;
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/Message.test.jsx`
Beklenen: PASS.

---

## Task 7: `SkillPicker.jsx` — `/` listesi

**Files:**
- Create: `prompt-chat/src/SkillPicker.jsx`
- Test: `prompt-chat/src/SkillPicker.test.jsx`
- Modify: `prompt-chat/src/app.css`

**Interfaces:**
- Consumes: `matchSkills(skills, query)` (Task 3).
- Produces: `<SkillPicker skills query onPick />` — `onPick(name)` seçilen skill'in adıyla çağrılır.
  Eşleşme yoksa hiçbir şey çizmez.

- [ ] **Step 1: Write the failing test**

`prompt-chat/src/SkillPicker.test.jsx` oluştur:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import SkillPicker from "./SkillPicker.jsx";

const SKILLS = [
  { name: "netlestirme", description: "Soruları çıkarır.", body: "A" },
  { name: "plan-yazma", description: "Adımlara böler.", body: "B" },
];

describe("SkillPicker", () => {
  it("lists every skill with its description when nothing is typed yet", () => {
    render(<SkillPicker skills={SKILLS} query="" onPick={() => {}} />);
    expect(screen.getByText("/netlestirme")).toBeTruthy();
    expect(screen.getByText("Adımlara böler.")).toBeTruthy();
  });

  it("narrows the list as the name is typed", () => {
    render(<SkillPicker skills={SKILLS} query="plan" onPick={() => {}} />);
    expect(screen.getByText("/plan-yazma")).toBeTruthy();
    expect(screen.queryByText("/netlestirme")).toBeNull();
  });

  it("draws nothing at all when no name matches", () => {
    const { container } = render(<SkillPicker skills={SKILLS} query="zzz" onPick={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  it("hands the chosen name to onPick", () => {
    const onPick = vi.fn();
    render(<SkillPicker skills={SKILLS} query="" onPick={onPick} />);
    fireEvent.click(screen.getByText("/plan-yazma"));
    expect(onPick).toHaveBeenCalledWith("plan-yazma");
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/SkillPicker.test.jsx`
Beklenen: FAIL — `Failed to resolve import "./SkillPicker.jsx"`.

- [ ] **Step 3: Write the implementation**

`prompt-chat/src/SkillPicker.jsx` oluştur:

```jsx
import { matchSkills } from "./skills.js";

// Drawing nothing when nothing matches is deliberate: an empty box under the text area would look
// like a bug, and the user is mid-word anyway.
export default function SkillPicker({ skills, query, onPick }) {
  const shown = matchSkills(skills, query);
  if (shown.length === 0) return null;

  return (
    <ul className="skill-picker">
      {shown.map((skill) => (
        <li key={skill.name}>
          <button type="button" onClick={() => onPick(skill.name)}>
            <span className="skill-picker-name">/{skill.name}</span>
            <span className="skill-picker-desc">{skill.description}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}
```

`app.css`'in sonuna ekle:

```css
.skill-picker {
  list-style: none;
  margin: 0 0 8px;
  padding: 4px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-2);
  max-height: 240px;
  overflow-y: auto;
}

.skill-picker button {
  display: block;
  width: 100%;
  padding: 8px 10px;
  border: 0;
  border-radius: 4px;
  background: none;
  color: var(--ink);
  text-align: left;
  cursor: pointer;
}

.skill-picker button:hover {
  background: var(--bg-3);
}

.skill-picker-name {
  display: block;
  color: var(--accent);
  font-family: "IBM Plex Mono", monospace;
  font-size: 13px;
}

.skill-picker-desc {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  opacity: 0.75;
}
```

- [ ] **Step 4: Run it and watch it pass**

Çalıştır: `cd prompt-chat && npx vitest run src/SkillPicker.test.jsx`
Beklenen: PASS — 4 test.

---

## Task 8: `App.jsx` ve `Sidebar.jsx` — her şeyi bağla

**Files:**
- Modify: `prompt-chat/src/App.jsx`
- Modify: `prompt-chat/src/App.test.jsx`
- Modify: `prompt-chat/src/Sidebar.jsx`
- Modify: `prompt-chat/src/app.css`

**Interfaces:**
- Consumes: `skills` ve `errors` (Task 4), `splitSkillPrefix` / `findSkill` (Task 3),
  `<SkillPicker>` (Task 7), `<Message skill>` (Task 6), `sendChat({..., skills})` (Task 5).
- Produces: son davranış. Başka görev buna dayanmaz.

- [ ] **Step 1: Write the failing test**

Önce `App.test.jsx`'in **import satırlarının hemen altına** sahteyi koy. `skillSource.js` repodaki
gerçek dosyaları okur; testin ona bağlı olması, bir skill metnini düzeltmenin testi kırması demek
olurdu. Vitest `vi.mock`'u dosyanın tepesine taşır ve fabrika dışarıdaki değişkenleri göremez, bu
yüzden liste burada, yerinde yazılıdır:

```jsx
vi.mock("./skillSource.js", () => ({
  skills: [
    { name: "netlestirme", description: "Soruları çıkarır.", body: "SORU TALİMATI" },
    { name: "plan-yazma", description: "Adımlara böler.", body: "PLAN TALİMATI" },
  ],
  errors: [],
}));
```

Sonra dosyanın sonuna aşağıdaki bloğu ekle. **Yeni yardımcı yazma** — dosyada zaten duran
`withKey()`, `write()`, `composer()`, `sendButton()` ve `inChat()` kullanılır. `inChat()` şart:
bir sohbetin ilk mesajı aynı zamanda kenar çubuğundaki başlığıdır, kapsamsız bir `getByText`
iki eşleşme bulup patlar.

```jsx
describe("calling a skill", () => {
  it("changes nothing at all when no skill is called", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("cevap"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("cevap")).toBeTruthy();
    expect(screen.queryByText("/plan-yazma")).toBeNull();
    // messages[0] is the system message, so the user's own turn is at 1.
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("opens the list when the draft is a bare slash", () => {
    withKey();
    render(<App />);
    write("/");
    expect(screen.getByText("/plan-yazma")).toBeTruthy();
    expect(screen.getByText("/netlestirme")).toBeTruthy();
  });

  it("closes the list once a space is typed", () => {
    withKey();
    render(<App />);
    write("/plan-yazma bir şey");
    expect(screen.queryByText("Adımlara böler.")).toBeNull();
  });

  it("puts the picked name into the draft, ready for the question", () => {
    withKey();
    render(<App />);
    write("/pl");
    fireEvent.click(screen.getByText("/plan-yazma"));
    expect(composer().value).toBe("/plan-yazma ");
  });

  it("stores the name, shows the tag, and sends the instruction", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("1. kutu bul"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("/plan-yazma taşınacağım");
    fireEvent.click(sendButton());

    expect(await screen.findByText("1. kutu bul")).toBeTruthy();
    expect(inChat().getByText("/plan-yazma")).toBeTruthy();
    expect(inChat().getByText("taşınacağım")).toBeTruthy();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1].content).toBe("PLAN TALİMATI\n\ntaşınacağım");
  });

  it("refuses an unknown name and never reaches the network", () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("olmamalı"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("/yok-boyle bir şey");
    fireEvent.click(sendButton());

    expect(screen.getByText(/"\/yok-boyle" bulunamadı/)).toBeTruthy();
    expect(screen.getByText(/\/plan-yazma/)).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("clears the complaint once a valid call replaces it", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("tamam")));
    render(<App />);

    write("/yok-boyle bir şey");
    fireEvent.click(sendButton());
    expect(screen.getByText(/bulunamadı/)).toBeTruthy();

    write("/plan-yazma bir şey");
    fireEvent.click(sendButton());

    expect(await screen.findByText("tamam")).toBeTruthy();
    expect(screen.queryByText(/bulunamadı/)).toBeNull();
  });

  it("sends nothing when only the name was typed", () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("olmamalı"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("/plan-yazma");
    fireEvent.click(sendButton());

    expect(fetchMock).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Çalıştır: `cd prompt-chat && npx vitest run src/App.test.jsx`
Beklenen: FAIL — liste çizilmiyor, etiket yok, bilinmeyen ad ağa gidiyor.

- [ ] **Step 3: Write the implementation**

`App.jsx`'e üç import ekle:

```jsx
import SkillPicker from "./SkillPicker.jsx";
import { skills } from "./skillSource.js";
import { findSkill, splitSkillPrefix } from "./skills.js";
```

`pending` durumunun yanına bir durum daha ekle:

```jsx
  const [skillError, setSkillError] = useState(null);
```

`send()`'i şununla değiştir:

```jsx
  async function send() {
    const typed = active.draft.trim();
    if (!typed || pending) return;

    const { name, content } = splitSkillPrefix(typed);
    if (name && !findSkill(skills, name)) {
      const available = skills.map((s) => `/${s.name}`).join(", ");
      setSkillError(`"/${name}" bulunamadı. Mevcut skill'ler: ${available}`);
      return;
    }
    // A name with nothing after it is a half-typed message, not a request: without a loop there is
    // nothing for an instruction on its own to act on.
    if (!content) return;
    setSkillError(null);

    // The reply belongs to the chat that asked for it, so its id is captured before the await: the
    // user may well be looking at a different chat by the time the answer lands.
    const askedIn = active.id;
    const question = name ? { role: "user", content, skill: name } : { role: "user", content };
    const asked = [...active.messages, question];

    setChats((cs) => setDraft(replaceMessages(cs, askedIn, asked), askedIn, ""));
    setPending(true);
    try {
      const reply = await sendChat({ key: apiKey, model, messages: asked, skills });
      setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "assistant", content: reply }])
      );
    } catch (err) {
      // Covers a non-200 response and a request that never left: network, CORS, unparsable body.
      setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "error", content: err.message }])
      );
    }
    setPending(false);
  }
```

`send`'in altına ekle:

```jsx
  // The list belongs to the moment a name is being typed and nothing else: once a space arrives the
  // user has moved on to the question.
  const picking = /^\/[A-Za-z0-9-]*$/.test(active.draft);

  function pickSkill(name) {
    setChats((cs) => setDraft(cs, active.id, `/${name} `));
  }
```

`Message` çizimine `skill`'i geçir:

```jsx
          {active.messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} skill={m.skill} />
          ))}
```

`<footer>`'ın hemen içine, `<textarea>`'dan **önce** ekle:

```jsx
        <footer>
          {picking && (
            <SkillPicker skills={skills} query={active.draft.slice(1)} onPick={pickSkill} />
          )}
          {skillError && <div className="skill-error">{skillError}</div>}
```

`Sidebar.jsx`'te bozuk skill'leri ayarlarda göster. Önce import ekle:

```jsx
import { errors } from "./skillSource.js";
```

Sonra `settings-body` içindeki iki `<input>`'un altına:

```jsx
            {errors.length > 0 && (
              <ul className="skill-errors">
                {errors.map((e) => (
                  <li key={e.path}>
                    {e.path} — {e.reason}
                  </li>
                ))}
              </ul>
            )}
```

`app.css`'in sonuna ekle:

```css
.skill-error,
.skill-errors {
  margin: 0 0 8px;
  padding: 8px 10px;
  border: 1px solid var(--danger);
  border-radius: 8px;
  color: var(--danger);
  font-size: 12px;
}

.skill-errors {
  list-style: none;
}
```

- [ ] **Step 4: Run the whole suite**

Çalıştır: `cd prompt-chat && npm test`
Beklenen: PASS — hepsi yeşil, toplam bugünkü 69'un belirgin şekilde üstünde.

---

## Self-review notları

**Spec kapsamı.** Spec'teki beş "ne çalışır" maddesinin karşılığı: (1) repoda skill → Task 4;
(2) `/` listesi → Task 7 + 8; (3) mesaj skill ile gider → Task 5; (4) talimat sohbette kalır →
Task 5'in "instruction accumulates" testi; (5) model listeyi bilir → Task 5 `systemMessage`.
Hata tablosunun üç satırı da karşılanıyor: bilinmeyen ad Task 8, bozuk dosya Task 2 + 8, silinmiş
skill Task 5.

**Bilerek dışarıda bırakılan.** Listede klavyeyle gezinme (ok tuşları, Enter) yok — fare ile
seçiliyor ya da ad elle yazılıyor. İki skill'lik bir listede tuş desteği, denenmemiş bir rahatlık
için fazladan durum demek. Gerçekten rahatsız ederse ayrı bir tur.

**Doğrulanmamış varsayım.** `import.meta.glob`'un `{ query: "?raw", import: "default", eager: true }`
biçimi Vite 5.4 içindir. Task 4'ün testi bunu doğrudan sınar: desen tutmazsa liste boş kalır ve test
kırmızı olur — sessizce geçmez.

**Commit.** Bu plan hiçbir görevde commit atmaz. Kullanıcı `npm run dev` ile deneyip onayladıktan
sonra iki commit atılır: `feat(prompt-chat): skills called with /name` (kod + skill dosyaları) ve
gerekirse `docs(prompt-chat)` (spec ve bu plan).
