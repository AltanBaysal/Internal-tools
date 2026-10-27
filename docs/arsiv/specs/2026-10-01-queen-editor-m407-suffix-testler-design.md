# Madde 407 — Prompt'u yazan modelin system prompt'una suffix, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 6 · **Parça:** 407 · v8-6 · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`, kararlar yol haritasının 407 satırında: Queen AI'ın
H3, WAN ve ses prompt'larını yazarken aldığı system prompt QueenAgent'taki suffix'le biter
*(kullanıcı, 30 Eylül — "queen editorde promptları yazana prompta queen editorde system promptunada
suffix ekleyelim")*, ve metin QueenAgent'takiyle birebir aynı *(kullanıcı, 30 Eylül — "evet")*.
QueenAgent'ın suffix'ine ve metnine dokunulmaz.

## Bugün ne oluyor

Üç yazar — WAN'ın `VideoPromptWriter`'ı, `H3VideoPromptWriter` ve `AudioPromptWriter`
([prompt_writer.py](../../../queen-editor/backend/features/photo_generation/data/prompt_writer.py))
— Queen AI'a kendi metnini system mesajı olarak gönderiyor; loop'ta `LOOP_RULE`, H3'ün sonrakine
bağlı karesinde `LINKED_RULE` metnin arkasına ekleniyor. Suffix hiçbirinde yok. QueenAgent'ın suffix'i
`SYSTEM_PROMPT_SUFFIX`
([prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py)); sahibi onu ileride
elle güçlendirecek *(queen-agent BACKLOG — "Suffix system prompt'u güçlendirilecek")*.

## Metin nasıl paylaşılır — karar

**Queen Editor kendi kopyasını tutar, ve Queen Editor'ün testi QueenAgent'ın dosyasını okuyup iki
metni karşılaştırır.** Sahibi QueenAgent'ın suffix'ini değiştirdiği gün `python -m pytest
queen-editor -q` kırmızıya döner ve kopyanın da değişmesi gerektiğini söyler: "birebir aynı" ya doğru
kalır ya yüksek sesle bozulur.

- **Çalışırken QueenAgent'ın dosyasını okumak değil:** iki araç birbirinden bağımsız bozulabilmeli
  (FOUNDATION Karar 8'in gerekçesi). İki backend de `backend` adlı bir paket; Queen Editor'ün kodu
  QueenAgent'ınkini ancak yol üzerinden yükleyerek okuyabilirdi, ve QueenAgent'ta bir yeniden
  adlandırma Queen Editor'ü Colab'da, çalışırken bozardı.
- **Ortak bir modül değil:** QueenAgent'ın koduna dokunmak gerekirdi — bu madde onu yasaklıyor — ve
  iki aracı çalışırken birbirine bağlayan yeni bir katman olurdu.
- **Bağ yalnız testte, ve tek yerde.** Bir aracın testinin öteki aracın dosyasını okumasının örneği
  var: `test_version_record.py` iki aracın da belgelerini okuyor.
- **QueenAgent'ın modülü yüklenerek okunur, metin olarak ayrıştırılmaz:** test, QueenAgent'ın
  gönderdiği değeri okur, sahibi onu nasıl yazarsa yazsın. `prompt.py` kendi kuralıyla hiçbir şey içe
  aktarmıyor; bu yüzden Queen Editor'ün test sürecinde yüklenmesi güvenli.

## Kurallar

1. **Her yazarın system mesajı suffix'le biter**, her modda: WAN, H3 ve ses; standart, loop ve
   sonrakine bağlı. Suffix modun kurallarından sonra gelir — `LINKED_RULE`'dan da sonra.
2. **Suffix'ten önce gelen metin bugünkünün aynısı.** Yazarın metni ve modun kuralı değişmez; yalnız
   sona suffix eklenir.
3. **Queen Editor'ün suffix'i QueenAgent'ınkiyle birebir aynı**, boşluğu ve satır sonları dahil.
4. **Taşıyıcı değişmez.** DeepSeek istemcisi prompt'tan habersiz kalır
   ([client.py](../../../queen-editor/backend/services/deepseek/client.py)); suffix'i yazarlar ekler,
   ve istemcinin testleri olduğu gibi kalır.

## Testler — `backend/tests/test_video_prompt_writer.py`

### Yardımcılar

- **`_sent(instruction)`** — yazarın Queen AI'a gönderdiği system mesajı: verilen metin, arkasında
  `prompt_writer.SYSTEM_PROMPT_SUFFIX`. Modül dosyanın başında içe aktarılır, ad çağrıldığında
  okunur: kırmızı turda henüz olmayan ad yalnız onu soran testi düşürür, dosyanın toplanmasını değil.
- **`_queen_agent_suffix()`** — QueenAgent'ın `prompt.py`'si yolundan yüklenir, ve
  `SYSTEM_PROMPT_SUFFIX`'i döner. Yol, depo kökünden: `queen-agent/backend/features/workspace/domain/
  prompt.py`.

### Değişen testler — gönderilen mesajın tamamını soranlar

Bugün system mesajını birebir karşılaştıran on iki test, beklenen mesajı `_sent(...)` ile yazar —
neyi sorduklarının geri kalanı aynı:

- `test_the_wan_writer_shows_queen_ai_the_photo_and_the_scenario`
- `test_a_wan_frame_with_no_scenario_sends_the_photo_alone`
- `test_the_sound_is_written_from_the_video_s_prompt_alone`
- `test_the_h3_writer_shows_queen_ai_the_photo_and_the_scenario`
- `test_a_frame_with_no_scenario_sends_the_photo_alone`
- `test_a_loop_video_is_asked_for_a_motion_that_returns`
- `test_a_plain_video_is_asked_for_nothing_extra`
- `test_a_linked_video_shows_queen_ai_both_pictures_in_order`
- `test_a_loop_video_shows_its_picture_once`
- `test_wan_asks_for_the_same_returning_motion`
- `test_wan_never_hears_of_picture_2`
- `test_the_sound_is_shown_no_picture_whatever_it_is_handed`

Bunlar kural 1'i ve 2'yi birlikte tutar: mesaj tam olarak "yazarın metni + modun kuralı + suffix".

### Yeni testler

- **`test_the_suffix_is_queen_agent_s_word_for_word`** — `prompt_writer.SYSTEM_PROMPT_SUFFIX ==
  _queen_agent_suffix()`. Kural 3. Hata mesajı Türkçe, iki dosyanın yolunu söyler: QueenAgent'ın
  suffix'i değişmişse Queen Editor'ünkinin de aynı yapılması gerektiğini.
- **`test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix`** — WAN, H3 ve ses yazarı
  standart, loop ve sonrakine bağlı modda yazar; gönderilen her system mesajı `_queen_agent_suffix()`
  ile biter. Ses yazarı modu dinlemiyor, ama üç yazara aynı üç modu sormak "her modda"yı tek bir
  döngüyle söyler. Kural 1, maddenin *Bitti sayılır*'ının cümlesiyle: QueenAgent'ın metniyle
  karşılaştırılır, kopyayla değil.

Kural 4'ün testi zaten var: `test_deepseek_client.py` system mesajını olduğu gibi gönderiyor.

## Kırmızı beklenen

- `_sent(...)` kullanan on iki test kırmızı: `prompt_writer`'da `SYSTEM_PROMPT_SUFFIX` yok.
- `test_the_suffix_is_queen_agent_s_word_for_word` kırmızı, aynı nedenle.
- `test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix` kırmızı: gönderilen mesaj
  yazarın metniyle bitiyor.
- Öteki her şey yeşil kalır; dosya toplanabiliyor.

## Bilinçli olarak yapılmayan

- QueenAgent'ın `prompt.py`'sine ve testlerine dokunulmaz.
- Suffix'in boş olmadığı sorulmaz: QueenAgent'ta boş suffix geçerli bir hâl
  (`test_prompt.py`), ve boşaldığı gün kopyanın da boşalması pin testinin işi.
- Ekran değişmez; dist yok. Yol haritasına dokunulmaz.
