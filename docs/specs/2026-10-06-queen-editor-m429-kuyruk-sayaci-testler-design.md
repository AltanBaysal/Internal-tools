# Madde 429 — Kuyruğun sayacı her işi bir kez sayar, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 429 · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Madde 6 Ekim'de hizalandı; kullanıcının teknik hatalar için sözü
*("ui tasrımı ve ya behaviroyusa konuşalım yoksa en mantıklı şekilde çöz")*: ekran ve davranış
değişmez, hata giderilir. Hata kuralı da onun *("bug çözerken nedenini anlaumazsan rastgeke çözüm
yapma bulmadım de lütfen")*: **bu turun kırmızı testleri sebebi gösterir**; gösteremezlerse uygulama
turu yazılmaz ve madde *"bulamadım"* diye döner.

## Olan

Bir video kuyruktan düşürülüp yeniden istendikten sonra *(madde 211)*, ya da projenin H3 uzunluğu
değiştikten sonra kırmızı videoya *Tekrar dene* basıldığında *(madde 422)*, kuyruk biter ve panel
*"… kare üretildi"* der — o video için bir fazla. **Olması gereken:** her iş bir kez sayılır, motor
onu bir kez yaptığı gibi.

## Sebep — izden, kodla

**Planın bir satırı bir iş değil.** Plan yalnız eklenen bir dosya: aynı iş için ikinci bir satır
iki yoldan yazılıyor.
- **Düşürülüp yeniden istenen katman:** `queue_layer` hücreyi `queued` ile yeniden açıp yeni bir
  satır ekliyor; eski satır planda kalıyor
  *([queue_layer.py:145-154](../../queen-editor/backend/features/photo_generation/domain/usecases/queue_layer.py))*.
- **Uzunluk değiştikten sonra Tekrar dene:** `at_length_now` videonun en son satırını yeni
  uzunlukla bir daha ekliyor
  *([video_length.py:35-55](../../queen-editor/backend/features/photo_generation/domain/video_length.py))*.

**İşin kimliği (kare, katman)'dır.** Durum kayıtta kare ve katman başına tek hücre, ve motor
planı tip tip okurken her karenin yalnız en son satırını alıyor — `_latest_per_frame`, madde 211
*([queue.py:50-67, 93](../../queen-editor/backend/features/photo_generation/domain/queue.py))*.
Aynı (kare, katman) için iki satır, motor için tek iş.

**Sayaç satır sayıyor:** `counts` planın bütün satırlarını dolaşıyor, ve her satırın durumunu o
tek hücreden okuyor *([queue.py:106-116](../../queen-editor/backend/features/photo_generation/domain/queue.py))*.
İki satırlı bir iş bitince `done` onu iki kez sayıyor, `total` satır sayısı; kırmızıysa `failed`
iki, `failures`'ta karenin dosyası iki kez. Bu sayılar hem koşu sürerken `runner.report`'la hem de
koşu bitince `summary` ile yayımlanıyor
*([run_loop.py:236-238, 294](../../queen-editor/backend/features/photo_generation/domain/run_loop.py))*.

**Ekranda görünen:** kuyruk bitince paneldeki *"{job.done} kare üretildi"*
*([QueuePanel.jsx:228](../../queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx))*.

**Elenenler:**
- **Ekran saymıyor:** sunucunun `done`'ını olduğu gibi yazıyor. Panelin kırmızı kartı sayısını
  sunucunun `failed`'ından değil, galerinin karelerinden alıyor
  *([useGeneration.js:355-368](../../queen-editor/frontend/src/features/photo_generation/useGeneration.js))* —
  o kart doğru sayıyor.
- **Kayıt çift değil:** kayıt (kare, katman) başına katlanıyor; tek hücre.
- **Motor işi iki kez yapmıyor:** `test_only_one_video_is_made_after_the_first_was_dropped` ve
  `test_tekrar_dene_makes_a_red_video_again_at_the_projects_length_now` tek üretim görüyor.

**İz bu turda sebep sayılmıyor:** aşağıdaki testler iki yolu da gerçek use case'lerle yürür ve kuralı
`counts`'un kendisinde sorar. Bugün kırmızı olmaları ve **kırmızı oldukları yer — sayıların planın
satır sayısı olması** — sebebi kanıtlar.

## Kurallar

1. **Bir iş bir kez sayılır**, planda kaç satırı olursa olsun: `total`, `done`, `failed` ve
   `failures` — sayacın yayımladığı her sayı.
2. **İşin kimliği (kare, katman):** bir karenin fotoğrafı ve videosu iki iş, iki kez sayılır.
3. **Başka bir şey değişmez:** tek satırlı işlerin sayıları bugünkü gibi; motor, plan ve ekran
   dokunulmadan kalır.

## Nasıl kanıtlanıyor

- **Kural `counts`'ta, sahte hücrelerle** — `test_frame_queue.py`'nin `job` ve `slots`'u.
- **Kullanıcının iki yolu sahte portlarla** *(CODE-STANDARD, Tests)*: madde 211'in testlerinin
  yardımcıları (`frame_with_a_photo`, `ask_again`, `drop_the_video`) ve 422'nin (`red_videos`,
  `at`); sayılar koşunun bittiği `runner.status()`'tan.
