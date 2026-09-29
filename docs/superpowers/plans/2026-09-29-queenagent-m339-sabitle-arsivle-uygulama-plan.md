# Madde 339 — Proje sabitlenir ve arşivlenir, sunucu · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test turunun kırmızı testlerini yeşile getiren sunucu kodu: iki işaret dosyası, portun iki
yöntemi, `edit_project`'in iki argümanı, `PATCH`'in ve proje JSON'ının iki alanı, ve
CODE-STANDARD'ın tablosu.

**Architecture:** `project.json` değişmez. Projenin klasöründe `pinned` ve `archived` boş dosyaları
cevabı taşır; `FileProjectStore` onları okur ve yazar, `edit_project` onları istenince yazar ve
`project.json`'ı yalnız yeniden adlandırınca yazar, kapı gövdeden ikisini de geçirir.

**Tech Stack:** Flask, pytest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m339-sabitle-arsivle-uygulama-design.md)

## Global Constraints

- Yalnız committed testlerin tarif ettiği; sıra (v9-2j) ve ekran (v9-2q, v9-2t) yok.
- Ön uç değişmez, `dist` derlenmez.
- Kod ve yorum İngilizce; yorum neden'i söyler, yalnız bugün doğru olanı.
- Testler yalnız CLAUDE.md'deki dört satırla, paralel.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Sabitleme ve arşiv, uçtan uca

**Files:**
- Modify: `queen-agent/backend/features/workspace/domain/project.py`
- Modify: `queen-agent/backend/features/workspace/domain/ports.py` — `ProjectStore`
- Modify: `queen-agent/backend/features/workspace/data/file_project_store.py`
- Modify: `queen-agent/backend/features/workspace/domain/usecases/edit_project.py`
- Modify: `queen-agent/backend/features/workspace/presentation/routes.py` — `patch_project`, `_project_json`
- Modify: `queen-agent/CODE-STANDARD.md` — *Separation of concerns*'in tablosu ve altındaki cümle
- Test: `queen-agent/backend/tests/test_pin_archive.py`, `test_projects_api.py` (test turunda yazıldı)

**Interfaces:**
- Produces: `Project.pinned`, `Project.archived`; `ProjectStore.set_pinned(project_id, pinned)`,
  `ProjectStore.set_archived(project_id, archived)`; `edit_project(store, project_id, name=None,
  pinned=None, archived=None) -> Project` (diskten yeniden okunmuş proje); proje JSON'ında
  `"pinned"`, `"archived"`.

- [ ] **Step 1: `Project`'e iki alan**

```python
    chat_count: int = 0
    file_count: int = 0
    # Read the same way, each from a file of its own beside project.json (Madde 339): each answers a
    # question of its own and is written at a moment of its own.
    pinned: bool = False
    archived: bool = False
```

- [ ] **Step 2: Portun iki yöntemi** — `ProjectStore`'un sonuna:

```python
    def set_pinned(self, project_id: str, pinned: bool) -> None:
        """Pin the project or let it go. Asking for what already stands changes nothing."""

    def set_archived(self, project_id: str, archived: bool) -> None:
        """Archive the project or bring it back. Asking for what already stands changes nothing."""
```

- [ ] **Step 3: `FileProjectStore`**

Sabitler `TRASH_DIR`'ın altına:

```python
# Empty, and there or not there: each answers a question project.json does not (CODE-STANDARD). The
# pin's mtime is when the project was pinned, which is why pinning twice leaves the file alone.
PINNED_FILE = "pinned"
ARCHIVED_FILE = "archived"
```

`list_all`'da `Project(...)`'ye:

```python
                    pinned=self._store.exists(f"{entry}/{PINNED_FILE}"),
                    archived=self._store.exists(f"{entry}/{ARCHIVED_FILE}"),
```

`delete`'in altına:

```python
    def set_pinned(self, project_id, pinned):
        self._mark(project_id, PINNED_FILE, pinned)

    def set_archived(self, project_id, archived):
        self._mark(project_id, ARCHIVED_FILE, archived)
```

`_write`'ın altına:

```python
    def _mark(self, project_id, name, on):
        path = f"{project_id}/{name}"
        if self._store.exists(path) == on:
            return
        if on:
            self._store.write_text(path, "")
        else:
            self._store.remove(path)
```

Modülün açıklaması: *the only place that knows the project.json schema* →
*the only place that knows how a project is laid out on disk*.

- [ ] **Step 4: `edit_project`**

```python
def edit_project(store, project_id, name=None, pinned=None, archived=None) -> Project:
    current = store.get(project_id)
    if current is None:
        raise ProjectNotFound(project_id)

    if name is not None:
        trimmed = name.strip()
        # The browser cancels on an empty prompt, but that is a convenience; the rule lives here.
        if not trimmed:
            raise InvalidProjectName(name)
        # created_at stays: it is the project's history, not something a rename rewrites.
        store.replace(replace(current, name=trimmed))
    # project.json is written on create and on rename, and a pin is neither: each of these is a
    # file of its own, written only when it is what was asked for (CODE-STANDARD).
    if pinned is not None:
        store.set_pinned(project_id, pinned)
    if archived is not None:
        store.set_archived(project_id, archived)
    # Read back rather than assembled here: the counts and the two marks are the disk's answer.
    return store.get(project_id)
```

- [ ] **Step 5: Kapı**

```python
    @workspace_bp.patch("/api/projects/<project_id>")
    def patch_project(project_id):
        payload = request.get_json(silent=True) or {}
        try:
            project = edit_project(
                project_store,
                project_id,
                name=payload.get("name"),
                pinned=payload.get("pinned"),
                archived=payload.get("archived"),
            )
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except InvalidProjectName:
            return jsonify({"error": "a project needs a name"}), 400
        return jsonify(_project_json(project))
```

`_project_json`'a `"pinned": project.pinned, "archived": project.archived`.

- [ ] **Step 6: CODE-STANDARD**

Tabloya `trash/<name>`'in altına:

```markdown
| `pinned` | is this project pinned, and since when | on pin; removed on unpin |
| `archived` | is this project archived | on archive; removed on unarchive |
```

Altındaki cümle: *a field that answers a fifth question wants a fifth artifact* → *a field that
answers a new question wants an artifact of its own*.

- [ ] **Step 7: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent arka ucu 946 yeşil; ön ucu 652; queen-editor arka ucu 377'nin bilinen iki
kırmızısı ve 1158 yeşil; ön ucu 749.

- [ ] **Step 8: Commit**

```powershell
git add queen-agent/backend/features/workspace queen-agent/CODE-STANDARD.md docs/superpowers/specs/2026-09-29-queenagent-m339-sabitle-arsivle-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m339-sabitle-arsivle-uygulama-plan.md
git commit -m @'
feat: Madde 339 -- a project is pinned and archived in files of its own, and the project list says both

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
