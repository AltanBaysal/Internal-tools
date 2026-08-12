# Görev 2 — Model listesi grafiğin istediğini söyler · Uygulama planı

> **Ajanlar için:** GEREKLİ ALT BECERİ: bu planı superpowers:executing-plans ile uygula.

**Amaç:** Video model grubunu grafiğin gerçekten yüklediği dosyalara eşitlemek ve bu eşitliği
testle tutmak.

**Tasarım:** [spec](../specs/2026-08-13-queen-editor-v6-gorev-2-model-listesi-design.md)

## Genel kısıtlar

- Ad grafiğin dediği, URL kaynağın kendi adresi — ikisi ayrı alan, öyle kalır.
- Civitai'nin token'ı arkasındaki dosyalar `url: None`.
- Test: `python -m pytest queen-editor -q`. Ön yüz değişmiyor.

---

### Task 1: Graf ile grubun tutarlılığı

**Dosyalar:**
- Değiştir: `queen-editor/backend/tests/test_workflow_asset.py`,
  `queen-editor/backend/features/producers/domain/model_groups.py`

- [ ] **Adım 1: Düşen testi yaz**

```python
def _model_files(node):
    """Every .safetensors named anywhere in the graph, nested widgets included -- Power Lora
    Loader keeps its loras inside dicts, so a flat scan would miss half of them."""
    if isinstance(node, str):
        return {node} if node.endswith(".safetensors") else set()
    if isinstance(node, dict):
        return set().union(*(_model_files(v) for v in node.values()), set())
    if isinstance(node, list):
        return set().union(*(_model_files(v) for v in node), set())
    return set()


def test_every_model_the_video_graph_loads_is_in_the_video_group():
    with open(config.VIDEO_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    listed = {row["name"] for row in GROUPS["video"]}
    missing = sorted(_model_files(workflow) - listed)
    assert not missing, f"Graf bu dosyaları yüklüyor ama grup saymıyor: {missing}"
```

- [ ] **Adım 2: Koş, düştüğünü gör** — üç ad eksik listelenmeli.
- [ ] **Adım 3: Grubu düzelt** — VAE satırının adı `Wan2_1_VAE_fp32.safetensors` olur (URL aynı
      kalır, satıra nedeni yazılır); iki Animations LoRA'sı `url: None` ile eklenir.
- [ ] **Adım 4: Koş, geçtiğini gör**
- [ ] **Adım 5: Tam takımı koş** — `python -m pytest queen-editor -q`
- [ ] **Adım 6: Commit**
