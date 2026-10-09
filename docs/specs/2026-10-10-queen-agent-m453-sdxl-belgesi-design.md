# Madde 453 · SDXL belgesi — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
453 · **Dal:** `feat/queenagent-v10`, ana klasörde, **commit'lenmeden** — belge, tool açıklamaları ve
Start a scenario'nun bir cümlesi modele gider, kullanıcı onları VS Code'un Changes'inde okur ve
onayıyla commit'lenir *(kullanıcı, 30 Eylül — "commitleme yani ben onayı verince commitlenecek")* ·
**Kurallar:** [FOUNDATION](../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) · **Plan:**
[m453 planı](../plans/2026-10-10-queen-agent-m453-sdxl-belgesi-plan.md)

## Ne, neden

Kullanıcı, 9 Ekim: *"SDXL promptu nasıl yazılır diye her yere dağınık yazdık … SDXL promptu nasıl
yazılır diye bir doküman yazalım ve sabit ekleyelim akışa, sürekli cache'te olur ve AI her zaman
bilir, skill gibi ama hep olan"*.

**Bugün** `SDXL_PROMPT_RULES` altı tool'un — `add_character`, `update_character`, `add_outfit`,
`update_outfit`, `add_location`, `update_location` — açıklamasının sonuna ekli: her istekte aynı metnin
altı kopyası gidiyor. Görüntü modeline dair öbür kurallar yalnız skill'lerde: Start a scenario'nun
Step 5'i ve Step 10'u, Improve'un aynı kuralları tekrarlayan bağlamı ve Step 5'i. Ayna kuralı yalnız
Start a scenario'nun Step 3'ünde, ve istisnasız. Fotoğrafın boyutunu hiçbir metin söylemiyor; model
çekimi oranı bilmeden seçiyor.

