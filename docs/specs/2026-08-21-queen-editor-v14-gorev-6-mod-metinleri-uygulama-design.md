# v14 · Görev 6 — Tahmin ve onay metinleri moda göre değişiyor · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-6-mod-metinleri-testler-design.md) —
kararlar orada verildi ve commit edilmiş on bir test onları tarif ediyor.

## Değişen dosya

Tek dosya: **`features/photo_generation/LayerPanel.jsx`**.

### `WORDS` bir alan kazanıyor

`held` — o katmanı taşıyan bir kareyi niteleyen sıfat. Video tarafında `videolu`, ses tarafında
`sesi olan`. Kopya uyarısındaki tek fark bu kelime, ve `WORDS` zaten katmanın kendi sözlüğü.

### `MODE_WORDS` — modun kendi kelimeleri

Modül seviyesinde küçük bir tablo, yalnız iki satır:

```
loop   → { noun: "loop video",  tail: "her video kendine döner." }
linked → { noun: "bağlı video", tail: "her video sıradaki karede biter." }
```

Standart'ın satırı **yok**. Onun kelimeleri katmanın kendi kelimeleri (`noun`, `own`) ve bu tabloda
katman diye bir şey yok — standart buraya yazılsaydı iki satır gerekirdi, biri video biri ses için,
ve ikisi de `WORDS`'te zaten duran kelimelerin kopyası olurdu.

Satırı olmayan modun kelimeleri katmandan geliyor. Ses paneli mod satırını hiç çizmediği için modu
her zaman standart kalıyor; yani bu tablo ses tarafında hiç okunmuyor ve orada ayrı bir koşula gerek
kalmıyor.

### Cümlenin kurulması

Üç parça, sırayla:

1. **Sayı** — `owed`, bugünkü hesap.
2. **İsim** — modun `noun`'u, yoksa katmanın `noun`'u.
3. **Kuyruk** — kapsamda o katmanı taşıyan kare varsa kopya uyarısı, yoksa modun `tail`'i, o da
   yoksa katmanın kendi satırı (`her kare kendi ${own} alır.`).

Kopya sayısı kapsamdan çıkıyor: `scoped` içinde o katmanı taşıyanlar. *"Videosu olmayanlar"* kapsamı
onları zaten dışarıda bıraktığı için sayı orada kendiliğinden sıfır.

### Yeşil onayın durumu

`added` artık bir sayı değil, `{ count, mode }`. İstek gönderilirken o anki mod da kaydediliyor ve
kart onu okuyor. Kart on saniye duruyor; canlı modu okusaydı, arada satıra dokunulduğunda olmamış
bir üretimi haber verirdi.

`null` hâlâ "onay yok" demek — sayı ile mod ayrı iki duruma bölünseydi ikisinin birlikte
temizlendiğine güvenmek gerekirdi.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor.
