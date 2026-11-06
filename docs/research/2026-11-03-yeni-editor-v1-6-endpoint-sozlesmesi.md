# Yeni editör — 6. Endpoint sözleşmesi

Bütün endpoint'lerin ortak kuralları, hata kodları ve her endpoint'in ne aldığı,
ne döndürdüğü. Endpoint'lerin listesi [1. adımdadır](2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
burada yeni endpoint yoktur. Alan adları ve değerler İngilizcedir (11. adım); bu belgede
mesajların ve hint'lerin anlamı Türkçe yazılır.

## Ortak kurallar

### Adresler

- Bütün endpoint'ler `/api`'nin altındadır: `GET /api`, `GET /api/health`, `GET /api/projects/{p}/frames`…
  Geri kalan her adres UI'ındır; core UI'ı da sunduğu için (9. adım) ikisi çakışmaz, queen-editor'daki
  gibi (kullanıcı, 5 Kasım). Bu belgede, 1. adımdaki gibi, `/api` öneki yazılmaz.
- Adresteki `{p}` projenin kimliği, `{id}` o projedeki şeyin kimliğidir.

### Kimlikler, zaman, sayılar

- **Proje kimliği:** 10 karakter, küçük harf ve rakam (ör. `k3v9q2mz7a`); rastgele, bütün Colab'lar
  arasında tek.
- **Projedeki her şeyin kimliği** (kare, video, edit, yer, iş, export) bir tamsayıdır; projenin tek
  sayacından gelir, o projede tektir, yeniden kullanılmaz (2. ve 4. adım). Türler aynı sayacı
  paylaştığı için bir sayı projede tek bir şeyi gösterir.
