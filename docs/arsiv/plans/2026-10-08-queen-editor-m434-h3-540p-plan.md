# Madde 434 — H3 videosu 540p'de, plan

> **Koşum:** bu oturumda, ana klasörde, satır satır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** İki H3 grafiğinin Director'ı 576 × 864'te ve timeline'ı `540p`'de; oran `auto` kalır.

**Yaklaşım:** Önce test: bugünkü 512 × 768 sabitlemesi 576 × 864'ü ve timeline'ın `540p`'sini sorar,
ve kırmızı görülür. Sonra iki grafikte iki girdi ve timeline'ın bir alanı değişir.

**Araçlar:** pytest.

**Spec:** [m434](../specs/2026-10-08-queen-editor-m434-h3-540p-design.md)

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, ve yalnız bugün doğru olanı söyler.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Yalnız iki H3 grafiği ve `test_workflow_asset.py` değişir; `comfy_h3_video_generator.py`'ye,
  frontend'e, `dist`'e ve yol haritasına dokunulmaz.

---

## Görev 1: Kırmızı test — `queen-editor/backend/tests/test_workflow_asset.py`

- [ ] **`test_both_h3_graphs_render_four_seconds_at_512_by_768` yerine:**

```python
def test_both_h3_graphs_render_four_seconds_at_576_by_864():
    """Madde 434: 540p, up from 480p's 512 x 768. 576 x 864 is not the Director panel's 540p size --
    the panel rounds each side to its 32px grid on its own and gets 576 x 896 for 2:3, 3.6% off the
    photo -- but exact 2:3 with both sides on that grid, the user's pick over the panel's ("bu
    olsun"). The aspect stays auto, so the video follows the photo: a photo of another shape came
    out stretched in an earlier trial.

    One number is quoted for every video, and one export joins both kinds -- two lengths or two
    sizes there would be a lie and a broken file."""
    for graph in _h3_graphs():
        director = graph["2730"]["inputs"]
        assert (director["duration"], director["width"], director["height"]) == (4, 576, 864)
        resolution = json.loads(director["timeline_data"])["resolution"]
        assert (resolution["aspect"], resolution["resolution"]) == ("auto", "540p")
```

- [ ] **`python -m pytest queen-editor -q`** — yalnız bu test kırmızı: `(4, 512, 768) != (4, 576, 864)`.
  Şekil testi yeşil kalır.

## Görev 2: `queen-editor/assets/workflow_video_h3_api.json`

- [ ] **`"2730"`'nin girdilerinde:** `"width": 512` → `"width": 576`, `"height": 768` →
  `"height": 864`.
- [ ] **`timeline_data`'nın içinde:** `\"resolution\":\"480p\"` → `\"resolution\":\"540p\"`. Dizenin
  geri kalanı — `aspect`, `input_scaling`, `custom_*`, `source_width/height` — olduğu gibi.

## Görev 3: `queen-editor/assets/workflow_video_h3_first_last_api.json`

- [ ] Görev 2'nin aynısı.

## Görev 4: Koş

- [ ] **Dört satır, paralel, olduğu gibi, depo kökünden.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil, ve sayılar değişmez — test yeniden adlandırıldı, eklenmedi.

## Görev 5: Commit — ana ajanın, kullanıcının Colab denemesinden sonra

- [ ] Spec, plan, test ve iki grafik. Mesajda çift tırnak yok; son satır
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
