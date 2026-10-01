# Madde 411 — Varyantlar tek işte, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Parça:** 411 · v8-8 · **Tur:** 1/2 — yalnız testler.

**Kullanıcıdan gereken — yok.** Madde 1 Ekim'de hizalandı; beş kararın beşi de Claude'un önerisi
*(kullanıcı — "oanylıuorum yapabilirsin maddlerde okeyim")*. Teknik kararlar Claude'un; ölçüm
kullanıcının son testinde. **Çıktıyı değiştirdiği için hiçbir şey commit'lenmez** *(madde 411)*:
testler, kod, spec'ler ve planlar çalışma ağacında kalır, kullanıcı VS Code'un Changes'inde okur.

## Bugün ne oluyor

`plan_frames` *([start_batch.py](../../../queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py))*
bir prompt'un her varyantını ayrı bir iş olarak planlıyor — `P{n}_{v}`, aynı prompt, negatif, model ve
LoRA, her birine kendi `new_seed()`'i. Döngü *([run_loop.py](../../../queen-editor/backend/features/photo_generation/domain/run_loop.py))*
her turda kuyruğun başındaki tek işi alıp `producer.generate(...)` ile ComfyUI'ye tek bir grafik
gönderiyor; dosya yazılınca satırını ekliyor. `ComfyClient.fetch_output` tam bir çıktı bekliyor —
fazlası "grafikte Batch Size 1 mi?" hatası.

## Araştırmadan, üstüne kurulanlar

- **Batch'in gürültüsü tek seed'den:** `prepare_noise` seed'le tek bir `torch.manual_seed(seed)`
  üreteci kurup bütün batch'in gürültüsünü o üreteçten bir seferde çekiyor
  *([comfy/sample.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy/sample.py))*.
  Kayıtlı seed bir varyantı tek başına yeniden üretmez — madde 411'in (1). kararı, kabul.
