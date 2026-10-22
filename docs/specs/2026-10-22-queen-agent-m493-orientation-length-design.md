# Madde 493 · QueenAgent yönü ve klip süresini başta sorar — tasarım

**Tarih:** 22 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-20-queen-agent-v11-roadmap.md),
493 · v11-6 · **Dal:** `feat/queenagent-v11`, ana klasörde · **Plan:**
[m493 planı](../plans/2026-10-22-queen-agent-m493-orientation-length-plan.md) · **Öncesi:**
[m492](2026-10-22-queen-agent-m492-krea-prompts-design.md) · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

Kararların hepsi kullanıcının, 22 Ekim; hiçbiri burada yeniden açılmadı. Modelin okuyacağı altı metnin
yeni hâli ekte, İngilizce, kodda olduğu gibi.

## Ne, neden

Kullanıcı, 22 Ekim: *"biz videoları yatay yapma özelliği eklemedik mi, queen agent başta sormalı ki ona
göre prompt yazsın"*; *"bir de video süresi var"*. Queen Editor v10'da fotoğraf ve video yatay ya da
dikey üretilebiliyor (476 – 477), ve bir klibin süresi seçiliyor.

**Bugün** (`queen-agent/backend/features/workspace/domain/prompt.py`):
- *"four seconds"* sabit: `EDIT_PROMPTS` (Context), `START_A_SCENARIO` (Context, Step 4, Step 6'nın
  tamamı), `KREA_START_SCENARIO` (Context, Step 2), `KREA_EDIT` (Context), `SDXL_GUIDE` ve `KREA_GUIDE`
  (*The scene*).
- `SDXL_GUIDE`, *The image model*: *"at 1024 x 1536: portrait, 2:3"* — yalnız dikey. `KREA_GUIDE`'da boyut
  yok.
- Notes dosyası yalnız Krea akışında (türsüz adla, `beach.krea.json` → `beach-notes.md`; karakter ve
  mekân görünüşleri); SDXL'de yok.

**Olacak:** iki start skill'i önce yönü ve bir klibin süresini sorar; cevaplar notes dosyasına yazılır;
iki edit onu okur, yoksa sorar; hiçbir metin süreyi ya da boyutu sabitlemez; prompt'lar fotoğrafı
seçilen yöne göre kadrajlar.

## Kullanıcının kararları (22 Ekim)

1. **İki start skill'in ilk adımı sorar:** yatay mı dikey mi, bir klip kaç saniye *("start senaryoların
   başına ilk madde olarak yatay mı dikey mi, bir klip kaç saniye olacak diye sorsan yeterli olur")*.
   **Ayrı bir adım olarak, en başa** *("ayrı bir adım olarak eklensin ilk adıma")*: sonraki adımların
   numaraları ve SDXL'in `-review-N.md` adları birer kayar.
