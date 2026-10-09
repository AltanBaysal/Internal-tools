# Madde 300 — Sıralama ve boşluk, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m300 test turu](2026-09-21-queen-editor-m300-sira-ve-bosluk-testler-design.md),
`d81f6b1e` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Dosyalar

**`domain/references.py`** — iki saf kural:
- `placed(order, rows)`: her satıra `slot` verir. Sıradaki adlar yuvaları belirler *(dosyası
  olmayan ad yuvasını boş bırakır)*, sırada geçmeyen dosyalar sona, ad sırasıyla eklenir.
- `gaps(rows)`: 1..N arasında eksik yuvası olan tipler. **302** bunu soracak.

**`data/reference_order_store.py`** — `references.json`, projenin kökünde, `order.json`'ın yanında.
Okunamayan dosya *"sıra yok"* demek: bir projenin yalnız sıra dosyası yüzünden açılamaması
`DriveOrderStore`'un da reddettiği bir şey.

**`domain/usecases/`** — üç senaryo sıra deposunu alıyor, ve yeni bir tane doğuyor:
`save_reference_order`. Gönderilen sıra **havuzdaki adlara göre süzülüyor**: bayat bir sekme
dosyaya hayalet bırakamaz *(`save_order`'ın kuralı)*. Süzgeç dosyası olmayan adı da eler — yani
kullanıcı sürükleyip yeni sırayı yollayınca ölü ad düşer ve boşluk kapanır.

**`presentation/reference_routes.py`** — `PUT …/references/order`.

**`shared/api.js`** — `saveReferenceOrder`.

**`ReferencePanel.jsx`** — karolar sürüklenebilir *(galerinin kendi HTML5 biçimi)*, boş yuva
çiziliyor, ve bırakma yeni sırayı yolluyor. Sıra **tipin kendi satırı** içinde: bir videoyu
fotoğrafların arasına sürüklemek diye bir şey yok.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil; `dist` aynı commit'te yeniden üretilir.
