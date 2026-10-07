# Madde 302 — Üretimin reddi, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok.

## Madde ne diyor

> Üç durumda üretim başlamıyor ve sebebini söylüyor: **H3 kurulu değil**, **havuz boş**, **arada boş
> yuva var**.

Üçü de üretimin **hiç başlamaması** gereken durumlar, ve üçünün de sebebi ekranda yazıyor. Sınırlar
gibi *(298)* bu da uygulamanın işi: H3'ün kendi hatası Colab loglarında kalır.

## Referans üretiminin kendi kapısı

Referans üretimi bir katman işi değil: ortada kare yok, kart doğuyor. O yüzden kendi ucu var —
`POST …/references/produce`, gövdesinde `prompts` ve `variants`.

**Bu maddede kapı yalnız reddediyor.** Kart doğurmak **303**'ün işi, ve o madde bu kullanım
senaryosunun gövdesini doldurur. Geçerli bir istek bugün `{"added": 0}` ile dönüyor — hiçbir şey
kuyruğa girmiyor, ve bu doğru: henüz kimse doğurmuyor.

## Üç sebep, ve iki eski sebep

- **H3 kurulu değil.** Hangi video modelinin kurulduğu defterin kararı *(`config.VIDEO_MODEL`)*, ve
  domain config okumaz — bayrak `main.py`'den geçiyor.
- **Havuz boş.** Referanssız bir referans üretimi yoktur.
- **Arada boş yuva var.** `references.gaps` *(300)* söylüyor; cümle hangi satırda olduğunu da söyler.

Bunlara ek olarak kuyruğun bugünkü iki kuralı aynen geçerli: **prompt listesi** okunabilir olmalı
*(`prompt_list.py`, fotoğraf üretiminin kendi ayrıştırıcısı)* ve **varyant** 1–26 arası olmalı
*(`start_batch`'in kendi kuralı)*. İkisi de yeniden yazılmıyor, oldukları yerden çağrılıyor.

## Yazılacak testler

### `backend/tests/test_reference_usecases.py`

1. **`test_a_reference_run_without_h3_is_refused`** — cümle H3'ü söylüyor.
2. **`test_a_reference_run_with_an_empty_pool_is_refused`**
3. **`test_a_reference_run_with_a_gap_in_the_pool_is_refused`** — cümle hangi satır olduğunu
   söylüyor.
4. **`test_a_reference_run_with_everything_in_place_is_accepted`** — bugün sıfır iş, ve **hata yok**.
5. **`test_a_reference_run_reads_the_prompt_list_the_way_the_photo_panel_does`** — bozuk liste
   `InvalidPrompts`.
6. **`test_a_reference_run_counts_variants_the_way_a_batch_does`** — 0 ve 27 reddediliyor.

### `backend/tests/test_reference_routes.py`

7. **`test_a_refused_reference_run_is_a_400_with_its_reason`**
8. **`test_a_reference_run_that_can_go_ahead_answers_with_what_it_took`**

### `frontend/src/features/photo_generation/useGeneration.test.jsx`

9. **referans kipi kendi ucuna gidiyor** — katman ucuna değil.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` ve `queen-editor/frontend` kırmızı.
