# Madde 426 · Videoda mutlu son — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
426 · v9-2 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Kod için hiçbir şey: maddenin 8 Ekim'deki hizalaması ve 9 Ekim'de Civitai'den okunanlar yetiyor.
**Çıktıyı değiştirir:** kullanıcı roadmap bitince Colab'da dener *(başlıktaki 8 Ekim kuralı — "roadmpş
sonuna kdar koş benş bekleme")*. Notebook bu dalı çektiği için push'tan sonra: düğme açıkken üretilen
H3 videosunun sonunda boşalmanın görülüp duyulduğu, ve düğme kapalıyken videonun bugünkü gibi çıktığı
orada görülür.

## Ne, neden

Kullanıcı videoda bir "mutlu son" istiyor *(8 Ekim — "mutlu son içinde bu modeli lora olarak ekleyip
kapatalım videoda böyle bir özellik olsun")*. "Bu model" HMCumshot, H3 için olan tek model. Hizalamada:
video panelinde, *Video uzunluğu*'nun altında bir *Mutlu son* düğmesi; varsayılanı kapalı, ve uzunluk
gibi projeye kaydedilir. Açıkken H3 videosu HMCumshot LoRA'sıyla üretilir, ve notebook LoRA'yı indirir.

**Sürüm ve güç — Claude'un kararı, maddede:** v1.0 *(Civitai model 2857340, sürüm **3329529**,
`HMCumshot_V1.0.safetensors`, 302.898,77 KB, SHA256
`634C39CFCBFD9421A2D7B5ADC62573FC232384C4C75E003C2E11D3408AD0765C`)*, güç **0.7** — yazarın önerisi
("I recommend using strength 0.7"). v1.0'ın **tetik kelimesi yok**; v0.5'inki (`cumshot`) eklenmez.

**Prompt da sonu anlatır.** Yazarın notları: "this is mostly prompting", "A thorough description of
the cum texture helps a lot!", "Sound is still off, I recommend adding explicit sound description in
your prompts". O yüzden düğme açıkken Queen AI'ın H3 talimatına bir parça eklenir: video boşalmayla
biter, boşalmanın dokusu ve sesi açıkça anlatılır.

## Görülecek olan

