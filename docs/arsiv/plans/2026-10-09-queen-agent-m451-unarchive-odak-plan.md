# Madde 451 — Unarchive'dan sonra odak, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Archived'da Unarchive'dan sonra odak sıradaki satırın ⋯'sine, satır kalmadıysa aramaya
geçer; reddedilen Unarchive'da odak olduğu yerde kalır.

**Yaklaşım:** Önce test, kırmızı görülür, sonra kod. Dosyalar Edit ile değişir.

**Spec:** [m451](../specs/2026-10-09-queen-agent-m451-unarchive-odak-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları İngilizce.
- Arka uca, yol haritasına ve queen-editor'e dokunulmaz.

---

## Görev 1: `AllProjectsScreen.jsx` — Unarchive odağı devreder

- [ ] `AllProjectsScreen.test.jsx`, 450'nin bölümünün altında, `onScreen`'le: Archived'da Unarchive'dan
  sonra odak sonraki satırın ⋯'sinde (`preventScroll`); aramada aramanın bıraktığı sonraki satırda; son
  satırda ve tek satırda aramada, `focus` seçeneksiz; reddedilen Unarchive'da odak basışta verildiği
  ⋯'de kalır. Kırmızı (son test hariç: odak bugün gövdeye düşüyor, o da kırmızı).
- [ ] `AllProjectsScreen.jsx`: `archive`'da `if (toArchive)` kalkar, `handOverFrom(id)` her basışta;
  `handOverFrom`'un üstündeki yorum iki basışı ve neden ikisinin de satırı gösterilen sekmeden
  çıkardığını söyler. Yeşil.
- [ ] Test: basılan satırın ⋯'si bulunamazsa odak aramada, ilk ⋯'de değil. Kırmızı.
- [ ] `handOverFrom`: `at === -1` ise sonraki yok, arama. Reddin yorumu `archive`'ın üstüne. Yeşil.

## Görev 2: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`; `dist` `git add` ile sahnelenir.
- [ ] Dört suite, birer birer: `python -m pytest queen-agent -q`, `npm test --prefix
  queen-agent/frontend`, `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
