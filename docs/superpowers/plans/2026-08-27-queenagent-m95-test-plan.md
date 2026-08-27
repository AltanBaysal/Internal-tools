# Madde 95 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m95-prompt-sirasi-testler-design.md](../specs/2026-08-27-queenagent-m95-prompt-sirasi-testler-design.md)
**Bu turda kod yazılmaz.** Dokuz test kırmızıya döner, bir tanesi bugün de yarın da yeşil.
**Komut:** `python -m pytest queen-agent -q`

---

## Tek dosya

`queen-agent/backend/tests/test_build_prompts.py`. Ön yüz bu maddede değişmiyor, yani `dist` yok ve
`npm test` bu turda bir şey söylemiyor.

Var olan yirmi sekiz testin hiçbiri silinmiyor ve yeniden yazılmıyor. Üçü yeni sırayla da doğru
kalıyor — sabit sıra *(tek karakterli kare)*, iki karakterin kendi sırası *(ilk yazılan hâlâ önde)*,
ve karakter bloğunun bütün kalması. Yeni davranışı tarif eden şey aşağıdaki onu.

## 1 · Yeni sabitler

Dosyanın başındaki sabitlere iki tane ekleniyor, var olanlara dokunulmadan:

```python
PEOPLE = "1girl, 1boy"
# No count inside the identity: where the count belongs is the frame's own field, and this one is
# written the way the maps are meant to read from Madde 95 on.
EDA = "freckles, green eyes"
```

Var olan `AYLIN` ile `DENIZ` tanımlarının içindeki `1girl` / `1boy` **kalıyor**. Kod onları
ayıklamıyor *(K27)*, ve `test_a_repeated_solo_tag_is_left_exactly_as_written` bunun üstünde duruyor.

## 2 · Dokuz kırmızı

Hepsi dosyanın sonuna, `test_the_output_is_named_after_the_source`'un üstüne giriyor.

### 1. Sayı en başta

```python
def test_the_people_tag_is_written_right_after_quality():
    built = build_prompts(_structure(frames=[_frame(people="1girl")]))
    assert built == [f"{QUALITY}, 1girl, {AYLIN}, {BEDROOM}, an action, a camera"]
```

Bugün: alan hiç okunmuyor, sayı çıktıda yok. **Kırmızı.**

### 2. Sayısız eski kare

```python
def test_a_frame_without_a_people_tag_still_splits():
    # Files written before the field existed carry no count. What is missing is skipped -- the way a
    # missing quality is skipped -- and the order still opens up around the camera.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": [], "deniz": []})]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera, {DENIZ}"]
```

Bugün: `DENIZ` mekândan önce geliyor. **Kırmızı.**

### 3. Başı çeken her karede yeniden belirleniyor

```python
def test_who_leads_is_decided_frame_by_frame():
    # The same two people can be in front in one frame and behind in the next: what decides is the
    # order this frame wrote them in, nothing carried over from the maps.
    frames = [
        _frame(characters={"aylin": [], "deniz": []}),
        _frame(characters={"deniz": [], "aylin": []}),
    ]
    built = build_prompts(_structure(frames=frames))
    assert built[0].index(AYLIN) < built[0].index("a camera") < built[0].index(DENIZ)
    assert built[1].index(DENIZ) < built[1].index("a camera") < built[1].index(AYLIN)
```

Bugün: ikisi de kameradan önce. **Kırmızı.**

### 4. İkisi kameranın iki yakasında

```python
def test_the_second_character_lands_past_the_camera():
    frame = _frame(people=PEOPLE, characters={"aylin": [], "deniz": []})
    assert build_prompts(_structure(frames=[frame])) == [
        f"{QUALITY}, {PEOPLE}, {AYLIN}, {BEDROOM}, an action, a camera, {DENIZ}"
    ]
```

Bugün: sayı yok ve `DENIZ` başta. **Kırmızı.**

### 5. Öndeki blok bütün

```python
def test_the_leading_characters_outfit_comes_before_the_place():
    # The whole front half in one chain: identity, its outfit, then the place -- and whoever is left
    # is nowhere near them.
    frame = _frame(people=PEOPLE, characters={"aylin": ["gecelik"], "deniz": []})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert (
        built.index(AYLIN)
        < built.index(GECELIK)
        < built.index(BEDROOM)
        < built.index("a camera")
        < built.index(DENIZ)
    )
```

Bugün: `DENIZ` mekândan önce, zincir kırılıyor. **Kırmızı.**

### 6. Arkadaki blok da bütün

```python
def test_the_outfit_of_whoever_comes_last_follows_them_past_the_camera():
    frame = _frame(people=PEOPLE, characters={"aylin": [], "deniz": ["takim"]})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert built.index("a camera") < built.index(DENIZ) < built.index(TAKIM)
```

Bugün: ikisi de kameradan önce. **Kırmızı.**

### 7. Üç kişide ikinci ve üçüncü yan yana

```python
def test_the_second_and_third_stay_side_by_side_at_the_end():
    # The accepted cost of the new order: the two behind can still bleed into each other. What the
    # order protects is the one in front.
    structure = _structure(
        characters={"aylin": AYLIN, "deniz": DENIZ, "eda": EDA},
        frames=[_frame(people="2girls, 1boy", characters={"aylin": [], "deniz": [], "eda": []})],
    )
    assert build_prompts(structure)[0].endswith(f"{DENIZ}, {EDA}")
```

Bugün: üçü de mekândan önce, çıktı `a camera` ile bitiyor. **Kırmızı.**

### 8. Eski düz listede de ilk isim öne geçiyor

```python
def test_the_old_list_form_makes_its_first_name_the_leading_character():
    built = build_prompts(_structure(frames=[_frame(characters=["aylin", "deniz"])]))[0]
    assert built.index(AYLIN) < built.index("a camera") < built.index(DENIZ)
```

Bugün: ikisi de kameradan önce. **Kırmızı.**

### 9. Kimsesi olmayan kare de sayısını söylüyor

```python
def test_a_frame_with_nobody_in_it_still_says_how_many():
    built = build_prompts(_structure(frames=[_frame(people="no humans", characters={})]))
    assert built == [f"{QUALITY}, no humans, {BEDROOM}, an action, a camera"]
```

Bugün: sayı çıktıda yok. **Kırmızı.**

## 3 · Bir yeşil bekçi

```python
def test_an_empty_people_tag_adds_nothing():
    # Green today because the field is not read at all, and it has to stay green tomorrow: a count
    # that is written blank must not leave a gap behind, the way an empty quality does not.
    built = build_prompts(_structure(frames=[_frame(people=" ")]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]
```

## 4 · Nasıl koşulur

```
python -m pytest queen-agent -q
```

Beklenen: **dokuz `FAILED`**, hepsi `test_build_prompts.py`'den. Yeşil bekçi geçer.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi — defter bu dalı gösterdiği için
kırmızılar ve koşunun sonunda `main`'e çevrilecekler.

## 5 · Commit

Spec, plan ve testler tek kırmızı commit'te:

```
test(queen-agent): red for a prompt that leads with its main character
```
