# Madde 463 · Mod sohbetin ayarıdır — plan

**Spec:** [2026-10-10-queen-agent-m463-mod-sohbetin-design.md](../specs/2026-10-10-queen-agent-m463-mod-sohbetin-design.md)

Her adımda önce test yazılır ve kırmızı görülür, sonra kod. Backend yolları `queen-agent/backend/`,
frontend yolları `queen-agent/frontend/src/` altında.

## Backend

1. **`features/workspace/domain/modes.py`**: `MODES`. **`domain/errors.py`**: `UnknownMode`.
2. **`features/workspace/data/file_project_store.py`**: `chat_mode`, `set_chat_mode`; satırda `mode`
   yalnız Edit değilken; bilinmeyen değer Edit; `_put` satırı yerinde günceller. Test:
   `tests/test_file_project_store.py`: mod yazılıp geri okunuyor ve yeniden başlatmadan sonra duruyor;
   eski satır Edit; Edit yazılınca alan yok; sohbetin yeniden yazılışı modu silmiyor; olmayan satır
   `None` / `False`; iki sohbet kendi modunu tutuyor.
3. **`features/workspace/data/file_chat_store.py`** ve **`domain/ports.py`**: `mode_of`, `set_mode`;
   `LiveTurn.asks`. Test: `tests/test_file_chat_store.py`.
4. **`features/workspace/data/live_turns.py`**: `asks(tur, bekleme)`. Test: `tests/test_live_turns.py`.
5. **`domain/usecases/run_turn.py`**: `mode` parametresi gider, her çağrıda `chat_store.mode_of`; Allow'dan
   sonraki yerel Edit gider. Test: `tests/test_run_turn.py`: `_answer` modu store'a yazar; tur sürerken
   değişen mod bir sonraki çağrıda geçerli (iki yön); eski "Allow turun kalanını Edit yapar" testi,
   kararın modu değiştirdiği bir kontrolle "sonraki çağrı satırı okur" testine döner.
6. **`domain/usecases/pick_mode.py`** (yeni). Test: `tests/test_pick_mode.py`.
7. **`domain/usecases/answer_question.py`** (yeni). Test: `tests/test_answer_question.py`: Allow önce
   Edit yazar, sonra uyandırır (uyanan karar satırı Edit görür); bayat Allow ve Deny modu değiştirmez;
   tur yoksa `None`.
8. **`domain/usecases/advance_chat.py`**: taslağın modu doğumda satıra; bilinmeyen mod tutmadan
   reddedilir; var olan sohbette mod yok sayılır. Test: `tests/test_advance_chat.py`.
9. **`presentation/routes.py`**: `_chat_state(…, mode)`, modu okuyan tek yardımcı `chat_state`; `POST …/mode`; izin `{turn, mode}`;
    `UnknownMode` 400. Test: `tests/test_chats_api.py`: GET'te mod; yeni sohbet Edit; taslağın modu;
    POST mode 200/400/404 ve sohbet dosyasına dokunmuyor; iki sohbet; tur sürerken POST mode sonraki
    çağrıya ulaşıyor; Allow sunucuda Edit; retry'ın modu yok sayılıyor; 409 ve 202 modu taşıyor;
    `_asked` modu kapıdan seçiyor.

## Frontend

11. **`features/workspace/useChat.js`**: `pickMode` (`picked`), `answer` cevabın modunu yazar, `send`
    modu yalnız taslakta gönderir, `retry` mod göndermez. Test: `features/workspace/useChat.test.jsx`.
12. **`App.jsx`**: `lastMode` gider, `draftMode` gelir; seçici sohbetin modunu çizer. **`modes.js`**:
    `EDIT` gider. Test: `App.test.jsx`: yenileyince sohbetin modu; sohbet değişince kendi modu; seçim
    hemen çiziliyor ve POST ediliyor; ret geri dönüyor ve kart; Allow'dan sonra sunucunun modu (sunucu
    Ask derse Ask); taslağın modu ilk mesajla gidiyor ve yeni taslak Edit'te; retry gövdesinde mod
    yok.
13. `npm run build --prefix queen-agent/frontend`; dört takım tek tek.
