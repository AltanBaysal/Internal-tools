# Madde 221 · Projeler arşivlenebilecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-16-queen-editor-m221-arsiv-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı: `f3a1c48c`.

## Adımlar

**1 · `name_rules.py`.** `ARCHIVE_DIR = "arsiv"` ve `validate`'e ayrılmış ad kontrolü
*(`name.casefold() == ARCHIVE_DIR`)*, nokta kuralından sonra.

**2 · `services/drive/storage.py`.** `list_dirs(subdir="")`; olmayan alt klasör `[]`, kök hâlâ
`FileNotFoundError`. `rename_dir`'de taşımadan önce `os.makedirs(os.path.dirname(target),
exist_ok=True)`.

**3 · `features/projects/data/project_store.py`.** `list()` `ARCHIVE_DIR`'i atlar;
`list_archived()`, `archive(name)`, `restore(name)` eklenir. Üçü de `rename`'in `Project | None |
False` sözleşmesini paylaşır.

**4 · `features/projects/domain/usecases/archive_project.py`** *(yeni)*: `archive_project`,
`restore_project`, `list_archived_projects`.

**5 · `features/projects/domain/ports.py`.** `ProjectStore` protokolüne üç imza.

**6 · `features/projects/presentation/routes.py`.** Üç uç, ve `make_projects_blueprint` üç yeni
argüman alır.

**7 · `backend/main.py`.** Üçünü `partial` ile bağlar; `archive_project`'in `halt`'ı
`delete_project`'in kullandığı çağrılabilirin aynısı.

**8 · Ön yüz.**
- `shared/api.js`: `archiveProject`, `restoreProject`, `listArchivedProjects`.
- `vendor/kit.jsx`: `Icon.Archive` *(bir kutu)* ve `Icon.Undo`.
- `ProjectCard.jsx`: `onArchive`, `onRestore`, `archived` prop'ları.
- `ProjectsScreen.jsx`: başlıkta *Arşiv* düğmesi, tek liste, arşivin kendi boş cümlesi, ve her iki
  hareketten sonra yeniden okuma.

**9 · Takım koşulur**, dördü de — hepsi yeşil beklenir:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

**10 · `dist` derlenir** — ön yüz değişti:

```
npm run build --prefix queen-editor/frontend
```

**11 · Yol haritası** 221'i ✅ yapar, durum 8/12 olur.

**12 · Tek commit** — kaynak ve `dist` birlikte.

## Değişen dosyalar

`queen-editor/backend/features/projects/domain/name_rules.py`,
`queen-editor/backend/services/drive/storage.py`,
`queen-editor/backend/features/projects/data/project_store.py`,
`queen-editor/backend/features/projects/domain/usecases/archive_project.py` *(yeni)*,
`queen-editor/backend/features/projects/domain/ports.py`,
`queen-editor/backend/features/projects/presentation/routes.py`,
`queen-editor/backend/main.py`,
`queen-editor/frontend/src/shared/api.js`,
`queen-editor/frontend/src/vendor/kit.jsx`,
`queen-editor/frontend/src/features/projects/ProjectCard.jsx`,
`queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`,
`queen-editor/frontend/dist/**`,
`docs/superpowers/roadmaps/2026-09-11-queen-editor-v5-roadmap.md`.
