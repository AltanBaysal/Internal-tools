# Madde 330 — H3 videoları Mystic XXX'siz, test turunun planı

> **Koşum:** bu oturumda, satır satır. Commit orkestratörün.

**Hedef:** İki H3 grafiğinin yığınında adı olan tek yuvanın 0.7'de açık Motion Booster olduğunu, üç
kipte de ComfyUI'ye giden yığının Mystic'i adlandırmadığını ve grubun Mystic'i saymadığını söyleyen
testler — kırmızı.

**Yaklaşım:** Grafikler okunuyor, üretici gerçek grafiklerle ve sahte istemciyle koşuyor. Yığının
yuvaları `on`'la süzülmüyor, adlarıyla okunuyor: `"lora"`'sı `"None"` olmayan her yuva sayılıyor.
Üç eski test yeni yığını ve yeni grubu soruyor; defterin Mystic testi yalnız docstring'ini
değiştiriyor *(spec, Değişen)*.

**Araçlar:** pytest (`parametrize`; `tmp_path` yok — gerçek dosyalar okunuyor).

**Spec:** [m330 test turu](../specs/2026-09-24-queen-editor-m330-mystic-kapali-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod, grafik ve defter
  değişmiyor.
- Mystic'in adı her yerde `MysticXXX_MMH3-V4.safetensors`; Motion Booster'ınki
  `H3_Motion_BoosterV2.safetensors`.

---

## Görev 1: Grafikler — Değişen

**Dosya:** Değiştir: `queen-editor/backend/tests/test_workflow_asset.py` —
`test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_half`'ın yerine.

**Arayüz — uygulama turunun vereceği:** iki grafiğin `2678.stack_data`'sında Mystic'in yuvası
`{"on":true,"lora":"None","str":1,"vs":1,"as":1}`; Motion Booster'ın yuvası olduğu gibi.

- [ ] **Adım 1: Test.**

```python
def test_the_h3_graphs_carry_motion_booster_alone_at_seventy():
    """Motion Booster at 0.7 is the user's pick from 213's trial, and since madde 330 the stack's only
    lora: Eros is tried alone, its author having folded Mystic XXX into the checkpoint itself. One
    stack serves all three modes: it takes the model the Director picked for its mode (output 5), and
    REF2VA runs on the I2VA graph (madde 304). A slot is read by its name, not filtered by `on`:
    whether the loader honours `on` is unknown, and "None" is how every empty slot has loaded nothing
    since 213 -- so a lora switched off but still named stays red here. The stack keeps its loras
    inside a JSON string, which the model scan above cannot see into -- so it is read here, and its
    file held to the group."""
    for graph in _h3_graphs():
        stack = graph["2678"]["inputs"]
        assert stack["model"] == ["2730", 5], "Yığın Director'ın kipine göre seçtiği modeli almıyor"
        named = [(slot["lora"], slot["str"], slot["on"]) for slot in json.loads(stack["stack_data"])
                 if slot["lora"] != "None"]
        assert named == [("H3_Motion_BoosterV2.safetensors", 0.7, True)], \
            f"Yığının adı olan yuvaları: {named}"

    assert "H3_Motion_BoosterV2.safetensors" in {row["name"] for row in model_groups.H3_VIDEO}, \
        "Grup yığının LoRA'sını saymıyor"
```

## Görev 2: Üretici — Değişen

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_h3_video_generator.py` —
`test_every_h3_video_is_rendered_with_mystic_xxx_at_half_strength`'in yerine; `every_mode` aynen.

**Arayüz:** `ComfyH3VideoGenerator`'ın imzası değişmiyor; üretici yığına dokunmuyor.

- [ ] **Adım 1: Test.**

```python
@every_mode
def test_no_h3_video_is_rendered_with_mystic_xxx(asked):
    """Madde 330: Eros is tried alone, in every mode. Mystic's file still comes down -- its notebook row
    stays, so turning it back on is a graph edit -- which is why the stack is what is asked: by name,
    on or off, because whether the loader honours `on` is unknown. Only the producer can say what
    REF2VA's render carries: it has no graph of its own (madde 304)."""
    client = FakeClient()

    shipped_generator(client).generate("motion", "", 42, **asked)

    stack = json.loads(client.submitted[STACK_NODE]["inputs"]["stack_data"])
    named = [slot["lora"] for slot in stack if slot["lora"] != "None"]
    assert "MysticXXX_MMH3-V4.safetensors" not in named, f"Yığının adı olan yuvaları: {named}"
```

## Görev 3: Grup — Değişen

**Dosya:** Değiştir: `queen-editor/backend/tests/test_producers.py` — `H3_FILES`'ın son satırı gidiyor.

- [ ] **Adım 1: Liste.**

```python
    ("vae_approx", "taeh3.safetensors"),
    ("loras", "H3_Motion_BoosterV2.safetensors"),
]
```

## Görev 4: Defter — yalnız docstring

**Dosya:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` —
`test_the_notebook_fetches_mystic_xxx_by_its_version_into_the_loras`'ın docstring'i; gövde aynen.

- [ ] **Adım 1: Docstring.**

```python
    """Madde 328: the address is the user's -- Civitai version 3266628, "v4.0 (FL2VA & REF2VA)" -- and
    the file lands in loras/ under the name the lora stack would load it by. Madde 330 took it out of
    the stack and kept this row: the file stays on the disk, so turning it back on is a graph edit
    and no notebook change. A row of CIVITAI_H3, which only an H3 run reaches
    (test_an_unticked_group_costs_no_bytes)."""
```

## Görev 5: Koşu

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi.
- [ ] **Adım 2: Durup dön** — commit orkestratörün: test dosyaları, spec ve bu plan,
  `test(m330): …(red)`.

## Beklenen kırmızı

`queen-editor` pytest'inde altı test, hepsi Mystic hâlâ yığında ve grupta olduğu için:

- Görev 1: `test_the_h3_graphs_carry_motion_booster_alone_at_seventy` *(Mystic 0.5'te adıyla yığında)*.
- Görev 2: `test_no_h3_video_is_rendered_with_mystic_xxx`'in üç kipi *(Mystic gidiyor)*.
- Görev 3: `test_the_h3_group_names_its_files_the_way_the_graph_loads_them` *(grup Mystic'i sayıyor)*,
  `test_a_machine_with_h3_on_it_has_a_video_producer` *(disk Mystic'siz, grup onu arıyor)*.

Görev 4 yeşil. Başka hiçbir test kıpırdamaz; öteki üç satır yeşil.
