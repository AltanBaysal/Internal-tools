# Madde 412 — Uygulama V8 diyecek, test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Dört ekranın dördünün de başlığında tam `version.js`'in dediğini çizdiğini söyleyen
testler. Kırmızı yok — sebebi spec'te, ve gizlenmiyor.

**Mimari:** Proje listesinin, proje ekranının ve karenin sayfasının başlık testi, 285'teki export
testi gibi `VERSION`'ı içe alır ve ekranda `` `Queen Editor ${VERSION}` `` arar. Değer hiçbir teste
yazılmaz.

**Araçlar:** vitest, Testing Library.

**Spec:** [m412 test turu](../specs/2026-10-01-queen-editor-m412-surum-v8-testler-design.md)

## Genel kısıtlar

- Yalnız testler; `version.js` ve ekranlar bu turda değişmez.
- `"V8"` ya da başka bir sayı hiçbir teste yazılmaz *(248)*.
- `ExportScreen.test.jsx` ve `version.test.js` değişmez.
- Test adları ve yorumlar İngilizce.
- Dört satır CLAUDE.md'deki gibi, paralel, borusuz, daraltılmadan.

---

### Görev 1: Üç başlık testi modülün değerine bağlanır

**Dosyalar:**
- Değiştir `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx:12-13, 63-70`
- Değiştir `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx:6-7, 215-221`
- Değiştir `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx:13-14, 157-164`

- [ ] Üç dosyada da `router.js`'in import satırının hemen altına, export testindeki sırayla:

```jsx
import { VERSION } from "../../shared/version.js";
```

- [ ] Üç dosyada da `puts the version next to the name` testinin yorumu ve beklentisi. Bugünkü:

```jsx
    // The shape, not the value: the number is shared/version.js's to say (madde 248).
    ...
    expect(screen.getByText(/^Queen Editor V\d+$/)).toBeTruthy();
```

  olacak:

```jsx
    // The module's value, not a pattern: the number is shared/version.js's to say (madde 248), and
    // a number typed into this screen would pass a pattern just as well (madde 412, as 285 did for
    // the export screen). The value itself is not pinned here: it is a decision, and pinning it
    // would put one decision in two places.
    ...
    expect(screen.getByText(`Queen Editor ${VERSION}`)).toBeTruthy();
```

  Testlerin açılışı (`openScreen()`, `renderScreen()`, `open("0_a")`) değişmez.

### Görev 2: Takımı koş ve commit'le

- [ ] Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: **kırmızı yok**, dört satır yeşil — ekranlar bugün de modülü okuyor; bu tur bağı
  tutuyor, sayıyı değil.
- [ ] Commit, spec ve plan ile: `test(queen-editor): Madde 412 -- …` — mesaj kırmızı olmadığını ve
  sebebini söyler. Çift tırnak yok; son satır
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
