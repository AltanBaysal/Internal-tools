# Madde 364 — Yüklenirken ve yüklenemeyince · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kırmızı commit'lenen Madde 364 testlerini, anlattıklarından fazlasını yapmadan yeşile
çevirmek.

**Architecture:** `useProjects` listenin hatasını (`error`) yazmanın reddinden (`writeError`) ayırır,
Try again'i (`retryProjects`) verir, oluşturmanın reddini çağırana fırlatır. İki ekran yüklenirken
340'ın `Spinner`'ını, liste okunamayınca ortak `ProjectsFailure`'ı çizer; `Copy`, `FilePanel`'den
kendi dosyasına taşınan `CopyButton`'dır.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [2026-09-29-queenagent-m364-yukleme-ve-hata-uygulama-design.md](../specs/2026-09-29-queenagent-m364-yukleme-ve-hata-uygulama-design.md)

## Global Constraints

- Arayüz İngilizce; yorumlar NEDEN'i ve yalnız bugün doğru olanı söyler; ölü kod yok.
- Sunucunun sözü olduğu gibi gösterilir ya da kopyalanır; kendi sebebimiz yazılmaz.
- Testler yalnız CLAUDE.md'nin dört satırıyla, paralel; hiçbir test susturulmaz.
- `dist` derlenmez (Claude derler). Commit'te çift tırnak yok, amend yok; sonu
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

### Task 1: `CopyButton` kendi dosyasında

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/CopyButton.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/FilePanel.jsx`

**Interfaces:**
- Produces: `<CopyButton text className />` — `ghost ${className}` sınıflı düğme; basınca `text`'i
  panoya yazar, `Copied` / `Could not copy` der (`data-said` `yes` / `no`), 2500 ms sonra `Copy`;
  `text` boşken soluk.

- [ ] **Step 1:** `FilePanel.jsx`'teki `CopyButton` fonksiyonu, `SAID_MS` ve importları
  `CopyButton.jsx`'e taşınır, `export default`; düğmenin sınıfı `` `ghost ${className}` ``. Yorumlar:
  genel olan (jest, `try`, düğmenin kendi yazısı, soluk) düğmeyle gider; dosyaya özgü olan (Madde
  193: dosyanın kendisi kopyalanır, panelin kopyası basışı kaybetmemek için; Madde 192) `FilePanel`'de,
  kullanıldığı yerde kalır.
- [ ] **Step 2:** `FilePanel.jsx` `import CopyButton from "./CopyButton.jsx"` ve
  `<CopyButton text={file?.text ?? ""} className="reader__copy" />`; `useEffect`, `useRef`,
  `useState` importları gider.

### Task 2: Ortak hata ekranı ve `useProjects`

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/ProjectsFailure.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/useProjects.js`

**Interfaces:**
- Consumes: Task 1'in `CopyButton`'ı.
- Produces: `<ProjectsFailure error onRetry />`. `useProjects()` →
  `{ projects, error, writeError, loading, createProject, editProject, removeProject, reloadProjects, retryProjects }`;
  `createProject(name)` reddedilince fırlatır.

- [ ] **Step 1:** `ProjectsFailure.jsx`:

```jsx
import CopyButton from "./CopyButton.jsx";

export default function ProjectsFailure({ error, onRetry }) {
  return (
    <div className="empty">
      <p className="empty__error">Couldn&apos;t load projects.</p>
      <div className="empty__actions">
        <button type="button" className="failure__retry" onClick={onRetry}>
          Try again
        </button>
        <CopyButton text={error} className="empty__copy" />
      </div>
    </div>
  );
}
```

- [ ] **Step 2:** `useProjects.js`: `reload` başarıda `setError(null)`; `retry = () => { setLoading(true); return reload(); }`;
  `writeError` durumu, `editProject` ve `removeProject` başta `setWriteError(null)`, `catch`'te
  `setWriteError(failure.message)`; `createProject`'in `try/catch`'i kalkar; dönüşe `writeError` ve
  `retryProjects: retry`.

### Task 3: İki ekran, App ve stil

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/NameProjectScreen.jsx`
- Modify: `queen-agent/frontend/src/App.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css`

**Interfaces:**
- Consumes: Task 2'nin `ProjectsFailure`'ı ve `useProjects`'i; 340'ın `Spinner`'ı.

- [ ] **Step 1:** `AllProjectsScreen`: prop'lara `writeError`, `onRetry`;
  `if (error && !loading) return <ProjectsFailure error={error} onRetry={onRetry} />;`
  aramanın satırından sonra:

```jsx
{writeError ? <p className="list-error">{writeError}</p> : null}
{loading ? (
  <div className="all-projects__spinner">
    <Spinner />
  </div>
) : (
  <ProjectList projects={projects} query={query} row={row} />
)}
```

- [ ] **Step 2:** `NameProjectScreen`: prop'lara `onRetry`; `const [refused, setRefused] = useState(null);`
  hook'larla birlikte, erken dönüşlerden önce;
  `if (loading) return <div className="empty"><Spinner /></div>;`,
  `if (error) return <ProjectsFailure error={error} onRetry={onRetry} />;`;
  `create`'te `Promise.resolve(onCreate(trimmed)).catch((failure) => setRefused(failure.message)).finally(…)`;
  `.empty__row`'un ardından `{refused ? <p className="empty__refused">{refused}</p> : null}`.
- [ ] **Step 3:** `App.jsx`: `useProjects`'ten `writeError`, `retryProjects`;
  `<AllProjectsScreen … writeError={writeError} onRetry={retryProjects} />`,
  `<NameProjectScreen … onRetry={retryProjects} />`;
  `createNamed` `const created = await createProject(name); navigate(\`/p/${created.id}/c/new\`, { replace: true });`.
- [ ] **Step 4:** `workspace.css`: `.chat__spinner`'ın ardından

```css
.all-projects__spinner {
  display: flex;
  justify-content: center;
  padding: 40px 12px;
}
```

  `.empty__error`'ın ardından

```css
.empty__actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.empty__copy[data-said="yes"] {
  color: var(--accent);
}

.empty__copy[data-said="no"] {
  color: var(--destructive);
}

.empty__refused {
  margin: 10px 0 0;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: #a4735a;
  overflow-wrap: anywhere;
}
```

  `.empty` ve `.empty__error`'ın yorumları bugünkü hâle göre.

### Task 4: Yeşili görmek ve commit

- [ ] **Step 1:** Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`. Beklenen: dördü yeşil.
- [ ] **Step 2:** Commit:

```
git add docs/superpowers/specs/2026-09-29-queenagent-m364-yukleme-ve-hata-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m364-yukleme-ve-hata-uygulama-plan.md queen-agent/frontend/src
git commit -m "feat: Madde 364 -- All projects and the naming screen wait with the spinner, and a list that did not come says so with Try again and Copy"
```
