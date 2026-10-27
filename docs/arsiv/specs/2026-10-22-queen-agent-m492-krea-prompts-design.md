# Madde 492 · QueenAgent Krea için prompt yazar — tasarım

**Tarih:** 22 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-20-queen-agent-v11-roadmap.md),
492 · v11-5 · **Dal:** `feat/queenagent-v11`, ana klasörde · **Plan:**
[m492 planı](../plans/2026-10-22-queen-agent-m492-krea-prompts-plan.md) · **Kurallar:**
[FOUNDATION](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../../queen-agent/CODE-STANDARD.md)

Bu spec, reviewer'ın 22 Ekim'de çizdiği ve kullanıcının aynı gün soru soru cevapladığı tasarımı taşır.
Tasarım dosyası `tmp/`'de duruyordu ve silinecek; bu yüzden kararların hepsi aşağıda, kendi başına
okunacak biçimde. Hiçbiri burada yeniden açılmadı. Modelin okuyacağı dört metnin tam hâli ekte.

## Ne, neden

Kullanıcı, 21 Ekim: *"queen agentta kreaya göre prompt yazabilmesi lazım mantıken"*. Queen Editor'de
fotoğraf artık Krea 2 Turbo'yla da çizilebiliyor (Queen Editor m482). Krea etiket değil düz cümle
okuyor, ve QueenAgent bugün yalnız SDXL'in etiket prompt'larını yazıyor.

**Bugün:** SDXL'in kuralları üç yerde. `SDXL_DOCUMENT` her isteğe system prompt'un arkasından gidiyor
(`model_engine._for_model`, Madde 453); birkaç kural da araç ve alan açıklamalarında (*"as tags"*,
*"Do not write solo"*, *"Never tags"*, *"Whoever is written first leads"* …); ve SDXL'in iki skill'i ile
Improve kendi kopyalarını taşıyor. Skill seçilmemiş bir turda da, SDXL'le ilgisi olmayan bir turda da
SDXL'in kuralları gidiyor.

**Olacak:** iki model, iki belge, dört skill.
- **İki belge:** `sdxl-prompt-writing.md` ve `krea-prompt-writing.md`. Kodda duran, salt okunur metinler;
  her projenin dosyalarının arasında görünürler. Ajan okur, değiştiremez; panel de gösterir.
- **Dört skill:** seçicide *SDXL start scenario, SDXL edit, Krea start scenario, Krea edit*. Improve
  kalkar. Her skill'in ilk satırı kendi modelinin belgesini önce okumasını söyler.
- **Kurallar yalnız kendi yerinde:** bir modelin prompt yazma kuralı yalnız o modelin belgesinde ve o
  modelin skill'lerinde durur. `SDXL_DOCUMENT` artık hiçbir isteğe kendiliğinden gitmez; araç
  açıklamalarındaki kural cümleleri belgeye taşınır.
- **Türü dosyanın adı söyler:** `plaj.sdxl.json` ya da `plaj.krea.json`. Bir Krea senaryosu yalnız bir
  stil ve kareler taşır: her karede sahne ve prompt. Kurulan prompt *stil + prompt*'tur.
- **Dört yeni araç** Krea için; SDXL'in dokuz aracı `sdxl_` önekini alır.

## Kullanıcının kararları (22 Ekim)

Hepsi kullanıcının; spec yalnız nasıl yapılacağını yazar.