2. **Cevaplar `<senaryo>-notes.md`'ye yazılır** *("sonra da notes'a not alırlar")*.
3. **SDXL start da notes dosyasını açar; SDXL edit işe başlarken onu okur** *("SDXL start scenario da
   <senaryo>-notes.md açsın, yönü ve süreyi oraya yazsın. SDXL edit de işe başlarken bu notu okusun.")*.
   Krea edit notes'u zaten okuyor. **Eski bir senaryonun notes'u yoksa edit skill'i yönü ve süreyi
   kullanıcıya sorar** *("mantıklı")*.
4. **Sabit değerler gider:** *"four seconds"* seçilen süre olur, SDXL belgesindeki sabit dikey 1024 × 1536
   seçilen yön olur; prompt'lar fotoğrafı o yöne göre kadrajlar, SDXL'de de Krea'da da.
5. **Yalnız prompt metinleri ve testleri değişir;** yeni araç, yeni JSON alanı yok — yön ve süre notes
   dosyasında yaşar.
6. **Bir modelin kuralı yalnız o modelin belgesinde ve skill'lerinde durur** (492'nin kuralı).
7. **Kelime sınırı aşılırsa gerektiği kadar yükselir,** yazılı kararla *("sınır gerektiği kadar
   yükseltilsin")*; yeni sayılar durakta kullanıcıya söylenir.
8. **Prompt metinlerini kullanıcı sonda okur** *("en son promptları ben okuyacağım")*; kod öncesi durak
   yok.
9. **Notes dosyasının adı türü taşır** *(kullanıcı, 22 Ekim — "evet böyle olsun")*: senaryonun dosya adı,
   `.json`'suz, arkasına `-notes.md` — `beach.sdxl.json` → `beach.sdxl-notes.md`, `beach.krea.json` →
   `beach.krea-notes.md`; `build_prompts`'un `beach.sdxl.py`'si gibi. 492'nin türsüz adı
   (`beach-notes.md`) bırakıldı: SDXL de notes açınca aynı projedeki `beach.sdxl.json` ile
   `beach.krea.json` aynı dosyayı paylaşır, ikinci start'ın `create_file`'ı reddedilirdi (reviewer
   bulgusu).

## Ne değişir

Yalnız `prompt.py`'deki altı metin ve onları tutan testler. Kod, araç, alan, ön yüz değişmez; `dist`
kurulmaz.

### 1. Ortak sözler

Altı metin aynı üç sözü kullanır, ki model bir metinden öbürüne aynı şeyi okusun:
- **"landscape or portrait"** — yön.
- **"the video length: how many seconds the video of each frame is"** — süre. Kullanıcının *"bir klip"*i
  metinlerde zaten *"the video of each frame"* diye geçiyor; yeni bir ad (*clip*) açılmadı.
- **"the notes file of the scenario"** — ikisinin yaşadığı yer.

### 2. Start skill'leri — `START_A_SCENARIO`, `KREA_START_SCENARIO`

- **Context:** *"The video of each frame is exactly four seconds."* yerine *"The video is landscape or
  portrait, and the video of each frame is exactly the video length, in seconds. The user chooses both
  in Step 1."*
- **Yeni Step 1 — "ask the orientation and the video length":** iki soruyu sorar; cevapların notes
  dosyasına hangi adımda gireceğini söyler; kullanıcı cevaplayınca onay beklemeden Step 2'ye geçer
  (*"This step waits for no approval once the user answers."*). Onay istemez: cevap onaydır, üstüne bir
  "evet" daha bir tur harcardı.
- **Notes dosyası, senaryonun adlandığı adımda açılır,** çünkü adı senaryonun dosya adından gelir
  (*"as in beach.sdxl-notes.md for beach.sdxl.json"* / *"as in beach.krea-notes.md for
  beach.krea.json"*, karar 9). Step 1'de senaryonun adı henüz yok; cevaplar o adıma kadar
  sohbette durur, sonra dosyaya yazılır (kullanıcının *"sonra da notes'a not alırlar"*ı).
  - SDXL: Step 3 (*write the characters and outfits*), senaryo dosyasını açan satırın arkasında.
  - Krea: Step 2 (*open the scenario with its name and style*), aynı yerde. Krea'nın notes adımı
    (Step 4) karakter ve mekân görünüşlerini artık **o** dosyaya yazar; dosyayı adlandıran satır Step
    2'ye taşındı.
- **Yalnız SDXL Step 1:** *"If the notes file of the scenario is already in the project, take the
  orientation and the video length from the notes file instead."* Sebep: SDXL akışı yeni bir sohbette
  planından devam eder (Step 2); bu satır olmasa devam eden her sohbet aynı soruyu yeniden sorardı. Krea
  akışının planı ve devamı yok; satır orada gereksiz bir parça olurdu.
- **Sahne kuralı:** *"Write each scene short enough for four seconds."* yerine *"Write each scene short
  enough for the video length: how many seconds the video of each frame is."* — dört kopyada (iki belge,
  iki start) bayt bayt aynı.
- **Kadraj:**
  - SDXL Step 6, belgenin kural kopyalarının yanında **Rule 7:** *"The photo has the orientation of the
    video, landscape or portrait. Choose the camera angle and where each character is in the photo to fit
    the orientation."* Belgede de aynı satır (aşağıda, 4); Step 6 Rule 1 – 6'yı belgeyle aynı tutuyordu,
    7 de aynı.
  - Krea Step 5: *"Frame the photo of each frame for the orientation in the notes."*
- **SDXL'de numaralar:** 10 adım 11 olur (*"eleven steps"*). Plan örneği `- [ ] 2. write the plan`. Eski
  Step 6 – 9'un denetimleri Step 7 – 10, review dosyaları `-review-7.md` … `-review-10.md`; negatif liste
  Step 11. *"by the rules of Step 5"* → *Step 6*; her *"Go on to Step N"* ve *"go to Step N"* birer kayar.
- **Step 7 (eski 6), süre denetimi:** başlık *"fit each scene into the video length"*; *"four seconds"*
  geçen dört cümle *"the video length"* olur, ikiye bölünen sahne *"two scenes of the video length
  each"*. Denetimlerin kuralları korunur: zamir yok, araç ve alan adı yok, *image model* yok.
- **Krea'da numaralar:** 5 adım 6 olur (*"six steps"*); *"in Step 4"* → *Step 5*, *"Go on to Step 5"* →
  *Step 6*.

### 3. Edit skill'leri — `EDIT_PROMPTS`, `KREA_EDIT`

- **Context:** *"used to make a video of exactly four seconds for each frame"* yerine *"used to make a
  video for each frame"*, ve yeni satır: *"The notes file of the scenario says whether the video is
  landscape or portrait, and the video length: how many seconds the video of each frame is."* Krea'da
  eski notes satırı *"The notes file also says how each character and each place looks."* olur.
- **Step 1:** SDXL edit senaryonun yanında notes dosyasını da okur (Krea edit zaten okuyordu). Yeni satır,
  ikisinde aynı, örnek ad kendi türüyle: *"If the notes file is missing, or does not say the orientation
  and the video length, ask the user. Write the answers into the notes file, as in beach.sdxl-notes.md
  for beach.sdxl.json."* (Krea'da *beach.krea-notes.md for beach.krea.json*). Hem notes'u olmayan eski SDXL senaryosunu hem 492'de açılmış, yönsüz Krea notes'unu
  karşılar. Cevabın dosyaya yazılması bir sonraki edit'in yeniden sormaması için; dosyanın adı, notes'u
  hiç olmayan senaryoda modelin onu adlandırabilmesi için.

### 4. Belgeler — `SDXL_GUIDE`, `KREA_GUIDE`

- **Boyut, iki yön için, Queen Editor'ün kendi değerleriyle** (bakıldı, 22 Ekim):
  - SDXL — `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`,
    `SIZES = {LANDSCAPE: (1536, 864), PORTRAIT: (1024, 1536)}`: *"at 1536 x 864 for a landscape video,
    16:9, or at 1024 x 1536 for a portrait video, 2:3."*
  - Krea — `comfy_krea_photo_generator.py`, `SIZES = {LANDSCAPE: (1280, 720), PORTRAIT: (832, 1248)}`:
    *"The photo is made at 1280 x 720 for a landscape video, 16:9, or at 832 x 1248 for a portrait video,
    2:3."* 492'de Krea belgesine boyut yazılmamıştı (*"No size: that is v11-6's"*); iki model ayrı
    boyutlarda çizdiği için her belge kendi modelininkini yazar.
- **Kadraj:** SDXL belgesinde *The prompt of a frame*'e **Rule 7** (Step 6'yla aynı satır); Krea belgesinde
  aynı bölüme: *"The photo has the orientation of the video, landscape or portrait. Choose how close the
  camera is and where each person is in the photo to fit the orientation."* — Krea'nın kendi sözüyle
  (kamera yakınlığı, kişinin yeri), etiket ve SDXL sözü yok.
