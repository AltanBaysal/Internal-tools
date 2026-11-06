# Madde 516 · "Kuyruktan çıkar" yalnız sıradaki işi çıkarır — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-15), 516 · v11-15 ·
**Spec:** [2026-10-29-queen-editor-m516-kuyruktan-cikar-yalniz-isi-design.md](../specs/2026-10-29-queen-editor-m516-kuyruktan-cikar-yalniz-isi-design.md)

Önce test: testler yeni kuralı söyler (kırmızı), sonra kod (yeşil).

## 1. Sunucu testleri

- `backend/tests/test_photo_usecases.py`, `test_the_gallery_stops_reporting_a_deleted_layer`'ın
  altına:
  - `video_owed(...)` ve `dequeue(...)` yardımcıları;
  - sıradaki video çıkar, kare ve fotoğraf kalır, hiçbir şey silinmez;
  - ekranda sırada, sunucuda inmiş video: dokunulmaz (asıl kırmızı test);
  - üstünde bekleyen ses de çıkar;
  - kopya karede yalnız video çıkar;
  - bilinmeyen ve iki kez gelen kimlik; bozuk kare listesi.
- `backend/tests/test_photo_routes.py`: `make_client`'a `dequeue_layer`; `dequeue_request` yardımcısı;
  çıkarma, inmiş video, `photo` için 404, bozuk liste 400, olmayan proje 404.
- `backend/tests/test_plan_hold.py`: çıkarmayla aynı anda gelen Kuyruğa ekle işi yeniden sıraya
  koyuyor; kilit kaldırılınca kırmızı olduğu denendi.

## 2. Sunucu kodu

- `domain/usecases/dequeue_layer.py` (yeni): `owed_on`, `dequeue_layer`.
- `domain/usecases/remove_layer.py`: borçlu işleri `owed_on` ile bulur; davranışı aynı.
- `presentation/routes.py`: `DEQUEUEABLE`, `POST …/layers/<kind>/dequeue`, blueprint'e `dequeue_layer`.
- `main.py`: `dequeue_layer` bağlanır.
- `python -m pytest queen-editor -q`.

## 3. Ekran

- Testler önce:
  - `shared/api.test.js`: `dequeueLayer`'ın adresi ve gövdesi;
  - `PhotoDetail.test.jsx`: api mock'una `dequeueLayer`; "a layer waiting in the queue" bloğu (çıkarma,
    ret, kopya kare); karar 38'i anan test yorumu düzelir;
  - `App.test.jsx`: api mock'una `dequeueLayer`.
- `shared/api.js`: `dequeueLayer(project, frames, kind)`.
- `useGeneration.js`: `dequeueLayer(frames, kind)`.
- `PhotoDetail.jsx`: `handleDequeue`; bekleyen sekme onu çağırır; karar-38 yorumu.
- `removeLayer`, `handleRemoveLayer` ve onay kutusu 516'dan önceki gibi.
- `npm test --prefix queen-editor/frontend`, sonra `npm run build --prefix queen-editor/frontend`.

## 4. BACKLOG

- `queen-editor/BACKLOG.md`, Diğer'in başına: birleşik export'ta ses taşması; bekleyen kopya karenin
  "bekliyor" görünmesi; bekleyen kopya karenin `remove_frames`'ten sonra geri gelmesi.
