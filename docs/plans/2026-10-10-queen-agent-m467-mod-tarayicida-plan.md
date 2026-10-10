# Madde 467 · Mod tarayıcıda — plan

**Spec:** [2026-10-10-queen-agent-m467-mod-tarayicida-design.md](../specs/2026-10-10-queen-agent-m467-mod-tarayicida-design.md)

Önce testler yazılır ve kırmızı görülür, sonra kod. Kod elle değişir, `git revert` yok. Backend yolları
`queen-agent/backend/`, frontend yolları `queen-agent/frontend/src/` altında.

## Backend

1. **Testler:**
   - `tests/test_chats_api.py`: 463'ün mod bölümü gider; yerine mod hiçbir yere yazılmıyor (sohbet
     dosyası, `projects.json` satırı, GET cevabı); mod kapısı yok (405); bilinmeyen mod mesaj,
     düzenleme ve retry'da 400 ve hiçbir şey yazılmıyor; mod gönderilmezse (ya da `null`) Edit;
     düzenleme ve retry gönderildiği modda koşuyor. `_asked` modu mesajla gönderir; izin cevapları
     yine `{turn}`. `_app`'e `projects` parametresi (testin `projects.json`'u flush edebilmesi için).
   - `tests/test_advance_chat.py`: taslak modu bölümü gider; bilinmeyen mod üç yolda tutmadan
     reddediliyor.
   - `tests/test_run_turn.py`: `_answer` modu parametreyle verir; Allow turun kalanını Edit yapar
     (463 öncesi test geri gelir), Deny modu değiştirmez; tur sürerken seçilen mod testleri ve modsuz
     tur testi gider.
   - `tests/test_modes.py`: bilinmeyen moda varsayılan veren test gider; yerine bilinmeyen mod kurala
     ulaşırsa hata (`KeyError`), ve `MODES` kuralın modlarıyla aynı.
   - `tests/test_file_project_store.py`: 463'ün mod testleri gider; 463'ün `mode` yazdığı satır okunuyor,
     sohbet yazılınca güncelleniyor ve flush'tan sonra satırda `mode` yok.
   - `tests/test_file_chat_store.py`, `tests/test_live_turns.py`: mod ve `asks` testleri gider.
   - `tests/test_pick_mode.py`, `tests/test_answer_question.py`: silinir.
2. **`features/workspace/domain/modes.py`**: `DEFAULT` kalır, yorumu isteği anlatır; `MODES =
   tuple(_WITHOUT_ASKING)`; `needs_permission` `_WITHOUT_ASKING[mode]` okur, varsayılana düşmez.
3. **`features/workspace/domain/usecases/advance_chat.py`**: `mode=None` → Edit; bilinmeyen →
   `UnknownMode`, tutmadan önce; `run_turn(..., mode)`; satıra mod yazma gider.
4. **`features/workspace/domain/usecases/run_turn.py`**: zorunlu `mode` parametresi, Allow'dan sonra
   `mode = EDIT`; `mode_of` okuması gider.
5. **`features/workspace/presentation/routes.py`**: `payload.get("mode")`; retry'da `UnknownMode` 400;
   `POST …/mode`, `chat_state` yardımcısı ve cevaplardaki mod gider; izin kapısı `live.decide`.
6. **`features/workspace/data/file_project_store.py`**: `chat_mode`, `set_chat_mode`, `_chat_row_of`,
   `_mode_of` gider; `_put` 463'ten önceki gibi satırı bütünüyle değiştirir, 463'ün bıraktığı `mode`
   anahtarı sohbetin bir sonraki yazılışında dosyadan çıkar.
7. **`features/workspace/data/file_chat_store.py`**, **`data/live_turns.py`**, **`domain/ports.py`**:
   `mode_of`, `set_mode`, `asks` gider. **`domain/errors.py`**: `UnknownMode`'un yorumu.
8. **Silinir:** `domain/usecases/pick_mode.py`, `domain/usecases/answer_question.py`.

## Frontend

9. **Testler:**
   - `App.test.jsx`: 463'ün mod bölümü gider; yerine yeni sayfa ve yenileme Edit; seçilen mod sohbet
     değişince ve yeni sohbette duruyor; seçim istek göndermiyor; mesaj ve düzenleme modu taşıyor;
     taslağın ilk mesajı modu taşıyor. Retry gövdeleri `{mode: "edit"}`; Plan'da Try again `{mode:
     "plan"}` (463 öncesi test geri gelir). `paused` 463 öncesine döner; Allow seçiciyi Edit yapıyor ve
     sonraki mesaj Edit'le gidiyor; Deny modu bırakıyor.
   - `features/workspace/useChat.test.jsx`: 463'ün `pickMode` testleri gider; mesaj her zaman modu
     taşıyor; `answerAgain("ask")` gövdesi `{mode: "ask"}`.
10. **`features/workspace/useChat.js`**: `picked`, `picks`, `shownMode`, `pickMode` gider; `answer`
    cevaptan mod okumaz; `send` ve `retry` modu gövdeye koyar, varsayılansız.
11. **`App.jsx`**: tek `mode` durumu; seçici, `onSend`, `onRetry`, `onAnswerAgain` onu kullanır; `onAllow`
    `setMode(EDIT)`. **`features/workspace/modes.js`**: `EDIT` ihracı geri gelir.

## Kural dosyası ve bitiş

12. **`queen-agent/CODE-STANDARD.md`**: 463'ün iki eklemesi çıkar (87bfc6fe'den önceki metin).
13. `npm run build --prefix queen-agent/frontend`; dört takım tek tek.
