# Madde 361 — Ad sorma ekranı · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `d649fe87`'nin kırmızı testlerini kodla yeşile getirmek.

**Architecture:** Sunucu projeyi adıyla doğurur (tek kural `project_name`); ön uç `/new`'de
`NameProjectScreen`'i çizer, App oluşturmayı ve dönüşü yönetir, `Bar` sağdaki düğmenin adını alır.

**Tech Stack:** Flask, React 18, vitest.

**Spec:** [2026-09-29-queenagent-m361-ad-sorma-uygulama-design.md](../specs/2026-09-29-queenagent-m361-ad-sorma-uygulama-design.md)

## Global Constraints

- Testlere dokunulmaz; yalnız kod.
- Kod İngilizce, yorum NEDEN'i söyler; ölü kod kalmaz.
- Testler yalnız CLAUDE.md'nin dört satırıyla; `dist` derlenmez (Claude derler).

---

### Task 1: Sunucu

**Files:** Modify `domain/usecases/create_project.py`, `presentation/routes.py`
(`edit_project.py`'ye dokunulmaz — spec'e bakın).

**Interfaces:** Produces `create_project(store, new_id, name, now) -> Project`.

- [ ] **Step 1:** `create_project.py`:

```python
def create_project(store, new_id, name, now):
    trimmed = (name or "").strip()
    if not trimmed:
        raise InvalidProjectName(name)
    project = Project(id=new_id, name=trimmed, created_at=now)
    store.add(project)
    return project
```

- [ ] **Step 2:** `routes.py` `post_project`: read payload, `create_project(..., name=payload.get("name"), ...)`,
  `except InvalidProjectName: return jsonify({"error": "a project needs a name"}), 400`.

### Task 2: Ön uç

**Files:** Modify `shared/useRoute.js`, `features/workspace/Bar.jsx`, `features/workspace/useProjects.js`,
`App.jsx`, `features/workspace/workspace.css`; Create `features/workspace/NameProjectScreen.jsx`.

- [ ] **Step 1:** `parsePath`: `if (parts.length === 1 && parts[0] === "new") return { view: "new", projectId: null, chatId: null };`
- [ ] **Step 2:** `Bar`: `exit = project ? "Exit project" : null` default; the button renders when `exit`.
- [ ] **Step 3:** `useProjects.createProject(name)` → `postJson("/api/projects", { name })`.
- [ ] **Step 4:** `NameProjectScreen.jsx` as the spec's markup; `sending` ref; Enter without Shift.
- [ ] **Step 5:** `App.jsx`: `namingFrom` state, `askForNewProject`, `leaveNaming`, `createNamed`;
  sidebar hidden on `new`; `NameProjectScreen` on `new`; `Bar` `exit`/`onExit`; Esc's last branch.
- [ ] **Step 6:** `workspace.css`: `.empty__title`, `.empty__line`, `.empty__box`, `.empty__row`,
  `.empty__field` under `.empty__error`, values from the design's `kit.css`.

### Task 3: Yeşil ve commit

- [ ] **Step 1:** Dört satır, paralel; hepsi yeşil.
- [ ] **Step 2:** Diff FOUNDATION, CODE-STANDARD, tasarım ve satırın *Bitti sayılır*'ına karşı okunur.
- [ ] **Step 3:** `git commit -m "feat: Madde 361 -- ..."` (çift tırnaksız, Co-Authored-By satırıyla).
