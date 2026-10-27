# Madde 432 — HF indirmesi düşünce yeniden denenir, plan

> **Koşum:** bu oturumda, ana klasörde, satır satır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** `hf_fetch` düşen bir indirmeyi en çok 3 kez dener, aralarında 30 saniye; her düşüşte konsola
hatanın kendisi ve HF'nin cevabı basılır. 401, 403, 404 ve tam inmiş ama bozuk dosya yeniden
denenmez.

**Yaklaşım:** Önce testler: sahteler HF gibi hata atar, bekleme her testte sahtedir, ve yeni testler
kırmızı görülür. Sonra `downloads.py`'de bir döngü ve hatayı atıldığı gibi yazan küçük bir yardımcı.

**Araçlar:** pytest.

**Spec:** [m432](../specs/2026-10-08-queen-editor-m432-hf-yeniden-deneme-design.md)

## Her yere geçerli kurallar

- Yorumlar, docstring'ler ve test adları **İngilizce**; konsola ve `assert`'e giden metin **Türkçe**.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Hiçbir test gerçek bir saniye beklemez: `time.sleep` her testte sahte.
- Yalnız `colab/downloads.py` ve `backend/tests/test_colab_downloads.py` değişir; notebook'a,
  `fetch`'e, `civitai_fetch`'e, frontend'e, `dist`'e ve yol haritasına dokunulmaz.

---

## Görev 1: Sahteler — `queen-editor/backend/tests/test_colab_downloads.py`

- [ ] **`waits` fikstürü, `autouse`:** `downloads.time.sleep`'i istenen saniyeleri listeye yazan bir
  sahteyle değiştirir ve listeyi verir. Her testte çalışır; beklemeyi soran test onu adıyla ister.
- [ ] **`HfHubHTTPError` sahtesi:** `OSError`'dan; `response`'u `status_code` ve `text` taşıyan bir
  `SimpleNamespace`. HF'nin cevap verdiği hata böyle görünür.
- [ ] **`DROP`:** 2 Ekim'deki Xet hatasının mesajı, adresi 4000 karakteri aşacak kadar uzun.
- [ ] **`_hub`'a `errors=()`:** ilk çağrılar sırayla onları atar; sonra dosya bugünkü gibi iner.
- [ ] **`_eros(downloads, tmp_path)`:** yeni testlerin ortak çağrısı — H3 Eros Max beta5'i
  `hf_fetch` ile ister.
- [ ] **`_mirror`:** aynada olmayan dosya için `OSError` yerine 404'lü `HfHubHTTPError`.
- [ ] **`test_a_failed_huggingface_download_says_what_hugging_face_said`:** kendi sahtesi yerine
  `_hub(..., errors=[HfHubHTTPError(<aynı cümle>, 404)])`. Assert'leri değişmez.

## Görev 2: Kırmızı testler — aynı dosya

- [ ] `test_a_huggingface_download_that_drops_is_tried_again_and_comes_down` — 2 çağrı, `waits == [30]`,
  dosya yerinde, satır geri döner.
- [ ] `test_a_dropped_attempt_prints_the_error_as_it_was_raised` — konsolda `RuntimeError: {DROP}`
  tamamıyla; `deneme 1/3`'lü satırda etiket ve `30 sn`.
- [ ] `test_a_dropped_attempt_prints_hugging_face_s_response_as_sent` — `HfHubHTTPError: <mesaj>`,
  `HTTP 502` ve HTML gövdesi.
- [ ] `test_a_body_that_cannot_be_read_does_not_hide_the_drop` — `.text`'i `ResponseNotRead` atan
  bir `_Unread` cevaplı 502; 2 çağrı, `waits == [30]`; konsolda hata, `HTTP 502` ve okuyucunun hatası.
  Okuma korunmadan kırmızı: hücre okuyucunun hatasıyla durur.
