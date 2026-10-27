# Madde 321 — Silme: × hemen siliyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-a` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

× bir pencere açıyor *(`kedi.png silinsin mi?`)*, silme ancak `Sil`'le gidiyor. Sunucu dosyayı
siliyor ama sıraya dokunmuyor: ölü ad yuvasını tutuyor, ardındakiler kaymıyor, ekran boşluğu kesikli
bir yuva olarak çiziyor ve üretim `Havuzda boş yuva var (…)` diye reddediyor *(madde 300, 302)*.
Drive'dan elle silinen dosya da aynı boşluğu bırakıyor.

## Kurallar

1. **× hemen siliyor, pencere yok.** Cevap gelince sıra ondan yeniden çiziliyor.
2. **Ardındakiler birer yer yukarı kayıyor.** Yuva numarası sunucunun cevabından; sırayı sıkıştırmak
   sunucunun işi *(FOUNDATION 4)*.
3. **Boşluk hiçbir yoldan doğmuyor.** Sıra belgesinde dosyası olmayan bir ad — Drive'dan elle
   silinmiş — yuva tutmuyor; numara yalnız havuzda duran dosyalar arasında sayılıyor.
4. **Silinen adın sırada yeri kalmıyor:** aynı adla sonradan yüklenen dosya eski yerine değil,
   sıranın sonuna giriyor — 320'nin *"sıranın sonuna ekliyor"*u. Yalnız okurken yeniden numaralamak
   bunu vermez; ölü ad sırada durdukça yeni dosyayı ortaya çeker.
5. **Üretimin boşluk reddi gidiyor.** Sırada Drive'dan silinmiş bir ad dururken üretim başlıyor, ve
   H3'e kalanlar sırayla gidiyor.
6. **Silme, havuzun tepesindeki reddi temizliyor** — 320'nin kuralı. 320 silme yarısını test etmedi
   *("Silme bugün de temizliyor")*; bugün temizleyen, pencerenin `Sil`'i. Bu turda yeniden yazılan yol
   o.