- **Sahne:** *The scene*'in süre satırı, start skill'leriyle aynı.
- Belgeler notes dosyasından söz etmez: notes bir akış parçası, skill'lerin; belge yalnız prompt'un nasıl
  yazıldığını söyler.

### 5. Yorumlar

`prompt.py`'de: skill bloğunun yorumu (Improve'un denetimleri artık *Steps 7 – 11*), Krea skill'lerinin
yorumu (adım numaraları; 493'ün notu), belgelerin yorumu (*"No size: that is v11-6's"* kalkar; iki boyut
ve kaynakları). Testlerde 493'ü anan yorumlar.

### 6. Testler

- `test_skills.py`: `STEPS` 11, `KREA_STEPS` 6; adım numaralı her test bir kayar (`_step(5)` → `_step(6)`
  …, `CHECKS = [7, 8, 9, 10]`); yeni testler — iki start'ın Step 1'i, SDXL'in notes'tan okuması, notes'un
  senaryoyla açılması (ikisinde), Rule 7, Krea'nın kadraj satırı, iki edit'in notes'u okuyup eksikse
  sorması, dört skill'in notes örneği türüyle (`NOTES_EXAMPLE`, hiçbirinde `beach-notes.md` yok), hiçbir
  skill'de *"four seconds"* ve *"1536"* yok.
