# Madde 496 — Başlıkta sürüm V11 yazar, plan

**Hedef:** `version.js` `V11` diyor; ekranların başlığı `Queen Editor V11`.

**Spec:** [m496](../specs/2026-10-27-queen-editor-m496-surum-v11-design.md)

## Kısıtlar

- Kaynakta değişen tek dosya `queen-editor/frontend/src/shared/version.js`, tek satırı; yorumu
  değişmez.
- Hiçbir test değişmez ya da eklenmez *(spec, "Testler")*.
- `dist/` aynı değişiklikle build'lenir.
- Takımlar teker teker koşar.

### Görev 1: Sayı

**Dosya:** `queen-editor/frontend/src/shared/version.js:7`

- [ ] `export const VERSION = "V10";` → `export const VERSION = "V11";`

### Görev 2: Build

- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] Yeni bundle'da `Queen Editor ` ile birlikte `V11` geçtiği, `"V10"` geçmediği taranır.

### Görev 3: Takımlar

- [ ] `npm test --prefix queen-editor/frontend`, sonra `python -m pytest queen-editor -q`.
- [ ] Beklenen: ikisi de yeşil. Commit'i ana ajan atar.
