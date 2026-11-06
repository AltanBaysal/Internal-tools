# Madde 533 · Yapılmış kodun sınırları — tasarım

**Tarih:** 7 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-42),
533 · v1-42 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

[Kararlar 12](../roadmaps/2026-11-06-queen-studio-v1-kararlar.md#sapmalar)'nin denetimi 527–529'un
kodunda dört açık buldu ([kararlar 15](../roadmaps/2026-11-06-queen-studio-v1-kararlar.md#sapmalar)).
Bu madde onları kapatır: girdinin sürebildiği her harcamanın, iş yapılmadan önce bir sınırı olur
([CODE-STANDARD, Cost](../../queen-studio/CODE-STANDARD.md#cost)). Her sınır küçük kurulmuş bir
testle sınanır; hiçbir test megabaytlık gövde göndermez.

## Kararlar

### 1. `GET /api/health` iş parçacığı beklemez

- `health` artık `async def`'tir (`core/api/endpoints.py`), dizin gibi: yalnız belleği okur.
  Düz `def` her istekte anyio'nun 40 işçi iş parçacığından birini ister; bekleyen istekler
  (`/wait`, yavaş Drive çağrıları) hepsini tutunca health de sıraya girer ve agent core'u gitmiş
  sanır. Kural FOUNDATION 2'ye yazıldı: yalnız belleği okuyan endpoint `async`'tir.
- **Test:** işçi sınırı 1'e indirilir, bir test route'u onu bir olayla tutar; health o arada cevap
  verir. Route tutmayı en çok 5 sn sonra bırakır, yalnız test düşerken: yeşil yol hiç beklemez.

### 2. Bir gövde en çok 1 MiB

- `core/body.py` `MAX_BYTES` 4 MiB'tan 1 MiB'a iner. API'nin alacağı en büyük gövde edit'in 5000
  yerlik `replace`'idir (~250–300 KB); 20.000 karenin sırası (~120 KB), 1000'lik toplu seçim ve
  4000 karakterlik prompt altında kalır. 1 MiB en büyüğün ~3,5 katıdır; medya gövdeyle gelmez
  (6. adım, Gövde). Gövdenin sürdüğü her sayı — öğeleri, bilinmeyen anahtarları, onların
  hataları — buna dayanır. 6. adımın Gövde satırı düzeltildi.
- Hata baytla söyler, sorgununki gibi: `The body is over 1,048,576 bytes, the most one request
  takes.` Böylece sınır testte küçük kurulunca (1024) cümle de doğru kalır.

### 3. Aynı anda tutulan gövdeler en çok 8 MiB

- Bağlantıyı değil, belleği harcayanı sınırlarız (ana agent'ın kararı, review'dan sonra). Uvicorn'un
  `limit_concurrency`'si boştaki keep-alive bağlantılarını ve gövdesiz `GET`'leri de sayar, düz
  metinle cevap verir; tünel HTTP/2 olduğu için bir ekranın küçük fotoğraf yağmuru onu aşardı.
- `BodyLimit` gövdenin belleğinin zaten sahibidir; artık o anda okunan ya da cevaplanan bütün
  gövdelerin baytını da sayar (`held`). Bir parça bu toplamı `HELD_BYTES`'ın üstüne çıkaracaksa
  istek okunmadan 503 `busy` alır (yeni kod, `CODES`'ta ve 6. adımın tablosunda; hint: hiçbir şey
  yapılmadı, öndekiler cevaplanınca yeniden gönderilir). Gövde isteğin cevabı bitene kadar sayılır;
  okunurken düşen, reddedilen ya da cevaplanan her istek tuttuğunu bırakır (`finally`).
  Gövdesiz istek — `GET`, health — burada hiç reddedilmez.
- **Bayt, sayı değil:** sayıyla 100 baytlık gövdeler de en büyüğü gibi sayılırdı. **8 MiB, neden:**
  reviewer'ın ölçümüyle `json.loads` `[{},{}…]`'yi ham boyunun ~23 katına çıkarır, 1 MiB'lık gövde
  ~24 MB olur; ayrıştırılmış gövdeler FastAPI'nin ayrıştırma ile doğrulama arasında bir işçi
  beklediği yerde (bir `def` bağımlılığı) birikir. 8 MiB en çok sekiz en büyük gövde, en kötü
  ~190 MB; en büyük gerçek gövdeden ~27 tane. Agent çağrılarını sırayla gönderir (8. adım), UI'ın
  değişiklikleri küçüktür: meşru iş sınırın çok altında.
- Kontrol ile ekleme arasında `await` yok: olay döngüsündeki iki istek aynı boşluğa birlikte
  giremez.
- **Test:** sınırlar küçük kurulur; bir route gövdesini tutarken ikinci gövde 503 `busy` alır,
  değişiklik yapılmaz, health 200 verir; tutulan bırakılınca aynı istek geçer. `BodyLimit`
  doğrudan sürülerek (test istemcisi gövdeyi tek iletiyle gönderir) büyük gövde, gövdenin
  ortasında ayrılan çağıran ve cevaplanan istek sonrası `held` 0'dır.

### 4. Hata yalnız gösterdiği sorunları biçimler

- FastAPI'nin doğrulama hatasının handler'ı (`core/errors.py`) yalnız ilk `PROBLEMS_SHOWN` (6)
  sorunu cümleye çevirir; kalanları sayar (`details.more`, üst `message`'daki toplam). Önceden her
  sorun biçimlenip sonra atılıyordu: 1 MiB'lık bilinmeyen anahtarlı gövde ~75.000 hata getirir.
- Hint bütün sorunların yerlerine bakar (`header` var mı, başka yer var mı). Yer tek yoldan
  çıkar, `_places`: alanın ilk parçası; doğrulama handler'ı onu biçimlemeden `loc`'un ilk
  parçasından verir. Herkese açık `invalid(address, problems, details)` aynı imzayla kaldı ve her
  alanı zorunlu `_invalid(address, shown, count, places, details)`'a bırakır.
- `_failure` pydantic'in `ValidationError`'ını `error_count()` ile sayar (`errors()` her hata için
  bir dict kurar), FastAPI'ninkini `len(errors())` ile.
- **Ölçüm** (bu makinede, 4000 bilinmeyen anahtarla): hata başına süre ~45 µs'den ~10 µs'ye indi.
  Bellek tepesi hata başına ~0,9 KB kaldı: FastAPI'nin ve pydantic'in kendi hata listesi. 1 MiB'lık
  en kötü gövdede ~70 MB geçici bellek ve olay döngüsünde ~0,75 sn.
- **Pydantic erken durabiliyor mu** (2.14.3'te denendi): liste alanında `max_length` aşılınca tek
  `too_long` hatası döner, öğelerin hataları toplanmaz; `Annotated[list[X], FailFast()]` ilk kötü
  öğede durur. Bilinmeyen anahtar (`extra="forbid"`) için böyle bir şey yok: her anahtar bir hata.
  **Sonraki seçenek:** modelin önünde bir `before` doğrulayıcı bilinmeyen anahtarları sayıp tek
  hata verebilir; bugün gerçek gövde modeli olmadığı için yapılmadı.

### 5. Her gövdenin şemasında sınır

`tests/test_body.py`'nin gövde yürüyüşü genişledi: OpenAPI belgesindeki her istek gövdesinde,
her model bir kez, adlı alanları olan nesne bilinmeyen alanı reddeder (`additionalProperties:
false`), her liste `maxItems`, her metin `maxLength` (enum ya da sabit kendiliğinden sınırlı), her
açık nesne (`dict`) `maxProperties` taşır, hiçbir alan `Any` değildir. Sınırını unutan model suite'i
düşürür; yürüyüşün ısırdığı her eksiği bulan bir modelle sınanır.

## Sınırlar

| Sınır | Değer | Nerede | Sınırda | Test (küçük kurulmuş) |
|---|---|---|---|---|
| Bir gövde | 1 MiB | `core/body.py` `MAX_BYTES` | 400 `invalid_request`, endpoint okumadan | 1024 B |
| Tutulan gövdeler | 8 MiB | `core/body.py` `HELD_BYTES` | 503 `busy`, okumadan | iki gövdenin toplamından 1 eksik |
| Biçimlenen sorun | 6 | `core/errors.py` `PROBLEMS_SHOWN` | kalanlar `details.more`'da | 2: 20 sorundan 2'si biçimlenir |
| Health'in işçi ihtiyacı | 0 | `core/api/endpoints.py` | — | işçi sınırı 1 ve tutulu |
| Gövde şemasındaki sınırlar | her alan | `tests/test_body.py` | suite düşer | eksik sınırlı bir model |

## Maliyet

Hiçbiri Drive'a, diske ya da ağa gitmez. Doğrulama hatası: O(`PROBLEMS_SHOWN`) biçimleme ve
sorunların yerlerinden bir küme (O(sorun), sorun başına yeni metin kurmadan). Gövdenin iki sınırı
parça başına iki toplama.

## Ne bozulabilir

- **Sınırın altındaki meşru iş reddedilirse:** 1 MiB en büyük gerçek gövdenin ~3,5 katı, 8 MiB
  ~27 tanesi. `busy` bir şey yapılmadan döner; aynı anahtarla yeniden gönderilebilir.
- **`held` kaçarsa** core her gövdeyi `busy` diye reddederdi: her çıkış yolu `finally`'de bırakır,
  üçü testle.
- **Hint'in bir yeri kaybetmesi:** biçimlenmeyen sorunlar da hint'e girer (testle).
- **Kalan bedel:** bilinmeyen anahtarlarla dolu 1 MiB'lık gövde FastAPI'de ~70 MB ve ~0,75 sn
  harcar; o sürede olay döngüsü, health dahil, bekler. Sınırı gövdenin sınırı.
- **Sunucunun kendi korumaları** (h11'in 16 KB'lık baş sınırı) uygulamanın önünde, düz metinle
  cevap verir: CODE-STANDARD, Cost'a istisna olarak yazıldı.

## Testler

- `tests/api/test_health.py`: health, bütün işçiler tutulurken cevap verir.
- `tests/test_body.py`: sınırlar 1 MiB ve 8 MiB; küçük kurulunca büyük gövde reddedilir (chunked
  da), tam sınırdaki varır; tutulan gövdeler sınırdayken yenisi 503 `busy`, health 200, bırakılınca
  geçer; her çıkışta `held` 0; her gövde şeması sınırlı, eksik sınırlı model bulunur.
- `tests/test_errors.py`: 20 sorundan yalnız gösterilen 2'si biçimlenir, `more` 18; gösterilmeyen
  başlık sorunu başlıkların hint'ini korur.

## Bitti sayılır

Kabul koşulunun dört satırı: health işçiler doluyken cevap veriyor; gövde 1 MiB, hata yalnız
gösterdiğini biçimliyor ve kalanı sayıyor, liste alanlarının sınırı şema yürüyüşüyle zorunlu;
aynı anda tutulan gövdelerin sınırı var; her sınır küçük kurulmuş bir testle. Suite'ler yeşil.

## Sonraki maddeler

- **Her gövde modeli:** her liste `max_length` (roadmap'in sayısıyla: sıra 20.000, toplu 1000,
  edit'in yerleri 5000) ve `Annotated[list[X], FailFast()]`; her `dict` ve her metin `max_length`
  (prompt 4000, negatif 2000, sahne 500); `Any` yok. Şema yürüyüşü eksiğini yakalar.
- **İlk gerçek gövde modelinde (v1-10/v1-11)** kötü bir 1 MiB'lık gövdenin bedeli (bellek, olay
  döngüsündeki süre) yeniden ölçülür; bilinmeyen anahtarlar için `before` doğrulayıcı orada seçilir.
- **Yalnız belleği okuyan endpoint `async`'tir** (FOUNDATION 2).
- **v1-22:** adaptör sunucunun ve tünelin düz metin cevaplarını dört alanlı hata sanmaz.
