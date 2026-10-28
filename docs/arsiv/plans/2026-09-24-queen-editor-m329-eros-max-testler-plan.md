# Madde 329 — Eros Max beta5 ve yarı güçte Mystic XXX, test turunun planı

> **Koşum:** bu oturumda, satır satır. Commit orkestratörün.

**Hedef:** İki H3 grafiğinin bütün model düğümlerinin Eros'u yüklediğini, üç kipte de ComfyUI'ye
Eros'un ve 0.5'te Mystic'in gittiğini, defterin Eros'u `HF_H3`'ten `H3DIFF`'e indirdiğini, DaSiWa'nın
defterden ve gruptan çıktığını söyleyen testler — kırmızı.

**Yaklaşım:** Grafikler ve defter okunuyor, üretici gerçek grafiklerle ve sahte istemciyle koşuyor.
Model düğümleri sınıflarıyla *(`UNETLoader`)* bulunuyor, id'leriyle değil. Dört eski test yeni gücü, yeni
modeli ve yeni grubu soruyor *(spec, Değişen)*. Beklenen ad dört dosyada aynı dize:
`10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`, grafikte ve grupta `MiniMaxH3/` önekiyle.

**Araçlar:** pytest (`parametrize`; `tmp_path` yok — gerçek dosyalar okunuyor).

**Spec:** [m329 test turu](../specs/2026-09-24-queen-editor-m329-eros-max-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod, grafik ve defter
  değişmiyor.
- Eros'un adı: `MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors` grafikte ve grupta;
  defterde `MiniMaxH3/`'süz, çünkü klasörü `H3DIFF` veriyor.

---

## Görev 1: Grafikler

**Dosya:** Değiştir: `queen-editor/backend/tests/test_workflow_asset.py` —
`test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_one`'ın yerine iki test.

**Arayüz — uygulama turunun vereceği:** iki grafiğin iki `UNETLoader`'ı da
`"unet_name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"`, `"weight_dtype": "default"`;
`2678.stack_data`'da Mystic'in yuvası `"str": 0.5`.

- [ ] **Adım 1: Yeni test, `test_every_model_the_h3_graphs_load_is_in_the_h3_group`'un ardına.**

```python
def test_both_h3_graphs_load_eros_max_beta5():
    """Madde 329: the checkpoint the user's liked example was made with, tried after Mystic XXX over
    DaSiWa disappointed. Each graph has two model loaders -- the Director takes one as its FL2VA model
    and the other as its REF2VA model, and picks by mode -- so every loader is asked, found by its
    class rather than its id: what is asked is which model the graph loads, and a third loader would
    slip past a test naming two ids. Whether the group counts the file is the scan's question above:
    unet_name is a plain input it sees."""
    expected = {("MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", "default")}

    for graph in _h3_graphs():
        loaded = {(node["inputs"]["unet_name"], node["inputs"]["weight_dtype"])
                  for node in graph.values() if node["class_type"] == "UNETLoader"}
        assert loaded == expected, f"Grafiğin model düğümleri bunları yüklüyor: {loaded}"
```

- [ ] **Adım 2: Değişen test.**

```python
def test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_half():
    """Motion Booster at 0.7 is the user's pick from 213's trial. Mystic XXX came with madde 328 and
    sits at half strength under Eros (madde 329): Eros's author folded Mystic into the checkpoint
    itself, so full strength would lay it on twice. One stack serves all three modes: it takes the
    model the Director picked for its mode (output 5), and REF2VA runs on the I2VA graph (madde 304)
    -- that wire is why the lora needed no new export. The stack keeps its loras inside a JSON string,
    which the model scan above cannot see into -- so it is read here, and its files held to the
    group. Sorted: what is asked is what the stack loads, not which slot holds it."""
    expected = [("H3_Motion_BoosterV2.safetensors", 0.7), ("MysticXXX_MMH3-V4.safetensors", 0.5)]

    for graph in _h3_graphs():
        stack = graph["2678"]["inputs"]
        assert stack["model"] == ["2730", 5], "Yığın Director'ın kipine göre seçtiği modeli almıyor"
        loaded = sorted((slot["lora"], slot["str"]) for slot in json.loads(stack["stack_data"])
                        if slot["on"] and slot["lora"] != "None")
        assert loaded == expected, f"Yığın bunları yüklüyor: {loaded}"

    listed = {row["name"] for row in model_groups.H3_VIDEO}
    missing = [name for name, _strength in expected if name not in listed]
    assert missing == [], f"Grup yığının bu LoRA'larını saymıyor: {missing}"
```

## Görev 2: Üretici — ComfyUI'ye giden grafik

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_h3_video_generator.py` — sondaki Mystic
testinin yerine bir kip listesi ve iki test.

**Arayüz:** `ComfyH3VideoGenerator(client, workflow_path, first_last_path, timeout)` ve `generate`'in
imzası değişmiyor; üretici model düğümlerine ve yığına dokunmuyor.

- [ ] **Adım 1: Üç kip bir kez yazılıyor, iki test onu kullanıyor.**

```python
# Kareden's two graphs and Referanstan: every H3 video of the session.
every_mode = pytest.mark.parametrize("asked", [
    {"source": ("P0_0.png", b"PNG")},
    {"source": ("P0_0.png", b"PNG"), "end": ("P1_0.png", b"END")},
    {"references": POOL},
], ids=["i2va", "fl2va", "ref2va"])


@every_mode
def test_every_h3_video_is_rendered_with_eros_max_beta5(asked):
    """Madde 329. The Director picks one of the graph's two model loaders by its mode, so what reaches
    ComfyUI is asked of every loader it is sent -- and REF2VA has no graph of its own and runs on the
    I2VA export with its mode changed (madde 304), so only the producer can say which model its
    render loads."""
    client = FakeClient()

    shipped_generator(client).generate("motion", "", 42, **asked)

    loaded = {node["inputs"]["unet_name"] for node in client.submitted.values()
              if node["class_type"] == "UNETLoader"}
    assert loaded == {"MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"}, \
        f"ComfyUI'ye giden model düğümleri bunları yüklüyor: {loaded}"


@every_mode
def test_every_h3_video_is_rendered_with_mystic_xxx_at_half_strength(asked):
    """Every H3 video of the session carries Mystic XXX (madde 328), at half strength under Eros
    (madde 329). The graph test reads the files; this reads what reaches ComfyUI -- only the producer
    can say REF2VA's render carries the stack."""
    client = FakeClient()

    shipped_generator(client).generate("motion", "", 42, **asked)

    stack = json.loads(client.submitted[STACK_NODE]["inputs"]["stack_data"])
    loaded = {slot["lora"]: slot["str"] for slot in stack if slot["on"] and slot["lora"] != "None"}
    assert loaded.get("MysticXXX_MMH3-V4.safetensors") == 0.5, f"Yığın bunları yüklüyor: {loaded}"
```

## Görev 3: Defter

**Dosya:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` —
`test_the_notebook_fetches_the_h3_checkpoint_and_lora_by_their_versions`'ın yerine üç test.

**Arayüz:** `HF_H3`'te `("TenStrip/10Eros-Max", "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors",
H3DIFF, "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", <etiket>, <taban>)`; `CIVITAI_H3`'te
DaSiWa'nın satırı yok.

- [ ] **Adım 1: Değişen test.**

```python
def test_the_notebook_fetches_motion_booster_by_its_version():
    """Named rather than derived, like the photo checkpoints: the one lora the user kept from 213's
    trial."""
    assert "3228867" in _cell("CIVITAI_H3 = ["), "Civitai version id defterde yok: 3228867"
