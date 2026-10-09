# Madde 300 — Sıralama ve boşluk, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Karar 21 Eylül'de verildi: *"kaymasın, arada boş kalırsa hata versin
bence — çünkü kayınca fotoların referansları kayacak. User manuel yapsın… ama sürükle bırakla
sırası değiştirebilir olsun."*

## Madde ne diyor

> Referanslar sürükle-bırakla sıralanıyor, ve arada kalan boş yuva ekranda görünüyor.

Sebebi H3'ün kendi kuralı *(yol haritasının kararı)*: referansları **yoğun paketleyip sıraya göre**
numaralandırıyor, yuvanın numarasına göre değil. Numaralar kayarsa prompt'taki `<Picture 3>` başka
bir resmi gösterir — **sessiz** bir hata, ve en kötüsü o.

## Sıra ayrı bir belge

297 havuzu klasörün kendisi yaptı ve *"kullanıcının istediği sıra ayrı bir soru"* dedi. Burası o
soru, ve CODE-STANDARD'ın kuralı gereği **kendi dosyasını** alıyor: `references.json`, projenin
kökünde, `order.json`'ın yanında. Tipe göre üç liste:

```json
{"picture": ["kedi.png", "kuş.png"], "video": [...], "audio": [...]}
```

## Boşluk nasıl var oluyor

**Sıradaki bir ad, dosyası olmadan da yuvasını tutar.** Silmek dosyayı götürür, sırayı değiştirmez —
yani o yuva boşalır ve sonrakiler yerinde kalır. Kullanıcının istediği tam olarak bu: *"sildim
diyelim, 2 boş ve gerisi doğru."*

Bunun güzel yanı: `remove_reference` sıraya hiç dokunmuyor, ve boşluk kendiliğinden doğuyor.

Kullanıcı sürükleyip boşluğu kapattığında ekran **yeni sırayı** yolluyor; ölü ad o listede
olmadığı için dosyadan düşüyor. Sıra kendini böyle temizliyor.

**Sırada adı geçmeyen dosya sona ekleniyor**, ad sırasıyla — yeni yüklenen referans, ve hiç sıra
belgesi olmayan bir havuz böyle okunuyor *(galerinin `apply_order` kuralının aynısı)*.

## Yuva numarası cevabın içinde

Her satır `slot` taşıyor *(tipi içinde 1'den başlayan)*. Ekran boşluğu bundan çiziyor: 1, 3, 4
geldiyse ikinci yuva boştur. Sunucunun ayrıca *"şu kadar yuva"* demesi gerekmiyor.

**302** boşluğu buradan soracak: bir tipte 1..N arasında eksik yuva varsa üretim başlamıyor.

## Yazılacak testler

### `backend/tests/test_references.py`

1. **`test_the_stored_order_gives_each_reference_its_slot`**
2. **`test_a_slot_whose_file_is_gone_stays_empty`** — 1 ve 3 doluyken 2 yok.
3. **`test_a_file_the_order_never_heard_of_waits_at_the_end`** — ad sırasıyla.
4. **`test_with_no_stored_order_the_pool_reads_by_name`** — 297'nin hâli bozulmuyor.
5. **`test_a_missing_slot_in_the_middle_is_a_gap`**
6. **`test_the_last_one_leaving_is_not_a_gap`**
7. **`test_each_kind_counts_its_own_slots`** — video 1,2 ile fotoğraf 1,2 birbirine karışmıyor.

### `backend/tests/test_reference_usecases.py`

8. **`test_the_pool_carries_the_slot_each_reference_stands_in`**
9. **`test_removing_the_middle_one_leaves_its_slot_empty`** — maddenin kalbi.
10. **`test_the_order_the_user_dragged_is_stored`**
11. **`test_a_dragged_order_drops_the_names_it_left_out`** — boşluk böyle kapanıyor.
12. **`test_an_order_that_is_not_lists_of_names_is_refused`**

### `backend/tests/test_reference_routes.py`

13. **`test_the_order_is_saved_and_read_back`** — gerçek diskle, ve yeni bir sunucu aynı sırayı
    okuyor.

### `frontend/.../ReferencePanel.test.jsx`

14. **boş yuva çiziliyor** — 1 ve 3 doluyken arada boş bir kutu var.
15. **sürükleyip bırakmak yeni sırayı yolluyor.**

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` ve `queen-editor/frontend` kırmızı.
