# Madde 301 — Video penceresinde referans modu, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Pencerenin şekli 21 Eylül'de konuşuldu: *"video üretim penceresinde
referans ve standart diye seçenekler olur… prompt yeri fotoğraftaki gibi toplu prompt alır, aynı
yapıda."*

## Madde ne diyor

> *Standart / referans* seçimi; referans seçilince pencere toplu prompt ve varyant alıyor, loop ile
> sonrakine bağlama kapanıyor. Satır *"N prompt × M varyant = K kart"* diyor.

## Neden yeni bir seçim, yeni bir kip değil

Bugünkü *"üretim modu"* satırı bir videonun **nerede biteceğini** seçiyor: standart, loop,
sonrakine bağla. Referans o soruya bir cevap değil — videonun **neyden yapıldığını** değiştiriyor:
karenin fotoğrafından değil, havuzdan. O yüzden üstte ayrı bir satır: **Standart / Referans**.

Referans seçilince pencere başka bir pencere oluyor:

- **Kapsam satırı gider.** Ortada kare yoktur; üretim kart doğurur *(303)*.
- **Üretim modu satırı gider.** Loop ve sonrakine bağlama referansla yok *(yol haritasının kararı)*.
- **Toplu prompt kutusu gelir** — fotoğraf panelindeki biçimin aynısı, çünkü kullanıcı onu zaten
  böyle yazıyor.
- **Varyant satırı kalır.**
- **Satır sayar:** *"2 prompt × 3 varyant = 6 kart"*.

## Sunucu tarafı bu maddede yok

Buton isteği **referans tipiyle** gönderiyor; onu anlayan uç **302 ve 303**'te geliyor. Bu maddede
basılırsa sunucu tanımadığı tipi reddeder ve pencere kendi kırmızı kartında bunu söyler — koşu
bitmeden kullanıcıya gitmiyor *(CLAUDE.md 10: kullanıcı koşunun sonunda deniyor)*.

## Yazılacak testler — `LayerPanel.test.jsx`

1. **video penceresi Standart/Referans soruyor, ses penceresi sormuyor** — sesin havuzla işi yok.
2. **Referans seçilince kapsam ve üretim modu satırları kapanıyor.**
3. **Referans seçilince toplu prompt kutusu geliyor.**
4. **satır kartları sayıyor** — *"2 prompt × 3 varyant = 6 kart"*.
5. **okunamayan prompt listesi sayı yerine sebebini söylüyor.**
6. **boş prompt listesiyle basınca istek gitmiyor**, ve sebep yazıyor.
7. **basınca prompt'lar ve varyant referans tipiyle gidiyor.**

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend` kırmızı.