```

- [ ] **Adım 2: Eros'un satırı.**

```python
def test_the_notebook_fetches_eros_max_from_its_author_s_repo_into_the_h3_diffusion_models():
    """Madde 329: the file the author says to use by default (TURBO-hybrid int8), from the Hugging
    Face repo the Civitai page points at -- Civitai's own version link hands out a different, w4a8
    file. A row of HF_H3: only an H3 run reaches it (test_an_unticked_group_costs_no_bytes), and
    hf_fetch uploads nothing, so the file never touches the mirror. H3DIFF is where the graph's
    MiniMaxH3/ prefix looks."""
    cell = _cell("HF_H3 = [")
    listing = cell[cell.find("HF_H3 = ["):]
    listing = listing[:listing.find("\n]")]

    assert re.search(r'\(\s*"TenStrip/10Eros-Max",'
                     r'\s*"10Eros_Max_h3_TURBO-hybrid_beta5_int8\.safetensors",'
                     r'\s*H3DIFF,\s*"10Eros_Max_h3_TURBO-hybrid_beta5_int8\.safetensors",',
                     listing), f"HF_H3'te Eros satırı yok:\n{listing}"
```

- [ ] **Adım 3: DaSiWa'dan iz kalmıyor.**

```python
def test_the_retired_dasiwa_h3_checkpoint_is_gone_from_the_notebook():
    """Eros took its place (madde 329). A row left behind would still bring ~21 GB down on every H3
    run, for a file no graph loads."""
    source = _source()

    for leftover in ("dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_"
                     "row-wise_convrot_runtime_mixed.safetensors", "3314686"):
        assert leftover not in source, f"Defterde DaSiWa H3'ten iz kaldı: {leftover}"
```

## Görev 4: Grup — Değişen

**Dosya:** Değiştir: `queen-editor/backend/tests/test_producers.py` — `H3_FILES`'ın ilk satırı.

- [ ] **Adım 1: Satır.**

```python
H3_FILES = [
    ("diffusion_models", "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"),
    ("text_encoders", "qwen3vl_32b_minimax_h3_int4_convrot.safetensors"),
```

## Görev 5: Koşu

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi.
- [ ] **Adım 2: Durup dön** — commit orkestratörün: test dosyaları, spec ve bu plan,
  `test(m329): …(red)`.

## Beklenen kırmızı

`queen-editor` pytest'inde on iki test, hepsi Eros henüz hiçbir yerde olmadığı, DaSiWa her yerde
durduğu ve Mystic 1'de olduğu için:

- Görev 1: `test_both_h3_graphs_load_eros_max_beta5` *(dört düğüm de DaSiWa)*,
  `…_mystic_xxx_at_half` *(Mystic 1'de)*.
- Görev 2: Eros testinin üç kipi *(DaSiWa gidiyor)*, Mystic testinin üç kipi *(1 gidiyor)*.
- Görev 3: Eros satırı *(yok)*, DaSiWa'nın izi *(ad da sürüm de defterde)*. Değişen Motion Booster
  testi yeşil.
- Görev 4: `test_the_h3_group_names_its_files_the_way_the_graph_loads_them` *(grup DaSiWa'yı sayıyor)*,
  `test_a_machine_with_h3_on_it_has_a_video_producer` *(disk Eros'u tutuyor, grup DaSiWa'yı arıyor)*.

Başka hiçbir test kıpırdamaz; öteki üç satır yeşil.
