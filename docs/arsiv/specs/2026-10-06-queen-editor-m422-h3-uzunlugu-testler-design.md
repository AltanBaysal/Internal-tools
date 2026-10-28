# Madde 422 — H3 videosu projenin uzunluğunda, test turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 422 · v9-1b · **Tur:** 1/2 — yalnız testler.
**Üstüne kurulduğu:** [m421 test turu](2026-10-06-queen-editor-m421-h3-uzunluk-yok-testler-design.md),
[m421 uygulama turu](2026-10-06-queen-editor-m421-h3-uzunluk-yok-uygulama-design.md).
**Commit'lenmez:** çıktıyı değiştirdiği için 421'le birlikte kullanıcının VS Code'daki Changes'inde
okunur, ve onayıyla commit'lenir *(yol haritası, Dalga 5)*.

**Kullanıcıdan gereken — yok.** Madde 5 Ekim'de hizalandı; kararları yol haritasının *Maddelerin
kararları → v9-1* bölümünde, kullanıcının sözleriyle. Aşağıdaki teknik kararlar Claude'un.

## Kullanıcının sözü

*"videoları veya 4 8 12 arasında seçebilmek video uzunlupunu"*, *"h3e özel"*, *"tek seçim video
panelinde"*, *"varsalın 8 olsun"*, *"evet hatıkasnsjın"* *(5 Ekim)*. Tasarım turunda: Referanstan'dan
üretilen videolar da seçili uzunlukta *("Evet, iki sekme de")*; karenin sayfasından üretilen H3
videosu — *Yeniden üret — yeni kare*, *Tekrar dene — bu kareye* — projenin seçili uzunluğunda
*("Evet")*; kuyrukta bekleyen video eklendiği uzunlukta çıkar *("Eklendiği uzunlukta")*.

## Bugün ne oluyor

Uzunluk grafiğin içinde sabit: H3'ün iki grafiğinde Director'ın (`"2730"`) `duration`'ı 4, WAN'ın
grafiğinde `"178"` 5. Hiçbir iş bir uzunluk taşımıyor, hiçbir üretici bir uzunluk almıyor, ve
projenin bir uzunluk ayarı yok.

## Grafik uzunluğu nasıl alıyor

Okunan: `assets/workflow_video_h3_api.json`, `workflow_video_h3_first_last_api.json`, ve grafiğin
kaynağı olan `collab-toolbox/video_experiments/minimax-h3/workflow.json` (bilgi, bağımlılık değil).

- **Uzunluk Director'ın `duration`'ı — saniye, tam sayı.** Grafiğin kendi notu (*Quick Start*):
  *"Also set **duration** (s) and **frame_rate** (default 24 …)"*. Kaynak grafikte Director'ın
  `duration` çıkışı `INT`.
- **Kare sayısı diye ayrı bir düğüm yok.** Örnek (latent) Director'dan `MiniMaxH3DirectorGuide`'a
  gider ve oradan çıkar; Video Combine kare hızını Director'ın çıkışından alır. Kare sayısı
  düğümün içinde süreden ve kare hızından çıkıyor; dışarıdan izlenecek bir sayı yok.
- **Director süreyi iki yerde daha tutuyor:** kendi `builder_state`'inde ve `timeline_data`'nın
  `builder_state`'inde (`"duration": 4`). Düğümün hangisini okuduğu çalıştırmadan söylenemez —
  prompt'un dört yeri gibi —, o yüzden üçü de aynı sayıyı taşır *(üreticinin prompt için verdiği
  kararın aynısı)*.
- **FL2VA'nın açılış cümlesi uzunluğa uyar:** *"Picture 2 … aligns with the 4.00-second mark"*
  bugün Director'ın `duration`'ından okunuyor; video 12 saniyeyse cümle *12.00* der.
- **Dokunulmayanlar:** `ModelPreviewOverrideKJ`'nin `preview_frames`'i (120) örnekleme sırasındaki
  küçük önizleme, video değil. Timeline satırlarının `start` / `duration`'ı sıra numarası, saniye
  değil — FL2VA grafiğinde ikinci resim 4 saniyelik videoda `start: 1`.
- **Gönderilen grafikler 4'te kalır:** uzunluk taşımayan bir iş — 422'den önce kuyruğa girmiş her
  iş — bugünkü gibi grafiğin kendi 4'üyle çıkar; o da eklendiği uzunluk.

