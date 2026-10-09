# Madde 456 · Karakter, kıyafet ve mekânda add ile update tek bir `set` olur — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
456 · **Dal:** `feat/queenagent-v10`, ana klasörde, **commit'lenmeden** — tool'ların adları, tarifleri ve
cevapları modele gider; 10 Ekim'den beri bu koşuda metni Claude okuyup doğrular ve commit'ler
*(kullanıcı — "kendin verify et promptları ve sonraki aşamaya geç")* · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Plan:** [m456 planı](../plans/2026-10-10-queen-agent-m456-set-plan.md)

## Ne, neden

Kullanıcı, 9 Ekim: *"direkt add ve update ayırmak yerine tek bir set mi yapsak basitleştirmek için ne
dersin, set ve remove kalır?"*; Claude'un sorusuna *"set/remove da yapılsın"*.

**Bugün** her map için üç tool var: `add_X` var olan adı, `update_X` olmayan adı reddediyor, ikisi de
tag'lerin bütününü yazıyor; `remove_X` siliyor. Üç map, dokuz tool; bütün liste 17.

**Olacak:** `set_character`, `set_outfit`, `set_location` — ad yoksa açar, varsa değiştirir, yeni adla
yeniden adlandırır ve ad bütün frame'lerde değişir — ve bugünkü `remove_X`. Liste 17'den 14'e iner.

**Üstüne yazma görünür:** var olan bir ada `set` denince cevap onu değiştirdiğini söyler, eski metni
tırnak içinde verir ve o adı anan frame'leri sayar. Yeni açtığında, ondan önce bilinen adları sayar —
model yanlışlıkla bir yazım farkıyla ikinci bir giriş açtıysa, yanındakini orada görür.

Tasarımı reviewer çizdi, ana agent tartışıp onayladı; bu belge onu yazıya döker.

## Olacak

### 1 · Şema — `domain/tools.py`

Üç tool da aynı dört alanı alır:

| Alan | Zorunlu | Tarif |
|---|---|---|
| `file` | evet | `THE_SCENARIOS_FILE` |
| `name` | evet | `SET_X_NAME` |
| `tags` | hayır | `SET_X_TAGS` |
| `new_name` | hayır | `AN_ENTRYS_NEW_NAME` |

Yeniden adlandırma `name` + `new_name`. `TOOL_SPECS` ve `run_tool` bugünkü gibi elle yazılı kalır:
tablo yok, adlardan parça ayıklama yok.

### 2 · Kurallar, bu sırayla — `_set_entry`

Önce `_opened`'ın dosya düzeyindeki retleri, bugünkü gibi: dosya yok, JSON değil, frames listesi yok.
Sonra:

1. `name` boş → ret, ad gerekli.
2. Map dolu ama dict değil — dolu bir liste ya da dize — → ret, dosyaya dokunulmaz. **Yeni**: bugünkü
   `_add_entry` böyle bir map'i sessizce `{}` ile değiştirip yazıyordu (tools.py:779-782) —
   kullanıcının elle yazdığı bir şeyi silmek, 1. ilke. Map hiç yoksa, `null` ya da boşsa ret değil:
   içinde elle yazılmış bir şey yok, ilk giriş onu açar *(reviewer, 10 Ekim — tasarım `null`'ı da
   reddediyordu; düzeltildi)*.
3. `new_name == name` → yeniden adlandırma yok sayılır — ad olsun olmasın, her şeyden önce: yeni giriş
   açarken iki alanı da dolduran zayıf bir model yine ekler *(reviewer, 10 Ekim)*.
4. `name` yok, `new_name` var → `_unknown`'ın cümlesiyle ret. `new_name` adıyla giriş **açılmaz**:
   olmayan bir şeyi yeniden adlandırmak isteyen model yanlış adı yazmıştır.
5. `name` yok, `tags` yok ya da boş → ret, yeni giriş tag ister.
6. `name` yok, `tags` var → eklenir.
7. `name` var ve `tags` bugünkü metne eşit → tag'ler verilmemiş sayılır: yazılmaz, *"Changed"*
   denmez.
