# Madde 491 · Süren tur uzun yoklamayla — plan

**Hedef:** `GET …/events` bir kez JSON ile cevap verip biter; ekran turu `after=<sürüm>` ile soran
bir döngüyle dinler. Ekranda hiçbir şey değişmez.

**Spec:** [m491](../specs/2026-10-22-queen-agent-m491-long-polling-design.md)

Önce testler yazılır ve kırmızı görülür, sonra kod. Yollar `queen-agent/` altında. Takımlar teker
teker koşar. Tünel açılmaz.

## Görev 1: Sunucu

1. **Testler, `backend/tests/test_chats_api.py`:**
   - yardımcılar: `_listen`, `_chunks`, `_data` gider; `_asked_once(client, pid, cid, after=None)` kapıyı
     bir kez sorar; `_heard` kapıyı `after=` ile turun sonuna kadar sorar ve cevapları döner;
     `_until_asked` ve `_asked` aynı döngüyle soruyu bekler;
   - *the events door* bölümü: tur yokken `{turn: null}` ve JSON; `after`'sız ilk cevap turu ve
     sürümü hemen veriyor; `after` ile her değişiklik bir cevap, iki değişiklik birleşmiş tek
     snapshot; sessizken (`BEAT_SECONDS` kısaltılmış) aynı sürüm; sayı olmayan `after` hemen; tur
     bitince `{turn: null}`; turun kendi hatası cümlesiyle; iki dinleyici aynı cevabı alıyor;
     sürüm geçişindeki tutuş biter.
2. **`backend/tests/test_last_activity.py`, `test_pin_archive.py`:** akışı sonuna kadar okumak yerine
   turun bitişini kapıyı yoklayarak bekleyen yerel bir yardımcı.
3. **`backend/features/workspace/presentation/routes.py`:** `get_events` tek cevap; `_listened`,
   `_frame`, `EVENT_HEADERS`, `json` ve `Response` import'ları silinir; `BEAT_SECONDS`'ın docstring'i.

## Görev 2: Ekran

4. **Testler, `frontend/src/features/workspace/useChat.test.jsx`:** sahte sunucuda `/events` her soruyu
   test cevaplayana kadar bekletir (`asks`, `say`); `streams()` yerine soruların yolları:
   - ilk soru `after`'sız, sonraki `?after=<sürüm>`; `{turn: null}` sormayı bitirir ve kaydı okutur;
   - düşen soru kartsız, 3 sn sonra aynı `after`'la yeniden soruluyor (sahte saat);
   - ekran ayrılınca havadaki sorunun cevabı çizilmiyor ve yenisi sorulmuyor;
   - kendi turu ekran dışındayken düşen soru yeniden soruluyor ve sonu duyuluyor;
   - `gaveUp`/`GAVE_UP`/`reach` testleri silinir.
5. **Testler, `frontend/src/App.test.jsx`:** aynı sahte kapı; `fetch` saplamalarından turu olanlar
   `/events`'i ona yollar; `hear` en yeni bekleyen soruyu cevaplar; kopma ve vazgeçme testleri
   yeniden deneme olur.
6. **`frontend/src/test-setup.js`:** `FakeEventSource` silinir. **`frontend/src/shared/api.js`** ve
   **`api.test.js`:** `reach` silinir.
7. **`frontend/src/features/workspace/useChat.js`:** `streams` → `listeners`; `follow` + `ask` döngüsü;
   `AGAIN_MS = 3000`; `gaveUp`, `GAVE_UP`, `probed`, `heard` bayrağı silinir; `letGo` haritadan çıkarır.

## Görev 3: Belgeler ve bitiş

8. **`CODE-STANDARD.md`**, *Stack*: uzun yoklama ve sebebi.
9. `queen-agent` altında (dist hariç) `EventSource`, `_listened`, `EVENT_HEADERS`, `reach(`, `GAVE_UP`,
   `event-stream` taranır — model servisininki kalır.
10. `npm run build --prefix queen-agent/frontend`; `python -m pytest queen-agent -q`, sonra
    `npm test --prefix queen-agent/frontend`. Commit'i ana ajan atar.
