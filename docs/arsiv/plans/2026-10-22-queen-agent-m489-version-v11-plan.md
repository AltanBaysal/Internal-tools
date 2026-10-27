# Madde 489 — Başlıkta sürüm V11 yazar, plan

**Hedef:** `version.js` `V11` diyor; üst çubukta `QueenAgent V11`.

**Spec:** [m489](../specs/2026-10-22-queen-agent-m489-version-v11-design.md)

## Kısıtlar

- Kaynakta değişen tek dosya `queen-agent/frontend/src/shared/version.js`, tek satırı; yorumu
  değişmez.
- Hiçbir test değişmez ya da eklenmez *(spec, "Testler")*.
- `dist/` aynı değişiklikle build'lenir.
- Takımlar teker teker koşar.

### Görev 1: Sayı

**Dosya:** `queen-agent/frontend/src/shared/version.js:11`

- [ ] `export const VERSION = "V10";` → `export const VERSION = "V11";`

### Görev 2: Build

- [ ] `npm run build --prefix queen-agent/frontend`
- [ ] `queen-agent/` altında, `node_modules/` dışında `V10` kalmadığı taranır (eski bundle dahil).

### Görev 3: Takımlar

- [ ] `npm test --prefix queen-agent/frontend`, sonra `python -m pytest queen-agent -q`.
- [ ] Beklenen: ikisi de yeşil. Commit'i ana ajan atar.
