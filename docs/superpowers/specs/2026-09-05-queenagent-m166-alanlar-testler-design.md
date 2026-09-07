# Madde 166 · test turu — `quality` ve `people` kodun eline geçer

**Kaynağı:** [v7 yol haritası, Madde 166](../plans/2026-09-05-queenagent-v7-roadmap.md).
Bu tur **yalnız testleri** yazar; kod değişmez ve takım kırmızı commit'lenir.

---

## Ne değişecek *(uygulama turunun işi, burada yalnız tarif)*

`build_prompts.py`'de iki satır:

- `lead = [structure.get("quality") or DEFAULT_QUALITY, frame.get("people", "")]` → yalnız
  `DEFAULT_QUALITY`. Dosyanın kendi zinciri **okunmaz**, `people` diye bir alan **yoktur**.
- `build_character_prompts`'ın `quality = structure.get("quality") or DEFAULT_QUALITY` satırı da
  aynı şekilde.

**`camera` okunmaya devam eder.** Madde 166 onu yazan aracı kaldırmıyor — bugün zaten yalnız
`add_frames` yazıyor ve o 173'te gidiyor. Eski dosyalardaki `camera` `shots` gibi okunur, ve bu
tur onu **koruyan** bir test ekler.

## Kapsam düzeltmesi — şema bu maddede açılmıyor

Yol haritası 166'nın *"şema metninin üç alanı anlatan cümleleri"*ni de değiştireceğini yazıyordu.
**Değişmiyor:** `schema.py` Madde 172'de bütünüyle siliniyor, ve `test_schema.py`'nin bu üç alana
bakan testleri onunla gidiyor. Burada düzeltilirse aynı satırlar iki kez yazılmış olur — koşunun
kendi işini geri almaması kuralı *(163, 165 ve üç adlandırmanın bu koşuya alınmama sebebi)*.

**Arada kalan pencere bilerek:** 166 ile 172 arasında şema modele `people` ve `quality` yazmasını
söylüyor, kod onları okumuyor. Deneme Dilim 1'in **sonunda** — yani 172'den sonra — koşuluyor, o
yüzden bu pencere dışarıya çıkmıyor.

## Yayılma alanı ölçüldü

`quality`, `people` ve `camera` alanlarını **okuyan tek üretim dosyası** `build_prompts.py`
*(satır 51, 60, 97)*. `schema.py` yalnız metninde anıyor. Testlerde derlenmiş promptun içinde
zinciri doğrulayan tek dosya `test_build_prompts.py`; `test_tools.py:685` alanın **dosyada
kaldığını** doğruluyor ve o iddia değişmiyor.

---

## Testler

Hepsi `queen-agent/backend/tests/test_build_prompts.py`.

### Kırmızı olacak üç nail

| Test | İddiası |
|---|---|
| `test_a_files_own_quality_chain_is_ignored` | `quality` taşıyan yapı `DEFAULT_QUALITY` ile derleniyor, dosyanınki promptta hiç yok |
| `test_a_frames_people_field_is_ignored` | `people` taşıyan kare onsuz derleniyor |
| `test_a_try_ignores_the_files_own_quality` | Aynısı `build_character_prompts` için |

**Neden bu üçü kırmızı:** bugünkü kod dosyanın zincirini tercih ediyor ve `people`'ı zincirin hemen
arkasına koyuyor. Üçü de bugünkü davranışı değil, **yarınkini** yazıyor.

### Fikstür değişikliği — yeşil kalır, kırmızı üretmez

`_structure()`'dan `quality` alanı **çıkar**, ve `{QUALITY}` ile başlayan bütün beklentiler
`{DEFAULT_QUALITY}`'ye döner *(yaklaşık 40 satır)*. Bugünkü kod alan yokken zaten koda düşüyor, o
yüzden bu satırlar **yeşil kalıyor** — ve uygulama turunda da yeşil kalacaklar. Fikstürde alan
bırakılsaydı, kırmızıya **uygulama turunda** düşerlerdi; bir tur kırmızıyı diğerine bırakamaz.

