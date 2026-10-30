# Madde 520 · Seçilen bir kare yalnız kendisi sayılır — tasarım

**Tarih:** 30 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-19),
520 · v11-19 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-30-queen-editor-m520-secim-yalniz-kendisi-plan.md](../plans/2026-10-30-queen-editor-m520-secim-yalniz-kendisi-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Video panelinde "Seçili kareler" ile gönderilen bir seçim yalnız seçilen karelere iş ekliyor; aynı
fotoğrafı paylaşan kopyalar seçilmedikçe girmiyor. Kopyala'dan sonra seçim, v4'teki gibi kopyaya geçiyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*; BACKLOG'un işi (513'ün QA'sı): *"Kopyala'dan sonra galerinin
seçimi kopyanın üstüne geçiyor"*. 509–519'a dokunulmaz.

**Kullanıcının kararı** *(30 Ekim — Kopyala'dan sonra seçim seçilen karede mi kalsın, kopyaya mı geçsin
sorusuna: "2")*: seçim kopyaya geçmeye devam eder. Maddenin ilk kabul koşulu (*"seçim o karede kalıyor"*)
bununla değişti; BACKLOG'un işi bir hata değil, v4'ün kararı olduğu için silinir.

## Bugün

BACKLOG seçimin dosya adına bağlı olduğunu tahmin ediyordu. Kod öyle değil: galerinin seçimi zaten karenin
kimliğiyle tutuluyor (`Gallery`'nin `selected`'ı kimlik listesi), ve seçim çubuğunun sunucuya gönderdiği
her şey kimlik. Kırmızı testler iki şey gösterdi:

- **Seçim kopyaya bilerek taşınıyor.** `Gallery.handleCopy` Kopyala'nın cevabındaki ikizlerin kimliklerini
  seçim yapıyor. Bu v4 yol haritasının 11. maddesinin kararı — *"seçim kopyaya geçer"* (Fark 77): kopyanın
  ayrı bir bildirimi yok, fark edilmesi seçimin ona geçmesiyle. QA'nın gördüğü bu: kare seçildi, Kopyala,
  seçim ikizde, "Videoları sil" ikizin videosunu sildi. Kullanıcı bu davranışı istiyor (yukarıda); değişmez.
- **Video panelinin "Seçili kareler"i dosya adı gönderiyor.** `LayerPanel` seçimi kimlikle eşliyor ama
  isteğe `frame.file` koyuyor; sunucuda `queue_layer.frames_in_scope` kareyi dosya adıyla seçiyor. Kopyala
  ikizi ve varyant kopyası kaynağının resmini, dolayısıyla dosya adını paylaştığı için (madde 102), bir
  karenin seçimi o resmi gösteren her kareyi kapsıyor. Sunucunun yeni testi: `0_a` ve ikizi `C1_0_a`,
  seçim `0_a`'nın dosyası → 1 değil 2 iş (kırmızı). Ekran "1 video üretilecek" der, sıra 2 iş alır.

Kapılara tek tek bakıldı. Kimlik alanlar: kare silme (`removeFrames`), Kopyala (`copyFrames`), katman silme
(`removeLayer`), kuyruktan çıkarma (`dequeueLayer`), yeniden üretme (`regenerateFrame`), Tekrar dene
(`retryFrame`), sıra (`saveOrder`), ses kapama (`saveMuted`). Dosya adı alan tek kapı katman ekleme:
`POST …/layers/<kind>` ve onun `files`'ı.

## Ne yapılır

### Katman ekleme kareleri kimlikle alır

`POST /api/projects/<project>/layers/<kind>` gövdesinde `files` yerine `frames`: seçilen karelerin
kimlikleri, öteki kapıların aldığı gibi. Anahtar yoksa bugünkü gibi "katmanı olmayan her kare".

- **`queue_layer`:** parametre `files` → `frames`. Doğrulaması öteki kapılarınki: `frame_list.checked`,
  cümlesi *"Katman eklenecek kare listesi metin dizisi olmalı."*; route `InvalidFrames`'i 400 ile, `field`
  olmadan döner (öteki kapılar gibi; ekranda `files` alanını işaretleyen bir kutu yok). `InvalidScope`
  kalkar.
- **`frames_in_scope`:** satırı `frame["id"]` ile seçer. Kapsamın kendi kuralları — oturmuş kart ve açan
  katman (519), altındaki katman (`layers.NEEDS`), seçimin katmanı olan kareyi de kapsaması (madde 25) —
  değişmez.
- **Ekran:** `LayerPanel` `inSelection`'ın kimliklerini gönderir; `api.queueLayer` gövdeye `{frames}`
  koyar; `useGeneration.queueLayer` parametresinin adı `frames`.

**Bir karenin seçimi ne demek:** yalnız o kare. Resmini paylaşan ikiz ya da varyant kopyası seçilmedikçe
kapsamda değil. Dosya adıyla seçen başka kapı kalmadı.

**Eski çağıranlar:** bu kapıyı yalnız ekran çağırıyor; ajanın araçlarında katman ekleme yok. Eski bir
sekme de yeni sunucuya ulaşamaz: her sunucu başlatışı cloudflared'i öldürüp yeni bir Quick Tunnel açıyor
(`colab/server.py`, `serve`), adres değişiyor. `dist` aynı değişiklikte yeniden derleniyor. Bu yüzden
`files` okunmaya devam etmez. Ama yok sayılmaz da: yok sayılan `files` "seçim yok" demek olur ve katman
katmanı olmayan her kareye asılırdı — en geniş kapsam, birkaç kare kastedilen bir basıştan (reviewer;
516'nın bayrağıyla aynı desen). Route `files` taşıyan gövdeyi 400 ile reddeder: *"Kareler frames ile
gönderilmeli."*; plana hiçbir şey yazılmaz.

### Kopyala değişmez

`Gallery.handleCopy` seçimi ikizlere taşımaya devam eder; `copyPhotos` ikizlerin kimliklerini döndürür.
Kopyala'dan sonraki basışlar ikizlere gider — kullanıcının istediği bu.

## Maliyet

Proje, sohbet ve dosya sayısından bağımsız; her basış bir istek.

| İş | Ne yapar |
|---|---|
| Kuyruğa ekle, "Seçili kareler" | değişmez: bir `POST …/layers/video`; plan kilidinde galeri bir kez okunur, kapsam satır başına bir küme bakışı (eskiden dosya adıyla, şimdi kimlikle). Bir karenin seçimi artık ikizine iş yazmaz: daha az plan satırı, daha az kopya. |
| Kopyala, Videoları sil, Sil | değişmez. |

## Ne kaybolabilir, ne bozulabilir

- **Hiçbir şey daha fazla yazılmaz ya da silinmez.** Değişen yalnız katman eklemenin kapsamı; daralır.
- **Kuyruğa ekle seçilmeyen kareye iş yazmaz.** Eskiden bir karenin seçimi resmini paylaşan her kareye iş ve
  kopya yazıyordu; ekranın tahmini (`inSelection`) bunu saymıyordu. Artık tahmin ile sıranın aldığı aynı.
- **Geçersiz gövde:** `frames` liste değilse ya da metin olmayan bir öğe taşıyorsa, ya da gövde eski
  `files` anahtarını taşıyorsa, basış kilide girmeden 400 ile reddedilir; plana hiçbir şey yazılmaz.

## Sınırlar

- Kopyala'dan sonra seçimin kopyaya geçmesi kullanıcının kararıyla kalıyor; kaynağa dönmek için ona
  basmak gerekir.

## Ne zaman bitti

- **Sunucu:**
  - `0_a` ve Kopyala ikizi `C1_0_a`; `frames=["0_a"]` ile video basışı tek iş yazar, `0_a`'ya (bugün
    kırmızı: dosya adıyla 2 iş);
  - route `{"frames": ["P0_0"]}` ile yalnız `P0_0`'a video planlar; `{"frames": "P0_0"}` 400 ve
    *"Katman eklenecek kare listesi metin dizisi olmalı."*, plana video yazılmaz;
  - `{"files": ["P0_0.png"]}` 400 ve *"Kareler frames ile gönderilmeli."*, plana video yazılmaz (bugün
    kırmızı: 202, her kareye video);
  - `queue_layer`'ı ve `frames_in_scope`'u seçimle çağıran bütün eski testler kimlikle geçer
    (`test_photo_usecases.py`, `test_made_once.py`, `test_plan_hold.py`); 512, 513, 516, 519'un testleri
    değişmeden geçer.
- **Ekran:**
  - video paneli, ikizi olan bir karenin seçimiyle `onQueue(["0_a"], 1, "loop")` (bugün kırmızı: dosya
    adı); bağlantı kırılınca düşen modun testi kimliklerle;
  - `queueLayer` gövdesi `{frames, variants, mode}`;
  - galerinin "moves the selection onto the twins" testi değişmeden geçer.
- `dist` yeniden derlendi; iki queen-editor takımı yeşil
  (`test_notebook_clones_its_branch.py`'nin iki testi kullanıcının Colab denemesi için kasten kırmızı).

## Aynı değişiklikte

BACKLOG'dan *"Kopyala'dan sonra galerinin seçimi kopyanın üstüne geçiyor"* silinir: davranış v4'ün kararı ve
kullanıcı onu tuttu. `frame_list`'in docstring'i kimlik listesini alan kapıları sayıyordu (üç); katman
ekleme ve kuyruktan çıkarma da eklendi.