- **History kaydı** projenin sıra numarasıyla (`seq`) anılır.
- **Model kimliği** modelin adıdır (ör. `nova-3dcg`, `h3`). **Core kimliği** `GET /health`'in söylediğidir.
- **Zaman** ISO 8601, UTC, saniyeyle: `2026-11-04T09:12:00Z`. Süzgeçte yalnız gün de verilebilir
  (`2026-11-04` = o günün 00:00'ı, UTC).
- **Süre** saniye (sayı), **boyut** bayt (tamsayı).

### Gövde

- İstek ve cevap gövdesi JSON'dur, UTF-8; medya dosyaları dışında.
- **Zarf yoktur.** Tek bir şeyi döndüren cevap o şeyin kendisidir. Liste cevabı:
  `{"items": [...], "total": 1234, "offset": 0, "limit": 100}` — `total` süzgece uyanların sayısıdır.
- Bilinmeyen bir alan hatadır, sessizce atılmaz (1. adım: model almadığı şeyi sessizce atmaz; kural
  bütün gövdelere aynı uygulanır). Adresin almadığı sorgu parametresi de öyledir (`query.<ad>`,
  `unknown`); liste sorgusunu kendisi ayrıştıran endpoint'ler onu kendileri reddeder (madde 529).
- Gövde en çok 4 MB'tır (20.000 karelik bütün sıra ~120 KB).
- **Agent başlıkları görmez:** MCP tool'u çağrının durumunu ve gövdesini döndürür (8. adım). Agent'ın
  bilmesi gereken hiçbir şey yalnız bir cevap başlığında durmaz.

### İstek başlıkları

Değiştiren her istek (`POST`, `PATCH`, `DELETE`) iki başlık taşır; ikisini de MCP adaptörü ve UI
kendileri ekler, agent yazmaz:

| Başlık | Değer | Neden |
|---|---|---|
| `Idempotency-Key` | 1–128 yazdırılabilir ASCII karakter. Adaptör: `<liste anahtarı>-<sıra>` (8. adım); UI: her basışa yeni bir UUID | Aynı istek iki kez yapılmasın (aşağıda) |
| `Actor` | `agent` ya da `ui` | History "kimin yaptığını" kaydeder; bunu isteği yapan söyler (2. adım). `core` yalnız core'un kendi kayıtlarındadır |

Biri eksik ya da geçersizse istek yapılmaz: `invalid_request`. `GET` ikisini de almaz.

### HTTP durumları

| Durum | Ne zaman |
|---|---|
| `200` | Her başarı: okuma, değişiklik, oluşturma, iş verme, `/wait`'in süresinin dolması |
| `400` | İsteğin kendisi yanlış: biçim, eksik ya da bilinmeyen alan, ad kuralı, modelin almadığı alan, sorgu sözdizimi |
| `404` | Adresteki ya da gövdenin gösterdiği şey yok; endpoint yok |
| `403` | Agent'a kapalı istek; adaptörün kendisi döner, core'a gitmez (proje silmek, 8. adım) |
| `405` | Adres var, fiil yok |
| `409` | İstek doğru ama projenin şu anki hali izin vermiyor (kare kuyrukta, export sürüyor, model kurulu değil, aynı anahtar başka içerikle…) |
| `500` | Core'un kendi hatası |
| `503` | Arkadaki servis düştü ya da belirsiz kaldı (Drive) |
| `507` | Drive'da yer yetmiyor (`storage_low`) |

Agent `code`'a bakar; HTTP durumu kaba sınıftır. Yalnız `200` başarıdır; `201`, `202`, `204` kullanılmaz,
çünkü her cevabın bir gövdesi vardır ve tekrarı aynı cevabı döner.

### Değiştiren isteğin cevabı

Değiştiren istek, değiştirdiği şeylerin **bugünkü halini** döner: oluşturulan proje, verilen işler ve
düşecekleri kareler, değişen edit. Silinen şey `{"id": 17, "deleted": true}` olarak görünür; işle
birlikte giden kareler gibi isteğin yan etkileri de cevaptadır (ör. `deleted_frames`). Agent bir sonraki
adım için ikinci bir okuma yapmak zorunda kalmaz (queen-editor de cevapla galeriyi döndürüyordu, ikinci
gidiş-dönüş olmasın diye).

### Aynı istek iki kez

Kural kesindir; 2. ve 4. adımın kararlarının sözleşmesidir.

1. Değiştiren her istek `Idempotency-Key` taşır. Yoksa istek yapılmaz (`invalid_request`).
2. **İsteğin özeti:** fiil, adres, sıralanmış sorgu ve gövdenin kanonik JSON'unun SHA-256'sı. `Actor`
   özete girmez.
3. **Anahtar nerede aranır:** adresteki projenin son 24 saatin değişikliklerinde (history
   kayıtlarında, 4. adım) ve bu core'da hâlâ süren isteklerde. Projeye bağlı olmayan değiştiren
   istekler: `POST /projects` (anahtar Colab diskindeki `creates.json`'da da aranır, 4. adım),
   `POST /models/{id}/download` (yalnız süren
   isteklerde; indirme zaten tekrarı zararsızdır).
4. Gelen istek için, sırayla:
   - **Aynı anahtar bu core'da hâlâ sürüyor, özet aynı:** istek yeniden yapılmaz. İlki biter beklenir,
     en çok 90 sn; ilkinin cevabı (durumu ve gövdesiyle, hata da olsa) buna da döner. 90 sn dolarsa
     `request_in_progress` döner, hiçbir şey yapılmaz.
   - **Aynı anahtar sürüyor, özet farklı:** hemen `idempotency_key_reused`.
   - **Anahtar son 24 saatin bir değişikliğinde, özet aynı:** istek yeniden yapılmaz; ilk isteğin
     durumu, gövdesi değiştirdiği şeylerin bugünkü haliyle döner. Cevapta `Idempotent-Replayed: true`
     başlığı vardır (log ve debug için; agent'ın bilmesi gerekmez).
   - **Anahtar bulundu, özet farklı:** `idempotency_key_reused`.
   - **Anahtar yok:** istek yeni bir istek olarak yapılır.
5. **Kaydedilmeyenler:** reddedilen istek (her `4xx`), hiçbir şeyi değiştirmeyen istek (ör. durmuş
   kuyruğa `pause`) ve `storage_unconfirmed` ile dönen istek anahtar bırakmaz; aynı anahtarla tekrarına
   yeniden bakılır. `storage_unconfirmed`'in tekrarı 4. adımdaki bakıştan geçer: yazılmışsa anahtar
   bulunur, ilk cevap döner; yazılmamışsa bir kez yapılır.
6. 24 saatten eski anahtar unutulur; aynı anahtarla gelen istek yeni istektir.
7. İki projeye yazan tek istek olan `resume`'un anahtarı adresteki projededir.

### Liste sorgusu

Listeleyen her endpoint aynı sorguyu alır (1. adım); sözdizimi PostgREST'inkidir (kullanıcı, 5 Kasım —
"süzülsün, PostgREST dediğin olsun"). FastAPI'nin kendi süzme dili yoktur; sorgu, bellekteki kayıtlara
uygulanan küçük bir ayrıştırıcıdır:

| Ne | Biçim | Örnek |
|---|---|---|
| Süzmek | `<alan>=<işleç>.<değer>` | `status=eq.waiting` |
| İşleçler | `eq`, `neq`, `in.(a,b)`, `gt`, `gte`, `lt`, `lte`, `is.null`, `is.true`, `is.false`; `not.` önüne gelir | `video.status=in.(waiting,running)`, `video=not.is.null` |
| Regex | `match.<desen>` (büyük/küçük harfe bakar), `imatch.<desen>` (bakmaz: desen de metin de önce küçültülür, `I`, `ı`, `İ` ve `i` dördü de `i` sayılır; böylece hem Türkçe hem İngilizce bulunur); Python `re`, desen en çok 200 karakter | `photo.prompt=imatch.yağmur` |
| Tarih aralığı | aynı alana iki işleç | `updated=gte.2026-11-01&updated=lt.2026-11-08` |
| Sıralamak | `order=<alan>.<asc\|desc>,…` | `order=created.desc` |
| Sayfa | `limit` (varsayılan 100, en çok 1000; `0` yalnız `total`'ı verir), `offset` | `limit=50&offset=100` |
| Alanlar | `select=<alan>,<alan.alt>,…`; `select=*` hepsi | `select=id,scene,photo.prompt` |

- Süzülebilen, sıralanabilen ve seçilebilen alanlar cevabın alanlarıdır, türetilenler dahil (ör.
  karenin `video.status`'u). İç içe alan noktayla anılır.
- Birden çok süzgeç "ve"dir. "Veya" yoktur; agent iki çağrı yapar.
- Her listenin bir varsayılan sırası vardır (karelerde `position`, history'de `seq.desc`…) ve kısa bir
  varsayılan alan seti: agent'ın bağlamı gereksiz veriyle dolmasın (1. adım). Tam kayıt tek şeyin
  `GET`'inde ya da `select=*` ile gelir. Tek şeyin `GET`'i de `select` alır.
- Bilinmeyen alan, işleç, bozuk regex ya da tarih: `invalid_request`; `details` o listenin alanlarını sayar.
- **Maliyet:** süzme bellekte yapılır, Drive'a gitmez (4. adım); yalnız history'nin eski blokları
  istenince indirilir (History'de).

### Toplu seçim

`DELETE /projects/{p}/frames` ve `DELETE /projects/{p}/jobs` neyi
seçtiklerini aynı adresin `GET`'ine verilen süzgeçle söyler (kullanıcı, 5 Kasım):
`DELETE /projects/{p}/jobs?status=eq.waiting`, `DELETE /projects/{p}/frames?id=in.(17,18,25)`.

- `GET` aynı süzgeçle neyi listeliyorsa istek ona yapılır; `order`, `limit`, `offset`, `select` alınmaz.
- Süzgeçsiz toplu istek reddedilir (`invalid_request`): yanlışlıkla bütün kareleri silmesin. Hepsi
  isteniyorsa `?all=true` yazılır.
- Ya hep ya hiç (2. adım): seçilenlerden biri bile engelliyse hiçbiri yapılmaz, hata engellerin
  hepsini sayar. Seçim boş çıkarsa istek bir şey yapmadan `200` döner.

### Konum

Bir şeyin sıradaki yeri her yerde aynı alanla söylenir: `"at": "start" | "end" | {"after": <kimlik>}`.
Karelerde kare, kuyrukta iş, edit'te yer kimliğidir.

### `/wait`

- `?timeout=<sn>`, 0–90, varsayılan 90. Tünel ~100 sn sessiz kalan isteği keser (7. adım).
- Beklenen olunca ya da süre dolunca `200` ile, o şeyin `GET`'iyle aynı gövdeyi döner. Süre dolduysa
  gövde "henüz bitmedi" halini gösterir (iş hâlâ `waiting`); hata değildir. Agent yeniden bekler.
- Beklenen şey **kendiliğinden ilerlemiyorsa** da hemen döner: işin ya da kuyruğun beklemesi ancak
  agent'ın bir adımıyla sürecekse (kuyruk durmuş, kuyruğu hiçbir Colab çalıştırmıyor, ya da başka
  bir Colab'daki iş süre sınırının iki katından uzun süredir çalışıyor: o Colab kapanmış olabilir,
  4. adım). Yoksa agent 90 sn'lik beklemeleri sonsuza kadar tekrarlar.
- Export'un `/wait`'i, export'u bu Colab yapmıyorsa hemen döner; hint export'un başka bir Colab'da
  sürdüğünü, o Colab kapandıysa `DELETE …/exports/{id}` ile iptal edilebileceğini söyler.
- Bir listede en çok bir `/wait` olur; adaptör ikincisini taşıyan listeyi hiçbir çağrı göndermeden
  reddeder (`too_many_waits`, 8. adım). Birden çok işi beklemek için `…/queue/wait` kullanılır.

### Medya

- Fotoğraf `image/png`; küçüğü (`?size=small`, uzun kenarı 512 px) `image/jpeg`. Video `video/mp4`,
  `Range` isteklerini kabul eder (UI'daki oynatma için).
- Fotoğraf hiç değişmez ve kimlikler yeniden kullanılmaz: `Cache-Control: public, max-age=31536000,
  immutable`. Karenin videosu silinip yeniden üretilebildiği için video adresinin içeriği değişebilir:
  `ETag` videonun kimliğidir, `Cache-Control: no-cache`. (queen-editor'da adın yeniden kullanılması
  önbelleği bozuyordu; backlog, 481.)
- İlk istek dosyayı Drive'dan indirir (~1 sn), sonra diskten (4. adım).

## Hatalar

### Biçim

Her hata dört alanla döner (11. adım):

```json
{"code": "frame_in_queue",
 "message": "Frame 17 cannot be deleted: job 4401 is waiting for it.",
 "details": {"frame": 17, "jobs": [4401]},
 "hint": "Removing job 4401 from the queue is enough; the frame has no photo yet, so it goes with the job."}
```

- `details` her zaman bir nesnedir, boş olabilir. `hint` yoksa `null`'dır.
- **Birden çok engel:** ya hep ya hiç bir istek engellerin hepsini sayar (2. adım). Her engel
  `details.problems`'ta kendi `code`, `message`, `hint`'iyle ve gösterdiği kimliklerle durur. Üstteki
  `code` hepsi aynıysa o, değilse `several_problems`'tır; `message` kaç engel olduğunu söyler.
- `400`'lerde her sorun bir alanı gösterir: `{"field": "body.negative", "code": "not_accepted",
  "message": …}`. Alan yolları `body.`, `query.`, `header.` ya da `path.` (adresteki alan, ör. `{id}`) ile başlar. Alan sorunlarının kodları:
  `missing`, `unknown`, `wrong_type`, `not_allowed` (izinli değerlerden değil), `out_of_range`,
  `not_accepted` (model bu alanı almıyor), `not_supported` (model bu yöntemi yapmıyor), `name_rule`,
  `duplicate`, `bad_query`.
- FastAPI'nin kendi doğrulama hataları da bu biçime çevrilir; mesajları biz yazarız (5. adım).
- **Hint kuralı** (11. adım): core'un kendi kuralından gelen hatada ne yapılacağını söyler. Servis
  hatasında (Drive, ComfyUI, ffmpeg) `message` servisin sözüdür; `hint` neden tahmin etmez, emir
  vermez, yalnız durumu ve elde olan seçeneği söyler. Kesin bir şey yoksa `null`.

### İsteğin hataları

"Hint" sütunu: **kural** — core'un kuralı, ne yapılacağını söyler; **seçenek** — servis hatası, durumu
ve seçeneği söyler; **yok** — `null`.

| `code` | HTTP | Ne zaman | Hint |
|---|---|---|---|
| `invalid_request` | 400 | Gövde, sorgu ya da başlık yanlış; `details.problems` her alanı sayar | kural: ne verilmeli; modelin alanlarıysa `GET /models/{id}`'yi gösterir |
| `too_many_waits` | 400 | Listede birden çok `/wait` var; adaptör listeyi göndermez (8. adım) | kural: bir listede tek `wait`; birden çok iş için `…/queue/wait` |
| `unknown_endpoint` | 404 | Böyle bir adres yok | kural: `GET /api` |
| `method_not_allowed` | 405 | Adres var, bu fiil yok | kural: adresin fiilleri |
| `project_not_found` | 404 | Proje yok ya da silinmiş; ikisi ayrılmaz | yok |
| `project_delete_not_allowed` | 403 | Agent proje silmek istedi; adaptör göndermez (8. adım) | kural: proje silmek kullanıcının işidir, UI'dan silinir; arşivlemek agent'ın elindedir |
| `frame_not_found` | 404 | Kare yok; adreste ya da gövdede. Core karenin silindiğini biliyorsa `details.deleted` | yok |
| `edit_not_found`, `place_not_found`, `job_not_found`, `export_not_found`, `model_not_found` | 404 | Aynısı, kendi türü için | yok |
| `no_media` | 404 | İstenen dosya yok: fotoğrafı henüz gelmedi, videosu yok, ya da Drive'da elle çöpe atılmış (`details.reason`) | gelecekse kural: işin `wait`'i; Drive'da yoksa seçenek |
| `frame_in_queue` | 409 | Silinecek karenin ya da videonun işi kuyrukta (bekliyor ya da çalışıyor); `details.jobs` | kural: işleri `DELETE …/jobs/{id}` ile çıkarmak; fotoğrafı gelmemiş kare işiyle birlikte gider (1. adım) |
| `frame_in_export` | 409 | Silinecek kareyi süren bir export kullanıyor; `details.export` | kural: export'u beklemek (`…/exports/{id}/wait`) ya da iptal etmek |
| `order_mismatch` | 409 | Bütün sıra (kareler ya da kuyruk) bugünkü hepsini tam bir kez içermiyor; `details.missing`, `extra`, `duplicate` | kural: eksikleri ve fazlaları söyler |
| `job_finished` | 409 | Son durumdaki iş kuyruktan çıkarılmak istendi; `details.status` | yok |
| `model_not_installed` | 409 | İşin modeli bu Colab'da kurulu değil ve inmiyor (10. adım) | kural: `POST /models/{id}/download`; inerken iş verilebilir |
| `model_wrong_gpu` | 409 | Model bu Colab'ın kartında çalışmıyor; `details.gpu`, `details.gpus` | seçenek: modelin çalıştığı kartlar; kullanıcıya sor |
| `export_running` | 409 | Bu Colab'da başka bir export sürüyor; `details.project`, `details.export` (başka projeninki olabilir) | kural: `GET /projects/{project}/exports/{export}/wait` |
| `export_blocked` | 409 | Edit boş, silinmiş yer ya da videosu olmayan kare var; `details.problems` yerleri sayar | kural: yerleri çıkarmak ya da başka kareye çevirmek (`PATCH …/edits/{id}`) |
| `export_finished` | 409 | Bitmiş (ya da başarısız, iptal) export iptal edilmek istendi | yok |
| `idempotency_key_reused` | 409 | Aynı anahtar farklı bir istekle geldi | kural: yeni istek yeni anahtarla |
| `request_in_progress` | 409 | Aynı anahtarlı ilk istek 90 sn'de bitmedi | kural: aynı anahtarla yeniden gönderilince bitmişse ilk cevabı döner |
| `project_newer_format` | 409 | Proje bu core'dan yeni bir sürümle yazılmış (4. adım) | seçenek: Colab'ı yeni sürümle açmak; kullanıcıya sor |
| `storage_unconfirmed` | 503 | Drive'a yazma ~60 sn'de belli olmadı (4. adım) | seçenek: aynı anahtarla yeniden gönderilirse yapılmışsa ilk cevap döner, yapılmamışsa bir kez yapılır |
| `storage_rejected` | 503 | Drive yazmayı reddetti (kota, hız sınırı ~60 sn sürdü) | seçenek: hiçbir şey yazılmadı; aynı anahtarla yeniden gönderilebilir |
| `project_unreadable` | 503 | Projenin baş dosyası okunamıyor; projeye her istek bunu alır | seçenek: önceki hali Drive'ın sürüm geçmişinde; kullanıcının kararı |
| `storage_low` | 507 | Export başlarken Drive'daki boş yer çıktının tahmini + 2 GB'tan az (4. adım) | seçenek: yer açılınca yeniden denenebilir; kullanıcıya sor |
| `ffmpeg_failed` | 503 | Durağan görüntü ya da küçük fotoğraf üretilemedi; `message` ffmpeg'in sözü | yok |
| `internal` | 500 | Core'un hatası; `message` hatanın kendisi, ayrıntısı log'da | yok |

### Export'un ve kuyruğun nedenleri

Export'un başarısızlığı ve kuyruğun kendiliğinden durması da aynı dört alanla kayıtta durur
(`export.error`, `queue.stop_reason`). İş başarısız olmaz: işin hatası da kuyruğu durdurur, iş sıranın
başında bekler (2. adım). Bunlar isteğin hatası değildir; istek `200` döner, neden kaydın içindedir.

| `code` | Nerede | Ne zaman | Hint |
|---|---|---|---|
| `comfy_error` | kuyruk | ComfyUI işe hata verdi (ör. geçersiz prompt); `message` ComfyUI'nin sözü (7. adım) | seçenek: iş sıranın başında bekliyor; `resume` onu baştan üretir, ya da iş `DELETE …/jobs/{id}` ile çıkarılıp düzeltilmiş hali verilir |
| `generation_timeout` | kuyruk | Fotoğraf 5, video 10 dk'da bitmedi (varyantlarda çarpılır); `message` ComfyUI'nin son sözü | seçenek: aynısı |
| `comfy_down` | kuyruk | ComfyUI yeniden başlatıldıktan sonra da düştü ya da açılamadı; `message` ComfyUI log'unun ilgili satırları | seçenek: kuyruk bu yüzden durdu; düzelince `POST …/queue/resume`; kullanıcıya sor |
| `model_download_failed` | kuyruk | Sırası gelen işin modeli inemedi; `message` kaynağın ya da aracın sözü | seçenek: `POST /models/{id}/download` yeniden, sonra `resume` |
| `storage_low` | kuyruk | İş başlarken Drive'da yer yetmedi | seçenek: işler bekliyor; yer açılınca `resume`; kullanıcıya sor |
| `storage_rejected` | kuyruk, export | Ürün Drive'a yüklenemedi | seçenek |
| `ffmpeg_failed` | export | ffmpeg'in sözü | yok |
| `core_restarted` | export | Export'u yapan core yarıda kapandı (4. adım) | seçenek: yeniden başlatılabilir |
| `media_gone` | export | Bir yerin videosu Drive'da yok (elle çöpe atılmış) | yok |

## Endpoint'ler

Her biri için kısaca: ne alır, ne döner, kendine özgü hataları. Ortak hatalar (`invalid_request`,
`*_not_found`, depo hataları, anahtar hataları) tekrar yazılmaz. Her değiştiren istek anahtar ve
`Actor` taşır.

### Discovery

**`GET /api`** — Agent'ın API'yi öğrendiği dizin; koddan üretilir (kullanıcı, 5 Kasım — "token
olarak efficient olsun"; "endpoint miktarı scale oldukça patlamayalım diye"):

```json
{"app": "queen-studio", "version": "1.0.0",
 "rules": "<ortak kurallar, kısa: adresler, anahtar, liste sorgusu, konum, wait, hata biçimi>",
 "sections": [{"name": "Frames",
               "about": "<iki üç cümle: kare nedir, sırası, fotoğrafı ve videosu>",
               "endpoints": ["GET /projects/{p}/frames: Projenin kareleri"]}]}
```

Her endpoint tek bir metin satırıdır, `"<fiil> <adres>: <özet>"`; nesne değildir, çünkü üç anahtarın
her satırda yinelenmesi endpoint başına ~30 bayt tutar (madde 529; kararlar, Sapmalar).

**`GET /api?path=<adres>`** — Bir adresin ayrıntısı: o adresteki her fiilin aldığı alanlar (tür,
zorunlu mu, bir cümle), döndürdüğü ve kendine özgü hataları. Ör. `GET /api?path=/projects/{p}/frames`
`GET`, `PATCH` ve `DELETE`'i birlikte verir. Modelin aldığı alanlar `GET /models/{id}`'dedir; burada
tekrar yazılmaz, oraya gösterilir. Bilinmeyen adres `unknown_endpoint`.

- Agent oturumun başında dizini okur, ayrıntıya yalnız kullanacağı adres için bakar; birkaç adresin
  ayrıntısı tek listede istenir. Endpoint sayısı arttıkça dizin endpoint başına bir satır büyür.
- Tam OpenAPI `GET /api/openapi.json`'dadır; UI'ın TypeScript türleri ondan üretilir (5. adım), agent'a
  gerekmez.

**`GET /health`** — `{"app": "queen-studio", "core": "<core kimliği>", "version": "1.0.0"}`; `app`,
`GET /api`'deki gibi, uygulamanın tek ad sabitinden okunur. Drive'a gitmez. Adaptör `app`'e bakarak adresin bizim core'umuz olduğunu doğrular (8. adım).

### Models

**`GET /models`** — Liste. Varsayılan alanlar: `id`, `kind` (`photo` | `video`), `description`,
`size` (bayt), `gpus` (çalıştığı kartlar), `runs_here` (bu Colab'ın kartında çalışıyor mu), `status`
(`installed` | `downloading` | `failed` | `absent`), `progress` (0–100, iniyorsa), `error` (inemediyse,
dört alanlı). Ör. `?kind=eq.video&status=eq.installed`, `?runs_here=is.true`.

**`GET /models/{id}`** — Yukarıdakiler ve:
- `methods`: her yöntem (`t2i`, `i2v`) için aldığı alanlar: `{"negative": {"type": "string",
  "required": true, "description": …}, …}`. İşin gövdesi buna karşı bakılır.
- `loras`: seçimler, `{"id", "description", "trigger", "files": [{"file", "strength"}]}`; `none` da
  bir seçimdir.
- `orientations`, `lengths` (video, saniye), `max_variants`.

**`POST /models/{id}/download`** — Gövde yok. İndirmeyi başlatır; iniyorsa ya da kuruluysa bir şey
yapmaz. Döner: model (`GET /models/{id}`'nin kısa hali). Hata: `model_wrong_gpu`. İnemediyse yeniden
dener.

**`GET /models/{id}/wait`** — İnmesi bitene (kurulu ya da inemedi) kadar bekler; model döner. İnmiyorsa
hemen döner.

### Projects

Bir projenin satırı: `id`, `name`, `archived`, `created`, `updated`, `runner` (`this` | `other` |
`null`: kuyruğunu bu Colab mı, başka bir Colab mı çalıştırıyor). Bunlar ana listenin etiketlerinden
gelir (4. adım); liste projeleri yüklemez.

**`GET /projects`** — Satırların listesi, yalnız bu alanlarla süzülür. Varsayılan sıra `updated.desc`.
Ör. `?name=imatch.gece`, `?updated=gte.2026-10-29`, `?archived=is.true`. Okunamayan proje listede
`unreadable: true` ile görünür. Maliyet: 0–1 Drive listelemesi (5 sn önbellek).

**`GET /projects/{id}`** — Satır ve `counts`: `{"frames", "edits", "waiting_jobs"}`. Projeyi yükler
(ilk seferde ~1–5 sn, 4. adım). `lost_changes`: bu core'un bu projede, başka bir Colab'ın aynı andaki
yazmasıyla kaybolan değişiklikleri; her biri zamanı, `action`'ı ve hedefiyle (4. adım, Değerlendirme
4). Core'un belleğindedir, log'a da yazılır; core yeniden başlayınca boşalır. Yoksa boş liste.

**`POST /projects`** — Gövde `{"name"}`. Döner: `{"project": <satır>, "same_name": [<satır>…]}`;
aynı adlı başka proje varsa `same_name` onları sayar (2. adım). Hata: ad kuralı
(`invalid_request`, `name_rule`; mesaj hangi kuralın bozulduğunu söyler).

**`PATCH /projects/{id}`** — Gövde `{"name"?, "archived"?}`, en az biri. Döner: aynı biçim
(`project`, `same_name`).

**`DELETE /projects/{id}`** — Yalnız UI'dan, bir onayla; adaptör göndermez (8., 9. adım). Gövde
yok. Projenin bütün dosyaları, history'si dahil, Drive'ın çöpüne gider (4. adım). Döner: `{"id",
"deleted": true}`. Başka Colab'daki üretim en geç 30 sn'de durur.

### Frames

Kare:

```json
{"id": 17, "position": 3, "scene": "…",
 "photo": {"status": "done", "job": 4401,
           "prompt": "…", "model_prompt": "…", "negative": "…", "model": "nova-3dcg",
           "lora": {"id": "…", "files": [{"file": "…", "strength": 0.8}]},
           "orientation": "portrait", "seed": 123, "batch_index": 0,
           "width": 832, "height": 1216, "created": "…", "from_frame": null},
 "video": {"status": "done", "id": 233, "job": 4410,
           "prompt": "…", "model_prompt": "…", "model": "h3", "length": 5, "seed": 9,
           "happy_ending": false, "duration": 5.04, "created": "…"}}
```

- `photo.status`: `waiting` | `running` | `done`. `video.status`: `none` | `waiting` |
  `running` | `done`. İkisi de işlerden okunur, saklanmaz (2. adım). Ürünü gelmemiş karenin
  bilgisi işinden gelir.
- `position` bugünkü yerdir (0'dan), kimlik değildir.

**`GET /projects/{p}/frames`** — Liste; varsayılan sıra `position`, varsayılan alanlar `id`,
`position`, `scene`, `photo.status`, `video.status`. Ör. `?photo.prompt=imatch.yağmur`,
`?video.status=eq.none`.

**`GET /projects/{p}/frames/{id}`** — Bütün kare.

**`PATCH /projects/{p}/frames/{id}`** — Gövde `{"at": …}`. Döner: kare.

**`PATCH /projects/{p}/frames`** — Gövde `{"order": [kimlikler]}`. Döner: `{"order": [...]}`. Hata:
`order_mismatch`.

**`DELETE /projects/{p}/frames/{id}`** — Döner: `{"id", "deleted": true}`. Hatalar: `frame_in_queue`,
`frame_in_export`.

**`DELETE /projects/{p}/frames/{id}/video`** — Döner: kare (videosuz). Hatalar: `no_media`,
`frame_in_queue`, `frame_in_export`.

**`DELETE /projects/{p}/frames`** — Toplu seçimle. Döner: `{"deleted": [kimlikler]}`.
Hatalar: tek kareninkiler, `details.problems`'ta kare kare.

### Media

**`GET /projects/{p}/frames/{id}/photo`** — `?size=full|small`, varsayılan `full`. Hata: `no_media`.

**`GET /projects/{p}/frames/{id}/video`** — Video. Hata: `no_media`. UI'ın oynatması içindir; adaptör
videoyu agent'a göndermez, yalnız türünü ve boyutunu söyler (8. adım).

**`GET /projects/{p}/frames/{id}/video/stills/{n}`** — Videonun `n`. saniyesindeki kare, `image/jpeg`
(kullanıcı, 5 Kasım). `n` tam sayıdır, `0`'dan videonun süresine kadar; son sayı son kareyi verir. 5
sn'lik videoya bakmak tek listede `0`…`5` için altı çağrıdır. Her resim kendi çağrısının cevabıdır;
hiçbir resim JSON'un içinde dolaşmaz, adaptör onu agent'a resim olarak verir (8. adım; sıkı test
edilir). `?size=small|full`, varsayılan `small` (uzun kenarı 512 px, ~200 token). Diskte üretilir,
saklanmaz (4. adım). Hatalar: `no_media`, `n` süreyi aşarsa `invalid_request`, `ffmpeg_failed`.

### Edits

Edit: `{"id", "name", "created", "updated", "places": [{"id", "frame", "muted", "deleted"}]}`;
`deleted` yerin karesi silinmişse `true`'dur.

**`GET /projects/{p}/edits`** — Liste; varsayılan sıra `updated.desc`, varsayılan alanlar `id`,
`name`, `updated`, `places_count`. Ör. `?updated=gte.2026-11-05`.

**`GET /projects/{p}/edits/{id}`** — Bütün edit, yerleri sırasıyla.

**`POST /projects/{p}/edits`** — Gövde `{"name", "places"?: [{"frame", "muted"?}], "all_frames"?:
true}`. `all_frames` projenin bütün karelerini karelerin sırasıyla koyar; `places` ile birlikte
verilemez. `muted` verilmezse `false`. Döner: edit.

**`PATCH /projects/{p}/edits/{id}`** — Bir istek, bir işlem; gövde `op`'la ayrılır:

| `op` | Gövde | Ne yapar |
|---|---|---|
| `rename` | `name` | Adı değiştirir |
| `add` | `frames: [kimlik…]`, `at` (yer kimliğiyle; verilmezse `end`), `muted`? | Kareleri yan yana koyar; aynı kare birden çok kez olabilir |
| `remove` | `places: [yer…]` | Yerleri çıkarır |
| `move` | `places: [yer…]`, `at` | Yerleri sırasıyla oraya taşır |
| `set` | `places: [{"id", "frame"?, "muted"?}]` | Yerin karesini ya da sesini değiştirir; yerin kimliği kalır (2. adım). Silinmiş yere yeni kareyi koymak budur |
| `replace` | `places: [{"id"?, "frame", "muted"?}]` | Bütün sırayı verir; `id`'li yer kalır, `id`'siz yeni yerdir; verilmeyen yerler çıkar |

Döner: edit. Ya hep ya hiç; bir istek bir history kaydı.

**`DELETE /projects/{p}/edits/{id}`** — Döner: `{"id", "deleted": true}`.

### Jobs

İş:

```json
{"id": 4401, "method": "t2i", "status": "waiting", "target_frame": 4402, "source_frame": null,
 "input": {"…": "verilen her şey"}, "seed": 123, "created": "…", "started": null, "finished": null,
 "generation_seconds": null, "stop_reason": null}
```

- `status`: `waiting` | `running` | `done` | `cancelled`. İş başarısız olmaz; hata verirse kuyruk
  durur, iş `waiting` olarak sıranın başına döner (2. adım).
- `stop_reason` türetilir: bekleyen işte kuyruğun kendiliğinden durma nedenidir.

**Bütün üretim endpoint'lerinin cevabı:** `{"jobs": [<iş>…], "queue": <kuyruk>}`. Her iş düşeceği
kareyi (`target_frame`) söyler (1. adım). `queue` kuyruğun bugünkü halidir; kendiliğinden durmuşsa
nedeni `stop_reason`'dadır ve iş yine kabul edilmiştir (2. adım). Kuyruğu kimse çalıştırmıyorsa (bu
Colab başka projenin kuyruğunu çalıştırıyor) `queue.state` bunu söyler.

**`POST /projects/{p}/jobs/photo/t2i`** — Gövde:

| Alan | |
|---|---|
| `scene` | zorunlu |
| `prompt` | zorunlu |
| `negative` | model alıyorsa zorunlu (boş metin geçerli); almıyorsa verilemez |
| `model` | zorunlu |
| `lora` | zorunlu, modelin seçimlerinden; `none` da seçimdir |
| `orientation` | zorunlu, modelin yönlerinden |
| `variants` | zorunlu, 1–`max_variants` |
| `seed` | isteğe bağlı, verilmezse rastgele; varyantların seed'i ondan türetilir: `seed`, `seed+1`… |
| `at` | isteğe bağlı; yeni karelerin yeri, verilmezse `end` |

Ve modelin `methods.t2i`'sinde başka alan varsa onlar. Hatalar: `model_not_installed`; modelin almadığı
alan `invalid_request` (`not_accepted`).

**`POST /projects/{p}/jobs/video/i2v`** — Gövde: `frame` (kaynak kare), `model`, `prompt`, `length`
(modelin uzunluklarından), `seed`?, ve modelin `methods.i2v`'sindeki alanlar (bugün H3'te
`happy_ending`). Kaynağın videosu yoksa ve onu hedefleyen iş yoksa video o kareye, değilse kaynağın
hemen arkasına giren yeni bir kareye düşer (2. adım). Hatalar: `model_not_installed`; kaynak karenin
fotoğrafı yoksa `no_media`.

**`GET /projects/{p}/jobs`** — Liste, bitenler dahil; varsayılan sıra `created.desc`, varsayılan
alanlar `id`, `method`, `status`, `target_frame`, `created`. Ör.
`?method=eq.i2v&status=eq.waiting`.

**`GET /projects/{p}/jobs/{id}`** — Bütün iş.

**`GET /projects/{p}/jobs/{id}/wait`** — İş son durumuna varana kadar, ya da kuyruğu kendiliğinden
ilerlemiyorsa hemen; iş döner.

**`DELETE /projects/{p}/jobs/{id}`** — Bekleyen ya da çalışan işi çıkarır. Döner: `{"job": <iş>,
"deleted_frames": [...]}`; iş için açılmış, ürünü gelmemiş kare işle birlikte gider (1. adım). Hata:
`job_finished`.

**`DELETE /projects/{p}/jobs`** — Toplu seçimle. Döner: `{"cancelled": [işler], "deleted_frames":
[...]}`. Hata: `job_finished`, `details.problems`'ta.

### Queue

Kuyruk:

```json
{"state": "running", "paused": false, "stop_reason": null, "runner": "this",
 "running": 4401, "waiting": [4403, 4404]}
```

- `state` türetilir: `empty` (bekleyen ve çalışan yok), `running`, `waiting_model` (model iniyor),
  `starting_comfy` (ComfyUI açılıyor), `paused` (istekle durduruldu), `stopped` (kendiliğinden durdu;
  nedeni `stop_reason`), `unrun` (bekleyen var, çalıştıran Colab yok).
- `runner`: `this` | `other` | `null`; hangi Colab olduğu söylenmez (9. adım).

**`GET /projects/{p}/queue`** — Kuyruk.

**`GET /projects/{p}/queue/wait`** — Kuyruk ilerlemeyi bırakana kadar bekler: `state` `running`,
`waiting_model` ya da `starting_comfy` dışında bir şey olunca. Kuyruk döner.

**`PATCH /projects/{p}/queue`** — Gövde `{"move": [işler], "at": …}` ya da `{"order": [işler]}`.
Döner: `{"queue": <kuyruk>, "skipped": [...]}`; o arada başlamış ya da bitmiş işler atlanır (2. adım).
Hata: `order_mismatch` (eksik ya da hiç var olmamış iş).

**`POST /projects/{p}/queue/pause`** — Gövde yok. Döner: kuyruk.

**`POST /projects/{p}/queue/resume`** — Gövde yok. Döner: `{"queue": <kuyruk>, "released": <proje
kimliği> | null}`; `released`, bu Colab'ın bıraktığı öbür projenin kuyruğudur. `stop_reason` silinir.
Boş kuyrukta yalnız durmuşluğu kalkar.

**`DELETE /projects/{p}/queue`** — Döner: `{"queue": <kuyruk>, "cancelled": [işler],
"deleted_frames": [...]}`.

### Exports

Export: `{"id", "name", "folder", "link", "edit", "status", "created", "finished", "error",
"places": [{"frame", "muted"}]}`; `status`: `running` | `done` | `failed` | `cancelled`; `places`
başladığı andaki kopyadır (2. adım).

**`POST /projects/{p}/exports`** — Gövde `{"edit", "name"?, "preview"?: true}`. `name` en çok 58
karakterdir (2. adım); verilmezse `<proje> - <edit>`, 58 karakterde kesilir, sonda kalan boşluk ve
noktalar atılır. Döner: export (adın son hali `(1)` dahil, klasörü, bağlantısı).
`preview: true` hiçbir şey oluşturmaz, kaydetmez, hata vermez; döner: `{"name", "videos", "seconds",
"muted_places": [...], "places_without_video": [...], "deleted_places": [...], "can_start": bool}`.
Hatalar: `export_blocked`, `export_running`, `storage_low`.

**`GET /projects/{p}/exports`** — Liste; varsayılan sıra `created.desc`, varsayılan alanlar `id`,
`name`, `status`, `created`.

**`GET /projects/{p}/exports/{id}`** — Export.

**`GET /projects/{p}/exports/{id}/wait`** — Son durumuna kadar; export döner.

**`DELETE /projects/{p}/exports/{id}`** — Süren export'u iptal eder, başka Colab'ınkini de. Döner:
export. Hata: `export_finished` (birleşik videosu yüklenmişse export `done` olmuştur, 1. adım).

**`GET /projects/{p}/exports/{id}/files`** — Liste: `{"name", "kind": "video" | "photo", "size",
"link"}`; varsayılan sıra `name`.

### History

Kayıt: `{"seq", "time", "actor": "agent" | "ui" | "core", "core", "action", "target": {"type",
"id"}, "before", "after"}`.

- `action`: `project.create`, `project.rename`, `project.archive`, `frames.order`,
  `frame.move`, `frame.delete`, `frames.delete`, `video.delete`, `edit.create`, `edit.change`,
  `edit.delete`, `jobs.create`, `jobs.cancel`, `queue.order`, `queue.pause`,
  `queue.resume`, `queue.clear`, `queue.stop` (kendiliğinden), `export.start`, `export.cancel`,
  `photo.arrived`, `video.arrived`. Yeni bir değişiklik türü yeni bir ad alır.
- `before` ve `after` veridir, dosya değil; büyük olabilir (20.000 karenin sırası ~0,7 MB).

**`GET /projects/{p}/history`** — Liste; varsayılan sıra `seq.desc`, varsayılan alanlar `before` ve
`after` dışında hepsi. Ör. `?target.id=eq.40&select=*`, `?action=eq.frame.delete&time=gte.2026-11-05`.
Maliyet: son kayıtlar bellektedir; eski bir sayfa ya da süzgeç eski blokları yeniden eskiye indirir
(blok başına ~0,4 sn, sonra diskten). `seq=lt.<n>` ya da tarih aralığı indirilecek blokları sınırlar.
