# Madde 400 — H3 prompt'unu Queen AI yazar, fotoğrafı ve senaryoyu görerek, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 2 · **Parça:** 400 · v8-3b · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`, kararlar yol haritasında: satır 400 ve *v8-3 —
QueenAgent'ın yeni listesi*. Metinleri Claude yazdı *(kullanıcı, 1 Ekim — "promptları sen yaz ben
sonra incelicem commitle de")*; bu madde "H3 (400)" ve "Loop" metinlerini kullanır. Ön deneme yok
*(kullanıcı, 30 Eylül — "abi direk queen editore deneriz artık o durumu")*: DeepSeek'e hiçbir yerden
gerçek istek gitmez. Koşuda tek şey kullanıcının: Colab Secrets'taki `DEEPSEEK_API_KEY`'e — QueenAgent'ın
kullandığı aynı secret — bu defterin erişimini açmak.

## Bugün ne oluyor

H3 oturumunda video işinin prompt'u boşsa, sırası gelince `H3VideoPromptWriter` yazıyor
*(`data/xai_prompt_writer.py`)*: grok'a *(`services/xai/client.py`)* yalnız fotoğrafın SDXL etiketleri
gidiyor — ne fotoğrafın kendisi, ne karenin senaryosu. Döngü yazara yalnız karenin sözlerini ve modu
veriyor *(`run_loop.make_job` → `writer.write(prompts, mode)`)*. Queen Editor'de DeepSeek yok; defter
yalnız `XAI_API_KEY`'i okuyup sunucuya `QE_XAI_API_KEY` olarak veriyor.

## Kurallar

1. **H3 oturumunda H3 prompt'unu Queen AI (DeepSeek) yazar.** System mesajı H3 metni; user mesajında
   karenin üretilmiş fotoğrafı — resmin kendisi — ve senaryosu varsa `Scenario: <senaryo>`.
   Fotoğrafın SDXL etiketleri gitmez: model onların çizdiği resmi görüyor.
2. **Senaryosu olmayan kare yalnız fotoğrafı gönderir.** H3 metni o durumda ne yapılacağını
   söylüyor.
3. **Senaryo, prompt'un numarasıyla bulunur**, 397'nin kurduğu gibi: planın o numaralı fotoğraf
   satırındaki `scene`. Varyant, ikiz, yeni kelimelerle yeniden üretilen kare aynı senaryoyu görür;
   yeni satırlara senaryo yazılmaz. Başka prompt'un senaryosu gelmez; düz listeden gelen karenin
   senaryosu boştur.
