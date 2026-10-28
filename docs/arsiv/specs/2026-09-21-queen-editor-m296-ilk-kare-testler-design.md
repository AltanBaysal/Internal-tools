# Madde 296 — Video inince ilk karesi fotoğraf yuvasına, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok.

## Madde ne diyor

> *(Kullanıcı, 21 Eylül — "card'da olabilir bence, bazen hızlıca dolanmak istiyoruz ve videonun
> yüklenmesi daha yavaş sürüyor".)* Fotoğrafı olmayan bir karta video indiğinde ilk karesi `ffmpeg`
> ile çıkarılıp fotoğraf yuvasına yazılıyor. **Bir üretim işi ilk kez iki yuvayı birden dolduruyor.**

Kullanıcının bunu istemesinin ikinci sebebi de var *(21 Eylül)*: *"export'ta photos kısmı var ya, bir
kartın direkt fotoğrafı yoksa ilk karesi fotoğrafı olsun."* İkisi de aynı yazmayla karşılanıyor —
galeri de export da zaten **fotoğraf yuvasını** okuyor, ve ikisi de bu maddeden haberdar olmuyor.

## Nerede oluyor

**`domain/run_loop.py`**, videonun satırı yazıldıktan hemen sonra. Kural yuvalar hakkında, ve
yuvaların kuralı domain'in: *"fotoğraf yuvası boşsa, videonun ilk karesi oraya yazılır."* Boşluk
`layers.can_produce(…, PHOTO)` ile sorulur — 293'te tek yere inen kural burada da tekrarlanmaz.

**Çıkarma işi ffmpeg'in**, yani `data/`'nın. Domain oraya bakamaz *(CODE-STANDARD)*, o yüzden yeni
bir port: `ports.Stills`, tek yöntem — `first_frame(video: bytes) -> bytes`.

## Taşıma yolu

Port, `writers`'ın gittiği yoldan gider: `make_job(..., stills=None)`, ve kuyruğa açılan **yedi
kapının** hepsi onu taşır *(`run_queue`, `start_batch`, `queue_layer`, `regenerate`, `retry_frame`,
`retry_failed`, `resume_batch`)*. Bugün `writers` tam olarak böyle taşınıyor; ikinci bir yol icat
etmek, iki yolun ayrışacağı gün demek.

`None` olduğunda hiçbir şey çıkarılmaz — bugünkü davranış, ve bütün eski testlerin dokunulmadan
yeşil kalmasının sebebi.

## Kararlar

**1. Fotoğraf yuvası doluysa hiçbir şey yapılmaz.** Üretilmiş bir resmin üstüne yazmak *"üret = ekle"*
kuralını çiğnerdi, ve kullanıcının işi kutsaldır *(FOUNDATION 1)*.

**2. Kırmızı bir fotoğraf yuvası da doludur.** `can_produce` bunu zaten böyle okuyor: kırmızı katman
yuvayı tutar ve *Tekrar dene* ile kurtarılır. Kendiliğinden bir resim yazmak o kurtarmayı çalardı.

**3. Çıkarma patlarsa video yine de tamamdır.** Satırı yazıldı, dosyası diskte, ve kullanıcının
istediği oydu. Hata `log`'a ffmpeg'in kendi son satırıyla düşer *(stil: sebep uydurulmaz)*, kart
resimsiz kalır — bugünkü hâli. Kuyruk durmaz.

**4. Resmin adı kartın kendi adı** *(`photo_file(fid)`)*: fotoğraf yuvasının dosyası her zaman öyle
adlandırılır, ve galeri seçimi o ada bakar.

**5. Satırın prompt'u boş.** Bu resmi kimse yazmadı; videonun sözlerini fotoğraf satırına kopyalamak,
kartın *"bu resim şundan yapıldı"* cevabını yanlışlardı.

## Yazılacak testler

### `backend/tests/test_frame_queue.py` — döngü

1. **`test_a_video_landing_on_a_pictureless_card_writes_its_first_frame`** — fotoğrafsız karta video
   inince kartın fotoğraf yuvası dolu, dosya kartın kendi adıyla kaydedilmiş, ve çıkarıcıya giden
   baytlar videonun baytları.
2. **`test_a_card_that_has_a_picture_keeps_it`** — fotoğrafı olan karta video inince ikinci bir
   kayıt yazılmıyor, resim değişmiyor.
3. **`test_a_red_photo_slot_is_not_filled_behind_the_users_back`** — fotoğrafı patlamış kart
   *Tekrar dene*'yi bekler; video inince oraya resim yazılmaz.
4. **`test_a_video_stands_on_its_own_when_no_stills_port_was_handed`** — `stills` verilmediğinde
   bugünkü davranış: yalnız video yazılır.
5. **`test_a_first_frame_that_cannot_be_read_leaves_the_video_done`** — çıkarıcı patlayınca videonun
   satırı duruyor, kuyruk *done* ile bitiyor, ve `log` ffmpeg'in cümlesini taşıyor.
6. **`test_the_gallery_draws_the_frame_the_video_left`** — maddenin *"görülür"* cümlesi: galeri
   kartı o resimle çiziyor.

### `backend/tests/test_ffmpeg_stills.py` — araç

7. **`test_the_first_frame_is_asked_of_ffmpeg`** — komut videonun yolunu, tek kare isteğini ve PNG
   hedefini taşıyor.
8. **`test_a_failed_extraction_carries_ffmpegs_own_last_line`** — hata ffmpeg'in son satırı, uydurma
   bir sebep değil.

## Bu turda yapılmayacaklar

- **Export'a dokunulmuyor**: fotoğraf yuvasını zaten yazıyor, ve bu maddenin bütün amacı ona ayrıca
  bir şey öğretmemek.
- Frontend'e dokunulmuyor: galeri de zaten fotoğrafı çiziyor.
- Referans kipinden doğan kartlar *(303)* ve REF2VA üreticisi *(304)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı, sebebi yukarıdaki sekiz testten altısı *(2, 3 ve 4
bugün de yeşil — `stills` hiç yokken hiçbir şey yazılmıyor)*.
