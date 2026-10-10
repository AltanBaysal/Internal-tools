# Madde 461 · Tur sunucuda kendi başına koşar — plan

**Spec:** [2026-10-10-queen-agent-m461-tur-kendi-basina-design.md](../specs/2026-10-10-queen-agent-m461-tur-kendi-basina-design.md)

Her adımda önce test yazılır ve kırmızı görülür, sonra kod. Yollar `queen-agent/backend/` altında.

1. **`features/workspace/domain/turn.py`** — `status_of`, `Snapshot`, `Question`, `changed`, `applied`;
   `Progress` `stream_answer.py`'den buraya. Test: `tests/test_turn.py` — her durum, açık hat, son mesajı
   kullanıcının olan eski bir sohbet, başarısız ve durdurulmuş cevap, canlı tur (koşan, bekleyen,
   bitmiş); `applied`'ın her parçası ve sorunun `wait`'i. `chat.py`'den `is_owed_an_answer` ve
   `test_chat.py`'deki iki testi gider (`status_of`'un testlerine geçer).
2. **`domain/ports.py`** — `Stops` ve `Permissions` gider; `TurnControl` (`stopped`, `hold`,
   `decision`) ve `Turns` (`reserve`, `release`, `get`, `any_in`, `start`) gelir. `domain/permission.py`
   `Waiting`'i bırakır.
3. **`data/live_turns.py`** — `LiveTurn` ve `LiveTurns`. Test: `tests/test_live_turns.py` — rezervasyon,
   458'in sekiz iş parçacıklı bariyeri, bırakışın yalnız kendi turunu silmesi, Stop'un kimlikle,
   kesmenin Stop'tan sonra da gelse kesilmesi, kararın `wait`'le ve tur kimliğiyle, erken kararın
   yok sayılması, `decision`'ın Stop'la `None` dönmesi, `start`'ın parçaları uygulayıp önce bırakıp
   sonra bitirmesi, hatanın görüntüye geçmesi. `data/memory_stops.py`, `data/memory_permissions.py`,
   `tests/test_stops.py`, `tests/test_permissions.py` gider.
4. **`domain/usecases/append_message.py`** — üçüncü parametre sohbetin kendisi (`None` = yenisini aç);
   `chat_store.get` yok. Test: `tests/test_append_message.py`, `tests/test_delete_project.py` çağrıları.
5. **`domain/usecases/run_turn.py`** (`git mv stream_answer.py`) — verilen kayıt, `control`, okumasız
   son yazı, `EmptyMessage` → `EngineFailed(NOTHING)`. Test: `tests/test_run_turn.py` (`git mv
   test_stream_answer.py`) — sahte `control`'ler; saat ve temizlik testleri gider; kaydın okunmadığı.
6. **`domain/usecases/retry_turn.py`** — `drop_failed_answer.py`'nin yerine. Test:
   `tests/test_retry_turn.py` — cevapsız, başarısız (tek yazma, Continue here'in işareti), cevaplanmış,
   durdurulmuş, boş: hiçbir şey yazmıyor.
7. **Kurallar domain'e** (review'dan sonra): `domain/errors.py`'ye `ChatHeld`, `ChatFull`,
   `NothingToAnswer`, `VersionNotFound`, `ProjectAnswering`; `usecases/advance_chat.py` (`Started`,
   `Nothing`), `usecases/hold_chat.py`, `usecases/open_version.py`; `trim_chat` ve `delete_project`
   `turns`'ü alır; `ports.py`'ye `LiveTurn`. Test: `tests/test_advance_chat.py`,
   `tests/test_delete_project.py`.
8. **`presentation/routes.py`** — `make_workspace_bp(projects, chats, files, engine, turns)`; mesaj,
   Try again, Stop, izin, sohbeti okuma, sürüm, Continue here, proje silme; köprü `_sse(chat_id, turn)`
   ve `_told`, `BEAT_SECONDS`, `BUSY`, `PROJECT_BUSY`. Test: `tests/test_chats_api.py` — 409'lar, süren
   tur, geç Stop / erken Allow, tarayıcısız izin, okuma/yazma sayıları, sinyal, yazılmış cevapta Try
   again, art arda iki yazışın iki kartı; karelerin sırasını tutan testler `file-start` olmadan.
   Route'lar use case'lerin sonucunu ve hatalarını durum kodlarına çevirir.
9. **`main.py`** — `LiveTurns()`. Testlerin kurulumu: `test_files_api.py`, `test_last_activity.py`,
   `test_pin_archive.py`, `test_projects_api.py`. `BACKLOG.md`: `run_turn.py` adı, proje silme yarışı.
10. Dört suite birer birer; frontend testleri değişmeden geçmeli.