- **Grafiğin her node'u batch'i taşıyor; yapısı değişmiyor.** `EmptyLatentImage` `batch_size`'ı
  `"23"` *Batch Size* node'undan okuyor *([nodes.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/nodes.py))*.
  `FaceDetailerPipe` batch'teki resimleri tek tek, `seed + i` ile işleyip birleştiriyor
  *([impact_pack.py](https://raw.githubusercontent.com/ltdrdata/ComfyUI-Impact-Pack/Main/modules/impact/impact_pack.py))*.
  `SaveImage` her resim için bir dosya yazıp sonuçları batch sırasıyla, `type: "output"` olarak
  döndürüyor. `Image Comparer (rgthree)` `PreviewImage`'dan türüyor: `a_images` / `b_images`,
  `type: "temp"` *([image_comparer.py](https://raw.githubusercontent.com/rgthree/rgthree-comfy/main/py/image_comparer.py))*
  — bugünkü süzgeç onları zaten saymıyor. `Seed (rgthree)` tek bir sayı döndürüyor
  *([seed.py](https://raw.githubusercontent.com/rgthree/rgthree-comfy/main/py/seed.py))*.
- **Kartın belleğini ComfyUI söylüyor:** `GET /system_stats` → `devices[0].vram_total`, bayt
  *([server.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/server.py))*. Defter
  değişmez.
- **Eşik ComfyUI'nin kendi bellek kuralından** — sayılar uygulama turunun spec'inde, kaynaklarıyla.
  Sonucu: Colab'ın T4'ü (14,74 GiB) bu grafiğin **7** varyantını tek batch'te tutuyor, 8'ini değil;
  A100 40 GB (39,56 GiB) panelin izin verdiği 26'nın hepsini. **4 varyantlı bir prompt iki kartta da
  batch'le üretilir.**

## Kurallar

1. **Bir prompt'un varyantları tek işte üretilir:** kuyruğun başındaki fotoğraf işi, ve hemen
   arkasında duran, aynı prompt numarasından, aynı prompt, negatif, model ve LoRA'yla ve **hiç sırası
   gelmemiş** varyantlar — üretici bunu yapabiliyorsa ve kart tutuyorsa. ComfyUI'ye tek grafik gider;
   seed baştaki varyantın planlı seed'i.
2. **Her varyant kendi adıyla, kendi resmiyle iner** — `P{n}_{v}.png`, batch'in sırasıyla. **Her
   satır, kendi dosyası yazıldıktan sonra** eklenir *(CODE-STANDARD, Separation of concerns)*.
3. **Her satırın seed'i batch'in seed'i;** `renderSeconds` batch'in süresinin varyant sayısına bölümü.
4. **Tek varyantlı prompt bugünkü gibi:** `generate`, ve kart hiç sorulmaz.
5. **Kart prompt'un varyantlarını tutmuyorsa hepsi tek tek, bugünkü gibi** — kendi seed'leriyle.
   Kart, **prompt'un istendiği varyant sayısıyla** sorulur (plandaki aynı prompt'un varyantları), ve
   her turda aynı cevabı verir: tutmayan bir prompt "kalanı sığana dek tek tek, sonra batch" olmaz.
6. **Batch hata verirse bütünüyle yeniden denenir** — aynı varyantlarla, üç kez. Üçüncüde de
   karenin hatasıysa varyantların hepsi kırmızı, aynı sebeple.
7. **Durdurulursa yarıdaki batch'in tamamı gider:** hiçbir dosya, hiçbir satır; devam edince batch
   bütünüyle yeniden üretilir.
8. **Tekrar dene ile geri gönderilen kare tek başına üretilir** — tek tek de, *Tümünü tekrar dene*
   ile hep birlikte de; kendi planlı seed'iyle. **Yeniden üret** ile doğan kare de tek başına.
9. **Galeride başka yere sürüklenen varyant durduğu yerde, tek başına üretilir.**
10. **Yalnız fotoğraf:** aynı prompt'tan doğmuş video işleri, üreticisi batch yapabilse de tek tek.
11. **Durum, batch'in her karesini adlandırır:** `current` baştaki iş, `batch` onunla birlikte
    üretilen öteki karelerin kimlikleri; `startedAt` ile birlikte söylenir, turun ilk raporu
    `batch`'i `None` yapar. `pending` batch'tekileri saymaz.
12. **Zaman satırı batch'in dosyalarını birlikte adlandırır:** `⏱ P0_0.png, P0_1.png · render … sn ·
    drive … sn`.
13. **ComfyUI'nin istemcisi** (`services/comfy/`): `fetch_outputs(entry, count, extensions=None)`
    çıktıların hepsini sırasıyla indirir, sayı tutmazsa gelenleri yazarak durur; `fetch_output` aynen
    kalır. `vram_total()` `/system_stats`'ın ilk cihazının `vram_total`'ını verir.
14. **Fotoğraf üreticisi** (`data/`): `generate_batch(prompt, negative, seed, count, model, lora)`
    sayıyı `"23"` *Batch Size* node'una yazar, gerisi `generate`'le aynı; `count` resim döndürür.
    `generate` `"23"`'e dokunmaz. `fits_batch(count)` kartı ComfyUI'ye sorar.
15. **Ekran:** galeride batch'in her kutucuğu *foto üretiliyor* ve canlı süreyi gösterir, seçilemez;
    karenin sayfasında batch'teki karenin *Üretim süresi* canlı ilerler; kuyruk sayacı batch'tekileri
    bekleyen saymaz. Bitince her karenin süresi kendi satırından — batch'in süresinin payı.
16. **Hiçbir test gerçek bir ComfyUI'ye, GPU'ya, Drive'a ya da saate dokunmaz.**

**Değişmeyen:** `assets/workflow_*.json`, ComfyUI'nin kurulumu ve başlatılması, defter, video ve ses
işleri, referans havuzu, `fetch_output`'un sözleşmesi, tek varyantlı prompt, bir karenin Tekrar
dene'si ve Yeniden üret'i.

## Nasıl kanıtlanıyor

Döngü sahte üreticilerle koşar. **Batch yapabilen sahte**, `FakeGenerator`'ın üstüne
`fits_batch(count)` (kaç varyant tuttuğu verilir, sorulan sayılar not edilir) ve
`generate_batch(...)` (çağrıyı not eder, `count` ayrı resim döner, istenirse karenin hatasını atar ya
da durdurmayı ister) taşır. **Bugünkü sahteler batch yapamaz** — öteki bütün testler bugünkü yoldan
geçer. İstemci ve üretici testleri bugünkü sahte HTTP'yi ve sahte istemciyi kullanır; sözleşme testi
gerçek üreticiyi gönderilen grafikle koşturur.

## Yazılacak testler

### `backend/tests/test_variant_batch.py` — yeni; sahteler `test_photo_usecases`'ten

1. **Varyantlar üreticiye tek batch olarak gider** — iki prompt × iki varyant, seed'ler 11, 22, 33,
   44: `batches == [("a", "neg", 11, 2, "", ""), ("b", "neg", 33, 2, "", "")]`, tek `generate` yok.
2. **Her varyant kendi adıyla, kendi resmiyle iner** — `saved` `P0_0.png`, `P0_1.png`, … batch'in
   sırasıyla, her biri kendi baytlarıyla.
3. **Her satır kendi dosyasından sonra** — dosyalar ve satırlar tek günlükte: kaydet P0_0, satır P0_0,
   kaydet P0_1, satır P0_1.
4. **Her satır batch'in seed'ini taşır** — dört satırın seed'i 11, 11, 33, 33.
5. **Her satırın süresi batch'in süresinin payı** — sahte saat; 80 saniyelik dört varyantlı batch:
   her satırda `renderSeconds == 20.0`.
6. **Tek varyantlı prompt bugünkü gibi** — `variants=1`: tek `generate`, batch yok, kart sorulmadı.
7. **Kart tutmuyorsa tek tek** — tuttuğu 1: dört `generate`, kendi seed'leriyle; batch yok.
8. **Kart prompt'un hepsini tutmuyorsa kalanı da batch'lenmez** — üç varyant, kart ikisini tutuyor:
   üç `generate`, batch yok; kart hep `3` ile soruldu.
9. **Batch hata verirse bütünüyle yeniden denenir, sonra hepsi kırmızı** — "a" patlıyor: "a"'nın
   batch'i üç kez, her seferinde iki varyantla; `P0_0` ve `P0_1` kırmızı, sebep `… — 3 kez denendi`;
   "b"'nin batch'i iniyor.
10. **Durdurulan batch'ten hiçbir şey kalmaz, devam edince bütünü üretilir** — batch durdurmayı isteyip
    düşüyor: durum `paused`, kaydedilen yok, satır yok; `resume_batch` ile ikisi de tek batch'te iner.
11. **Tekrar dene ile geri gelen kare tek başına** — iki varyant kırmızı; `retry_frame("P0_1")`: tek
    `generate`, P0_1'in planlı seed'i 22; batch yok.
12. **Tümünü tekrar dene ile geri gelenler de tek tek** — `retry_failed`: iki `generate`, 11 ve 22.
13. **Yeniden üretilen kare tek başına** — `regenerate` aynı sözlerle: tek `generate`, batch yok.
14. **Sürüklenen varyant durduğu yerde, tek başına** — sıra P0_0, P1_0, P1_1, P0_1: `generate` P0_0,
    batch P1 (2), `generate` P0_1.
15. **Video işleri batch'lenmez** — aynı prompt'tan iki video işi, üreticisi batch yapabilse de: iki
    `generate`, batch yok, kart sorulmadı.
16. **Durum batch'in karelerini adlandırır** — batch üretilirken: `current.id == "P0_0"`,
    `batch == ["P0_1", "P0_2"]`, `startedAt` dolu, `pending` yalnız P1'in kareleri; turun ilk raporunda
    `batch is None`.
17. **Zaman satırı batch'in dosyalarını birlikte adlandırır** — `⏱ P0_0.png, P0_1.png · render 80.0 sn
    · drive 0.0 sn`.

### `backend/tests/test_comfy_client.py`

18. **`fetch_outputs` her çıktıyı sırasıyla indirir** — üç `output`, bir `temp`: üç `/view`, baytlar
    sırasıyla.
19. **`fetch_outputs` sayı tutmazsa durur** — iki çıktı, üç istendi: `RuntimeError`, metninde
    `3 çıktı bekleniyordu, 2 geldi` ve gelen dosyanın adı.
20. **`vram_total` `/system_stats`'ın ilk cihazını okur** — adres `http://comfy:8188/system_stats`,
    dönen `vram_total`.
21. **`vram_total` ulaşılamayan sunucuyu adlandırır** — `ComfyUnreachable`, ilk satırında adres.

### `backend/tests/test_comfy_photo_generator.py`

`FakeClient` `fetch_outputs(history, count)` ve `vram_total()` kazanır; varsayılan grafiğe `"23"`
*Batch Size* node'u eklenir.

22. **`generate_batch` sayıyı Batch Size node'una yazar, `count` resim döner** — prompt, negatif,
    seed `generate`'teki gibi yazılır; bekleme sınırı resim başına, `count` katı. *(Uygulama turunda
    düzeltildi: ilk hâli tek fotoğrafın sınırını bekliyordu — sebep uygulama spec'inde.)*
23. **`generate` Batch Size'a dokunmaz** — tek resimde `"23"` grafiğin kendi değerinde, 1.
24. **`generate_batch` diskteki grafiği değiştirmez.**
25. **Batch Size node'u olmayan grafik hangi node'un eksik olduğunu söyler** — metninde `23`.
26. **`fits_batch` kartı ComfyUI'nin kuralıyla tartar** — parametreli: T4 (14,74 GiB) 4 ve 7 evet, 8
    hayır; A100 40 GB (39,56 GiB) 26 evet; 8 GiB'lik kart 2 hayır.

### `backend/tests/test_producer_contract.py`

27. **Bir prompt'un varyantları gerçek fotoğraf üreticisinden tek batch'le geçer** — gönderilen grafikle:
    tek `submit`, `"23"`'ün değeri 2, ve grafikte `EmptyLatentImage`'ın `batch_size`'ı `"23"`'ten;
    `P0_0.png` ve `P0_1.png` iner.

### Ekran — `frontend/src/features/photo_generation/`

28. **`useGeneration`, batch'teki kareleri adlandırır** — `batch` `["P0_1", "P0_2"]`; başka projenin
    koşusunda `[]`.
29. **`useGeneration`, batch'tekileri bekleyen saymaz** — dört bekleyen kare, biri `current`, ikisi
    `batch`te: fotoğraf kuyruğu 1.
30. **`Gallery`, batch'in her kutucuğu canlı süreyle üretiliyor der** — `foto üretiliyor0:46`, üçünde
    de.
31. **`Gallery`, batch'teki kutucuk seçilemez** — seçim halkası yok.
32. **`PhotoDetail`, batch'teki karenin süresi canlı ilerler** — `0:46`, vurgu renginde.
33. **`ProjectScreen`, galeriye batch'i verir** — `P0_1`'in kutucuğunda `0:46`.

## Kırmızı beklenen

- `test_variant_batch.py`: 1, 2, 4, 5, 8, 9, 10, 14, 16, 17 kırmızı — döngü `fits_batch`'i hiç
  sormuyor. 3, 6, 7, 11, 12, 13, 15 **yeşil**: bugünkü yoldan zaten geçiyorlar; bugünü kilitliyorlar,
  değişiklik onları bozmasın diye.
- `test_comfy_client.py` 18–21: `AttributeError` — `fetch_outputs` ve `vram_total` yok.
- `test_comfy_photo_generator.py` 22, 24, 25, 26: `AttributeError`; 23 yeşil.
- `test_producer_contract.py` 27: iki ayrı `submit`.
- Ekran 28–33: `batch` yok — kırmızı; 29 bugün 2 sayıyor.
- Öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Sığmayan batch parçalara bölünmez — karar (4) "tek tek, bugünkü gibi".
- Kartın cevabı saklanmaz: her batch'te `/system_stats` bir kez sorulur, yerel bir istek.
- Satıra batch'in büyüklüğü ya da sırası yazılmaz: kimse okumuyor.
- `workflow_api.json`'a, deftere, `dist`'e ve yol haritasına dokunulmaz.
