# Görev 4 — Ses üreticisinin kurulumu · Uygulama planı

> **Ajanlar için:** GEREKLİ ALT BECERİ: bu planı superpowers:executing-plans ile uygula.

**Amaç:** Ses grubunu örnekleyicinin gerçekten yüklediği dosyaya eşitlemek ve ağırlık yolunu tek
yerden türetmek.

**Tasarım:** [spec](../specs/2026-08-13-queen-editor-v6-gorev-4-ses-kurulumu-design.md)

## Genel kısıtlar

- Dosya adı tek yerde: `model_groups.py`. `main.py` yolu oradan kurar.
- Test: `python -m pytest queen-editor -q`. Ön yüz değişmiyor.

---

### Task 1: Grup ve yol

**Dosyalar:**
- Değiştir: `queen-editor/backend/features/producers/domain/model_groups.py`
- Test: `queen-editor/backend/tests/test_producers.py`

**Arayüz:** `GROUPS["audio"]` tek satır; `audio_weights(files)` — grubun satırından
`ModelFiles.path` ile yolu kuran yardımcı (aynı dosyada, `main.py` onu çağırır).

- [ ] **Adım 1: Düşen testleri yaz** — grup tek satır, adı NSFW fine-tune, adresi `phazei`
      deposunda ve `None` değil; `audio_weights` `models/mmaudio/<ad>` ile biten yolu döndürür.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Grubu ve yardımcıyı yaz**
- [ ] **Adım 4: Koş, geçtiklerini gör**
- [ ] **Adım 5: Tam takım + commit**
