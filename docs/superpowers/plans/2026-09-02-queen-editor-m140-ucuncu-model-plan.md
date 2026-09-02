# Madde 140 · Üçüncü model — Plan

**Tasarım:** [2026-09-02-queen-editor-m140-ucuncu-model-design.md](../specs/2026-09-02-queen-editor-m140-ucuncu-model-design.md)
**Dal:** `feat/v6`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

---

## Tur 1 — test

### A. Tek iddia, adıyla birlikte düzeliyor.

`test_the_notebook_offers_both_photo_models` → `test_the_notebook_offers_every_photo_model`:

```python
def test_the_notebook_offers_every_photo_model():
    """Named rather than derived: this is the one place saying which models the notebook can fetch,
    so a silent edit cannot quietly change what a run is able to install. Reading the list itself
    would only say that the list contains what it contains.
    """
    cell = _cell("PHOTO_MODELS = [")

    for name in ("nova3DCGXL_ilV90.safetensors", "novaOrangeXL_rexV10.safetensors",
                 "novaAnimeXL_ilV190.safetensors"):
        assert name in cell, f"Defter bu modeli indirmiyor: {name}"
    for version in ("2744564", "2945776", "2940478"):
        assert version in cell, f"Civitai version id defterde yok: {version}"
```

Eski adı silinir; iki isimden birini yaşatmak hangisinin geçerli olduğunu soru hâline getirirdi.

### B. Koşuldu: **1 kırmızı, 732 yeşil.**

`python -m pytest queen-editor -q` — tek kırmızı, ve mesajı adını söylüyor:
`Defter bu modeli indirmiyor: novaAnimeXL_ilV190.safetensors`.

Üç bekçi *(eşleşme, kapalı gelme, kontrol)* yeşil kaldı — defter henüz değişmedi, yani ikili
hâliyle hâlâ tutarlı. Kırmızı olan tek şey defterin üçüncü modeli **bilmemesi**, ki bu turun
iddiası da tam olarak o.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.**

### C. Kırmızı commit.

Test dosyası, bu turun iki belgesi, ve yol haritasının güncellenmiş kararı.

---

## Tur 2 — uygulama

### D. CONFIG — kutu ve kontrol.

Kutu, ötekilerin altına *(hizalama yok: desen `=` öncesinde tam bir boşluk istiyor)*:

```python
PHOTO_NOVAANIME = False  #@param {type:"boolean"}
```

Kontrol, kutu sırasıyla:

```python
assert not INSTALL_PHOTO or PHOTO_NOVA3DCG or PHOTO_NOVAORANGE or PHOTO_NOVAANIME, (
```

**Sıra önemli:** test beklediği satırı `re.findall`'ın döndürdüğü **belge sırasıyla** kuruyor, yani
kutuların CONFIG'deki sırası ile kontroldeki sıra aynı olmak zorunda.

### E. İndirme hücresi — satır.

`PHOTO_MODELS`'ın sonuna:

```python
    (PHOTO_NOVAANIME, 7, 2940478, "novaAnimeXL_ilV190.safetensors", "Nova Anime XL IL v19.0"),
```

Başka hiçbir şey değişmiyor: `CIVITAI_PHOTO`'nun eklemesi ve `PHOTO_GIB`'in toplamı zaten liste
üstünden çalışıyor.

### F. Metin — boyut cümleleri.

Giriş hücresindeki ve CONFIG yorumundaki *"her biri ~7 GiB"* doğru kalıyor; değişen, üçünü birden
seçenin ne ödediği. Modeller başlığındaki `~2+7n` de doğru kalıyor.

Defterin *"Foto modeli eklemek"* notu üç yeri sayıyor — satır, kutu, kontrol — ve bu ekleme tam
olarak o üçünü yapıyor, yani not doğrulanmış oluyor.

### G. Koşulur, **sayı koşudan alınır.** Yeşil commit.

`queeneditor.ipynb` ve bu turun belgeleri. `dist` derlenmiyor: ön yüz değişmiyor.

---

## Bilerek yapılmayanlar

**`model_groups.py`, üretici, grafik, ön yüz, `dist`.**

**Panelin yalanı** — `nova3DCG` kutusu boşken panel *"kurulu değil"* diyor. Taşınıyor, kendi
maddesi.

**`skip` / `xfail` yok.**
