# Madde 143 · Tur 1 (test) — Plan

**Tasarım:** [2026-09-02-queen-editor-m143-panel-testler-design.md](../specs/2026-09-02-queen-editor-m143-panel-testler-design.md)
**Dal:** `feat/v6`
**İki test dosyası:** `test_producers.py` ve `test_notebook_installs_the_producer_groups.py`.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `FakeFiles` ikinci soruyu öğrenir.

```python
class FakeFiles:
    def __init__(self, present=()):
        self.present = set(present)

    def exists(self, folder, name):
        return (folder, name) in self.present

    def has_any(self, folder, suffix):
        return any(at == folder and name.endswith(suffix) for at, name in self.present)

    def path(self, folder, name):
        return f"/models/{folder}/{name}"
```

Sahte, gerçeğin yaptığı işi **aynı veriden** yapıyor: tek bir `present` kümesi, iki soru. Ayrı bir
alan tutsaydı test, kodun tutarlı olmadığı bir dünyayı kurabilirdi.

## B. Grubun şekli değişiyor.

```python
def test_the_photo_group_carries_everything_the_graph_reads():
    """The checkpoint is the one row that names a kind rather than a file: which model is on the
    machine is the user's pick since Madde 140, and the graph loads whichever it was told to."""
    rows = model_groups.GROUPS["photo"]

    assert rows[0] == {"folder": "checkpoints", "suffix": ".safetensors"}
    assert [(row["folder"], row["name"]) for row in rows[1:]] == [
        ("loras", "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"),
        ("upscale_models", "4x_foolhardy_Remacri.pth"),
        ("ultralytics/bbox", "face_yolov9c.pt"),
        ("sams", "sam_vit_b_01ec64.pth"),
    ]
```

## C. Üç yeni kırmızı — panelin gerçek sorusu.

Bunlar `model_groups`'un kendi grubunu değil, **kuralı** ölçüyor, o yüzden test dosyasının kendi
`GROUPS`'una bir foto grubu geliyor:

```python
PICKED = {"photo": [{"folder": "checkpoints", "suffix": ".safetensors"},
                    {"folder": "loras", "name": "style.safetensors"}]}


def test_the_photo_producer_is_installed_with_whichever_model_was_picked():
    """Madde 140 made every checkpoint a box, so the panel cannot ask for one by name any more --
    a user who ticked only the second model renders fine and must read as installed."""
    files = FakeFiles(present=[("checkpoints", "novaOrangeXL_rexV10.safetensors"),
                               ("loras", "style.safetensors")])

    assert list_producers(PICKED, files)[0]["installed"] is True


def test_a_checkpoint_folder_with_nothing_in_it_is_not_installed():
    """The other half of the same claim: any is not none."""
    files = FakeFiles(present=[("loras", "style.safetensors")])

    assert list_producers(PICKED, files)[0]["installed"] is False


def test_a_half_written_download_is_not_a_model():
    """The notebook fetches into <name>.part and renames only once it has validated the file, so an
    interrupted run leaves one behind. Counting it would make the panel lie the other way round."""
    files = FakeFiles(present=[("checkpoints", "novaOrangeXL_rexV10.safetensors.part"),
                               ("loras", "style.safetensors")])

    assert list_producers(PICKED, files)[0]["installed"] is False
```

## D. Adres yasağı iki şekli birden kapsar.

```python
def test_no_group_carries_an_address_the_app_would_have_to_fetch():
    """Addresses live in the notebook now. One left here would be a second truth nobody reads.

    Two shapes are allowed and no third: a row names a file, or it names a kind of file.
    """
    for group in model_groups.GROUPS.values():
        for row in group:
            assert set(row) in ({"folder", "name"}, {"folder", "suffix"}), row
```

## E. Defter kontrolü adsız satırda patlamamalı.

`test_every_file_the_panel_counts_is_fetched_by_the_notebook` bugün `row["name"]` diyor ve adsız
satırda `KeyError` verir:

```python
def test_every_file_the_panel_counts_is_fetched_by_the_notebook():
    """A row that names a kind rather than a file is skipped here and covered by
    test_the_notebook_offers_every_photo_model instead, which pins all three models by name and by
    version id -- a tighter guard than this one, not a looser one."""
    missing = [row["name"] for group in GROUPS.values() for row in group
               if "name" in row and row["name"] not in _source()]

    assert missing == [], f"Defter bu dosyaları indirmiyor: {missing}"
```

## F. Koşuldu: **4 kırmızı, 732 yeşil.**

| Test | Koşunun söylediği |
|---|---|
| B `..._carries_everything_the_graph_reads` | 🔴 satırda `name` var, `suffix` bekleniyor |
| C1 `..._whichever_model_was_picked` | 🔴 `KeyError: 'name'` — `list_producers` şekli tanımıyor |
| C2 `..._folder_with_nothing_in_it...` | 🔴 aynı `KeyError` |
| C3 `..._half_written_download...` | 🔴 aynı `KeyError` |
| D `..._no_group_carries_an_address...` | 🟢 beklendiği gibi |
| E `..._every_file_the_panel_counts...` | 🟢 **beklenmiyordu** |

**İki tahmin tuttu, biri tutmadı, ve tutmayan E.** Plan onu `KeyError` kırmızısı diye yazmıştı;
yeşil geldi, çünkü grup henüz değişmedi — bugünkü satırların hepsi `name` taşıyor, yani
`if "name" in row` süzgeci hiçbir şeyi elemiyor. Yani E bir kırmızı değil, **uygulama turundan
önce gelmesi gereken bir bekçi tadilatı**: grubun şekli değişince `row["name"]` patlardı, ve o
patlama maddenin konusuyla ilgisiz bir yerde olurdu.

D için tahmin *"yeşil kalabilir"* diye yazılmıştı ve öyle oldu — iddia grubun şekli değiştiğinde
anlamını kazanacak.

Üç `KeyError`'ın kırmızı sayılması doğru: kod yeni şekli **tanımıyor**, ve bir istisna da bir
cevaptır — yanlış cevap.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.**

## G. Kırmızı commit.

İki test dosyası ve bu turun iki belgesi.

## Bilerek yapılmayanlar

**`model_groups.py`, `list_producers.py`, `ports.py`, `comfy_models.py`** — hiçbiri bu turda.

**`skip` / `xfail` yok.**

**Grafiğin fallback'i** — tasarımda gerekçesi yazılı; davranışı yanlış değil.
