# v14 · Görev 13 — Seçim barının görünümü · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-13-secim-bari-testler-design.md) —
kararlar orada verildi ve commit edilmiş dört test onları tarif ediyor.

## Değişen dosya

Tek dosya: **`features/photo_generation/Gallery.jsx`**. İki değişiklik.

### 1 · Barın biçimi

`BAR` sabiti iki şey değiştiriyor:

- `gap: 14` → `10`. Bar üç düğmeyle tasarlanmıştı; bugün altı taşıyor (Fark 83).
- `whiteSpace: "nowrap"` geliyor. İki işi birden yapıyor: hiçbir düğmenin yazısı ikiye bölünmüyor,
  ve esnek bir öğe kendi `min-content` genişliğinin altına inmediği için düğmeler birbirinin
  içine de sıkışmıyor.

Öğelerin ikinci satıra düşmemesi için satır **yazılmıyor**: `display: flex` sarmayı zaten kapalı
getiriyor, ve hiçbir şey yapmayan bir kural kod olarak durmaz.

### 2 · Katman düğmelerinin koşulu

Bugünkü koşul "o katmanı taşıyan en az bir kare seçili" idi. Önüne bir koşul daha geçiyor:
**seçimde üretilmemiş kare yok.**

`chosenQueued` zaten hesaplanıyor — silme penceresinin üç hâlini ayıran şey o — yani yeni bir soru
sorulmuyor, sorulmuş olanın cevabı bir yerde daha okunuyor.

Koşul `LAYER_ACTIONS.map`'in **dışına** çıkıyor, içine değil: soru katman başına değil seçim
başına, ve iki düğme için iki kez sorulması aynı cevabın iki kez yazılması olurdu.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor, yol haritası 13/31 oluyor. Barın
konumu (Fark 84) bu maddede değişmiyor ve sorusu kullanıcıya soruluyor.