8. `name` var ve değişecek bir şey kalmadı → ret, hiçbir şey değişmezdi.
9. `new_name` başka bir girişin adı → ret, hiçbir şey yazılmaz.
10. `tags` verildi → metin değişir. Boş dize izinli ve metni siler, bugünkü update'teki gibi.
11. `new_name` verildi → giriş yeniden adlandırılır; frame'ler bugünkü yardımcılarla izler
    (`_renamed_in_frames`, `_outfit_renamed`), değişmeden.

"Verildi": `tags` için anahtar var ve `null` değil — boş dize bir değerdir. `name` ve `new_name`
kırpılarak okunur, bugünkü gibi.

### 3 · Cevaplar

`which` map'in adı: `characters`, `outfits`, `locations`. Kart = `ToolResult.outcome`.

| Durum | Cevap | Kart |
|---|---|---|
| eklendi | `Added Aylin to characters as a new character; known before it: aylin, deniz.` — önce hiçbiri yoksa `known before it: nothing.` | `Added` |
| değişti | `Changed aylin in characters; frames naming it: 1, 2, 4. Its text was "1girl, long teal hair".` — hiçbir frame anmıyorsa `frames naming it: none.` | `Changed` |
| yeniden adlandırıldı | `Renamed aylin to ayla in characters; 2 frames followed.` | `Renamed` |
| yeniden adlandırıldı ve metin değişti | `Renamed aylin to ayla in characters and changed its text; 2 frames followed. Its text was "1girl, long teal hair".` | `Renamed` |
| ad yok | `A character needs a name.` / `An outfit needs a name.` / `A location needs a name.` | `Refused` |
| map dict değil | `characters in bar-scene.json is not a map of names to tags, so nothing was written.` | `Refused` |
| olmayan ad + `new_name` | `_unknown`'ın cümlesi: `aylin is not in characters; known: deniz.` | `Not there` |
| olmayan ad, tag yok | `A new character needs tags.` | `Refused` |
| değişecek bir şey yok | `Nothing would change about aylin.` | `Nothing to change` |
| yeni ad dolu | `There is already a character called ayla.` | `Already there` |

Bilinen adlar `_unknown`'daki gibi sıralı. Frame numaraları bire göre, modelin saydığı gibi
(`_frames_naming`).

### 4 · Metinler — `domain/prompt.py`

Ana agent'ın verdiği metinler, harfi harfine:

- **"What more than one tool says" bölümüne** `SETTING_AN_ENTRY` — üç `SET_X`'in ortak iki maddesi.
- `AN_ENTRYS_NEW_TAGS` yeni metniyle; docstring'i *"every set_ tool's"* der.
- `AN_ENTRYS_NEW_NAME` yeni metniyle.
- `SET_CHARACTER`, `SET_CHARACTER_NAME`, `SET_CHARACTER_TAGS`, `SET_OUTFIT`, `SET_OUTFIT_NAME`,
  `SET_OUTFIT_TAGS`, `SET_LOCATION`, `SET_LOCATION_NAME`, `SET_LOCATION_TAGS` — her `_TAGS` kendi
  map'inin kategorileriyle başlar ve `AN_ENTRYS_NEW_TAGS` ile biter.
- On sekiz `ADD_X*` / `UPDATE_X*` sabiti silinir. `REMOVE_X` ve `REMOVE_X_NAME` aynı kalır.
- `EDIT_FILE`'ın son cümlesi silinir: *"Renaming an entry through all the frames that name it is the
  usual case."* Madde 171'den beri senaryo `edit_file`'a kapalı; cümle artık yanlış tool'u gösterirdi.
- Yorumlar: SDXL bölümündeki *"the add_ and update_ and remove_ tools build it"* →
  *"the set_, add_, update_ and remove_ tools build it"*; ortak bölümün *"Nine tools ask for a
  scenario's file"* → *"Six tools"*.

### 5 · Kapı cümlesi — `_shut`

Bugün: *"{wanted} is a structure file; it is not written or changed as text. Use start_scenario to open
one, and the add_, update_ and remove_ tools to change it."*

Sonra: *"{wanted} is a structure file; it is not written or changed as text. Use start_scenario to open
one, and the set_, add_, update_ and remove_ tools to change it."* — `add_` ve `update_` frame'ler için
kalır.

### 6 · Kod — `domain/tools.py`

- Yeni `_set_entry(file_store, project_id, args, which)`. `_opened`, `_saved`, `_article`, `_unknown`,
  `_frames_naming`, `_renamed_in_frames` ve `_outfit_renamed`'i değiştirmeden kullanır.
