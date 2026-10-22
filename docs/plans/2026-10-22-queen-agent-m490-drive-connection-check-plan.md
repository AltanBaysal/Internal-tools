# Madde 490 · Drive bağlantı kontrolü — plan

**Hedef:** `Store` her işlemden önce kökü yoklar ve kökü hiç açmaz; bir disk hatası ekrana 503 ve
cümlesiyle gelir; kök yoksa sunucu açılmaz; 448'in taşıma kodu yok.

**Spec:** [m490](../specs/2026-10-22-queen-agent-m490-drive-connection-check-design.md)

Önce testler yazılır ve kırmızı görülür, sonra kod. Yollar `queen-agent/` altında. Takımlar teker
teker koşar; frontend ve `dist` değişmez.

## Görev 1: `Store` — kontrol ve kök

1. **Testler, `backend/tests/test_store.py`:**
   - kökün stat'ı Errno 107 verince her açık yöntem (`read_text`, `write_text`, `list_dir`, `move`)
     `RootUnreachable` veriyor, `FileNotFoundError` değil, cümlede OS'un sözü var, kökte bir şey
     yazılmıyor; listedeki yöntemler `Store`'un açık yöntemleriyle aynı;
   - kök yokken her yöntem `RootUnreachable`, kök açılmıyor (`test_root_is_created_…` bunun yerine);
   - aygıt değişince `RootUnreachable`, cümlede iki kimlik;
   - kurulum stat etmiyor; her işlem kökü bir kez stat ediyor (`move` dahil);
   - kontrol geçip kök yokken `write_text("p1/chats/c.json")` ve `move` kökü açmıyor;
   - `_counting_makedirs` `_counting_folder_makes` olur ve `os.mkdir`'i de sayar; var olan klasöre yazma ve taşıma klasör açmıyor;
   - `mtime` testi silinir.
2. **`backend/services/store/store.py`:** `RootUnreachable(OSError)`; `_device`; `_reached()`; her açık
   yöntemde `_full`'dan sonra bir kez; `_into_folder` yöntem olur, kök klasörse hatayı yükseltir,
   değilse `_make_below_root` ile birer birer `os.mkdir`; `mtime` gider.

## Görev 2: Tek işleyici

3. **Test, `backend/tests/test_app_errors.py` (yeni):** bir blueprint'in `OSError`'ı ve
   `RootUnreachable`'ı `503 {"error": str}`; başka bir hata 503 olmuyor.
4. **Testler, `backend/tests/test_chats_api.py`:** `test_a_request_that_breaks_before_its_turn_…`
   500 → 503; kök gidince mesaj 503 ve cümle, kök açılmıyor; tur sürerken kök gidince `events`'in
   son karesi cümle.
5. **`backend/web/app.py`:** `@app.errorhandler(OSError)` → log satırı + `503`.

## Görev 3: Açılış

6. **Test, `backend/tests/test_composition.py`:** `python main.py` olmayan bir `QUEENAGENT_ROOT`'la
   sıfır olmayan kodla çıkıyor, stderr'de *"QueenAgent did not start"* ve *"cannot be reached"*,
   kök açılmamış. `test_old_projects_are_moved_at_start` silinir.
7. **`main.py`:** `except (ProjectsUnreadable, OSError)`; `move_old_projects` import'u ve satırı gider.

## Görev 4: 448

8. Silinir: `backend/features/workspace/data/old_projects.py`, `backend/tests/test_old_projects.py`,
   `FileProjectStore.take_in`.
9. **Test, `backend/tests/test_notebook.py`:** Serve hücresinde `START_CAP = 90`, `⏳` yok;
   `test_the_wait_ends_when_the_server_dies`'ın docstring'i 448'i değil reddedilen açılışı söyler.
10. **`queenagent.ipynb`:** `START_CAP = 90`, yorumu; `reported` ve `⏳` satırı gider.

## Görev 5: Belgeler ve bitiş

11. **`CODE-STANDARD.md`**, `store/` satırı; **`README.md`**, *Run it*: kök önceden var olmalı.
12. `queen-agent` altında `old_projects`, `take_in`, `mtime(`, `START_CAP = 600` taranır.
13. `python -m pytest queen-agent -q`, sonra `npm test --prefix queen-agent/frontend`. Commit'i ana
    ajan atar.
