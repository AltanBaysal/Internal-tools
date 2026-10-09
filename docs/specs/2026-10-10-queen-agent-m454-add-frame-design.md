# Madde 454 · `add_scene` `add_frame` olur — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
454 · **Dal:** `feat/queenagent-v10`, ana klasörde, **commit'lenmeden** — tool'un adı ve bir ret cümlesi
modele gider; 10 Ekim'den beri bu koşuda metni Claude okuyup doğrular ve commit'ler *(kullanıcı —
"kendin verify et promptları ve sonraki aşamaya geç")* · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Plan:** [m454 planı](../plans/2026-10-10-queen-agent-m454-add-frame-plan.md)

## Ne, neden

Kullanıcı, 9 Ekim: *"neden add scene ve update frame, update scene değil mesela?"*; *"isimleri
standartlaştıralım"*.

**Bugün** frame'i `add_scene` ekliyor, `update_frame` ve `remove_frame` değiştirip siliyor: aynı şeye iki
kelime. Dosya (`frames`), numaralar (`frame 3`), tool'ların cevapları (*"as frame 3"*, *"2 frames after it
moved up"*) hep *frame* diyor; tek ayrık ad `add_scene`.

**Olacak:** `add_frame`, `update_frame`, `remove_frame`. *Scene* frame'in içindeki sahne cümlesinin adı
olarak kalır. Davranış değişmez.

## Olacak

### 1 · Tool'un adı — `domain/tools.py`

`TOOL_SPECS`'te `"name": "add_scene"` → `"name": "add_frame"`, ve `run_tool`'un dalı `add_frame`'i
`_add_frame`'e yollar.