- `test_prompt.py`: iki belgenin sahne bölümü *"short enough for the video length"*, hiçbirinde *"four
  seconds"* yok; iki belge kadrajı söylüyor; her belge kendi boyutunu iki yön için veriyor.
- `test_tools.py`: belge testi *"1536 x 864"* ve *"1024 x 1536"* arıyor.
- **Kelime tavanları** (`test_the_texts_stay_short_enough_to_be_read`, yazılı kararla, kullanıcının 22
  Ekim sözü):

  | Metin | Önce (sayı / tavan) | Sonra (sayı / tavan) |
  |---|---|---|
  | `START_A_SCENARIO` | 1 834 / 1 835 | 2 012 / 2 020 |
  | `EDIT_PROMPTS` | 200 / 205 | 263 / 275 |
  | `KREA_START_SCENARIO` | 416 / 430 | 531 / 540 |
  | `KREA_EDIT` | 260 / 270 | 314 / 325 |

## Maliyet

Koddan sayıldı, ölçülmedi. Drive ve ağ gidişlerinde yalnız modelin seçtiği araç çağrıları değişir; kod
yolu aynı.

| İşlem | Drive | Not |
|---|---|---|
| SDXL start, notes dosyasını açmak | 1 yazma (+ `projects.json` kuyruğu) | senaryo başına bir kez, `create_file` |
| Krea start | + 1 okuma + 1 yazma, senaryo başına bir kez | notes artık Step 2'de açılır (`create_file`, 1 yazma — bugünkü tek yazmanın yerine) ve Step 4'te görünüşler eklenir (`edit_file`: 1 okuma + 1 yazma) |
| SDXL edit, notes'u okumak | 1 okuma, kutuda değilse | sohbet başına bir kez; kutudaysa 0 |
| Edit, notes yoksa ya da eksikse | 1 yazma | yalnız eski senaryoda, bir kez |
| Belgeler | 0 | metin bellekte; birkaç satır uzadı |

**Token:** seçili skill isteğin kuyruğunda her model turunda tam fiyatla gider. SDXL start ≈ 178 kelime
(≈ 230 token) uzadı, Krea start ≈ 115, SDXL edit ≈ 63, Krea edit ≈ 54. Belgeler okunduğu sohbette
kutuda: SDXL ≈ 45, Krea ≈ 55 kelime uzadı. Önbellekli baş (`SYSTEM_PROMPT`, araç listesi) değişmez.

## Ne kaybolabilir, ne bozulabilir

- **Yazma:** kod yolu değişmez; notes `create_file` / `edit_file` ile, `Store.write_text`'in geçici dosya
  ve yerine koyma yolundan. Bir senaryonun notes'u bir kez açılır; ikinci `create_file` adı alınmış diye
  reddedilir.
- **Ad çakışması — kapandı** (karar 9): notes adı türü taşıdığı için `plaj.sdxl.json` ile `plaj.krea.json`
  aynı projede ayrı dosyalar açar (`plaj.sdxl-notes.md`, `plaj.krea-notes.md`).
