# QueenAgent v7 Yol Haritası — iki model, ve kaynak başına araçlar

**Tarih:** 5 Eylül 2026 · **Dal:** `feat/queenagent-v7` *(v6'nın ucundan, `1f14120`)* · **Tool:** queen-agent

**Kaynağı:** [2026-09-05-queenagent-v7-tasarim.md](../research/2026-09-05-queenagent-v7-tasarim.md).
Kararlar orada; burası sıra ve maddeler. Bir madde belgeyle çelişirse belge kazanır ve madde düzelir.

**Numaralar 166'dan başlıyor.** 150–165 `arsiv/v7-eski-150-165` dalında kullanıldı ve orada kalıyor;
tasarım o günden bu yana yarı yarıya değiştiği için aynı numara iki şey demesin. v6'nın **141**'i
açık kalıyor.

---

## Koşunun bağlayıcı kuralları

- **Model aracın imzasını bilir, dosyanın şeklini bilmez.** Hiçbir araç bir yol *(`characters/aylin`)*
  ya da tür parametresi *(`kind`)* almaz; parametrenin kendi adı nereye yazılacağını söyler. Argüman
  yapılı olabilir — o aracın sözleşmesi, dosyanın saklanma biçimi değil; yanlış şekli araç reddeder.
- **Ekle, güncelle, çıkar ayrı araçlardır.** `add_*` var olan ada, `update_*` olmayan ada reddeder;
  sessiz üzerine yazma yoktur.
- **Grok'un yazdığı ana ajana dönmez.** Araç dosyaya yazar, makbuz döndürür.
- **Silen araç yoktur.** Ajan silinmesini istiyorsa kullanıcıya söyler.
- **Her madde iki tur:** önce yalnız testler, kırmızı commit; sonra kod, yeşil commit. Dört sabit test
  satırı sırayla, birebir *(CLAUDE.md)*. Ön yüze dokunan madde `dist`'i aynı commit'te derler.
- **Deneme defterle:** `queenagent.ipynb`'de `BRANCH = "feat/queenagent-v7"`; merge'den önce `main`'e
  döner. Deneme 1 ve 2 **skill seçmeden** koşulur — skill metinleri 178'e kadar eski takımı anlatıyor,
  ve araç açıklamalarının tek başına yetip yetmediği zaten görülmek istenen şey.

---

# Dilim 1 — model JSON yazmayı bırakır

**Deneme 1'in sorusu:** model senaryonun kadrosunu yalnız araçlarla kurabiliyor mu, ve kapalı kapıya
ne yapıyor. *(Eski koşunun cevaplanmamış tek sorusu.)*

## Madde 166 — Kare alanları sadeleşir: `quality`, `people`, `camera` kalkar

- **Ne çalışır:** üç alan modelin elinden çıkar. Kalite zincirini kod her prompta kendisi koyar
  *(`DEFAULT_QUALITY`)*; dosyadaki `quality` okunmaz. Kişi sayısı karakterin kendi etiketlerinde durur
  *(`1girl`)*, `people` diye bir alan yoktur. Çekim açısı `action`'ın içindedir; `camera` alanı
  yazılmaz, eski dosyalarda varsa `shots` gibi okunmaya devam eder.
- **Nasıl görülür:** `quality` taşıyan eski bir dosya derlenince zincir yine kodunki. `people`'ı olmayan
  bir kare derlenince prompt sayıyı karakter bloğundan alıyor. `camera`'sı olan eski kare bozulmuyor.
- **Değişen:** `build_prompts.py`'nin `lead` satırı ve `build_character_prompts`'ın quality satırı
  ile *"count is a frame's own field"* diyen docstring'i. **Şema burada açılmıyor** — o üç alanı
  anlatan cümleleri 172'de şemayla birlikte gidiyor, iki kere yazılmasın *(spec'te gerekçesi)*.
  Aradaki pencere dışarı çıkmıyor: deneme Dilim 1'in sonunda, 172'den sonra koşuluyor.

## Madde 167 — `start_scenario` yapı dosyasını doğurur

- **Ne çalışır:** `start_scenario(name)` boş haritalar ve boş kare listesiyle `<name>.json` yazar. Ad
  alınmışsa reddeder: *There is already a file called bar-scene.json.* `WRITES_FILES`'a girer, kart
  çizilir; kiplerde `create_file`'ın yanında durur.
- **Nasıl görülür:** *"bar-scene senaryosunu başlat"* → kart, ve dosya listesinde `bar-scene.json`.
- **Neden ayrı araç:** `create_file` belge doğurur, bu yapı dosyası. 171 kapıyı kapatınca modelin
  elinde `.json` doğuracak kendi aracı kalmış olur.

