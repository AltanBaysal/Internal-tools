# Madde 412 — Uygulama V8 diyecek, uygulama turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `version.js` `V8` diyor; dört ekranın başlığı `Queen Editor V8`.

**Mimari:** Sayı tek yerde; ekranlar onu okuyor ve test turundan beri dördü de tam onu çizmeye bağlı.

**Araçlar:** vitest.

**Spec:** [m412 uygulama turu](../specs/2026-10-01-queen-editor-m412-surum-v8-uygulama-design.md)

## Genel kısıtlar

- Değişen tek dosya `queen-editor/frontend/src/shared/version.js`, tek satırı.
- Hiçbir test değişmez.
- `dist/` bu şeritte build'lenmez; koşuyu yürüten birleştirmede bir kez build'ler.
- Dört satır CLAUDE.md'deki gibi, paralel, borusuz, daraltılmadan.

---

### Görev 1: Sayı

**Dosya:** Değiştir `queen-editor/frontend/src/shared/version.js:7`

- [ ] Bugünkü:

```js
export const VERSION = "V6";
```

  olacak:

```js
export const VERSION = "V8";
```

  Dosyanın yorumu (1–6. satırlar) değişmez.

### Görev 2: Takımı koş ve commit'le

- [ ] Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: dört satır yeşil.
- [ ] Commit, spec ve plan ile: `feat(queen-editor): 412 -- …`. Çift tırnak yok; son satır
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
