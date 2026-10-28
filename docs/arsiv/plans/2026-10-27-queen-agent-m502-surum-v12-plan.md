# Madde 502 — Başlıkta sürüm V12 yazar, plan

**Hedef:** `version.js` `V12` diyor; üst çubukta `QueenAgent V12` yazıyor.

**Spec:** [m502](../specs/2026-10-27-queen-agent-m502-surum-v12-design.md)

## Kısıtlar

- Kaynakta değişen tek dosya `queen-agent/frontend/src/shared/version.js`, tek satırı; yorumu
  değişmez.
- Hiçbir test değişmez ya da eklenmez *(spec, "Testler")*.
- `dist/` aynı değişiklikle build'lenir.
- Takımlar teker teker koşar.

### Görev 1: Sayı

**Dosya:** `queen-agent/frontend/src/shared/version.js:11`

- [ ] `export const VERSION = "V11";` → `export const VERSION = "V12";`

### Görev 2: Build

- [ ] `npm run build --prefix queen-agent/frontend`
- [ ] Yeni bundle'da `bar__version` ile birlikte `V12` geçtiği, `V11` geçmediği taranır.

### Görev 3: Takımlar

- [ ] `npm test --prefix queen-agent/frontend`, sonra `python -m pytest queen-agent -q`.
- [ ] Beklenen: ikisi de yeşil. Commit'i ana ajan atar.