## Madde 168 — Karakter yönetimi

- **Ne çalışır:** `add_character(file, name, tags)` — ad varsa reddeder. `update_character(file, name,
  tags?, new_name?)` — ad yoksa reddeder, yalnız verileni değiştirir; ad değişince onu anan kareler de
  değişir ve kaçı değiştiği cevapta yazar. `remove_character(file, name)` — bir kare anıyorsa reddeder:
  *aylin is still in frames 1, 3. Nothing was removed.*
- **Nasıl görülür:** üç çağrı, üç kart; dosya listesinde `.json` güncel. Aynı adı ikinci kez eklemek
  reddediliyor ve sebebi ekranda.
- **Ortak açıcı:** dosya yok → *There is no file by that name.*; JSON değil → ayrıştırıcının kendi
  cümlesi; kare listesi yok → *has no frames list.* Bir kez yazılır, 169–174 aynısını kullanır.
- **Cevaplar:** *Added aylin to characters.* · *Changed aylin in characters; 2 frames name it.* ·
  *Renamed aylin to ayla in characters; 2 frames followed.* · *Removed aylin from characters.*

## Madde 169 — Kıyafet yönetimi

- **Ne çalışır:** `add_outfit` / `update_outfit` / `remove_outfit`, 168'in şekli. Silme bekçisi kendi
  ilişkisini korur: *gecelik is still worn in frames 1, 3. Nothing was removed.*
- **Nasıl görülür:** kıyafet eklenip bir karede giydirilince silinemiyor; kareden çıkarılınca
  siliniyor.
- **Kendi kuralı:** yalnız giysi; kişi tarif edilmez, sayı yazılmaz — 172'nin metni söyler.

## Madde 170 — Mekân yönetimi

- **Ne çalışır:** `add_location` / `update_location` / `remove_location`. Silme bekçisi: *bedroom is
  still the place in frames 1, 3. Nothing was removed.*
- **Nasıl görülür:** 169 gibi.
- **Kendi kuralı:** içinde insan yok, sayı yasak — 172'nin metni söyler.

## Madde 171 — Kapı kapanır: `create_file` ve `edit_file` `.json`'a dokunamaz

- **Ne çalışır:** iki araç `.json` uzantılı ada reddeder: *bar-scene.json is a structure file; it is
  not written or changed as text.* **İstisna yok** *(kullanıcı kararı, 5 Eylül)*: bozuk bir dosyayı da
  model onarmaz — araçlar *is not valid JSON* der ve durur, model kullanıcıya söyler, kullanıcı elle
  düzeltir. `.json`'a metin olarak dokunan hiçbir yol kalmaz.
- **Nasıl görülür:** model `create_file` ile senaryo yazmaya kalkınca ret cümlesi, ve bir sonraki
  raundda `start_scenario`. *Kapalı kapıya ne yaptığı Deneme 1'de izlenir.*
- **Şartı 167–170:** kapandığında modelin elinde alternatif olmalı — arşivin sırasından tek fark bu.

## Madde 172 — Şema aracı uçar, yerine `SDXL_PROMPT_RULES` gelir

- **Ne çalışır:** `read_prompt_structure_schema` ve `schema.py` silinir; `modes.py`'nin `READS`'i tek
  ada iner. Etiket alan altı aracın *(`add_*`, `update_*`)* açıklamasına aynı kural metni eklenir: kişi
  sayısı karakterin etiketinde, `solo` orada değil; kıyafet kişi tarif etmez; mekânda insan yok;
  kalite etiketi yazılmaz. Tek metin, tek kaynak.
- **Nasıl görülür:** model şemayı çağıramıyor; kural her çağrıda parametrenin yanında.
- **Bedeli açık:** altı kopya, her istekte. Damga dar gelirse tek kopya `SYSTEM_PROMPT`'a iner —
  takas denemede ölçülür, önceden kapanmaz.

---

# Dilim 2 — sahne ve prompt ayrılır, Grok gelir

**Deneme 2'nin soruları:** Grok'un yazdığı action'lar *(kullanıcı yargısı)*, `solo` kuralı tutuyor mu,
ve **damga** — ana ajanın harcaması ile kare isteklerininki yan yana. *(Damga okunurken 179 henüz
koşulmamış olacak: okunan dosya istekte iki kere duruyor, rakam onu da içeriyor.)*

## Madde 173 — Kare sahnesiyle ve kadrosuyla doğar: `add_scene` gelir, `add_frames` gider