- **492'den kalan Krea notes'u:** 492 ile 493 arasında açılmış bir Krea senaryosunun notes'u türsüz adla
  (`plaj-notes.md`) durur. Krea edit `plaj.krea-notes.md`'yi arar; bulamazsa yönü ve süreyi sorar ve yeni
  adla bir notes açar, eski dosyadaki görünüşler orada kalır. Taşıma kodu yok (492'nin kuralı); model
  dosya listesinde eskisini görüp okuyabilir, garanti değil.
- **Model sırayı atlarsa** yön ve süre sorulmadan iş başlar; edit'in eksik notes'ta sorması ve SDXL'in
  notes'tan okuması bunu sonradan yakalar. Garanti yok: davranışı yalnız Colab gösterir.
- **SDXL'de devam eden sohbet:** projede başka bir senaryonun notes'u varsa Step 1 onu okuyabilir. Satır
  *"the notes file of the scenario"* diyor; bir projede birden çok SDXL senaryosu olduğunda model hangi
  senaryo olduğunu plan ve dosya adlarından seçer. Kabul edilebilir: yanlış seçim kullanıcının ilk
  cevabında görünür.
- **Queen Editor yönü notes'tan okumaz.** Kullanıcı Queen Editor'de yönü elle seçer; QueenAgent'ın
  yazdığıyla farklı seçerse prompt öbür yöne kadrajlanmış olur. Bu madde iki aracı bağlamaz (iki ayrı
  proje, 8 Ekim).
- **İki istek aynı anda, çökme:** kod yolu değişmediği için bugünkü gibi; bir sohbette tur tektir.
- **Yol ve gizli şey:** yeni bir değer yola dönmez; metinlerde gizli bir şey yok.

## Sınırlar

- Kod, araç, JSON alanı, `skills.py`, ön yüz, Queen Editor değişmez. `dist` kurulmaz.
- Süreye bir sınır ya da Queen Editor'ün seçebildiği değerlerin listesi yazılmaz: süre kullanıcının
  cevabı, olduğu gibi.
- Belgeler notes dosyasını anmaz; notes yalnız skill'lerde.

## Bitti sayılır

1. Testler gösteriyor ki: iki start'ın Step 1'i yönü ve süreyi soruyor ve Step 2'ye geçiyor; SDXL Step 1
   notes'tan okuyabiliyor; notes, senaryonun adlandığı adımda yön ve süreyle açılıyor (SDXL Step 3, Krea
   Step 2); iki edit notes'u okuyor, eksikse sorup yazıyor; hiçbir skill'de ve belgede *"four seconds"*
   yok, skill'lerde *"1536"* yok; SDXL akışı 11, Krea akışı 6 adım, review adları 7 – 10; SDXL Step 6'da ve
   belgesinde Rule 7, Krea'nın Step 5'inde ve belgesinde kadraj satırı; her belge kendi boyutunu iki yön
   için veriyor; tavanlar yukarıdaki tabloda.
2. Dört takım tek tek yeşil.
3. **QA, Playwright:** dosya panelinde `sdxl-prompt-writing.md` ve `krea-prompt-writing.md` açılıyor;
   ikisinde de *"four seconds"* ve tek başına *"1024 x 1536: portrait"* yok, iki yönün boyutu ve kadraj
   satırı var. Seçicide dört satır bugünkü gibi. **Not:** seçici skill'in yalnız adını ve kısa açıklamasını
   gösterir (`skills.js`), talimat metnini göstermez; dört skill'in metni testlerle ve `prompt.py`'den
   denetlenir, ekranda ancak gerçek bir model turunda görünür.
4. **Colab — kullanıcının:** start skill'i önce yönü ve süreyi soruyor, cevabı `<ad>.sdxl-notes.md` ya da
   `<ad>.krea-notes.md`'ye
   yazıyor; sahneler seçilen süreye, prompt'lar seçilen yöne göre; edit notes'u okuyor, yoksa soruyor.

---

## Ek A — `START_A_SCENARIO` (seçicide *SDXL start scenario*)

