# Madde 12 — Odak halkası her yerde · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 12](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** sapma 86 · `HANDOFF.md` §9
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Açık soru yok; kapsam bir yerde daraltılıyor

Sapma 86: composer'ın metin alanına sekmeyle gelindiğinde halka hiç çizilmiyor. Sebebi tek satır —
`.composer__input { outline: none }`. Arama kutusu Madde 2'de silindiği için sapmanın öbür yarısı
zaten yok.

**`.row-x:focus-visible { opacity: 1 }` kalıyor ve kuralı çiğnemiyor.** O satır bir odak *halkası*
yazmıyor; hover'da beliren bir denetimi klavyeyle gelindiğinde de **görünür** kılıyor. Kaldırılsaydı
sekmeyle dolaşan biri var olmayan bir düğmeye odaklanmış olurdu. Kural "hiçbir bileşen kendi odak
halkasını yazmaz"dır; görünürlük ayrı bir sorudur.

**Satırların kendisi bu maddede odaklanabilir olmuyor.** Sohbet ve dosya satırları bugün `div`;
gerçek düğmeye dönüşmeleri **Madde 34**'ün işi ve orada `title` ile birlikte ele alınıyor.

---

## 1 · Ne değişir

`.composer__input`'tan `outline: none` gider. Halka `shared/app.css`'teki tek `:focus-visible`
kuralından gelir — 2px vurgu rengi, 2px boşluk.

Başka hiçbir yerde odak stili yazılmıyor; bu maddeden sonra da yazılmayacak.

---

## 2 · Katman denetimi

Tek dosya, tek satır. Kural gevşemiyor: odak stilinin tek evi `shared/app.css` olmaya devam ediyor.

---

## 3 · Kabul ölçütü

1. `.composer__input` `outline` yazmaz.
2. `app.css` tam olarak bir `:focus-visible` kuralı taşır ve halka 2px vurgu rengidir.
3. Ön yüzde `.row-x:focus-visible` dışında `focus` geçen bir kural kalmaz — o da yalnız
   `opacity` yazar.

## 4 · Risk

Yok denecek kadar az. Tek dikkat: halka `textarea`'nın kendi kenarına çizilecek, composer kartının
kenarına değil — tasarımın odak kuralı öğeye bağlı, kaba değil.
