# Madde 402 — Sonrakine bağlı karede geçiş yumuşar, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 3 · **Parça:** 402 · v8-3f · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`, kararlar yol haritasında: satır 402 ve *v8-3 —
QueenAgent'ın yeni listesi* ("Sonrakine bağlı karede geçiş yumuşar"). Metni Claude yazdı *(kullanıcı,
1 Ekim — "promptları sen yaz ben sonra incelicem commitle de")*; bu madde
`tmp/queen-editor-prompts.md`'nin "Sonrakine bağlı kare (402 — H3'e eklenir)" bölümünü kullanır.
DeepSeek'e hiçbir yerden gerçek istek gitmez.

## Bugün ne oluyor

400'den sonra H3 oturumunda `H3VideoPromptWriter` *(`data/xai_prompt_writer.py`)* Queen AI'a H3 metnini
system mesajı olarak, karenin fotoğrafını ve `Scenario: <senaryo>`'yu user mesajı olarak gönderiyor.
`asked()` loop'ta Loop metnini ekliyor; sonrakine bağlı kare H3 metnini tek başına alıyor, ve yazan
model sonraki kareyi hiç görmüyor. Döngü *(`domain/run_loop.py`)* yazarı `writer.write(words, mode,
source=under, scene=…)` ile soruyor; videonun vardığı resmi `_end_for(…)` yazardan **sonra** buluyor ve
yalnız üreticiye `end` olarak veriyor: bağlıda `linkedTo`'nun fotoğrafı, loop'ta karenin kendi
fotoğrafı, standartta hiçbiri. Bağlanacak karenin fotoğrafı yoksa `_end_for` `MissingEndFrame`
atıyor — ama yazar o zamana kadar sorulmuş oluyor.

## Kurallar

1. **Bağlı videonun yazarı sonraki karenin fotoğrafını da görür.** Yazara üreticinin aldığı `end`'in
   kendisi verilir — aynı resim, aynı `(ad, bayt)`. Queen AI'a iki resim gider, sırayla: önce bu karenin
   fotoğrafı *(Picture 1)*, sonra sonraki karenin *(Picture 2)*.
2. **Bağlı videonun talimatı H3 metni ve arkasında bağlı metin**, `tmp/queen-editor-prompts.md`'nin
   "Sonrakine bağlı kare (402 — H3'e eklenir)" bölümü, kelimesi kelimesine. Testler metnin tamamını
   değil anlamlı cümlelerini tutar; kelimesi kelimesine aynı olduğu uygulama turunda dosyayla
   karşılaştırılarak doğrulanır.
3. **Yalnız H3.** Bağlı metin Picture 2'yi anıyor, ve WAN'ın yazarına hiç resim gösterilmiyor: bağlı
   metin WAN'a gitmez. WAN ve ses bugünkü gibi sorulur — mesajları harfi harfine aynı *(404 onları
   değiştirir)*. Döngünün tek çağrı biçimi olduğu için ikisi de `end`'i alır ve yok sayar.
4. **Loop değişmez:** loop'un vardığı resim karenin kendi fotoğrafı; yazar onu bir kez gösterir,
   talimat H3 metni ve Loop metni. **Standart değişmez:** tek resim, H3 metni.
5. **Videonun vardığı resim yazardan önce bulunur, ve bir kez okunur:** aynı okuma hem yazara hem
   üreticiye gider. Bağlanacak karenin fotoğrafı yoksa kare bugünkü gibi kırmızıya döner
   *(`MissingEndFrame`, üç deneme)* — ve yazar hiç sorulmaz: üretilemeyecek bir video için istek
   harcanmaz.
6. **Soru bugünkü gibi sorulur:** iş prompt taşımıyorsa ve karenin sözleri varsa, iş başına bir kez.
   H3 üreticisinin yazdığı hizalama satırı *(`FL2VA_SENTENCE`)* değişmez.

## Yazılacak testler

