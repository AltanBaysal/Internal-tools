# Madde 140 · Tur 1 (test) — Plan

**Tasarım:** [2026-09-02-queen-editor-m140-modeller-testler-design.md](../specs/2026-09-02-queen-editor-m140-modeller-testler-design.md)
**Dal:** `feat/v6`
**Bu tur yalnız `test_notebook_installs_the_producer_groups.py`'ye dokunur.** Defter ellenmez.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## 0. `re` içeri alınır.

Dosyanın başındaki `import json` / `import os` yanına `import re`. İki test kutuları ve satırları
isimle topluyor; bunu düz `in` ile yapmak *"bir tane var"* diyebilirdi ama *"hepsi eşleşiyor"*
diyemezdi.

## A. Kutu ile satır birbirini tutar.

```python
def test_every_extra_photo_model_has_a_checkbox_of_its_own():
    """The switch has to sit in CONFIG -- Colab draws #@param only where it is written -- and the
    row saying what to fetch sits in the model cell. Two lists, and a name in one but not the other
    is either a box that downloads nothing or a download nobody can turn off.
    """
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", _cell("# === CONFIG ==="), re.M)
    rows = re.findall(r"^\s*\((PHOTO_\w+),", _cell("PHOTO_EXTRA = ["), re.M)

    assert boxes, "CONFIG'de tek bir ek model kutusu yok"
    assert sorted(boxes) == sorted(rows), f"Kutular {sorted(boxes)}, satırlar {sorted(rows)}"
```

## B. Ek modeller kapalı gelir.

```python
def test_the_extra_photo_models_come_switched_off():
    """A run that touches none of the boxes downloads exactly what it downloaded before this item
    existed. That is the claim that makes the rest of this safe to add.
    """
    config = _cell("# === CONFIG ===")
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", config, re.M)
    on = re.findall(r"^(PHOTO_\w+) = True  #@param", config, re.M)

    assert boxes, "CONFIG'de tek bir ek model kutusu yok"
    assert on == [], f"Ek model açık geliyor: {on}"
```

**`boxes` satırı A ile aynı ve bilerek tekrarlanıyor.** Onsuz test bugün **yeşil** gelirdi: hiç
`PHOTO_*` yokken `on` boş çıkar ve iddia bedavaya doğrulanır. 139'da `test_break_never_touches_a_comma`
tam olarak böyle bir vakum testiydi ve koşuda yakalandı; aynı hata ikinci kez yazılmıyor.

## C. İşaretlenmemiş model bayt harcamaz.

```python
def test_an_unticked_photo_model_costs_no_bytes():
    """The rule the three producer boxes already follow, one level down: a row is reached only
    through its own switch.
    """
    assert "in PHOTO_EXTRA if on" in _cell("PHOTO_EXTRA = ["), \
        "PHOTO_EXTRA satırları kendi anahtarıyla süzülmüyor"
```

## D. Disk tahmini seçime göre büyür.

```python
def test_the_photo_estimate_grows_with_the_models_that_were_chosen():
    """The disk check measures against this number and stops the run before a byte is fetched. A
    fixed number under a download that varies is the one way that check can lie.
    """
    assert "(INSTALL_PHOTO, PHOTO_GIB," in _cell("SIZES = ["), \
        "SIZES foto için hâlâ sabit bir sayı taşıyor"
    assert "for on, gib" in _cell("PHOTO_GIB ="), \
        "PHOTO_GIB seçilen modellerden toplanmıyor"
```

## E. Seçilen model gerçekten indiriliyor.

```python
def test_the_notebook_fetches_the_model_this_item_chose():
    """Named rather than derived: this is the one place that says which model 140 added, so a
    silent edit in the notebook cannot quietly change what a run installs.
    """
    source = _source()

    assert "novaOrangeXL_rexV10.safetensors" in source, "Yeni model defterde yok"
    assert "2945776" in source, "Civitai version id defterde yok"
```

## F. Giriş hücresi listeyle uyuşur — 138'in bıraktığı hata.

```python
def test_the_intro_agrees_with_the_custom_node_list():
    """The count lives in three places -- the list, the heading over it, and the sentence that opens
    the notebook. The third went stale when the list grew to 20 (Madde 138) because the test that
    guards the count only ever read the heading.
    """
    listed = _cell("CUSTOM_NODES = [").count('.git"),')
    intro = _cell("# Queen Editor — Colab kurulumu")

    assert listed, "CUSTOM_NODES listesi okunamadı"
    assert f"({listed} custom node)" in intro, \
        f"Giriş hücresindeki sayı listeyle uyuşmuyor: {listed} satır"
```

## G. Koşuldu: **6 kırmızı, 726 yeşil.**

`python -m pytest queen-editor -q` — altısı da gerçek `AssertionError`, hiçbiri `ImportError`
değil *(yeni bir isim doğmuyor)*. Koşunun verdiği sebepler:

| Test | Kırmızının sebebi |
|---|---|
| A | `PHOTO_*` kutusu yok — `boxes` boş |
| B | aynı — ve B'nin ikinci iddiası bu satır olmadan bedavaya geçerdi |
| C | `PHOTO_EXTRA` hücresi yok, `_cell` `""` döndürüyor |
| D | `SIZES` foto için `8` sabitini taşıyor |
| E | dosya adı ve version id defterde yok |
| F | `listed` **20** okundu, giriş hücresinde `(20 custom node)` yok — 138'in bıraktığı hata |

F'nin mesajı özellikle kayda değer: sayıyı listeden okuyup *"20 satır"* diye bastı, yani test
kendi beklentisini de doğru yerden alıyor.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.** Madde ön yüze dokunmuyor.

## H. Kırmızı commit.

Test dosyası ve bu turun iki belgesi. Defter commit'e girmez.

## Bilerek yapılmayanlar

**`queeneditor.ipynb` ellenmez** — bu turun tamamı testtir.

**`skip` / `xfail` yok.**

**`model_groups.py`, uygulama, grafik, `dist`** — hiçbiri bu maddede değil.

**LoRA için ayrı bekçi yazılmaz** — A iddiası her `PHOTO_EXTRA` satırının bir kutusu olmasını
zorunlu kıldığı için LoRA o listeye zaten giremiyor.
