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

**Ekran** — `features/photo_generation/PhotoDetail.test.jsx`
- `QUEUED_COPY`'nin yorumu: `done` sunucunun cevabı.
- "takes it out of the queue without asking" → fotoğraf sekmesinin "Kuyruktan çıkar"ı
  `dequeueLayer("düğün", ["P0_1"], "video")`; `removeFrames` yok, onay yok, `navigate` yok, Foto sekmesi
  açık. Ret testi: *"Video kuyruktan çıkarılamadı"* ve sunucunun cümlesi.
- Kopyanın videosu çizilirken fotoğraf sekmesinin "Kuyruktan çıkar"ı kapalı.

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
  karede. Modülün yorumu.
- `frontend/src/features/photo_generation/PhotoDetail.jsx`: `handleDequeue(layer)`; fotoğraf sekmesinde
  `produced && awaited` (resmi kendisinin değil) → `handleDequeue(frame.owed[0])`; bekleyen sekme
  `handleDequeue(open)`; o düğme karenin bir katmanı çizilirken kapalı (`dequeues`, `photoBinOff`); sil
  düğmelerinin üstündeki yorum.
- `frontend/src/features/photo_generation/LayerPanel.jsx`: `eligible`, açan katmanı (`type`, yoksa
  `"photo"`) `owed`'da ya da `failed`'da olan satırı saymaz.
- `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`,
  `npm run build --prefix queen-editor/frontend`.

## 3. BACKLOG

- `queen-editor/BACKLOG.md`: iki iş silinir — *"Sıradaki kopya kare kaynağının fotoğrafı yerine "bekliyor"
  gösteriyor"* ve *"Sıradaki kopya kare "Kuyruktan çıkar"dan sonra geri geliyor"*; bir iş girer — *"Aynı
  kimlik iki kez gelince kare iki kez sayılıyor"*.