Grafik bu soruya açık cevap veriyor; tahmin edilen bir düğüm yok. **Bilinmeyen:** H3'ün 512×768'de
12 saniyeyi Colab'ın kartında ve `VIDEO_TIMEOUT`'un (30 dk) içinde yapıp yapamadığı — Colab'da
görülür.

## Kararlar

1. **Uzunluk projenin kendi dosyasında:** proje klasöründe `video_length.json`, `{"seconds": 8}`.
   Fotoğraf panelinin `settings.json`'ı değil: o, fotoğraf grubu gönderilince baştan yazılıyor ve
   başka bir soruya cevap veriyor; uzunluk seçildiği anda yazılır ve kuyruk onu okur
   *(CODE-STANDARD, Separation of concerns)*. Galerinin sırası gibi — ekranın yazdığı, kuyruğun
   okuduğu bir dosya —, `photo_generation` özelliğinde durur; kuyruk onu başka özellikten istemez.
2. **Kapı:** `GET /api/projects/<proje>/video-length` → `200 {"seconds": 8}` (kayıt yoksa 8);
   `PUT /api/projects/<proje>/video-length`, gövde `{"seconds": 12}` → `204`. 4, 8, 12 dışında her
   şey — 5, `"8"`, 8.5, `true`, `null`, alan yok — `400 {"error": "Video uzunluğu 4, 8 ya da 12 saniye
   olmalı."}`, ve hiçbir şey yazılmaz. Proje yoksa ikisi de `404 {"error": "Proje yok: <proje>"}`, ve
   PUT klasör açmaz. Okunamayan dosya 8 okunur. Ekran 424'te.
3. **Yalnız H3 oturumunda iş uzunluk taşır** *("h3e özel")*: H3 oturumunda kuyruğa giren her video
   işinin plan satırında `"seconds"` — o anki uzunluk. WAN oturumunda hiçbir iş taşımaz, ve WAN
   bugünkü gibi grafiğinin 5'iyle çıkar. **İki türlü okunabilen yer, ve seçilen:** her video işi
   uzunluğu taşıyıp WAN onu görmezden gelebilirdi; gelmez, çünkü o zaman bir WAN videosunun satırı 8
   der ama video 5 saniye olur, ve 423 her videonun gerçek uzunluğunu toplayacak.
4. **Dört kapı da o anki uzunluğu yazar:** *Kareden* (`queue_layer`, video), *Referanstan*
   (`queue_references`), *Yeniden üret — yeni kare* (`regenerate`, video). Ses ve fotoğraf işi
   uzunluk taşımaz.
