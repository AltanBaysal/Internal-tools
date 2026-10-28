# Madde 298 — Havuzun sınırları sunucuda, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok.

## Madde ne diyor

> Adet *(9 fotoğraf / 3 video / 3 ses)*, klip süresi *(2–15 sn)* ve toplamlar *(görsel 15 sn, ses
> 15 sn)* doğrulanıyor. Süre dosyanın kendisinden okunuyor — `ffprobe`; ffmpeg zaten kurulu.
>
> **Bitti sayılır:** Onuncu fotoğraf, 20 saniyelik bir klip ve toplamı taşıran bir ekleme
> reddediliyor; reddin cümlesi hangi sınıra takıldığını söylüyor.

Sınırı **uygulama hesaplar ve reddeder**, H3'ün hatasına bırakılmaz: o hata Colab loglarında kalır,
kullanıcı görmez *(yol haritasının kararı)*.

## Bir okuma kararı: "görsel toplam"

Fotoğrafın süresi yok. Dolayısıyla *"görsel toplamı 15 sn'yi geçemez"* cümlesinin hesaplanabilir tek
okuması **videoların toplamı**; fotoğraflar adet sınırıyla *(9)* sınırlanıyor, süreyle değil. Havuz
böyle sayıyor, ve kullanıcı koşunun sonunda Colab'da denerken H3 başka bir şey derse burası tek
satırda düzeltilir.

## Süre nereden okunuyor

**Gelen dosya** için baytlardan: geçici bir odaya yazılıp `ffprobe`'a sorulur — 296'nın ilk kare
çıkarıcısının yaptığı iş, başka bir soruyla. Yeni bir araç: `data/ffmpeg_clips.py`.

**Havuzda duran dosya** için kendi yolundan: depo dosyanın yolunu zaten biliyor, ve `ffprobe`
başlıktan okuduğu için dosyayı Drive'dan belleğe çekmeye gerek yok. Bu yüzden **süreyi havuzun
listesi taşıyor** — `list_references` artık her satırda `seconds` veriyor *(fotoğrafta `None`)*.
Ekran da *(299)* bunu gösterecek, yani ikinci bir hesap doğmuyor.

Yani: **sınırlar havuzun kendi listesi üzerinden hesaplanıyor.** `add_references` gelenleri listenin
üstüne ekleyip kuralı bir kez soruyor.

## Kurallar

```
LIMITS   = {picture: 9, video: 3, audio: 3}
2 sn ≤ bir klip ≤ 15 sn          (video ve ses; fotoğrafın süresi yok)
videoların toplamı ≤ 15 sn
seslerin toplamı  ≤ 15 sn
```

**Reddin cümlesi hangi sınıra takıldığını söyler**, ve hangi dosyada takıldığını: kullanıcı on iki
dosya seçmiş olabilir. Tek bir hata tipi *(`PoolLimit`)*, çünkü kapı hepsini aynı şekilde
çeviriyor — ayıran şey cümle.

**Press bir bütün:** 297'deki gibi, bir dosya reddedilirse hiçbiri yazılmaz.

**Süresi okunamayan klip reddedilir**, ffprobe'un kendi cümlesiyle. Süresi bilinmeyen bir dosyayı
havuza almak, sınırın o andan sonra hiç hesaplanamaması demek olurdu.

## Yazılacak testler

### `backend/tests/test_references.py` — kural

1. **`test_a_kind_that_is_full_refuses_the_next_one`** — dokuz fotoğraf varken onuncu; cümlede
   sayı ve dosyanın adı.
2. **`test_a_clip_shorter_than_the_model_takes_is_refused`** — 1 sn.
3. **`test_a_clip_longer_than_the_model_takes_is_refused`** — 20 sn.
4. **`test_the_videos_together_cannot_pass_fifteen_seconds`** — 8 + 8.
5. **`test_sound_is_counted_apart_from_the_pictures_and_videos`** — dolu video toplamı sesi
   engellemiyor.
6. **`test_a_picture_has_no_duration_to_count`** — dokuz fotoğraf hiçbir toplamı taşırmıyor.
7. **`test_what_is_already_in_the_pool_counts`** — havuzdaki iki video, gelen üçüncüyü sınırın
   öbür tarafına atıyor.
8. **`test_a_press_is_counted_as_a_whole`** — tek tek geçen ama birlikte taşıran iki dosya.

### `backend/tests/test_reference_usecases.py` — kullanım senaryoları

9. **`test_a_reference_that_passes_a_limit_is_refused_and_nothing_is_written`**
10. **`test_only_a_clip_is_asked_how_long_it_is`** — fotoğraf `ffprobe`'a hiç gitmiyor.
11. **`test_the_pool_says_how_long_each_clip_is`** — liste `seconds` taşıyor, fotoğrafta `None`.
12. **`test_a_clip_whose_length_cannot_be_read_is_refused`** — ve hiçbir şey yazılmıyor.

### `backend/tests/test_ffmpeg_clips.py` — araç

13. **`test_the_length_comes_back_as_a_number`**
14. **`test_a_length_that_cannot_be_read_carries_ffprobes_own_last_line`**

### `backend/tests/test_reference_routes.py` — kapı

15. **`test_a_reference_that_passes_a_limit_is_a_400`** — cümle geliyor.

## Bu turda yapılmayacaklar

Ekran *(299)*, sıra ve boşluk *(300)*, üretim *(301–305)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı, ve kırmızının sebebi bu on beş test.
