# Madde 319 — Havuzun sırası ne gösteriyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

Havuz 318'den beri ortada, ama kutuları sol sütunun ölçüsünde: 68 × 48, numarasız. Sıraların
arkasında tek bir `Ekle` var, üç tip için ortak *(ReferencePanel.jsx)*.

## Kurallar

1. **Her referans 144 × 108 bir kutu;** sol üstünde yuva numarası *(sunucunun `slot`'u — `<Picture N>`'in
   `N`'si)*, sağ üstünde `×`, altında dosya adı, klipse süresi.
2. **Son referansın ardından tek bir `+ Ekle` kartı**, sıra dolana kadar; dolu sırada yok.
3. **Boş havuz üç sırayı yalnız `Ekle` kartlarıyla gösteriyor.**
4. **Bu maddede kart yalnız görünüyor.** Seçici, tek dosya, `Yükleniyor…` 320'nin; bugünkü ortak
   `Ekle` 320'ye kadar yükleme yolu olarak kalıyor. Silinen referansın bıraktığı boşluk da 321'e kadar
   çiziliyor, yeni ölçüde.

## Adlar

Kart `data-add="<tip>"` taşıyor *(`picture` · `video` · `audio`)*; kutular bugünkü gibi
`data-reference="<ad>"`.

## Yazılacak testler — `ReferencePanel.test.jsx`, yeni blok *"what a row shows"*

1. **Her referans 144 × 108 çiziliyor, yuva numarası üstünde** — ikinci fotoğrafın kutusunda `2`;
   resmin genişliği 144 px, yüksekliği 108 px.
2. **Sıranın son referansını tek bir `Ekle` kartı izliyor** — kartın önündeki kardeş son kutu.
3. **Dolu sırada `Ekle` kartı yok** — üç videolu sırada yok, fotoğraf sırasında var.
4. **Boş havuz üç sırayı yalnız `Ekle` kartlarıyla gösteriyor** — üç kart, hiç kutu yok.

**Değişen:** yok. **Bekçiler:** sıra başlıkları, resim, süre, boşluk, sürükleme, yükleme, ret ve
silme testleri — kutunun içeriği ve davranışı değişmiyor, yalnız ölçüsü.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend` vitest'te 1–4 kırmızı, öteki üç satır yeşil.