4. **Mod:** standart — H3 metni; loop — H3 metni ve Loop metni, bugünkü gibi arkasına eklenir;
   sonrakine bağlı — **bu maddede H3 metni tek başına** *(sonraki karenin fotoğrafı ve bağlı metin
   402'de)*.
5. **Metinler kelimesi kelimesine** `tmp/queen-editor-prompts.md`'den: "H3 (400)" `H3_VIDEO_INSTRUCTION`'ın,
   "Loop" `LOOP_RULE`'un yerine. Testler metnin tamamını değil anlamlı cümlelerini tutar; metnin
   kelimesi kelimesine aynı olduğu uygulama turunda dosyayla karşılaştırılarak doğrulanır.
6. **DeepSeek'in taşıyıcısı xAI'ınki gibi:** `POST https://api.deepseek.com/chat/completions`,
   `Authorization: Bearer <anahtar>`, model `deepseek-flash`; resim yalnız user mesajında, içerik bir
   dizi — `image_url` parçası *(`data:<tür>;base64,…`, tür dosyanın adından)* ve `text` parçası. Söz
   yoksa `text` parçası hiç yok. Cevap `choices[0].message.content`, kırpılmış. Hata sunucunun kendi
   gövdesiyle; boş cevap hata. Anahtar kırpılır; anahtar yoksa ya da yalnız boşluksa istek hiç
   gitmez, ve `NotConfigured` `DEEPSEEK_API_KEY`'i ve Colab Secrets'ı adıyla söyler.
7. **Anahtar ortamdan:** sunucu `QE_DEEPSEEK_API_KEY`'i okur. Defter `DEEPSEEK_API_KEY`'i Colab
   Secrets'tan kırparak okur, sunucuya `QE_DEEPSEEK_API_KEY` olarak verir, ve kurulum anlatımının
   Secrets satırı onu adıyla sayar. `XAI_API_KEY` yerinde kalır *(406 kaldırır)*.
8. **WAN ve ses değişmez:** WAN oturumunun video prompt'unu ve her oturumun ses prompt'unu grok,
   bugünkü metin ve girdilerle yazar. Döngünün tek çağrı biçimi olduğu için ikisi de fotoğrafı ve
   senaryoyu alır ve yok sayar — grok'a giden mesaj bugünküyle harfi harfine aynı. Loop metninin
   değişmesi WAN'a da ulaşır; bu isteniyor.
9. **Soru bugünkü gibi sorulur:** yazar, iş prompt taşımıyorsa ve karenin sözleri varsa, iş başına bir
   kez sorulur; üç deneme tek soruyu paylaşır. H3 üreticisinin yazdığı resim hizalama satırı
   *(`I2VA_SENTENCE` / `FL2VA_SENTENCE`)* değişmez.

## Yazılacak testler

Kırmızı koşuda eksik bir isim toplamayı durdurmasın diye yeni modül ve yeni isimler kullanıldıkları
yerde içe aktarılır: pytest toplama hatasında bütün oturumu durdurur.

### `test_deepseek_client.py` — yeni, `services/deepseek/client.py`

`FakeHttp` xAI testindeki gibi — tek isteği kaydeder, testin kurduğu cevabı döner. İstemci
`DeepSeekClient(anahtar, "deepseek-flash", "https://api.deepseek.com/chat/completions", http=…,
timeout=120)`; soru `complete(talimat, söz, resimler)`, resimler `[(ad, bayt)]`.

1. **İstek modeli, talimatı, resmi ve sözü taşıyor** — adres, `Bearer k-1`, 120 sn, gövde: system
   düz metin; user içeriği `[image_url (data:image/png;base64,…), text]`. Cevap kırpılmış dönüyor.
2. **Resmin türü adından okunuyor** — `kare.jpg` → `data:image/jpeg;base64,…`.
3. **Söz yoksa user mesajında yalnız resim var** — `text` parçası hiç yok.
4. **HTTP hatası sunucunun kendi gövdesiyle** — 401 ve gövde mesajda.
5. **Beklenmeyen biçim gelenin kendisini gösteriyor.**
6. **Boş cevap hata**, boş prompt değil.
7. **Anahtar yoksa hiçbir şey sormadan söylüyor** — `NotConfigured`, istek yok, mesajda
   `DEEPSEEK_API_KEY` ve `Colab Secrets`.
8. **Anahtar başlığa kırpılmış gidiyor.**
9. **Yalnız boşluk olan anahtar anahtarsız sayılıyor.**

### `test_video_prompt_writer.py` — H3 yazarı, metinler, WAN ve ses

Yeni sahte: `FakeVisionClient.complete(system, text="", images=())` — her soruyu `(talimat, söz,
resimler)` olarak kaydeder. `PHOTO = ("P0_0.png", b"PNGDATA")`, `THRONE` bir senaryo.

10. **H3 yazarı Queen AI'a fotoğrafı ve senaryoyu gösteriyor** —
    `write({"photo": "score_9_up, …"}, "standard", source=PHOTO, scene=THRONE)` →
    `[(H3_VIDEO_INSTRUCTION, "Scenario: " + THRONE, [PHOTO])]`; SDXL etiketleri hiçbir parçada yok.
11. **Senaryosu olmayan kare yalnız fotoğrafı gönderiyor** — `(H3_VIDEO_INSTRUCTION, "", [PHOTO])`.
12. **Sonrakine bağlı kare bu maddede yalnız H3 metnini alıyor** — talimat `H3_VIDEO_INSTRUCTION`'ın
    kendisi.
13. **H3 metni konuşmasız senaryoda konuşma istemiyor** — `write no speech at all` ve
    `No one speaks.`
14. **H3 metni fotoğrafa Picture 1 diyor, ilk satırı koda bırakıyor** — `call the photo Picture 1` ve
    `Never write the line.`
15. **H3 metni senaryosuz karede ne yapılacağını söylüyor** —
    `If no scenario is given, write a small, natural motion for Picture 1.`
16. **Loop metni kameranın durduğunu söylüyor** — `The camera holds a static shot.` ve
    `The last frame is the first photo again`.
17. **WAN bugünkü gibi soruluyor, ne verilirse verilsin** — `VideoPromptWriter`'a fotoğraf ve senaryo
    verilince çağrı `[(VIDEO_INSTRUCTION, "kırmızı elbiseli kadın")]`.
18. **Ses bugünkü gibi soruluyor, ne verilirse verilsin** — `AudioPromptWriter`'a fotoğraf ve senaryo
    verilince mesaj bugünkü `Scene:` / `Motion:` satırları.

**Değişen:** H3 yazarının bugünkü testleri yeni çağrı biçimine geçiyor —
`test_the_h3_writer_converts_the_photo_prompt_with_its_own_instruction` 10'a dönüşüyor;
`test_the_h3_instruction_never_asks_for_dynv2` *(standart, loop, bağlı — gönderilen talimatta dynv2
yok)*, `test_a_loop_video_is_asked_for_a_motion_that_returns`,
`test_a_plain_video_is_asked_for_nothing_extra` `FakeVisionClient` ve fotoğrafla çağırıyor.
`test_the_h3_instruction_says_the_photo_is_the_first_frame` yeni cümleyi tutuyor:
`The photo is the first frame of the video.` Loop metninin iki testi yeni cümleleri tutuyor:
`comes back to the first pose` ve `shows as a stop each time the video starts again`; `same speed` ve
`slows down`.

### `test_photo_usecases.py` — döngü yazara ne veriyor

`FakeWriter.write(prompts, mode="standard", source=None, scene="")` — `sources` ve `scenes`
listeleri, `modes`'un yanında ayrı ayrı.

19. **Yazar videonun yapıldığı fotoğrafı görüyor** — `0_a.png` bayt'ları → `writer.sources ==
    [("0_a.png", b"PNGDATA")]`.
20. **Yazara karenin senaryosu veriliyor, prompt'un numarasıyla** — plan: 0 numaralı fotoğraf satırı
    `THRONE`, 1 numaralı `GARDEN`; video işi `1_a`'da → `writer.scenes == [GARDEN]`.
21. **İkiz kaynağının senaryosunu görüyor** — `P0_0` satırı `THRONE`; video işi `C1_P0_0`'da, ikizin
    satırında senaryo yok → `[THRONE]`.
22. **Düz listenin karesinin senaryosu boş** — `[""]`.

### `test_composition_root.py` — main.py'nin kablosu

23. **H3 oturumunun video prompt'u Queen AI'ın** — `QE_DEEPSEEK_API_KEY` boş, `h3`: video yazarı
    fotoğrafla sorulunca `DEEPSEEK_API_KEY`'i adıyla söyleyen bir hata.
24. **WAN oturumunun video prompt'u hâlâ grok'un** — `QE_XAI_API_KEY` boş, WAN: hata `XAI_API_KEY`
    diyor.
25. **H3 oturumunun ses prompt'u hâlâ grok'un** — ses yazarı `XAI_API_KEY` diyor.
26. **Anahtar ortamdan, model ve adres DeepSeek'in** — `QE_DEEPSEEK_API_KEY=ds-1` →
    `config.DEEPSEEK_API_KEY == "ds-1"`, `DEEPSEEK_MODEL == "deepseek-flash"`, `DEEPSEEK_URL`
    `https://api.deepseek.com/chat/completions`.

### `test_notebook_installs_the_producer_groups.py` — defter

27. **DeepSeek anahtarı Secrets'tan kırpılarak okunuyor** —
    `DEEPSEEK_API_KEY = (userdata.get("DEEPSEEK_API_KEY") or "").strip()`.
28. **Anahtar sunucuya gidiyor** — Flask hücresinde `"QE_DEEPSEEK_API_KEY": DEEPSEEK_API_KEY`.
29. **Kurulum anlatımı secret'ı adıyla sayıyor** — Secrets satırının hücresinde `DEEPSEEK_API_KEY`.

**Bekçiler — değişmeden yeşil kalıyor:** xAI istemcisinin bütün testleri; WAN'ın ve sesin bugünkü
yazar testleri; H3'ün üç bölüm testi; `test_wan_asks_for_the_same_returning_motion`; döngünün soru
testleri — `test_a_frame_with_no_photo_prompt_is_not_worth_an_ask`,
`test_the_three_attempts_of_one_job_spend_a_single_ask`, `test_a_model_that_will_not_answer_stops_the_run`,
`test_the_writer_is_told_which_mode_the_job_is_in`; H3 üreticisinin hizalama satırı testleri;
xAI yoklamasının defter testleri; `test_notebook_stays_readable`.

**Ekran:** değişmiyor, test yok.

## Bitti sayılır

Dört test satırı koşulur. `queen-editor` pytest'inde 1–21, 23–29 ve değişen H3 ve Loop testleri
kırmızı, doğru sebeple: `services/deepseek` yok; H3 yazarı `source` ve `scene` almıyor ve grok'a
etiketleri gönderiyor; metinler eski; döngü yazara fotoğraf ve senaryo vermiyor; `config`'te DeepSeek
yok; defter anahtarı okumuyor. 17, 18, 24 ve 25 bilinmeyen argümanla kırmızı. 22 kırmızı koşuda da
yeşil — sahte yazarın varsayılanı boş; uygulamadan sonra düz listenin karesine senaryo
uydurulmadığının bekçisi. `queen-agent`'ın iki satırı ve `queen-editor` vitest'i yeşil.