1. **Bir modelin prompt kuralları yalnız o modelin belgesinde ve o modelin skill'lerinde durur**
   *("model instructlarını onunla alakalı skill hariç hiçbir yerde olmadığından emin olalım"; "seçicideki
   skillerde olabilir o modelin skilliyse")*. Öbür modelin metninde, `SYSTEM_PROMPT`'ta, araç ve alan
   açıklamalarında, `model_engine`'de, araç cevaplarında ve hata cümlelerinde durmaz.
2. **Araç ve alan açıklamaları araçta kalır** *("toolda açıklama yazabilirsin sıkıntı yok, schema
   açıklayacaksan ayrı bir dosya olarak genel durmasın demek istemiştim")*: aracın ne yaptığını, alanın
   ne tuttuğunu ve biçimini, içerik listeleriyle söyler. Yalnız prompt yazma kuralları çıkar. Şemayı
   anlatan ayrı bir genel dosya yok.
3. **Davranış maddeleri açıklamalarda kalır** (`SETTING_AN_ENTRY`, `ADD_FRAME`, `UPDATE_FRAME`,
   `REMOVE_*`, `REMOVE_FRAME`, `AN_ENTRYS_NEW_TAGS`).
4. **`characters` ve `before` birer kısa biçim cümlesi alır** (aşağıda, 4).
5. **Alanın adı `tags` kalır.**
6. **"Karede ilk yazılan kişi prompt'u açar" SDXL belgesine gider.**
7. **Sahne kuralları araç açıklamalarından çıkar;** her modelin start skill'i ve belgesi taşır.
8. **Seçici kalır, dört satırla; Improve kalkar** *("improve skilinin kendisi kalksın … Krea start
   scenario olacak, bir de Krea edit olacak")*.
9. **Skill seçilmemiş bir turda kural gitmez** *("hiçbiri gitmez")*.
10. **İki belge var, ajan okur ama değiştiremez** *("2 skill olacak işte sdxl ve krea prompt yazımı";
    "ajan değiştiremez sadece okur")*; **dosya panelinde de görünürler** *("dosya panelimde de görünse
    sıkıntı yok basit tutabilirsin")*. Skill'in ilk satırı belgeyi önce okumasını söyler *("bizim
    skillimizin başında söyleriz git ve şu skili oku önce")*.
11. **Okunan belgeler kutunun 5'lik sınırına sayılır.**
12. **Krea karelerinde `number` yok.**
13. **Notlar `<senaryo>-notes.md`'ye yazılır.**
14. **Stil senaryo başlarken kullanıcıya sorulur** *("senaryo başlarken sorulsun")*, ve
    `krea_start_scenario` onu yazar.
15. **`START_A_SCENARIO`'daki SDXL kural kopyaları kalır** (Rule 1 – 6, ayna, negatif liste, Step 4).
    Step 4 sahne kuralının eksik satırını alır, dört kopya aynı olsun diye *(kullanıcı, 22 Ekim — spec'in
    açık sorusuna 1. seçenek)*; tavan 1 830 → 1 835.
16. **Türü dosyanın adı söyler** *("plaj.krea.json ya da plaj.sdxl.json … bu mantıklı")*. İçeriğe bakıp
    tür seçmek reddedildi *("hayır kontrol böyle yapılmamalı bu çok kötü bir tasarım")*. İçerik adın
    türüne uymazsa dosya reddedilir; hiçbir yerde sessizce öbür türe düşülmez.
17. **Eski `<ad>.json` dosyaları kurulmaz** *("onlar build alamasın …")*. Cevap yalnız
    *"plaj.json is not a valid scenario file."* *("özellikle öyle bir şey demesin, yönlendirme yapmasın,
    valid değil desin yeter")*. Kullanıcı isterse ajan içeriği var olan araçlarla yeni dosyaya taşır
    *("gerek yok bu zaten yeni projelerde kullanılacak, agent yeni json açıp ona aktarır")*. Rename aracı
    yok, taşıma kodu yok.
18. **İki risk kabul edildi:** bir projede belgeyle aynı adda bir dosya varsa belge onu listede
    gölgeler; proje kartındaki dosya sayısı paneldekinden iki eksik görünür.
19. **Krea metinleri basit; karakterin nasıl anlatılacağına katı kural yok** *("şu an bu kısıtlamalara
    girmeyelim")*. SDXL için yalnız var olan kurallar kullanılır *(9 Ekim — "bizde olan kuralları kullan
    sadece")*; Krea'nın kuralları aşağıdaki araştırmadan.

## Bugün — koddan okunanlar

- **`prompt.py`** modele söylenen her metnin yeri (Madde 189): `SYSTEM_PROMPT`, üç skill
  (`START_A_SCENARIO`, `EDIT_PROMPTS`, `IMPROVE`), `SDXL_DOCUMENT` (3 539 karakter), ve araç / alan
  açıklamaları.
- **`model_engine._for_model`** her isteğin önüne iki system mesajı koyar: `system_prompt()` ve
  `SDXL_DOCUMENT`.
- **`skills.INSTRUCTIONS`** üç kimliği metinlere eşler; `instruction_for` bilmediği kimliğe `""` döner.
  `run_turn` talimatı isteğin sonuna koyar.
- **`FileFileStore`** proje dosyalarını bilen tek sınıf: `list_names`, `list_files`, `read`, `read_body`,
  `write`, `delete`. Hangi dosyanın olduğunu `projects.json`'dan (bellekte) bilir, içeriği Drive'dan
  okur. Ajanın dosya listesi (`run_turn._named`), `read_file`, açılan dosyalar kutusu (`_boxed`) ve panel
  (`list_files`, `read_file` kullanım durumu) hep ondan okur.
- **`tools.py`** 14 araç. `scenario_name` her senaryoyu `.json` yapar; `_shut` `.json`'u `create_file` ve
  `edit_file`'a kapatır; `_opened` senaryoyu okur ve bir `frames` listesi ister; `_build` `.json`'u
  `build_prompts`'a verir. `_renumbered` her karenin `number`'ını yerinden yazar.
- **`build_prompts.py`** SDXL'in kurucusu; `render_module` ve `prompts_name` (`x.json` → `x.py`).
- **`modes.py`** EDIT'te sorulmadan koşan araçların adları.
- **Ön yüz** `skills.js`'te üç satır. Dosya paneli `.md`'yi Markdown olarak gösterir; silme hatası
  `failureFrom`'la cevabın `error`'unu gösterir.
- **Kelimeler:** `START_A_SCENARIO` 1 823 kelime (tavan 1 830), `EDIT_PROMPTS` 197 (tavan 205).

## Ne değişir

### 1. İki belge — `prompt.py`'de `GUIDES`

```python
GUIDES = {
    "sdxl-prompt-writing.md": SDXL_GUIDE,   # Ek A
    "krea-prompt-writing.md": KREA_GUIDE,   # Ek B
}
```

İki metin, modülün öbür metinleri gibi adlı sabitler; sözlük adı metne bağlar.

- **Tek bir sözlük, ad → metin,** `prompt.py`'de, çünkü modele söylenen her metin orada (Madde 189).
  `SDXL_DOCUMENT` kalkar; metni `sdxl-prompt-writing.md`'nin gövdesi olur.
- **Kodla gelir, salt okunur.** Drive'a kopyalanmaz: her projede bir kopya ayrışırdı, kullanıcı ya da
  model onu değiştirebilirdi, ve her okuma bir Drive gidişi olurdu. Repoda ayrı `.md` dosyası da olmaz:
  domain dosya okumaz, bunun için bir port, bir veri sınıfı ve bir yol daha gerekirdi.
- **Markdown başlıklarıyla** (`#`, `##`), çünkü adları `.md` ve panel onları Markdown olarak çizer.
- **SDXL belgesi** bugünkü `SDXL_DOCUMENT` + araç açıklamalarından taşınan SDXL kuralları (aşağıda,
  *Denetim*) + *The scene* bölümü. Yeni kural yok.
- **Krea belgesi** araştırmadan (aşağıda, *Araştırma*) + *The scene*. SDXL'e dair hiçbir şey yok. Boyut
  yazmaz: yön ve boyut v11-6'nın.
- **Sahne bölümü** dört yerde durur: iki belge, iki start skill'i. Bir değişiklik dört yerde elle
  yapılır — kuralın "yalnız o modelin yerinde" durmasının bedeli, kabul edildi.

### 2. Belgeler her yerde görünür, tek kapıdan — `FileFileStore`

`FileFileStore(store, projects, guides, listed_at)`. İkisini `main.py` verir: `GUIDES` ve sunucunun
açıldığı an (`datetime.now(timezone.utc).isoformat(timespec="milliseconds")`, bir kez).

- **`list_names`, `list_files`:** projenin satırları, belgelerle aynı adı taşıyanlar dışarıda, ardından
  iki belge. Belgenin satırı `File(name, "md", listed_at)`.
- **`read`, `read_body`:** ad `guides`'taysa metin bellekten döner, Drive'a gidilmez; `read_body`
  `FileBody(File(name, "md", listed_at), text)`.
- **`write` ve `delete`** belgeye hiç ulaşmaz: yazan ve silen kapılar belgeyi daha önce reddeder (3).
  `FileFileStore` belgeyi diske hiç yazmaz, silmez.
- Panel, ajanın listesi, `read_file`, kutu ve `run_turn` değişmez — hepsi zaten bu sınıftan okuyor.
  Ajanın listesi şöyle görünür: `bar-scene.sdxl.json, bar-scene.sdxl.py, sdxl-prompt-writing.md,
  krea-prompt-writing.md`.

### 3. Değiştirilemez

- **`create_file`:** belgenin adını `edit_file`'ın cümlesiyle, dosya okunmadan reddeder:
  *"sdxl-prompt-writing.md is read-only; it is read, not written."* *"There is already a file called
  … Use edit_file"* demez: `edit_file` onu bir tur sonra yine reddederdi (reviewer bulgusu).
- **`edit_file`:** `_shut`'ın yanında tek bir koşul, dosya okunmadan:
  *"sdxl-prompt-writing.md is read-only; it is read, not written."*
- **Panelden silme:** `delete_file` (kullanım durumu) adı `GUIDES`'ta bulursa yeni `ReadOnlyFile`
  hatasını yükseltir (`errors.py`); route onu **409** ve `{"error": "<ad> is read-only; it is read, not
  written."}` yapar. Ekran cümleyi bugünkü yoldan (`useFiles` → `failureFrom`) gösterir; ön yüz değişmez.
  Tasarımın dosya listesinde `errors.py` ve `routes.py` yoktu; ret ekrana başka yoldan doğru ulaşamaz:
  `FileFileStore.delete` belgenin satırını bulamaz, ve bugünkü 404 *"file not found"* yanlış olurdu.
- Senaryo araçlarının adları `.sdxl.json` / `.krea.json` / `.py` ile biter; bir belgenin adına hiç
  yazamazlar.

### 4. Araçlar — ad, açıklama, alan

**Ad kuralı.** Bir türe ait aracın adı `sdxl_` ya da `krea_` ile başlar, açıklaması *"SDXL scenario:"*
ya da *"Krea scenario:"* ile. İki türde de çalışan aracın adında önek yoktur, açıklaması *"SDXL or Krea
scenario:"* ile başlar. Açıklamalar aracın ne yaptığını, alanın ne tuttuğunu ve biçimini söyler; prompt
yazma kuralı taşımaz.

| Ad | Tür | Ne yapar | Durum |
|---|---|---|---|
| `read_file` | genel | projenin bir dosyasını okur; iki belge de bu dosyaların arasında | değişmez |
| `create_file` | genel | yeni bir belge yazar | açıklamada iki açılış aracının adı |
| `edit_file` | genel | var olan bir belgenin bir parçasını değiştirir | belgeyi reddeder |
| `sdxl_start_scenario` | SDXL | boş bir `<ad>.sdxl.json` açar | `start_scenario`'dan |
| `sdxl_set_character`, `sdxl_remove_character` | SDXL | karakter girdisi | adlandı |
| `sdxl_set_outfit`, `sdxl_remove_outfit` | SDXL | kıyafet girdisi | adlandı |
| `sdxl_set_location`, `sdxl_remove_location` | SDXL | mekân girdisi | adlandı |
| `sdxl_add_frame`, `sdxl_update_frame` | SDXL | kare: sahne, oyuncular, mekân, aksiyon | adlandı |
| `krea_start_scenario` | Krea | stiliyle boş bir `<ad>.krea.json` açar: `{"style", "frames": []}` | yeni |
| `krea_set_style` | Krea | senaryonun stilini değiştirir | yeni |
| `krea_add_frame` | Krea | kareler ekler: sahne ve prompt | yeni |
| `krea_update_frame` | Krea | bir karenin sahnesini ya da prompt'unu değiştirir | yeni |
| `remove_frame` | ikisi | bir kareyi çıkarır | türü addan alır |
| `build_prompts` | ikisi | `<ad>.py`'yi kurar | kurucuyu addan seçer |

14 araç 18 olur. Belge okumak için yeni araç yok. `remove_frame` ve `build_prompts` bölünmez: birinin
işi iki türde aynı, öbürününkini dosyanın adı seçiyor; iki build aracı yanlışını çağırmak için bir kapı
daha açardı. Tek bir `krea(op=…)` aracı içinde gizli bir anahtar taşırdı; var olan araçları genişletmek
her araca iki türün alanlarını yükler ve adı hangi tür için olduğunu söyleyemezdi; Krea dosyasını metin
olarak yazdırmak, birbirine benzeyen karelerde `edit_file` çapası isterdi (128/171'in kaldırdığı hata).

**Açıklamalardan çıkan cümleler** (gittikleri yer *Denetim*'de):

| Sabit | Bugün | Sonra |
|---|---|---|
| `SET_CHARACTER` | *"Add or change a character in a scenario: the tags an image model draws them from."* | *"SDXL scenario: add or change a character, the entry an image model draws them from."* |
| `SET_CHARACTER_TAGS` | *"Write the character as tags: how many … Do not write solo: … Do not write clothes here …"* | *"The character: how many people this entry draws, their age, body, hair and face. The count goes here and nowhere else, because this is the one place a count sits next to the person it counts. Do not write clothes here -- those are outfits."* + `AN_ENTRYS_NEW_TAGS` |
| `SET_OUTFIT_TAGS` | *"Write the clothes as tags and nothing else: the garments …"* | *"The clothes: the garments, their colour, their material, and what they leave bare. …"* (gerisi aynı) |
| `SET_LOCATION_TAGS` | *"Write the place as tags: what kind …"* | *"The place: what kind of place it is, …"* (gerisi aynı) |
| `ADD_FRAME_SCENE` | *"What happens, in English. … Never tags."* | *"What happens. The scene becomes the video of the frame, and the action of the frame is written from the scene."* |
| `ADD_FRAME_CHARACTERS` | *"… Whoever is written first leads the frame's prompt. …"* | *"Who is in the frame: a map from each character's name to the list of outfits they wear. Left out for a frame with nobody in it."* |
| `UPDATE_FRAME_CHARACTERS` | *"Who is in the frame, each name with the outfits they wear. Replaces …"* | *"Who is in the frame: a map from each character's name to the list of outfits they wear. Replaces the whole cast rather than adding to it; empty leaves nobody in it."* |
| `ADD_FRAME_BEFORE` | beş cümle | *"The number of the frame to go in front of. Left out, or one past the last, means the end."* |
| `ADD_FRAME` | *"… every frame after an insertion moves up."* · *"… with update_frame."* | *"… every frame after an insertion moves up and keeps everything it carries, its action included. This is how a scene goes into the middle of a scenario; taking the tail out and adding it again is not."* · *"… with sdxl_update_frame."* — `ADD_FRAME_BEFORE`'un iki cümlesi burada, kaybolmaz |
| `UPDATE_FRAME` | *"… written here, and corrected here, in your own words."* | *"… written here, and corrected here."* |
| `UPDATE_FRAME_ACTION` | *"The action of the frame as tags: … Written by the SDXL prompt rules. …"* | *"The action of the frame: what the photo shows, and the shot. The photo is the first frame of the video. Replaces the action there. Empty takes the action off the frame."* |
| `BUILD_PROMPTS` | *"… The code assembles every frame in a fixed order, so a character reads the same in all of them. …"* | *"SDXL or Krea scenario: build the prompt list from a scenario file: for each frame, its scene sentence and its prompt.\n- The kind comes from the file's name, .sdxl.json or .krea.json.\n- This tool writes a Python file named after the scenario, replacing what it wrote last time."* |
| `CREATE_FILE` | *"… start_scenario opens those."* | *"… sdxl_start_scenario and krea_start_scenario open those."* |
| `START_SCENARIO` | *"Open a new scenario … the file is always .json."* | *"SDXL scenario: open a new one … the file is always .sdxl.json."* |

Öbür SDXL açıklamaları (`REMOVE_*`, `SET_OUTFIT`, `SET_LOCATION`, `UPDATE_FRAME_SCENE`,
`UPDATE_FRAME_LOCATION`, `ADD_FRAME_LOCATION`) yalnız *"SDXL scenario:"* önekini alır; `REMOVE_FRAME`
*"SDXL or Krea scenario:"*. Sabitlerin adları değişmez — yalnız araçların adları.

**Krea araçlarının metinleri** (yeni sabitler; `KREA_START_SCENARIO` adı skill'in olduğu için aracınki
`KREA_START_SCENARIO_TOOL`):

| Sabit | Metin |
|---|---|
| `KREA_START_SCENARIO_TOOL` | *"Krea scenario: open a new one, with its style.\n- The file is born with the style and no frames, and its name always ends in .krea.json.\n- This tool refuses a name that is already taken. A scenario is opened once and added to, never started a second time."* |
| `KREA_STYLE` | *"The look shared by every frame. It is put in front of every frame's prompt."* |
| `KREA_SET_STYLE` | *"Krea scenario: change the style. The new style replaces the old one and reaches every frame at the next build."* |
| `KREA_ADD_FRAME` | *"Krea scenario: add scenes, one frame each, in the order they happen.\n- The frames go at the end, unless before names a frame to go in front of.\n- A frame's number is not yours to give. It is the frame's place in the list, and every frame after an insertion moves up.\n- Every frame needs its scene and its prompt. Nothing is written unless every frame in the call is good.\n- The answer names the frames it made, which is how you say which frame you mean next."* |
| `KREA_SCENE` | *"What happens. The scene becomes the video of the frame."* |
| `KREA_PROMPT` | *"The prompt of the frame's photo. The built prompt is the style, then this."* |
| `KREA_UPDATE_FRAME` | *"Krea scenario: change a frame, naming it by its number.\n- Only what you give is changed.\n- A Krea frame always has a scene and a prompt, so neither can be emptied."* |

Ortak kalanlar: `THE_SCENARIOS_FILE`, `THE_STRUCTURES_FILE`, `WHICH_FRAME`, `START_SCENARIO_NAME`,
`ADD_FRAME_BEFORE`, `ADD_FRAME_FRAMES`.

**Alanlar.** `krea_start_scenario(name, style)`, `krea_set_style(file, style)`,
`krea_add_frame(file, frames: [{scene, prompt}], before?)`, `krea_update_frame(file, frame, scene?,
prompt?)`. Hepsi zorunlu, `before`, `scene` ve `prompt` (güncellemede) dışında.

**`modes.py`:** dokuz ad yeni adlarıyla, dört Krea aracı EDIT'e. **`WRITES_FILES`:** `create_file`,
`sdxl_start_scenario`, `krea_start_scenario`, `build_prompts`.

**Araç cevaplarında adlar:** `_shut` *"Use sdxl_start_scenario or krea_start_scenario to open one, and
the sdxl_ and krea_ tools to change it."*; *"add_frame takes a list"* → aracın kendi adıyla. Cevaplar
dosyanın biçimini söyler, prompt kuralı değil.

### 5. Tür, dosyanın adından

- **`scenario_kind(name)`** (`tools.py`, `scenario_name`'in yanında; saf): ad, büyük-küçük harf
  katlanarak, `.sdxl.json` ile bitiyorsa `"sdxl"`, `.krea.json` ile bitiyorsa `"krea"`, değilse `None`.
- **`scenario_name(name, kind)`:** bugünkü gibi son uzantıyı atar, kalandan varsa `.sdxl` ya da `.krea`'yı
  atar, sonra `.<kind>.json` ekler. `sdxl_start_scenario("plaj")` → `plaj.sdxl.json`;
  `krea_start_scenario("plaj.json")` → `plaj.krea.json`; `sdxl_start_scenario("plaj.krea")` →
  `plaj.sdxl.json` — ad, aracın türünü değiştiremez.
- **Senaryo okuyan her araç önce addan türü sorar, dosyayı okumadan** (0 Drive):
  - ad türü söylemiyorsa (`plaj.json`, ya da `notes.md`): *"plaj.json is not a valid scenario file."*
    Yönlendirmez.
  - `sdxl_` aracı bir `.krea.json`'a: *"plaj.krea.json is a Krea scenario; use the krea_ tools."*;
    `krea_` aracı bir `.sdxl.json`'a: *"plaj.sdxl.json is an SDXL scenario; use the sdxl_ tools."*
  - `remove_frame` ile `build_prompts` iki türü de alır, türü addan.
- **İçerik adın türüne uymuyorsa reddedilir,** cevap uymayanı adlar, hiçbir şey yazılmaz:
  - **Krea** (`krea_prompts.py`'de, kendi türünün yanında): üst düzeyde yalnız `style` (metin) ve `frames`
    (liste); her karede yalnız `scene` ve `prompt` (metin). Eksik ve fazla anahtarların hepsi birden, ör.
    *"plaj.krea.json: frame 3 has characters; a Krea frame has scene and prompt."*
  - **SDXL** (`tools.py`'de, `_opened`'ın yanında, bir fonksiyon): bugünkü denetim (bir `frames` listesi,
    harita olan haritalar), ve buna `style` anahtarının ve karede `prompt`'un reddi. `_opened` ve
    `_build`'in SDXL yolu ikisi de onu çağırır.
- **Bozuk bir dosya** hiçbir zaman öbür tür sayılmaz; her zaman ret alır.
- **Kare.** Krea karesi tam olarak `{"scene", "prompt"}`; `number` taşımaz, listedeki yerinden sayılır
  (`_numbered` öyle sayıyor). `_renumbered` yalnız `.sdxl.json`'da koşar.
- **Krea araçlarında boş değer:** sahne, prompt ve stil boş olamaz — `krea_start_scenario`,
  `krea_set_style`, `krea_add_frame` ve `krea_update_frame` boş ya da yalnız boşluk olan bir değeri
  yazmadan reddeder (*"a scene needs a sentence saying what happens"* gibi). Sebep: biçim her iki anahtarı
  ister, ve kurucu boş bir stil ya da prompt'u zaten reddeder; ret yazmadan önce gelsin.
- **Kurulan modülün adı:** `prompts_name` değişmez: `plaj.sdxl.json` → `plaj.sdxl.py`, `plaj.krea.json` →
  `plaj.krea.py`. Tür adda kalır: atılsaydı aynı projedeki iki tür aynı `plaj.py`'ye yazar, biri öbürünü
  silerdi. Queen Editor adı okumuyor; kullanıcı metni panelden kopyalıyor.
- **Notlar dosyası** `<senaryo>-notes.md`, türsüz adla: `plaj.krea.json` → `plaj-notes.md`. Adı Krea
  skill'inin kuralı, kod üretmez (SDXL'in `-negative.md`'si gibi). Bir projede iki `plaj.krea.json`
  olamayacağı için çakışmaz.

### 6. `build_prompts` ve `krea_prompts.py`

- **`_build`** önce türü addan alır: `.krea.json` → `build_krea_prompts`, `.sdxl.json` → SDXL denetimi ve
  `build_prompts`, türsüz → *"… is not a valid scenario file."* Bugünkü *"would be written over by its own
  output"* reddi kalkar: türlü bir ad hiçbir zaman `.py`'ye eşit olamaz.
- **`krea_prompts.py`** (yeni, domain, saf): `krea_problems(source, structure)` biçimi denetler ve
  sorunların listesini döner; `build_krea_prompts(source, structure)` önce onu sorar, sonra her kare için
  `{"scene": scene, "photo": style.strip() + " " + prompt.strip()}` kurar. Boş bir stil ya da prompt varsa
  eksiklerin hepsi birden `BadStructure` olur.
- `render_module` ve `prompts_name` ortak. Çıktının şekli aynı (`{scene, photo}`); Queen Editor ve
  `build_prompts.py` değişmez.

### 7. Skill'ler ve seçici

| Satır (ekran) | Kimlik | Sabit | İlk satır |
|---|---|---|---|
| SDXL start scenario | `start-a-scenario` (aynı) | `START_A_SCENARIO` | *Read sdxl-prompt-writing.md first.* |
| SDXL edit | `edit-prompts` (aynı) | `EDIT_PROMPTS` | *Read sdxl-prompt-writing.md first.* |
| Krea start scenario | `krea-start-scenario` | `KREA_START_SCENARIO` (Ek C) | *Read krea-prompt-writing.md first.* |
| Krea edit | `krea-edit` | `KREA_EDIT` (Ek D) | *Read krea-prompt-writing.md first.* |

- **SDXL metinleri** ilk satırı alır. `EDIT_PROMPTS`'un gerisi olduğu gibi: 197 → 200 kelime, tavan 205
  aynı.
- **`START_A_SCENARIO` Step 4 bir satır daha alır** *(kullanıcı, 22 Ekim — açık soruya 1. seçenek)*:
  `"- Write each scene in English.\n"`'in hemen arkasına `"- Write each scene in sentences, never as
  tags.\n"`. Tasarım *"never tags"*ın Step 4'te zaten durduğunu sanıyordu, durmuyordu; bu satırla sahne
  kuralının dört kopyası (iki belge, iki start skill'i) bayt bayt aynı olur, ve `ADD_FRAME_SCENE`'den
  çıkan *"Never tags"* SDXL akışının kendi metninde de kalır. Gerisi olduğu gibi: 1 823 → 1 834 kelime;
  tavan bu yazılı kararla 1 830 → 1 835.
- **Krea metinleri** yeni ve basit; kendi tavanlarını alır: `KREA_START_SCENARIO` 416 kelime, tavan 430;
  `KREA_EDIT` 260, tavan 270 — metnin uzunluğu ve birkaç kelime pay, bir sonraki cümleye yer değil.
  SDXL'e dair hiçbir şey yazmazlar; bir araç adı, alt çizgili bir kelime geçirmezler (Madde 393).
- **Kimlikler aynı kalır;** eski mesajlar ve tarayıcının hatırladığı seçimler bozulmaz.
- **Improve kalkar:** `IMPROVE`, `skills.INSTRUCTIONS["improve"]`, `skills.js`'in satırı ve testleri.
  Var olan bir SDXL senaryosunu beş adımda baştan denetleyen akış gider; aynı denetimler SDXL start
  scenario'nun 6 – 10. adımlarında yeni senaryo için kalır. Var olan bir senaryonun negatif listesi SDXL
  edit'te düz sözle istenebilir; kuralları SDXL belgesinde. Eski sohbetlerde: kayıttaki `skill:
  "improve"` tarih olarak kalır; tarayıcı onu hatırlıyorsa düğme kimliğini yazar (`skillName`'in
  bugünkü yedeği); sunucu talimat eklemez, tur skill'siz koşar. Başka satır seçilince düzelir.
- **Seçicinin satırları** (`skills.js`; QueenAgent'ın arayüzü İngilizce):

  | `id` | `name` | `detail` |
  |---|---|---|
  | `start-a-scenario` | SDXL start scenario | Answer a few questions and get the characters, the places and the prompts. *(aynı)* |
  | `edit-prompts` | SDXL edit | Fix what is wrong in prompts you already have, and build them again. *(aynı)* |
  | `krea-start-scenario` | Krea start scenario | Answer a few questions and get the scenes and the Krea prompts. |
  | `krea-edit` | Krea edit | Fix what is wrong in Krea prompts you already have, and build them again. |

### 8. `model_engine`

`_for_model` yalnız `system_prompt()`'u koyar; `SDXL_DOCUMENT` gitmez. Sabit baş tek mesaj olur.
`ports.py`'deki `stream_alone` belge dizesi SDXL belgesini anıyor; sözü buna göre düzelir.

### 9. Eski dosyalar

Drive'da `<ad>.json` adında eski SDXL senaryoları var.
- `build_prompts` ve `sdxl_` / `krea_` araçları onları aynı cümleyle reddeder: *"plaj.json is not a valid
  scenario file."* Kabul etselerdi türü tahmin etmiş olurlardı.
- `read_file` ve panel onları bugünkü gibi açar; kullanıcı panelden silebilir.
- **İçeriği taşımak,** kullanıcı isterse: ajan eski dosyayı `read_file` ile okur, `sdxl_start_scenario` ile
  yenisini açar, `sdxl_set_*` ve `sdxl_add_frame` / `sdxl_update_frame` ile yeniden yazar. Girdi ve kare
  sayısı kadar çağrı; büyük bir senaryo bir turun 32 adımını aşarsa iş sonraki mesajda sürer.
- Uygulamada bir dosyayı yeniden adlandıran yol yok; kullanıcı Drive'da elle adlandırırsa uygulama
  görmez (FOUNDATION 2). Bir senaryonun türü doğduğu anda sabitlenir.

### 10. Ekran

- **Seçici:** dört satır; Improve yok. Sonra `dist` yeniden kurulur.
- **Dosya paneli:** her projede iki belge, `md` çipiyle; Markdown olarak açılır. Silmeye basılırsa
  409'un cümlesi bugünkü hata satırında görünür.
- **Araç adımları** kayıttaki adla görünür (`⏺ sdxl_add_frame(…)`); eski sohbetler eski adları gösterir.
- Ön yüzde seçici dışında değişiklik yok.

## Denetim — model kuralları nerede, nereye gider

`features/workspace`'te modele metin gönderen her yer okundu: `prompt.py`'nin sabitleri,
`model_engine._for_model`, `run_turn`'ün `_asked` / `_named` / `_boxed`'ı, `black_box`'ın `CHECK`'i,
`permission`'ın `REFUSED`'ı, `tools.py`'nin cevapları, `build_prompts.py`'nin `BadStructure` cümleleri.
Taşınan her şey var olan bir kural; belgede zaten olan ikinci kez yazılmaz.

**Taşınanlar:**

| Yer | Kural | Gittiği yer |
|---|---|---|
| `model_engine._for_model` | `SDXL_DOCUMENT` her isteğe | `sdxl-prompt-writing.md`'nin gövdesi; artık gönderilmez |
| `SET_CHARACTER` | *"the tags an image model draws them from"* | SDXL belgesinde zaten var (*Write tags*) |
| `SET_CHARACTER_TAGS` | *"as tags"*; *"Do not write solo"* ve gerekçesi | *as tags* zaten var; solo SDXL belgesinin *What is left out*'una |
| `SET_OUTFIT_TAGS` | *"as tags and nothing else"* | SDXL belgesinde zaten var |
| `SET_LOCATION_TAGS` | *"as tags"* | SDXL belgesinde zaten var |
| `ADD_FRAME_SCENE` | *"in English"*; *"Never tags"* | iki belgenin *The scene*'i ve Krea start skill'i ve SDXL Step 4 (*in English* orada zaten var; *never as tags* Step 4'e eklenir, kullanıcı, 22 Ekim) |
| `ADD_FRAME_CHARACTERS` | *"Whoever is written first leads the frame's prompt"* | SDXL belgesinin *The prompt of a frame*'i |
| `UPDATE_FRAME` | *"in your own words"* | silinir |
| `UPDATE_FRAME_ACTION` | *"as tags"*; *"Written by the SDXL prompt rules"* | belgede zaten var (*reads the tags … of every frame's action*); işaret silinir |
| `BUILD_PROMPTS` | *"fixed order, so a character reads the same"* | SDXL belgesinin *The prompt of a frame*'i |

**Kural taşımayanlar** (dokunulmaz ya da yalnız önek / ad alır): `SYSTEM_PROMPT`, `system_prompt()`,
`SYSTEM_PROMPT_SUFFIX`, `LAST_ROUND`, `NO_FILES_YET`, `FILES_HELD`, `OPENED_FILES`, `REFUSED`,
`REFUSED_WORDS`, `CHECK`, `APPROVED`; aracın ne yaptığını ve alanın biçimini söyleyen açıklamalar;
`tools.py` cevapları (*"A new character needs tags"* … — dosyanın biçimi, `tags` alanın adı);
`BadStructure` cümleleri; `DEFAULT_QUALITY` ve `BREAK` (kodun SDXL çıktısına koyduğu parçalar);
`prompt.py`'nin modül açıklaması (yorum, modele gitmez — `SDXL_DOCUMENT`'ı anan cümlesi `GUIDES`'a
döner). `START_A_SCENARIO` ve `EDIT_PROMPTS` SDXL'in kendi skill'leri, olduğu gibi kalır.

**Madde 453'ün kuralı** — *"a rule about one field is read while that field is being written"* — büyük
ölçüde korunur: alanın içeriği ve sınırları (sayı burada, kıyafet değil, mekânda kimse yok, kıyafetin
adı) alanda kalır. Belgeye yalnız tek bir alana ait olmayan yazım kuralları gider. İstisna *"Do not write
solo"*: karakter alanına ait, ama kullanıcı onu prompt yazma kuralı saydı; belge kutudayken görünür.

## Araştırma — Krea 2 Turbo'ya prompt yazmak

22 Ekim'de web'den; hiçbir şey denenmedi. Kaynaklar aşağıda.

- **Düz cümle, etiket değil.** Krea'nın kendi rehberi: *"We recommend users to use natural language
  prompts"*, *"Long detailed prompts yield best results"* [1]. Model kartı *"natural-language text
  descriptions"* der [2]. fal: *"Krea 2 was trained on short, medium, and long natural language"* [4].
  Krea'nın kendi genişletme talimatı çıktıyı tek bir düz paragraf ister, madde ve JSON olmadan [3].
- **Stil önde.** Krea'nın belgesi Turbo için: *"Turbo works well with concise prompts, but benefits from
  clear style, palette, and composition notes"* ve *"Add style language early"* [5]. fal: bir ortam ya da
  dönem adlandırılınca *"the whole image reorganizes around that"* [4]. Kod stili her karenin önüne
  koyduğu için kare prompt'u stili tekrarlamaz.
- **Birden çok kişi.** Krea'nın genişletme talimatı: her öznenin özellikleri ve eylemleri bir arada,
  pozlar, etkileşim ve yerleşim somut sözlerle [3]. Topluluk rehberi: *"For two people, assign positions
  and actions separately"* [6].
- **Yazılmayanlar.**
  - *Kalite etiketleri ve etiket listeleri:* resmî kaynakların hiçbiri onları önermiyor, hepsi düz cümle
    istiyor [1][2][4]; topluluk şablonu *"Avoid mechanical keyword lists or comma-stuffed style"* [7].
    *masterpiece, best quality, score_9* SDXL / Danbooru alışkanlığı.
  - *Ağırlık:* *"Standard weighting (e.g., (word:1.5) in the prompt text) does not work with the
    Qwen3-VL encoder that Krea2 uses"* [8].
  - *BREAK:* Queen Editor'ün Krea grafiğinde prompt doğrudan Qwen3-VL'e gider; orada `BREAK` bir kelime
    (Queen Editor m482, 3).
  - *Negatif:* Turbo 8 adım, CFG kapalı çalışır [2][9]; Queen Editor'ün grafiği cfg 1'de, negatifi
    `ConditioningZeroOut` — ComfyUI cfg 1'de negatifi hiç hesaplamaz (m482, 3). Negatif yazmanın etkisi
    yok.
  - *Tetik kelimesi:* SNOFS'un Krea 2 v1.5 sürümünde tetik kelimesi yok (`trainedWords` boş) [10];
    grafiğin tetik düğümü boş (m482, 3).
- **SNOFS.** Yazarı: *"SNOFS was trained on natural language … not tags"*, *"It will work best if you use
  full sentences to describe what you want"*; altyazı örneği *"her panties are pulled down to her
  thighs"*, *"panty pull"* değil; sayfası beden bölümlerini düz adlarıyla yazıyor [10].
- **Yazıda tırnak.** Fotoğrafta okunacak kelimeler tırnak içinde [1][3].
- **Sınır:** kaynakların hiçbiri sahne başına uzunluk, yön ya da boyut kuralı vermiyor. Boyut v11-6'nın.

**Kaynaklar**
1. Krea, *Prompting Guide* — https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md
2. Krea, *Krea-2-Turbo* model kartı — https://huggingface.co/krea/Krea-2-Turbo
3. Krea, prompt genişletme talimatı (`expansion.txt`) — https://github.com/krea-ai/krea-2/blob/main/docs/expansion.txt
4. fal, *How To Use Krea 2 Open Source* — https://fal.ai/learn/tools/how-to-use-krea-2-open-source
5. Krea, *Krea 2 Turbo* belgesi — https://www.krea.ai/docs/user-guide/features/krea-2-turbo
6. AIREITER, *Krea 2 prompting guide* (topluluk) — https://aireiter.com/blog/krea-2-prompting-guide
7. Hugging Face tartışması, topluluk şablonu — https://huggingface.co/krea/Krea-2-Turbo/discussions/4
8. ComfyUI Wiki, KJNodes *Krea2 Prompt Weight* — https://comfyui-wiki.com/en/custom-nodes/ComfyUI-KJNodes/nodes/krea2-prompt-weight
9. Krea, `krea-2` deposu README — https://github.com/krea-ai/krea-2
10. Civitai, SNOFS (model 1972981, sürüm 3390681) — https://civitai.com/api/v1/models/1972981
11. Queen Editor m482 spec'i — [2026-10-21-queen-editor-m482-krea2-photo-option-design.md](2026-10-21-queen-editor-m482-krea2-photo-option-design.md)

## Maliyet

Koddan sayıldı, ölçülmedi. Hepsi proje ve sohbet sayısından bağımsız.

| İşlem | Drive | Not |
|---|---|---|
| Dosya listesi (ajan, panel) | 0 | iki ad daha, bellekten |
| Belgeyi okumak (`read_file`, panel) | 0 | metin bellekten; 1 model turu, sohbette bir kez |
| Kutudaki belge, her turda | 0 | bugün kutudaki her dosya turda 1 Drive okuması; belge değil |
| `edit_file` / silme bir belgeye | 0 | ret, dosya okunmadan |
| Türsüz ya da öbür türün adı | 0 | ret, dosya okunmadan |
| `sdxl_start_scenario`, `krea_start_scenario` | 1 yazma (+ `projects.json` kuyruğu) | ad kontrolü bellekten |
| `krea_set_style`, `krea_update_frame`, `remove_frame`, `sdxl_*` | 1 okuma + 1 yazma | kare sayısından bağımsız; bugünkü gibi |
| `krea_add_frame` | 1 okuma + 1 yazma, **N kare için** | skill kareleri toplu ekletir; tur en çok 32 adım |
| `build_prompts` | 1 okuma + 1 yazma | bugünkü gibi |
| İçerik taşımak (eski `.json`) | girdi + kare sayısı kadar çağrı, her biri 1 okuma + 1 yazma | yalnız kullanıcı isterse |

**Token ve önbellek.**
- **Bugün:** `SDXL_DOCUMENT` (3 539 karakter, ≈ 1 060 token) her istekte, önbellekli baştaydı.
- **Sonra:** belgeyi okuyan sohbette kutuyla, önbelleksiz kuyrukta gider (SDXL belgesi 4 281
  karakter, ≈ 1 280 token; Krea belgesi 2 556, ≈ 770). Kutudaki belge her model turunda tam fiyatla
  gider: SDXL akışının bir turunda bugünkünden pahalı, öbür her turda ucuz. Okumayan her istekten tamamen düşer. Araç listesi kural cümleleri kadar kısalır, dört Krea
  aracı kadar uzar.
- **Önbellek:** araç listesi ve sabit baş değiştiği için yayından sonraki ilk istekte bir kez ıskalanır.
- **Kutu:** son açılan 5 dosya; okunan belge onlardan biri. Bir akış belgeyi, senaryoyu, notları ve
  planı birlikte tutar. Belge kutudan düşerse model onu yeniden okur: bir model turu, 0 Drive.

## Ne kaybolabilir, ne bozulabilir

- **Model belgeyi okumazsa** kuralsız yazar (tag yerine cümle, girdiye solo). Alanların içeriği ve
  sınırları açıklamada kaldığı için girdinin ne tuttuğu yine bilinir; skill'in ilk satırı bunu karşılar.
  Skill'siz bir turda garanti yok — kullanıcının seçtiği bedel.
- **Sahne kurallarının dört kopyası** ayrışabilir; bir değişiklik dört yerde elle yapılır. Kabul edildi.
- **Aynı adda dosya:** bir projede `sdxl-prompt-writing.md` adında gerçek bir dosya varsa belge onu
  listede gölgeler; dosya Drive'da durur. Kabul edildi.
- **Proje kartındaki dosya sayısı** `projects.json`'dan, belgeleri saymaz. Kabul edildi.
- **Var olmayan bir projenin dosya listesi** bugün boş; sonra iki belge. Hiçbir şey yazılmaz.
- **`NO_FILES_YET`** (*"This project holds no files yet."*) üretimde artık söylenmez: liste hiç boş değil.
  Sabit ve `_named` dokunulmadan kalır; bulgu olarak not.
- **Eski `shots` anahtarı** (`build_prompts`'un geri düşüşü) yalnız türsüz eski dosyalarda olabilir, ve
  onlar artık kurulmaz; kod dokunulmadan kalır, bulgu olarak not.
- **Yazma:** `Store.write_text` geçici dosyaya yazıp yerine koyar. Her ret yazmadan önce gelir; bir
  çağrının karelerinden biri bozuksa hiçbiri yazılmaz. Eski SDXL dosyalarına dokunulmaz.
- **İki istek aynı anda:** aynı senaryoya iki araç çağrısı bugünkü gibi; bir sohbette tur tektir (461),
  araçlar sırayla koşar. Belgeler bellekte, salt okunur; yarış yok.
- **Çökme:** belge hiç yazılmadığı için kaybolamaz. Bir senaryo yazması bugünkü atomik yoldan.
- **Ad ve yol:** belge adı yalnız sözlükte aranır; hiçbir değer yola dönmez. Ad yine `safe_name`'den geçer.
- **Gizli bir şey** yok: belgeler kodda, herkese açık metinler.

## Sınırlar

- Yön ve video süresi yok (v11-6). Krea belgesi boyut yazmaz; SDXL belgesindeki 1024 × 1536 kalır.
- Queen Editor, `build_prompts.py`'nin SDXL kurucusu, `render_module`, `prompts_name`, `run_turn`,
  `context_box`, `SYSTEM_PROMPT` değişmez.
- Rename aracı, taşıma kodu, otomatik taşıma yok. `tools.py`'yi türe göre bölmek ayrı bir karar.
- Krea'nın stil referansı, LoRA seçimi ve negatif listesi yok.

## Bitti sayılır

1. Testler gösteriyor ki:
   - `GUIDES` iki ad taşır; SDXL belgesi bugünkü belgenin bütün kurallarını, solo'yu, "ilk yazılan açar"ı,
     sabit sırayı ve sahne bölümünü taşır; Krea belgesinde SDXL'e dair bir şey yok, SDXL belgesinde
     Krea'ya dair bir şey yok;
   - hiçbir araç ve alan açıklamasında iki belgenin hiçbir kuralı yok; `SYSTEM_PROMPT`'ta da;
   - `model_engine` yalnız system prompt'u koyuyor;
   - her projenin listesinde iki belge var, okunuyor (Drive'a gidilmeden), `edit_file` ve silme
     reddediyor, `create_file` de aynı salt-okunur cümleyle reddediyor; aynı adlı satır gölgeleniyor;
   - dört skill, kimlikleri ve ilk satırları; Improve yok; Krea metinleri araç adı geçirmiyor, kendi
     tavanlarının altında;
   - `scenario_kind` ve türlü `scenario_name`; türsüz ad *"… is not a valid scenario file."* ile, öbür tür
     doğru öneki adlayarak reddediliyor, dosya okunmadan;
   - Krea biçim denetimi fazla ve eksik anahtarları bir kerede adlıyor; SDXL `style`'ı ve karede
     `prompt`'u reddediyor;
   - `krea_start_scenario` → `<ad>.krea.json` `{"style", "frames": []}`; `krea_add_frame` kareleri `number`
     olmadan, `before` ile ekliyor; `krea_update_frame` ve `krea_set_style` değiştiriyor; boş değer
     yazmadan reddediliyor; `remove_frame` Krea'da numara yazmıyor;
   - `build_prompts` Krea'da her kare için `stil + " " + prompt`'u `<ad>.krea.py`'ye yazıyor, SDXL'de
     bugünkü gibi `<ad>.sdxl.py`'ye.
2. Seçicide dört satır; `dist` yeniden kuruldu.
3. Dört takım tek tek yeşil.
4. **QA, Playwright:** seçicide dört satır, Improve yok; dosya panelinde iki belge Markdown olarak
   açılıyor, silme reddediliyor ve cümlesi görünüyor; Krea senaryosu açma, kare ekleme, `build_prompts`;
   türsüz eski bir `.json`'ın reddi.
5. **Colab — kullanıcının:** *Krea start scenario* ile kurulan prompt'lar Queen Editor'de Krea 2 Turbo'yla
   istenen sahneyi ve tarzı veriyor; SDXL akışı bugünkü gibi çalışıyor.

---

## Ek A — `sdxl-prompt-writing.md` (modelin okuduğu metin)

Bugünkü `SDXL_DOCUMENT`, Markdown başlıklarıyla; taşınan üç kural (solo, ilk yazılan, sabit sıra) ve
*The scene*. Başka her satır kelimesi kelimesine bugünkü belgeden.

```text
# SDXL prompt writing

## The image model
- The photo of each frame is made by an SDXL-family image model trained on Danbooru's own tags, at 1024 x 1536: portrait, 2:3.
- The image model reads the tags of every entry and of every frame's action.
- The image model is weak and draws every tag in the prompt. A complex prompt breaks the image.

## Writing a tag
- Write tags, never sentences. An article is not a tag either.
- Use a tag that the Danbooru vocabulary already has, rather than a description of the same thing. The model has seen a real tag many times, and has never seen a paraphrase of it.
- Write the tags in English, with spaces where the site writes underscores.
- Put one thing in each tag, split the way the vocabulary splits it. Do not join two tags into one longer phrase.
- When the vocabulary has no tag for it, write a few plain words in the same short form.

## What is left out
- Never write quality tags. The code already puts them at the front of every prompt, so yours would be printed twice.
- Never write the word or inside a tag. The model draws one picture and cannot toss a coin between two choices, so pick one and write only that.
- Never write solo in a character's entry. The same character stands alone in one frame and next to somebody in the next, so an entry claiming solo is wrong in half of them.
- Never add a mirror unless the user asks for one. A mirror breaks the image.

## The prompt of a frame
- The code builds every frame's prompt in a fixed order, so a character reads the same in all of them.
- Whoever is written first among a frame's characters leads the frame's prompt.
- The prompt of a frame describes one photo: the first moment of the scene.
- Some tags are not visible from some camera angles. So a character, an outfit or a place can have more than one entry, for different camera angles.
- The most common mistake: a tag hidden by the camera angle goes onto another character. For example, the hair of a hidden head ends up on another character.
- Rule 1: If one of the character's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 2: If one of the outfit's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 3: If one of the place's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 4: The image model draws one photo. The whole prompt of the frame must describe only one photo. If the prompt describes more than one photo, remove the extra part.
- Rule 5: The whole prompt of the frame must be simple enough for the weak image model. If a part of the prompt is too hard, make the part simpler, and keep the same moment.
- Rule 6: If the scene is NSFW, name each visible body part directly, as in penis or vagina. Never use a euphemism.

## The negative list
- The negative list is for the image model, not the video model. The negative list tells the image model what not to draw in the photo.
- The scenario has one negative list, for every frame. A tag in the negative list works on the whole photo, not on one character.
- The biggest problem is the features of the characters mixing, as in the hair of one character on another character. Focus the negative list on keeping the features of each character apart.
- Never write a feature of a character into the negative list. For example, dark skin in the negative list made a dark-skinned man come out white.
- To keep a feature of a character, write the opposite tags instead. For example, pale male and white man for a dark-skinned man.

## The scene
- Write each scene in English.
- Write each scene in sentences, never as tags.
- Write the words a character says inside quotes, in natural, well-written English. Translate the words when the user gives the words in another language.
- Write each scene short enough for four seconds.
- Each scene is used later to write the prompt for the video model.
```

Nereden: solo `SET_CHARACTER_TAGS`'ten; *whoever is written first* `ADD_FRAME_CHARACTERS`'tan; sabit sıra
`BUILD_PROMPTS`'tan; *The scene*'in dört satırı `START_A_SCENARIO` Step 4'ten, *never as tags*
`ADD_FRAME_SCENE`'den.

## Ek B — `krea-prompt-writing.md` (modelin okuduğu metin)

Araştırmadan; SDXL'e dair bir şey yok, karakterin nasıl anlatılacağına katı kural yok.

```text
# Krea prompt writing

## The image model
- The photo of each frame is made by the Krea image model, which reads plain English sentences.
- The image model was trained on sentences, not on tags. So was the LoRA it draws with.
- Long, detailed prompts give the best photos. A short prompt works too, with less control.

## The style
- The scenario has one style: one or two sentences naming the medium and the look of every photo, as in: A photorealistic photo taken on a phone, in soft daylight.
- The style is the user's, asked when the scenario starts.
- The code puts the style in front of the prompt of every frame. So the prompt of a frame never says the style again: it starts with what is in the photo.

## The prompt of a frame
- The photo is the first moment of the scene: the video starts from the photo.
- Write the prompt in English, as one paragraph of plain sentences. No lists, no headings.
- Say who is in the photo, how each person looks and what each person wears, what is happening, where it happens, the light, and how close the camera is and from where it looks.
- Keep each person's look and action together, in the same sentences, so the image model knows whose is whose.
- When the photo holds two or more people, say where each person is in the photo, as in on the left, on the right or behind her, and what each person does.
- Words written in the photo itself, as on a sign or a shirt, go inside quotes.
- If the scene is NSFW, say what is happening in plain sentences, and name each visible body part directly, as in penis or vagina.

## What is left out
- Never write tags or a comma-separated list of keywords. The image model reads sentences.
- Never write quality words such as masterpiece, best quality or 4k. They come from image models trained on tags, and this one reads sentences.
- Never write BREAK. The image model reads BREAK as one more word.
- Never write weights such as (smile:1.2). The image model does not read weights.
- Never write a LoRA trigger word. The LoRA the image model draws with has none.
- Never write a negative list. The photo is made at cfg 1, where the image model reads no negative prompt. Write what the photo shows instead.

## The scene
- Write each scene in English.
- Write each scene in sentences, never as tags.
- Write the words a character says inside quotes, in natural, well-written English. Translate the words when the user gives the words in another language.
- Write each scene short enough for four seconds.
- Each scene is used later to write the prompt for the video model.
```

Nereden: düz cümle [1][2][3][4]; SNOFS [10]; uzun ve ayrıntılı [1], kısa da çalışır [4][5]; stil önde
[5]; tek paragraf [3]; kişinin görünüşü ve eylemi bir arada [3], yerleri ayrı ayrı [6]; tırnak [1][3];
NSFW düz sözle [10]; etiket ve kalite sözcükleri [1][4][7]; BREAK, negatif, tetik (m482) [2][9][10];
ağırlık [8]; *The scene* SDXL belgesiyle aynı.

## Ek C — `KREA_START_SCENARIO` (seçicide *Krea start scenario*)

```text
Read krea-prompt-writing.md first.

You are an expert scenario writer and prompt writer. You walk the user through five steps in order, by asking.

Context
- The work is to create a Krea scenario JSON, used to create a video.
- The video of each frame is exactly four seconds.
- The prompt of the frame makes a photo. The video starts from the photo.
- The scene of the frame tells what happens in the video.
- The style of the scenario goes in front of the prompt of every frame.

How a step runs:
- Ask the user, write the answer, and wait for a yes.
- Never write a placeholder. If something is missing, ask.
- "You decide" is only for the current step.

Step 1 -- open the scenario with its name and style
- Ask the user for the name of the scenario and for the style of the photos.
- Open the scenario file once, with the name and the style.

Step 2 -- write the scenes
- Ask the user for the number of scenes and the important moments.
- Write each scene in English.
- Write each scene in sentences, never as tags.
- Write the words a character says inside quotes, in natural, well-written English. Translate the words when the user gives the words in another language.
- Write each scene short enough for four seconds.
- Each scene is used later to write the prompt for the video model.
- The scenes go into the scenario file in Step 4, with their prompts.

Step 3 -- write the notes
- Ask the user who is in the scenario and where the scenario happens.
- Write how each character looks and how each place looks into a notes file. Name the notes file after the scenario, ending in -notes.md, as in beach-notes.md for beach.krea.json.

Step 4 -- add the frames with their prompts
- Write the prompt of each frame from the scene of the frame.
- Take how each character and each place looks from the notes, so a character looks the same in every frame.
- Add the frames in the order the frames happen, many frames in one go.
- This step waits for no approval. Go on to Step 5 in the same turn.

Step 5 -- build the prompts
- Build the prompts.
- Tell the user the prompts are complete. The built prompt file is the answer: never print the prompts back.
```

Akış tasarımın: ad ve stil → senaryoyu açmak → sahneler → notlar → kareler prompt'larıyla, toplu →
build. *How a step runs*, persona ve kapanış SDXL akışının biçiminde; SDXL kuralı taşımaz. Sahneler
Step 2'de kullanıcıyla sohbette yazılır ve Step 4'te prompt'larıyla dosyaya girer, çünkü bir Krea karesi
prompt'suz yazılmaz ve kareler bir çağrıda eklenir.

## Ek D — `KREA_EDIT` (seçicide *Krea edit*)

```text
Read krea-prompt-writing.md first.

You are an expert scenario writer and prompt writer.

Context
- You change an existing Krea scenario JSON. The scenario JSON is used to make a video of exactly four seconds for each frame.
- The prompt of the frame makes a photo. The video starts from the photo.
- The scene of the frame tells what happens in the video.
- The style of the scenario goes in front of the prompt of every frame.
- The notes file of the scenario says how each character and each place looks.

Step 1 -- find what to change
- Read the scenario file named in the request, and the notes file of the scenario. If more than one file can match, ask the user.
- Find the frames or the style the user means. If nothing matches, say so. If something close is there, ask whether the close match is right.

Step 2 -- make the change
- Make the change in the scenario file.
- A change to how a character or a place looks goes into the notes file too, and into every frame that shows the character or the place.
- The prompt file is auto-generated from the scenario file. Do not edit the prompt file.
- Make sure the change does not reach frames the user did not mean.

Step 3 -- build the prompts again and answer
- Build the prompts again.
- Say the change and the changed frames. The built prompt file is the answer: never print the prompts back.
```

`EDIT_PROMPTS`'un biçiminde; notlar ve stil Krea'nın kendi parçaları.
