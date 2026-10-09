# Madde 224 · Arşiv ekranı kendi düğmelerini taşıyacak — uygulamanın planı

**Spec:** [uygulama turu](../specs/2026-09-16-queen-editor-m224-arsiv-ekrani-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı commit: `03e0f03c`. Bu tur onu yeşile çeviriyor.

## Adımlar

**1 · `ProjectsScreen.jsx` — başlıktaki öbek.** `justifySelf: "end"` div'inin içi `inArchive`'a göre
ikiye ayrılır: arşivde tek bir ghost *Arşivden çık*, projelerde bugünkü *Arşiv* + *Yeni proje*. İkisi
de `toggleArchive`'ı çağırır.

**2 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

**3 · `npm run build --prefix queen-editor/frontend`** — `dist` kaynakla aynı commit'e girer.

**4 · Commit.**

## Değişen dosyalar

`queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`,
`queen-editor/frontend/dist/**`.
