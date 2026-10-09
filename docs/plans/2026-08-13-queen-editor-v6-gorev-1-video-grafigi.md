# Görev 1 — Video grafiği repoya girer · Uygulama planı

> **Ajanlar için:** GEREKLİ ALT BECERİ: bu planı superpowers:executing-plans ile uygula.

**Amaç:** Video grafiğini queen-editor'ün kendi dosyası yapmak ve shipped grafiklerin şeklini
testle tutmak.

**Tasarım:** [spec](../specs/2026-08-13-queen-editor-v6-gorev-1-video-grafigi-design.md)

## Genel kısıtlar

- Dosya **kopyalanır**, çalışma anında `collab-toolbox` okunmaz.
- Export elle düzenlenmez — öksüz node'lar dahil olduğu gibi taşınır.
- Test: `python -m pytest queen-editor -q`. Ön yüz değişmiyor, `dist/` gerekmez.

---

### Task 1: Shipped grafiklerin şekli

**Dosyalar:**
- Oluştur: `queen-editor/workflow_video_api.json` (kopya)
- Değiştir: `queen-editor/backend/tests/test_workflow_asset.py`

- [ ] **Adım 1: Düşen testi yaz** — video grafiği için, foto testinin ikizi:

```python
def test_video_workflow_is_api_format_with_the_nodes_we_patch():
    with open(config.VIDEO_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert "nodes" not in workflow, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
    assert workflow["287"]["class_type"] == "LoadImage"
    assert "image" in workflow["287"]["inputs"]
    assert workflow["233:240"]["class_type"] == "PromptGenerator"
    assert {"prompt", "seed"} <= set(workflow["233:240"]["inputs"])
    assert workflow["210"]["class_type"] == "Seed (rgthree)"
    assert "seed" in workflow["210"]["inputs"]
```

- [ ] **Adım 2: Koş, düştüğünü gör** — `FileNotFoundError`, çünkü dosya henüz yok.
- [ ] **Adım 3: Dosyayı kopyala** — `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json`
      → `queen-editor/workflow_video_api.json`. 500 satırlık JSON'u elle yazmak yerine tek kopyalama
      komutu; içeriğe dokunulmaz.
- [ ] **Adım 4: Koş, geçtiğini gör**
- [ ] **Adım 5: Foto testinin boşluğunu kapat** — mevcut testin sonuna:

```python
    assert "ckpt_name" in workflow["45"]["inputs"]
```

- [ ] **Adım 6: Tam takımı koş** — `python -m pytest queen-editor -q`
- [ ] **Adım 7: Commit** — spec, plan, graf ve test aynı commit'te.
