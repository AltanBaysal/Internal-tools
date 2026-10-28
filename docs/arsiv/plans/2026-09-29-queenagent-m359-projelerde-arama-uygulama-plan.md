# Madde 359 — Projelerde arama · uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** `b4ffbd05`'in kırmızı testlerini (D1–D9, C7, C8) yeşile çeviren kod; fazlası değil.

**Mimari:** Arama `AllProjectsScreen`'in kendi durumu; süzme aynı dosyada küçük bir `fold` ve bir
`ProjectList` bileşeni. Stil `workspace.css`'te tasarımın iki kuralı.

**Teknoloji:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m359-projelerde-arama-uygulama-design.md)

## Genel kısıtlar

- Kutunun adı ve yazısı tam olarak `Search projects`; eşleşme yoksa tam olarak `No projects match "<kırpılmış arama>".`
- UI metni ve yorumlar İngilizce; yorum NEDEN'i söyler.
- Odak çizgisi yazılmaz (`app.css`'in).
- Testler yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur. `dist` derlenmez.

---

### Görev 1: Arama ve stil

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx`
- Değişir: `queen-agent/frontend/src/features/workspace/workspace.css` (`.all-projects__head`'in altı)

- [ ] **Adım 1: Baştaki yorumu güncelle.** İkinci paragraf:

```jsx
// The search is this screen's own state: what is shown while typing is the UI's (FOUNDATION,
// Decision 4), so it reaches neither the server nor the address.
//
// The row's ⋯ and the Archived tab are items of their own (360, 363), and so are the spinner and
// the sentence a failed list gets (364).
```

- [ ] **Adım 2: `useState`'i içe al, `fold`'u ve `ProjectList`'i `Section`'ın altına yaz.**

```jsx
import { useState } from "react";

// Case and accents do not count, as in the design's data.js: "cafe" finds "Café".
const fold = (text) => text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

function ProjectList({ projects, query, onOpenProject }) {
  // Asked first: with nothing to search, "no match" would be the wrong news.
  if (!projects.length) return <p className="all-projects__empty">No projects yet.</p>;
  const asked = query.trim();
  const found = projects.filter((project) => fold(project.name).includes(fold(asked)));
  if (!found.length) return <p className="all-projects__empty">{`No projects match "${asked}".`}</p>;
  return (
    <>
      <Section
        label="Pinned"
        projects={found.filter((project) => project.pinned)}
        onOpenProject={onOpenProject}
      />
      <Section
        label="Recent"
        projects={found.filter((project) => !project.pinned)}
        onOpenProject={onOpenProject}
      />
    </>
  );
}
```

- [ ] **Adım 3: Ekranda durumu tut, kutuyu başlığın altına koy, gövdeyi `ProjectList`'e bırak.**
  `useState` `if (error)`'dan önce (hook'un sırası). Başlık satırından sonra:

```jsx
        <div className="all-projects__tools">
          {/* Focused as the screen opens (the design's 142), even while the list is on its way:
              handing it over again once the list comes could pull it from where the user went. */}
          <input
            type="text"
            className="all-projects__search"
            placeholder="Search projects"
            aria-label="Search projects"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            autoFocus
          />
        </div>
        {/* Until the list has come, "no projects yet" is a guess and not a fact. */}
        {loading ? null : (
          <ProjectList projects={projects} query={query} onOpenProject={onOpenProject} />
        )}
```

- [ ] **Adım 4: `workspace.css`'e iki kural.**

```css
/* The search's row; the Archived tab joins it on the right (Madde 363). */
.all-projects__tools {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 0 0 28px;
}

.all-projects__search {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius-control);
  padding: 8px 12px;
  background: var(--surface);
  font-family: inherit;
  font-size: 13.5px;
  color: var(--ink);
}
```

- [ ] **Adım 5: Dört satırı paralel koş.** Dördü yeşil.
- [ ] **Adım 6: Commit.** Uygulama spec'i, bu plan, iki dosya:
  `feat: Madde 359 -- Search projects narrows All projects by name, focused on open`
