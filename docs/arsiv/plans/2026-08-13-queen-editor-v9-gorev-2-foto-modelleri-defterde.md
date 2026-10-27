# v9 · Görev 2 — Fotoğraf modelleri defterde kurulsun (uygulama planı)

**Spec:** [2026-08-13-queen-editor-v9-gorev-2-foto-modelleri-defterde-design.md](../specs/2026-08-13-queen-editor-v9-gorev-2-foto-modelleri-defterde-design.md)
**Amaç:** Defterin bu daldan önceki indirme hücreleri birebir geri gelsin; fotoğraf uçtan uca
çalışsın.

**Kaynak:** `git show 32c216a:queen-editor/app.ipynb` — v7'nin silme commit'inden (`b30d0a6`) bir
öncesi, yani hücrelerin çalışan son hâli.

**Komut:** `python -m pytest queen-editor -q`

## Global kısıtlar

- Hücreler **birebir** kopyalanır: çalışan tek satır değişmez.
- Defter markdown ve `print`/`assert` metni **Türkçe**, kod yorumları **İngilizce**.
- Görev tek commit; commit mesajında çift tırnak yok.

## Adım 1 — Bağı kuran testi yaz (kırmızı)

**Dosya:** `backend/tests/test_notebook_installs_the_photo_group.py` (yeni)

- [ ] **1.1 Testi yaz:**

```python
"""The notebook installs what the panel counts.

The app reads a producer's group off the disk and the notebook is what puts it there
(FOUNDATION 9). Nothing connects the two lists at runtime, so a file added to the group and
forgotten in the notebook would leave the panel saying "kurulu değil" for good, with nobody able to
see why. This test is that connection.
"""
import os

from backend.features.producers.domain.model_groups import GROUPS

NOTEBOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app.ipynb")


def _notebook():
    with open(NOTEBOOK, encoding="utf-8") as handle:
        return handle.read()


def test_every_photo_file_the_panel_counts_is_fetched_by_the_notebook():
    text = _notebook()

    missing = [row["name"] for row in GROUPS["photo"] if row["name"] not in text]

    assert missing == [], f"Defter bu dosyaları indirmiyor: {missing}"


def test_the_gated_files_are_fetched_the_way_that_works():
    """curl, not aria2c: Civitai redirects to its store, which answers 403 if the login cookie
    travels with the request. aria2c forwards it; curl drops it when the host changes."""
    text = _notebook()

    assert "civitai_probe" in text, "Ağır indirmeden önce kapılı erişim yoklanmalı"
    assert "civitai.red/api/download/models" in text
```

- [ ] **1.2 Koş, kırmızıyı gör** — `python -m pytest queen-editor -q -k notebook_installs`
      Beklenen: beş dosya da eksik, `civitai_probe` yok.

## Adım 2 — Yardımcıları geri getir

**Dosya:** `queen-editor/app.ipynb`, hücre `df871d38` (NotebookEdit)

- [ ] **2.1** Bugünkü `log` ve `run`'ın yanına, `32c216a`'dan birebir: `human`, `head_text`,
      `check_safetensors`. `import` satırı `os, json, time, struct, subprocess` olur.
      Son `print` satırı hangi yardımcıların hazır olduğunu sayar.
- [ ] **2.2** Hücrenin ilk yorumu bu defterdeki gerçek kullanıcılarını söyler (custom node hücresi
      ve model hücresi) — eski defterin "section 6 (render)" cümlesi buraya taşınmaz.

## Adım 3 — Model markdown'ı ve indirme hücresini geri getir

**Dosya:** `queen-editor/app.ipynb` (NotebookEdit, `insert`)

- [ ] **3.1** Custom node hücresinden (`8e4cc402`) sonra markdown: "## Modeller — önce gated probe,
      sonra indir (~7.5 GiB)" — `32c216a`'daki `3ad9cb36` hücresi birebir.
- [ ] **3.2** Onun ardından indirme hücresi — `32c216a`'daki `05c61d4d` birebir: hedef klasörler,
      `check_binary`, `fetch`, `civitai_url`, `cookie_header`, `civitai_probe`, `CIVITAI_MODELS`,
      `OPEN_MODELS`, üç adımlı akış (probe → açık indirmeler → Civitai) ve özet.
- [ ] **3.3** Yeri doğrula: ComfyUI'yi başlatan hücreden (`d5c4f4e8` / `2bc455dd`) **önce**.

## Adım 4 — Yeşil ve gözle okuma

- [ ] **4.1 Koş** — `python -m pytest queen-editor -q`
- [ ] **4.2** Defteri baştan sona oku: hücre sırası CONFIG → Drive → klon → yardımcılar →
      ComfyUI+node → modeller → ComfyUI başlat → Flask. Sarkan bir cümle kalmasın.

## Adım 5 — Belgeler

- [ ] **5.1 `README.md`** — Run all'ın ne kurduğu ve ne kadar sürdüğü; fotoğraf dışındakilerin
      henüz inmediği.
- [ ] **5.2 Yol haritası** — v9 durumu "2/2 bitti, Colab turu bekliyor".

## Adım 6 — Kapanış

- [ ] **6.1 Commit** — defter + test + spec + plan + belgeler.

## Kendi kontrolüm

- Eski hücre yalnız fotoğrafın beş dosyasını indiriyor; "sadece fotoğraf" kısıtı için hücreye
  dokunmaya gerek yok. ✓
- MMAudio hücresi geri gelmiyor: kullanıcı sesin sırasının sonra olduğunu söyledi. ✓
- `CONFIG` hücresindeki `CIVITAI_COOKIE` assert'i zaten duruyor ve şimdi yine gerekli — ona
  dokunulmuyor. ✓
- Ön yüz değişmiyor, `dist/` yeniden derlenmiyor. ✓
