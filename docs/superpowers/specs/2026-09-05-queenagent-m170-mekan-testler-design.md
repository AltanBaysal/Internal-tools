# Madde 170 · test turu — mekân yönetimi

**Kaynağı:** [v7 yol haritası, Madde 170](../plans/2026-09-05-queenagent-v7-roadmap.md).
Kalıbı [168](2026-09-05-queenagent-m168-karakter-testler-design.md) kurdu,
[169](2026-09-05-queenagent-m169-kiyafet-testler-design.md) taşınabilir olduğunu gösterdi. Bu madde
**üçüncü ve son kaynak**. Bu tur yalnız testleri yazar.

---

## Mekânın kendi farkı: karede tekil bir alan

Karakter kadronun anahtarı, kıyafet o anahtarın listesinin içinde — ikisi de `cast_of`'un okuduğu
yerde. **Mekân hiç orada değil:** karenin kendi alanı, `frame["location"]`, ve **bir karenin tek
mekânı var.**

Bunun iki sonucu:

- `_frames_naming` mekân için kadroya hiç bakmıyor, alanı okuyor.
- `_renamed_in_frames` mekân için listeye girmiyor, alanı yazıyor.

Şekil belirsizliği de yok: bir karakterin iki yazılışı, bir kıyafetin iki yazılışı var; bir mekân
her zaman tek dize. Yani bu üç maddenin **en dar** olanı, ve kalıbın gerçekten kalıp olup olmadığını
en iyi bu ölçüyor: yeni bir kaynak iki satırla mı geliyor, yoksa gövde her seferinde mi
esniyor.

## Fiil zaten yazılı

`_STILL_USED_IN`'in `"locations"` satırı 169'da yazıldı ve bugüne kadar hiç koşmadı:

> *bedroom* is still the place in frames *1, 2, 3*. Nothing was removed.

Bu madde onu çalıştıran ilk test. *"is still in frames"* demek bir mekân için yanlış okunurdu —
mekân karede **duran** bir şey değil, karenin kendisi.

---

## Testler — `test_tools.py`

`CAST`'in tek mekânı `bedroom` ve üç karenin üçü de orada. Silinebilir bir girdi gerekiyor:
fikstüre **`kapi_onu`** ekleniyor, hiçbir karenin yeri değil.

| Test | İddiası |
|---|---|
| `test_add_location_writes_the_name_and_its_tags` | Haritada duruyor |
| `test_add_location_says_what_it_added` | *Added balkon to locations.* |
| `test_add_location_refuses_a_name_that_is_already_there` | *There is already a location called bedroom.* — belirteç `a`, çünkü tekil sessizle başlıyor |
| `test_add_location_needs_a_name` | *A location needs a name.* |
| `test_update_location_changes_the_tags` | Metin değişiyor |
| `test_update_location_refuses_a_name_nobody_knows` | Bilinen **mekânlar** sayılıyor |
| `test_update_location_renames_and_the_frames_follow` | Üç karenin `location` alanı yeni adı taşıyor, kadroları el değmemiş |
| `test_update_location_says_how_many_frames_followed` | *Renamed bedroom to yatak in locations; 3 frames followed.* |
| `test_remove_location_takes_the_name_out` | Yersiz mekân gidiyor |
| `test_remove_location_refuses_while_it_is_a_frames_place` | **Kendi fiili:** *is still the place in frames 1, 2, 3* |
| `test_remove_location_leaves_the_frames_alone` | Silinince kareler el değmemiş |

Ortak açıcı için `LOCATION_TOOLS` üstünde parametreli bir test, `test_modes.py`'nin `WRITES`'ına
ve `test_every_tool_is_declared_to_the_model`'e üç ad.

**Bir tane de kalıbı ölçen test:** `test_the_three_maps_are_managed_by_the_same_nine_tools` —
dokuz aracın hepsi `TOOL_SPECS`'te, ve her birinin imzası aynı şekilde *(`file` + `name`, ekleyen
ve güncelleyen ayrıca `tags`)*. Üç kaynağın gerçekten tek kalıp olduğunu söyleyen tek yer; sonraki
bir madde birine parametre eklerse burası söyler.

---

## Bu turda yapılmayanlar

- **Kod açılmıyor.**
- **Kapı hâlâ açık** — 171. Bu maddeden sonra dokuz araç var, yani modelin yapı dosyasına
  dokunmak için metne ihtiyacı kalmıyor; kapı ancak o zaman kapanabilir, ve sırası öyle dizildi.
- **Kareye mekân koyan araç yok** — `add_scene` ve `update_frame`, 173 ile 174.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Koşan kırmızı: 17 vak'a.** On bir yeni mekân testi, ortak açıcının üç parametreli vak'ası,
   kalıbı ölçen test, `test_modes.py`'nin ask kipi testi, ve
   `test_every_tool_is_declared_to_the_model`.
3. Öteki üç takım rakamlarını korur.
4. Kırmızı commit'lenir.