**Liste parametresi `scenes` → `frames`** *(ana agent, 10 Ekim — "each item is a frame with its own
`scene` field, and the user's 'isimleri standartlaştıralım' is the point of the item")*: her öğe kendi
`scene` cümlesini taşıyan bir frame; liste de *scenes* adını taşısaydı kelime aynı çağrıda iki anlama
gelirdi. Zorunlu alanlar `["file", "frames"]`. Öbür parametreler — `file`, `before`, ve her öğenin
`scene`, `characters`, `location`'ı — ve onların tarifleri aynı.

Fonksiyon `_add_scene` → `_add_frame`, öbür ikisi (`_update_frame`, `_remove_frame`) gibi tool'un adını
taşısın diye. İçi aynı.

### 2 · Metinlerin adları — `domain/prompt.py`

Altı sabit tool'un adını taşıyor; tool'la birlikte adlarını değiştirirler. Metinleri değişmez, listenin
tarifi dışında — o parametrenin kendisini anıyor:

| Bugün | Sonra |
|---|---|
| `ADD_SCENE` | `ADD_FRAME` |
| `ADD_SCENE_BEFORE` | `ADD_FRAME_BEFORE` |
| `ADD_SCENE_SCENES` — *"The scenes to add. A list even when there is one of them."* | `ADD_FRAME_FRAMES` — *"The frames to add. A list even when there is one of them."* |
| `ADD_SCENE_SCENE` | `ADD_FRAME_SCENE` |
| `ADD_SCENE_CHARACTERS` | `ADD_FRAME_CHARACTERS` |
| `ADD_SCENE_LOCATION` | `ADD_FRAME_LOCATION` |

`ADD_FRAME_SCENE` artık `UPDATE_FRAME_SCENE`'in yanında aynı düzende okunuyor: tool, sonra alan.

### 3 · Modun listesi — `domain/modes.py`

Edit modunun sormadan geçirdikleri arasında `"add_scene"` → `"add_frame"`. Ask ve Plan bugünkü gibi
sorar.

### 4 · Modele giden metin, önce ve sonra

Değişen yedi yer; öğe alanlarının tarifleri ve `ADD_FRAME`'in öbür maddeleri bayt bayt aynı.

| Yer | Bugün | Sonra |
|---|---|---|
| Tool listesindeki ad | `add_scene` | `add_frame` |
| Liste parametresinin adı ve zorunlular | `scenes`; `["file", "scenes"]` | `frames`; `["file", "frames"]` |
| Listenin tarifi | *"The scenes to add. A list even when there is one of them."* | *"The frames to add. A list even when there is one of them."* |
| Liste değilken ret | *"add_scene takes a list of scenes, even when there is one of them."* | *"add_frame takes a list of frames, even when there is one of them."* |
| Liste boşken cevap | *"No scenes were given, so scene.json is unchanged."* | *"No frames were given, so scene.json is unchanged."* |
| `ADD_FRAME`'in dördüncü maddesi | *"Every name a scene uses must already be in the file. … nothing is written unless every scene in the call is good."* | *"Every name a frame uses must already be in the file. … nothing is written unless every frame in the call is good."* |
| Öğe nesne değilken ret | *"frame 3: a scene is an object with scene, characters and location."* | *"frame 3: a frame is an object with scene, characters and location."* |

Boş liste cevabı parametreyi anıyor — boş gelen `frames` —, ve *scenes* demeye devam etseydi model
olmayan bir argümanı arardı. Son iki satır reviewer'ın bulgusu *(ana agent, 10 Ekim)*: ikisi de listenin
bir öğesini *scene* diye anıyordu, ve öğe artık bir frame.

**Değişmeyen, *scene* diyen metinler** — her biri bir sahneyi ya da sahne cümlesini anlatıyor, öğeyi
değil *(ana agent, 10 Ekim — "keep the others as they are")*: `ADD_FRAME`'in ilk satırı *"Add scenes to a
structure file, one frame each, in the order they happen."*; `ADD_FRAME_BEFORE`'un *"This is how a scene
goes into the middle"*'ı; *"frame 3: a scene needs a sentence saying what happens."*; başarı cevabı
*"Added 1 scene to scene.json as frame 3."* ve kartta *"1 scene"*.

**Kodda:** `_add_frame`'in döngüsü ve `_frame_from` öğeyi `given` diye anar, `_update_frame`'in
argümanlarına dediği gibi; docstring ve yorum *frame* der.

Ve eski adla gelen çağrı, her silinen tool'un yolundan, `run_tool`'un genel cevabını alır: *"There is no
tool called add_scene."* — yeni cümle değil, bugün `add_frames` ya da `list_files` alan cevap.

`ADD_FRAME`'in açıklaması zaten *"Write the action afterwards with update_frame."* diye bitiyor; şimdi aynı
kelimeyle doğan ve değişen frame'i anlatıyor.

### 5 · Ekran — değişmez

Adım kartı tool'un adını olduğu gibi yazar: `⏺ add_frame(scene.json)`, yanında *"1 scene"*
(`ToolCalls.jsx`'in `headOf`'u). Etiket tablosu yok, frontend'de hiçbir tool adı geçmiyor. Yeni tur
`add_frame` gösterir.

**Eski sohbet:** kaydında `{"tool": "add_scene", "target": "scene.json", "outcome": "1 scene"}` duruyor.
Okunurken ad olduğu gibi gelir (`file_chat_store._as_message`), ve kart `⏺ add_scene(scene.json)` · *1
scene* der — o turda gerçekten çalışan tool. Kayıt çevrilmez: kayıt o turda ne olduğunun tanığıdır, ve
eski ad okunaklı. İzin kartı da adı olduğu gibi yazar; eski bir izin kartı kayıtta durmuyor.

Bu yüzden `dist` yeniden kurulmaz.

### 6 · Modelin bağlamı — kayıtlı sohbet geri gidince

**DeepSeek eski `add_scene` çağrılarını hiç görmez.** Kayıtlı sohbetten modele giden yalnız her mesajın
metni: `stream_answer._conversation` her mesajı `{"role", "content": message.text}` olarak koyar. Bir
mesajın `calls`'u diske ve ekrana gider, isteğe gitmez; araç çağrıları ve `tool` mesajları yalnız o an
süren turun içinde, bellekte yaşar. Açık dosyalar kutusu (`context_box`) `calls`'tan yalnız
`read_file`'ları okur, ve onları da dosyanın adı olarak.

Yani yeni bir istek: system prompt, SDXL belgesi, metinden ibaret geçmiş, ve `add_frame`'li tool listesi.
Tool listesiyle çelişen bir çağrı geçmişte yok.

**Adın sızabileceği tek yol metin:** modelin eski bir cevabında ya da projedeki bir dosyada (ör. bir plan
dosyası) *"add_scene"* kelimesi yazılı olabilir. Model onu çağırırsa:

- `needs_permission` bilinmeyen tool'u sormaz — kullanıcıya izin kartı çıkmaz;
- `run_tool` *"There is no tool called add_scene."* der, dosyaya dokunulmaz;
- model bir sonraki turda listedeki `add_frame`'i görür.

Bedeli en çok bir model turu, ve bir kez. Önemli değil; eski ad için takma ad tutulmaz — maddenin "`add_scene`
hiçbir yerde yok"u ve tek ad kuralı onu dışarıda bırakır.

**Önbellek:** `tools` dizisi her isteğin sabit önünde. Ad değişince o ön bir kez değişir, ve ilk istekte
önbellek o noktadan sonrasını kaçırır; sonra yine bayt bayt aynı. Ad aynı uzunlukta (9 harf), istek boyu
değişmez.

## Ne tutar

**Disk:** hiç değişmez — `add_frame` bugünkü `add_scene`'in yaptığını yapar: senaryoyu bir kez okur, bir
kez yazar. **Ağ:** her model turu yine tek istek. **Token:** aynı; ad aynı uzunlukta.

## Sınırlar

- **Yalnız adlar.** Tool'un adı ve liste parametresinin adı; parametreyi ya da öğeyi anan beş cümle
  onlarla. Öğe alanlarının tarifleri, başarı cevabı (*"Added 1 scene to scene.json as frame 3."*, kartta *"1
  scene"*) ve öbür ret cümleleri aynı. Davranış aynı: yalnız argümanın anahtarı değişti.
- **456 değil.** Karakter, kıyafet ve mekânın add / update çiftlerine dokunulmaz.
- **Skill metinleri** tool'u adıyla anmıyor; dokunulmaz.
- **Diskteki senaryo dosyaları** değişmez: tool adı dosyada yazmıyor.
- **Kayıtlı sohbetler** çevrilmez; eski adım kartı eski adla görünür.
- Frontend, `dist` ve queen-editor değişmez.

## Değişen dosyalar

- `queen-agent/backend/features/workspace/domain/tools.py` — `TOOL_SPECS`'teki ad, `frames` parametresi
  ve sabit adları, `run_tool`'un dalı, `_add_frame`, üç cümle, `_frame_from`'un `given`'ı, yorumlar.
- `queen-agent/backend/features/workspace/domain/prompt.py` — altı sabitin adı, listenin tarifi,
  `ADD_FRAME`'in dördüncü maddesi.
- `queen-agent/backend/features/workspace/domain/modes.py` — Edit modunun listesi.
- Testler: `test_tools.py`, `test_modes.py`, `test_skills.py`, `test_prompt.py` (bir yorum).

## Testler

- **`test_tools.py`:** frame ekleyen bütün testler `add_frame`'i çağırır; tool listesinin kümesinde
  `add_frame` var, `add_scene` yok (bu kümenin eşitliği eski adı da dışarıda tutar). Eski adla gelen
  çağrının cevabı, silinen her tool'un tek yolu: `list_files`, `mark_step_done` ve `add_frames`'in
  testleri onu tutar. Yeni olan yalnız bunların görmediği: `test_no_tool_text_points_at_add_scene` —
  hiçbir tool'un açıklamasında ya da tarifinde `add_scene` geçmiyor. Testler listeyi `frames=` ile
  verir; parametreler tam olarak `{"file", "before", "frames"}`, zorunlular `["file", "frames"]`; liste
  değilken ret *"add_frame takes a list of frames"*; boş liste tam cümleyle *"No frames were given, so
  scene.json is unchanged."*; nesne olmayan öğe *"frame 3: a frame is an object with scene, characters
  and location."* Üç yorumun yanlışı düzelir: kayıtlı çağrı modele geri gitmez; eski ad modelin okuduğu
  sözlerde — eski bir cevap, bir dosya — durabilir.
- **`test_modes.py`:** `WRITES`'ta `add_frame`; Plan modu `add_frame`'i soruyor. Silinen tool'ları tek
  tek arayan yedi test (`list_files`, `build_character_prompts`, `write_plan`, `write_frame_prompt`,
  `write_missing_actions`, `mark_step_done`, `add_scene`) tek bir genel testle değişir *(ana agent, 10
  Ekim — onaylı)*: her modun listesi, modele verilen tool'ların alt kümesi. Listeden okunur, çünkü
  `needs_permission` bilinmeyen tool'a zaten "sorma" der ve geride kalan ad yeşil geçerdi; listeye
  bellekte `add_scene` konunca test kırmızı.
- **`test_skills.py`:** düzenleme skill'i frame ekleyen tool'u anmıyor — artık `add_frame` aranır
  (`add_frames`'i de kapsar). İki test `ADD_FRAME_SCENE` ve `ADD_FRAME_CHARACTERS`'ı yeni adlarıyla
  içe aktarır.

## Bitti sayılır

- Agent'ın tool listesinde `add_frame(file, frames, before)` var; `add_scene` kodda, testlerde ve modele giden hiçbir metinde
  yok (yalnız eski adın artık tool olmadığını söyleyen testlerde).
- Frame eklemek bugünkü gibi çalışıyor: aynı cevap, aynı dosya.
- Dört suite yeşil. Frontend, `dist` ve queen-editor değişmemiş.
