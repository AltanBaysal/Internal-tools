# Madde 143 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-02-queen-editor-m143-panel-testler-design.md](2026-09-02-queen-editor-m143-panel-testler-design.md)
**Kırmızı commit:** `9d370be` — 4 kırmızı, 732 yeşil; ön yüz 28 dosya / 587 yeşil.
**Dal:** `feat/v6`

## Ne yeşile dönecek

Dört test: grubun şekli, ve `list_producers`'ın yeni satırı okuyabilmesinin üç hâli *(seçilen model
sayılır / boş klasör sayılmaz / yarım indirme sayılmaz)*.

## Dört dosya, dördü de küçük

### 1. `model_groups.py` — checkpoint satırı türünü söyler

```python
{"folder": "checkpoints", "suffix": ".safetensors"},
```

adının yerine. Yorumu neden'i taşıyor: hangi modelin makinede olduğu Madde 140'tan beri
kullanıcının seçimi, ve grafik kendisine verilen neyse onunla üretiyor.

Modülün başlığı da düzeliyor — *"hangi dosya"* değil artık, *"hangi dosya ya da hangi tür dosya"*.

### 2. `ports.py` — port ikinci soruyu kazanır

```python
def has_any(self, folder: str, suffix: str) -> bool:
    """Is there a file of this kind here? The question a group asks when which one is the
    user's pick."""
```

Portun bir sorusu vardı, ikisi oluyor. Üçüncüsü olmuyor: yazma, indirme, silme hâlâ yok
*(FOUNDATION 9)*.

### 3. `list_producers.py` — satırın şekline bakar

```python
installed = bool(group) and all(
    files.exists(spec["folder"], spec["name"]) if "name" in spec
    else files.has_any(spec["folder"], spec["suffix"])
    for spec in group)
```

`"name" in spec` satırın hangi soruyu sorduğunu söylüyor. Ayrı bir alan — `kind: "any"` gibi —
aynı şeyi ikinci kez yazmak olurdu: adın yokluğu zaten bunu söylüyor.

### 4. `comfy_models.py` — gerçek dosya sistemi

```python
def has_any(self, folder, suffix):
    directory = os.path.join(self._root, "models", folder)
    try:
        return any(entry.name.endswith(suffix) and entry.is_file()
                   for entry in os.scandir(directory))
    except FileNotFoundError:
        return False
```

`os.scandir`, `os.listdir` değil: klasörde yüzlerce dosya olsa bile ilk uyanı bulunca duruyor, ve
`is_file()` girişin kendisinden okunuyor — ikinci bir `stat` çağrısı yok.

**`FileNotFoundError` sessizce `False`:** defter klasörleri açılışta yaratıyor ama uygulama hiç
kurulum yapılmamış bir makinede de kalkabiliyor, ve *"klasör yok"* ile *"klasör boş"* panel için
aynı cevap — kurulu değil.

## Ne değişmiyor

- **Video ve ses grupları.** İkisinde de her dosya adıyla yükleniyor.
- **`audio_weights`** — `GROUPS["audio"][0]`'ı okuyup adıyla yol kuruyor, ve o satır adlı kalıyor.
- **Panelin çizimi, rotalar, ön yüz, `dist`.** Cevap değişiyor, şekli değil: `installed` hâlâ bir
  `bool`.
- **Defter.** Bu madde uygulamanın defteri yakalaması.

## Sonuç: panel artık doğru

| Kullanıcının seçimi | Bugün | Bu maddeden sonra |
|---|---|---|
| yalnız nova3DCG | kurulu | kurulu |
| yalnız novaOrange | **kurulu değil** *(yalan)* | kurulu |
| üçü birden | **kurulu değil** *(yalan)* | kurulu |
| hiçbiri | kurulu değil | kurulu değil |

Üçüncü satır bugünkü hatanın en görünür hâli: **her modeli indiren kullanıcı bile** panelde
"kurulu değil" görüyordu, çünkü aranan dosya adı değil, aranan *o* dosya adıydı.

Defterin bu davranışı anlatan uyarı notu da kalkıyor — artık doğru olmayan bir uyarı.

## Colab'da görülecek

Foto kutusu ve **yalnız** `PHOTO_NOVAORANGE` işaretli bir koşu: **Üreticiler** panelinde
*"Fotoğraf üreticisi — kurulu"*. Bugün orada "kurulu değil" yazıyor.