**FOUNDATION 1'den bilinçli ayrılış.** İlke *"every destructive action is explicit and confirmed"*
diyor; satır *"Pencere sormuyor"* — tasarımın bilinçli kararı *(V2-UPDATE §3 — "× deletes at once,
with no window"; BEHAVIOUR, Decided here)*. Kullanıcıya soruldu ve satır kazandı *(24 Eylül — "yıkıcı
bir eylem değil, user geri çok hızlı koyabilir")*: havuzdaki dosya kullanıcının yüklediği bir kopya,
geri koymak bir `Ekle`. Karar [yol haritasının](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md)
321 satırında.

## Yazılacak testler

### `backend/tests/test_references.py`

1. **Değişen** `test_a_slot_whose_file_is_gone_stays_empty` →
   `test_a_file_gone_from_the_folder_leaves_no_hole` — sıra `[bir, iki, üç]`, klasörde `bir` ve `üç`:
   yuvalar `1, 2`.

### `backend/tests/test_reference_usecases.py`

2. **Değişen** `test_removing_the_middle_one_leaves_its_slot_empty` →
   `test_removing_the_middle_one_moves_the_ones_after_it_up` — `iki` silinince `(bir, 1), (üç, 2)`.
   Sıranın dokunulmadığını söyleyen satır gidiyor.
3. **Yeni** `test_a_removed_name_uploaded_again_goes_to_the_end` — `iki` silinip aynı adla yeniden
   yüklenince `(bir, 1), (üç, 2), (iki, 3)`.

### `backend/tests/test_reference_routes.py`

4. **Değişen** `test_a_deleted_reference_leaves_its_slot_where_it_was` →
   `test_a_deleted_reference_leaves_no_hole_after_a_restart` — kapıdan silinen ortadaki: cevap
   `(bir, 1), (üç, 2)`, ve aynı klasördeki ikinci sunucu da öyle okuyor *("sayfa yenilenince de")*.

### `backend/tests/test_photo_usecases.py`

5. **Yeni** `test_a_file_gone_from_the_pool_by_hand_does_not_stop_a_reference_run` — sıra
   `[kedi, at, kus]`, havuzda `kedi` ve `kus`: üretim bir kart alıyor, üretici `kedi`, `kus`'u bu
   sırayla alıyor. `FakeReferenceOrders` bir sıra alabiliyor, `run_references` onu geçiriyor.

### `ReferencePanel.test.jsx` — yeni blok *"deleting at once"*

6. **Değişen** `asks before taking a reference out` → `deletes at once, with no window` — ×'e basınca
   `removeReference("düğün", "kedi.png")`, `kedi.png silinsin mi?` yok, satır `Fotoğraflar 0/9`.
7. **Değişen** `draws the slot a deleted reference left empty` →
   `numbers the row the way the server answers after a delete` — üç fotoğraftan ortadakinin ×'i;
   cevap `(bir, 1), (üç, 2)`; `üç.png`'nin kutusu `2` diyor, `iki.png`'nin kutusu yok.
8. **Yeni** `clears the refusal at the top of the pool` — ret kartı duruyorken × basılınca kart
   gidiyor.

İki değişen test ilk bloktan bu bloğa taşınıyor.

## Giden testler

- `test_a_missing_slot_in_the_middle_is_a_gap` ve `test_the_last_one_leaving_is_not_a_gap`
  *(`test_references.py`)* — `references.gaps`'in testleri. Tek okuyucusu üretimin boşluk reddi ve o
  gidiyor; 3. kuralla yuvalar her zaman 1'den sıkı, yani `gaps`'e sorulacak bir havuz kalmıyor.
  Fonksiyon uygulama turunda silinir; testleri bu turda gidiyor, yoksa yeşil turda test silmek
  gerekirdi.
- `test_a_reference_run_with_a_gap_in_the_pool_is_refused` *(`test_reference_usecases.py`)* — ters
  cevabıyla 5. test oldu. Taşındı, çünkü üretimin *başladığını* görmek kuyruğun sahtelerini istiyor ve
  onlar `test_photo_usecases.py`'da; buradaki `run` yardımcısı yalnız retlere kadar koşuyor — kendi
  docstring'i öyle söylüyor.

## Değişen, beklentisi bugün de tutan

- `test_a_dragged_order_drops_the_names_it_left_out` →
  `test_a_sent_order_keeps_only_the_names_the_pool_holds` *(`test_reference_usecases.py`)*.
  Docstring'i boşluğun sürükleyerek kapandığını söylüyordu, ve 321'le boşluk yok; yolladığı sırada
  ölü ad da yoktu, yani sunucunun süzgecini hiç koşmuyordu. Artık bir silmeden önce açık kalmış
  sekmenin yolladığı ölü adı gönderiyor ve belgede görmemeyi bekliyor — 4. kural bu süzgece de
  dayanıyor. Bugün de geçer: bekçi.
- `ready_pool`'un docstring'i *(`test_reference_usecases.py`)* — *"no holes"* gidiyor.

## Bekçiler

- `test_references.py`: `test_the_stored_order_gives_each_reference_its_slot`,
  `test_a_file_the_order_never_heard_of_waits_at_the_end`,
  `test_with_no_stored_order_the_pool_reads_by_name`, `test_each_kind_counts_its_own_slots`.
- `test_reference_usecases.py`: `test_removing_takes_the_file_off_the_disk`,
  `test_removing_something_that_is_not_there_is_not_an_error` *(iki kez silmek bir kez silmekle aynı
  yerde biter — sıra yazılırken de)*, `test_the_pool_carries_the_slot_each_reference_stands_in`,
  `test_the_order_the_user_dragged_is_stored`, `test_a_reference_run_without_h3_is_refused`,
  `test_a_reference_run_with_an_empty_pool_is_refused`.
- `test_reference_routes.py`: `test_two_references_are_uploaded_listed_and_one_is_deleted`,
  `test_the_order_is_saved_and_read_back`, `test_a_reference_run_that_can_go_ahead_answers_with_what_it_took`.
- `test_photo_usecases.py`: `test_a_reference_job_is_rendered_with_the_pools_own_files`.
- `ReferencePanel.test.jsx`: `sends the order a drag makes`, 319'un ve 320'nin blokları.

## Test yazılmayan

- **Ekranın boş yuva çizimi** *(`slotted`, `HOLE`, `N. yuva boş`)* uygulama turunda ölü kod olarak
  gidiyor. Sunucu artık boşluklu bir cevap üretemiyor; ekrana boşluk veren bir test, olmayan bir
  durumu beklerdi.
- **Boş havuz cümlesi** 324'ün *(Kol B)*; burada dokunulmuyor.
- **Drive'dan elle silinip uygulamadan aynı adla yeniden yüklenen dosya.** Sıra belgesinde ölü ad
  kalıyor; 4. kural × yolunda sabitlendi, bu nadir yol sabitlenmedi.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest'te 1–5, vitest'te 6–8 kırmızı; `queen-agent`
satırları yeşil.