- **Ne çalışır:** `add_scene(file, scenes)` — her sahne `{scene, characters: {ad: [kıyafetler]},
  location}`; **yalnız `scene` zorunlu** *(kullanıcı kararı, 5 Eylül)*, manzara karesinin kadrosu, yakın
  çekimin mekânı olmayabilir. Kod kareye numarasını verir *(`number`)* ve sona ekler. Her ad haritalarda aranır;
  bulunmayanların **hepsi birden** döner: *frame 4: aylin is not in characters; known: lara, deniz.*
  Hiçbir şey yazılmaz. `add_frames` `TOOL_SPECS`'ten, `modes.py`'den ve testlerden gider.
- **Nasıl görülür:** üç sahne tek çağrıda, kart *Added 3 scenes to bar-scene.json as frames 4-6.*
  Dosyada her karenin `scene`, `characters`, `location`, `number` alanı var, `action` yok.
- **Değişen:** `MAX_ROUNDS`'un eski zinciri anlatan yorumu.

## Madde 174 — `update_frame` ve `remove_frame`

- **Ne çalışır:** `update_frame(file, frame, scene?, characters?, location?)` — yalnız verileni
  değiştirir, `action`'a dokunmaz *(o 176'nın)*. Olmayan kare: *bar-scene.json has 5 frames; there is
  no frame 9.* Bilinmeyen ad: 173'ün cümlesi. `remove_frame(file, frame)` — siler, kalanlar 1'den
  yeniden numaralanır: *Removed frame 3 from bar-scene.json; 5 frames left, renumbered from 1.*
- **Nasıl görülür:** kare silinince dosyadaki `number`'lar boşluksuz.

## Madde 175 — Prompt yazan model bir rol olur: `write_once` yolu

- **Ne çalışır:** `Engine.write_once(system, user)` — kendi sistem promptuyla tek soru, araç yok,
  konuşma yok; cevap metni ve harcaması döner. `XaiEngine(clients, default, prompt_writer)` ikinci
  adı taşır; `config.PROMPT_MODEL = "grok-build-0.1"`, `main.py` bağlar. `run_tool` motoru alır
  *(`engine=None` varsayılan; motor yokken araç reddeder, öteki araçlar etkilenmez)*. Aracın harcaması
  `ToolResult.spent` ile turun damgasına **eklenir**. Ölü `Engine.complete` / `XaiEngine.complete` /
  `XaiClient.complete` yolu sökülür; port imzasını bekleyen test canlı yola *(`write_once`)* taşınır.
- **Nasıl görülür:** ekranda hiçbir şey — 176'nın yolu. Damgada `sent` aracın istekleriyle büyüyor.
- **Değişen:** defterin *"besteci üç satır çiziyor"* yorumu → *"prompt aracı ikinci anahtarı harcıyor"*.
  İki anahtar hâlâ zorunlu.

## Madde 176 — `write_frame_prompt`: Grok karenin action'ını yazar

- **Ne çalışır:** `write_frame_prompt(file, frame, note?)`. Sistem promptu `WRITE_FRAME_SYSTEM_PROMPT`
  + `SDXL_PROMPT_RULES`; kullanıcı mesajı **o karenin** kadrosu *(adlar ve etiketler, kıyafetlerle)*,
  mekânı ve etiketleri, sahne cümlesi, varsa not. Cevap **düz metin**, JSON değil — yazılacak tek alan
  var. `frames[n].action`'a yazılır, **her zaman üzerine**. Makbuz: *Wrote frame 3 of bar-scene.json.*
  Metin cevaba basılmaz.
- **Reddettiği:** sahnesi olmayan kare *(Frame 3 has no scene to write from.)*, olmayan kare, motor yok.
  Düşen ya da boş dönen istek kareyi boş bırakır ve söyler; yeniden deneme yok — aynı kareyi yeniden
  çağırmak retry'nin kendisi.
- **Nasıl görülür:** kart, ve bağlam kabında karenin `action`'ı dolu. Notla ikinci çağrı action'ı
  değiştiriyor.
- **Geri dönüş yolu belgede:** kalite yetmezse Grok yalnız action yazmaya devam eder, bu zaten o yol.

---

# Dilim 3 — ürün yüzeyi

**Deneme 3'ün sorusu:** iki skill baştan sona — bir senaryo kur, promptlarını üret, derle — ve besteci.

## Madde 177 — Besteci iki satır: Queen Flash ve Queen Pro, varsayılan Flash

