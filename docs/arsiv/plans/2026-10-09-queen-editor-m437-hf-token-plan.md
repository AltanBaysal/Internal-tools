# Madde 437 — Notebook HF_TOKEN'ı kendisi okur, plan

> **Koşum:** bu oturumda, ana klasörde, satır satır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Notebook `HF_TOKEN`'ı `userdata.get` ile kendisi okur ve ortama koyar; HF'nin indirmesi ve
aynaya yükleme token'ı huggingface_hub'a açıkça verir, kütüphane kasaya gitmez. Token yoksa ya da
okunamazsa bir satır bunu, okumanın attığı hatayla söyler, ve koşu token'sız sürer.

**Yaklaşım:** Önce testler, kırmızı görülür. Sonra `colab/downloads.py`, sonra defter.

**Spec:** [m437](../specs/2026-10-09-queen-editor-m437-hf-token-design.md)

## Her yere geçerli kurallar

- Yorumlar, docstring'ler ve test adları **İngilizce**; konsola ve `assert`'e giden metin **Türkçe**.
- Token hiçbir satıra basılmaz. Yol haritasına dokunulmaz.

---

## Görev 1: Kırmızı testler

- [ ] **`backend/tests/test_colab_downloads.py`:**
  - `test_the_hf_token_is_read_into_the_environment_and_never_printed`
  - `test_a_token_that_cannot_be_read_says_what_the_read_raised`
  - `test_an_empty_token_is_said_to_be_empty`
  - `test_a_huggingface_download_hands_its_token_over_outright` (token'la ve token'sız)
  - `test_an_upload_to_the_mirror_hands_its_token_over_outright` (token'la ve token'sız)
  - İkisi `_handed` ile `_hub`'ın ve `_mirror`'ın sahtesini sarar.
- [ ] **`backend/tests/test_notebook_installs_the_producer_groups.py`:**
  `test_the_notebook_reads_the_hf_token_itself_before_anything_downloads`.
- [ ] `python -m pytest queen-editor -q`: yalnız yeni testler kırmızı.

## Görev 2: `colab/downloads.py`

- [ ] `use_hf_token(read)`: okur, kırpar; okunduysa ortama koyar ve `OK` satırı. Hata da boş değer de
  kendi yerinde `_without_token(said)`'i çağırır ve döner.
- [ ] `_without_token(said)`: ortamdan siler, `WARN` satırı, altında token'sız gidileceği cümlesi.
- [ ] `_token()`: `os.environ.get("HF_TOKEN") or False`.
- [ ] `hf_fetch`: `hf_hub_download(..., token=_token())`. `_upload`: `upload_file(..., token=_token())`.

## Görev 3: Defter

- [ ] Ortak yardımcılar hücresi: `from colab.downloads import ..., use_hf_token`, import'ların altında
  `use_hf_token(userdata.get)`.

## Görev 4: Koş

- [ ] Dört satır, birer birer, depo kökünden:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

## Görev 5: Commit — ana ajanın
