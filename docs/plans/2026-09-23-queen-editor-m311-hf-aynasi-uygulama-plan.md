# Madde 311 — HF aynası, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `c20ea6d2`'nin dokuz kırmızısı yeşile dönsün: Civitai dosyaları önce aynadan, düşüşte
Civitai'den iner ve aynaya çıkar.

**Yaklaşım:** `downloads.py`'ye `civitai_fetch` ve `_upload`; defterde dört hücre `NotebookEdit`
ile, değişmeyen satırlar harfi harfine; README'de iki satır.

**Araçlar:** `huggingface_hub` (`hf_hub_download`, `HfApi.upload_file`), fonksiyonların içinde import.

**Spec:** [m311 implementasyon turu](../specs/2026-09-23-queen-editor-m311-hf-aynasi-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve docstring İngilizce, konsol metinleri Türkçe.
- Defterin kod hücrelerinde yorum yok. Testler dört satırla koşulur.

---

## Görev 1: `civitai_fetch`

**Dosyalar:** Değiştir: `queen-editor/colab/downloads.py` — `cookie_header`'ın altına.

- [ ] **Adım 1:**

```python
def _upload(mirror, path, target, label):
    """Up to the mirror. A refusal is printed, not raised: the file is already down and usable, and
    the next run tries again."""
    from huggingface_hub import HfApi

    start = time.perf_counter()
    try:
        HfApi().upload_file(path_or_fileobj=target, path_in_repo=path, repo_id=mirror,
                            commit_message=f"{label} (Civitai {path})")
    except Exception as e:
        log(f"{label}: aynaya yüklenemedi — {type(e).__name__}: {e}", "WARN")
        return
    size, took = os.path.getsize(target), time.perf_counter() - start
    log(f"{label}: aynaya yüklendi — {human(size)}, {took:.0f} sn, {size / took / 2**20:.1f} MB/s", "OK")


def civitai_fetch(mirror, version_id, target_dir, filename, label, cookie):
    """A Civitai file, from the user's Hugging Face mirror when it is there. When it is not -- or will
    not come down -- the mirror's own sentence is printed, the file comes from Civitai the way it
    always did, and it goes up to the mirror so the next run takes the fast road (madde 311)."""
    path = f"{version_id}/{filename}"
    try:
        hf_fetch(mirror, path, target_dir, filename, label)
        return
    except RuntimeError as e:
        log(f"{label}: aynadan alınamadı, Civitai'den inecek — {e}", "WARN")
    if len(cookie or "") <= 200:
        raise RuntimeError(
            f"❌ {label}: aynada yok, ve Civitai'den inmesi için CIVITAI_COOKIE gerekiyor — Colab 🔑 "
            f"Secrets'a 'CIVITAI_COOKIE' adıyla ekle: civitai.red → giriş → F12 → Application → "
            f"Cookies → __Secure-civ-token değeri (ES256 JWT)")
    civitai_probe(version_id, label, cookie)
    fetch(civitai_url(version_id), target_dir, filename, label, parallel=False,
          headers=cookie_header(cookie))
    _upload(mirror, path, os.path.join(target_dir, filename), label)
```

## Görev 2: Defter

**Dosyalar:** `queen-editor/queeneditor.ipynb` — hücreler `8215086b`, `df871d38`, `f0df85b4`, `34c9ff58`.

- [ ] **Adım 1: CONFIG (`8215086b`)** — `DRIVE_FOLDER = "queenEditor"`'ın altına:

```python
HF_MIRROR    = "Test468735/queen-editor-models"
```

  şu blok siliniyor:

```python
if INSTALL_PHOTO or INSTALL_VIDEO:
    assert len(COOKIE_VALUE or "") > 200, (
        "❌ CIVITAI_COOKIE yok/çok kısa — Colab 🔑 Secrets'a 'CIVITAI_COOKIE' adıyla ekle: "
        "civitai.red → giriş → F12 → Application → Cookies → __Secure-civ-token değeri (ES256 JWT)"
    )
```

  ve `print(f"✓ Proje kökü: MyDrive/{DRIVE_FOLDER}")`'ın altına:

```python
print(f"✓ HF aynası: {HF_MIRROR}")
```

- [ ] **Adım 2: Yardımcılar (`df871d38`)** — import satırı:

```python
from colab.downloads import fetch, hf_fetch, civitai_fetch
```

- [ ] **Adım 3: Modeller (`f0df85b4`)** — `# === Gated probe ===` bölümü siliniyor; Civitai döngüsü:

```python
# === Civitai downloads ===
for vid, d, fn, label in civitai_jobs:
    civitai_fetch(HF_MIRROR, vid, d, fn, label, COOKIE_VALUE)
```

- [ ] **Adım 4: Giriş (`34c9ff58`)** — Secrets maddesi:

```markdown
2. **🔑 Secrets:** `GITHUB_TOKEN` (fine-grained, yalnız bu repo, `Contents: read`); `HF_TOKEN`
   (fine-grained, yalnız CONFIG'deki `HF_MIRROR` reposu, okuma + yazma — Civitai dosyaları önce
   oradan iner, yenileri oraya yüklenir); `CIVITAI_COOKIE` yalnız aynada henüz olmayan bir dosya
   için (civitai.red → F12 → Application → Cookies → `__Secure-civ-token`, ~30 günde bir yenilenir);
   video için `XAI_API_KEY` (video prompt'unu yazan dil modeli).
```

## Görev 3: README, koşu, commit'ler

- [ ] **Adım 1: Secrets tablosu** — `CIVITAI_COOKIE` satırı:

```markdown
| `CIVITAI_COOKIE` | The `__Secure-civ-token` cookie from `civitai.red` (log in → F12 → Application → Cookies). Only a gated file the Hugging Face mirror does not hold yet comes from Civitai, with this cookie; once everything is mirrored a run needs none. It expires every ~30 days; re-paste it when an install stops with Civitai's own response. |
```

  altına:

```markdown
| `HF_TOKEN` | Your private Hugging Face repo that mirrors the Civitai files (`HF_MIRROR` in CONFIG). A file it holds comes from there, fast; a file it lacks comes from Civitai once and is uploaded to it. Make it fine-grained, **that one repo only, read and write**. |
```

- [ ] **Adım 2: Dört satırı koş** — dördü de yeşil.

- [ ] **Adım 3: Yeşil commit** — `downloads.py`, defter, README, bu spec ve bu plan.

- [ ] **Adım 4: Yol haritası** — 311 ✅, *Kapandı* notu, *Durum: 20/20*; ayrı `docs(m311)` commit'i.
