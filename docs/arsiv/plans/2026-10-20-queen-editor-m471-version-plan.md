# Madde 471 — Başlıkta sürüm V10 yazar, plan

**Hedef:** `version.js` `V10` diyor; ekranların başlığı `Queen Editor V10`.

**Spec:** [m471](../specs/2026-10-20-queen-editor-m471-version-design.md)

## Kısıtlar

- Kaynakta değişen tek dosya `queen-editor/frontend/src/shared/version.js`, tek satırı; yorumu
  değişmez.
- Hiçbir test değişmez ya da eklenmez *(spec, "Testler")*.
- `dist/` aynı değişiklikle build'lenir.
- Takımlar teker teker koşar.

### Görev 1: Sayı

**Dosya:** `queen-editor/frontend/src/shared/version.js:7`

- [ ] `export const VERSION = "V9";` → `export const VERSION = "V10";`

### Görev 2: Build

- [ ] `npm run build --prefix queen-editor/frontend`

### Görev 3: Takımlar

- [ ] `npm test --prefix queen-editor/frontend`, sonra `python -m pytest queen-editor -q`.
- [ ] Beklenen: ikisi de yeşil. Commit'i ana ajan atar.