`QUALITY` sabiti yalnız kırmızı nail'de kullanılmak üzere kalır. `PEOPLE` sabiti silinir.

### Ölen testler ve sebepleri

| Test | Neden |
|---|---|
| `test_a_file_that_writes_its_own_quality_keeps_it` | Açık bırakılan kapı kapanıyor; iddiası tersine döndü *(yerine ilk nail)* |
| `test_the_people_tag_is_written_right_after_quality` | Alan yok *(yerine ikinci nail)* |
| `test_an_empty_people_tag_adds_nothing` | Alan yok |

### Adı ve gövdesi değişenler — iddiası duruyor, dayanağı değil

| Bugün | Yarın | Ne oluyor |
|---|---|---|
| `test_a_frame_without_a_people_tag_still_splits` | `test_two_characters_split_around_the_camera` | `people` öncesini anlatan gerekçe gidiyor, sıralama iddiası kalıyor |
| `test_a_frame_with_nobody_in_it_still_says_how_many` | `test_a_frame_with_nobody_in_it_still_builds` | Sayacak alan yok; kimsesiz karenin derlendiği iddiası kalıyor |
| `test_a_structure_without_quality_gets_the_chain_from_code` | `test_the_quality_chain_always_comes_from_code` | Artık *"alan yoksa"* değil, *"her zaman"* |
| `test_a_try_without_quality_gets_the_chain_from_code` | `test_a_try_always_gets_the_chain_from_code` | Aynısı |

`people=PEOPLE` argümanı beş sıralama testinden çıkar: `test_the_second_character_lands_past_the_camera`,
`test_the_leading_characters_outfit_comes_before_the_place`,
`test_the_outfit_of_whoever_comes_last_follows_them_past_the_camera`,
`test_the_two_behind_are_cut_off_from_each_other_too`, `test_break_never_touches_a_comma`.
`test_loose_commas_and_spaces_are_tidied_away` `quality` argümanını bırakır; boşluk temizliğini
zaten `camera=" ,, medium shot,"` ile ölçüyor.

### Eklenen iki yeşil ifade

| Test | Neden yeşil ve neden yine de yazılıyor |
|---|---|
| `test_the_count_rides_in_the_characters_own_tags` | Bugün de geçiyor — `AYLIN` zaten `1girl` ile başlıyor. Sayının artık **nerede** durduğunu söyleyen tek yer bu; `people` gidince yazılı hiçbir yerde kalmıyordu |
| `test_an_old_frames_camera_is_still_read` | `camera`'yı yazan araç kalmayacak *(173)*, ama eski dosyalar taşıyor. `shots` fallback'inin yanındaki ikinci koruma |

---

## Bu turda yapılmayanlar

- **Kod açılmıyor.** `build_prompts.py` bu turda okunur, yazılmaz.
- **`schema.py` ve `test_schema.py` açılmıyor** — yukarıdaki kapsam düzeltmesi.
- **`solo` kuralı yazılmıyor.** İki kişilik karede `solo`'nun yanlış olduğu 172'nin kural metninin
  işi. `test_a_repeated_solo_tag_is_left_exactly_as_written` bugünkü hâliyle duruyor: araç yazılanı
  olduğu gibi taşıyor ve yanlış sayı ekranda görülüyor.
- **`add_frames`'in `people` yazabilmesi** — araç keyfî kare JSON'u alıyor, ve 173'te gidiyor.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir *(CLAUDE.md)*.
2. **Beklenen kırmızı: 3**, hepsi `test_build_prompts.py`'de ve hepsi yukarıdaki nail tablosunda.
   Başka kırmızı çıkarsa yayılma alanı ölçümü eksiktir ve spec düzelir.
3. `queen-agent/frontend`, `queen-editor` ve `queen-editor/frontend` **hiç etkilenmez** — bu madde
   yalnız bir domain modülünün okuduğu alanları değiştiriyor.
4. Kırmızı commit'lenir. `skip` ya da `xfail` yok.