- Ekran testi yok: ekran sunucunun sayısını yazıyor, hata orada değil.

## Yazılacak testler

Hepsi `backend/tests/test_frame_queue.py`'de, dosyanın sonunda — kuyruğun kuralının kendi dosyası,
ve dalga 6'nın öteki maddelerinin dokunmadığı bir yer.

### Kural

1. **`test_a_job_planned_twice_is_counted_once`** — P0_0'ın fotoğrafı ve iki video satırı; ikisi de
   bitmiş: `{"total": 2, "done": 2, "failed": 0, "failures": []}`. Kural 2'yi de tutuyor: kare
   başına tek sayan bir düzeltme `total`'ı 1 yapar.
2. **`test_a_failed_job_planned_twice_is_one_failure`** — aynı plan, video kırmızı:
   `{"total": 2, "done": 1, "failed": 1, "failures": ["P0_0.png"]}`.

### Kullanıcının yolları

3. **`test_a_video_dropped_and_asked_for_again_is_counted_once`** — madde 211: video istenir,
   düşürülür, loop istenir ve kuyruk koşar: `total` 2, `done` 2, `failed` 0, `failures` boş.
4. **`test_a_red_video_sent_back_at_a_new_length_is_counted_once`** — 422: 4 saniyede kırmızı
   olmuş video, proje 12'deyken Tekrar dene ile yeniden yapılır: `total` 2, `done` 2.
5. **`test_a_red_video_that_fails_again_at_a_new_length_is_one_failure`** — aynısı, video yine
   kırmızı: `total` 2, `done` 1, `failed` 1, `failures` `["0_a.png"]`.

## Kırmızı beklenen

- 1 – 5 kırmızı, hepsi aynı yerden: sayılar planın satır sayısı. 1, 3 ve 4'te `total` ve `done` 3;
  2'de `total` 3, `failed` 2 ve `failures` `["P0_0.png", "P0_0.png"]`; 5'te `total` 3, `failed` 2
  ve `failures` `["0_a.png", "0_a.png"]`.
- Öteki her şey yeşil; öteki üç satır yeşil. **Kırmızı başka bir yerden geliyorsa sebep
  kanıtlanmamıştır:** commit yok, madde *"bulamadım"* diye döner.

## Bilinçli olarak yapılmayan

- Plan düzeltilmiyor: ne istendiğinin kaydı, ve iş gerçekten iki kez istendi *(madde 211'in
  kararı)*. Tek olan borç, ve artık sayı.
- Ekran değişmiyor; frontend testi yok. *"kare üretildi"*nin videoyu da kare diye sayması bu
  maddenin konusu değil.
- `dist`'e ve yol haritasına dokunulmuyor.
