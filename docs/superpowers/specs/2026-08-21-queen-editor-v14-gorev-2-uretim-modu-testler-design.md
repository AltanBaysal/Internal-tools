# v14 · Görev 2 — Kuyruk işinin üretim modunu taşıması · **test turu**

**Kaynak:** [Yol haritası v14, 2. madde](../plans/2026-08-20-queen-editor-v14-roadmap.md) ·
[1. maddenin uygulama turu](2026-08-21-queen-editor-v14-gorev-1-bitis-karesi-uygulama-design.md)

Bu tur yalnız testleri yazar. Takım kırmızı biter ve kırmızı commit edilir; kodu ikinci tur yazar.

## Bu turun sınırı

**İçeride:** üç modun adı, kuyruğa modla iş eklenmesi, bağlı modda hedef karenin kuyruğa girerken
çözülmesi, plan dosyasının modu kaybetmemesi, ve motorun modu okuyup bitiş karesini seçmesi.

**Dışarıda:** ekranın tamamı. Panelde mod seçicisi 4., ardışıklık kuralı 5., cümleler 6. maddede;
uç noktanın `mode` anahtarını okuması da 4. maddenin işi. Bu turdan sonra kuyruk modu **taşıyabilir**
olacak, ama ona mod veren tek şey testler olacak.

1. madde motorun bitiş karesi **alabilmesini** getirdi. Bu madde ona bitiş karesini **verecek**
olanı getiriyor.

## Kararlar

**1. Üç modun adı domain'de, tek dosyada.** `domain/production_mode.py`: `STANDARD`, `LOOP`,
`LINKED`, hepsini sayan `ALL`, ve bir işin modunu okuyan `of(job)`. Ekrandaki Türkçe adları bu
dosyanın işi değil — kimlik ile etiket ayrı şeyler, ve etiketi okuyan yalnız ön yüz.

**2. Modu tanımayan iş standarttır.** `of`, `mode` anahtarı olmayan ya da tanımadığı bir değer
taşıyan işe `standard` der. Modlar doğmadan önce planlanmış her video işi bugün nasıl üretiliyorsa
öyle üretilmeye devam ediyor; bu bir "hoşgörü" değil, tek doğru cevap.

**3. Mod kuyruğa girerken yazılıyor, üretilirken değil.** `queue_layer` bir `mode` alıyor ve video
işinin plan satırına yazıyor. Bağlı modda **hedef kare de** o an çözülüp `linkedTo` olarak yazılıyor.
Sebebi: kuyruk saatlerce akıyor ve kullanıcı bu sırada galeriyi sürükleyebiliyor. Render anında
okunan bir "sonraki kare", kullanıcının butona bastığında baktığı kare olmazdı.

