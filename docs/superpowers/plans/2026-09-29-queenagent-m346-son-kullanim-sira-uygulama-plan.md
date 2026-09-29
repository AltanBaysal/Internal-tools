# Madde 346 — Projenin son kullanıldığı an, ve listenin sırası, sunucu · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test turunun kırmızılarını yeşile getirmek: proje son kullanıldığı anı sohbet dosyalarından
okur, liste önce sabitlenenleri sabitlendikleri sırayla, sonra en son kullanılanı verir.

**Architecture:** `Project` iki okunan alan (`last_chat_at`, `pinned_at`) ve iki özellik
(`last_activity`, `pinned`) taşır; `FileProjectStore` ikisini mtime'lardan doldurur; `list_projects`
yeni kuralla dizer; `_project_json` `lastActivity`'yi ekler.

**Tech Stack:** Python, Flask.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m346-son-kullanim-sira-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; yorum neden'i söyler, bugün doğru olanı.
- Testler değişmez; `skip`/`xfail` yok.
- `npm run build` koşulmaz, `dist` commit'lenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Kod, belge, yeşil

**Files:**
- Modify: `queen-agent/backend/features/workspace/domain/project.py`
- Modify: `queen-agent/backend/features/workspace/data/file_project_store.py`
- Modify: `queen-agent/backend/features/workspace/domain/usecases/list_projects.py`
- Modify: `queen-agent/backend/features/workspace/presentation/routes.py` — `_project_json`
- Modify: `queen-agent/CODE-STANDARD.md` — *No file repeats another's answer* paragrafı
- Modify: `queen-agent/frontend/src/features/workspace/useProjects.js` — `createProject`'in yorumu

**Interfaces:**
- Consumes: test turunun planındaki arayüz.
- Produces: `Project.last_chat_at`, `Project.pinned_at`, `Project.last_activity`, `Project.pinned`;
  proje JSON'ında `"lastActivity"`.

- [ ] **Step 1: `project.py`**

```python
"""Project -- the workspace that owns a set of chats and a set of files."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    created_at: str
    # Derived from the directories at read time and never written back: the counts are the
    # directory's own answer, so storing them would be a second copy that can go stale.
    chat_count: int = 0
    file_count: int = 0
    # Read the same way (Madde 346): when a chat of this project was last written, empty while it
    # has none -- the chats already say it, so it is stored nowhere.
    last_chat_at: str = ""
    # Each read from a file of its own beside project.json (Madde 339): each answers a question of
    # its own and is written at a moment of its own. The pin is the file's mtime, empty when unpinned.
    pinned_at: str = ""
    archived: bool = False

    @property
    def last_activity(self):
        # A project nobody has talked in yet was last used when it was made.
        return self.last_chat_at or self.created_at

    @property
    def pinned(self):
        return bool(self.pinned_at)
```

- [ ] **Step 2: `file_project_store.py`** — `list_all` ve bir yardımcı:

```python
    def list_all(self):
        projects = []
        for entry in self._store.list_dir(""):
            path = f"{entry}/{PROJECT_FILE}"
            if not self._store.exists(path):
                continue  # anything else living under the root is not ours to read
            raw = json.loads(self._store.read_text(path))
            chats = self._store.list_dir(f"{entry}/{CHATS_DIR}")
            pin = f"{entry}/{PINNED_FILE}"
            projects.append(
                Project(
                    id=entry,
                    name=raw["name"],
                    created_at=raw["createdAt"],
                    chat_count=len(chats),
                    file_count=len(self._store.list_dir(f"{entry}/{FILES_DIR}")),
                    # A chat file is written whenever anybody talks in it, so the newest one says
                    # when the project was last used (Madde 346).
                    last_chat_at=max(
                        (self._stamp(f"{entry}/{CHATS_DIR}/{name}") for name in chats), default=""
                    ),
                    pinned_at=self._stamp(pin) if self._store.exists(pin) else "",
                    archived=self._store.exists(f"{entry}/{ARCHIVED_FILE}"),
                )
            )
        return projects

    def _stamp(self, path):
        # The shape the routes stamp createdAt with -- UTC, to the millisecond -- so the two compare
        # as text, which is how the list is ordered.
        return datetime.fromtimestamp(self._store.mtime(path), timezone.utc).isoformat(
            timespec="milliseconds"
        )
```

ve en üstte `from datetime import datetime, timezone`.

- [ ] **Step 3: `list_projects.py`**

```python
"""List projects: the pinned first, in the order they were pinned, then the most recently used.

The sidebar's order, and so the project the app opens on. The design's All projects (135, 167).
"""


def list_projects(store):
    projects = store.list_all()
    # The id breaks ties so the order never wobbles.
    pinned = sorted(
        (project for project in projects if project.pinned),
        key=lambda project: (project.pinned_at, project.id),
    )
    recent = sorted(
        (project for project in projects if not project.pinned),
        key=lambda project: (project.last_activity, project.id),
        reverse=True,
    )
    return pinned + recent
```

- [ ] **Step 4: `routes.py`** — `_project_json`'a `"lastActivity": project.last_activity`.

- [ ] **Step 5: `CODE-STANDARD.md`** — paragraf şöyle olur:

```markdown
**No file repeats another's answer.** The file list is the directory listing itself: the name is the
filename, "2h ago" is its mtime, the order is mtime descending. A project's "2h ago" is its newest
chat file's mtime, or its createdAt while it has none. The count on a sidebar project row is a
directory count. ...
```

- [ ] **Step 6: `useProjects.js`** — yorum:

```js
      // Appended until the list is read again: where it belongs is the server's order
      // (list_projects.py), and a copy of that rule here would drift from it.
```

- [ ] **Step 7: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: 954, 695, 1160, 749 — hepsi yeşil.

- [ ] **Step 8: Commit**

```powershell
git add queen-agent/backend/features/workspace/domain/project.py queen-agent/backend/features/workspace/data/file_project_store.py queen-agent/backend/features/workspace/domain/usecases/list_projects.py queen-agent/backend/features/workspace/presentation/routes.py queen-agent/CODE-STANDARD.md queen-agent/frontend/src/features/workspace/useProjects.js docs/superpowers/specs/2026-09-29-queenagent-m346-son-kullanim-sira-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m346-son-kullanim-sira-uygulama-plan.md
git commit -m @'
feat: Madde 346 -- the project list says when each project was last used, read off its chats, and lists the pinned first then the most recent

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
