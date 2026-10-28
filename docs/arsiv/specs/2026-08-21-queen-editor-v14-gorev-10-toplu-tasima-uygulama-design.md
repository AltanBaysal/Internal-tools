# v14 · Görev 10 — Toplu kart taşıma · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-10-toplu-tasima-testler-design.md) —
kararlar orada verildi ve commit edilmiş dokuz test onları tarif ediyor.

## Değişen dosya

Tek dosya: **`features/photo_generation/Gallery.jsx`**. Dört küçük değişiklik.

### 1 · Taşınanların listesi, render başına bir kez

Bileşenin gövdesinde, karo döngüsünün üstünde:

> Sürükleme başlamamışsa boş. Başlamışsa: sürüklenen kart seçiliyse galeri sırasındaki seçili
> kimlikler, değilse yalnız o kart.

Döngünün içinde değil, çünkü her karo için yeniden hesaplanacak bir liste değil — sürüklemenin
kendisi hakkında tek bir gerçek.

### 2 · `handleDrop` bloğu taşıyor

Bugünkü iki `splice` yerine: taşınanlar süzülerek çıkarılıyor, sonra blok `to` indeksine
yerleştiriliyor. Tek kart bu kuralın bir elemanlı hâli, dolayısıyla bugünkü davranış aynen duruyor.

Sunucuya gitme kararı **sonucun karşılaştırılmasıyla**: yeni dizi eskisiyle aynıysa çağrı yok.
Bugünkü `from === to` koruması bunun içinde kalıyor.

Sürüklenenlerin listesi burada yeniden hesaplanmıyor — 1. maddedeki değer okunuyor, yani "kim
taşınıyor" sorusunun tek bir cevabı var.

### 3 · Sürüklenen görünümü bloğun tamamında

`dragging`, "bu karo taşınanlardan biri mi" oluyor. Efektin kendisi değişmiyor.

`isSlot` bugünkü koşulunu koruyor (`!dragging`), ve genişleyen `dragging` sayesinde yuva bloğun
hiçbir kartının üstünde doğmuyor.

### 4 · Seçim açıkken sürükleme açık

`draggable={!selecting}` → `draggable`. Basış hâlâ seçimi değiştiriyor; tamamlanan bir sürükleme
`click` üretmiyor ve kodun bugünkü yorumu bunu zaten söylüyor. O yorumun "seçim varken basış
seçimdir" cümlesi artık yanlış — düzeltiliyor.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor.
