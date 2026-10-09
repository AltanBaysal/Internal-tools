# Madde 433 — ComfyUI cevap vermeyince, plan

> **Koşum:** bu oturumda, ana klasörde, satır satır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Queen Editor'de düşen her deneme canlı log'a kendi hatasını basar. Hata ComfyUI'nin cevap
vermediği durumlardan biriyse (bağlanılamadı, 5xx, isteğin süresi doldu) her yeniden denemeden önce
45 sn beklenir, ve Durdur beklemeyi keser. ComfyUI hücresi eski ComfyUI'nin portu bırakmasını bekler.
Ancak kendi başlattığı süreç yaşıyorken ve cevap verirken "hazır" der; yoksa ComfyUI'nin log'uyla
düşer.

**Yaklaşım:** Önce testler, kırmızı görülür. Sonra sırayla: servisin işareti, politikanın beklemesi,
döngünün satırı ve beklemesi, `colab/comfy.py`, ve defter.

**Araçlar:** pytest.

**Spec:** [m433](../specs/2026-10-08-queen-editor-m433-comfy-hazir-yeniden-deneme-design.md)

## Her yere geçerli kurallar

- Yorumlar, docstring'ler ve test adları **İngilizce**. Log'a, konsola ve `assert`'e giden metin
  **Türkçe**.
- Hiçbir test gerçek bir saniye beklemez.
- Kartın ve hata mesajlarının metni değişmez. Frontend'e, `dist`'e ve yol haritasına dokunulmaz.

---

## Görev 1: Kırmızı testler

- [ ] **`backend/tests/test_policy.py`:**
  - `test_an_engine_that_gave_no_answer_is_waited_for_45_seconds`
  - `test_anything_else_is_tried_again_at_once`
- [ ] **`backend/tests/test_comfy_client.py`:**
  - `FakeResponse.raise_for_status` gerçek `requests.HTTPError`'ı atar, cevabı üstünde. Bugünkü
    sahte bir `RuntimeError` atıyor, ve sarma onu tanımaz.
  - `FakeHttp`'ye `raises=`: verilen hata her istekte atılır (`ReadTimeout` için).
  - Testler: bağlanılamayan sunucu `no_answer`; `submit` 500 `no_answer` / 400 değil, metin aynı;
    `upload_image` 500 `no_answer`; `/view` 503 `no_answer` / 404 değil, metin `requests`'inki;
    `/system_stats` 502 `no_answer`; `ReadTimeout` `no_answer`, `TimeoutError`, metin aynı; render
    süresi `no_answer` değil; `node_errors` `no_answer` değil; `ComfyExecutionError` `no_answer`
    değil.
- [ ] **`backend/tests/test_failed_attempts.py` (yeni):** sahteler `test_photo_usecases`'ten
  (`FakeStore`, `FakeRecord`, `FakePlanStore`, `FrameFault`, `frame`, `sync_runner`). Bir `NoAnswer`
  sahtesi (`no_answer = True`), sırayla hata atan bir producer, ve saniyeleri yazan bir `sleep`.
  `make_job` doğrudan çağrılır, `log=lines.append, sleep=waits.append` ile. Spec'teki sekiz test.
- [ ] **`backend/tests/test_colab_comfy.py` (yeni):** modül fikstürde import edilir (`colab.nodes`
  testindeki gibi). Sahteler:
  - `pkill` komutları yazılır.
  - `Popen` bir `FakeProc` döner (`pid`, `poll()` sırayla, `returncode`), ve log'a 40 satır yazar.
  - `urlopen` sırayla cevap verir ya da `URLError` atar.
  - `socket.create_connection` sırayla bağlanır ya da `ConnectionRefusedError` atar.
  - `time.sleep` yazılır.

  Testler spec'teki sekiz test.
- [ ] **`backend/tests/test_notebook_installs_the_producer_groups.py`:**
  `test_the_notebook_starts_comfyui_through_start_comfy`. ComfyUI hücresi
  `start_comfy(COMFY_ROOT, COMFY_PORT, COMFY_LOG)` der, ve `start_comfy` `colab.comfy`'den import
  edilir.
- [ ] **`python -m pytest queen-editor -q`:** yalnız yeni testler kırmızı. Spec'in saydığı, bugünkü
  davranışı sabitleyen testler yeşil.

## Görev 2: `backend/services/comfy/errors.py`

- [ ] `ComfyUnreachable`'a `no_answer = True` eklenir.
- [ ] `ComfyHttpError(RuntimeError)`, `(text, status)` ile kurulur. `no_answer` ancak `status >= 500`
  ise doğrudur.
