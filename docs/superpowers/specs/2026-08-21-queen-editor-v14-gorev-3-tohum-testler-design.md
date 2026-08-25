# v14 · Görev 3 — Video ve sesin tohumunun kayda geçmesi · **test turu**

**Kaynak:** [Yol haritası v14, 3. madde](../plans/2026-08-20-queen-editor-v14-roadmap.md)

Bu tur yalnız testleri yazar. Takım kırmızı biter ve kırmızı commit edilir; kodu ikinci tur yazar.

## Bugünkü hâl

Bir katman işi tohumsuz planlanıyor (`queue_layer` `"seed": None` yazıyor). Sonra:

- **Ses** üreticisi kendi tohumunu icat ediyor (`MMAudioGenerator._random_seed`), çünkü MMAudio
  `torch.manual_seed`'e bir tam sayı vermek zorunda. İcat edilen sayı üreticinin içinde kalıyor.
- **Video** üreticisi hiçbir şey yapmıyor: `seed is None` olduğunda grafiğin kendi `-1`'i yerinde
  kalıyor ve rastgeleliği ComfyUI yapıyor.

İki durumda da üretilen katmanın kaydına `"seed": None` yazılıyor. Yani bir videoyu ya da sesi aynı
şekilde bir daha üretmenin yolu yok — kayıt hangi sayıyla üretildiğini bilmiyor.

## Yol haritasının önerisi ve neden değiştirildi

Yol haritası "üç üreticinin de kullandığı tohumu geri döndürmesi" diyor. **Video için bu
uygulanamaz.** Tohumsuz bir video işinde grafikteki değer `-1` olarak kalıyor; rgthree'nin `Seed`
node'u o `-1`'i yalnız tarayıcıdaki widget'ta rastgeleliyor, API'den gönderilen graf'ta değil.
Dolayısıyla üreticinin dürüstçe döndürebileceği tek sayı `-1` olurdu — kayda geçse de hiçbir şeyi
yeniden üretmez.

**Karar: tohumu domain seçer.** Eksik tohum, iş üretime gönderilmeden önce `run_loop` içinde
seçiliyor ve hem üreticiye hem kayda aynı sayı gidiyor. Bu, üreticinin bir şey döndürmesini
gerektirmiyor — çağrı biçimi değişmiyor — ve yan etkisi olarak videodaki `-1` hatasını da kapatıyor.

## Kararlar

**1. Tohum bir modülde.** `domain/seed.py`: `MAX = 2**31 - 1` ve `random_seed()`. Bugün aynı aralık
üç yerde ayrı ayrı yazılı (`main.py`'de iki `lambda`, `mmaudio_generator.py`'de bir fonksiyon); üçü
tek yerde birleşiyor. Aralık foto işlerinin planlandığı aralığın aynısı — tohum nerede doğarsa
doğsun tohumdur.

**2. Tohumu iş başlamadan önce motor seçiyor.** `run_loop`, işin `seed`'i `None` ise bir tane
seçiyor ve o sayıyı hem `producer.generate`'e hem `record.append`'e veriyor.

**3. Bir işin üç denemesi tek tohum paylaşıyor.** Tohum, denemelerin sayacıyla aynı yerde
sıfırlanıyor: iş değiştiğinde yeni tohum, aynı iş tekrar denendiğinde aynı tohum. İkinci deneme
başka bir tohumla gitseydi, "aynı tohumla bir daha üret" kaydın söylediği şey olmazdı.

**4. Ses üreticisi artık tohum icat etmiyor.** `MMAudioGenerator` `new_seed` portunu ve
`_random_seed`'i bırakıyor; kurucusu `(sampler, ffmpeg, tmp_dir=None)` oluyor. İcat ettiği sayının
kayda ulaşma yolu yoktu, ve iki yerde tohum seçmek iki farklı cevap demek.

**5. `main.py` iki `lambda`'yı bırakıyor.** `start_batch` ve `regenerate` `seed.random_seed`
alıyor; `import random` düşüyor.

## Yazılacak testler

### `backend/tests/test_seed.py` (yeni)

| # | Test | Ne diyor |
|---|---|---|
| 1 | `test_a_seed_is_inside_the_range_a_photo_job_is_planned_in` | 0 ≤ tohum ≤ `MAX` |
| 2 | `test_two_seeds_are_not_the_same_number` | Sabit dönmüyor |

### `backend/tests/test_photo_usecases.py`

| # | Test | Ne diyor |
|---|---|---|
| 3 | `test_a_seedless_job_is_produced_with_a_seed_the_engine_chose` | Üreticiye giden tohum None değil |
| 4 | `test_the_seed_a_job_was_produced_with_is_written_down` | Kayda giden tohum üreticiye gidenle aynı |
| 5 | `test_a_job_that_carried_its_own_seed_keeps_it` | Foto işinin tohumu değişmiyor |
| 6 | `test_the_three_attempts_of_one_job_share_one_seed` | Üç deneme aynı sayı |
| 7 | `test_two_seedless_jobs_get_seeds_of_their_own` | İki iş iki ayrı sayı |

### `backend/tests/test_mmaudio_generator.py`

| # | Test | Ne diyor |
|---|---|---|
| 8 | `test_the_sound_engine_invents_no_seed_of_its_own` | Verilen tohum aynen sampler'a gidiyor, kurucu `new_seed` almıyor |

## Bitti sayılır

`python -m pytest queen-editor -q` sekiz yeni testte kırmızı; kalan üç takım yeşil. Kırmızılık
`seed` modülünün olmamasından, `run_loop`'un tohum seçmemesinden ve `MMAudioGenerator`'ın hâlâ
`new_seed` taşımasından geliyor.