- `_add_entry`, `_update_entry`, altı spec, altı `run_tool` dalı ve *"already called that"* reddi
  silinir.
- `_remove_entry`'nin docstring'i *"Not a set with the value left out"* der.
- **`_remove_entry` aynı reddi alır** *(ana agent, 10 Ekim — onaylı)*: dolu bir liste ya da dize map'te
  `key in entries` bir dizede alt dize arıyor, ve `del` `TypeError` atıp turu düşürüyordu. Cümle
  `_set_entry`'ninkiyle aynı, ikisi de `_not_a_map`'ten.
- `_frames_naming`'in docstring'i bugün doğru olanı söyler: mekân frame'in kendi alanından okunur.

### 7 · Modlar — `domain/modes.py`

Edit'in listesinden `add_X` ve `update_X` çıkar, `set_X` girer. Ask ve Plan bunların hiçbirini
listelemiyor; `set` ikisinde de sorar, bugünkü add / update gibi.

### 8 · Ekran ve kayıtlı sohbetler

Frontend'de tool adı geçmiyor; adım kartı adı olduğu gibi yazar: `⏺ set_character(bar-scene.json)` ·
*Changed*. `dist` yeniden kurulmaz.

**Göç yok.** Eski sohbetteki `add_X` / `update_X` kartları o turda çalışanı göstermeye devam eder.
Model eski adı bir metinden alıp çağırırsa `run_tool`'un genel cevabını alır — *"There is no tool called
add_character."* —, `needs_permission` bilinmeyen tool'u sormaz, dosyaya dokunulmaz; bedel en çok bir
tur. Diskteki senaryo dosyaları değişmez: tool adı dosyada yazmıyor.

## Ne tutar

**Disk, bir `set` çağrısı başına:** Drive'da senaryonun bir okunuşu, sonra iki yazma, O(1) — projedeki
dosya, sohbet ve frame sayısından bağımsız. Okuma `file_store.read`: dosyanın satırı bellekteki
`projects.json`'dan, metni diskten tek okuma. Yazma `_saved` → `file_store.write`: önce senaryo dosyası
(`Store.write_text` geçici dosyaya yazar, `os.replace` ile değiştirir; çökme ya eski dosyayı ya
yenisini bırakır), sonra dosyanın satırı (`put_file`) — `projects.json`'u kuyruktaki tek yazıcı biraz
sonra yazar, içerik önce. Frame'leri dolaşmak bellekte, O(frame).

- **Ret:** bir okuma, yazma yok. Map dict değilken de — dosya bayt bayt aynı kalır.
- **Aynı tag'ler:** bir okuma, yazma yok (kural 7–8).
- **Bugünle fark:** yok — bugünkü add / update de bir okuma, aynı iki yazma. Yeni ret yolu (kural 2)
  bir yazmayı kaldırır.

Bir test bunu sabitler: `file_store`'u sayan bir sarmalayıcıyla başarılı `set` `["read", "write"]`,
ret `["read"]`, aynı tag'ler `["read"]`.

**Aynı anda iki istek:** bugünkü map tool'larıyla aynı — oku, değiştir, yaz; ikisi aynı senaryoya aynı
anda yazarsa sonuncusu kalır. Bir sohbetin turu tool'ları sırayla çalıştırır; bu madde yeni bir yarış
açmıyor. **Yol:** dosya adı `safe_name`'den geçer, bugünkü gibi; giriş adı yalnız JSON'un içinde anahtar
olur, yola dönmez.