- Video panelinde, Kareden'de de Referanstan'da da, *Video uzunluğu*'nun hemen altında **Mutlu son**:
  aynı `Mono` başlık, aynı `wf-segment`, iki düğme — **Kapalı** · **Açık** (`aria-label` *"Mutlu son
  kapalı"*, *"Mutlu son açık"*), seçili olan `is-on`. Uzunluğun komşusu, uzunluğun biçiminde: panelde
  bir açma–kapama bileşeni yok, ve iki seçenekli bir segment uzunluğun üç seçeneklisinin aynısı.
- Basınca hemen değişir ve projeye yazılır; yazılamazsa eski hâline döner ve hatanın cümlesi panelin
  kırmızı kartında — uzunluğun kuralı *(424)*.
- Proje yeniden açılınca düğme kaydedildiği yerde. Hiç kaydedilmediyse **Kapalı**.
- Açıkken, uzunluğu söyleyen her cümle mutlu sonu da söyler: *"… alır. 8 sn, mutlu son."* —
  Kareden'in satırı, kopya uyarısı, Referanstan'ın *"… kart."* satırı, karenin sayfasında Yeniden
  üret'in notu ve Tekrar dene'nin *"Aynı kare yeniden denenir."*'i. Kapalıyken cümleler bugünkü gibi.
  Uzunluk okunamadıysa ama düğme açıksa: *" Mutlu son."*
- Ses paneli düğmeyi çizmez; video satırı okunmadan da çizilmez — uzunluğun kuralı.

## Kurallar

1. **İş, kuyruğa girdiği andaki düğmeyi taşır** — uzunluk gibi *(422: "Eklendiği uzunlukta")*. Açıkken
   işin plan satırında `"happyEnding": true`; **kapalıyken alan hiç yazılmaz**, ve plan satırı bugünkü
   gibi okunur. Bekleyen iş, düğme sonradan değişse de taşıdığıyla üretilir.
2. **Uzunluğun girdiği her kapı:** Kareden (`queue_layer`, yalnız video işi), Referanstan
   (`queue_references`), Yeniden üret (`regenerate`, yalnız video), Tekrar dene (`retry_frame`,
   `retry_failed`). Tekrar dene kırmızı videoyu **o anki** düğmeyle yeniden kuyruğa koyar, uzunluğu o
   anki uzunlukla koyduğu gibi: satırı ikisinden biri değiştiyse yeniden yazılır, ikisi de aynıysa
   hiçbir şey eklenmez. İkisi tek seferde, tek satırla.
3. **Açıkken grafik:** iki H3 grafiğinin LoRA yığınında (`"2678"`, DaSiWa'nın `DaSiWa_LTX2LoraLoader`'ı,
   `stack_data` JSON'u) ilk boş yuva — `"lora": "None"` olan ilki, bugün 2. yuva — `{"on": true,
   "lora": "HMCumshot_V1.0.safetensors", "str": 0.7}` olur; yuvanın `vs` ve `as`'ı olduğu gibi (1, 1),
   Motion Booster'ınki gibi. I2VA, FL2VA, ve I2VA grafiğinde koşan REF2VA. **Kapalıyken grafik
   bugünkünün aynısı** — yığına dokunulmaz. Boş yuva yoksa ya da yığın düğümü yoksa iş Türkçe bir
   cümleyle düşer: grafik değişmiş demektir.
4. **Açıkken talimat:** `H3_VIDEO_INSTRUCTION` (+ modun kuralı) + `HAPPY_ENDING_RULE`; ardından her zamanki
   gibi `SYSTEM_PROMPT_SUFFIX`. **Kapalıyken talimat bugünkünün kelimesi kelimesine aynısı.** Parça
   İngilizce, talimatın kendi dilinde: video boşalmayla biter; boşalma `[Shot 1]`'in son olayı; dokusu
   somut kelimelerle (renk, kıvam, fışkırışı, nereye düştüğü, akışı, yayılışı); sesi `overall_soundscape`'te
   açıkça. Uzunluk söylemez *(421'in kuralı)*, tetik kelimesi istemez.
5. **Notebook:** `CIVITAI_H3`'e bir satır — `(3329529, LORA, "HMCumshot_V1.0.safetensors", "H3 HMCumshot
   v1.0")`. `civitai_fetch` ile, önce HF aynasından; aynada yoksa Civitai'den iner ve aynaya çıkar.
   `MIRRORLESS`'a girmez: brif aynayı istiyor, ve dosya denemede değil, bir özelliğin dosyası.
6. **Video grubu (`model_groups.GROUPS["video"]`) dosyayı sayar.** Neden: grup "bu üretici bu makinede
   her işini yapabilir mi"nin cevabı. Düğmesi açık bir iş bu dosyayı yükler; dosya yokken ComfyUI'nin
   ne yapacağı — işi reddetmesi mi, DaSiWa'nın yükleyicisinin yuvayı sessizce atlaması mı — bilinmiyor,
   ve sessizce atlarsa kullanıcı LoRA'sız bir videoyu mutlu sonlu sanar. Grupta olunca panel dosya
   yokken *"kurulu değil"* der. Bedeli yok: notebook dosyayı video kutusu işaretliyken her zaman
   indirir, bu dal çekilip notebook koşunca dosya orada. Mystic XXX'in tersi: o yığında değil, grup
   onu saymıyor. Motion Booster'ınki gibi, yığının JSON'unda — model taramasının göremediği yerde.
   Disk tahmini (`~37 GiB`) değişmez: 0,3 GiB, 5 GiB payın içinde.

## Birimler

### Yeni — `photo_generation` özelliğinde

- **`domain/happy_ending.py`** — `InvalidSwitch` ve `check(on)`: `bool` dışındaki her şeyi *"Mutlu son
  açık ya da kapalı olmalı."* ile reddeder.
- **`domain/video_settings.py`** — bir video işinin projeden taşıdığı, tek yerde:
  - `HAPPY_ENDING = "happyEnding"` — plan satırındaki alanın adı; döngü de bunu okur.
  - `carried(length, ending, project)` — `{"seconds": length(project)}` (uzunluk verildiyse) +
    `{"happyEnding": True}` (düğme açıksa). `video_length.carried`'ın yerine; üç kuyruk kapısı bunu
    çağırır.
  - `as_set_now(plan_store, project, fids, length, ending)` — `video_length.at_length_now`'ın yerine,
    iki ayarı birden: her karenin en son video satırı o anki ayarlarla; `ending` verildiyse eski
    `happyEnding` önce çıkarılır, sonra `carried`'ın cevabı yazılır; satır değişmediyse eklenmez; tek
    `append`.
- **`data/happy_ending_store.py`** — `DriveHappyEndingStore(storage)`: `project_exists`, `read` (`bool`
  ya da `None`; okunamayan her şey `None`), `write` (`{"on": bool}`). Dosya `happy_ending.json` —
  kendi dosyası *(CODE-STANDARD, Separation of concerns: ayrı bir soru, ayrı bir basışta yazılır)*.
- **`domain/usecases/happy_ending.py`** — `get_happy_ending(switches, project)` (proje yoksa
  `ProjectMissing`; kayıtlı `True` değilse `False`) ve `save_happy_ending(switches, project, on)` (önce
  değer, sonra proje, sonra yazar).
- **`presentation/happy_ending_routes.py`** — `make_happy_ending_blueprint(get, save)`:
  `GET /api/projects/<proje>/happy-ending` → `{"on": false}`; `PUT` gövde `{"on": true}` → `204`;
  `InvalidSwitch` → `400`, `ProjectMissing` → `404`, ikisinde de `{"error": cümle}`.
- **`domain/ports.py`** — `HappyEndingStore`; `PhotoGenerator.generate`'e ve `PromptWriter.write`'a
  `happy_ending=False`.

### Değişen

- **`domain/video_length.py`** — `carried` ve `at_length_now` `video_settings`'e taşınır; `LENGTHS`,
  `DEFAULT`, `InvalidLength`, `check` kalır.
- **`queue_layer`, `queue_references`, `regenerate`** — `ending=None`;
  `video_settings.carried(length, ending, project)`.
- **`retry_frame`, `retry_failed`** — `ending=None`; `video_settings.as_set_now(…, length, ending)`.
- **`run_loop`** — `happy = bool(current.get(video_settings.HAPPY_ENDING))`; yazara ve üreticiye
  `happy_ending=happy`. Kuyruğun tek çağrı biçimi: her üretici ve her yazar alır *(422'nin gerekçesi)*.
  Üretilen satıra yazılmaz: neyin istendiği plan satırında, kalıcı; kimse satırdan okumuyor.
- **`ComfyH3VideoGenerator.generate(…, happy_ending=False)`** — açıksa grafik yüklendikten sonra
  `_with_happy_ending(workflow, name)`; üç kipte.
- **`ComfyPhotoGenerator`, `MMAudioGenerator`** — `happy_ending=False` alır, görmezden gelir.
- **`H3VideoPromptWriter.write(…, happy_ending=False)`** — açıksa `HAPPY_ENDING_RULE` eklenir.
  **`AudioPromptWriter`** alır, görmezden gelir.
- **`main.py`** — `_happy_endings = DriveHappyEndingStore(_storage)`,
  `_happy_ending = partial(get_happy_ending, _happy_endings)`; beş kapıya `ending=_happy_ending`;
  blueprint `create_app`'in listesinde.
- **`producers/domain/model_groups.py`** — `GROUPS["video"]`'a `{"folder": "loras", "name":
  "HMCumshot_V1.0.safetensors"}`.
- **`queeneditor.ipynb`** — `CIVITAI_H3`'e satır *(kural 5)*.
- **Sahte üreticiler ve yazarlar** (testlerde) — imzalarına `happy_ending=False`.

### Frontend

- **`shared/api.js`** — `getHappyEnding(project)` → `body.on`; `saveHappyEnding(project, on)` → PUT
  `{ on }`.
- **`useVideoLength.js` → `useVideoSettings.js`** — 424'ün kancasının gövdesi bir fabrikaya döner,
  `videoSetting(read, write)`: proje başına bellek, okuma, basışta hemen gösterip yazma, yazılamazsa
  geri dönme. İki kanca ondan: `useVideoLength` (`{ seconds, choose }`, bugünkü gibi) ve
  `useHappyEnding` (`{ on, choose }`). Ve `videoSaid(seconds, on)` — cümlelerin sonu, iki ekranın
  ortak cümlesi.
- **`LayerPanel.jsx`** — blok *Video uzunluğu*'nun altında; `handleLength` iki ayara hizmet eden
  `handleSetting(choose, value)` olur; `lengthSaid` → `settingsSaid = videoSaid(length, ending)`.
- **`PhotoDetail.jsx`** — `useHappyEnding`; iki not `videoSaid`'le; Tekrar dene'nin notu söylenecek
  bir şey varken.
- **`dist`** yeniden derlenir.

## Bilinen sonuçlar

- **Kullanıcının yazdığı prompt'a dokunulmaz.** Referanstan'ın kartları ve Yeniden üret'in videosu
  kullanıcının kendi kelimeleriyle gelir; Queen AI'a sorulmaz, ve düğme açıksa yalnız LoRA eklenir.
  Sonu orada kullanıcı kendisi yazar. Queen AI'ın yazdığı her prompt — Kareden'in, ve Tekrar dene'nin
  yeniden yazdığı — parçayı alır.
- **Loop ve bağlı video:** düğme açıkken talimat iki kuralı birden taşır — loop'un "son kare ilk
  fotoğraf", bağlının "son kare Picture 2"si ve mutlu sonun "video boşalmayla biter"i. İkisi birbirini
  sınırlar; hangisinin ağır bastığı Colab denemesinde görülür. Kod birini ötekine tercih etmez.
- **Ses yazarı** mutlu sondan habersiz: video prompt'unun kendisini okur, ve o prompt boşalmayı
  zaten anlatıyor.
- **Bu daldan önce kurulmuş bir oturumda** dosya yok, ve panel video üreticisini *"kurulu değil"* der;
  notebook'un modeller hücresi bir kez daha koşunca gelir.

## Testler

- `test_happy_ending.py` *(yeni)* — kapı: varsayılan kapalı, yazılan geri gelir, kendi dosyasında,
  `bool` dışı reddedilir, bilinmeyen proje 404, okunamayan dosya kapalı. Kuyruk: dört kapıdan giren
  video işi açıkken `happyEnding` taşır, kapalıyken alan yok; ses ve foto taşımaz; Tekrar dene o anki
  düğmeyle — açılıp kapanınca satırdan alan çıkar, değişmediyse plan aynı; bekleyen iş eklendiği
  düğmeyle; döngü üreticiye ve yazara iletir.
- `test_comfy_h3_video_generator.py` — açıkken üç kipte yığında HMCumshot 0.7, Motion Booster yerinde;
  kapalıyken gönderilen grafik yüklenenin aynısı; boş yuva yokken Türkçe hata.
- `test_video_prompt_writer.py` — açıkken talimat + parça (+ suffix), üç modda; kapalıyken bugünküyle
  aynı; parça dokuyu ve sesi istiyor; açıkken de uzunluk yok.
- `test_producer_contract.py` — fotoğraf ve ses üreticisi `happy_ending`'i alır; gerçek döngü düğmesi
  açık bir işi gerçek H3 üreticisine verir.
- `test_producers.py`, `test_notebook_installs_the_producer_groups.py` — grup ve notebook satırı.
- `test_composition_root.py` — kapı açık, kuyruk kapının yazdığını okuyor.
- `api.test.js`, `LayerPanel.test.jsx`, `PhotoDetail.test.jsx` — düğme, yeri, kaydı, hatası,
  cümleler.

## Sınırlar

- Grafik dosyalarına dokunulmaz: LoRA çalışırken, yalnız açık işte eklenir.
- Uzunluğun kapısı, dosyası ve sözleşmesi değişmez. Export, galeri, oynatıcı değişmez.
- Yol haritasına dokunulmaz.

## Bitti sayılır

- Video panelinde *Mutlu son* düğmesi *Video uzunluğu*'nun altında, varsayılanı kapalı, ve proje
  yeniden açılınca yerinde.
- Açıkken dört kapıdan giren H3 videosunun grafiğinde HMCumshot 0.7, ve Queen AI'ın talimatında sonun
  parçası; kapalıyken grafik ve talimat bugünküyle aynı.
- Notebook dosyayı H3'ün öteki dosyalarıyla indiriyor; video grubu onu sayıyor.
- Dört satır yeşil; `dist` yeniden derlenmiş.
- Colab'da: düğme açıkken videonun sonu, ve kapalıyken videonun bugünkü hâli — kullanıcının
  denemesinde görülecek.
