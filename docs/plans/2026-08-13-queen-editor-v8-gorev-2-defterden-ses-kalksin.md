# v8 · Görev 2 — Defterden ses hücreleri ve model notu kalksın (uygulama planı)

**Spec:** [2026-08-13-queen-editor-v8-gorev-2-defterden-ses-kalksin-design.md](../specs/2026-08-13-queen-editor-v8-gorev-2-defterden-ses-kalksin-design.md)
**Amaç:** Defter yalnız uygulamanın koşması için gerekeni kursun; ses motoru panelin işi olarak
kalsın, ve bunu bir test korusun.

**Komut:** `python -m pytest queen-editor -q`

## Global kısıtlar

- Defterdeki markdown ve `print`/`assert` metni **Türkçe**, kod yorumları **İngilizce**.
- Yorum kod ile çelişemez: silinen hücreye atıf yapan her cümle aynı commit'te düzelir.
- Görev tek commit; commit mesajında çift tırnak yok.

## Adım 1 — Kırmızı test

**Dosya:** `backend/tests/test_model_install_is_the_apps_job.py`

- [ ] **1.1 Testi yaz** — dosyanın sonuna:

```python
NOTEBOOK = os.path.join(ROOT, "app.ipynb")
# The sound engine is a library, so it was the last thing the notebook installed for a producer.
# Leaving that cell in would not break anything -- it would quietly become a second way of
# installing the same engine, and the two only disagree on a fresh machine.
ENGINE = "MMAudio"


def test_the_notebook_installs_no_producer_engine():
    with open(NOTEBOOK, encoding="utf-8") as handle:
        assert ENGINE not in handle.read()
```

- [ ] **1.2 Koş, kırmızıyı gör** — `python -m pytest queen-editor -q -k producer_engine`
      Beklenen: `AssertionError` (defterde beş yerde geçiyor)

## Adım 2 — Hücreleri sil

**Dosya:** `queen-editor/app.ipynb` (NotebookEdit ile)

- [ ] **2.1 Sil** — `5b33516b` (MMAudio başlığı), `6269c93f` (klon + pip + import),
      `3ad9cb36` ("Modeller — burada inmez").

## Adım 3 — Kalan atıfları düzelt

- [ ] **3.1 `8de17e98`** (ComfyUI markdown) — "kurulumu bir sonraki hücrede" gitti; not artık
      Üreticiler panelini gösterir.
- [ ] **3.2 `34c9ff58`** (giriş) — akış satırından MMAudio adımı çıkar. Başlık Görev 3'ün işi.
- [ ] **3.3 `df871d38`** (ortak yardımcılar) — "custom node ve MMAudio hücreleri" artık tek hücre;
      hücrenin `assert` gerekçesi de tek kullanıcıya göre yazılır.

## Adım 4 — Yeşil ve kapanış

- [ ] **4.1 Koş** — `python -m pytest queen-editor -q` (tam takım)
- [ ] **4.2 Defteri gözle oku** — silinenlerin arkasında sarkan bir cümle kalmasın.
- [ ] **4.3 Commit** — defter + test + spec + plan.

## Kendi kontrolüm

- Test defterle sınırlı, repo geneli değil: `MMAudio` kelimesi kodda, testlerde ve bu belgelerde
  doğru yerde duruyor, oraları yakalamamalı. ✓
- Silinen üç hücrenin taşıdığı bilgi (modeller panelden kurulur) giriş hücresinde zaten var, o
  yüzden silme bilgi kaybı değil. ✓
- `run` ve `log` yardımcıları duruyor: onları custom node hücresi de kullanıyor. ✓
