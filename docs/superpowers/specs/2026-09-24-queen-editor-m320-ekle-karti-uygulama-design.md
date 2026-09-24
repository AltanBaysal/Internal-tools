# Madde 320 — Ekleme: sıranın kendi `Ekle` kartı, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-a` *(Kol A)* · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m320 test turu](2026-09-24-queen-editor-m320-ekle-karti-testler-design.md),
`1bf92234`.

## Sunucu

- **`add_references(…, files, row=None)`** — `row`, dosyanın seçildiği sıranın tipi. Dosyanın tipi
  okunur okunmaz, ad çözülmeden: `row` verilmiş ve dosyanın tipi başkaysa
  `UnknownReference(f"{name} {SAID[row]} yuvasına giremez — bu dosya {SAID[kind]}.")`. Yeri tasarımın
  sırası: tanınmayan → yanlış sıra → süresi okunamayan → sınırlar. Cümledeki ad tarayıcının
  gönderdiği ad — dosya yazılmıyor, havuzun vereceği ad hiç doğmuyor. `row` yoksa bugünkü gibi, her
  dosya kendi tipine.
- **`UnknownReference`, `PoolLimit` değil:** ret dosyanın **ne olduğuyla** ilgili, havuzun
  doluluğuyla değil; kapı ikisini zaten aynı 400'le geçiriyor. Sınıfın docstring'i yeni durumu da
  söylüyor.
- **`SAID[row]`, `.get` değil:** ekran yalnız üç tipi yolluyor; olmayan bir tipe bekçi yok.
- **Kapı** formun `kind` alanını `row=` diye geçiriyor; alan yoksa `None`.

## Ekran

### `api.js`

`uploadReferences(project, files, kind)` — `kind` formun alanı. Koşulsuz: tek çağıran havuzun kartı,
ve kart her zaman bir sıranın.

### `ReferencePanel.jsx`

- **`ROWS`** her sıraya `accept` *(`image/*` · `video/*` · `audio/*`)* ve seçicinin adını
  *(`fotoğraf ekle` · `video ekle` · `ses ekle`)* ekliyor. `accept` yalnız tarayıcının seçicisini
  daraltıyor — seçicide *Tüm dosyalar*'a geçilebilir; dosyanın o sıraya girip giremeyeceği sunucunun
  kuralı *(FOUNDATION 4)*, yeni cümle de bunun için.
- **Kart `AddCard`** — `Tile`'ın yanında küçük bir bileşen: `data-add` kutusu ve hemen ardında gizli
  `<input type="file">` *(`multiple` yok)*; kutuya basmak kendi `ref`'iyle seçiciyi açıyor. Kutunun
  imleci `pointer`.
  - **Label değil:** label'ın kendi sözü içindeki girişin adı olur — üç kartın sözü de `Ekle`, yani üç
    seçici de `Ekle` diye anılırdı. Her seçici kendi tipinin adını taşıyor *(test 9)*.
  - **Seçici kutunun içinde değil, ardında:** içindeyken seçicinin tıklaması kutuya kabarır ve kutu
    seçiciyi ikinci kez tıklar.
  - Klavyeyle ulaşılmıyor — bugünkü ortak `Ekle` de ulaşılmıyordu *(`display: none`)*.
- **`uploading`** — yoldaki sıranın tipi ya da `null`. O kartın yüzü `qe-spinner` ve `Yükleniyor…`
  *(uygulamanın `Ekleniyor…` düğmelerindeki halka)*; `uploading` doluyken **üç seçici de
  `disabled`**. `busy` yalnız silmenin kalıyor — silme yoldayken onay penceresi ekranı zaten örtüyor.
- **`handlePick(kind, event)`** dosyayı sıranın tipiyle yolluyor; başındaki `setError(null)` sonraki
  seçimde reddi temizliyor. Seçici `multiple` taşımadığı için liste en çok tek dosya.
- **Ret kartı** sıraların üstünde, `PANEL`'in ilk çocuğu. Silme onu bugün de temizliyor.
- **Ortak `Ekle` gidiyor**, 319'un *"ne yaptığı 320'nin"* yorumuyla birlikte.

### `app.css`

`.qe-spinner`'ın yorumu yeni yerini de söylüyor.

## Dist

Kolda derlenmez — [yol haritası](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md), *320–324 iki
paralel kolda*: birleşme commit'i bir kez derler.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
