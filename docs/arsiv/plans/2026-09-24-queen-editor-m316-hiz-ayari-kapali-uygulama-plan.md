# Madde 316 — HF'nin yüksek hız ayarı şimdilik kapanıyor, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `e638691e`'in kırmızısı yeşile dönsün.

**Spec:** [m316 implementasyon turu](../specs/2026-09-24-queen-editor-m316-hiz-ayari-kapali-uygulama-design.md)

---

## Görev 1: `colab/downloads.py`

- [ ] **Adım 1: `hf_fetch`'in başı** — bu dört satır:

```python
    # huggingface_hub reads its variables once, when it is imported, so the switch comes first. It
    # has hf_xet try to fill the machine's bandwidth and use every CPU core (madde 312).
    os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"
    # Imported here: Colab ships it, and this module has to import where it is not installed.
```

  şuna iniyor:

```python
    # Imported here: Colab ships it, and this module has to import where it is not installed.
```

## Görev 2: Koşu, commit'ler

- [ ] **Adım 1: Dört satırı koş** — dördü de yeşil.
- [ ] **Adım 2: Yeşil commit** — `downloads.py`, bu spec ve bu plan: `feat(m316): …`.
- [ ] **Adım 3: Yol haritası** — 316 ✅, *Kapandı* notu, *Durum: 23/24*; ayrı `docs(m316)` commit'i.
