# Madde 422 — H3 videosu projenin uzunluğunda, uygulama turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 422 · v9-1b · **Tur:** 2/2 — kod.
**Üstüne kurulduğu:** [m422 test turu](2026-10-06-queen-editor-m422-h3-uzunlugu-testler-design.md) —
kararlar, kapının biçimi ve grafiğin uzunluğu nasıl aldığı orada.
**Commit'lenmez:** 421'le birlikte kullanıcının Changes'inde okunur, ve onayıyla commit'lenir.

## Yaklaşımlar

- **Seçilen — uzunluk işin satırında, üretici onu alır.** Kuyruğa giren H3 videosu o anki uzunluğu
  plan satırında taşır, döngü onu üreticiye verir, H3 Director'a yazar. Kuyrukta bekleyen işin
  uzunluğu değişmez, çünkü üretim anında projenin ayarı hiç okunmaz.
- **Elenen — üretim anında projenin ayarını okumak:** daha az satır, ama bekleyen video
  eklendiği uzunlukta değil, o anki uzunlukta çıkar; kullanıcı tersini istedi.
- **Elenen — uzunluğu yalnız üreticiye uzunluk taşıyan işte vermek:** sahte üreticilere dokunmazdı,
  ama kuyruğun tek çağrı biçimini ikiye bölerdi (`test_producer_contract`).

## Birimler

### Yeni — `photo_generation` özelliğinde

- **`domain/video_length.py`** — kural, dışarıdan hiçbir şey içe aktarmaz (yalnız `layers` ve
  `queue`):
  - `LENGTHS = (4, 8, 12)`, `DEFAULT = 8`;
  - `InvalidLength` ve `check(seconds)` — 4, 8, 12 dışındaki her şeyi (tam sayı olmayanı ve `bool`'u
    da) *"Video uzunluğu 4, 8 ya da 12 saniye olmalı."* ile reddeder;
  - `carried(length, project)` — kuyruğa giren video işinin taşıdığı: `{"seconds": length(project)}`,
    `length` `None` ise `{}`;
  - `at_length_now(plan_store, project, fids, length)` — kırmızı videoları o anki uzunlukla
    yeniden kuyruğa koyan satırlar: her karenin en son video satırı, `seconds`'ı yeni uzunlukla,
    bir kez plana eklenir; zaten o uzunluktaysa eklenmez; `length` `None` ya da `fids` boşsa hiçbir
    şey yapmaz. İki Tekrar dene de kullanır, o yüzden kuralın yanında.
- **`data/video_length_store.py`** — `DriveVideoLengthStore(storage)`: `project_exists`, `read`
  (tam sayı ya da `None`; okunamayan, `bool` ya da sayı olmayan her şey `None`), `write`
  (`{"seconds": n}`). Dosya `video_length.json`.
- **`domain/usecases/video_length.py`** — `get_video_length(lengths, project)` (proje yoksa
  `ProjectMissing`; kayıtlı değer `LENGTHS`'te değilse 8) ve `save_video_length(lengths, project,
  seconds)` (önce değer — ucuz ret önce —, sonra proje, sonra yazar).
- **`presentation/video_length_routes.py`** — `make_video_length_blueprint(get_video_length,
  save_video_length)`: GET `{"seconds": n}`; PUT `204`; `InvalidLength` → `400`, `ProjectMissing` →
  `404`, ikisinde de `{"error": cümle}`. Kendi blueprint'i, Referanstan'ın kaydı gibi: kartların
  fabrikası ve onu kuran testler değişmez.
- **`domain/ports.py`** — `VideoLengthStore` protokolü; `PhotoGenerator.generate`'e `seconds`.

### Değişen

- **`queue_layer`** — `length=None`; video işinde her satıra `carried(length, project)` — bir basışta
  bir kez sorulur.
- **`queue_references`** — `length=None`; her karta `carried(length, project)`.
- **`regenerate`** — `length=None`; video işinin satırına `carried(length, project)`.
- **`retry_frame`, `retry_failed`** — `length=None`; kırmızı videolar için `at_length_now`, kırmızı
  satırlar kuyruğa geri yazılmadan **önce**: zaten koşan bir döngü işi eski uzunlukla almasın.
- **`run_loop`** — `producer.generate(…, seconds=current.get("seconds"))`; `_made_with` işin
  uzunluğunu üretilen satıra `seconds` olarak yazar, iş taşımıyorsa yazmaz.
- **`ComfyH3VideoGenerator`** — `generate(…, seconds=None)`: uzunluk verildiyse Director'ın
  `duration`'ı o olur — I2VA, FL2VA ve REF2VA'da, FL2VA'nın cümlesi okunmadan önce —; `_render`
  `duration`'ı iki `builder_state`'e de yazar, prompt gibi. Verilmediyse grafiğin kendi 4'ü durur ve
  üç yer yine aynı. Modül belgesi ve `seconds()`'ın belgesi doğru olanı söyler.
- **`ComfyVideoGenerator`, `ComfyPhotoGenerator`, `MMAudioGenerator`** — `seconds=None` alır ve
  görmezden gelir; belgeleri neden olduğunu söyler.
- **`main.py`** — `_video_lengths = DriveVideoLengthStore(_storage)`; `_video_length` H3
  oturumunda `partial(get_video_length, _video_lengths)`, WAN'da `None`; kuyruğun beş kapısına
  `length=_video_length`; kapının blueprint'i `create_app`'in listesinde.

## Bilinen sonuçlar

- **Tekrar dene yeni uzunlukla satır eklerse**, kuyruğun sayıları (`queue.counts` — plan satırı
  sayar) o videoyu bir fazla sayar: kuyruk panelinin *"… kare üretildi"*si. Plan zaten böyle
  çoğalıyor — kuyruktan çıkarılıp yeniden istenen katman da satır ekliyor *(madde 211)* —, ve
  sayılar bu maddenin konusu değil. Uzunluk değişmediyse satır eklenmez, sayılar bugünkü gibi.
- **H3 oturumunda eklenip WAN oturumunda üretilen video** WAN'ın 5 saniyesiyle çıkar, ama satırı
  işin uzunluğunu söyler. Bir oturum tek video modeli kurar *(madde 243)*; bekleyen işler model
  değişen bir oturuma taşınırsa olur. 423 bunu bilir.
- **Export'un toplamı** 423'e kadar her videoyu grafiğin süresiyle sayar; `export_summary.py`'nin
  belgesi *"uzunluk seçilemiyor"* diyor — o dosya 423'ün.

## 423 ve 424 için

- **424 — kapı:** `GET /api/projects/<proje>/video-length` → `{"seconds": 8}`;
  `PUT …/video-length` gövde `{"seconds": 12}` → `204`; ret `400 {"error": "Video uzunluğu 4, 8 ya
  da 12 saniye olmalı."}`; proje yoksa `404 {"error": "Proje yok: <proje>"}`.
- **423 — her videonun uzunluğu:** üretilen videonun kayıt satırında `"seconds"`. Satırda yoksa
  (422'den önceki her video ve WAN'ınki) uzunluk grafiğin `seconds()`'ı. 423 bunu kaydın katlanışına
  (`slots`), galeriye ve kopyaların taşıdıklarına (`copy_frame.CARRIED`) ekler.

## Doğrulama

Dört satır. Test turunun 44 kırmızısı yeşile döner; öteki her şey yeşil kalır.
