# Madde 384 — uygulama turu planı

> **Ajan için:** adımlar sırayla, bu oturumda (CLAUDE.md alt ajan istemiyor). Adımlar `- [ ]` ile.

**Amaç:** `c8efd4a2`'nin kırmızı testlerini kodla yeşile getirmek: arşiv sabitlemeyi sunucuda siler,
arşivdekiler son kullanıma göre dizilir, `Undo` yalnız arşivi geri alır.

**Mimari:** Kural `edit_project` kullanım durumunda; `Project.pinned` arşivdekini sabitli okumaz;
`list_projects` blokları `pinned`'le kurar. Tarayıcı `Undo`'da yalnız `onArchiveProject(id, false)` der.

**Teknoloji:** Flask (sync), React 18.

**Spec:** [2026-09-30-queenagent-m384-arsiv-sabitlemeyi-siler-uygulama-design.md](../specs/2026-09-30-queenagent-m384-arsiv-sabitlemeyi-siler-uygulama-design.md)

## Genel kısıtlar

- Kod ve yorumlar İngilizce; yorum yalnız nedeni ve bugün doğru olanı söyler.
- Testler değişmez; `skip`/`xfail`/`.skip`/`.todo` yok.
- `dist` derlenmez.
- Dört test satırı CLAUDE.md'deki gibi, paralel.

---

### Görev 1: Sunucu

**Dosyalar:** `queen-agent/backend/features/workspace/domain/usecases/edit_project.py`,
`.../domain/project.py`, `.../domain/usecases/list_projects.py`, `.../data/file_project_store.py`,
`queen-agent/CODE-STANDARD.md`

- [ ] **Adım 1: `edit_project.py`** — 382'nin özel durumu kalkar; arşiv işaretinin yazıldığı yer:

```python
    if archived is not None:
        store.set_archived(project_id, archived)
        # A project goes into the archive without its pin, and comes out without one (Madde 384):
        # the archive deletes it, and Unarchive clears one an archive made before that rule left.
        if archived != current.archived:
            store.set_pinned(project_id, False)
```

- [ ] **Adım 2: `project.py`** — `pinned` aynı ifade, yorum:

```python
    # Each read from a file of its own beside project.json (Madde 339): each answers a question of
    # its own and is written at a moment of its own. pinned_at is the pin file's mtime, empty when
    # there is none.
    pinned_at: str = ""
    archived: bool = False
    ...
    @property
    def pinned(self):
        # An archived project is never pinned (Madde 384) -- not even one an archive made before
        # that rule left its pin file beside.
        return bool(self.pinned_at) and not self.archived
```

- [ ] **Adım 3: `list_projects.py`** — bloklar `pinned`'le:

```python
    # `pinned` is never true of an archived project, so the archived are ordered by last use alone
    # (Madde 384). The id breaks ties so the order never wobbles.
    pinned = sorted(
        (project for project in projects if project.pinned),
        key=lambda project: (project.pinned_at, project.id),
    )
    recent = sorted(
        (project for project in projects if not project.pinned),
        key=lambda project: (project.last_activity, project.id),
        reverse=True,
    )
```

- [ ] **Adım 4: `file_project_store.py`** — yorum: *The pin's mtime is when the project was pinned,
  which is why pinning twice leaves the file alone.*

- [ ] **Adım 5: CODE-STANDARD** — `pinned` satırı:
  `| \`pinned\` | is this project pinned, and since when | on pin; removed on unpin, on archive and on unarchive — an archived project is never pinned |`

### Görev 2: Tarayıcı

**Dosyalar:** `queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx`,
`queen-agent/frontend/src/App.jsx`

- [ ] **Adım 1: `AllProjectsScreen.jsx`** — `onRestoreProject` prop'u kalkar, ve:

```jsx
  // The project Archive has just taken, while its Undo is on offer. It stands where the server
  // lists it: the archive took its pin away (Madde 384), so that is Recent, by its last use.
  const [undoing, setUndoing] = useState(null);
  ...
  const shown =
    tab === "archived"
      ? archived
      : projects.filter((project) => !project.archived || project.id === undoing);
  ...
  const archive = (id, toArchive) => {
    if (toArchive) setUndoing(id);
    onArchiveProject?.(id, toArchive);
  };
  const undo = async (id) => {
    // Held until the list has come back: let go sooner, the project would vanish for a moment.
    await onArchiveProject?.(id, false);
    // Unless another project's offer began meanwhile.
    setUndoing((current) => (current === id ? null : current));
  };
  ...
    project.id === undoing ? (
      <UndoRow key={project.id} name={project.name} onUndo={() => undo(project.id)} />
```

- [ ] **Adım 2: `App.jsx`** — `onRestoreProject={…}` satırı kalkar.

### Görev 3: Yeşil ve commit

- [ ] **Adım 1:** Dört satır paralel; dört süit yeşil.
- [ ] **Adım 2:** Commit (spec, plan, kod):
  `feat: Madde 384 -- the archive deletes the pin on the server; the archived are listed by last use, and Undo only unarchives`
