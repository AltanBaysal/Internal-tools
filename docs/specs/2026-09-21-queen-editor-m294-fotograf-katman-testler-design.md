# Madde 294 — Fotoğraf da silinebilir bir katman, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok.

## Madde ne diyor

> **Olacak:** fotoğraf da öteki katmanlar gibi silinir, yuvası boşalır, kart durmaya devam eder —
> **son katman gidince kutu gider**. Fotoğrafı silinen kartın videosu durur.
>
> **Bitti sayılır:** Fotoğrafı silinen kart galeride videosuyla duruyor; videosu da silinince kart
> galeriden gidiyor.

Kuralın yarısı **293'te** yapıldı: `remove_layer` artık fotoğrafla birlikte videoyu götürmüyor. Bu
madde kalan yarısı — **galerinin** fotoğrafsız kalmış kartı ayakta tutması, ve isteğin sunucuya
ulaşabilmesi.

## Bugün ne oluyor

1. `presentation/routes.py` · `REMOVABLE = (VIDEO, AUDIO)` — `POST …/layers/photo/delete` 404.
2. `list_frames`, madde 292'den beri kartın satırını **onu açan** katmandan okuyor. Fotoğraf silinince
   o katmanın durumu `deleted` olur, `SHOWN`'da da değildir, açık da değildir — ve kart **galeriden
   tamamen düşer**. Videosu diskte durduğu hâlde görünmez olur.
3. `file` alanı fotoğraf yuvasının dosyasını okuyor, **silinmiş olsa bile**: kart artık olmayan bir
   dosyanın adıyla çizilirdi.

## Kural

**Kartı açan iş, planda o kimlikle görünen ve yuvası hâlâ kapanmamış ilk iştir.** Kapanmış
*(`deleted` ya da `removed`)* bir katman kart adına konuşamaz; sıradaki iş konuşur.

**Boş kutu yaşamaz** *(kullanıcı kararı, 21 Eylül)*: konuşacak iş kalmayınca kart galeriden gider.
Ayrı bir kontrol değil — aynı cümlenin diğer ucu.

`file` ise yalnız **duran** bir fotoğrafın dosyasını verir; fotoğraf gitmişse kart kendi kimliğinin
verdiği adla çizilir *(`photo_file(fid)`)*. Bu alan seçimin ve saklanan sıranın anahtarı olduğu için
kimliğin saf bir fonksiyonu olarak kalması gerekiyor; saklanan sıra zaten kimlikle tutuluyor.

## Yazılacak testler

### `backend/tests/test_photo_usecases.py` — galeri

1. **`test_a_card_whose_photo_is_deleted_keeps_its_video`** — fotoğrafı silinmiş, videosu duran kart
   galeride; `layers` yalnız videoyu veriyor, durumu `done`. Bugün kırmızı: kart hiç yok.
2. **`test_a_card_with_no_photo_is_drawn_under_its_own_name`** — aynı kartın `file` alanı silinmiş
   dosyayı değil, kimliğinin adını veriyor. Bugün kırmızı.
3. **`test_a_card_whose_every_layer_is_gone_leaves_the_gallery`** — fotoğrafı ve videosu silinmiş kart
   galeride yok. *"Boş kutu yaşamaz."* İkinci bir kart da eklenir, yoksa galeri zaten boş döner ve
   test yanlış sebepten yeşil olur — 292'de bir kez düşülen tuzak.
4. **`test_a_card_still_owed_a_layer_stays_though_its_photo_went`** — fotoğrafı silinmiş ama videosu
   hâlâ kuyrukta olan kart galeride, `pending`. Kutuyu ayakta tutan şey *"elinde bir şey var"* değil,
   *"konuşacak bir işi var"*. Bugün kırmızı.
5. **`test_deleting_the_photo_leaves_the_card_where_it_was`** — iki kartlı galeride ortadakinin
   fotoğrafı silinince sıra değişmiyor. Kart, açan işinin planda durduğu yerde kalır.

### `backend/tests/test_photo_routes.py` — kapı

6. **`test_the_photo_is_a_layer_that_can_be_deleted`** — `POST …/layers/photo/delete` artık 404
   değil, ve `remove_layer`'a `photo` ile gidiyor. Bugün kırmızı.

## Bu turda yapılmayacaklar

- **Ekran.** Bu madde fotoğraf silmeyi arayüze **koymuyor**: kullanıcı böyle bir düğme istemedi, ve
  ekrandaki silme hareketi 295'in konusu. Açılan şey kural ve kapı.
- Videonun ilk karesinin fotoğraf yuvasına yazılması *(296)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı, ve kırmızılığın sebebi beklenen sebep: 1, 2, 4, 6
düşer. 3 ve 5 bugün de yeşildir — düşerlerse testin kendisi yanlıştır.
