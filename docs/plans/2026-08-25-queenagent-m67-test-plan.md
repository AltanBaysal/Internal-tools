# Madde 67 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-25-queenagent-m67-durdurma-testler-design.md](../specs/2026-08-25-queenagent-m67-durdurma-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Testlerin konuşacağı adlar

Madde 66'nın dersi: içe aktarılamayan bir ad `pytest`i toplama hatasına düşürüyor ve suite kırmızı
değil bozuk oluyor. O yüzden **adlar bu turda doğar**, davranış ikinci turda.

- **`MemoryStops`** — `data/memory_stops.py`. Üç yolu var: `want(project_id, chat_id)`,
  `wanted(project_id, chat_id)`, `clear(project_id, chat_id)`. İçinde bir küme ve bir kilit; kilit
  çünkü sunucu çok iş parçacıklı ve iki istek aynı kaydı elliyor. Domain tarafında karşılığı
  `ports.py`'de bir `Stops` protokolü.
- **`Message.stopped: bool = False`** — `calls`'ın yanında, aynı kuralla: boşken diske yazılmaz.
- **Uç nokta:** `POST /api/projects/<pid>/chats/<cid>/stop`.
- **`stream_answer`** bir parametre daha alır: durdurma kaydı.

Bu turda **yalnız adlar** yazılır: sınıfın yolları vardır ama davranışı yoktur, alan vardır ama
kimse doldurmaz, uç nokta yoktur. Testler davranış üzerinde düşer.

## Dosyalar

`backend/tests/test_stops.py` *(yeni)* · `test_stream_answer.py` · `test_chats_api.py` ·
`test_file_chat_store.py` · `frontend/src/features/workspace/ChatScreen.test.jsx` ·
`frontend/src/App.test.jsx`

## Testler

### `test_stops.py` — dört test *(yeni dosya)*

Sorulmamış bir sohbet istenmemiş sayılıyor. `want` sonrası isteniyor. `clear` sonrası yine
istenmiyor. Bir sohbete konan bayrak **aynı projedeki başka bir sohbeti** etkilemiyor — kayıt
sohbet başına, proje başına değil.

### `test_stream_answer.py` — dört test

Var olan `ScriptedEngine` kullanılır; durdurma, ilk turdan sonra bayrağı koyan bir kayıtla
kurgulanır.

Motor bir daha çağrılmıyor ve üretim bitiyor. O ana kadar söylenen diske düşüyor. Düşen mesaj
durdurulmuş olarak işaretli. Hiç konuşmadan durdurulduysa hiçbir mesaj yazılmıyor — sohbette hâlâ
yalnız kullanıcının mesajı var. Ayrıca cevap bittiğinde bayrak temizlenmiş oluyor.

### `test_chats_api.py` — üç test

`POST .../stop` kabul ediliyor. Olmayan sohbet için 404. Sohbetin GET'i mesajın `stopped` alanını
taşıyor.

### `test_file_chat_store.py` — iki test

`stopped` yalnız doğruyken diske yazılıyor. Alanı taşımayan eski bir sohbet okununca mesajlar
durdurulmamış geliyor.

### `ChatScreen.test.jsx` — üç test

Cevap akarken durdurma düğmesi çiziliyor; boştayken çizilmiyor; basılınca kendisine verilen yol
çağrılıyor.

### `App.test.jsx` — iki test

Durdurulan bir sohbet **kendiliğinden yeniden istemiyor**: durdurmadan sonra `/answer` bir kez daha
çağrılmıyor. Kullanıcı yeni bir mesaj gönderince otomatik istek yeniden çalışıyor.

## Beklenen kırmızı

**Arka uçta 51, ön yüzde 3.** İkisini birbirinden ayırmak gerekiyor:

**Bu maddenin kendi testleri — 19 tanesi.** Adlar var ama hiçbiri bir şey yapmıyor: kayıt
`NotImplementedError` atıyor, alan hep yanlış, uç nokta 404 veriyor, düğme çizilmiyor.

**`test_stream_answer.py`'nin geri kalanı — 32 tanesi, mekanik sebeple.** `stream_answer` bir
parametre daha alıyor ve dosyadaki her çağrı onu geçiriyor; imza henüz değişmediği için hepsi
`TypeError` ile düşüyor. Davranışları bozuk değil, çağrıları henüz karşılıksız. İkinci tur imzayı
açtığında hepsi kendiliğinden yeşile döner — **dönmezlerse orada gerçek bir şey kırılmış demektir**,
ve bu satır o ayrımın kaydıdır.

**Parametre neden zorunlu:** varsayılan vermek 32 testi kırmızıya düşürmezdi, ama bağımlılığı
isteğe bağlıymış gibi gösterirdi. Kompozisyon kökü her zaman bir kayıt geçiriyor; geçirmeyen tek
şey testler, ve testlerin kolaylığı için üretim imzası yalan söylemez.

**`test_chats_api.py`'nin `_client`'ı bu turda değişmiyor.** Blueprint'in imzası da bir parametre
kazanacak, ama onu şimdi geçirmek dosyadaki bütün API testlerini `TypeError`'a düşürürdü — kazancı
olmayan bir kırmızı. İkinci tur ikisini birlikte açar.

## Bu turda yapılmayan

`stream_answer`'ın gövdesi, rotanın uç noktası, deponun yazma/okuma yolları, `ChatScreen`'in
düğmesi, `useChat`'in durdurma yolu — hiçbiri. `dist` derlenmez.
