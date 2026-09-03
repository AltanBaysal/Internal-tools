# Madde 152 — Test turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m152-parametre-testler-design.md) ·
**Tur:** test *(kırmızı commit'lenir)*

Yalnız testler, hepsi `test_tools.py`'de. `tools.py`'ye dokunulmuyor.

---

## 1. Yardımcı

- `_add(files, **fields)` — `add_frames`'i düz parametrelerle çağıran küçük bir sarmalayıcı, makul
  varsayılanlarla *(`name="scene.json"`, bir `action`, bir `camera`)*.
- Sebebi: on iki test aynı çağrıyı yapıyor ve her birine beş parametre yazmak, ölçtükleri şeyi
  gürültünün altında bırakır. Bir testin **neyi** değiştirdiği tek satırda görünsün.

## 2. On iki testi çevir

`frames=[FRAME]` → düz parametreler. Ölçülen şey değişmiyor:

- sona ekleme · sayıların cevabı · kartın kelimesi · haritalara dokunmama · Türkçe'nin okunur
  kalması · olmayan dosya · bozuk JSON'un kendi cümlesi · `frames` listesi olmayan yapı · kart
  çizmemesi · kapının yapısal araçların önünde olmaması

## 3. İki testi çıkar

- **`test_add_frames_refuses_a_frames_argument_that_is_not_a_list`** — `frames` diye bir parametre
  kalmıyor.
- **`test_adding_nothing_writes_nothing`** — boş liste diye bir şey kalmıyor. Yerine 5. adımdaki
  `action`/`camera` reddi geçiyor.

## 4. Şekil testleri

- **`test_a_frame_is_built_from_flat_parameters`** — dosyada doğru şekliyle duruyor.
- **`test_the_new_frame_carries_no_people_field`** — model onu yazmıyor, kod da henüz saymıyor.
- **`test_add_frames_asks_for_no_people_and_no_frames_list`** — araç tanımında iki parametre de yok.

## 5. Ret testleri

Her birinde **iki iddia**: cevapta ret var, ve dosya aynı kalmış.

- **`test_one_unknown_field_refuses_the_whole_call`**
- **`test_the_old_nested_form_is_refused`** — `frames=[…]` artık tanınmayan bir alan.
- **`test_a_character_nobody_knows_refuses_the_frame`** — cümle bilinenleri sayıyor.
- **`test_an_outfit_nobody_knows_refuses_the_frame`**
- **`test_a_frame_without_an_action_is_refused`**
- **`test_a_frame_without_a_camera_is_refused`**

## 6. Geçen testler

- **`test_a_character_can_enter_a_frame_wearing_nothing`**
- **`test_a_frame_with_nobody_in_it_is_allowed`**

## 7. Koş, kırmızıyı gör, commit'le

```
python -m pytest queen-agent -q
```

Büyük kırmızı bekleniyor: çevrilen on iki test ve yeni testlerin çoğu. Diğer üç satır ardışık
koşulur — bu madde onlara dokunmuyor.

`test(m152): …`
