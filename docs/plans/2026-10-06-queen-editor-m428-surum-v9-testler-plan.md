# Madde 428 — Başlıkta sürüm V9 yazar, test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Bu turda tutulacak yeni bir olgu yok: dört ekranın dördünün de başlığında tam
`version.js`'in dediğini çizdiği 412'den beri testle tutuluyor. Kırmızı yok — sebebi spec'te, ve
gizlenmiyor.

**Mimari:** Sayı tek yerde, `frontend/src/shared/version.js`'te. Dört başlık testi `VERSION`'ı içe
alıp ekranda `` `Queen Editor ${VERSION}` `` arıyor; `version.test.js` yalnız biçimi tutuyor. Değer
hiçbir teste yazılmaz *(248)*.

**Araçlar:** vitest, Testing Library.

**Spec:** [m428 test turu](../specs/2026-10-06-queen-editor-m428-surum-v9-testler-design.md)

## Genel kısıtlar

- Yalnız testler; `version.js` ve ekranlar bu turda değişmez.
- `"V9"` ya da başka bir sayı hiçbir teste yazılmaz *(248)*.
- Hiçbir test dosyası değişmez: `version.test.js`, `ProjectsScreen.test.jsx`,
  `ProjectScreen.test.jsx`, `PhotoDetail.test.jsx`, `ExportScreen.test.jsx` olduğu gibi kalır.
- Dört satır CLAUDE.md'deki gibi, paralel, borusuz, daraltılmadan.
- `dist/` bu şeritte build'lenmez.

---

### Görev 1: Bağın bugün tutulduğunu doğrula

**Dosyalar:** okunur, değişmez —
- `queen-editor/frontend/src/shared/version.test.js:9`
- `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx:13, 72`
- `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx:7, 224`
- `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx:14, 166`
- `queen-editor/frontend/src/features/photo_generation/ExportScreen.test.jsx:11, 71`

- [ ] Dört başlık testinin de `VERSION`'ı `../../shared/version.js`'ten içe aldığını ve tam şunu
  aradığını gör:

```jsx
    expect(screen.getByText(`Queen Editor ${VERSION}`)).toBeTruthy();
```

- [ ] `version.test.js`'in yalnız biçimi tuttuğunu gör:

```js
  expect(VERSION).toMatch(/^V\d+$/);
```

- [ ] `queen-editor/` altında `dist/` dışında `V8` yazan tek yerin `version.js` olduğunu gör
  (Grep: `\bV8\b|Queen Editor V`, `frontend/dist/**` hariç).

### Görev 2: Takımı koş ve commit'le

- [ ] Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: **kırmızı yok**, dört satır yeşil — ekranlar bugün de modülü okuyor; testler bağı
  tutuyor, sayıyı değil.
- [ ] Commit, yalnız spec ve plan: `test(queen-editor): Madde 428 -- …` — mesaj kırmızı olmadığını
  ve sebebini söyler. Çift tırnak yok; son satır
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
