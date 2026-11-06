# Madde 530 · Liste sorgusu — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-6),
530 · v1-6 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

Listeleyen her endpoint aynı PostgREST sorgusunu alır: süzmek, desenle aramak (`like`, `ilike`), tarih aralığı, sıralama, sayfa,
alan seçimi; toplu değişiklik aynı süzgeçle seçer; tek şeyin `GET`'i `select` alır
([6. adım, Liste sorgusu, Toplu seçim, Konum](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md#liste-sorgusu)).
Kullanıcı, 5 Kasım — "süzülsün, PostgREST dediğin olsun".

Bugün gerçek bir liste yok. Bu madde ortak, saf bir parçadır: her liste yalnız alanlarını bildirir —
öğesinin modeliyle —, ayrıştırıcı ve değerlendirici geneldir. Sonraki endpoint maddeleri yalnız
bildirir. Kurallar, roadmap'in Bağımlılık notundaki gibi, yalnız testte açılan bir listede
(`tests/sample.py`'nin `/notes`'u) sınanır.

**Konum** (`"at": "start" | "end" | {"after": <kimlik>}`) bir alanın biçimidir, sorgunun değil: onu
alan ilk gövdeyle (v1-12'nin kare taşıması) yazılır; bu maddede kod yoktur.

## Yerleri

```
core/lists/
  fields.py    listenin alanları (ListField), öğe modelinden okunur: türleri (Kind), izinli değerleri
  pattern.py   `like`/`ilike`'ın deseni (Pattern): okunuşu, sınırı, eşleşmesi; `fold`
  parse.py     sorgu metni → Query; sorunları alan alan sayar
  run.py       Query'yi bellekteki kayıtlara uygular: süzgeç, sıra, sayfa ve onun bayt bütçesi, seçim
  listing.py   Listing: bir listenin bildirimi ve FastAPI'ye bağlanışı (query, selection, one)
tests/lists/   aynı beş dosyanın testleri
```

Beş dosya birlikte bir iş görür ve hiçbir gruba ait değildir: köke beş dosya koymak yerine kendi
klasöründedir (CODE-STANDARD, Düzen'e bir satır eklendi; ana agent'ın kararı, 6 Kasım). `fields`,
`parse` ve `run` FastAPI'yi bilmez; yalnız `listing` bilir.

## Bir listeyi bildirmek

```python
FRAMES = Listing(Frame, default=("id", "position", "scene", "photo.status", "video.status"),
                 order="position")

@frames.get("/projects/{p}/frames", summary=…, response_model=FRAMES.page,
            openapi_extra=FRAMES.extra)
def every(p: …, query: Annotated[Query, Depends(FRAMES.query)]) -> Response:
    return FRAMES.answer(project.frames(), query)
```

- **Alanlar öğenin modelinden okunur:** cevabın alanları sorgunun alanlarıdır, türetilenler dahil
  (6. adım). Ayrıca yazılmadıkları için birbirinden kayamazlar. `str` metin, `Literal["a", "b"]`
  izinli değerli metin, `int` tamsayı, `float` sayı, `bool`, `datetime` zaman; iç içe model hem
  kendisi (bütün olarak) hem noktalı alanlarıyla (`photo`, `photo.status`); `list` ve `dict` yalnız
  bütün olarak. `X | None` X'tir, boş olabilir. Bilinmeyen tür, modelin ve alanın adıyla
  `ValueError`: liste bildirilirken, ilk testte düşer.
- **Kayıtlar JSON biçimindedir** (`model_dump(mode="json")`'ın verdiği): sorgu onlara bakar, seçilen
  alanlar oldukları gibi döner. Kaydın taşımadığı alan boştur (`null`).
- **Ayrılmış adlar** (`select`, `order`, `limit`, `offset`, `all`) bir listenin üst alanı olamaz:
  bildirim `ValueError` verir. Varsayılan seçim ve sıra da bildirilirken ayrıştırılır; yanlışı
  `ValueError`.
- **Cevap** `{"items", "total", "offset", "limit"}` (6. adım, Gövde), core'un kendi yazdığı JSON baytları olarak döner (bütçesiyle, Sınırlar'da);
  belgede `Page[<öğe>]`'dir. Öğeler belgede bütün modelin türüyle görünür, açıklaması yalnız
  `select`'in andığı alanları taşıdıklarını söyler. FastAPI dönen değeri modele karşı doğrulasaydı
  kısmi öğeler düşerdi; kayıtlar zaten core'un kendi verisidir.
- **`extra`** işleme `x-list`'i koyar: `{"order": "position", "select": "id,position,…"}`. Bir
  adresin ayrıntısı onu `list` olarak verir (`discovery`'nin `x-errors` gibi aktardığı); agent
  varsayılan sırayı ve alanları oradan öğrenir. Boy testi de listeleri onunla bulur.

## Sorgu

| Ne | Biçim |
|---|---|
| Süzmek | `<alan>=<işleç>.<değer>`; `not.` önüne gelir |
| İşleçler | `eq`, `neq`, `in.(a,b)`; `gt`, `gte`, `lt`, `lte` (sayı ve zaman); `like`, `ilike` (metin); `is.null` (her alan), `is.true`, `is.false` (`bool`) |
| Tarih aralığı | aynı alan iki kez: `updated=gte.2026-11-01&updated=lt.2026-11-08` |
| Sıra | `order=<alan>[.asc\|.desc],…` |
| Sayfa | `limit` 0–1000, varsayılan 100; `0` yalnız `total`'ı verir. `offset` ≥ 0 |
| Alanlar | `select=<alan>,<alan.alt>,…`; `select=*` hepsi |

- **Birden çok süzgeç "ve"dir;** aynı alan yinelenebilir (tarih aralığı), her biri ayrı koşuldur.
  Ayrılmış bir parametre (`select`, `order`, `limit`, `offset`, `all`) iki kez verilirse
  `duplicate`'tir: hangisinin geçerli olduğunu tahmin etmeyiz.
- **Değerler alanın türüyle okunur:** tamsayı `-?[0-9]{1,18}`, sayı ondalıklı da, `bool` `true` ya
  da `false`, zaman `2026-11-04T09:12:00Z` ya da yalnız gün (`2026-11-04` = 00:00 UTC; 6. adım,
  Zaman). İzinli değerli metin (`status`) yalnız o değerleri alır; `status=eq.waitng` boş liste
  değil `not_allowed`'dur. `in.()` içindeki değerler virgülle ayrılır; tırnak yoktur, virgüllü bir
  metin `eq`'yla aranır.
- **Boş değer (`null`) SQL'deki gibi yalnız `is.null`'a uyar:** `eq`, `gt`, `like` ve onların
  `not.`'lusu boş değeri dışarıda bırakır (PostgREST de öyle). `not.is.null` boş olmayanlardır.
  Kaydın boş bir iç içe nesnesinin alanları da boştur (`photo` `null` ise `photo.status` da).
- **Zamanlar** kayıttaki metinden `datetime.fromisoformat`'la okunup karşılaştırılır: kayıt
  saniyesinden küçük parça taşısa da sıra doğru kalır.
- **Sıra:** her listenin varsayılan sırası vardır; istenen sıra önce, eşitlerde varsayılan sıra.
  Boşlar iki yönde de sona gider (PostgREST `desc`'te başa koyar; agent `finished.desc` deyince
  bitmişleri önce görmek ister). Nesne ve liste alanı sıralanmaz. `asc` yazılmayabilir.
- **Seçim:** `photo.prompt` `{"photo": {"prompt": …}}` döner, `photo` boşsa `{"photo": null}`.
  `photo` da seçilmişse bütünü döner. Alanlar istendiği sırayla. Varsayılan seçim listenin kısa
  alan setidir; `select=*` bütün kayıt.

### Desen: `like` ve `ilike`, regex değil

- **Regex yok** (kullanıcıyla verilen karar, 6 Kasım; 6. adımdan sapma, kararlar 11). İlk yapılışta
  `match`/`imatch` `regex` paketiyle ve sorgu başına bir süre bütçesiyle yazılmıştı. Review'da
  yalnız *derlenen* bir desen (`(?:(?:(?:a{1,1000}){1,1000}){1,1000})`, on kez `[\w\W]{1,65535}`)
  bu makinenin belleğini bitirip onu düşürdü: süre bütçesi eşleşmeyi sınırlar, derlemeyi değil; aynısı
  Colab'da core'u düşürürdü. Paket kaldırıldı.
- **`like.<desen>`, `ilike.<desen>`** PostgREST'in işleçleri, onun yazışıyla: desen bütün metindir,
  `*` herhangi bir karakter dizisi (boş da); `*rain*` içinde geçeni, `rain*` öyle başlayanı, `rain`
  yalnız tam eşitini bulur. `*`'ın kaçışı yoktur: `*`'ın kendisi aranamaz (PostgREST'te de `*` `%`'ye
  çevrilir). `like` büyük/küçük harfe bakar, `ilike` bakmaz. Yalnız metin alanlarında, `not.`'la da.
- **Eşleştirici motorsuzdur** (`core/lists/pattern.py`, `Pattern.read` ve `matches`): desen
  `*`'lardan parçalanır; ilk parça metnin başı, son parça sonu, aradakiler sırayla `str.find`'la, her
  biri bir öncekinin ardında aranır. En soldaki yer her zaman yeter, geri dönüş yoktur: kayıt başına
  O(L·m), L metnin boyu, m bir parçanın boyu: yazıldığı gibi ≤ 200, `ilike`'ın `casefold`'u onu
  uzatabildiği için (`ß` → `ss`, `ﬃ` → `ffi`; bir karakter en çok üçe çıkar) katlanmış parçada
  ≤ 600. L'de doğrusal kalır.
- **Desen en çok 200 karakter** (`MOST_CHARACTERS`; 6. adım), yazıldığı gibi sayılır; fazlası
  `out_of_range`, eşleşmeden önce: doğrusal iş de sınırlı kalır. Katlanmış `ilike` deseni en çok
  üç katıdır (yukarıda).
- **`ilike`'ta dört i:** desende de metinde de önce `I`, `ı`, `İ` `i`'ye çevrilir, sonra Unicode'un
  `casefold`'u (`Ğ` `ğ`, `ß` `ss`); böylece `yağmur` `YAĞMUR`'u, `ışık` `IŞIK`'ı ve `Işık`'ı,
  `istanbul` `İSTANBUL`'u bulur. Önce çevirmek gerekir: `casefold` `İ`'yi `i` ve bir birleşen
  nokta yapar.

### Sınırlar

Bir sorgunun core'a yaptırabileceği her şey, iş yapılmadan önce sınırlıdır (CODE-STANDARD, Maliyet);
her sınırın bir testi var, sınır gerekirse küçültülerek:

| Ne | Sınır | Neden | Aşılınca |
|---|---|---|---|
| Sorgunun boyu | 16 KiB (`core.query.QUERY_BYTES`) | Core'un kendi sınırı, sunucudan bağımsız: parametre sayısını ve her adın, değerin boyunu bu tutar. Bir listenin en büyüğü 1000 yedi basamaklı kimlikli bir `in`, virgülleri `%2C` gönderilince ~10 KB, yanında birkaç süzgeç | `invalid_request` (`query` `out_of_range`), yönlendirmeden önce (`QueryLimit`, `BodyLimit`'in yanında) |
| İsteğin başı | 16 KB (`main.HEAD_BYTES`), yalnız dış koruma | Uvicorn `http="h11"` ile açılır (httptools kurulunca onu seçerdi). h11 yalnız henüz bitmemiş bir başı keser: tek okumada gelen baş her boyda ayrıştırılır (QA, 530: 16–20 KB'lık başlar uygulamaya vardı, ~70 KB reddedildi). Liste sınırları buna değil `QUERY_BYTES`'a dayanır | 400, uygulamaya varmadan |
| Bir alanın süzgeci | 2 (`FILTERS_PER_FIELD`) | Bir aralık iki süzgeçtir; üçüncüsü aralığın söylemediği bir şey söylemez | `out_of_range`, alanda bir kez; fazlası okunmaz |
| `in`'in değeri | 1000 (`MOST_IN` = `MOST_LIMIT`) | Bir sayfanın tuttuğu kadar | `out_of_range`, değerler okunmadan |
| `order`'ın alanı | her alan bir kez | Anahtar sayısı listenin alan sayısını geçmez | `duplicate` |
| `select`'in alanı | her alan bir kez | Aynısı | `duplicate` |
| Desen | 200 karakter (`MOST_CHARACTERS`) | 6. adım; eşleşme O(L·m) kalır | `out_of_range` |
| `limit` | 0–1000 (`MOST_LIMIT`) | 6. adım | `out_of_range` |
| Sayı ve tamsayı | 18 basamak | Makinenin sayısı | `wrong_type` |
| Cevabın boyu | 1 MiB (`listing.PAGE_BYTES`) | Aşağıda | `invalid_request`, sığan öğe sayısıyla |

**Cevabın bayt bütçesi.** Sayfa öğe öğe yazılır ve yazılırken sayılır; bütçeyi geçecek öğede
`invalid_request` döner: alan `query.limit` `out_of_range`, `details.fits` sığan öğe sayısı, hint
`limit`'i o sayıya indirmeyi ya da `select`'le daha az alan istemeyi söyler. Sayfa hiçbir zaman
kesilip gönderilmez. 1 MiB bir dış sınırdır — core'un belleği ve tünel için —, agent'ın bağlamının
sınırı değil: onu varsayılanlar tutar (100 öğe × `LIST_ITEM_BYTES` ≈ 25 KB). Örnek listenin en kötü
bütün öğesi 793 B, 1000'i ~0,8 MB: sığar (testle). 1000 bütün kare, uzun prompt'larıyla, sığmaz; o
istek daha azını istemesi söylenerek reddedilir. Tek şeyin `GET`'i de aynı bütçeyle (`select` hint'i).

## Toplu seçim

- `DELETE /projects/{p}/frames` ve `…/jobs` `Depends(LISTING.selection)` alır: aynı listenin
  süzgeçleri, `order`, `limit`, `offset`, `select` alınmaz (`unknown`: toplu değişiklik bütün
  eşleşenlere yapılır). `all=true` hepsini seçer; `all`'un başka değeri `not_allowed`.
- **Süzgeçsiz ve `all=true`'suz istek reddedilir:** `query` `missing`, "A bulk change names what it
  acts on: filters, or `all=true` for every one". `all=true` süzgeçle birlikte de geçerlidir;
  süzgeç uygulanır.
- `selection`, değiştiren isteğin `change` bağımlılığını kendi alt bağımlılığı olarak alır ve
  `Selection(filters, change)` verir. Başlıklar eksikse FastAPI `selection`'ı hiç çağırmaz, cevap
  başlıkları sayar; sorgunun sorunları başlıklar düzelince gelir — m529'un "önce ve yalnız" kuralı
  gibi. Böylece her `DELETE`'i başlıksız deneyen test bu route'ları da kapsar.
- `LISTING.matches(records, selection)` eşleşenleri verir; ya hep ya hiç ve engellerin sayılması
  onları kullanan maddenindir (v1-12, v1-15). Seçim boşsa endpoint bir şey yapmadan `200` döner.

## Tek şeyin `GET`'i

`Depends(LISTING.one)` yalnız `select` alır (varsayılan bütün kayıt); başka parametre `unknown`.
`LISTING.answer_one(record, picked)` seçilen alanları döner. Projenin `GET /projects/{id}`'si
satırdan fazlasını (`counts`, `lost_changes`) döndüğü için o madde kendi modeliyle ikinci bir
`Listing` bildirir.

## Hatalar

- Her sorun `invalid_request`'in `details.problems`'ında `{field, code, message}`; alan
  `query.<ad>`, `query.order`, `query.select`, toplu istekte süzgeçsizlikte `query`. Kodlar: bilinmeyen
  alan `unknown`, yanlış türde değer `wrong_type`, izinli olmayan değer `not_allowed`, yanlış ya da
  alana uymayan işleç `bad_query`, 200'ü aşan desen ve sayfa sınırları `out_of_range`, yinelenen ayrılmış
  parametre `duplicate`.
- `details.fields` listenin alanlarını sayar (6. adım: "`details` o listenin alanlarını sayar").
  Türleri ayrıntıdadır; hint m529'unki: `` `GET /api?path=<adres>` gives what this address takes.``
  Sözdizimi dizinin `rules`'unda.
- Gelen değer mesaja yazılmaz (m529); çağıranın adı `cut`'la `FIELD_BYTES`'ta kesilir, cümle
  `PROBLEM_BYTES`'ta, ilk altı sorun listelenir, kalanı `more`. Bunun için m529'un iki yardımcısı
  açıldı: `errors.cut` (`_cut`) ve `errors.invalid(address, problems, details)` (`_invalid`'in
  `ApiError` kuran yarısı); `errors.template` (`_template`) route'un adresini verir.
- **Yinelenen parametre, liste dışında da** (m529, Sonraki maddeler için): `known_query` bir
  route'un tek değerli parametresi iki kez gelirse `duplicate` der; FastAPI sonuncuyu sessizce
  alıyordu (`?path=/a&path=/b`). Liste türündeki bir sorgu parametresi yinelenebilir.

## Dizin

`RULES` sorgunun bir cümlesini alır: listenin cevabı, işleçler, `not.`, boşun yalnız `is.null`'a
uyması, sıra, sayfa, seçim, zaman ve toplu seçim. Ayrıntı `list`'i (`x-list`) verir.

## Boy sınırları

`tests/budgets.py`'ye `LIST_ITEM_BYTES` 256 B: listenin varsayılan alanlarıyla bir öğe. Neden: 6.
adımın en büyük varsayılan seti karelerinki — iki kimlik, bir sahne, iki durum: ~230 B. Test
belgedeki `x-list`'li her işlemi yürür, öğenin şemasından en kötü bir öğe kurar (tamsayı 7 basamak,
izinli değerlerin en uzunu, zaman 20 karakter, `maxLength`'li metin o kadar, sınırsız metin
`TEXT_SAMPLE_BYTES` 120 B — bir iki cümlelik sahne), varsayılan alanları seçer ve ölçer. Sayfa
cevabı (`items`, `total`) dönüp `x-list` taşımayan işlem de aynı yürüyüşte düşer: boy testinden
kaçamaz. Hata sınırı (`ERROR_BYTES` 2048) değişmez: en kötü sorgu hatası (çağıranın en uzun yedi
adı, bozuk `order` ve `select`) belgedeki her listede ölçülür; örnek listenin 18 alanıyla 1390 B,
karelerin ~32 alanıyla ~1,7 KB beklenir. Bugünkü boylar: core'un dizini, `rules`'un sorgu
cümlesiyle, 639 B'tan 1277 B'a çıktı (sınır 6144); `/notes`'un 18 alanlı ayrıntısı 1918 B (sınır
4096).

## Maliyet

| İşlem | Drive | Disk | Ağ | İşlemci |
|---|---|---|---|---|
| Sorgunun ayrıştırılması | 0 | 0 | 0 | O(parametre); desen bir kez parçalanır, en çok 200 karakter |
| Liste (`answer`) | 0 | 0 | 0 | süzgeç O(N·F), bir `like` O(N·T·m), m ≤ 200 (`ilike`'ta katlanınca ≤ 600), T'de doğrusal; sıra O(M log M) (önceden sıralı kayıtta ~O(M)); seçim ve yazım O(L), en çok `PAGE_BYTES` |
| `limit=0` | 0 | 0 | 0 | yalnız süzgeç: sıralamaz, seçmez |
| Toplu seçim (`matches`) | 0 | 0 | 0 | O(N·F) |
| Tek şey (`answer_one`) | 0 | 0 | 0 | O(seçilen alan) |

N kayıt, F süzgeç, M eşleşen, L sayfadaki öğe, T metnin boyu. Sorgu kayıtlara bakmadan önce
ayrıştırılır: yanlış sorgu hiçbir kaydı yüklemez. `ilike` her kaydın metnini bir kez katlar
(`translate`, `casefold`). Bellek: eşleşenlerin listesi (kayıtlara gösterge), O(M), ve en çok
`PAGE_BYTES`'lık cevap; desen 200 karakterle, süzgeç ve değer sayıları Sınırlar'daki gibi sınırlı. Parça hiçbir şeyi önbelleklemez; aynı istekte aynı şeyi iki kez okumaz.

## Ne bozulabilir

- **Bir desen core'u dondurur ya da belleğini bitirir:** regex yok; desen 200 karakter, eşleşme
  geri dönüşsüz, kayıt başına doğrusal. Geç düşen bir desen testle (100.000 karakterde).
- **Çok uzun bir sorgu** sayıları büyütür: core `QUERY_BYTES`'ta yönlendirmeden önce keser; h11'in
  baş sınırı buna yetmez (yukarıda).
- **h11'in reddettiği büyük baş log'a iz bırakır:** Uvicorn/h11 `core.log`'a bir ERROR yazar
  (`LocalProtocolError`, durum `MUST_CLOSE`); sunucu ayakta kalır, istek 400 alır. Kodda
  kovalanmadı.
- **Model ile sorgu ayrışır:** alanlar modelden okunur, ayrıca yazılmaz.
- **Yanlış yazılmış süzgeç bütün listeyi döner** (`statsu=eq.x`): bilinmeyen alan reddedilir;
  izinli olmayan değer de.
- **Süzgeçsiz toplu silme:** `all=true`'suz reddedilir.
- **Toplu istek sayfayla sınırlanır sanılır:** `limit` alınmaz, reddedilir.
- **Varsayılan alan seti büyür:** belgedeki her liste boy sınırıyla ölçülür.
- **Hata büyür:** alan sayısı ve sorunlar sınırlı; en kötü sorgu hatası ölçülür.
- İki istek aynı anda: parça paylaşılan bir şey yazmaz; `Listing` bildirildikten sonra değişmez.
  Kayıtlar okunurken değişmemelidir: 4. adımın "bellekteki hal tek hamlede değişir" kuralı onları
  veren maddenindir.

## Testler

Önce düşen testle; hiçbiri ağ açmaz, hiçbiri gerçek zaman beklemez.

- `tests/lists/test_fields.py`: her türün okunuşu, iç içe model, `X | None`, `Literal`, liste ve
  sözlük; bilinmeyen tür ve ayrılmış ad `ValueError`.
- `tests/lists/test_parse.py`: her işleç ve `not.`; her türün değeri; gün ve zaman; izinli değer;
  `in`; yinelenen alan ve ayrılmış parametre; sıra, sayfa, seçim ve yanlışları; `like`/`ilike`'ın
  `Pattern`'i ve desenin sınırı; `match` artık işleç değil; Sınırlar: alanın iki süzgeci ve
  üçüncüsü, `in`'in 1000 değeri ve 1001'incisi, `order`'da ve `select`'te iki kez anılan alan;
  toplu seçimin kuralları; tek şeyin `select`'i.
- `tests/lists/test_pattern.py`: `like`'ın eşleştiricisi (baş, son, aradakiler, `*`'sız desen,
  boşlar, örtüşmeyen parçalar, büyük/küçük harf); `fold`'un dört i'si ve `casefold`'u; desenin
  sınırında ve ötesinde; uçları tutan ama ortadaki parçası düşen desen, 100.000 karakterde.
- `tests/lists/test_run.py`: süzgeçler "ve"; boşun SQL'deki gibi davranması; `like`/`ilike`
  kayıtlarda; zamanın karşılaştırılması; sıra, boşlar sonda, eşitlerde varsayılan; sayfa, bütçesine
  tam sığan ve bir bayt fazlası; seçim.
- `tests/lists/test_listing.py`: örnek `/notes` listesi API'den — cevap, varsayılanlar, hata
  biçimi ve `details.fields`, sorgunun kayıttan önce reddi, toplu seçim (başlıklar önce,
  süzgeçsizlik, `all=true`), tek şeyin `select`'i; ayrıntıda `list` ve zamanın `date-time`'ı; en
  kötü sorgu hatası sınırda; her listenin varsayılan öğesi `LIST_ITEM_BYTES`'ta, `x-list`'siz sayfa
  düşer; `PAGE_BYTES` 300'e indirilince sayfa, 100'e indirilince tek şey reddedilir; örneğin en
  kötü 1000 bütün öğesi sığar.
- `tests/test_query.py`: yinelenen tek değerli parametre `duplicate`, dizinin `?path=`'i de; liste
  türü yinelenebilir, `list[str] | None` da; `QUERY_BYTES` 32'ye indirilince fazlası endpoint
  koşmadan reddedilir, tam sınırdaki okunur.
- `tests/test_main.py`: sunucu h11'le, 16 KB'lık korumayla açılır; koruma 64 bayta indirilince
  bitmemiş bir baş uygulamaya varmadan 400 alır. Yalnız bunu gösterir: tek okumada gelen başı
  `QUERY_BYTES` tutar.
- Bilinmeyen işleç (`id=match.1`) alanın aldığı işleçleri sayar.
- Var olan testler (`test_change`'in yürüyüşü, ayrıntıların ve hataların boyu, her başarı 200)
  `/notes`'u da kapsar. ruff ve pyright temiz; `openapi.json` değişmez (örnek liste yalnız testte).

## Bitti sayılır

Kabul koşulunun dört satırı: her liste aynı sorguyu alıyor, kabulün "regex"i `like`/`ilike`'la
(kullanıcının kararı, 6 Kasım), `ilike` dört i'yi birlikte buluyor;
yanlış sorgu listenin alanlarını sayan hatayla dönüyor, sorgu bellekte; toplu seçim aynı süzgeçle,
süzgeçsizi `all=true`'suz reddediliyor; varsayılan alan seti kayıtlı sınırla ölçülüyor. Ayrıca
dizinin kuralı sorguyu söylüyor, ayrıntı listenin varsayılanlarını veriyor, iki suite yeşil.

## Sonraki maddeler için

- **Her liste maddesi:** `Listing(<öğe>, default=…, order=…)` grubun kurallarının yanında; route
  `response_model=L.page`, `openapi_extra=L.extra` (kendi `x-errors`'uyla birleşerek), sorgu
  `Depends(L.query)`, cevap `L.answer(kayıtlar, query)`. Kayıtlar JSON biçiminde, zamanlar
  `2026-11-04T09:12:00Z`: modelin `datetime`'ları saat dilimli (UTC) olmalı; dilimsiz bir zaman
  dilimli bir süzgeçle karşılaştırılınca `TypeError` verir, cevap `500` olur. Varsayılan sıra eşitlik bırakmasın (`created.desc` aynı saniyede
  eşitlenir: `created.desc,id.desc`). Bir metin alanına `max_length` vermek boy testinin ölçüsünü
  gerçeğe yaklaştırır.
- **v1-12, v1-15 (toplu silme):** `Depends(L.selection)`, `L.matches(kayıtlar, selection)`;
  engelleri sayan hata m529'un notundaki gibi ilk altıyla kesilir.
- **v1-10 (history):** eski blokları yalnız gereken süzgeç indirir (6. adım, History); `Query`'nin
  `seq` ve `time` süzgeçleri okunarak hangi blokların gerektiği bulunur, sonra `answer`.
- **v1-29 (UI):** öğeler belgede bütün modelin türüyle; `select`'le kısmi öğe alan ekran alanların
  eksik olabileceğini bilir, ya da `select=*` ister.
- **Ayrıntının boyu:** 30 alanlı bir öğe her alanın açıklamasıyla `DETAIL_BYTES`'a (4096) yaklaşır;
  kareler maddesi açıklamaları kısa tutar ya da sınırı nedeniyle büyütür.