```text
Read sdxl-prompt-writing.md first.

You are an expert scenario writer and prompt writer. You walk the user through eleven steps in order, by asking.

Context
- The work is to create a scenario JSON, used to create a video.
- The video is landscape or portrait, and the video of each frame is exactly the video length, in seconds. The user chooses both in Step 1.
- The prompt of the frame makes a photo. The video starts from the photo.
- The scene of the frame tells what happens in the video.
- The image model is weak.

How a step runs:
- Ask the user, write the answer into the scenario JSON, and wait for a yes.
- Never write a placeholder. If something is missing, ask.
- "You decide" is only for the current step.

Step 1 -- ask the orientation and the video length
- Ask the user whether the video is landscape or portrait, and how many seconds the video of each frame is.
- If the notes file of the scenario is already in the project, take the orientation and the video length from the notes file instead.
- The answers go into the notes file in Step 3.
- This step waits for no approval once the user answers. Go on to Step 2 in the same turn.

Step 2 -- write the plan
- Look for a plan in the project.
- If there is no plan, write a plan file: one line for each step, as in - [ ] 2. write the plan. A done step reads - [x] 2. write the plan.
- If there is a plan, read the plan and carry on from where the work stopped. The plan's marked steps show how far the work got, and the files of the project confirm it.
- This step waits for no approval. Go on in the same turn.

Step 3 -- write the characters and outfits
- Ask who is in the scenario.
- Open the scenario file once, with a name for the scenario.
- Write the orientation and the video length into a notes file. Name the notes file after the scenario file, ending in -notes.md, as in beach.sdxl-notes.md for beach.sdxl.json.
- Write each character as an entry. Use the name from the user. Without a name, use short English words, as in young man.
- Write each outfit as one entry: all the clothes worn together, as in red dress and black heels.

Step 4 -- write the places
- Ask where the scenario happens.
- Write each place as an entry.
- Do not add a mirror to a place unless the user asks for one. A mirror breaks the image.

Step 5 -- write the scenes
- Ask the user for the number of scenes and the important moments.
- Write each scene in English.
- Write each scene in sentences, never as tags.
- Write the words a character says inside quotes, in natural, well-written English. Translate the words when the user gives the words in another language.
- Write each scene short enough for the video length: how many seconds the video of each frame is.
- Each scene is used later to write the prompt for the video model.

Step 6 -- update the frames and build the prompts
Context
- The prompt of a frame describes one photo: the first moment of the scene.
- The image model is weak and draws every tag in the prompt. A complex prompt breaks the image.
- Some tags are not visible from some camera angles. So a character, an outfit or a place can have more than one entry, for different camera angles.
- The most common mistake: a tag hidden by the camera angle goes onto another character. For example, the hair of a hidden head ends up on another character.
- Rule 1: If one of the character's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 2: If one of the outfit's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 3: If one of the place's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 4: The image model draws one photo. The whole prompt of the frame must describe only one photo. If the prompt describes more than one photo, remove the extra part.
- Rule 5: The whole prompt of the frame must be simple enough for the weak image model. If a part of the prompt is too hard, make the part simpler, and keep the same moment.
- Rule 6: If the scene is NSFW, name each visible body part directly, as in penis or vagina. Never use a euphemism.
- Rule 7: The photo has the orientation of the video, landscape or portrait. Choose the camera angle and where each character is in the photo to fit the orientation.
Work
- Update the frames one at a time.
- For each frame, first read the scene of the frame. Then update the frame by the rules.
- After the last frame, build the prompts.
- This step waits for no approval. Go on to Step 7 in the same turn.

Step 7 -- fit each scene into the video length
Context
- The scene of each frame becomes a video of exactly the video length. A scene with more events does not fit the video.
Part 1 -- review
- Tell the user in one short line what the step improves.
- In the built prompt file, find each scene with more events than the video length can show.
- Write the frame numbers and the reason for each frame in a review file. Name the review file after the scenario, ending in -review-7.md. If every scene fits, write no review file and go to Step 8.
Part 2 -- fix
- Fix only the frames in the review file.
- If the scene can be written again to fit the video length with every event kept, write the scene again.
- If not, split the scene into two scenes of the video length each, and put the second scene right after the first scene.
- Update each changed frame and each new frame by the rules of Step 6.
- Build the prompts again.
- This step waits for no approval. Go on to Step 8 in the same turn.

Step 8 -- fit each prompt into one photo
Context
- The image model is weak and draws every tag in the prompt. The image model draws one photo, so a prompt describing more than one photo breaks the image.
Part 1 -- review
- Tell the user in one short line what the step improves.
- In the built prompt file, find each prompt describing more than one photo can hold.
- Write the frame numbers and the reason for each frame in a review file. Name the review file after the scenario, ending in -review-8.md. If every prompt fits into one photo, write no review file and go to Step 9.
Part 2 -- fix
- Fix only the frames in the review file. Do not change the scene, and do not add a new scene.
- Find where the extra part comes from in the scenario file, and remove the extra part there, so the prompt describes one photo.
- If other frames use the same entry, add a new entry for the frame instead.
- Build the prompts again.
- This step waits for no approval. Go on to Step 9 in the same turn.

Step 9 -- remove tags hidden by the camera angle
Context
- The image model is weak and draws every tag in the prompt, hidden or not.
- For example, the image breaks, or the image model puts the tag on another character in the photo, because the hidden part has no place in the photo. The hair of a character with a hidden head can end up on another character.
Part 1 -- review
- Tell the user in one short line what the step improves.
- In the built prompt file, find each prompt with tags hidden by the camera angle of the prompt.
- Write the frame numbers and the reason for each frame in a review file. Name the review file after the scenario, ending in -review-9.md. If no prompt has a hidden tag, write no review file and go to Step 10.
Part 2 -- fix
- Fix only the frames in the review file.
- Find where each hidden tag comes from in the scenario file, and remove the hidden tag there.
- If other frames use the same entry, add a new entry for the frame instead.
- Build the prompts again.
- This step waits for no approval. Go on to Step 10 in the same turn.

Step 10 -- simplify prompts too hard to draw
Context
- The image model is weak and draws every tag in the prompt. A prompt too hard for the image model breaks the image.
Part 1 -- review
- Tell the user in one short line what the step improves.
- For each prompt in the built prompt file, ask: can a weak image model draw the prompt as written?
- Write the frame numbers and the reason for each frame in a review file. Name the review file after the scenario, ending in -review-10.md. If every prompt can be drawn, write no review file and go to Step 11.
Part 2 -- fix
- Fix only the frames in the review file.
- Find where the hard part comes from in the scenario file, and make the hard part simpler there. The frame still shows the same moment.
- If other frames use the same entry, add a new entry for the frame instead.
- Build the prompts again.
- This step waits for no approval. Go on to Step 11 in the same turn.

Step 11 -- write the negative list
Context
- The negative list is for the image model, not the video model. The negative list tells the image model what not to draw in the photo.
- The scenario has one negative list, for every frame. A tag in the negative list works on the whole photo, not on one character.
- The biggest problem is the features of the characters mixing, as in the hair of one character on another character. Focus the negative list on keeping the features of each character apart.
- Never write a feature of a character into the negative list. For example, dark skin in the negative list made a dark-skinned man come out white.
- To keep a feature of a character, write the opposite tags instead. For example, pale male and white man for a dark-skinned man.
Work
- Tell the user in one short line what the step does.
- Read every tag of every entry of the scenario. Then write one negative list for the whole scenario.
- Write the tags by the same rules as the entries.
- Write the negative list into a file of the negative list alone. Name the file after the scenario, ending in -negative.md.
- Write only the tags into the file, separated by commas. Nothing else goes into the file.
- Tell the user the prompts and the negative list are complete.
```

