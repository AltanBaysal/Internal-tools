# Madde 519 · Bekleyen kopya kare doğru görünür ve yerinde kalır — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-18), 519 · v11-18 ·
**Spec:** [2026-10-30-queen-editor-m519-bekleyen-kopya-kare-design.md](../specs/2026-10-30-queen-editor-m519-bekleyen-kopya-kare-design.md)

Önce test: testler yeni kuralı söyler (kırmızı), sonra kod (yeşil).

## 1. Testler

**Sunucu** — `backend/tests/test_photo_usecases.py`
- `copy_waiting_for_its_video()`: `0_a` fotoğrafıyla, kopyası `P0_1` aynı resmi tutuyor, videosu planda.
- Kopyanın videosunun yanına: bekleyen kopya `done` ve resmiyle; videosu kırmızı kopya `done`,
  `failed: ["video"]`; iki varyantlı basış bekleyen kopyaya kendi kopyasını vermez; kopyanın videosu
  çıkarılınca sıra dosyası aynı, kopya yerinde ve `done`.
- 512'nin ve 513'ün iki varyantlı çift basış testleri (`test_plan_hold.py`, `test_made_once.py`) olduğu
  gibi kalır; durum değişince kırmızıya döner, kapsam sorusuyla yeşile.
- `remove_frames`'in yanına: videosu sırada kendi fotoğraflı kare silinince video `removed`, kare geri
  gelmez; bekleyen kopya silinince video `removed`, `store.deleted` boş, kopya geri gelmez.
- Kopyala ikizi: kendisi için bir şey planlanmamışken video basışının kapsamında; videosu planlanınca
  ikinci iki varyantlı basışta kendi kopyasını almaz.
- `making(project, fid, kind, batch)`: işçisi bir karenin katmanını yapan `PhotoRunner`. İşçinin elindeki
  ya da çizimindeki kare silinmez (`Busy`, hiçbir şey silinmez ya da yazılmaz, sıra aynı); başka kare
  çizilirken ve başka projenin koşusunda silme geçer.
- `remove_frames`'in bütün çağrıları işçiyle (`sync_runner()`, `idle_runner()`): `test_photo_usecases.py`,
  `test_made_once.py`, `test_plan_hold.py`, `test_photo_routes.py`'nin `make_client`'ı.
- `test_photo_routes.py`: çizilen kareyi silme 409, cümle kareyi adlandırır, fotoğraf diskte.
- Fotoğrafı diskte olmayan video: üretici çağrılmaz, video `failed`, *"Kaynak dosya yok: 0_a.png"*.
  Üretilmiş fotoğrafı anlatan ama baytlarını sahte depoya koymayan yardımcılar ve testler (`video_project`,
  `video_job_project`, prompt yazımı testleri; `test_made_once.py`, `test_export_total.py`) fotoğrafın
  baytlarını koyar.

**Ekran** — `features/photo_generation/PhotoDetail.test.jsx`
- `QUEUED_COPY`'nin yorumu: `done` sunucunun cevabı.
- "takes it out of the queue without asking" → fotoğraf sekmesinin "Kuyruktan çıkar"ı
  `dequeueLayer("düğün", ["P0_1"], "video")`; `removeFrames` yok, onay yok, `navigate` yok, Foto sekmesi
  açık. Ret testi: *"Video kuyruktan çıkarılamadı"* ve sunucunun cümlesi.
- Kopyanın videosu çizilirken fotoğraf sekmesinin "Kuyruktan çıkar"ı kapalı; kendi videosu çizilen karede
  Sil kapalı.

**Ekran** — `features/photo_generation/Gallery.test.jsx`
- Seçimde çizilen bir kare varken Sil kapalı ve *"Üretilen kare bitince silinebilir."*; yalnız öteki kare
  seçiliyken açık.

**Ekran** — `features/photo_generation/LayerPanel.test.jsx`
- Bekleyen (`type: "video"`, `owed: ["video"]`) ve videosu kırmızı kopya ne "Videosu olmayan kareler"de
  ne "Seçili kareler"de sayılır.
- Kırmızılar çalıştırılıp görülür.

## 2. Kod

- `backend/features/photo_generation/domain/usecases/list_frames.py`: fotoğraf hücresi `done` olan kartın
  durumu `done`; modülün yorumu.
- `backend/features/photo_generation/domain/usecases/queue_layer.py`: `frames_in_scope`, açan katmanı
  (`queue.type_of(frame)`) borçlu ya da kırmızı kartı atlar; satırın `type`'ının nereden geldiğini söyleyen
  yorum.
- `backend/features/photo_generation/domain/usecases/remove_frames.py`: borçlu işlere `removed` yazan
  döngü `deleted + removed` üstünden; kapanan hücre atlanır; boş borçta fotoğraf hücresi yalnız üretilmemiş
  karede. İşçi ilk parametre; `_being_made` işçinin bu projede yaptığı kareleri (`current`, `batch`)
  verir, istenenlerden biri onlardansa `Busy`. Modülün yorumu.
- `backend/features/photo_generation/presentation/routes.py`: silme kapısında `Busy` → 409.
- `backend/main.py`: `remove_frames`'e `_photo_runner`.
- `backend/features/photo_generation/domain/run_loop.py`: `MissingSource` (kare düzeyinde); `_source_for`
  okunamayan kaynakta onu yükseltir.
- `frontend/src/features/photo_generation/PhotoDetail.jsx`: `handleDequeue(layer)`; fotoğraf sekmesinde
  `produced && awaited` (resmi kendisinin değil) → `handleDequeue(frame.owed[0])`; bekleyen sekme
  `handleDequeue(open)`; kareyi ya da işlerini götüren her düğme karenin bir katmanı çizilirken kapalı
  (`dequeues`, `binOff`); sil düğmelerinin üstündeki yorum.
- `frontend/src/features/photo_generation/Gallery.jsx`: `chosenMaking`; Sil kapalı ve yanında sebebi.
- `frontend/src/features/photo_generation/LayerPanel.jsx`: `eligible`, açan katmanı (`type`, yoksa
  `"photo"`) `owed`'da ya da `failed`'da olan satırı saymaz.
- `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`,
  `npm run build --prefix queen-editor/frontend`.

## 3. BACKLOG

- `queen-editor/BACKLOG.md`: iki iş silinir — *"Sıradaki kopya kare kaynağının fotoğrafı yerine "bekliyor"
  gösteriyor"* ve *"Sıradaki kopya kare "Kuyruktan çıkar"dan sonra geri geliyor"*; bir iş girer — *"Aynı
  kimlik iki kez gelince kare iki kez sayılıyor"*, *"Katmanı kırmızı karonun seçim dairesine basılamıyor"*,
  *"Video paneli zaten sırada olan videoyu da sayıyor"*.
