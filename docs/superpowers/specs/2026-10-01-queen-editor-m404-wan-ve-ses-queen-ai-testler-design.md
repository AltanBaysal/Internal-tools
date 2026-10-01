# Madde 404 — WAN'ın video prompt'unu ve ses prompt'unu Queen AI yazar, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 5 · **Parça:** 404 · v8-3d · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`, kararlar yol haritasının 404 satırında: "1 Ekim'de
netleşti" *(kullanıcı — "wan değişsin sesi katma abi ve mmaudio da video promptundan alsın")*, ve her
prompt kendi turunda *(29 Eylül kararı)*. Metinleri Claude yazdı *(kullanıcı, 1 Ekim — "promptları sen
yaz ben sonra incelicem commitle de")*; bu madde `tmp/queen-editor-prompts.md`'nin "WAN (404)" ve
"Ses — MMAudio (404)" bölümlerini kullanır. DeepSeek'e hiçbir yerden gerçek istek gitmez.

## Bugün ne oluyor

`data/xai_prompt_writer.py`'de üç yazar var. `H3VideoPromptWriter` Queen AI'a *(DeepSeek,
`services/deepseek/client.py`)* H3 metnini, karenin fotoğrafını ve `Scenario: <senaryo>`'yu gönderiyor
(400, 402). `VideoPromptWriter` (WAN) ve `AudioPromptWriter` hâlâ grok'a *(`services/xai/client.py`)*
gidiyor: WAN'a fotoğrafın SDXL etiketleri ve eski `VIDEO_INSTRUCTION`, sese `Scene: <fotoğrafın
sözleri>` ve `Motion: <videonun prompt'u>` ve eski `AUDIO_INSTRUCTION`; `source`, `end`, `scene`'i yok
sayıyorlar. `main.py` WAN'ı ve sesi `_xai`'a bağlıyor. Döngü *(`run_loop._unwritten`)* bir işi, karenin
herhangi bir sözü varsa yazdırıyor — ses için de: videonun prompt'u yokken bile fotoğrafın sözleri
yetiyor.

## Kurallar

1. **WAN'ın video prompt'unu Queen AI yazar, H3'ünki gibi:** system mesajı WAN metni; user mesajında
   karenin fotoğrafı — resmin kendisi — ve senaryosu varsa `Scenario: <senaryo>`. Fotoğrafın SDXL
   etiketleri gitmez.
2. **Senaryosu olmayan kare yalnız fotoğrafı gönderir.** WAN metni o durumda ne yapılacağını söylüyor.
3. **WAN'ın modu:** standart — WAN metni; loop — WAN metni ve arkasında Loop metni, bugünkü gibi;
   sonrakine bağlı — WAN metni tek başına ve tek resim. Bağlı metin H3'ündür; WAN'a sonraki karenin
   fotoğrafı gösterilmez.
4. **Ses prompt'unu Queen AI yazar, yalnız videonun prompt'undan:** system mesajı ses metni; user
   mesajında `Video prompt: <videonun prompt'u>`. Fotoğrafın sözleri gitmez, hiç resim gitmez. Mod,
   `source`, `end`, `scene` alınır ve yok sayılır — döngünün tek çağrı biçimi.
5. **Her prompt kendi turunda:** ses, videodan ayrı bir istekle yazılır — bugünkü gibi.
6. **Videonun prompt'u yoksa ses yazarı sorulmaz** — döngünün "çevrilecek bir şey yok" kuralı, sesin
   kendi malzemesiyle: ses yalnız videonun prompt'undan yazıldığı için, karenin fotoğrafının sözü olsa
   da videonun prompt'u yoksa yazar sorulmaz ve ses bugünkü sözsüz kare gibi boş prompt'la üretilir.
   Videonun prompt'u henüz kayıtta değilse — video kendi prompt'unu taşıyıp daha üretilmediyse — ses
   bekler: video üretilince prompt'u kayda girer ve ses o zaman yazılır. Video ve sesin kuralı bu;
   video işinin kuralı bugünkü gibi — karenin herhangi bir sözü.
7. **Metinler kelimesi kelimesine** `tmp/queen-editor-prompts.md`'den: "WAN (404)" `VIDEO_INSTRUCTION`'ın,
   "Ses — MMAudio (404)" `AUDIO_INSTRUCTION`'ın yerine; dosyanın alışkanlığıyla üç tırnağın içinde
   baştan ve sondan birer satır sonu. `H3_VIDEO_INSTRUCTION`, `LOOP_RULE`, `LINKED_RULE` değişmez.
   Testler metnin tamamını değil anlamlı cümlelerini tutar; kelimesi kelimesine aynı olduğu uygulama
   turunda dosyayla karşılaştırılarak doğrulanır.
8. **Üç yazar da tek Queen AI istemcisine bağlı** *(`main.py`)*; WAN oturumunda da, H3 oturumunda da.
   Grok'u hiçbir yazar sormaz. xAI istemcisinin dosyası, `config`'teki xAI satırları ve defterin xAI
   satırları yerinde kalır *(406 siler)*. Ekranda model seçimi yok — ekran değişmez.

## Yazılacak testler

### `test_video_prompt_writer.py` — WAN ve ses yazarları, metinler

Grok biçimli `FakeClient` *(`complete(system, user)`)* kalkar: artık her yazar `FakeVisionClient`
*(`complete(system, text="", images=())`, her soruyu `(talimat, söz, resimler)` olarak kaydeder)* ile
sorulur.

1. **WAN yazarı Queen AI'a fotoğrafı ve senaryoyu gösteriyor** — `VideoPromptWriter(client).write(
   {"photo": "score_9_up, …"}, "standard", source=PHOTO, scene=THRONE)` → `[(VIDEO_INSTRUCTION,
   "Scenario: " + THRONE, [PHOTO])]`, ve yazılan cevap dönüyor. Bugünkü
   `test_the_photo_prompt_is_what_the_model_is_asked_to_convert` ve
   `test_wan_is_asked_as_before_whatever_else_it_is_handed`'in yerine.
2. **Senaryosu olmayan WAN karesi yalnız fotoğrafı gönderiyor** — `(VIDEO_INSTRUCTION, "", [PHOTO])`.
3. **WAN metni hareketi istiyor, fotoğrafı yeniden anlattırmıyor, kamerayı tutuyor** —
   `Never describe the photo again.`, `Keep the camera static: no camera movement, no zoom, no pan.`
   Bugünkü `test_the_instruction_says_what_wan_needs_and_what_to_leave_out`'un yerine.
4. **WAN metni sese yer vermiyor** — `Wan makes no sound.` ve `Write no sounds and no spoken words.`
5. **WAN metni senaryosuz karede ne yapılacağını söylüyor** —
   `If no scenario is given, write a small, natural motion for the photo.`
6. **WAN loop'ta aynı dönen hareketi istiyor** — `write(…, "loop", source=PHOTO, scene="")` →
   `[(VIDEO_INSTRUCTION + LOOP_RULE, "", [PHOTO])]`. `test_wan_asks_for_the_same_returning_motion`
   bu çağrı biçimine geçer.
7. **WAN Picture 2'yi hiç duymuyor** — `"linked"`, `source=PHOTO`, `end=NEXT`, `scene=THRONE` →
   `[(VIDEO_INSTRUCTION, "Scenario: " + THRONE, [PHOTO])]`: bağlı metin yok, resim tek.
   `test_wan_never_hears_of_picture_2` yeni cevabı tutar.
8. **Ses yalnız videonun prompt'undan yazılıyor** — `AudioPromptWriter(client).write({"photo":
   "kırmızı elbiseli kadın", "video": "kadın başını çeviriyor"})` → `[(AUDIO_INSTRUCTION,
   "Video prompt: kadın başını çeviriyor", [])]`. Bugünkü `test_the_sound_is_written_from_both_prompts`'un
   yerine; `test_a_frame_with_no_video_prompt_still_sends_what_it_has` kalkar *(kural 6: o kare artık
   sorulmaz)*.
9. **Sese resim ve fotoğrafın sözü gitmiyor, ne verilirse verilsin** — `source`, `end=NEXT`,
   `scene=THRONE` verilince yine `[(AUDIO_INSTRUCTION, "Video prompt: kadın dönüyor", [])]`.
   `test_the_sound_is_asked_as_before_whatever_else_it_is_handed`'in yerine.
10. **Ses metni videonun prompt'undan yazdırıyor** — `The video prompt says what happens in the video.`
    ve `Write only the sounds the video prompt implies.`

**Değişen, aynı cümleyle yeşil kalan:** `test_the_sound_instruction_asks_for_the_scenes_own_sounds`
(`No music`, `No speech` yeni metinde de var) ve `test_the_sound_writer_takes_the_mode_and_ignores_it`
`FakeVisionClient`'a geçer.

### `test_photo_usecases.py` — döngü sesi ne zaman yazdırıyor

11. **Videosunun prompt'u olmayan ses yazarı sormuyor** — fotoğrafın sözü `kırmızı elbiseli kadın`;
    video üretilmiş ama satırında prompt boş; prompt'suz ses işi; ses yazarı var → `writer.calls ==
    []`, ve ses boş prompt'la üretiliyor.
12. **Ses, videonun kendi prompt'u kayda girince yazılıyor** — video işi kullanıcının prompt'unu
    taşıyor (`elini kaldırıyor`), ses işi prompt'suz, ikisinin de üreticisi var, yalnız sesin yazarı
    var → ses yazarı bir kez soruluyor ve gördüğü `{"photo": …, "video": "elini kaldırıyor"}`; ses o
    cevapla üretiliyor.

**İsmi değişen:** `test_a_sound_job_is_written_from_the_frames_two_prompts` →
`test_a_sound_job_s_writer_is_handed_the_frame_s_words` — döngü yazara karenin bütün sözlerini verir,
yazar videonunkini seçer; iddiası aynı.

### `test_composition_root.py` — main.py'nin kablosu

13. **WAN oturumunun video prompt'u Queen AI'ın** — `QE_DEEPSEEK_API_KEY` boş, WAN: hata
    `DEEPSEEK_API_KEY` diyor. `test_a_wan_session_s_video_prompt_is_still_grok_s`'in yerine.
14. **Her oturumun ses prompt'u Queen AI'ın** — WAN ve H3, parametreli: ses yazarı `DEEPSEEK_API_KEY`
    diyor. `test_an_h3_session_s_sound_prompt_is_still_grok_s`'in yerine.

**Bekçiler — değişmeden yeşil kalıyor:** H3 yazarının, H3 metninin, Loop ve bağlı metnin bütün
testleri; DeepSeek ve xAI istemcisinin testleri; döngünün soru testleri —
`test_a_frame_with_no_photo_prompt_is_not_worth_an_ask`, `test_the_three_attempts_of_one_job_spend_a_single_ask`,
`test_a_model_that_will_not_answer_stops_the_run`, `test_a_sound_is_written_seeing_the_video_s_written_prompt`,
403'ün yazma testleri; `test_producer_contract.py` *(yazarsız koşu kaydın sözlerine hiç sormaz)*;
defterin xAI testleri *(406 değiştirir)*; `test_an_h3_session_s_video_prompt_is_queen_ai_s`.

**Ekran:** değişmiyor, test yok.

## Bitti sayılır

Dört test satırı koşulur. `queen-editor` pytest'inde 1–9, 11–14 kırmızı, doğru sebeple: WAN yazarı
grok çağrı biçimiyle soruyor ve fotoğrafı, senaryoyu göndermiyor; metinler eski; ses iki satırı
gönderiyor; döngü sesi fotoğrafın sözüyle yazdırıyor; `main.py` WAN'ı ve sesi grok'a bağlıyor. 10 eski
metinde yok — kırmızı. 12'de bugün ses yazarı video üretilmeden, yalnız fotoğrafın sözüyle soruluyor —
kırmızı. `queen-agent`'ın iki satırı ve `queen-editor` vitest'i yeşil.