## Ek B — `EDIT_PROMPTS` (seçicide *SDXL edit*)

```text
Read sdxl-prompt-writing.md first.

You are an expert scenario writer and prompt writer.

Context
- You change an existing scenario JSON. The scenario JSON is used to make a video for each frame.
- The notes file of the scenario says whether the video is landscape or portrait, and the video length: how many seconds the video of each frame is.
- The prompt of the frame makes a photo. The video starts from the photo.
- The scene of the frame tells what happens in the video.
- The image model is weak.

Step 1 -- find what to change
- Read the scenario file named in the request, and the notes file of the scenario. If more than one file can match, ask the user.
- If the notes file is missing, or does not say the orientation and the video length, ask the user. Write the answers into the notes file, as in beach.sdxl-notes.md for beach.sdxl.json.
- Find the frames or the entries the user means. If nothing matches, say so. If something close is there, ask whether the close match is right.

Step 2 -- make the change
- Make the change in the scenario file.
- The prompt file is auto-generated from the scenario file. Do not edit the prompt file.
- Make sure the change does not reach frames the user did not mean.

Step 3 -- build the prompts again and answer
- Build the prompts again.
- Say the change and the changed frames. The built prompt file is the answer: never print the prompts back.
```

## Ek C — `KREA_START_SCENARIO` (seçicide *Krea start scenario*)

