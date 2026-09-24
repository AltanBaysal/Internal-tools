# Madde 316 — HF'nin yüksek hız ayarı şimdilik kapanıyor, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `hf_fetch`'in yüksek hız ayarına dokunmadığını söyleyen tek test — kırmızı.

**Yaklaşım:** 312'nin testi yerini tersine bırakıyor. Ortam `0` ile kuruluyor, HF'nin indiricisi
310'un sahtesiyle, ve `hf_fetch`'ten sonra değişkene bakılıyor.

**Spec:** [m316 test turu](../specs/2026-09-24-queen-editor-m316-hiz-ayari-kapali-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve docstring **İngilizce**, assert mesajı **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.

---

## Görev 1: Test

**Dosya:** Değiştir: `queen-editor/backend/tests/test_colab_downloads.py` —
`test_hugging_face_s_downloader_is_taken_in_high_performance_mode`'un yerine.

- [ ] **Adım 1: Test.**

```python
def test_hugging_face_s_downloader_is_taken_with_high_performance_left_off(
        downloads, monkeypatch, tmp_path):
    """High-performance mode had HF's chunk server answer 429 on its first run, and the run died;
    with it off, two full runs never saw one (madde 316). hf_fetch leaves the switch to the
    environment, where a fresh Colab machine has nothing -- it comes back with 313, from the
    backlog, once the 429 is solved."""
    monkeypatch.setenv("HF_XET_HIGH_PERFORMANCE", "0")
    _hub(monkeypatch, _safetensors())

    downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                       str(tmp_path), "taeh3.safetensors", "H3 TAE")

    assert os.environ["HF_XET_HIGH_PERFORMANCE"] == "0", \
        "hf_fetch HF'nin yüksek hız ayarını açtı"
```

## Görev 2: Koşu ve kırmızı commit

- [ ] **Adım 1: Dört satırı koş** — `queen-editor` pytest'te yalnız bu test kırmızı; öteki üç satır
  yeşil.
- [ ] **Adım 2: Kırmızı commit** — test dosyası, spec ve bu plan: `test(m316): …(red)`.
