# Madde 227 · Arşiv bir işaret olacak — uygulamanın planı

**Spec:** [uygulama turu](../specs/2026-09-16-queen-editor-m227-arsiv-isaret-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı commit: `c98a0db1`.

## Adımlar

**1 · `name_rules.py`** — ayrılmış adın cümlesi sebebini söylemeyi bırakıyor; `ARCHIVE_DIR` duruyor,
artık **eski** arşiv klasörünün adı olarak.

**2 · `project_store.py`** — maddenin gövdesi.

- `MARK_FILE = "arsiv.json"`, `_marks()` / `_write_marks()`; okunamayan her şey boş liste.
- `list` / `list_archived` işarete göre ayrılıyor; `list` `ARCHIVE_DIR`'ü atlamayı sürdürüyor.
- `archive` / `restore` → `bool`. `is_archived` işarete bakıyor.
- `rename` işareti taşıyor, `delete` düşürüyor.
- `create` ile `rename`'in 223 ön kontrolleri kalkıyor.
- `__init__` göçü çağırıyor; `_free_name` dolu adın yanına iniyor.

**3 · `archive_project.py`** — `halt` ve `NameTaken` gidiyor; iki kullanım da `False` → `ProjectMissing`.

**4 · `routes.py`** — arşiv/geri alma uçlarından `NameTaken` yakalaması kalkıyor.

**5 · `main.py`** — `archive_project=partial(archive_project, _project_store)`. Silmedeki
`halt_project` **yerinde kalıyor**.

**6 · `ProjectCard.jsx`** — arşivdeki kart kalem + **Geri al** + çöp.

**7 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

**8 · `npm run build --prefix queen-editor/frontend`**, ve `dist` kaynakla aynı commit'e girer.

**9 · Commit.**

## Değişen dosyalar

`queen-editor/backend/features/projects/data/project_store.py`,
`queen-editor/backend/features/projects/domain/name_rules.py`,
`queen-editor/backend/features/projects/domain/usecases/archive_project.py`,
`queen-editor/backend/features/projects/presentation/routes.py`,
`queen-editor/backend/main.py`,
`queen-editor/frontend/src/features/projects/ProjectCard.jsx`,
`queen-editor/frontend/dist/**`.
