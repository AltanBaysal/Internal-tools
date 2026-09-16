# Madde 223 · Arşivdeki ad tutulmuş sayılacak — uygulamanın planı

**Spec:** [uygulama turu](../specs/2026-09-16-queen-editor-m223-arsiv-ad-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı commit: `f74d1b0d`. Bu tur onu yeşile çeviriyor, başka hiçbir şey eklemeden.

## Adımlar

**1 · `name_rules.py` — cümle.** `ARCHIVE_DIR`'ün altına `archive_taken(name)`. Tek metin, iki
kullanım paylaşıyor.

**2 · `project_store.py` — kural.**

- `is_archived(name)` → `self.storage.dir_exists(self._in_archive(name))`.
- `create`: `is_archived` ise `None`, **`make_dir`'den önce**.
- `rename`: `is_archived(new)` ise `None`, `storage.rename_dir`'den önce.

**3 · `create_project.py` — cümlenin seçimi.** `store.create` `None` dönerse `store.is_archived(name)`
sorulur; arşivse yeni cümle, değilse bugünkü.

**4 · `rename_project.py` — aynısı**, `new` için.

**5 · `ProjectsScreen.jsx` — satır.** `actionError` durumu; `handleArchive` ve `handleRestore`
`try/catch`; `toggleArchive` temizler; listenin üstünde `Icon.Warn` + `Note`.

**6 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

**7 · `npm run build --prefix queen-editor/frontend`** — ekran değişti, ve defter derlemiyor:
`dist` kaynakla **aynı** commit'e girer.

**8 · Commit.**

## Değişen dosyalar

`queen-editor/backend/features/projects/domain/name_rules.py`,
`queen-editor/backend/features/projects/data/project_store.py`,
`queen-editor/backend/features/projects/domain/usecases/create_project.py`,
`queen-editor/backend/features/projects/domain/usecases/rename_project.py`,
`queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`,
`queen-editor/frontend/dist/**`.
