# Madde 328 — Mystic XXX LoRA'sı, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Mystic XXX'in iki H3 grafiğinin yığınında 1'de durduğunu, üç kipte de ComfyUI'ye
gittiğini, panelin onu saydığını, defterin onu H3'le kendi sürümünden indirdiğini ve aynasız listede
olduğunu söyleyen testler — kırmızı.

**Yaklaşım:** Grafikler ve defter okunuyor, üretici gerçek grafiklerle ve sahte istemciyle koşuyor,
liste modülden okunuyor. İki eski test yeni yığını ve yeni grubu soruyor *(Değişen)*. Beklenen ad beş
yerde aynı dize: `MysticXXX_MMH3-V4.safetensors`.

**Araçlar:** pytest (`parametrize`, `tmp_path` yok — gerçek dosyalar okunuyor).

**Spec:** [m328 test turu](../specs/2026-09-24-queen-editor-m328-mystic-lora-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod, grafik ve defter
  değişmiyor.

---

## Görev 1: Grafikler — Değişen

**Dosya:** Değiştir: `queen-editor/backend/tests/test_workflow_asset.py` —
`test_the_h3_graphs_carry_motion_booster_alone_at_seventy`'nin yerine.

**Arayüz — uygulama turunun vereceği:** iki grafiğin `2678.stack_data`'sında açık bir yuva,
`"lora": "MysticXXX_MMH3-V4.safetensors"`, `"str": 1`; `model_groups.H3_VIDEO`'da
`{"folder": "loras", "name": "MysticXXX_MMH3-V4.safetensors"}`.

- [ ] **Adım 1: Test.**

```python
def test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_one():
    """Motion Booster at 0.7 is the user's pick from 213's trial; Mystic XXX at full strength is madde
    328's, for every H3 video of the session. One stack serves all three modes: it takes the model
    the Director picked for its mode (output 5), and REF2VA runs on the I2VA graph (madde 304) -- that
    wire is why the lora needed no new export. The stack keeps its loras inside a JSON string, which
    the model scan above cannot see into -- so it is read here, and its files held to the group.
    Sorted: what is asked is what the stack loads, not which slot holds it."""
    expected = [("H3_Motion_BoosterV2.safetensors", 0.7), ("MysticXXX_MMH3-V4.safetensors", 1)]

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

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_h3_video_generator.py` — başa
`from backend import config`, sona test.

**Arayüz:** `ComfyH3VideoGenerator(client, workflow_path, first_last_path, timeout)` ve `generate`'in
imzası değişmiyor; üretici yığına dokunmuyor.

- [ ] **Adım 1: Test.**

```python
# The graph's own lora stack; the producer never touches it -- loras are baked into the exports.
STACK_NODE = "2678"


def shipped_generator(client):
    """The producer over the graphs that ship rather than the test's own: the stack is theirs."""
    from backend.features.photo_generation.data.comfy_h3_video_generator import (
        ComfyH3VideoGenerator,
    )
    return ComfyH3VideoGenerator(client, config.H3_VIDEO_WORKFLOW_PATH,
                                 config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH, timeout=60)


@pytest.mark.parametrize("asked", [
    {"source": ("P0_0.png", b"PNG")},
    {"source": ("P0_0.png", b"PNG"), "end": ("P1_0.png", b"END")},
    {"references": POOL},
], ids=["i2va", "fl2va", "ref2va"])
def test_every_h3_video_is_rendered_with_mystic_xxx_at_full_strength(asked):
    """Every H3 video of the session, Kareden's two graphs and Referanstan alike (madde 328). The graph
    test reads the files; this reads what reaches ComfyUI -- REF2VA has no graph of its own and runs
    on the I2VA export with its mode changed (madde 304), so only the producer can say its render
    carries the stack."""
    client = FakeClient()

    shipped_generator(client).generate("motion", "", 42, **asked)

    stack = json.loads(client.submitted[STACK_NODE]["inputs"]["stack_data"])
    loaded = {slot["lora"]: slot["str"] for slot in stack if slot["on"] and slot["lora"] != "None"}
    assert loaded.get("MysticXXX_MMH3-V4.safetensors") == 1, f"Yığın bunları yüklüyor: {loaded}"
```

## Görev 3: Defter

**Dosya:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` —
`test_the_notebook_fetches_the_h3_checkpoint_and_lora_by_their_versions`'ın ardına.

**Arayüz:** `CIVITAI_H3`'te `(3266628, LORA, "MysticXXX_MMH3-V4.safetensors", <etiket>)`.

- [ ] **Adım 1: Test.**

```python
def test_the_notebook_fetches_mystic_xxx_by_its_version_into_the_loras():
    """Madde 328: the address is the user's -- Civitai version 3266628, "v4.0 (FL2VA & REF2VA)" -- and
    the name is the one the lora stack loads from loras/. A row of CIVITAI_H3, which only an H3 run
    reaches (test_an_unticked_group_costs_no_bytes)."""
    cell = _cell("CIVITAI_H3 = [")
    listing = cell[cell.find("CIVITAI_H3 = ["):]
    listing = listing[:listing.find("\n]")]

    assert re.search(r'\(3266628,\s*LORA,\s*"MysticXXX_MMH3-V4\.safetensors",', listing), \
        f"CIVITAI_H3'te Mystic XXX satırı yok:\n{listing}"
```

## Görev 4: Aynasız liste

**Dosya:** Değiştir: `queen-editor/backend/tests/test_colab_downloads.py` — sonuna.

**Arayüz:** `colab.downloads.MIRRORLESS`, 327'nin kümesi.

- [ ] **Adım 1: Test.**

```python
def test_mystic_xxx_is_kept_out_of_the_mirror(downloads):
    """Madde 328, the list's first entry: the lora is on trial ("şimdilik hugging face gitmesin, önce
    test edeyim"). What the list does is asked by 327's tests above; this asks that the file is on it,
    under the name the notebook downloads it by."""
    assert "MysticXXX_MMH3-V4.safetensors" in downloads.MIRRORLESS, \
        f"Mystic XXX aynasız listede değil: {downloads.MIRRORLESS}"
```

## Görev 5: Grup — Değişen

**Dosya:** Değiştir: `queen-editor/backend/tests/test_producers.py` — `H3_FILES`'ın sonuna.

- [ ] **Adım 1: Satır.**

```python
    ("loras", "H3_Motion_BoosterV2.safetensors"),
    ("loras", "MysticXXX_MMH3-V4.safetensors"),
]
```

## Görev 6: Koşu

- [ ] **Adım 1: Dört satırı koş.**
- [ ] **Adım 2: Durup dön** — commit orkestratörün: test dosyaları, spec ve bu plan,
  `test(m328): …(red)`.

## Beklenen kırmızı

`queen-editor` pytest'inde yedi test, hepsi Mystic XXX henüz hiçbir yerde olmadığı için:
Görev 1 *(yığın yalnız Motion Booster'ı yüklüyor)*, Görev 2'nin üç kipi *(yığında Mystic yok —
`loaded.get(...)` `None`)*, Görev 3 *(satır yok)*, Görev 4 *(liste boş)*, Görev 5'in
`test_the_h3_group_names_its_files_the_way_the_graph_loads_them`'i *(grupta satır yok)*. Başka hiçbir
test kıpırdamaz; öteki üç satır yeşil.