5. **Tekrar dene, kırmızı H3 videosunu o anki uzunlukla yeniden kuyruğa koyar** *("Tekrar dene —
   bu kareye" — "Evet")*. Tekrar dene bugün planı yeniden yazmıyor; işin satırı aynen kalıyor. Artık
   uzunluk o satırdakinden farklıysa, satır yeni uzunlukla bir kez daha plana yazılır — plan yalnız
   büyür, ve kuyruk bir karenin katmanını en son satırından yapar —; aynıysa hiçbir şey yazılmaz.
   Satırın geri kalanı — prompt, tohum, mod, bağlandığı kare — aynen. **İki türlü okunabilen yer, ve
   seçilen:** kullanıcının sözü karenin sayfasındaki *Tekrar dene*'yi anıyor; galerinin karosundaki
   *Tekrar dene* aynı kapıya gidiyor, ve kuyruk panelinin *Tekrar dene*'si (hepsi birden) aynı kuralı
   izler — üç düğme tek kural.
6. **Kuyrukta bekleyen video eklendiği uzunlukta çıkar:** uzunluk işin satırında; üretim anında
   projenin ayarı okunmaz.
7. **Her üretici uzunluğu alır, kullansa da kullanmasa da** — kuyruğun tek çağrı biçimi
   (`test_producer_contract`): `generate(…, references=(), seconds=None)`. H3 kullanır; WAN,
   fotoğraf ve ses alır ve görmezden gelir. İş uzunluk taşımıyorsa `None` gider, ve H3 grafiğin
   kendi süresini bırakır.
8. **Üretilen videonun kaydı uzunluğunu söyler:** satırda `"seconds"`, işin taşıdığı — mod ve
   bittiği resim gibi. 423 export'un toplamını her videonun bu sayısından hesaplayabilir; sayı
   olmayan satır (422'den önceki her video, ve WAN'ınki) grafiğin kendi süresidir.
9. **`main.py`:** H3 oturumunda kuyruğun kapıları projenin uzunluğunu okuyan bir fonksiyon alır
   (`_video_length`), WAN oturumunda `None`. Kapı iki oturumda da asılı.

**Değişmeyen:** gönderilen grafikler; WAN'ın grafiği ve üreticisinin yaptığı; fotoğraf ve ses; H3'ün
`seconds()`'ı ve export'un toplamı (423); ekran ve `dist` (424); 421'in metni.

## Nasıl kanıtlanıyor

Kuyruk ve döngü `test_photo_usecases.py`'nin sahteleriyle; kapı ve dosya gerçek `DriveStorage`'la,
geçici klasörde, kapı elle kurularak (`test_reference_settings.py` gibi); H3 ve WAN üreticileri kendi
testlerinin sahte istemcisiyle, ve H3 gönderilen grafiklerle de; `main.py` kendi testinde. Yeni
modüller testlerin içinde içe aktarılır, toplanırken düşmesinler.

Her üreticinin uzunluğu alması için **bugünkü sahte üreticiler** (`test_photo_usecases.py`'de 19,
`test_photo_routes.py`'de 5) `seconds=None` alır; `FakeGenerator` ne aldığını `lengths` listesine
yazar — `seconds` değil, çünkü alt sınıfı `BatchGenerator` o adı bir grubun ne kadar çalıştığı için
kullanıyor. Bu değişiklik bugün de yeşil: döngü henüz uzunluk vermiyor.

## Yazılacak testler

### `backend/tests/test_video_length.py` — yeni

**Projenin ayarı ve kapısı** — geçici klasörde `düğün`, kapı elle kurulur.

1. **Kayıt yoksa 8** — GET `200 {"seconds": 8}`.
2. **Konan uzunluk geri gelir** — parametreli 4, 8, 12: PUT `204`, GET o sayı.
3. **Uzunluk projeyle kalır** — PUT 12; aynı klasörde yeni bir mağaza ve kapı GET 12; dosya projenin
   kendi klasöründe `video_length.json`; `settings.json` ve `reference_settings.json` açılmamış.
4. **4, 8, 12 dışı reddedilir** — parametreli gövde: `5`, `0`, `16`, `"8"`, `8.5`, `true`, `null`,
   alan yok: `400`, cümle birebir; GET hâlâ 8; dosya yazılmamış.
5. **Bilinmeyen proje 404** — GET ve PUT `404 {"error": "Proje yok: yok"}`; `yok` klasörü açılmamış.
6. **Okunamayan kayıt 8** — parametreli dosya: `{ yarım`, `[]`, `{"seconds": 5}`,
   `{"seconds": "12"}`, `{"seconds": true}`: GET 8.

**Kuyruğa giren iş** — `length` kuyruğa projenin uzunluğunu söyleyen fonksiyon.

7. **Kareden'in videosu projenin uzunluğunu taşır** — iki kare, iki varyant, uzunluk 12: dört video
   satırının dördü de `"seconds": 12`.
8. **Ses işi uzunluk taşımaz** — videolu kare, ses, uzunluk 12: satırda `seconds` yok.
9. **Uzunluk almayan oturumda video işi uzunluk taşımaz** — `length=None` (WAN): satırda `seconds`
   yok.
10. **Referanstan'ın kartları projenin uzunluğunu taşır** — iki varyant, uzunluk 4: kartların ikisi
    de 4.
11. **Yeniden üretilen video projenin uzunluğunu taşır** — uzunluk 8: yeni satır 8.
12. **Yeniden üretilen fotoğraf uzunluk taşımaz.**
13. **Tekrar dene kırmızı videoyu o anki uzunlukla yeniden yapar** — 4'te eklenmiş, loop, tohumu 5,
    prompt'u yazılı kırmızı bir video; uzunluk artık 12: üretici 12 alır; prompt, tohum ve loop'un
    bittiği resim (karenin kendi resmi) aynen.
14. **Uzunluk değişmediyse Tekrar dene plana bir şey yazmaz** — 8'de eklenmiş, uzunluk 8: plana
    ekleme yok, üretici 8 alır.
15. **Hepsini tekrar dene her kırmızı videoyu o anki uzunlukla yapar** — 4'te eklenmiş iki kırmızı
    video, uzunluk 12: üretici iki kez 12 alır.

**Üretim**

16. **Video işinin taşıdığı uzunlukta yapılır** — elle yazılmış satır, `"seconds": 12`: üretici 12
    alır; üretilen videonun satırı `"seconds": 12`.
17. **Uzunluk taşımayan iş grafiğin kendisiyle yapılır** — satırda uzunluk yok: üretici `None` alır;
    videonun satırında `seconds` yok. *(Bugün de yeşil: 422'den önceki işleri tutar.)*
18. **Kuyrukta bekleyen video eklendiği uzunlukta çıkar** — uzunluk 8'ken Kareden'den eklenir (işçi
    başka işte, iş bekliyor), uzunluk 12'ye çekilir, sonra kuyruk koşar: üretici 8 alır.

### `backend/tests/test_comfy_h3_video_generator.py`

Sahte Director, gönderilen grafik gibi, `builder_state`'inde `duration` taşır.

19. **H3 videosu verilen uzunlukta yapılır** — parametreli I2VA, FL2VA, REF2VA, `seconds=12`:
    Director'ın `duration`'ı, `builder_state`'inin ve `timeline_data`'nın `builder_state`'inin
    `duration`'ı 12.
20. **FL2VA'nın cümlesi videonun sonunu verilen uzunlukta söyler** — `seconds=8`:
    *"… aligns with the 8.00-second mark …"*.
21. **Uzunluk verilmeyen video grafiğin kendi süresini korur** — parametreli I2VA, FL2VA, REF2VA:
    üç yer de 4. *(Bugün de yeşil.)*
22. **Gönderilen grafiklerde her H3 videosu verilen uzunlukta** — parametreli I2VA, FL2VA, REF2VA,
    gönderilen grafikler, `seconds=8`: üç yer 8.

### `backend/tests/test_comfy_video_generator.py`

23. **WAN uzunluğu alır ve grafiğinin süresini korur** — parametreli: sonu olmayan video → `"178"`
    hâlâ 5; sonu olan → ilk-son grafiğinin `"335"`'i hâlâ 9.

### `backend/tests/test_producer_contract.py`

24. **Video yapmayan üretici de uzunluğu alır** — gerçek fotoğraf ve ses üreticisi `seconds=8` ile
    çağrılır ve cevap verir.
25. **Kuyruk gerçek üreticilere uzunluk taşıyan bir video işini verir** — üç katmanlı kare, video
    satırı `"seconds": 8`: koşu `done`, üç dosya yazılmış. *(Bugün de yeşil: döngü uzunluğu henüz
    vermiyor; değişiklikten sonra WAN'ın onu alması gerektiğini tutar.)*

### `backend/tests/test_composition_root.py`

26. **Uygulama projenin uzunluk kapısını sunar** — parametreli H3 ve WAN oturumu: GET
    `/api/projects/m422-yok/video-length` → `404 {"error": "Proje yok: m422-yok"}`.
27. **H3 oturumunda kuyruk projenin uzunluğunu okur** — `QE_DRIVE_ROOT` geçici klasörde, `düğün`
    var: `main._video_length("düğün")` 8; kapıdan PUT 12, sonra 12.
28. **WAN oturumunda kuyruk uzunluk okumaz** — `main._video_length is None`.

## Kırmızı beklenen

- 1 – 6 (parametrelilerle 19 durum): `ModuleNotFoundError` — kapının modülleri yok.
- 7 – 15 ve 18 (10 test): `TypeError` — kuyruğun kapıları `length` almıyor.
- 16: üretici `None` alıyor, 12 değil.
- 19 (3 durum), 20, 22 (3 durum): `TypeError` — H3 `seconds` almıyor.
- 23 (2 durum), 24: `TypeError` — WAN, fotoğraf ve ses `seconds` almıyor.
- 26 (2 durum): kapı asılı değil; 27, 28: `AttributeError` — `main`'in `_video_length`'i yok.
- Toplam 44 kırmızı; 17, 21, 25 yeşil. Sahtelerin imzası değişen bugünkü testler, 421'in testleri ve
  öteki her şey yeşil.

## Bilinçli olarak yapılmayan

- Ekrandaki seçim, *Kuyruğa ekle*'nin cümlesi, karenin sayfasının notları — 424; frontend ve `dist`.
- Export'un toplamı — 423. Kayıttaki `seconds`'ı galeriye ve kopyalara taşımak da 423'ün: export
  galeriden okuyor.
- Grafiklerin varsayılanını 8'e çekmek: uzunluk taşımayan iş eklendiği uzunlukta, 4'te çıkmalı.
- WAN için uzunluk: kullanıcı *"h3e özel"* dedi.
- Kapıda `field`: tek alanlı bir kapı; cümle yetiyor.
