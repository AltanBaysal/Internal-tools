# Madde 440 — Agent'ın kara kutusu, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** agent'ın her isteği kutudan geçer, hatada ve boş cevapta en çok beş kez yeniden gider,
cevap bütün döner ve ekranda bir kerede belirir; Stop yarım cevabı atar; beş denemede olmazsa
hatanın sözü kayda başarısız cevap olarak yazılır, kart olarak görünür, Try again'le yeniden
cevaplanır, ve doluluğa sayılmaz.

**Yaklaşım:** Her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m440](../specs/2026-10-09-queen-agent-m440-kara-kutu-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları ve ekrandaki her söz İngilizce.
- Yol haritasına ve queen-editor'e dokunulmaz.

---

## Görev 1: `domain/black_box.py` — kutu

- [ ] `backend/tests/test_black_box.py`, sahte engine'lerle: iyi cevap tek istekte, sözler ve
  çağrılar bütün; hatadan sonra aynı istek; boş ve boşluk cevap yeniden, `silence_is_an_answer`'la
  değil; beş hatada `failed="technical"` ve son hatanın sözü; beş boşta `NOTHING`; anahtarsızlık
  denenir; Stop'ta ikinci istek yok; hiç fırlatmaz; `usage`. Kırmızı.
- [ ] `black_box.py`: `TRIES`, `NOTHING`, `TECHNICAL`, `Answer`, `ask(…, silence_is_an_answer)`;
  445'in yeri bir yorumla. Yeşil.

## Görev 2: `chat.py` — `failed`, doluluk, açık satır

- [ ] `test_chat.py`: başarısız cevap `chat_size`'a, `is_full`'a, `trim_point`'e sayılmaz;
  `sent_messages` atlar; `with_open_line` ilk satırda ve bir sürümde yalnız açık satırı değiştirir.
  Kırmızı.
- [ ] `chat.py`: `Message.failed`, `sent_messages`, `_size`, `with_open_line`. Yeşil.
- [ ] `append_message.py` (`failed` parametresi, `_with` → `with_open_line`), `trim_chat.py`
  (`_with_last` → `with_open_line`). Bugünkü testleri yeşil.

## Görev 3: `file_chat_store.py` — kayıt

- [ ] `test_file_chat_store.py`: `failed` yazılır ve okunur; boşken diskte yok. Kırmızı.
- [ ] `_message_json`, `_as_message`. Yeşil.

## Görev 4: `stream_answer.py` — döngü kutudan geçer

- [ ] `test_stream_answer.py`: söz parçası yok; hatadan sonra aynı cevap; dosya yazıp susan tur
  bitmiş sayılır ve yeniden sorulmaz, Madde 38'in testleri olduğu gibi — düzenleyip susan da; yalnız
  okuyup ya da *"Already there"* alıp susan tur yeniden sorulur; beş hatada başarısız cevap
  (adımlar, dosyalar, önceki sözler yok, başka istek yok); durmuş turda söz yok
  (`test_what_was_already_said_is_kept` tersine); Stop'ta yeniden istek yok; başarısız cevap sonraki
  turda gönderilmez. Bugünkü testlerin söz parçasına ve yarım cevaba bakan iddiaları yeni kurala
  geçer. Kırmızı.
- [ ] `test_append_message.py`: dosyaya yazmış sözsüz cevap kayda geçer. Kırmızı.
- [ ] `stream_answer.py`: `_Noting` (yazıları not eden dosya deposu), `ask`
  (`silence_is_an_answer=writes.wrote`), `failed`, stop; `EngineFailed`'ın yorumu.
  `append_message.py`: `wrote`. `ports.py`'nin
  `Engine` belgesi. Yeşil.

## Görev 5: Try again — `drop_failed_answer.py` ve route

- [ ] `test_chats_api.py`: kayıtta `failed`; akışta `chunk` yok; beş hatadan sonra `done`, kayıtta
  başarısız cevap; Try again çıkarıp yeniden cevaplar; kırpma işareti sorusuna geçer; dolu sohbette
  ret ve kart kalır. Bugünkü `chunk`'a ve `error`'a bakan testler yeni kurala geçer. Kırmızı.
- [ ] `drop_failed_answer.py`; `routes.py`: `_chat_json`'a `failed`, `_sse`'den söz dalı, sözsüz
  kapıda `drop_failed_answer`, `box.NOTHING`. Yeşil.
- [ ] `python -m pytest queen-agent -q`.

## Görev 6: ekran — bekleyiş, belirme, kart

- [ ] `ChatScreen.test.jsx`: bekleyiş söz çizmez; `arrived` mesajı `msg--arrived`; başarısız cevap kart,
  hatanın sözüyle, saatsiz; Try again yalnız son mesajken, tur sürmüyorken ve `onAnswerAgain`'le,
  yazı kutusundan değil; durmuş cevap dosya kartları, `Stopped`, saat sırasıyla, damgası saat yalnız;
  dipteki okur büyüyen bekleyişle iner; `FailureCard` kendi dosyasında. `streamingText`
  testleri kalkar ya da bekleyişe geçer. Kırmızı.
- [ ] `FailureCard.jsx`, `ChatScreen.jsx`, `workspace.css`. Yeşil.
- [ ] `App.test.jsx`: cevap tur bitince görünür, akarken görünmez; Try again'in ilk olayında kayıt
  yeniden okunur, kart gider, sözsüz istek oturumun modunu taşır (Plan'da `"plan"`); gelen cevap
  `msg--arrived`. `chunk`'lu akışlar yeni kurala geçer. Kırmızı.
- [ ] `useChat.js` (`arrived`, `chat` olayında yeniden okuma, `answerAgain`, sözsüz istekte mod),
  `App.jsx`. Yeşil.

## Görev 7: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
