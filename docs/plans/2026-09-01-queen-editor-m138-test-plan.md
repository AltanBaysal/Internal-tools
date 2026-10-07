# Madde 138 · Tur 1 (test) — Plan

**Tasarım:** [2026-09-01-queen-editor-m138-break-testler-design.md](../specs/2026-09-01-queen-editor-m138-break-testler-design.md)
**Dal:** `feat/v6`
**Bu tur yalnız test dosyalarına dokunur.** Grafik ve defter uygulama turunun işi.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## 0. Sınıf adı testte tek bir yerde durur.

`test_workflow_asset.py`'nin başına modül sabiti:

```python
BREAK_ENCODER = "CLIPTextEncodeBREAK"
```

Adın kaynağı düğümün kendi `NODE_DISPLAY_NAME_MAPPINGS` anahtarı; okunarak yazıldı, çalıştırılarak
değil. Sabit olarak durmasının sebebi uygulama turu: Colab'da gerçek ad farklı çıkarsa **tek satır**
düzelir, iddianın şekli değişmez. İki teste birden yazılsaydı düzeltme iki yerde aranırdı.

## A. `test_workflow_asset.py`: bir kırmızı, iki bekçi.

Dosya grafiği zaten `config.WORKFLOW_PATH`'ten okuyor ve `json.load` ediyor; yeni yardımcı yok.

**Kırmızı — maddenin kendisi:**

```python
def test_the_positive_encoder_understands_break():
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert workflow["36"]["class_type"] == BREAK_ENCODER
```

**Bekçi, yeşil kalmalı — negatif yol dokunulmuyor:**

```python
def test_the_negative_path_keeps_the_plain_encoder():
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert workflow["38"]["class_type"] == "CLIPTextEncode"
```

**Bekçi, yeşil kalmalı — zincir kablosuyla çivileniyor:**

```python
def test_the_prompt_reaches_the_encoder_through_the_chain():
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert workflow["39"]["inputs"]["string"][0] == "3"
    assert workflow["36"]["inputs"]["text"][0] == "39"
    assert "clip" in workflow["36"]["inputs"]
```

Üçüncüsü adaptörün yazdığı düğümden kodlayıcıya kadar olan yolu tutuyor: sınıf değişirken kablolar
düşerse, ya da `39` aradan çıkarılırsa kırmızı verir.

## B. `test_notebook_installs_the_producer_groups.py`: bir kırmızı, bir bekçi.

Dosyanın `_source()` ve `_cell()` yardımcıları var ve ikisi de yeterli; dokunulmuyor.

**Kırmızı — defter grafiğin istediği düğümü kurmalı:**

```python
def test_the_notebook_installs_the_encoder_the_graph_asks_for():
    assert "pamparamm/ComfyUI-ppm" in _source()
```

**Bekçi, bugün yeşil — sayı iki yerde yazılı, ikisi birlikte hareket etmeli:**

```python
def test_the_notebook_says_how_many_custom_nodes_it_installs():
    listed = _cell("CUSTOM_NODES = [").count('.git"),')
    heading = _cell("## ComfyUI + Custom Node")
    assert listed, "CUSTOM_NODES listesi okunamadı"
    assert f"({listed})" in heading, f"Başlıktaki sayı listeyle uyuşmuyor: {listed} satır"
```

Sayı teste **yazılmıyor**, listeden okunuyor — bugün 19, uygulama turunda 20 olacak ve başlık
güncellenmezse test o gün kırmızı verecek. Bekçinin bütün amacı bu.

## C. Koşuldu: **2 kırmızı, 724 yeşil.**

`python -m pytest queen-editor -q` — planlanan ikisi, ve yalnız onlar. İkisi de gerçek
`AssertionError`, yani ikisi de bir adın yokluğunu değil bir olgunun yanlışlığını gösteriyor:

- `test_the_positive_encoder_understands_break` — `assert 'CLIPTextEncode' == 'CLIPTextEncodeBREAK'`.
  Maddenin cümlesi, grafiğin kendi diliyle.
- `test_the_notebook_installs_the_encoder_the_graph_asks_for` — defter kaynağında paket geçmiyor.

**Üç bekçi de yeşil:** `test_the_negative_path_keeps_the_plain_encoder`,
`test_the_prompt_reaches_the_encoder_through_the_chain`, ve
`test_the_notebook_says_how_many_custom_nodes_it_installs` — sonuncusu bugünkü 19'u listeden okuyup
başlıkta buldu, yani sayaç çalışıyor ve uygulama turunda 20'yi bekleyecek.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.** Madde ön yüze dokunmuyor;
koşulmasının sebebi CLAUDE.md'nin *"her ikisi de, harfiyen"* kuralı. *(m137'nin planındaki "Node
kurulu değil" notu artık geçerli değil — komut bu makinede koştu.)*

## D. Kırmızı commit.

Test dosyaları ve bu turun iki belgesi.

## Bilerek yapılmayanlar

**`workflow_api.json` ve `queeneditor.ipynb` ellenmiyor.** İkisi de uygulama turunda, ve
[tasarımın](../specs/2026-09-01-queen-editor-m138-break-testler-design.md) kuralı gereği **aynı
commit'te** — ComfyUI kurulmamış bir düğümü isteyen grafiği reddediyor.

**`skip` / `xfail` yok.**

**Adaptör, `model_groups.py`, ön yüz, `dist` ellenmiyor.**

**Davranış testi yok.** `BREAK`'in gerçekten böldüğünü hiçbir birim testi söyleyemez; kanıt Colab'da,
aynı seed ile iki üretimin karşılaştırılması. Protokol uygulama turunun spec'inde yazılacak.