**Olacak:** tek bir SDXL belgesi, her istekte system prompt'tan **hemen sonra**, kendi sabit
mesajında. Belge yalnız bugün metinlerde duran kuralları toplar *(kullanıcı, 9 Ekim — "SDXL için yeni
bir prompt rule ekleme, bizde olan kuralları kullan sadece, yapılı olarak tek bir yere yaz")*. Altı
tool'un açıklaması sadeleşir.

## Olacak

### 1 · Belge — `domain/prompt.py`'de `SDXL_DOCUMENT`

`SDXL_PROMPT_RULES`'un yerini alır; o ad modülden kalkar. Yeni ad, metnin artık bir tool'a ekli kurallar
değil, kendi mesajı olan bir belge olduğunu söyler. QueenAgent'ın modele söylediği her metin gibi
`prompt.py`'de durur (Madde 189), ve modülün öbür metinleri gibi parantez içinde satır satır yazılır.

Beş bölüm, beceri metinlerinin başlık-ve-madde düzeninde:

- **The image model** — fotoğrafın boyutu: Queen Editor'ün workflow'undaki genişlik 1024, yükseklik
  1536 (`queen-editor/assets/workflow_api.json`) — dikey, 2:3. **Modelin adı yok** *(kullanıcı, 10
  Ekim — "Model adı olmasın")*: Queen Editor'de model seçiliyor, Nova 3DCG XL ve DaSiWa Illustrious.
  Bugünkü kuralların ilk satırı da bu cümleye girer: model SDXL ailesinden, Danbooru'nun
  etiketleriyle eğitildi. Kuralların kimi yönettiği: her girdinin ve her frame'in action'ının
  etiketleri — bugün kurallar girdi yazan altı tool'da duruyor, ve action'ın tarifi *"Written by the
  same rules as the entries"* diyor; yeni bir kapsam değil, ikisinin birleşimi. Ve Step 5'in bağlamından:
  model zayıf, her etiketi çizer, karmaşık prompt görüntüyü bozar.
- **Writing a tag** — bugünkü `SDXL_PROMPT_RULES`'un etiketin nasıl yazıldığını söyleyen beş maddesi,
  kelimesi kelimesine.
- **What is left out** — bugünkü iki yasak (kalite etiketleri, *or*), kelimesi kelimesine; ve ayna:
  kullanıcı istemedikçe eklenmez — Start a scenario'nun *"Do not add a mirror to a place. A mirror
  breaks the image."* cümlesi ile kullanıcının 29 Eylül'deki sözü — *"aynayı çok kötü ekliyor, kalite
  düşüyor, user özellikle sorarsa eklensin"* — birlikte.
- **The prompt of a frame** — Start a scenario'nun Step 5 bağlamı, Improve'un tekrarladığı biçimde,
  kelimesi kelimesine: bir frame'in prompt'u tek fotoğrafı, sahnenin ilk anını anlatır; kamera açısının
  gizlediği etiketler ve açıya göre girdiler; en sık hata; Rule 1 – 6.
- **The negative list** — Step 10'un bağlamındaki beş madde, kelimesi kelimesine.

Son iki bölüm skill'lerde **de kalır** *(kullanıcı, 10 Ekim — "Evet, kopyası belgeye de girsin")*:
skill'ler model zayıf olduğu için kendi metinlerini taşır. Bu kurallardan biri değişirse üç metinde —
belge, Start a scenario, Improve — elle değişir.

Başlığı *SDXL prompt rules*: action'ın tarifi belgeyi bu adla anar (aşağıda, 3).

**Belgenin tam metni** (modele bu gider; `x` düz ASCII):

```text
SDXL prompt rules

The image model
- The photo of each frame is made by an SDXL-family image model trained on Danbooru's own tags, at 1024 x 1536: portrait, 2:3.
- The image model reads the tags of every entry and of every frame's action.
- The image model is weak and draws every tag in the prompt. A complex prompt breaks the image.

Writing a tag
- Write tags, never sentences. An article is not a tag either.
- Use a tag that the Danbooru vocabulary already has, rather than a description of the same thing. The model has seen a real tag many times, and has never seen a paraphrase of it.
- Write the tags in English, with spaces where the site writes underscores.
- Put one thing in each tag, split the way the vocabulary splits it. Do not join two tags into one longer phrase.
- When the vocabulary has no tag for it, write a few plain words in the same short form.

What is left out
- Never write quality tags. The code already puts them at the front of every prompt, so yours would be printed twice.
- Never write the word or inside a tag. The model draws one picture and cannot toss a coin between two choices, so pick one and write only that.
- Never add a mirror unless the user asks for one. A mirror breaks the image.

The prompt of a frame
- The prompt of a frame describes one photo: the first moment of the scene.
- Some tags are not visible from some camera angles. So a character, an outfit or a place can have more than one entry, for different camera angles.
- The most common mistake: a tag hidden by the camera angle goes onto another character. For example, the hair of a hidden head ends up on another character.
- Rule 1: If one of the character's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 2: If one of the outfit's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 3: If one of the place's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 4: The image model draws one photo. The whole prompt of the frame must describe only one photo. If the prompt describes more than one photo, remove the extra part.
- Rule 5: The whole prompt of the frame must be simple enough for the weak image model. If a part of the prompt is too hard, make the part simpler, and keep the same moment.
- Rule 6: If the scene is NSFW, name each visible body part directly, as in penis or vagina. Never use a euphemism.

The negative list
- The negative list is for the image model, not the video model. The negative list tells the image model what not to draw in the photo.
- The scenario has one negative list, for every frame. A tag in the negative list works on the whole photo, not on one character.
- The biggest problem is the features of the characters mixing, as in the hair of one character on another character. Focus the negative list on keeping the features of each character apart.
- Never write a feature of a character into the negative list. For example, dark skin in the negative list made a dark-skinned man come out white.
- To keep a feature of a character, write the opposite tags instead. For example, pale male and white man for a dark-skinned man.
```

### 2 · İstekteki yeri — `data/model_engine.py`'nin `_for_model`'ı

Bugün her istek `_for_model`'dan geçer ve o, konuşmanın önüne tek bir system mesajı koyar:
`system_prompt()`. 453'ten sonra önde iki sabit mesaj durur:

```text
1. system  system_prompt()      — QueenAgent'ın sayfası ve sahibin eki (değişmez)
2. system  SDXL_DOCUMENT        — yeni, her istekte aynı
3. …       konuşma               — kullanıcı, asistan ve tool mesajları
…          dosya adları, açık dosyalar, skill'in talimatı, son tur notu (stream_answer'ın _asked'ı)
```

- **System prompt'un içine değil**, ayrı bir mesaj *(kullanıcı — "system promptu karıştırmayalım")*:
  `system_prompt()` ve `SYSTEM_PROMPT` değişmez, `SYSTEM_PROMPT_SUFFIX`'in yeri de.
- **`_for_model`'da, `stream_answer`'da değil:** sabit baş tek yerde kurulur. `_asked` değişen kuyruğu
  kuruyor; belgeyi oraya koymak başı iki dosyaya bölerdi.
- **Kontrolün isteğine gitmez:** `stream_alone` `_for_model`'dan geçmiyor (Madde 445) — kontrolün
  işi tek kelime. `ports.py`'deki belge dizesi bunu söyler: sabit başın hiçbiri, ne system prompt ne
  belge.
- Bir sabit; fonksiyon değil. `SYSTEM_PROMPT_SUFFIX` istek kurulurken okunuyor çünkü sahibin metni
  (Madde 196); belgede öyle bir ek yok, ve her istekte bayt bayt aynı.

### 3 · Tool açıklamaları sadeleşir

`"\n" + SDXL_PROMPT_RULES` altı açıklamanın sonundan çıkar. Her açıklamanın kendi maddeleri yerinde
kalır; bir alana özgü kurallar da o alanın tarifinde kalır — karakterde sayı, solo yok, kıyafet yok
(`ADD_CHARACTER_TAGS`); kıyafette kişi yok (`ADD_OUTFIT_TAGS`); kıyafete giyenin adı verilmez
(`ADD_OUTFIT`, `UPDATE_OUTFIT`); mekânda kimse yok (`ADD_LOCATION_TAGS`).

Altı açıklamaya belgeyi anan bir cümle **eklenmez**: belge her istekte önde, ve altı kopya bir cümle
yine altı kopya olurdu.

Bir işaret değişir: `UPDATE_FRAME_ACTION`'ın *"Written by the same rules as the entries."* cümlesi,
girdilerin kuralları tool açıklamalarından çıkınca nereye baktığını söylemez olur. *"Written by the
SDXL prompt rules."* olur — belgenin başlığı. Start a scenario ve Improve'un Step 10 / Step 5'teki
*"Write the tags by the same rules as the entries."* cümlesine dokunulmaz *(kullanıcı — "model
zayıf")*; girdiler belgeyle yazıldığı için o cümle de belgeye varır.

**Önce ve sonra** (yalnız değişen kuyruk; üstündeki maddeler aynı):

| Metin | Bugün sonu | Sonra sonu |
|---|---|---|
| `ADD_CHARACTER` | `…use update_character.\n` + `\n` + kurallar | `…use update_character.` |
| `UPDATE_CHARACTER` | `…refuses a name that is not there.\n` + `\n` + kurallar | `…refuses a name that is not there.` |
| `ADD_OUTFIT` | `…refuses a name that is already there.\n` + `\n` + kurallar | `…refuses a name that is already there.` |
| `UPDATE_OUTFIT` | `…refuses a name that is not there.\n` + `\n` + kurallar | `…refuses a name that is not there.` |
| `ADD_LOCATION` | `…refuses a name that is already there.\n` + `\n` + kurallar | `…refuses a name that is already there.` |
| `UPDATE_LOCATION` | `…refuses a name that is not there.\n` + `\n` + kurallar | `…refuses a name that is not there.` |
| `UPDATE_FRAME_ACTION` | `Written by the same rules as the entries.` | `Written by the SDXL prompt rules.` |

### 4 · Start a scenario'nun Step 3'ü — tek skill değişikliği

Belgeyle aynı şeyi söylesin diye ayna cümlesi istisnayı alır *(kullanıcı, 10 Ekim, bu cümleyi seçti)*:

- Bugün: *"Do not add a mirror to a place. A mirror breaks the image."*
- Sonra: *"Do not add a mirror to a place unless the user asks for one. A mirror breaks the image."*

Altı kelime; Start a scenario 1800 kelimeden 1806'ya çıkar, tavanı 1830, tavan değişmez.

### 5 · Dokunulmayanlar

Start a scenario'nun geri kalanı, `IMPROVE`, `EDIT_PROMPTS` *(kullanıcı — "model zayıf")*;
`SYSTEM_PROMPT`, `SYSTEM_PROMPT_SUFFIX`, `LAST_ROUND` ve tool adları (454 ve 456'nın); `client.py`,
`stream_answer.py`, `tools.py`; frontend; queen-editor.

## Ne tutar

**Disk:** hiç — belge koddaki bir sabit. **Ağ:** her model turu yine tek istek, O(1); kontrolün isteği
aynı. Değişen yalnız her isteğin boyu.

**Token, istek başına.** Ölçülen karakter; token DeepSeek'in İngilizce için verdiği oranla, karakter
başına yaklaşık 0,3 token, tahmin. Sabit baş = system mesajı + belge + `tools` dizisinin JSON'u:

| | Karakter | ≈ Token |
|---|---|---|
| Bugün: system + tools (altı kopya kurallarla) | 23 758 | ≈ 7 130 |
| Sonra: system + belge + tools | 21 979 | ≈ 6 590 |
| Fark, istek başına | −1 779 | ≈ −530 |

Bir kural kopyası `tools` JSON'unda 885 karakter (≈ 265 token); altısı 5 310 karakter (≈ 1 590 token).
Action'ın tarifi 8 karakter kısalır. Belge 3 539 karakter, 697 kelime (≈ 1 060 token) — skill'lerden
kopyalanan iki bölüm onun üçte ikisi. System mesajı 2 869 karakterde aynı kalır. Bir tur 32 isteğe
kadar gider, yani tur başına ≈ 17 000 token'a kadar daha az.

**Bu token'lar çoğunlukla önbellekteydi.** Altı kopya her isteğin sabit önündeydi, ve bir turun ikinci
isteğinden itibaren önbellekten okunuyordu; tur başına ≈ 17 000'in büyüğü önbellekli token, tam fiyatlı
değil. Kazanç asıl iki şey: daha kısa bir bağlam, ve bir kuralın altı yerine tek kopyası. Gerçek sayıyı
aynı turun önce ve sonra damgası verir: `usage.sent` ve `usage.cached` (`client.py`'nin `_spent`'i).

**Cache.** DeepSeek önbelleği isteğin değişmeyen önünü tutar. Bu madde o önü bir kez değiştirir —
belge eklenir, altı açıklama kısalır —, ilk istekte önbellek o noktadan sonrasını kaçırır; ondan sonra
baş her istekte bayt bayt aynıdır ve önbellekte kalır. Belge sistem mesajının hemen arkasında, değişen
her şeyin önünde durduğu için önbelleğin önüne katılır.

## Sınırlar

- **Yeni kural yok.** Belgenin her maddesi bugün bir metinde duruyor: yedisi `SDXL_PROMPT_RULES`'ta,
  kelimesi kelimesine; ayna Start a scenario'nun Step 3'ünde ve kullanıcının 29 Eylül sözünde;
  zayıf model, tek fotoğraf, kamera açısı ve Rule 1 – 6 Step 5'te ve Improve'da; negatif liste
  maddeleri Step 10'da ve Improve'un Step 5'inde, hepsi kelimesi kelimesine. Yeni olan yalnız iki
  cümle parçası: boyut (Queen Editor'ün workflow'undan) ve kapsam satırı (*"reads the tags of every
  entry and of every frame's action"* — bugün kuralların durduğu altı tool ile action'ın işaretinin
  birleşimi).
- Modelin başka özelliği (adı, LoRA, örnekleyici) yazılmaz.
- Belge yalnız `stream`'in isteklerine gider; kontrolün isteğine gitmez.

## Değişen dosyalar

- `queen-agent/backend/features/workspace/domain/prompt.py` — `SDXL_DOCUMENT` (`SDXL_PROMPT_RULES`'un
  yerine), altı açıklama, `UPDATE_FRAME_ACTION`, Start a scenario'nun Step 3 ayna cümlesi, yorumlar.
- `queen-agent/backend/features/workspace/data/model_engine.py` — `_for_model` belgeyi ikinci mesaj
  olarak koyar.
- `queen-agent/backend/features/workspace/domain/ports.py` — `stream_alone`'un belge dizesi.
- Testler: `test_model_engine.py`, `test_tools.py`, `test_prompt.py`, `test_skills.py`.

## Testler

Sözcükleri kullanıcının yeniden yazabileceği cümleler sabitlenmez; testler anahtar kelimelere bakar.

**Engine (`test_model_engine.py`):** belge her istekte system mesajının hemen arkasında, kendi system
mesajında; iki farklı konuşmanın istekleri aynı iki mesajla başlar; sahibin eki belgeye değmez ve
belgeyi system mesajına katmaz; roller `system, system, user, assistant`. Kontrolün isteği (zaten
birebir iki mesaj) değişmez.

**Prompt modülü (`test_prompt.py`):** hiçbir tool'un açıklamasında ve hiçbir parametre tarifinde
belgenin hiçbir maddesi yok — tool tariflerini dolaşan `_descriptions_in` yardımcısıyla; dolu olması
gereken metinlerde `SDXL_DOCUMENT`. `SDXL_PROMPT_RULES`'un bir yerde yeniden yazılmadığını bugünkü
kaynak testi tutar.

**Tool'lar (`test_tools.py`):** belge 1024 ve 1536'yı söylüyor, model adı söylemiyor; aynayı ve
kullanıcının istemesini anıyor; action'ın tarifi belgenin ilk satırını içeriyor. Kuralların bugünkü
testleri (Danbooru, alt çizgi, etiket başına bir şey, kalite, *or*, cümle değil etiket) belgeye bakar;
bir alana özgü kuralların belgede olmadığını söyleyen test o kuralların kendisine bakar (solo, sayı,
kıyafetin adı, mekânda kimse), çünkü belge artık *outfit* kelimesini taşıyor. Alanların kendi kuralları
yerinde.

**Skill'ler (`test_skills.py`):** hiçbir skill belgenin tamamını taşımıyor; Step 3 aynayı ve
kullanıcının istemesini anıyor; kelime tavanları aynı.

## Bitti sayılır

- Testler yeşil, dört suite yeşil. Frontend ve queen-editor değişmemiş.
- Her istekte system prompt'tan hemen sonra SDXL belgesi gidiyor; system prompt'un kendisi değişmemiş.
  Belgede fotoğrafın 1024 × 1536 dikey boyutu yazıyor, model adı yazmıyor. `SDXL_PROMPT_RULES` hiçbir
  tool'un açıklamasında yok; tool'ların kendi kuralları yerinde; Start a scenario'da yalnız ayna
  cümlesi değişmiş, Improve aynı.
- Kullanıcı metni Changes'te okuyup onaylıyor; commit ondan sonra.
