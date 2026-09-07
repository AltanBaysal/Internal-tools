# Madde 144 · Tur 1 (test) — Plan

**Tasarım:** [2026-09-02-queen-editor-m144-form-testler-design.md](../specs/2026-09-02-queen-editor-m144-form-testler-design.md)
**Dal:** `feat/v6`
**Bu tur yalnız `test_notebook_installs_the_producer_groups.py`'ye dokunur.** Defter ellenmez.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. Formda çizilen kısmı ayıran bir yardımcı.

Üçüncü test `#` yorumlarını değil **yalnız çizilen satırları** okumak zorunda, yoksa bugünkü
yorumları görüp bedavaya yeşil gelir — 139'daki vakum testinin aynısı olurdu.

```python
def _drawn(cell):
    """The part of a CONFIG cell Colab draws into the form: #@markdown lines only.

    A plain # comment never reaches the form, so a test that read the whole cell would pass on text
    the person ticking the box cannot see.
    """
    return "\n".join(line for line in cell.splitlines() if line.startswith("#@markdown"))
```

## B. İki grubun arasında ayraç ve başlık var.

```python
def test_the_form_separates_the_two_groups_of_boxes():
    """Colab draws #@param lines into the form and #@markdown text along with them, while a plain
    # comment never reaches it. The two blocks of boxes ran together there with nothing saying
    where one ended.

    Pinned by position rather than by wording: the words stay free to change, the structure cannot
    quietly go away.
    """
    config = _cell("# === CONFIG ===")
    divider = config.find("#@markdown ---")
    heading = config.find("#@markdown ### Fotoğraf modelleri")
    first_box = re.search(r"^PHOTO_\w+ = (?:True|False)  #@param", config, re.M)

    assert divider != -1, "Formda iki grubu ayıran çizgi yok"
    assert heading != -1, "Fotoğraf modelleri başlığı yok"
    assert first_box, "CONFIG'de tek bir model kutusu yok"
    assert divider < heading < first_box.start(), "Ayraç ve başlık kutuların önünde değil"
```

`first_box` desenle bulunuyor, adla değil: dördüncü model eklendiğinde ya da ilki yeniden
adlandırıldığında test kendini düzeltiyor.

## C. Üretici kutularının da başlığı var.

```python
def test_the_form_names_the_producer_boxes_too():
    """Labelling one block and leaving the other bare would read as if the bare one belonged to the
    labelled one -- the same confusion, moved up a line."""
    config = _cell("# === CONFIG ===")
    heading = config.find("#@markdown ### Üreticiler")
    first_box = config.find("INSTALL_PHOTO = ")

    assert heading != -1, "Üreticiler başlığı yok"
    assert heading < first_box, "Başlık kutuların önünde değil"
```

## D. Hangi kutu hangi model, formda yazıyor.

```python
def test_the_form_says_which_model_each_box_installs():
    """A box named PHOTO_NOVAANIME does not tell anyone what it fetches. The lines that do were
    plain # comments, which Colab never draws, so the person ticking the box could not read them.
    Measured over the drawn part alone -- the name being in the cell is what is already true.
    """
    drawn = _drawn(_cell("# === CONFIG ==="))

    for name in ("nova3DCG", "novaOrange", "novaAnime"):
        assert name in drawn, f"{name} formda tanıtılmıyor — yalnız yorumda kalmış"
```

## E. Koşuldu: **3 kırmızı, 736 yeşil.**

Üçü de gerçek `AssertionError`, ve üçünün mesajı da aynı şeyi başka açıdan söylüyor: bugünkü
CONFIG hücresinde tek bir `#@markdown` satırı yok.

| Test | Koşunun söylediği |
|---|---|
| C `..._names_the_producer_boxes_too` | `Üreticiler başlığı yok` — `assert -1 != -1` |
| B `..._separates_the_two_groups_of_boxes` | `Formda iki grubu ayıran çizgi yok` — `assert -1 != -1` |
| D `..._says_which_model_each_box_installs` | `nova3DCG formda tanıtılmıyor` — `assert 'nova3DCG' in ''` |

**D'nin mesajı A'daki kaygıyı doğruluyor:** `_drawn` **boş string** döndürdü. Yani test bütün
hücreyi okusaydı `nova3DCG`'yi bugünkü `#` yorumunda bulur ve bedavaya yeşil gelirdi — ölçtüğü şey
tam olarak *"kullanıcının görebildiği yerde mi"*.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.**

## F. Kırmızı commit.

Test dosyası ve bu turun iki belgesi.

## Bilerek yapılmayanlar

**`queeneditor.ipynb` ellenmez** — bu turun tamamı testtir.

**`skip` / `xfail` yok.**

**Metnin nasıl göründüğü** — takımın söyleyemeyeceği şey; doğrulaması Colab.