**Ağ:** her model turu yine tek istek. **Token, istek başına:** sabit baş (system + SDXL belgesi +
`tools` JSON'u) kısalır. Ölçülen karakter (`tmp/m456_size.py`); token, 453'teki gibi karakter başına
≈ 0,3, tahmin:

| | `tools` JSON'u | Sabit baş | ≈ Token |
|---|---|---|---|
| Bugün: 17 tool | 15 571 | 21 979 | ≈ 6 590 |
| Sonra: 14 tool | 13 479 | 19 887 | ≈ 5 970 |
| Fark, istek başına | −2 092 | −2 092 | ≈ −630 |

System mesajı (2 869) ve belge (3 539) aynı. Bir tur 32 isteğe kadar gider; tur başına ≈ 20 000 token'a
kadar daha az, çoğu önbellekli.

**Önbellek:** `tools` dizisi her isteğin sabit önünde. Bir kez değişir; ilk istekte önbellek o noktadan
sonrasını kaçırır, sonra yine bayt bayt aynı.

## Sınırlar

- **Yalnız üç map.** Frame'in `add_frame`, `update_frame`, `remove_frame`'i ve `build_prompts`
  dokunulmaz; `_shut` onları hâlâ `add_` ve `update_` diye anar.
- **`remove_X` aynı:** tarifi, cevabı, ret cümlesi.
- **Skill metinleri** tool'u adıyla anmıyor; dokunulmaz.
- **Diskteki senaryolar** değişmez ve aynı açılıyor; prompt'ları aynı kuruluyor — giriş yazılış şekli
  değişmedi.
- **Göç yok:** kayıtlı sohbetler çevrilmez.
- Frontend, `dist` ve queen-editor değişmez.

## Değişen dosyalar

- `queen-agent/backend/features/workspace/domain/tools.py` — üç spec, üç `run_tool` dalı,
  `_set_entry`; `_add_entry` ve `_update_entry` gider; `_shut`'ın cümlesi; `_remove_entry`'nin docstring'i.
- `queen-agent/backend/features/workspace/domain/prompt.py` — `SETTING_AN_ENTRY`, iki ortak kuyruk, dokuz
  `SET_X*`; on sekiz `ADD_X*` / `UPDATE_X*` gider; `EDIT_FILE`'ın son cümlesi; iki yorum.
- `queen-agent/backend/features/workspace/domain/modes.py` — Edit'in listesi.
- Testler: `test_tools.py`, `test_modes.py`.

## Testler

`test_tools.py`'nin giriş bölümü yeniden yazılır:

- tam *Added* cümlesi, *known before it* adlarıyla; hiçbiri yokken *nothing*;
- *Changed*, frame numaraları ve eski metinle; hiçbir frame anmıyorken *none*;
- yeniden adlandırma frame'leri götürür (iki şekil: map ve eski düz liste; kıyafetin kısa biçimi);
  tag'lerle birlikte eski metni tırnaklar;
- olmayan ada `new_name`: ret, dosya bayt bayt aynı;
- olmayan ad, tag yok: ret;
- aynı tag'ler: *Nothing would change*, yazma yok;
- `new_name == name` ve tag'ler: metin değişir; olmayan bir adda da ekler;
- yeni ad dolu: ret, dosya aynı;
- dolu liste ya da dize map: `set` de `remove` da reddeder, dosya bayt bayt aynı; `null` map ilk girişi
  alır;
- maliyet testi, sayan sarmalayıcıyla;
- dosya düzeyindeki retler `(set_X, remove_X)` üzerinden;
- şema: özellikler `{file, name, tags, new_name}`, zorunlular `{file, name}`; `remove_X` `{file, name}`;
- `SET_X*` sabitlerinin metin testleri (sayı, solo, kıyafet, kategoriler, kıyafetin adı, mekânda kimse
  yok, anatomi yok); her `set_X`'in açıklaması `SETTING_AN_ENTRY` ile, tag'leri `AN_ENTRYS_NEW_TAGS`
  ile biter; bir test o iki metnin *"the answer gives the text it had"* ve *"a new entry needs them"*
  dediğini tutar;
- 454'ün yolundan: eski altı ad ne `json.dumps(TOOL_SPECS)`'te ne skill metinlerinde geçiyor.

Tool listesinin eşitlik testi 14 adı sayar — eski altı ad orada yok. `test_modes.py`'nin `WRITES`'ı
`set_X`'i anar; 454'ün `test_no_mode_lists_a_tool_that_is_gone` testi eski adların modlarda kalmadığını
zaten tutar, ad başına mod testi eklenmez.

## Bitti sayılır

- Agent'ın tool listesinde karakter, kıyafet, mekân için yalnız `set_X` ve `remove_X` var; 14 tool.
- Var olan bir ada `set` denince cevap neyi değiştirdiğini ve eski metni söylüyor.
- Bugünkü senaryo dosyaları açılıyor ve prompt'ları aynı kuruluyor.
- Dört suite yeşil. Frontend, `dist` ve queen-editor değişmemiş.