Kırmızı koşuda eksik bir isim toplamayı durdurmasın diye yeni isim kullanıldığı yerde içe aktarılır
*(400'deki gibi)*.

### `test_video_prompt_writer.py` — H3 yazarı, bağlı metin, WAN ve ses

Yeni sabit: `NEXT = ("P1_0.png", b"NEXTDATA")` — sonraki karenin fotoğrafı. Yeni yardımcı
`_linked_rule()`, `_loop_rule()` gibi.

1. **Bağlı video Queen AI'a iki resmi sırayla gösteriyor** —
   `write(…, "linked", source=PHOTO, end=NEXT, scene=THRONE)` →
   `[(H3_VIDEO_INSTRUCTION + LINKED_RULE, "Scenario: " + THRONE, [PHOTO, NEXT])]`.
   `test_a_linked_video_gets_the_h3_text_alone_for_now`'ın yerine geçer.
2. **Bağlı metin ikinci fotoğrafa Picture 2 diyor, ve videonun orada bittiğini söylüyor** —
   `call the second photo Picture 2` ve `Picture 2 is the last frame of the video.`
3. **Bağlı metin geçişi ayrıntılı istiyor, iki fotoğrafı yeniden anlattırmıyor** —
   `Write the changes in detail, so the video flows into Picture 2 and never jumps.` ve
   `Never describe the two photos again.`
4. **Loop videosu resmini bir kez gösteriyor** — `write(…, "loop", source=PHOTO, end=PHOTO,
   scene="")` → `[(H3_VIDEO_INSTRUCTION + LOOP_RULE, "", [PHOTO])]`: bağlı metin yok, resim tek.
5. **WAN Picture 2'yi hiç duymuyor** — `VideoPromptWriter`'a `"linked"`, fotoğraf, sonraki fotoğraf ve
   senaryo verilince çağrı `[(VIDEO_INSTRUCTION, "kırmızı elbiseli kadın")]`.

**Değişen:** `test_the_sound_is_asked_as_before_whatever_else_it_is_handed` sese `end=NEXT`'i de verir
— mesaj yine bugünkü `Scene:` / `Motion:` satırları.

### `test_photo_usecases.py` — döngü yazara ne veriyor

`FakeWriter.write(prompts, mode="standard", source=None, end=None, scene="")` — `ends` listesi,
`sources`'ın yanında ayrı. Yeni yardımcı `write_one_video(mode, linked_to=None, numbers=(0, 1))`:
`render_one_video` gibi `0_a`'da tek video işi, galeride `numbers`'ın kareleri ve fotoğrafları; ama iş
prompt taşımıyor ve fotoğrafların sözleri var — yazar sorulsun diye; `(writer, generator, record)`
döner.

6. **Yazara üreticinin vardığı resim veriliyor** — üç mod, parametreli: standart → `None`; loop →
   `("0_a.png", b"0_a bytes")`; bağlı, `linkedTo="1_a"` → `("1_a.png", b"1_a bytes")`. Her birinde
   `writer.ends == generator.ends == [beklenen]`.
7. **Bağlanacak karenin fotoğrafı yoksa yazar sorulmuyor** — `numbers=(0,)`, iş `1_a`'ya bağlı:
   `writer.calls == []`, ve videonun hücresi `failed`.

**Bekçiler — değişmeden yeşil kalıyor:** H3 metninin, Loop metninin bütün testleri;
`test_a_plain_video_is_asked_for_nothing_extra` ve `test_a_frame_with_no_scenario_sends_the_photo_alone`
*(standart tek resim, H3 metni tek başına)*; `test_a_loop_video_is_asked_for_a_motion_that_returns`;
`test_the_h3_instruction_never_asks_for_dynv2` *(bağlı mod dahil — bağlı metinde de dynv2 yok)*;
`test_wan_is_asked_as_before_whatever_else_it_is_handed`, `test_wan_asks_for_the_same_returning_motion`;
döngünün soru testleri; bağlı videonun üretim testleri —
`test_a_linked_video_ends_on_the_next_frames_picture`,
`test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red`,
`test_a_linked_video_names_the_picture_it_ended_on`; H3 üreticisinin hizalama satırı testleri;
main.py'nin yazar kablosu testleri.

**Ekran:** değişmiyor, test yok.

## Bitti sayılır

Dört test satırı koşulur. `queen-editor` pytest'inde 1–5, değişen ses testi, 6'nın loop ve bağlı
hâlleri ve 7 kırmızı, doğru sebeple: yazarlar `end` almıyor; `LINKED_RULE` yok; döngü yazara vardığı
resmi vermiyor, ve resmi yazardan sonra buluyor. 6'nın standart hâli kırmızı koşuda da yeşil — sahte
yazarın varsayılanı `None`; uygulamadan sonra standart videoya resim uydurulmadığının bekçisi.
`queen-agent`'ın iki satırı ve `queen-editor` vitest'i yeşil.
