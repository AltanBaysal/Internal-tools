# Madde 442 — Sürüm numarası V10, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** QueenAgent'ın çubuğunda *"QueenAgent V10"* yazar; `V8` aracın hiçbir yerinde kalmaz.

**Yaklaşım:** Değeri tutan test yok ve yazılmaz (spec, *Sınırlar*); var olan testler biçimi ve
çubuğun sabiti gösterdiğini tutuyor, değişiklikten sonra yeşil kalmalı. Dosyalar Edit ile değişir.

**Spec:** [m442](../specs/2026-10-09-queen-agent-m442-surum-v10-design.md)

## Her yere geçerli kurallar

- Kod ve yorumlar İngilizce.
- Yol haritasına ve queen-editor'e dokunulmaz.

---

## Görev 1: `version.js` — V10

- [ ] `VERSION = "V10"`; yorumdaki *"none of them says V8"* *"none of them says which run this is"*
  olur.

## Görev 2: yorumlar sayısız

- [ ] `version.test.js`: *"pinning "V8""* *"pinning the value"* olur; `v8, 8, V8.1, V8-beta`
  örnekleri sayısız söylenir.
- [ ] `Bar.test.jsx`: *"rather than of "V8""* *"rather than of a literal"* olur.

## Görev 3: arama, derleme, suite'ler

- [ ] `queen-agent` ağacında (node_modules ve dist dışında) `V8` aranır: sonuç yok.
- [ ] `npm run build --prefix queen-agent/frontend`; dist'in bundle'ında `V10` var, `"V8"` yok.
- [ ] Dört suite, birer birer: `python -m pytest queen-agent -q`, `npm test --prefix
  queen-agent/frontend`, `python -m pytest queen-editor -q`, `npm test --prefix
  queen-editor/frontend`. `test_dist_is_committed` dist commit'lenene kadar kırmızı kalır.
