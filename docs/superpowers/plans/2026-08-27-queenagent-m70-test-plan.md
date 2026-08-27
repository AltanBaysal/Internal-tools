# Madde 70 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m70-iki-karakter-testler-design.md](../specs/2026-08-27-queenagent-m70-iki-karakter-testler-design.md)
**Bu turda kod yazılmaz.** Beş test kırmızıya döner.
**Komut:** `python -m pytest queen-agent -q`

---

## 1 · `backend/tests/test_build_prompts.py`

Dosyanın başında üçüncü bir karakter doğuyor; bugün iki tane var.

```python
ECE = "1girl, blonde bob"
```

ve `_structure`'ın `characters` haritasına giriyor:

```python
        "characters": {"aylin": AYLIN, "deniz": DENIZ, "ece": ECE},
```

Bu ekleme var olan hiçbir testi kırmıyor: haritada duran ama hiçbir karenin adını anmadığı bir isim
kural kitabında bile *"a note, not a violation"* — kurucu onu görmüyor bile.

`test_each_characters_block_stays_together`'in altına:

```python
# --- more than one person in a frame (Madde 70) ---------------------------------------------------
#
# They used to be built side by side, and an image model cannot tell two neighbouring descriptions
# apart -- whose hair is whose stops being answerable. The fix is distance: the main character stays
# at the front and everyone else goes after the camera, with the place and the action in between.


def test_a_frame_puts_everyone_after_the_first_at_the_end():
    frame = _frame(characters={"aylin": ["gunluk"], "deniz": ["takim"]})
    assert build_prompts(_structure(frames=[frame])) == [
        f"{QUALITY}, {AYLIN}, {GUNLUK}, {BEDROOM}, an action, a camera, {DENIZ}, {TAKIM}"
    ]


def test_three_characters_leave_only_the_first_at_the_front():
    # The second and third stay neighbours at the end, and the same bleeding is possible between
    # them. Known and accepted: the one that has to come out clean is the main character.
    frame = _frame(characters={"aylin": [], "deniz": [], "ece": []})
    assert build_prompts(_structure(frames=[frame])) == [
        f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera, {DENIZ}, {ECE}"
    ]


def test_one_character_is_built_exactly_as_it_was():
    # The half that must not move. A frame with one person has nothing to separate, and a change
    # there would be this item breaking what it was not asked to touch.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": ["gecelik"]})]))
    assert built == [f"{QUALITY}, {AYLIN}, {GECELIK}, {BEDROOM}, an action, a camera"]


def test_the_main_character_stays_in_front_of_the_place():
    # The other half of the rule: everyone else moves, the first one does not.
    frame = _frame(characters={"aylin": [], "deniz": []})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert built.index(AYLIN) < built.index(BEDROOM)
```

Son ikisi **doğdukları anda yeşil** — değişmemesi gerekeni tutan bekçiler.
`test_one_character_is_built_exactly_as_it_was`, `test_a_frames_outfit_follows_its_character` ile
aynı ölçüyü taşıyor; ikisi de duruyor çünkü biri *"kıyafet sahibini izler"* diyor, öteki *"tek
kişilik kare bu maddede değişmez"*.

### Yeşil kalması gerekenler

`test_each_characters_block_stays_together` ve `test_two_characters_keep_the_frames_own_order`
sıralamayı `index` ile ölçüyor. Yeni sırada `AYLIN < GUNLUK < DENIZ < TAKIM` hâlâ doğru — bloklar
bütün, yalnız araları açıldı — ve ilk yazılan hâlâ önce geliyor. İkisinin de iddiası ayakta, o yüzden
dokunulmuyor.

## 2 · `backend/tests/test_skills.py`

Yapılı metnin testlerinin arasına:

```python
def test_the_structured_instruction_keeps_the_count_out_of_the_character():
    # How many people are in a frame belongs to the frame: the same character is alone in one and
    # beside someone in the next. Carried in the entry it is wrong half the time, and written twice
    # when two people share a frame.
    assert '"aylin": "1girl' not in instruction_for("generate-prompts-plus")


def test_the_structured_instruction_shows_the_count_in_the_action():
    said = instruction_for("generate-prompts-plus")
    assert '"action": "1girl' in said
    # Named in the text as well as shown, because the shown one is only ever the single case.
    assert "2girls" in said


def test_the_structured_instruction_says_which_character_comes_first():
    # Code builds the order, but the model writes the map -- and which name it writes first is what
    # decides who stays at the front of the prompt.
    assert "the first character" in instruction_for("generate-prompts-plus").lower()
```

## Beklenen kırmızı

| Test | Neden |
|---|---|
| `..._puts_everyone_after_the_first_at_the_end` | bugün `DENIZ, TAKIM` ortada duruyor |
| `..._three_characters_leave_only_the_first_at_the_front` | aynısı, üç kişiyle |
| `..._keeps_the_count_out_of_the_character` | şema örneği `"aylin": "1girl, long teal hair, ..."` diyor |
| `..._shows_the_count_in_the_action` | örnek action sayı taşımıyor, metin `2girls` demiyor |
| `..._says_which_character_comes_first` | metinde böyle bir cümle yok |

**Beş.** Sayı bugünkü
[build_prompts.py:31-42](../../../queen-agent/backend/features/workspace/domain/build_prompts.py#L31-L42)
ve `GENERATE_PROMPTS_PLUS`'ın şema örneğinden türetiliyor.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `build_prompts.py` ve `skills.py` bu turda açılmaz.
- **Ön yüz açılmaz, `dist` derlenmez.**
- **`docs/2026-08-26-queenagent-ai-yolu-haritasi.md` açılmaz** — metni ve sırayı birebir taşıyor,
  ve kod turunda düzelecek.
