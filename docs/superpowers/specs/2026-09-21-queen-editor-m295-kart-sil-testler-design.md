# Madde 295 — Kartı sil, ekranda tek hareket, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok.

## Madde ne diyor

> *(Kullanıcı, 21 Eylül — "biz silme ve temizleme yaparken bunun da sıkıntısını yaşıyorduk: fotoğraf
> geç sil, geri videoya geç".)* **Olacak:** seçili kartlar katman seçtirmeden, içindeki her şeyle
> birlikte siliniyor.

## İki ayrı eksik

Kodu okuyunca kullanıcının tarif ettiği dolambaç ve ondan çıkan bir de sunucu açığı görünüyor.

**1. Detay sayfasında kartın çıkışı yalnız fotoğraf sekmesinde.**
`PhotoDetail`, *"her sekmede tek bir çıkış"* kuralıyla yazılmış *(madde 80)*: video sekmesinde
duran düğme **videoyu** siler, kartı değil. Kartı silmek için fotoğrafa geçmek gerekiyor — kullanıcının
anlattığı dolambaç tam olarak bu. Seçim çubuğundaki **Sil** zaten kartı içindekilerle birlikte
siliyor; eksik olan, kartın kendi sayfasından her sekmede silinebilmesi.

**2. Yerleşmemiş bir kart kuyruktan çıkarken yalnız fotoğraf yuvasına yazılıyor.**
`remove_frames`, üretilmemiş bir kart için `removed` satırını **fotoğraf** yuvasına yazıyor
*([remove_frames.py:60](../../../queen-editor/backend/features/photo_generation/domain/usecases/remove_frames.py#L60))*.
Kartın borcu başka bir katmansa o iş açık kalıyor — ve **madde 294'ten beri** açık kalan iş kartı
ayakta tutuyor. Yani bugün: fotoğrafı ve videosu birlikte planlanmış, henüz hiçbiri üretilmemiş bir
kart silinince galeriden **gitmiyor**. 294 bu açığı açtı; kapatılacağı yer burası.

Doğrusu: kart çıkarılırken **borçlu olduğu her katmana** `removed` yazılır. Adı da o katmanın kendi
adı olur *(`layer_file`)* — `remove_layer` düşen işler için bunu zaten böyle yapıyor.

## Yazılacak testler

### `backend/tests/test_photo_usecases.py`

1. **`test_a_card_pulled_out_of_the_queue_leaves_no_job_behind`** — fotoğrafı ve videosu planlanmış,
   hiçbiri üretilmemiş kart silinince iki yuvaya da `removed` yazılıyor ve kart galeriden gidiyor.
   Bugün kırmızı: video işi açık kalıyor, kart duruyor.
2. **`test_a_card_planned_only_as_a_video_can_be_pulled_out`** — videodan doğan *(madde 292)*,
   üretilmemiş kart silinince `removed` **video** yuvasına, videonun kendi adıyla yazılıyor. Bugün
   kırmızı: satır fotoğraf yuvasına gidiyor.
3. **`test_a_produced_card_still_loses_every_layer_it_holds`** — üretilmiş kartın silinmesi bugünkü
   gibi: fotoğraf, video ve ses diskten gidiyor. Bekçi, bugün yeşil.

### `frontend/src/features/photo_generation/PhotoDetail.test.jsx`

4. **video sekmesinde *Kareyi sil* var** — videosu olan bir kartın video sekmesinde hem
   *"Videoyu sil — kare kalır"* hem *"Kareyi sil"* duruyor. Bugün kırmızı.
5. ***Kareyi sil* kartın penceresini açıyor** — başlık *"1 kare silinsin mi?"*, ve gövde kartın
   kaybedeceklerini sayıyor *(`lostLayers`)*. Onaylanınca **katman değil kart** siliniyor. Bugün
   kırmızı.
6. **fotoğraf sekmesi kıpırdamıyor** — orada tek düğme var ve sözü aynı. Bekçi, bugün yeşil.

## Bu turda yapılmayacaklar

- Seçim çubuğu: **Sil** zaten kartı her şeyiyle siliyor, ve *"Videoları sil / Sesleri sil"*
  kullanıcının istediği kısayollar — kaldırılmıyor.
- Fotoğraf katmanını ekrandan silmek *(294'te kapı açıldı, düğme istenmedi)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` ve `queen-editor/frontend` kırmızı, sebepleri yukarıdaki dört
test. Kırmızı commit'lenir — frontend'in `dist` yapısı bu turda üretilmez, çünkü kaynak değişmiyor.
