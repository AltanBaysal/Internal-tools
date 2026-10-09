# Madde 225 · Beklerken ekran susmayacak — uygulamanın planı

**Spec:** [uygulama turu](../specs/2026-09-16-queen-editor-m225-bekleme-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı commit: `5f8e2dff`.

## Adımlar

**1 · `ProjectCard.jsx`** — `busy = null` özelliği. Doluysa tarih satırının yerinde o kelime, ve üç
düğme de `disabled`.

**2 · `ProjectsScreen.jsx`** — `working` durumu *(`{name, label}` ya da `null`)*; `handleArchive`
ile `handleRestore` başta kuruyor, **başarıda listeler okunduktan sonra**, hatada hemen kaldırıyor.
Karta `busy={working?.name === p.name ? working.label : null}` geçiyor.

**3 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

**4 · `npm run build --prefix queen-editor/frontend`**, `dist` kaynakla aynı commit'e girer.

**5 · Commit.**

## Değişen dosyalar

`queen-editor/frontend/src/features/projects/ProjectCard.jsx`,
`queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`,
`queen-editor/frontend/dist/**`.
