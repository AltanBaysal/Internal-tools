# Madde 529 · Ortak sözleşme: hatalar, başlıklar, `GET /api` — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-5),
529 · v1-5 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

Bütün endpoint'lerin paylaştığı sözleşme, endpoint'lerin kendisinden önce: her hata aynı dört alanla
döner, değiştiren her istek iki başlık taşır, gövde bilinmeyen alanı ve 4 MB'ı geçmeyi reddeder,
agent API'yi `GET /api`'nin kısa dizininden ve bir adresin ayrıntısından öğrenir
([6. adım, Ortak kurallar, Hatalar, Discovery](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md);
[1. adım, Discovery](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md#discovery);
[11. adım, Mesajlar](../research/2026-11-03-yeni-editor-v1-11-kod-standardi.md#mesajlar)). Kullanıcı,
5 Kasım — "token olarak efficient olsun, model tool listesi ve ne yaptığını bilsin, gerekince
detaylı olarak o endpoint'e baksın".

Bugün core'da tek gerçek endpoint health olduğu için kurallar, roadmap'in Bağımlılık notundaki gibi,
yalnız testte açılan adreslerde (`tests/sample.py`) sınanır; sonraki her endpoint aynı testlerin
içine kendiliğinden girer, çünkü örnek API core'un bütün gruplarını da taşır.

## Yerleri

```
core/
  errors.py          dört alanlı hata: Error modeli, kod tablosu, ApiError, FastAPI'nin hatalarının çevrilmesi
  body.py            istek gövdesi: RequestBody (bilinmeyen alan hatadır), BodyLimit (4 MB)
  change.py          değiştiren isteğin iki başlığı: Change ve change bağımlılığı
  query.py           sorgu: known_query (bilinmeyen parametre hatadır), own_query (kendi sorgusunu ayrıştıran route)
  server.py          create_api bunları bağlar (redirect_slashes kapalı, openapi_tags, RESPONSES, known_query)
  api/discovery.py   dizini ve ayrıntıyı OpenAPI belgesinden kuran saf fonksiyonlar, RULES
  api/endpoints.py   GET /api (dizin ve ?path=), health; grubun SECTION'ı
tests/
  contract.py        her hata cevabına bakan test istemcisi
  budgets.py         bağlamın kayıtlı sınırları
  sample.py          yalnız testte açılan örnek grup
```

Üç yeni dosya `core/`'un kökünde: her grubun paylaştığı şeyler oradadır (CODE-STANDARD, Düzen).
Dizin `api` grubunun kuralıdır: OpenAPI belgesini alır, cevabı verir, dışarıyı bilmez.

## Kararlar

### Hata

- **`Error` modeli** `code`, `message`, `details`, `hint`; dördü de zorunlu, `hint` `string | null`,
  `details` nesne. OpenAPI'de `components.schemas.Error` olarak durur ve `create_api`'nin
  `responses={"default": Error}`'u onu her işlemin hata cevabı yapar: UI'ın türlerinde
  `responses.default` `Error`'dur, v1-28'in hata görünümleri ona karşı derlenir. `default`'u yazmak
  FastAPI'nin kendi 422'sini ve `HTTPValidationError`'ını da belgeden çıkarır; API 422 dönmez.
- **Kod tablosu** (`CODES`): kod → HTTP durumu ve hint'in hep verilip verilmediği (6. adımın Hint
  sütunu: kural da seçenek de "verilir", yok "null"). Bugün yalnız core'un ürettikleri:
  `invalid_request` 400, `unknown_endpoint` 404, `method_not_allowed` 405, `internal` 500. Bir kodu
  ilk üreten madde satırını ekler. `ApiError` tabloda olmayan kodla kurulamaz (`KeyError`), durumu
  koddan alır: kod ile durum ayrı ayrı yazılmaz.
- **Alan sorunları** `details.problems`'ta `{field, code, message}`; `field` `body.`, `query.`,
  `header.`, `path.` ile başlar (adresteki alan, ör. `{id}`, `path.`'tir; 6. adım ilk üçünü
  sayıyordu, bu maddede dördüncüsü eklendi). Adı olmayan parametre (`?=1`) `query.(empty)`'dir.
  Alan kodları 6. adımın on kodu, `FieldCode` türünde; pyright yanlış adı yakalar.
- **Hatanın boyu, istek ne olursa olsun:** çağıranın verdiği her ad ve metin, gönderildiği bayt
  sayısıyla (JSON'da kontrol karakteri altı, `"` iki, `ğ` iki bayt) kesilir, sonu `…`: alan adı
  `FIELD_BYTES` 48, sorunun cümlesi `PROBLEM_BYTES` 128, adres `ADDRESS_BYTES` 200, `internal`'ın
  sözü `MESSAGE_BYTES` 300. İlk `PROBLEMS_SHOWN` (6) sorun listelenir, kalanların sayısı
  `details.more`'dadır; üst `message` hepsinin sayısını söyler. Böylece en büyük hata ~1,8 KB'ı
  geçemez (6 × ~220 B, cümle, iki hint); testlerin gönderdiği en kötüsü 1244 B (yedi tane 2000
  kontrol karakterli ad). 5000 karakterlik ad, 300 bilinmeyen parametre, 3000 karakterlik gövde
  anahtarı testle; boyu `contract.checked_client` ölçer.
- **FastAPI'nin doğrulama hatası** 400 `invalid_request` olur. Pydantic'in hata türleri bizim
  cümlemizle söylenir (`` `body.name` is missing.``, `` `body.count` must be at most 9.``); tabloda
  olmayan tür pydantic'in kendi sözünü alanın arkasında taşır. Tek sorunda üst `message` o sorunun
  cümlesidir, birden çoğunda kaç sorun olduğunu ve hiçbir şeyin yapılmadığını söyler. Hint kesindir:
  `` `GET /api?path=<adres>` gives what this address takes.`` — alanların ne olduğu ve neden istendiği
  açıklamalarıyla oradadır; mesaja yazılmaz, hata kısa kalsın diye. Başlığın sorunu ise ayrıntıda
  yoktur (agent başlık yazmaz), hint'i iki başlığı ve aldıklarını söyler (`change.HEADERS_HINT`);
  başlık ve öbür alan sorunları birlikteyse hint ikisini de söyler. Gelen değer mesaja yazılmaz:
  büyük olabilir, sır taşıyabilir. Adres route'un `path_format`'ıdır: `{name:path}` gibi bir
  dönüştürücü OpenAPI belgesindeki gibi `{name}` yazılır.
- **Dizinin kendi hataları:** dizin API'nin köküdür (`errors.INDEX = "/"`) ve çağrısı `GET /api`'dir;
  `?path=/` yoktur. Onun `invalid_request`'inin hint'i `` `GET /api` takes only `path`, an address
  `GET /api` lists.``, 405'i `` `/api` does not take POST.``, hint `` `GET /api` is the only call at
  this address.`` Bir test her hint'in andığı her `GET` çağrısını, `/api`'ye bağlı core'da yapar ve
  200 ister.
- **Bilinmeyen adres** (`unknown_endpoint`): `` `/x` is not an address of this API.``, hint
  `` `GET /api` lists every address.`` Adres `/api` öneksiz yazılır, dizindeki gibi; 200 bayttan
  uzunu kesilir (yukarıda).
- **Sondaki eğik çizgi:** FastAPI'nin `redirect_slashes`'ı kapalı. Onun 307'si mutlak `http://`
  adresi gösterir, tünelin `https`'i arkasında yanlıştır (m527, Sonraki maddeler için). `/health/`
  artık yönlendirilmez, `unknown_endpoint`'tir; tek adres, tek yazılış (v1-10'un isteğin özetine
  giren adresi de tektir).
- **Adres var, fiil yok** (`method_not_allowed`): bir adresin fiilleri ayrı route'larsa
  (`GET` ve `DELETE …/frames`) Starlette ilk route'ta durur ve `Allow`'u yalnız onun fiilleriyle
  verir. Fiillerin hepsi OpenAPI belgesinden okunur (FastAPI onu bir kez kurar, bellekte tutar).
  Belgede olmayan adresin — dizin, FastAPI'nin kendi `/openapi.json`'ı — tek route'u vardır, onun
  `Allow`'u bütündür (`HEAD` dışında); ayrıntısı olmadığı için hint çağrının kendisini adıyla söyler
  (`` `GET /api/openapi.json` is the only call at this address.``; dizinde `/api`). `/openapi.json`
  bir `APIRoute` değildir: `scope["route"]` ya hiç yoktur ya `/api` Mount'udur, adres bu yüzden
  isteğin kendisinden okunur. `details.methods`, hint ve `Allow` başlığı aynı listeyi verir: agent
  başlıkları görmez (6. adım).
- **Core'un kendi hatası** (`internal`): `message` istisnanın türü ve sözü (`RuntimeError: …`),
  en çok 300 bayt (`MESSAGE_BYTES`, sonu `…`); `hint` null. Doğrulama hatalarının
  (`ResponseValidationError`, pydantic'in `ValidationError`'ı) metni dönen değeri ve kaynak satırını
  taşır: cevapta yalnız türü ve sayısı (`ResponseValidationError: 1 validation error`). Starlette
  istisnayı cevaptan sonra yeniden fırlatır, Uvicorn izini bütünüyle `core.log`'a yazar ("Exception in
  ASGI application"); elle denendi (bu makinede, örnek API'yle).
- **Başka bir `HTTPException`** (core'un kendisi hep `ApiError` fırlatır): FastAPI'nin ve
  Starlette'in `4xx`'i — ör. okunamayan gövdenin 400'ü — `invalid_request`'tir, `body` `wrong_type`
  sorunuyla ve onların sözüyle; `5xx`'i `internal`, durumu ve sözüyle.
- **Handler'lar ve bağımlılıklar `async`** (`known_query`, `own_query`, `change`, dizin): depoya
  dokunmazlar, istek başına işçi iş parçacığına geçmezler. FOUNDATION 2'nin `def` kuralının nedeni
  (yavaş Drive çağrısı bir işçiyi tutsun) onlarda yok.
- **`ApiError` ve `respond`** `Error`'u tek yerde kurar: `respond` bir `ApiError` kurup onun
  `response()`'unu verir.

### Hint kuralına her hata cevabında bakmak

`tests/contract.py`'nin `checked_client`'ı bir test istemcisi verir ve her `4xx`/`5xx` cevabına
kendiliğinden bakar: tam dört alan; `code` tabloda ve HTTP durumu onunki; `message` boş değil;
`details` nesne; hint tablodaki gibi (verilirse boş olmayan metin, yoksa `null`); her alan sorunu
`{field, code, message}`, yeri dört önekten biri, kodu on koddan biri; boyu `ERROR_BYTES`'ı aşmıyor.
API'ye istek atan her test bu istemciyle atar: `tests/test_contract.py` `tests/`'te `contract.py`
dışında `TestClient(` geçen dosyayı bulursa düşer. Kontrolün ısırdığı, FastAPI'nin düz
`{"detail": ...}` cevabının reddedildiğiyle sınanır.

Makineyle bakılamayan yarısı: servis hatasının hint'inin neden tahmin etmemesi ve emir vermemesi.
O cümleleri reviewer okur.

### Başlıklar

- `change` bir FastAPI bağımlılığıdır; değiştiren her endpoint onu alır:
  `made: Annotated[Change, Depends(change)]`. `Idempotency-Key` 1–128 yazdırılabilir ASCII
  (`\x20`–`\x7e`), `Actor` `agent` ya da `ui` (`core` yalnız core'un kendi history kayıtlarındadır).
  Pydantic'in doğrulamasından geçtikleri için eksik ya da yanlış başlık gövdenin sorunlarıyla aynı
  `invalid_request`'te sayılır ve endpoint hiç koşmaz.
- Başlıklar OpenAPI'de işlemin zorunlu parametreleridir: UI'ın türü onları ister. `GET` ikisini de
  almaz; gelirse bakılmaz.
- **Unutulmasın diye:** bir test OpenAPI belgesindeki her `POST`, `PATCH`, `DELETE`'i başlıksız
  dener ve iki başlığın da sorun olarak sayıldığını ister; başlıksız bir route'u bulduğu ayrıca
  sınanır. Örnek API core'un gruplarını da taşıdığından sonraki her endpoint bu testin içindedir.
  (FastAPI 0.162 eklenen router'ları `api.routes`'ta düzleştirmiyor; yürüyüş bu yüzden belgede.)
- **v1-10 nasıl bağlanır:** endpoint `Change`'i alır ve v1-10'un "bir değişiklik" işine verir:
  `key` anahtarın 24 saatlik aranması ve kaydı, `actor` history kaydının `actor`'ü. İsteğin özeti
  (fiil, adres, sıralı sorgu, kanonik gövde) v1-10'undur; gerekirse `Change`'e alan ekler ya da
  `change`'i `Request`'i de alan bir bağımlılığa çevirir, endpoint'ler değişmez. Değiştiren istek
  bugün yok, bu yüzden anahtar hiçbir yerde tutulmuyor.

### Gövde

- **Bilinmeyen alan:** bütün istek gövdeleri `core.body.RequestBody`'den türer (`extra="forbid"`;
  adı FastAPI'nin `Body`'sini gölgelemesin diye); bilinmeyen alan `unknown` sorunudur. Bir test
  OpenAPI belgesindeki her istek gövdesini, iç içe nesneleri dahil, yürür ve hepsinin
  `additionalProperties: false` olduğunu ister: `RequestBody`'den türemeyen model düşer.
- **4 MB** (`MAX_BYTES`, 4 MiB): `BodyLimit` API'nin önünde bir ASGI ara katmanıdır, gövdeyi geldikçe
  sayar ve sınırı geçince endpoint okumadan 400 `invalid_request` döner (`field: body`,
  `out_of_range`). `Content-Length`'e güvenmez: parça parça (chunked) gelen gövde de sayılır. Sınırın
  içindeki gövde bir kez, bütün olarak endpoint'e verilir; sonra çağıranın kendi iletileri (ör.
  ayrılması) geçer. Gövde zaten endpoint'te bütün olarak bellekte tutulur; ara katman en çok
  `MAX_BYTES` ve bir parça okur.
- JSON olmayan gövde `body` `wrong_type`'tır, ayrıştırıcının sözüyle.

### Sorgu

- **Bilinmeyen sorgu parametresi** de hatadır (ana agent'ın kararı, 6 Kasım; 6. adımın Gövde
  kuralının sorguya genişlemesi, Sapmalar'a yazılır). FastAPI tanımadığı parametreyi okumadan bırakır:
  `GET /api?paht=/health` bütün dizini dönerdi. `known_query` `create_api`'nin bütün route'lara
  koyduğu bağımlılıktır (`FastAPI(dependencies=[...])`): route'un ve bağımlılıklarının okuduğu sorgu
  parametrelerini route'un `dependant`'ından toplar (sorgu modeli, `Annotated[Filter, Query()]`,
  alanlarıyla — takma adları dahil — sayılır), gerisini `query.<ad>` `unknown` sorunu olarak
  `invalid_request`'le reddeder; endpoint koşmaz. Kaynak OpenAPI belgesi değil `dependant`'tır, çünkü
  dizinin kendi route'u (`?path=`'i okur) belgede yok.
- **Önce ve yalnız:** uygulamanın bağımlılığı route'un kendi parametrelerinden önce çözülür;
  bilinmeyen parametre varsa cevap yalnız onları sayar, route'un öbür sorunları sonraki denemede
  gelir. Hepsini bir arada saymak FastAPI'nin doğrulamasının içine girmeyi isterdi.
- **Kendi sorgusunu ayrıştıran route** (v1-6'nın listeleri, PostgREST sorgusu: `status=eq.waiting`
  gibi adları önceden bilinmeyen parametreler) `own_query`'yi bağımlılık olarak alır:
  `query: Annotated[QueryParams, Depends(own_query)]`. Ham sorguyu verir; `known_query` onu alan
  route'a bakmaz, bilinmeyen alanı o listenin ayrıştırıcısı reddeder (6. adım, Liste sorgusu:
  `details` listenin alanlarını sayar). Testte örnek `GET /samples` böyle.
- **`/openapi.json` bakılmaz:** uygulamanın bağımlılıkları yalnız FastAPI'nin `APIRoute`'larında
  koşar, `/openapi.json` ise FastAPI'nin kendi Starlette route'udur. Onu kapsamak FastAPI'nin
  route'unu kendi route'umuzla değiştirmek olurdu (m527'nin kodu; sunulan belgenin `servers`'ı da
  değişirdi). Gerek de yok: belge UI'ın türleri içindir, `write_openapi.py` onu sunucu açmadan
  yazar, agent onu çağırmaz ve route hiçbir parametre okumaz; `?x=1` belgeyi değiştirmez.

### Bilerek böyle bırakılanlar

- **Gövdenin boyuna yönlendirmeden önce bakılır:** `BodyLimit` API'nin önündedir; 4 MB'tan büyük
  gövdeli bir istek, adresi olmasa da, `unknown_endpoint` değil `invalid_request` alır.
- **`GET`'in gövdesi okunmaz:** sayılır (sınır onu da tutar), ama hiçbir `GET` endpoint'i gövde
  almaz; gönderilen gövde yok sayılır. Bilinmeyen alan kuralı gövde alan adreslerindir.
- **`HEAD` 405 döner:** FastAPI `GET` route'una `HEAD` eklemiyor; agent ve UI `HEAD` kullanmaz.
- **Ayrıntıda tamsayı sınırları ondalıklı görünür** (`"minimum": 1.0`): FastAPI'nin kendi OpenAPI
  üretimi öyle yazıyor; ayrıntı belgeyi olduğu gibi aktarır.

### `GET /api`

- **Dizin** `{"app", "version", "rules", "sections": [{"name", "about", "endpoints": ["GET
  /health: Which app and which core answer here"]}]}`. `app` ve `version` OpenAPI'nin `info`'sundan
  (yani `about.py`'den); bölümler OpenAPI'nin `tags`'inden: her grup kendi `SECTION`'ını (ad ve iki
  üç cümle) router'ının yanında tutar, `create_api` onu `openapi_tags`'e koyar, router'ı o etiketle
  kurar. Satır `"<fiil> <adres>: <summary>"` metnidir. Endpoint eklemek dizine tam bir satır ekler;
  testle.
- **Satır metin, nesne değil** (ana agent'ın kararı, 6 Kasım; 6. adım düzeltildi, Sapmalar'a
  yazılır): 6. adımın `{"method", "path", "summary"}` nesnesinde üç anahtar her satırda yinelenir;
  health'in satırı 85 B'tan 53 B'a iner, v1'in ~45 endpoint'inde oturum başına ~1,5 KB (~370 token).
  Agent fiili ve adresi satırın başından okur.
- Bölümü olmayan bir işlem dizini durdurur (`ValueError`, işlemi adıyla söyler): dizinden sessizce
  düşen endpoint'i agent hiç bulamazdı.
- **`rules`** kodda yazılı kısa bir metin (`discovery.RULES`): adreslerin `/api` altında olduğu,
  JSON, bilinmeyen alanın hata olduğu, başarının hep 200 olduğu, hatanın dört alanı, `?path=`.
  Yalnız bugün doğru olanı söyler; liste sorgusunu, `at`'i, `/wait`'i onları yapan maddeler ekler.
  Başlıklar yazılmaz: agent onları yazmaz, MCP tool'u ekler (6. adım).
- **Ayrıntı** `GET /api?path=<adres>`: adresteki her fiil için `{"description"?, "path"?, "query"?,
  "body"?, "returns"?, "errors"?}`, boşlar yazılmaz. Alan `{"type", "required", "description", …}`:
  6. adımın modellerdeki biçimi; JSON Schema'nın agent'ın işine yarayan anahtarları kalır (`enum`,
  `default`, sınırlar, `pattern`), `title` ve geri kalanı atılır; `$ref` açılır; `X | null` X'in
  alanlarıyla `"type": "object | null"` olur; iç içe nesne `fields`, liste `items` taşır.
  `required` yalnız girdilerde yazılır. Başlıklar ayrıntıya girmez. `errors` işlemin kendine özgü
  hata kodlarıdır: route `openapi_extra={"x-errors": [...]}` ile söyler; bir test bu kodların
  tabloda olduğunu ister. Bilinmeyen adres `unknown_endpoint`.
- **Dizinin kendisi OpenAPI'de değildir** (`include_in_schema=False`): belgenin okunuşudur, bir
  adresi değil; kendi dizininde satırı olmaz, `rules` onu söyler.
- Çıplak `/api`'nin `/api/`'ye çevrilmesi sorguyu dokunmadan bıraktığı için `GET /api?path=/health`
  ayrıntıyı verir (m527, Sonraki maddeler için); testle.

### Boy sınırları

`tests/budgets.py`'de, bayt olarak (İngilizcede ~4 bayt bir token):

| Ne | Sınır | Neden | Bugün |
|---|---|---|---|
| Dizin | 6144 B | v1'in ~45 endpoint'i × ~65 B, dokuz bölüm, kurallar: ~5,3 KB | 639 B |
| Dizinin bir satırı | 96 B | `"<fiil> <adres>: <birkaç kelimelik özet>"`, tırnaklarıyla | 53 B (health) |
| Bir adresin ayrıntısı | 4096 B | v1'in en büyüğü t2i: ~10 alan girer, bir iş döner | 417 B (health) |
| Bir hata | 2048 B | kod, cümle, kimlikler, hint; en çok bir düzine alan sorunu | 807 B (örnekte yedi sorun) |

Dizin ve her adresin ayrıntısı örnek API'de (core'un bütün grupları dahil) ölçülür; hata sınırına
`contract.checked_client` her hata cevabında bakar. Sınırı geçen değişiklik sayıyı nedeniyle burada büyütür.

## Maliyet

| İşlem | Drive | Disk | Ağ | İşlemci |
|---|---|---|---|---|
| `GET /api` | 0 | 0 | 0 | O(endpoint): bellekteki OpenAPI belgesinden dizin |
| `GET /api?path=` | 0 | 0 | 0 | O(adresteki alan) |
| Herhangi bir hata cevabı | 0 | 0 | 0 | 405'te belgede tek arama |
| Başlıkların ve gövdenin bakışı | 0 | 0 | 0 | gövde boyunca bir sayım |
| Sorgunun bakışı | 0 | 0 | 0 | O(route'un parametresi + gelen parametre) |

OpenAPI belgesini FastAPI ilk istekte bir kez kurar ve tutar; dizin ve ayrıntı her istekte ondan
kurulur, kendi önbellekleri yoktur (45 endpoint mikro saniyeler). Hiçbiri depoya ya da diske gitmez:
API'nin elinde depo yok; depo portu gelince (v1-7) sayan taklitle sınanır.

## Ne bozulabilir

- **Endpoint değiştiren isteği başlıksız kabul ederse** anahtar hiç tutulmaz, aynı istek iki kez
  yapılabilir: belgedeki her değiştiren işlem testle denenir.
- **Gövde modeli `RequestBody`'den türemezse** bilinmeyen alan sessizce atılır: belgedeki her gövde testle
  yürünür.
- **Yanlış yazılmış sorgu parametresi** yok sayılırsa agent başka bir şeyin cevabını doğru sanır
  (`?paht=` bütün dizini döner): reddedilir. FastAPI'nin `dependant`'ının biçimi değişirse
  `test_query.py` düşer.
- **Büyük gövde** belleği doldurmasın: sınır geldikçe sayılır, chunked dahil.
- **Bir istisnanın sözü çağırana gider** (`internal`'ın `message`'ı, 300 baytta kesilmiş;
  doğrulama hatalarında yalnız türü ve sayısı): bugün core hiçbir sır okumaz.
  Sır tutan kapılar (v1-14'ün indirmeleri, Hugging Face token'ı ve Civitai cookie'si) sırrı
  istisnanın metnine, URL'ye ya da log'a koymamalı; koyarsa ekrana da düşer.
- **Dizinden düşen endpoint:** bölümsüz işlem dizini durdurur, gizlenmez.
- **Eski `Allow`:** fiiller belgeden okunur, yalnız ilk route'tan değil.
- İki istek aynı anda: hiçbir parça paylaşılan bir şey yazmaz; OpenAPI belgesini FastAPI kurar.

## Testler

Önce düşen testle (CODE-STANDARD, Testler); hiçbiri gerçek saniye beklemez, ağ açmaz.

- `tests/test_errors.py`: core'un fırlattığı hata dört alanla ve kodunun durumuyla; doğrulama hatası
  400, her alanı adıyla ve koduyla; her pydantic türünün cümlesi; JSON olmayan ve eksik gövde;
  bilinmeyen adres ve sondaki eğik çizgi (yönlendirme yok); 405'te adresin bütün fiilleri, dizinin
  kendi 405'i ve sorgu hatası `/api` adıyla; her hint'in andığı çağrı 200 döner; `internal`
  istisnanın sözüyle, uzunu kesilerek, doğrulama hatalarında yalnız türü ve sayısıyla, sunucuya
  yeniden fırlatılarak; `{name:path}` dönüştürücülü adres; uzun bilinmeyen adres kesilir;
  FastAPI'nin `4xx`'i `body` sorunu, `5xx`'i `internal`; belgede olmayan `/openapi.json`'ın 405'i;
  uzun, iki baytlı, kaçışlı ve tırnaklı adlar baytıyla kesilir; 300 sorunun ilk altısı ve kalanın
  sayısı; en uzun sorunlar da sınırın içinde; her işlemin hata cevabı `Error`, 422 yok; `Error` türü
  UI için; her başarı 200.
- `tests/test_contract.py`: kontrolün ısırdığı; `contract.py` dışında `TestClient(` kuran test yok.
- `tests/test_body.py`: sınırı geçen gövde endpoint'e varmadan reddedilir, chunked da; sınırdaki
  gövde bütün varır; her gövde modeli bilinmeyen alanı reddeder.
- `tests/test_change.py`: başlıksız, boş, uzun, ASCII dışı anahtar ve `core` aktör reddedilir, endpoint
  koşmaz; geçerli başlıklar endpoint'e `Change` olarak varır; `GET` başlık istemez; her değiştiren
  route başlıksız denenir, başlıksız route'u bulduğu da; başlıklar UI'ın türlerinde zorunlu;
  başlık sorununun hint'i başlıkların kuralı, öbür sorunlarla birlikteyse ikisi.
- `tests/test_query.py`: bilinmeyen sorgu parametresi her biri adıyla reddedilir, değişiklik
  yapılmaz; tanımlı parametre alınır; dizinin yanlış yazılmış `?paht=`'i reddedilir; sorgu
  modelinin alanları tanımlı sayılır, olmayanı reddedilir; `own_query` alan route her parametreyi
  alır; adsız parametre `query.(empty)`.
- `tests/api/test_discovery.py`: dizin; endpoint eklemek tam bir satır ekler; her işlem bölümünde
  bir satır; bölümsüz işlem dizini durdurur; dizinin ve satırların boyu; bir adresin ayrıntısı
  (yol, sorgu, iç içe gövde, dönüş, hatalar); başlıklar ayrıntıda yok; bilinmeyen adres; her
  ayrıntının boyu; `x-errors` kodları tabloda.
- `tests/test_server.py`: çıplak `/api` dizin, `/api?path=/health` ayrıntı; `/api/olmayan`
  `unknown_endpoint`.
- ruff ve pyright temiz; commit'lenen `openapi.json` core'unki; UI'ın suite'i yeşil, `dist` değişmedi
  (paket `openapi.json`'dan yalnız `info`'yu alır).

## Bitti sayılır

Kabul koşulunun dört satırı: her hata, FastAPI'ninkiler de, dört alanla ve hint kuralına her cevapta
bakılıyor; değiştiren istek iki başlıksız yapılmıyor, bilinmeyen alan — gövdede de sorguda da — atılmıyor; dizin ve ayrıntı
koddan, endpoint dizini bir satır büyütüyor, boy kayıtlı sınırla sınanıyor; sınır hatalara da
bakıyor. Ayrıca `Error` OpenAPI'de tür olarak duruyor, m527'nin v1-5'e bıraktığı iki not kapandı,
iki suite yeşil.

## Sonraki maddeler için

- **Her endpoint maddesi:** grubun `SECTION`'ı `create_api`'nin `openapi_tags`'ine, router
  `APIRouter(tags=[SECTION["name"]])`; her işlemin kısa bir `summary`'si (dizinin satırı) ve
  agent'a yazılmış `description`'ı olsun. FastAPI `summary`'siz işleme fonksiyonun adından, açıklamasız
  işleme docstring'inden yazar: docstring API'ye sızar.
- **Yeni hata kodu** `CODES`'a satırıyla girer; işlemin kendine özgü kodları `x-errors`'ta.
- **v1-6:** listeleyen endpoint `own_query`'yi alır (Sorgu) ve bilinmeyen alanı kendi
  ayrıştırıcısında reddeder; toplu seçimin `DELETE`'i de öyle; dizinin `rules`'una
  sorgunun bir cümlesi eklenir; listelerin varsayılan alan setinin sınırı `budgets.py`'ye.
  Yinelenen parametre: `known_query` adlara bakar, `?path=/a&path=/b`'yi kabul eder ve FastAPI
  sonuncuyu alır. Aynı alana iki işleç (tarih aralığı) liste sorgusunda geçerli olduğu için
  yinelenmenin kuralı v1-6'nın ayrıştırıcısıyla birlikte yazılsın.
- **v1-10:** `Change`'i alır (yukarıda); birden çok engelli hatanın `details.problems`'ı
  `{code, message, hint, …}` biçimindedir — `contract.check_error` bugün yalnız alan sorunlarına
  bakıyor, engellerin hint'ine bakmayı v1-10 ekler. `Idempotent-Replayed` başlığı da onun.
- **v1-13:** ayrıntı bugün yalnız JSON dönüşü yazar; resim ve video dönen işlemin `returns`'ü
  (medya türü) eklenmeli, yoksa ayrıntı onu hiç söylemez.
- **v1-14, v1-25:** sır tutan kodun istisna metni çağırana gider (Ne bozulabilir).
- **v1-22:** `rules`'un "adresler `/api` altında, burada öneksiz" cümlesi adaptörün adresi nasıl
  aldığına göre düzeltilir.
- **Çok engelli hata (v1-10, v1-12):** engelleri sayan `details.problems` da alan sorunları gibi
  ilk `PROBLEMS_SHOWN`'la ve `details.more`'yla kesilmeli; `order_mismatch`'in `missing`/`extra`
  kimlik listeleri de (20.000 karede binlerce kimlik). Hata sınırına `checked_client` bakar.