```text
Read krea-prompt-writing.md first.

You are an expert scenario writer and prompt writer. You walk the user through six steps in order, by asking.

Context
- The work is to create a Krea scenario JSON, used to create a video.
- The video is landscape or portrait, and the video of each frame is exactly the video length, in seconds. The user chooses both in Step 1.
- The prompt of the frame makes a photo. The video starts from the photo.
- The scene of the frame tells what happens in the video.
- The style of the scenario goes in front of the prompt of every frame.

How a step runs:
- Ask the user, write the answer, and wait for a yes.
- Never write a placeholder. If something is missing, ask.
- "You decide" is only for the current step.

Step 1 -- ask the orientation and the video length
- Ask the user whether the video is landscape or portrait, and how many seconds the video of each frame is.
- The answers go into the notes file in Step 2.
- This step waits for no approval once the user answers. Go on to Step 2 in the same turn.

Step 2 -- open the scenario with its name and style
- Ask the user for the name of the scenario and for the style of the photos.
- Open the scenario file once, with the name and the style.
- Write the orientation and the video length into a notes file. Name the notes file after the scenario file, ending in -notes.md, as in beach.krea-notes.md for beach.krea.json.

Step 3 -- write the scenes
- Ask the user for the number of scenes and the important moments.
- Write each scene in English.
- Write each scene in sentences, never as tags.
- Write the words a character says inside quotes, in natural, well-written English. Translate the words when the user gives the words in another language.
- Write each scene short enough for the video length: how many seconds the video of each frame is.
- Each scene is used later to write the prompt for the video model.
- The scenes go into the scenario file in Step 5, with their prompts.

Step 4 -- write the notes
- Ask the user who is in the scenario and where the scenario happens.
- Write how each character looks and how each place looks into the notes file.

Step 5 -- add the frames with their prompts
- Write the prompt of each frame from the scene of the frame.
- Frame the photo of each frame for the orientation in the notes.
- Take how each character and each place looks from the notes, so a character looks the same in every frame.
- Add the frames in the order the frames happen, many frames in one go.
- This step waits for no approval. Go on to Step 6 in the same turn.

Step 6 -- build the prompts
- Build the prompts.
- Tell the user the prompts are complete. The built prompt file is the answer: never print the prompts back.
```

## Ek D — `KREA_EDIT` (seçicide *Krea edit*)

```text
Read krea-prompt-writing.md first.

You are an expert scenario writer and prompt writer.

Context
- You change an existing Krea scenario JSON. The scenario JSON is used to make a video for each frame.
- The prompt of the frame makes a photo. The video starts from the photo.
- The scene of the frame tells what happens in the video.
- The style of the scenario goes in front of the prompt of every frame.
- The notes file of the scenario says whether the video is landscape or portrait, and the video length: how many seconds the video of each frame is.
- The notes file also says how each character and each place looks.

Step 1 -- find what to change
- Read the scenario file named in the request, and the notes file of the scenario. If more than one file can match, ask the user.
- If the notes file is missing, or does not say the orientation and the video length, ask the user. Write the answers into the notes file, as in beach.krea-notes.md for beach.krea.json.
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

## Ek E — belgelerde değişen satırlar

Belgelerin geri kalanı 492'nin Ek A ve Ek B'sindeki gibi.

`sdxl-prompt-writing.md`:

```text
## The image model
- The photo of each frame is made by an SDXL-family image model trained on Danbooru's own tags, at 1536 x 864 for a landscape video, 16:9, or at 1024 x 1536 for a portrait video, 2:3.

## The prompt of a frame   (Rule 6'nın arkasına)
- Rule 7: The photo has the orientation of the video, landscape or portrait. Choose the camera angle and where each character is in the photo to fit the orientation.

## The scene
- Write each scene short enough for the video length: how many seconds the video of each frame is.
```

`krea-prompt-writing.md`:

```text
## The image model   (son satır)
- The photo is made at 1280 x 720 for a landscape video, 16:9, or at 832 x 1248 for a portrait video, 2:3.

## The prompt of a frame   ("Say who is in the photo …" satırının arkasına)
- The photo has the orientation of the video, landscape or portrait. Choose how close the camera is and where each person is in the photo to fit the orientation.

## The scene
- Write each scene short enough for the video length: how many seconds the video of each frame is.
```