- [ ] `ComfyTimeout(TimeoutError)` eklenir, `no_answer = True`.
- [ ] Modülün docstring'i üç türü ve işareti söyler.

## Görev 3: `backend/services/comfy/client.py`

- [ ] `_send`: `except requests.ConnectionError`'dan sonra
  `except requests.Timeout as exc: raise ComfyTimeout(str(exc)) from exc`.
- [ ] `upload_image` ve `submit`:
  `raise ComfyHttpError(f"... -> HTTP {resp.status_code}\n{resp.text}", resp.status_code)`.
- [ ] `_ok(resp)`: `raise_for_status`'u çağırır. `requests.HTTPError` gelirse
  `ComfyHttpError(str(exc), resp.status_code)` atar, `from exc` ile. `_view`, `vram_total` ve
  `interrupt` bunu kullanır.

## Görev 4: `backend/features/photo_generation/domain/policy.py`

- [ ] `NO_ANSWER_WAIT = 45` eklenir; yorumu 90 sn'yi, yani hücrenin bütçesini söyler.
- [ ] `retry_wait(exc)`: `no_answer` ise `NO_ANSWER_WAIT`, değilse `0`. Docstring'i neden yalnız
  cevapsızlıkta beklendiğini söyler.

## Görev 5: `backend/features/photo_generation/domain/run_loop.py`

- [ ] `make_job(..., sleep=time.sleep)`; docstring'e bir paragraf eklenir.
- [ ] `_attempt_line(name, attempts, wait, exc)`:
  `⚠ {name} · deneme {n}/{MAX} düştü`. Sonuna `— {wait} sn sonra yeniden denenecek` ya da
  `— yeniden deneniyor` eklenir; son denemede hiçbir şey. Altında `{type(exc).__name__}: {exc}`.
- [ ] `_wait(runner, sleep, seconds)`: saniye saniye uyur, ve her saniyeden önce
  `runner.stop_requested()`'a bakar.
- [ ] `except` dalı:
  1. Durdurma kontrolü.
  2. `attempts += 1`.
  3. `wait` hesaplanır: son denemede 0.
  4. `log` varsa satır basılır.
  5. `attempts < MAX` ise `_wait`, sonra `continue`.

  Gerisi bugünkü gibi.

## Görev 6: `colab/comfy.py` ve defter

- [ ] `start_comfy(root, port, log_path)`:
  1. `_free(port)` çağrılır.
  2. Log `"wb"` ile açılır, çünkü içine yalnız ComfyUI yazar. `Popen` yapılır, ve log tutamacı
     kapanır.
  3. `log("ComfyUI başlatıldı …")` basılır.
  4. 45 bakış, 2 sn arayla: `_asked(url)` sorulur, sonra `proc.poll()`. Süreç kapandıysa
     `exit` hatası atılır. Cevap geldiyse `log("ComfyUI hazır (Ns)", "OK")` basılır ve `proc` döner.
  5. Döngü cevapsız biterse cevap vermedi hatası atılır.
- [ ] `_free(port)`: `TERM`, sonra `KILL`. Her birinin ardından en çok 30 kez, saniye arayla,
  `_refused(port)` sorulur. Port boşalmazsa dolu port hatası atılır.
- [ ] `_refused(port)`: `socket.create_connection(..., timeout=1)` denenir. Yalnız
  `ConnectionRefusedError` `True` döner.
- [ ] `_asked(url)`: cevap gelirse `None` döner, gelmezse `Tür: mesaj`.
- [ ] `_tail(path)`: log'un son 30 satırı, başlığıyla.
- [ ] **Defter:**
  - Ortak yardımcılar hücresi `from colab.comfy import start_comfy` ekler, ve basılan satırı
    `colab/comfy.py`'yi de sayar.
  - ComfyUI hücresi `start_comfy(COMFY_ROOT, COMFY_PORT, COMFY_LOG)` çağırır. Hücre bundan ibarettir:
    başlığı ve sonucu atayan tek satır.
- [ ] **`CODE-STANDARD.md`:** *Notebook code* bölümü `comfy.py`'yi de sayar (ComfyUI'nin başlatılması).

## Görev 7: Koş

- [ ] Dört satır, depo kökünden:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

## Görev 8: Commit — ana ajanın

- [ ] Spec, plan, testler, kod, defter ve `CODE-STANDARD.md`. Mesajda çift tırnak yok. Son satır:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