**4. "Sonraki kare" galerinin kendi sırası.** `list_frames`'in döndürdüğü dizide `index + 1`.
İkinci bir tanım yazılmıyor: detay sayfasının ileri oku bugün bunu böyle okuyor
(`PhotoDetail.jsx`'te `frames[index + 1]`), ve okun bir kuralı, videonun başka bir kuralı olsa video
kullanıcının hiç gitmediği yere giderdi.

**5. Sonrası olmayan kare kuyruğa hiç girmiyor — ama koşuyu durdurmuyor.** Galerinin son karesinin
bağlanacağı bir şey yok. O kare batch'in dışında kalıyor, kalanlar giriyor. Kapsamdaki her kare bu
yüzden düşerse cevap 0 — boş kapsam neyse o, çünkü ikisi de "borç yok, koşu başlamadı" demek.

**6. Mod video işinin dışına çıkmıyor.** Ses işine standart dışı bir mod verilmesi `InvalidMode`.
Sessizce yok saymak, çağıranın hatasını iyi çıkmış bir sesin arkasına saklamak olurdu. Ses işinin
plan satırında `mode` anahtarı **hiç doğmuyor** — taşımadığı bir kavramı boş değerle taşımıyor.

**7. Motor modu okuyor, bitiş karesini o seçiyor.** `run_loop`:
- standart → bitiş karesi yok, üreticiye `end=None`;
- loop → karenin **kendi** fotoğrafı, yani `source` ile aynı dosya;
- bağlı → `linkedTo` karesinin fotoğrafı.

Üretici hâlâ modu bilmiyor; ona yalnız bir resim gidiyor ya da gitmiyor (1. maddenin kararı).

**8. Bağlı modda hedefin fotoğrafı yoksa o kare kırmızıya döner, koşu sürer.** Yeni bir
`MissingEndFrame`, `frame_level = True` taşıyor — yani `policy.is_frame_fault`'un tanıdığı şekil. Bu
karenin karosu kızarır, kuyruk devam eder. Sessizce standart üretime düşmek, kullanıcının istediği
şeyden başka bir şeyi istediği şey diye teslim etmek olurdu.

**9. Plan dosyası tanımadığı anahtarları kaybetmiyor.** `DrivePlanStore.read` satırı `{**frame}` ile
kuruyor, yani `mode` ve `linkedTo` gidiş-dönüşten sağ çıkıyor. Bunun kendi testi var: modun motora
ulaşması bu gidiş-dönüşe bağlı, ve bir gün okumayı sıkılaştıran biri bunu farkında olmadan kırabilir.

## Sahtelerin genişlemesi

`test_photo_usecases.py`'daki her sahte üretici `generate(..., source=None)` imzasını taşıyor.
Motor `end=` göndermeye başladığında hepsi `TypeError` verir — ve o kırmızı, maddenin sorduğu şey
hakkında hiçbir şey söylemez. Bu yüzden **imzalar bu turda genişliyor**: sahteye `end=None`
eklemek kod yazmak değil, kırmızıyı okunur tutmak. `FakeGenerator` ayrıca aldığı bitiş karelerini
`ends` listesine yazıyor — motorun ne gönderdiğini görmenin başka yolu yok.

## Yazılacak testler

### `backend/tests/test_production_mode.py` (yeni)

| # | Test | Ne diyor |
|---|---|---|
| 1 | `test_a_job_that_names_a_mode_has_that_mode` | Üç mod da okunuyor |
| 2 | `test_a_job_that_names_no_mode_is_a_plain_one` | Anahtar yok → standart |
| 3 | `test_a_mode_nobody_knows_is_read_as_the_plain_one` | Tanınmayan değer → standart |

### `backend/tests/test_plan_store.py`

| # | Test | Ne diyor |
|---|---|---|
| 4 | `test_the_plan_keeps_a_jobs_production_mode` | `mode` ve `linkedTo` gidiş-dönüşten sağ çıkıyor |

### `backend/tests/test_photo_usecases.py`

Kuyruk:

| # | Test | Ne diyor |
|---|---|---|
| 5 | `test_a_video_job_carries_the_mode_it_was_queued_with` | standart ve loop plan satırına yazılıyor |
| 6 | `test_a_linked_video_job_names_the_frame_it_ends_on` | `linkedTo` = galeride bir sonraki kare |
| 7 | `test_the_last_frame_takes_no_linked_job_but_the_rest_do` | Son kare düşüyor, kalanlar giriyor |
| 8 | `test_a_linked_batch_with_nowhere_to_end_takes_nothing` | Hepsi düşerse 0, koşu başlamıyor |
| 9 | `test_a_sound_job_carries_no_mode_at_all` | Ses satırında `mode` anahtarı yok |
| 10 | `test_a_mode_nobody_knows_is_refused` | `InvalidMode` |
| 11 | `test_a_sound_cannot_be_asked_to_end_anywhere` | `InvalidMode` |

Motor:

| # | Test | Ne diyor |
|---|---|---|
| 12 | `test_a_plain_video_is_produced_with_no_ending_frame` | `end` None |
| 13 | `test_a_loop_video_ends_on_its_own_picture` | `end` = `source` |
| 14 | `test_a_linked_video_ends_on_the_next_frames_picture` | `end` = hedefin fotoğrafı |
| 15 | `test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red` | Karo kırmızı, kuyruk sürüyor |

## Bitti sayılır

`python -m pytest queen-editor -q` on beş yeni testte kırmızı; kalan üç takım yeşil. Kırmızılık
`production_mode` modülünün olmamasından, `queue_layer`'ın `mode` argümanını tanımamasından ve
`run_loop`'un üreticiye `end` göndermemesinden geliyor. Susturulmuş tek test yok.
