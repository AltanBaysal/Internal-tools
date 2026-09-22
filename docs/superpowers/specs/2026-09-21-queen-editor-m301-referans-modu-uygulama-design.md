# Madde 301 — Video penceresinde referans modu, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m301 test turu](2026-09-21-queen-editor-m301-referans-modu-testler-design.md),
`166940b0` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## İki dosya

**`production_modes.js`** — videonun **neyden yapıldığı** yeni bir liste: `FROM_FRAME` *(Standart)*
ve `FROM_POOL` *(Referans)*. Kipler *(loop, sonrakine bağla)* bir videonun nerede bittiğini
söylüyor; bu, neyden yapıldığını. Aynı dosyada, çünkü ikisi de üretimin sözcükleri ve ikisini de
aynı pencere soruyor.

**`LayerPanel.jsx`** — bir `source` durumu. `FROM_POOL` seçiliyken:
- kapsam ve üretim modu satırları çizilmiyor;
- toplu prompt kutusu çiziliyor *(fotoğraf panelinin biçimi, `aria-label` ile)*;
- tahmin satırı `"N prompt × M varyant = K kart"`;
- basınca `onQueue(null, varyant, "reference", promptMetni)`.

**Prompt sayısı** kutunun kendisinden okunuyor: metin `["…", "…"]` olarak ayrıştırılıyor. Fotoğraf
paneli bu biçimi zaten kullanıyor, ve **sunucu aynı ayrıştırıcıyı** kendi tarafında koşturuyor
*(`prompt_list.py`)* — ekrandaki sayı bir tahmin, kural değil; kuyruğa kaçının girdiğini sunucu
söylüyor, bugün de öyle.

Ayrıştırılamayan liste **sayı yerine sebebini** yazıyor, ve basınca istek hiç gitmiyor: bugünkü
`refusalOf` zincirine bir sebep daha ekleniyor — pencerenin kendi kırmızı kartı.

## Kapsam dışı

Sunucu tarafı *(302, 303)*. Bu turda pencere isteği **tipiyle** yolluyor, o kadar.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil; `dist` aynı commit'te.