- **Ne çalışır:** `models.js` iki satır — `deepseek-v4-flash` **Queen Flash**, `deepseek-v4-pro`
  **Queen Pro**; Grok satırı gider. `DEFAULT_MODEL` iki yerde de Flash *(`config.py`, `models.js`)*.
  `config.MODELS`'in Grok satırı **kalır**, 175 onu kullanıyor. Kimlikler değişmez: sağlayıcıya giden
  ad `config.py`'nin anahtarı.
- **Nasıl görülür:** menüde iki ad, fiyatlarıyla. Model seçmeyen mesaj Flash'la cevaplanıyor. Grok
  seçilmiş eski bir mesaj düğmede kendi kimliğini gösteriyor *(`modelName`'in bugünkü davranışı)*.
- **Değişen:** `models.test.js`, `ModelPicker.test.jsx`, `test_config.py`'nin üç model testi;
  `dist` aynı commit'te.

## Madde 178 — Skill metinleri yeni takımı anlatır

- **Ne çalışır:** *Start a scenario* — plan, karakterler *(`add_character`)*, kıyafet ve mekân, sahneler
  *(`add_scene`, kadrosuyla)*, el değiştirme. Sahne listesi dosyası yok. *Generate prompts+* — her kare
  için `write_frame_prompt`, sonra `build_prompts`; şikâyet notla yeniden yazdırmak ya da harita
  girdisini `update_*` ile düzeltmek. Kelime tavanı testleri korunur; `read_prompt_structure_schema`,
  `add_frames`, `-scenes.md`, `edit_file`-ile-kare hiçbir metinde geçmez.
- **Nasıl görülür:** Deneme 3.
- **Değişmeyen:** `SYSTEM_PROMPT` — andığı dört araç *(`read_file`, `create_file`, `edit_file`,
  `write_plan`)* yerinde.

## Madde 179 — Okunan dosya istekte bir kere durur

*(Arşiv dalının "Bekleyen"inden geldi; kullanıcı 5 Eylül'de bu koşuya aldı.)*

- **Sorun:** `read_file` bir cümleyle değil **dosyanın tamamıyla** cevap veriyor, ve o cevap turun
  sonuna kadar konuşmada kalıyor. Bağlam kabı da aynı dosyayı diskten okuyup yanına koyuyor. Okuma
  raundundan sonra her istekte **iki kopya** gidiyor — ve model aynı turda dosyayı düzenlerse,
  konuşmadaki kopya eski hâli, kaptaki yeni hâli söylüyor. Madde 129'un öldürdüğü bayatlık tur
  içinde hayatta.
- **Ne çalışır:** `read_file` bir **makbuz** döndürür — *bar-scene.json, 45 lines; it is in your
  opened files.* — içeriği değil. İçeriği yalnız kap taşır; kabın başlığı *"the last 5 files you
  opened"* der. `BOX_LIMIT` 5 kalır: kaptan düşen dosyayı yeniden okumak artık bir cümleye mal
  oluyor, kap kendini onarıyor. Okuma gecikmiyor — bugün de içerik bir sonraki raundda görülüyor.
- **Nasıl görülür:** okumadan sonraki raundun isteği dosyayı **bir** kere taşıyor. Aynı turda
  düzenlenen dosya istekte yalnız yeni hâliyle var. Damga küçülüyor.
- **Bedeli doğru okunsun:** kaldırılan kopya konuşmanın içinde, yani ikinci raunddan sonra
  **cache'li** olan; kap her raund tam fiyat gitmeye devam ediyor. Kazanç para değil, çelişkinin
  gitmesi.
- **Değişen:** `tools.py`'nin `read_file` cevabı; `_boxed`'ın başlığı;
  `test_the_box_and_a_read_show_a_file_the_same_way` — Madde 131'in *"tek biçim"* iddiası tek taraflı
  kalıyor, testin ne söylediği yeniden yazılır; `SYSTEM_PROMPT`'un okuma cümlesi içeriğin nerede
  belirdiğini söyler.

---

## Kapsam dışı, ve nerede duruyor

- **Toplu prompt aracı** *(bütün boş kareler tek çağrıda, paralel)* — `queen-agent/BACKLOG.md`.
- **Yazılan promptların doğrulanması** — `queen-agent/BACKLOG.md`.
- **`delete_file`** — açıldı, aynı gün kapandı: silen araç yok.
- **`queen-*` kimlikleri `config.py`'de** — yalnız arayüz kararı; sağlayıcı adı anahtarda kalıyor.
- **Arşivin 160'ı** *(OpenRouter kaydı)* — m149 depoda iz bırakmadı; kayıt istenirse sona eklenir.
- **Dosyanın şeklini tek yerde sahiplenen modül** — arşivin bağlayıcı kuralının kod tarafı. Ucuz ve
  serbest; bu koşuda maddesi yok.
