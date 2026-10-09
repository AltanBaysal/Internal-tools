# Madde 353 — All projects ekranı · uygulama planı

> **Ajan için:** Tek oturumda, satır satır (`superpowers:executing-plans`). Adımlar `- [ ]` ile izlenir.
> Yalnız `61cd5c44`'teki kırmızı testlerin tarif ettiği yazılır.

**Hedef:** Uygulamayı All projects ile açmak, `/p/<id>`'yi son sohbete açılan bir kapı yapmak, proje
ekranını ve sohbet silmeyi kaldırmak — testler yeşil.

**Mimari:** İki yeni küçük bileşen (`AllProjectsScreen`, `OpenProject`) ve bir yardımcı (`countOf`);
App'in kök çatalı ve proje ekranı kalkar; sunucudan sohbet silmenin dört katmanı kalkar.

**Teknoloji:** React 18, Vite, vitest; Flask.

**Spec:** [2026-09-29-queenagent-m353-all-projects-uygulama-design.md](../specs/2026-09-29-queenagent-m353-all-projects-uygulama-design.md)

## Genel kısıtlar

- Dört test satırı aynen, paralel; `dist` derlenmez.
- Ekran metni İngilizce ve tasarımın: `All projects`, `+ New project`, `Pinned`, `Recent`,
  `No projects yet.`, `N chats · N files`.
- Yorum yalnız bugünü ve nedeni söyler; ölü kod kalmaz.
- Commit: çift tırnak yok, amend yok, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

### Görev 1: Sunucu — sohbet silme kalkar

**Dosyalar:** sil `backend/features/workspace/domain/usecases/delete_chat.py`; değiştir
`presentation/routes.py`, `data/file_chat_store.py`, `domain/ports.py`, `domain/usecases/list_chats.py`,
`queen-agent/CODE-STANDARD.md`.

- [ ] `routes.py`: `delete_chat` import'u ve `delete_project_chat` kapısı silinir.
- [ ] `file_chat_store.py`: `delete`, `TRASH_DIR` ve `unique_name` import'u silinir.
- [ ] `ports.py`: `ChatStore.delete` silinir.
- [ ] `list_chats.py` docstring'i: `"""List chats newest first -- the sidebar shows the latest on top, and a project opens on it."""`
- [ ] CODE-STANDARD tablosu: `| trash/<name> | what did the user just delete | on a file's delete |`.

### Görev 2: `countOf.js`, `AllProjectsScreen.jsx`, `OpenProject.jsx`, `useChatLists.js`, `useProjects.js`

```js
// countOf.js
// One of a thing is one, not one of them -- the design writes the sentence out that way, in the
// delete question and on the All projects row alike.
export function countOf(many, word) {
  return `${many} ${word}${many === 1 ? "" : "s"}`;
}
```

```jsx
// AllProjectsScreen.jsx (özü)
function Section({ label, projects, onOpenProject }) {
  if (!projects.length) return null;
  return (
    <div className="all-projects__section">
      <div className="all-projects__label">{label}</div>
      <div className="all-projects__list">
        {projects.map((project) => (
          <div key={project.id} className="all-projects__row">
            <button type="button" className="all-projects__row-open" title={project.name}
              onClick={() => onOpenProject?.(project.id)}>
              <span className="all-projects__row-name">{project.name}</span>
              <span className="all-projects__row-meta">
                {`${countOf(project.chats ?? 0, "chat")} · ${countOf(project.files ?? 0, "file")}`}
              </span>
              <span className="all-projects__row-when">{relativeTime(project.lastActivity)}</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AllProjectsScreen({ projects, loading, error, onNewProject, onOpenProject }) {
  if (error) return <div className="empty"><p className="empty__error">{error}</p></div>;
  return (
    <div className="screen"><div className="screen__column">
      <div className="all-projects__head">
        <h1 className="screen__title">All projects</h1>
        <button type="button" className="empty__action" onClick={onNewProject}>+ New project</button>
      </div>
      {loading ? null : projects.length ? (<>
        <Section label="Pinned" projects={projects.filter((p) => p.pinned)} onOpenProject={onOpenProject} />
        <Section label="Recent" projects={projects.filter((p) => !p.pinned)} onOpenProject={onOpenProject} />
      </>) : <p className="all-projects__empty">No projects yet.</p>}
    </div></div>
  );
}
```

```jsx
// OpenProject.jsx
export default function OpenProject({ projectId, navigate }) {
  const [error, setError] = useState(null);
  useEffect(() => {
    let left = false;
    readChats(projectId).then(
      (chats) => {
        if (!left) navigate(`/p/${projectId}/c/${chats[0]?.id ?? "new"}`, { replace: true });
      },
      (failure) => {
        if (!left) setError(failure.message);
      },
    );
    return () => {
      left = true;
    };
  }, [projectId, navigate]);
  return error ? (
    <div className="screen"><div className="screen__column"><p className="list-error">{error}</p></div></div>
  ) : null;
}
```

- [ ] `useChatLists.js`: `deleteChat` → `export function readChats(projectId) { return getJson(`/api/projects/${projectId}/chats`); }`.
- [ ] `useProjects.js` `createProject`: `const created = await postJson("/api/projects"); await reload(); return created;`.

### Görev 3: `App.jsx`

- [ ] Import'lar: `AllProjectsScreen`, `OpenProject`, `countOf` gelir; `NoProjectsScreen`,
  `ProjectScreen`, `Skeleton`, `deleteChat` gider.
- [ ] `firstLoad`, `atFork`, `landing`, kök effect'i, `askToDeleteChat`, yerel `countOf` silinir.
- [ ] `newProject`: `const created = await createProject(); if (created) navigate(`/p/${created.id}/c/new`);`
- [ ] `deleteProject`: `if (route.projectId === id) navigate("/", { replace: true });`
- [ ] Render: `route.view !== "root"` iken `Sidebar`; `root` → `<AllProjectsScreen projects loading error
  onNewProject={newProject} onOpenProject={openProject} />`; `project` → `project ? <OpenProject
  key={project.id} projectId={project.id} navigate={navigate} /> : !loading ? <p className="screen__missing">That project does not exist.</p>`
  (`.screen` › `.screen__column` içinde); `chat` → `ChatScreen`, `onBack={() => navigate("/")}`.
- [ ] Proje ekranını ya da çatalı anan yorumlar bugüne çevrilir.

### Görev 4: `FilePanel.jsx`, `FileRail.jsx`, `FileRow.jsx`

- [ ] `FilePanel`: `back` parametresi ve `×` dalı silinir; bar hep `<button className="back back--inline">←</button>`.
- [ ] `FileRail`: `back` prop'u verilmez; `RefreshFiles`'ın `export`'u silinir; yorumlar.
- [ ] `FileRow`: baş yorumu.

### Görev 5: `workspace.css`

- [ ] Spec'teki kurallar silinir; `.all-projects__*` kuralları `kit.css`'teki değerlerle eklenir
  (`data-hover` seçicileri hariç).

### Görev 6: Sil, koş, commit

- [ ] `git rm` `ProjectScreen.jsx`, `NoProjectsScreen.jsx`.
- [ ] Dört satır paralel; hepsi yeşil.
- [ ] Commit: `feat: Madde 353 -- All projects opens the app, a row opens its project's latest chat, and the project screen and chat deletion are gone`
