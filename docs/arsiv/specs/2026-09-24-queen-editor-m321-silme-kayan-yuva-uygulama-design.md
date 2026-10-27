# Madde 321 — Silme: × hemen siliyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-a` *(Kol A)* · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m321 test turu](2026-09-24-queen-editor-m321-silme-kayan-yuva-testler-design.md),
`f311de83`.

**FOUNDATION 1'den bilinçli ayrılış.** İlke *"every destructive action is explicit and confirmed"*;
× onaysız siliyor. Kullanıcının kararı *(24 Eylül — "yıkıcı bir eylem değil, user geri çok hızlı
koyabilir")*, [yol haritasının](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) 321 satırında.
Kodun yorumu bu satırı gösteriyor, ilkeyi tekrarlamıyor.

## Sunucu

- **`references.placed`** — sıradan yalnız havuzda duran adlar sayılıyor:
  `[name for name in order.get(kind, []) if name in held]`. Yuvalar her zaman 1'den sıkı; Drive'dan
  elle silinmiş bir ad yuva tutmuyor *(test 1)*. `isinstance(name, str)` süzgeci gidiyor: `in held`
  yalnız havuzun adlarını geçiriyor, ve sıra belgesi metin olmayanları okurken zaten atıyor
  *(`DriveReferenceOrderStore.read`)*.
- **`references.gaps` gidiyor** — tek okuyucusu üretimin reddiydi.
- **`remove_reference`** dosyayı sildikten sonra sırayı adsız yazıyor:
  `{kind: [one for one in names if one != name] for kind, names in orders.read(project).items()}`.
  Sunucu sırayı sıkıştırıyor; aynı adla sonradan gelen dosya sonda *(test 3)*. Koşulsuz yazılıyor —
  ad sırada olmasa da; belge yalnız sıra tutuyor, aynı içeriği yeniden yazmak bir şey kaybettirmiyor.
  Havuzdaki bir dosya olmayan ad hâlâ hata değil *(iki kez silmek)*.
  - **Seçilmeyen yol:** silmeden sonra sırayı havuzun listesinden baştan yazmak *(`save_reference_order`
    gibi)*. Drive'dan elle silinmiş ölü adları da temizlerdi, ama listeyi iki kez okur — her klibe bir
    `ffprobe` daha — ve kullanıcının hiç sürüklemediği dosyaların ada göre sırasını belgeye dondururdu.
- **`queue_references`** boşluk reddini ve onu anlatan satırları siliyor; kalan iki ret — H3 yok,
  havuz boş — yerinde. Boş havuz cümlesine dokunulmuyor: Kol B'nin *(324)*.
- **Kapı:** `post_reference_run`'ın yorumu *"Five refusals"* → *"Four refusals"*.

## Ekran — `ReferencePanel.jsx`

- **× hemen siliyor:** `Tile`'ın `onRemove`'u doğrudan `handleRemove(name)`; `asking`, `busy`,
  `ConfirmModal` ve importu gidiyor. Cevap gelince havuz ondan çiziliyor ve ret kartı temizleniyor
  *(bugünkü `setError(null)`, test 8)*; silme başarısızsa sunucunun cümlesi aynı kartta.
- **Silme yoldayken bekleme hâli yok** — tasarımda da yok *(sayfanın ×'i anında)*. İkinci bir ×
  kendi isteğini yolluyor; son gelen cevap havuzun o anki hâli.
- **Boş yuva çizimi gidiyor:** `slotted`, `HOLE`, `N. yuva boş`. Sıra, sunucunun gönderdiği satırlar;
  numara `row.slot` — sunucunun *(FOUNDATION 4)*. `ADD` `HOLE`'dan türüyordu: ölçüleri kendi üstüne
  alıyor, görünüşü değişmiyor.
- **Sürükleme:** `handleDrop`'ta boşluğu yer sayan satır ve `Math.min` gidiyor — `splice` dizinin
  ötesine zaten sona ekliyor. Docstring'in *"ölü adlar … boşluk böyle kapanır"* cümlesi gidiyor.
  Sürüklemenin kendisi 322'nin.
- **Kol B'nin satırları** *(bileşenin docstring'i, imza, havuzun `useState`'i, `setPool`)*: dokunulmuyor.
  Silinen `asking`/`busy` satırları onlardan `error` satırıyla ayrılıyor.

## Doğruluğunu yitiren yorumlar

| Dosya | Olacak |
|---|---|
| `references.py` — `placed` | Yalnız havuzdakiler sayılıyor, ardındakiler kayıyor *(madde 321)* |
| `list_references.py` — modül | Satırın yuvası kendi sırasındaki yeri; boşluk, çizim, ret sözü gidiyor |
| `remove_reference.py` — modül | Ad sıradan da çıkıyor, ardındakiler kayıyor; iki kez silmek aynı yerde biter |
| `save_reference_order.py` — modül | Süzgeç boşluğu kapatmıyor; ölü ad aynı adla gelen dosyayı ortaya çekerdi |
| `reference_order_store.py` — modül | Dosyası gitmiş ad burada kalabilir *(Drive'dan elle)*, yuva tutmaz |
| `queue_references.py` — modül | İki şey durduruyor: H3 yok, havuz boş |
| `reference_routes.py` | *Four refusals* |
| `api.js` — `saveReferenceOrder` | *"… a slot the pool stops holding open"* gidiyor |
| `ReferencePanel.jsx` | `HOLE`, `slotted`, delik ve `handleDrop` yorumları; `ADD`'in yorumu kendi başına |

## Dist

Kolda derlenmez — [yol haritası](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md), *320–324 iki
paralel kolda*: birleşme commit'i bir kez derler. **Beklenen çakışma** `queue_references.py`: Kol B
boş havuz cümlesini değiştirdi, bu tur hemen altındaki boşluk reddini siliyor.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