- [ ] `test_a_download_is_given_up_after_three_attempts` — 3 çağrı, `waits == [30, 30]`; hata
  `deneme 3/3`'ü ve `RuntimeError: {DROP}`'u taşır.
- [ ] `test_the_error_that_stops_the_cell_carries_hugging_face_s_response` — üç 500; hata `HTTP 500`'ü
  ve gövdeyi taşır.
- [ ] `test_hugging_face_s_answer_about_the_file_is_not_asked_again`, 401 / 403 / 404 ile — 1 çağrı,
  `waits == []`; hata kodu ve gövdeyi taşır.
- [ ] `test_an_answer_under_hugging_face_s_own_sentence_is_read_and_printed_too` — bir
  `LocalEntryNotFoundError` sahtesi, `__cause__`'u 403'lü bir `HfHubHTTPError`; hata iki halkayı,
  atılan başta, ve `HTTP 403`'ü gövdesiyle taşır; 1 çağrı, `waits == []`. Zincir yürünmeden kırmızı:
  cevapsız sarmalayıcı yeniden denenir, ve ikinci çağrıda dosya iner.
- [ ] `test_a_file_that_came_down_whole_but_bad_is_not_downloaded_again` — kesik safetensors; 1 çağrı,
  `waits == []`.
- [ ] `test_a_file_missing_from_the_mirror_goes_to_civitai_without_waiting` — `waits == []`; konsolda
  `HTTP 404` ve `(boş gövde)`.
- [ ] **`python -m pytest queen-editor -q`** — yalnız yeni testler kırmızı (bugünkü `hf_fetch` ilk
  hatada durur, cevabı basmaz). Bozuk dosya testi bugün de yeşil: davranış zaten öyle, test onu
  sabitler. Bugünkü testler yeşil.

## Görev 3: `queen-editor/colab/downloads.py`

- [ ] **Sabitler, `hf_fetch`'in üstünde:** `ATTEMPTS = 3`, `WAIT = 30`, `FINAL = (401, 403, 404)`;
  yorumları neden bu sayılar olduğunu söyler.
- [ ] **`_chain(error)`:** hata ve atıldığı hatalar, atılan başta — `__cause__`, yoksa bastırılmamışsa
  `__context__`; kendine dönen zincirde ve beşinci halkada durur.
- [ ] **`_response(error)`:** zincirde `response` taşıyan ilk hatanın cevabı, ya da `None`.
- [ ] **`_raw(error)`:** zincirin her halkası `f"{type(e).__name__}: {e}"`, kendi satırında; cevap
  varsa altına `--- response: HTTP {status_code} ---` ve `text`, boşsa `(boş gövde)`. `text`'i okumak
  hata atarsa gövdenin yerinde `(gövde okunamadı — {type(e).__name__}: {e})`.
- [ ] **`hf_fetch`'te döngü:**

```python
    for attempt in range(1, ATTEMPTS + 1):
        try:
            got = hf_hub_download(repo, path, local_dir=STAGE)
            break
        except Exception as e:
            where = f"{label}: HF {repo}/{path}, deneme {attempt}/{ATTEMPTS}"
            answer = getattr(_response(e), "status_code", None)
            if answer in FINAL or attempt == ATTEMPTS:
                raise RuntimeError(f"{where}\n{_raw(e)}") from None
            log(f"{where} — {WAIT} sn sonra yeniden\n{_raw(e)}", "WARN")
        time.sleep(WAIT)
```

  `start` yerinde kalır; `_settled`, `os.replace` ve `_landed` döngüden sonra, bugünkü gibi.
- [ ] **Docstring:** yeniden denemeyi ve denenmeyenleri söyler.

## Görev 4: Koş

- [ ] **Dört satır, paralel, olduğu gibi, depo kökünden.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; queen-editor'ün backend'i 12 test fazla (10 yeni test, biri üç durumla).

## Görev 5: Commit — ana ajanın

- [ ] Spec, plan, test ve `downloads.py`. Mesajda çift tırnak yok; son satır
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
