# Madde 139 · Tur 1 (test) — Plan

**Tasarım:** [2026-09-02-queenagent-m139-break-testler-design.md](../specs/2026-09-02-queenagent-m139-break-testler-design.md)
**Dal:** `feat/v6`
**Bu tur yalnız `test_build_prompts.py`'ye dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## 0. Ayraç testte tek bir yerde durur.

Dosyanın başına modül sabiti:

```python
# What separates two character blocks. Written once: the node splits on the literal string, so a
# typo here would be a typo in every assertion at the same time.
BREAK = " BREAK "
```

Beş test onu kullanıyor; beşine ayrı ayrı yazmak, düzeltmesi beş yerde aranan bir literal olurdu.

## A. Üç test yeniden yazılır — sözleşme değişiyor.

**`test_the_second_character_lands_past_the_camera`** — bugün `, {DENIZ}` bekliyor:

```python
    assert build_prompts(_structure(frames=[frame])) == [
        f"{QUALITY}, {PEOPLE}, {AYLIN}, {BEDROOM}, an action, a camera{BREAK}{DENIZ}"
    ]
```

**`test_a_frame_without_a_people_tag_still_splits`** — aynı değişiklik, sayı etiketi taşımayan eski
dosyalarda:

```python
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera{BREAK}{DENIZ}"]
```

**`test_the_second_and_third_stay_side_by_side_at_the_end`** → adı ve yargısı değişir:

```python
def test_the_two_behind_are_cut_off_from_each_other_too():
    # The cost the ordering fix accepted -- the two behind bleeding into each other -- is not worth
    # accepting once a separator exists. One rule, no exception: every character block gets a break.
    structure = _structure(
        characters={"aylin": AYLIN, "deniz": DENIZ, "eda": EDA},
        frames=[_frame(people="2girls, 1boy", characters={"aylin": [], "deniz": [], "eda": []})],
    )
    assert build_prompts(structure)[0].endswith(f"{DENIZ}{BREAK}{EDA}")
```

Eski adı silinir. Kayıt commit'te ve spec'te duruyor; iki isimden birini yaşatmak, hangisinin
geçerli olduğunu soru hâline getirirdi.

## B. Bir yeni kırmızı — maddenin `_tags`'e dokunma sebebi.

```python
def test_break_never_touches_a_comma():
    frame = _frame(people=PEOPLE, characters={"aylin": ["gecelik"], "deniz": ["takim"]})
    built = build_prompts(_structure(frames=[frame]))[0]

    assert BREAK in built
    assert ", BREAK" not in built
    assert "BREAK," not in built
```

**İlk yazımı `BREAK in built` satırını taşımıyordu ve koşuda yeşil geldi** — bugün çıktıda hiç
`BREAK` olmadığı için iki olumsuz iddia da boşta doğruydu. Bir vakum testi: kırılması mümkün
olmayan bir iddia hiçbir şey ölçmüyor. Varlık iddiası önce geliyor, ve ötekileri o anlamlı kılıyor.

## C. İki bekçi — bugün yeşil, yeşil kalmalı.

```python
def test_a_single_character_frame_carries_no_break():
    # Nothing to separate: one block is one block.
    assert "BREAK" not in build_prompts(_structure())[0]


def test_a_character_tried_alone_carries_no_break():
    # The try path builds one character on their own, so there is never a second block.
    assert all("BREAK" not in prompt for prompt in _tried(_structure(), "aylin"))
```

Kimsenin olmadığı kare için ayrı bir bekçi yazılmıyor:
`test_a_frame_with_nobody_in_it_still_says_how_many` tam eşitlikle ölçüyor, yani araya bir `BREAK`
girse zaten kırmızı verir.

## D. Koşuldu: **4 kırmızı, 658 yeşil.**

`python -m pytest queen-agent -q` — dördü de gerçek `AssertionError`. Bu maddede kırmızının başka
türlüsü zaten olamazdı: yeni bir isim doğmuyor, o yüzden hiçbiri `ImportError` değil.

- `test_the_second_character_lands_past_the_camera` ve
  `test_a_frame_without_a_people_tag_still_splits` — beklenen ` BREAK `, gelen `, `.
- `test_the_two_behind_are_cut_off_from_each_other_too` — çıktı `… 1boy, short black hair, freckles,
  green eyes` ile bitiyor; üçüncü karakter hâlâ ikincinin virgülünün ardında.
- `test_break_never_touches_a_comma` — **ilk koşuda yeşil geldi ve düzeltildi**, yukarıda B'de
  yazılı.

**Yeşil bekçiler:** iki yenisi *(tek karakterli kare ve tek başına deneme)*, ve sırayı indeksle
ölçen eskiler — `test_who_leads_is_decided_frame_by_frame`,
`test_each_characters_block_stays_together`,
`test_the_outfit_of_whoever_comes_last_follows_them_past_the_camera`. Üçü sırayı ölçüyor, ve sıra
değişmiyor.

`npm test --prefix queen-agent/frontend` — **36 dosya, 570 yeşil.** Madde ön yüze dokunmuyor.

## E. Kırmızı commit.

Test dosyası ve bu turun iki belgesi.

## Bilerek yapılmayanlar

**`build_prompts.py` ellenmez.**

**`skip` / `xfail` yok.**

**Ön yüz, `dist`, skill metni, şema** — hiçbiri bu turda değil.
