# Madde 140 · Düzeltme · Tur 1 (test) — Plan

**Tasarım:** [2026-09-02-queen-editor-m140-duzeltme-testler-design.md](../specs/2026-09-02-queen-editor-m140-duzeltme-testler-design.md)
**Dal:** `feat/v6`
**Bu tur yalnız `test_notebook_installs_the_producer_groups.py`'ye dokunur.** Defter ellenmez.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. Üç test yeniden yazılır — `PHOTO_EXTRA` → `PHOTO_MODELS`, ve *"ek"* kelimesi düşer.

```python
def test_every_photo_model_has_a_checkbox_of_its_own():
    """The switch has to sit in CONFIG -- Colab draws #@param only where it is written -- and the row
    saying what to fetch sits in the model cell. Two lists, and a name in one but not the other is
    either a box that downloads nothing or a download nobody can turn off.
    """
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", _cell("# === CONFIG ==="), re.M)
    rows = re.findall(r"^\s*\((PHOTO_\w+),", _cell("PHOTO_MODELS = ["), re.M)

    assert boxes, "CONFIG'de tek bir model kutusu yok"
    assert sorted(boxes) == sorted(rows), f"Kutular {sorted(boxes)}, satırlar {sorted(rows)}"


def test_every_photo_model_comes_switched_off():
    """Every model is the user's pick, the group's own included: photo ticked draws the boxes empty
    and nothing heavy is chosen for anyone.

    The first assertion is not spare: with no PHOTO_* line at all the second holds for free.
    """
    config = _cell("# === CONFIG ===")
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", config, re.M)
    on = re.findall(r"^(PHOTO_\w+) = True  #@param", config, re.M)

    assert boxes, "CONFIG'de tek bir model kutusu yok"
    assert on == [], f"Model açık geliyor: {on}"


def test_an_unticked_photo_model_costs_no_bytes():
    """The rule the three producer boxes already follow, one level down: a row is reached only
    through its own switch."""
    assert "in PHOTO_MODELS if on" in _cell("PHOTO_MODELS = ["), \
        "PHOTO_MODELS satırları kendi anahtarıyla süzülmüyor"
```

## B. Yeni kırmızı — hiç model seçilmemişse defter durur.

```python
def test_choosing_photo_without_a_model_stops_the_notebook():
    """Photo ticked and every model box empty means a renderer with nothing to render with. Asked in
    CONFIG like every other gate: a second here, ten minutes after ComfyUI's install.

    The expected line is built from the boxes rather than written down, so a model added without
    being added to the guard fails here instead of silently reopening the hole.
    """
    config = _cell("# === CONFIG ===")
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", config, re.M)
    guard = "assert not INSTALL_PHOTO or " + " or ".join(boxes)

    assert boxes, "CONFIG'de tek bir model kutusu yok"
    assert guard in config, f"Beklenen kontrol yok:\n{guard}"
```

## C. Disk tabanı taban modeli saymaz.

```python
def test_the_photo_estimate_counts_only_what_the_group_always_takes():
    """The base is the four files the graph's branches read -- the lora, the upscaler, the detector,
    the SAM. The checkpoints are the user's pick, so counting one of them in the base would warn a
    single-model run about disk it is not going to use.
    """
    assert "(INSTALL_PHOTO, PHOTO_GIB," in _cell("SIZES = ["), \
        "SIZES foto için hâlâ sabit bir sayı taşıyor"
    assert "PHOTO_GIB = 2 +" in _cell("PHOTO_GIB ="), \
        "Disk tabanı hâlâ bir checkpoint'in payını taşıyor"
```

## D. İki model de indirilebilir.

```python
def test_the_notebook_offers_both_photo_models():
    """Named rather than derived: this is the one place saying which models the notebook can fetch,
    so a silent edit cannot quietly change what a run is able to install.
    """
    cell = _cell("PHOTO_MODELS = [")

    assert "nova3DCGXL_ilV90.safetensors" in cell, "Taban model artık seçilebilir değil"
    assert "novaOrangeXL_rexV10.safetensors" in cell, "İkinci model listede yok"
    assert "2744564" in cell and "2945776" in cell, "Version id'lerden biri eksik"
```

## E. Bir bekçi düşecek, ve bu doğru.

`test_every_file_the_panel_counts_is_fetched_by_the_notebook` `model_groups.py`'nin saydığı her
dosyanın defterde **anıldığını** arıyor. `nova3DCGXL_ilV90.safetensors` `CIVITAI_PHOTO`'dan
`PHOTO_MODELS`'a taşınıyor ama **defterde kalıyor**, yani bu test yeşil kalmalı. Koşuda
doğrulanacak; düşerse taşıma yanlış yapılmış demektir.

## F. Koşuldu: **5 kırmızı, 728 yeşil.**

Plan altı bekliyordu, koşu beş verdi — **sayı koşuya uyduruluyor, tersi değil.**

| Test | Koşunun söylediği |
|---|---|
| A1 `..._has_a_checkbox_of_its_own` | 🔴 `Kutular ['PHOTO_NOVAORANGE'], satırlar []` |
| A2 `..._comes_switched_off` | 🟢 **beklenmiyordu** — `PHOTO_NOVAORANGE` zaten var ve zaten kapalı, yani iddia bir önceki turda karşılanmıştı |
| A3 `..._costs_no_bytes` | 🔴 `in PHOTO_MODELS if on` yok, hücrenin adı hâlâ `PHOTO_EXTRA` |
| B `..._without_a_model_stops...` | 🔴 beklenen satırı olduğu gibi bastı: `assert not INSTALL_PHOTO or PHOTO_NOVAORANGE` |
| C `..._only_what_the_group_always_takes` | 🔴 `PHOTO_GIB = 8 +` duruyor |
| D `..._offers_both_photo_models` | 🔴 `PHOTO_MODELS` hücresi yok |

A2'nin yeşil kalması iddianın zayıf olduğu anlamına gelmiyor: taban modelin kutusu eklenince o
kutunun da kapalı gelmesini bu test tutuyor, ve o an gerçekten kırılabilir hâle geliyor.

**Bir bekçi düşmedi:** `test_every_file_the_panel_counts_is_fetched_by_the_notebook` yeşil — E'de
yazılan beklenti tuttu, `nova3DCGXL` defterde anılmaya devam ediyor.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil, 7.64 sn.**

**Ve bu, `8a2f88b`'de bırakılan kırmızıyı açıklıyor.** Orada aynı takım 586/587 vermişti, tek
kırmızı 5000 ms'lik bir zaman aşımıydı. Fark ölçüde: o koşularda duvar saati 34 sn ve toplam test
süresi 136-172 sn'ydi; burada 7.64 sn ve 16.9 sn. Aynı kod, on kat fark — yani kırmızıyı yazan
makine yüküydü, ve [vite.config.js](../../../queen-editor/frontend/vite.config.js) yorumunun
1 Eylül'de tarif ettiği şey birebir bu. Testin kendisi hâlâ kırılgan; ölçü artık iki uçtan da var.

## G. Kırmızı commit.

Test dosyası, bu turun iki belgesi, ve yol haritasının düzeltilen kararı.

## Bilerek yapılmayanlar

**Defter ellenmez** — bu turun tamamı testtir.

**`skip` / `xfail` yok.**

**`model_groups.py`, üretici, grafik, ön yüz, `dist`.**

**Panelin yalanı için test yazılmaz** — o davranış bu maddede bilerek taşınıyor, ve olmayan bir
kodun testi olmaz.
