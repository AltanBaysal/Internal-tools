# Madde 169 · test turu — kıyafet yönetimi

**Kaynağı:** [v7 yol haritası, Madde 169](../plans/2026-09-05-queenagent-v7-roadmap.md).
Kalıbı [Madde 168](2026-09-05-queenagent-m168-karakter-testler-design.md) kurdu; bu madde onu
**ikinci kaynağa** taşıyor. Bu tur yalnız testleri yazar.

---

## Kalıbın ne kadarı bedava geliyor

`_add_entry`, `_update_entry` ve `_remove_entry` `which`'i parametre alıyor, ve tekil hâli
`which[:-1]`'den türüyor. Yani `"outfits"` ile çağrıldıklarında **haritaya dokunan her şey**
kendiliğinden çalışıyor: ekleme, metin değiştirme, bilinmeyen adın cümlesi, alınmış ad reddi.

**Bedava gelmeyen iki şey var, ve ikisi de kareye dokunuyor:**

### 1 · Kıyafet karenin içinde başka yerde duruyor

Bir karakter karenin `characters` haritasının **anahtarı**; bir kıyafet o anahtarın **listesinin
içinde**. Yani *"hangi kareler bu adı anıyor"* sorusunun cevabı iki harita için iki ayrı yerde, ve
`_frames_naming` bugün yalnız karakteri biliyor.

Yeniden adlandırma da öyle: `_renamed_in_frames` bugün anahtarı değiştiriyor, kıyafet için
**listenin içindeki adı** değiştirmesi gerekiyor — ve `cast_of`'un okuduğu iki şekilde de
*(harita biçimi, ve tek adın listesiz yazıldığı hâl)*.

### 2 · Ret cümlesinin fiili farklı

Karakter *karede*, kıyafet *karede giyiliyor*, mekân *karenin yeri*. Üçü ayrı cümle çünkü üçü ayrı
ilişki — bir kıyafet için *"is still in frames"* demek, onu giyen kimse olmadan orada duruyormuş
gibi okunur.

> *gecelik* is still worn in frames *1, 3*. Nothing was removed.

Bu, `which` başına bir fiil demek. Tek yerde yazılan bir eşleme: üç cümlenin üç ayrı yerde
durması, üçünün ayrı ayrı bayatlaması demek.

---

## Testler — `test_tools.py`

`CAST` fikstürü zaten iki kıyafet taşıyor: `gecelik` 1. ve 3. karelerde giyiliyor, `takim` 2.
karede. Üçüncüsü gerekiyor — **hiçbir karede giyilmeyen** biri, silinebilen tek girdi. Fikstüre
`atki` ekleniyor.

| Test | İddiası |
|---|---|
| `test_add_outfit_writes_the_name_and_its_tags` | Haritada duruyor |
| `test_add_outfit_says_what_it_added` | *Added atki to outfits.* |
| `test_add_outfit_refuses_a_name_that_is_already_there` | *There is already an outfit called gecelik.* |
| `test_add_outfit_needs_a_name` | **Tekil hâl** — *An outfit needs a name.* |
| `test_add_outfit_needs_tags` | *A new outfit needs tags.* |
| `test_update_outfit_changes_the_tags` | Metin değişiyor |
| `test_update_outfit_refuses_a_name_nobody_knows` | Bilinen **kıyafetler** sayılıyor, karakterler değil |
| `test_update_outfit_renames_and_the_frames_follow` | Ad karenin **listesinin içinde** değişiyor, karakterin adı el değmemiş |
| `test_update_outfit_says_how_many_frames_followed` | *Renamed gecelik to pijama in outfits; 2 frames followed.* |
| `test_update_outfit_renames_inside_the_short_form_too` | Kıyafeti listesiz yazan kare de izliyor |
| `test_remove_outfit_takes_the_name_out` | Giyilmeyen kıyafet gidiyor |
| `test_remove_outfit_refuses_while_a_frame_wears_it` | **Kendi fiili:** *is still worn in frames 1, 3* |
| `test_remove_outfit_leaves_the_characters_alone` | Kıyafet silinince karakter haritası el değmemiş |

Ortak açıcı için üç aracı parametreleyen bir test — 168'in üç testinin aynısı, `OUTFIT_TOOLS`
üstünde. Ve `test_modes.py`'nin `WRITES`'ına üç ad, `test_every_tool_is_declared_to_the_model`'e
üç ad.

**Bir tanesi bilerek yeşil doğuyor:** `test_add_outfit_writes_the_name_and_its_tags` gibi haritaya
dokunan testler araç tanımlanmadan kırmızı — ama gövde zaten yazılı olduğu için uygulama turunda
tek satırla yeşile dönüyorlar. Kırmızıyı asıl taşıyan, kareye dokunan üç test ve fiil testi.

---

## Bu turda yapılmayanlar

- **Kod açılmıyor.**
- **Mekân araçları yok** — 170. Fiil eşlemesi orada üçüncü satırını alıyor.
- **Bir kıyafeti bir kareye giydiren araç yok** — o `add_scene` ve `update_frame`, 173 ile 174.
  Bu madde kıyafetin **var olduğu yeri** yönetiyor, karede giyildiği yeri değil.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Koşan kırmızı: 18 vak'a.** On üç yeni kıyafet testi, ortak açıcının üç parametreli vak'ası,
   `test_modes.py`'nin ask kipi testi, ve `test_every_tool_is_declared_to_the_model`.
3. Öteki üç takım rakamlarını korur.
4. Kırmızı commit'lenir.
