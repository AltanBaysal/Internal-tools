# Madde 495 · Altı model metni `prompt.py`'den `.md` dosyalarına — tasarım

**Tarih:** 23 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-20-queen-agent-v11-roadmap.md),
495 · v11-7 · **Dal:** `feat/queenagent-v11`, ana klasörde · **Koşu planı:**
[495 planı](../plans/2026-10-23-495-skill-md.md) · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

**Durak 1 — kullanıcının onayı (23 Ekim):** *"düzelt, önerilerin kabul edildi"*. Kabul edilenler:
Seçenek A; klasör `queen-agent/backend/features/workspace/skills/`, dosyalar seçicinin adlarıyla
(`sdxl-start-scenario.md`, `sdxl-edit.md`, `krea-start-scenario.md`, `krea-edit.md`) ve iki belge;
CLAUDE.md satırı taslaktaki gibi; CODE-STANDARD'ın iki cümlesi aşağıdaki gibi. Ve *"düzelt"*: belgeler
cümlesi Separation of concerns'te *"… read off the entries and never written."*in arkasına taşınır,
ki arkasındaki *"it"* yine `projects.json`'ı göstersin (reviewer'ın bulduğu, var olan bir kusur).

## Ne, neden

Kullanıcı, 23 Ekim: *"bu skilleri ve seçilebilen skilleri ayrı bir md mi yapsak ben okurdum direkt ...
rahat olurdu repoda oradan okusa"*; *"şimdilik ilk 6 dosyayı taşıyalım"*.

**Bugün** dört skill'in ve iki belgenin metni `queen-agent/backend/features/workspace/domain/prompt.py`'de,
Python string'i olarak, satır satır tırnaklı parçalar hâlinde duruyor: okumak için kodu okumak gerekiyor.

**Olacak:** altı metin repoda altı `.md` dosyasında durur, kullanıcı onları düz metin olarak açıp okur;
`prompt.py` onları sunucu açılırken bir kez okur ve bugünkü adlarıyla verir. Modele giden metin bayt bayt
aynı kalır; ekran, `dist`, seçicinin id'leri, araçlar, `GUIDES`'ın adları değişmez.

**Taşınan, tam altı metin:** `START_A_SCENARIO`, `EDIT_PROMPTS`, `KREA_START_SCENARIO`, `KREA_EDIT`,
`SDXL_GUIDE`, `KREA_GUIDE`.
**Kodda kalan:** `SYSTEM_PROMPT` ve `system_prompt()` (her istekte kuruluyor, suffix ekleniyor —
kullanıcı: *"dosya yokken bir kısmı farklı oluyor, suffix ekleniyor vs"*), `CHECK`, araç açıklamaları,
tek satırlık metinler (`LAST_ROUND`, `FILES_HELD`, …).

## Klasör ve dosya adları

**Klasör:** `queen-agent/backend/features/workspace/skills/` — koşu planının önerisi. Kullanıcı altısına
da *skill* diyor (*"2 skill olacak işte sdxl ve krea prompt yazımı"*, 22 Ekim). Klasör `domain/`'in
içinde değil, yanında: içinde kod yok, ve `domain/skills.py`'nin yanında bir `domain/skills/` klasörü
iki ayrı şeye aynı adı verirdi. `__init__.py` yok; hiçbir şey onu modül olarak içe aktarmaz.

**Dosyalar — öneri, seçicinin gösterdiği adlarla:**

| Metin | Seçicide | Dosya (öneri) | Plandaki seçenek (id'ler) |
|---|---|---|---|
| `START_A_SCENARIO` | SDXL start scenario | `sdxl-start-scenario.md` | `start-a-scenario.md` |
| `EDIT_PROMPTS` | SDXL edit | `sdxl-edit.md` | `edit-prompts.md` |
| `KREA_START_SCENARIO` | Krea start scenario | `krea-start-scenario.md` | `krea-start-scenario.md` |
| `KREA_EDIT` | Krea edit | `krea-edit.md` | `krea-edit.md` |
| `SDXL_GUIDE` | — (dosya panelinde) | `sdxl-prompt-writing.md` | aynı |
| `KREA_GUIDE` | — (dosya panelinde) | `krea-prompt-writing.md` | aynı |

Neden seçicinin adları: dosyayı açan kullanıcı, seçicide gördüğü adı bulur; dört ad simetrik olur. SDXL'in
iki id'si (`start-a-scenario`, `edit-prompts`) eski kayıtlar ve tarayıcının hatırladığı seçici için
değişmeden kalıyor (`skills.py`'nin docstring'i), ama dosya adının onlara eşit olması gerekmiyor: hangi
dosyanın hangi metin olduğunu `prompt.py`'de tek satır söylüyor. Plandaki seçenek de çalışır; fark yalnız
okunuşta. **Durak 1'de kullanıcıya sorulur.**

İki belgenin adı değişmez: dosya panelinde bu adlarla görünüyorlar ve skill'lerin ilk satırı onları bu
adla çağırıyor.

## Karar 1 — okuyan kod nerede durur

**Engel olan kurallar ve sebepleri:**

- `CODE-STANDARD.md`, *domain/*: *"Imports nothing external (no `flask`, no `requests`, no file-path or
  schema knowledge)."* Sebebi aynı dosyada ve FOUNDATION Decision 4'te: kurallar ağsız ve gerçek store'suz
  test edilir; dosya şemalarını yalnız `data/` bilir. Kural kullanıcının verisini, store'u hedefliyor.
- `prompt.py`'nin docstring'i: *"This module imports nothing, and will not. Everything else imports it,
  so anything it reached for would be a cycle waiting for its first line."* Sebebi döngü.
- 492'nin yorumu (`prompt.py`, belgeler bloğu): *"files in the repo would need a port the domain does not
  have"*.

**Metni kim kullanıyor:** dördü domain'de doğrudan — `skills.INSTRUCTIONS` → `run_turn` (`instruction_for`);
`prompt.GUIDES` → `tools._read_only` ve `delete_file` (adlarıyla, reddetmek için), ve `main.py` üzerinden
`FileFileStore`'a (metniyle).

### Seçenek A — `prompt.py` kendi altı metnini okur (öneri)

`prompt.py`'ye küçük bir okuyucu girer; dört skill sabiti ve `GUIDES` aynı adla kalır, değerleri
dosyadan gelir:

```python
from pathlib import Path

_SKILLS = Path(__file__).parent.parent / "skills"


def _read(name):
    return (_SKILLS / name).read_text(encoding="utf-8").rstrip("\n")


START_A_SCENARIO = _read("sdxl-start-scenario.md")
...
GUIDES = {name: _read(name) for name in ("sdxl-prompt-writing.md", "krea-prompt-writing.md")}
```

- **Dört skill sabiti adıyla kalır; `SDXL_GUIDE` ve `KREA_GUIDE` kalkar.** Onları `GUIDES`'tan başka
  hiçbir şey okumuyor; `GUIDES` her belgeyi kendi dosya adıyla okuyunca ad bir kez yazılır, ayrı bir
  sabit aynı adı ikinci kez taşırdı.

- **Değişen kod yalnız `prompt.py`.** `skills.py`, `tools.py`, `delete_file.py`, `run_turn.py`,
  `main.py`, `FileFileStore`, `ports.py` olduğu gibi kalır: hepsi bugünkü adları okuyor (`SDXL_GUIDE` ile
  `KREA_GUIDE`'ı `GUIDES`'tan başka okuyan yok). Testlerde değişen, aşağıda *Testler*'de.
- **Kuralların sebebi tutuyor:** altı dosya kullanıcının verisi değil, store'un değil; kodun kendi metni,
  `.md` olarak duruyor. Testler sahte bir port olmadan, ağsız okur. `pathlib` standart kütüphane:
  hiçbir şeyi geri içe aktarmaz, döngü açmaz.
- **Ama kuralın sözü değişir:** domain artık bir dosya yolu biliyor. Bu yüzden `CODE-STANDARD.md`'nin
  domain cümlesine adıyla bir istisna yazılır (aşağıda), ve `prompt.py`'nin docstring'i ile 492'nin
  yorumu doğru hâle getirilir. **Kural değişikliği: Durak 1'de kullanıcıya gösterilir.**

### Seçenek B — okuyucu `data/`'da, metin domain'e verilir

Domain kuralı yazıldığı gibi kalır. Okuyucu `data/` altında yeni bir modül (`data/model_texts.py`)
olur; domain yalnız adları tutar (skill id'leri, belge adları); metinleri `main.py` dağıtır.

- Belgeler için kolay: `FileFileStore` metni bugün de `main.py`'den alıyor; `tools._read_only` ile
  `delete_file` yalnız adlara bakıyor.
- **Skill'ler için var olan kod yeniden yapılandırılır:** `run_turn` metni bugün `instruction_for`'dan
  kendisi alıyor; bunun yerine metin haritasını parametre olarak alır, ve `make_workspace_bp` →
  `routes` → `LiveTurns`'ün turu başlatan yolu onu taşır. `skills.instruction_for` ya kalkar ya bir harita
  alır. `prompt.GUIDES` metinsiz kalır.
- Değişen testler: `test_skills.py`, `test_prompt.py`, `test_run_turn.py`, `test_chats_api.py`,
  `test_tools.py`, `test_model_engine.py`, `test_files_api.py`, `test_composition.py` — metni ya da
  `instruction_for`'u bugün doğrudan içe aktarıyorlar.
- Maliyet aynı (açılışta bir kez); kazanç yalnız kuralın sözünün değişmemesi.

**Öneri: A.** Aynı işi bir dosyanın değişmesiyle yapıyor; B'nin fazladan parçaları — bir modül, bir
parametre zinciri, sekiz test dosyasının değişmesi — yalnız bir kuralın sözünü korumak için, sebebini
değil. B var olan kodu yeniden yapılandırdığı için, seçilirse kod yazılmadan önce açıkça onay ister.

**A'nın içinde, okuyucunun yeri:** `prompt.py`'nin kendisi, ayrı bir modül değil. Madde 189'dan beri
*"every text the model is told"* orada adlanıyor; altısı artık orada yazılmıyor ama orada adlanmaya ve
gerekçelendirilmeye devam ediyor. Ayrı bir modül, dört satırlık iş için bir dosya daha olurdu.

## Okuyucunun dört ayrıntısı

- **`encoding="utf-8"`:** Windows'un varsayılanı (cp1254) değil. Bugün metinlerin hepsi ASCII; açıkça
  yazılınca yarın bir `ü` iki makinede aynı okunur. `store.py` da `utf-8` ile okuyor.
- **CRLF:** `read_text` metin kipinde açar (universal newlines): `\r\n` `\n` olur. Bu makinede
  `core.autocrlf=true` ve repoda `.gitattributes` yok — commit'ten sonraki her checkout dosyaları CRLF
  yazar (`git ls-files --eol`: `prompt.py` bugün `i/lf w/crlf`). Colab'da (Linux) LF. İkisinde de metin
  aynı. `.gitattributes` eklenmez: okuma ikisini de aynı yapıyor, fazladan bir parça olurdu.
- **Dosya sonu:** sabitler `\n` ile bitmiyor. Dosyalar, her metin dosyası gibi, bir satır sonuyla biter
  (editör ve git öyle ister; olmazsa git diff'i *"No newline at end of file"* der). Okuyucu sondaki satır
  sonlarını atar (`rstrip("\n")`): metin, bugünkü gibi son kelimesinde biter. Başka hiçbir şeye dokunmaz.
- **BOM yok sayılmaz:** `utf-8`, `utf-8-sig` değil. Metinlerin hiçbiri BOM'la başlamıyor; biri BOM'la
  kaydedilirse aşağıdaki kalıcı test kırmızı yanar, sessizce düzeltilmez.

## Karar 2 — why-yorumları nereye gider

**`prompt.py`'de kalırlar**, her birinin bugün yanında durduğu sabitin — artık okuyan satırın — üstünde.
`.md`'ye hiçbir yorum girmez: dosyanın her baytı modele gider; bir HTML yorumu (`<!-- -->`) da gider.

Yerinde kalan bloklar, kelimesi kelimesine:
- Skill bloğu (bugün satır 233 – 255): ruh hâli, Madde 492'nin dört metni, Madde 94, ilk satır, Madde 123'ün
  kelime sınırı.
- Krea iki metninin bloğu (487 – 503): Madde 492, 493, notes dosyasının adı.
- Belgeler bloğu (603 – 637): Madde 492, 453, 200, 493; kullanıcının alıntılanmış sözleri.

**Yalnız yanlış kalacak cümleler değişir** (CLAUDE.md: *"A comment says why, and what is true now"*):
- Belgeler bloğu, *"Here, as text, rather than in the user's Drive or in files of the repo: a copy in
  every project would drift and could be edited, and each read of one would be a round trip; files in the
  repo would need a port the domain does not have."* → Drive'a karşı gerekçe kalır; *"files in the repo
  would need a port"* yerine 495'in gerekçesi: repoda, `skills/`'te, kullanıcı okusun diye (23 Ekim
  alıntısı); açılışta bir kez okunur, kodun kendi metni olduğu için port gerekmez.
- Modül docstring'i: *"This module imports nothing, and will not."* → *"imports nothing of this app's"*,
  ve döngü gerekçesi aynen; `pathlib`'in standart kütüphane olduğu ve döngü açmadığı bir cümle. Bir
  paragraf eklenir: altı metin Madde 495'ten beri `../skills/`'te `.md` olarak yazılıyor, burada
  okunup adlanıyor. Madde 189'un *"read in one sitting"*i artık bu modül ve o klasör.
- `_read`'in kendi docstring'i: metin kipinin ve `rstrip`'in neden olduğu, iki satır (yukarıdaki
  ayrıntılardan).
- `skills.py` docstring'i, *"The texts themselves are in prompt.py since Madde 189"* → prompt.py'de
  adlanıyor, Madde 495'ten beri `skills/`'te yazılıyor.
- `file_file_store.py` docstring'i, *"text in the code, handed in by main.py"* → repodaki `skills/`'ten
  bir kez okunan metin, `main.py`'nin verdiği.
- `test_composition.py:74`, `test_the_file_store_is_handed_the_guides_and_the_moment_once`'ın
  docstring'i, *"The two prompt guides are text in the code"* → repodaki `skills/`'ten okunan metin.

**Hiçbir şey kaybolmaz:** silinen tek cümle 492'nin *"a port"* gerekçesi; yerine neden artık geçerli
olmadığı yazılır, geçmişi git'te. Reviewer üç bloğun her satırının yerinde olduğunu diff'te denetler.

## Karar 3 — bayt eşitliği nasıl kanıtlanır

**Tek seferlik kontrol, `tmp/m495-bytes.py`** (git'e girmez; Durak 2'den sonra silinir). Coder kurar,
reviewer okur, ana ajan 13. adımda kendisi yeniden çalıştırır.

1. **Eski değerler commit'ten:** `git show c1fdff97:queen-agent/backend/features/workspace/domain/prompt.py`
   (495 başlarken dalın ucu; adı sabit, ki kontrol commit'ten sonra da aynı şeyi karşılaştırsın).
   `ast.parse`, altı adın atamasını bulur, `ast.literal_eval` ile değerini alır — altısı da düz string
   birleştirmesi, f-string yok; kod çalıştırılmaz.
2. **Yeni değerler, modelin aldığı yoldan:** `prompt` modülünün dört skill sabiti,
   `skills.INSTRUCTIONS`'ın dört değeri, `prompt.GUIDES`'ın iki değeri (eski `SDXL_GUIDE`, `KREA_GUIDE`). Her biri eskisiyle `==`; ayrıca `.encode("utf-8")` eşitliği
   (aynı şey, açıkça). Eşit değilse ilk farklı karakterin yeri ve çevresi yazılır.
3. **Dosyanın kendisi:** her `.md`'nin ham baytları, `\r\n` → `\n` yapıldıktan sonra, `eski + "\n"`'nin
   UTF-8'i — dosyada fazladan ya da eksik bir şey olmadığını, okuyucunun neyi attığını görmek için.
   Dosyanın şu an LF mi CRLF mi olduğu yazılır.
4. **CRLF, varsayılmadan denenir:** her dosyanın CRLF kopyası `tmp/m495-crlf/`'e yazılır,
   `prompt._SKILLS` oraya çevrilir, `prompt._read(ad)` eskisine eşit mi bakılır. (`_read` klasörü her
   çağrıda modülün değişkeninden alıyor; bunun için parametre eklenmez.)
5. Çıktı: altı satır *eşit* ve çıkış kodu 0, ya da farkın kendisi ve 1.

**Kalıcı testler metnin içeriğine bakmaz** (gelecekte metin değişince kırılmasınlar diye), yalnız
okuyucunun sözleşmesine — aşağıda, *Testler*.

## CODE-STANDARD — değişecek iki cümle (Seçenek A ile; Durak 1'de gösterilir)

**1. Features, domain** (bugün satır 74 – 75):

> - **domain/** — pure rules, port definitions (`Protocol`), use cases. Imports nothing external (no
>   `flask`, no `requests`, no file-path or schema knowledge).

→

> - **domain/** — pure rules, port definitions (`Protocol`), use cases. Imports nothing external (no
>   `flask`, no `requests`, no file-path or schema knowledge). One exception, by name: `prompt.py` reads
>   six of the model's texts from the feature's `skills/` folder once, when it is imported (Madde 495).
>   They are the code's own text, kept as `.md` so the user can read them in the repo — not data and not
>   the store's — so no port stands between them, and a test reads them with no fake.

**2. Separation of concerns, belgeler** (bugün satır 46 – 48):

> The two prompt guides are the exception: they come from the code (`prompt.GUIDES`, Madde 492), listed
> after every project's own files and never written to disk.

→

> The two prompt guides are the exception: they come from the repo, not the store — the feature's
> `skills/` folder, read once into `prompt.GUIDES` (Madde 492, 495) — listed after every project's own
> files and never written.

Onaylı (Durak 1): bu cümle aynı paragrafta *"… and a file's chip are read off the entries and never
written."*in arkasına taşınır. Bugün *"projects.json is the one place a list is read from"*in hemen
arkasında durup sonraki *"To be that, it repeats …"*in *"it"*ini kendine çekiyor. Yeni yerinde
*"the exception"*, paragrafın *"the one exception"*ının yanında ikinci bir istisna gibi okunurdu
(reviewer); kullanıcının *"düzelt"*i doğru okunmasını istediği için cümle kuralı adlandırır:

> The two prompt guides are listed with no entry of their own: they come from the repo, not the store
> — the feature's `skills/` folder, read once into `prompt.GUIDES` (Madde 492, 495) — after every
> project's own files, and are never written.

## CLAUDE.md satırı — taslak, kullanıcı görmeden yazılmaz

*Commands*'ın altındaki *"Tests cover code. Documents are for people, … so none does (item 431)."*
paragrafının arkasına, aynı paragrafa:

> The exception is the `.md` files in `queen-agent/backend/features/workspace/skills/`: they are the
> model's input, read by the code, and tests read them as they read any constant (item 495).

## Ne değişir, dosya dosya (Seçenek A)

- **Yeni:** `queen-agent/backend/features/workspace/skills/` altında altı `.md` — içerik eski sabitin
  değeri, aynen, artı sonda bir `\n`. Write aracıyla yazılır (kullanıcının kuralı: dosya script'le değil,
  izlenebilen araçla); doğruluğunu Karar 3'ün kontrolü kanıtlar.
- **`domain/prompt.py`:** `from pathlib import Path`, `_SKILLS`, `_read`; dört skill sabiti `_read("…")`
  olur; `SDXL_GUIDE` ve `KREA_GUIDE` kalkar, `GUIDES` aynı adları ve metinleri her belgeyi adıyla okuyarak
  verir; docstring ve belgeler bloğundaki cümle (Karar 2).
- **`tests/test_composition.py`:** yalnız 74. satırdaki docstring cümlesi (Karar 2).
- **`domain/skills.py`:** yalnız docstring cümlesi.
- **`data/file_file_store.py`:** yalnız docstring cümlesi.
- **`tests/test_prompt.py`, `tests/test_retired_provider.py`, `tests/test_skills.py`:** aşağıda.
- **`queen-agent/CODE-STANDARD.md`:** iki cümle, onaylanırsa. **`CLAUDE.md`:** bir satır, onaylanırsa.
- **Roadmap:** 495'in satırı (eklendi), bitince ✅ ve *Durum 6/6*.
- Değişmeyen: `main.py`, `tools.py`, `delete_file.py`, `run_turn.py`, `ports.py`, ön yüz, `dist`.

## Testler

**Yeni, `test_prompt.py`'de (TDD: dosyalar yokken kırmızı):**
- **Her metin kendi dosyası:** `skills/` klasöründe tam altı `.md` var, başka dosya yok; her skill id'sinin
  `instruction_for(id)`'si ve her belgenin `GUIDES[ad]`'ı, kendi dosyasının metin kipinde okunup sondaki
  satır sonları atılmış hâline eşit. Adı-dosyayı bağlar; içeriğe bakmaz.
- **Okunan metnin biçimi:** altısında `\r` yok, `﻿` yok, metin baştan ve sondan boşluksuz
  (`text == text.strip()`). Bu test CRLF'yi güvenilir biçimde sınamaz: Write aracı LF yazar ve çalışma
  ağacı yeni bir checkout'a kadar LF kalır. **CRLF'yi sınayan, Karar 3'ün tek seferlik kontrolünün 4.
  adımıdır** (CRLF kopyadan `_read`).
- **Metin `prompt.py`'de yazılmıyor:** `ast` ile, dört skill adının (`START_A_SCENARIO`, `EDIT_PROMPTS`,
  `KREA_START_SCENARIO`, `KREA_EDIT`) atandığı değer bir string sabiti değil, bir çağrı. Madde 189'un
  *"bir metin iki yerde yazılmaz"* kuralı: biri metni `prompt.py`'ye geri yapıştırırsa dosyaya eşit
  olduğu için ilk test geçerdi, bu geçmez. Belgeler için: eski yer korumasına
  (`test_no_text_is_still_written_down_where_it_used_to_live`) `("prompt", "SDXL_GUIDE")` ve
  `("prompt", "KREA_GUIDE")` eklenir.

**Uyarlanan:**
- `test_retired_provider.py` bugün `.md`'leri belge sayıp atlıyor (*"Documents: tests test only code
  (madde 431)"*). Atlamaya devam etse, modelin okuduğu altı metin bu taramadan çıkar — test zayıflar.
  `skills/` klasöründeki `.md`'ler taranır, gerisi bugünkü gibi atlanır; yorum CLAUDE.md'deki istisnayı
  anar. **Taban:** `test_the_sweep_reads_the_tool`'un yanında, taramanın `skills/`'e ulaştığını gösteren
  bir assert — yürüyüşte `sdxl-edit.md` ile biten bir yol var; yoksa istisna hiçbir şeyi taramadan geçerdi.
- `test_skills.py`'nin `test_the_checks_are_written_in_the_flow_itself`'i `vars(prompt)`'un string'lerini
  yürüyor; `SDXL_GUIDE` ve `KREA_GUIDE` kalkınca iki belge bu yürüyüşten düşer. Testin gücü kalsın diye
  yürüyüşe `prompt.GUIDES`'ın değerleri de katılır.

**Değişmeden geçmesi gereken** (hiçbiri gevşetilmez, silinmez): `test_skills.py`'nin geri kalanı,
`test_prompt.py`'nin var olanları (`_texts_named_by`, `MUST_BE_FULL`, eski yer koruması), `test_tools.py`,
`test_model_engine.py`, `test_files_api.py`, `test_run_turn.py`, `test_chats_api.py`,
`test_composition.py`. Hepsi metne bugünkü adlarla ulaşıyor.

## Maliyet

| İşlem | Disk | Ağ | Not |
|---|---|---|---|
| Sunucunun açılışı (`prompt` içe aktarılırken) | 6 okuma, bir kez | 0 | repodan: yerelde checkout, Colab'da `/content/Internal-tools` — yerel disk, Drive değil |
| Her istek, her model turu | 0 | bugünkü gibi | metinler bellekte, bugünkü gibi |
| Dosya paneli, `read_file` (belgeler) | 0 | — | `FileFileStore` belleğindeki haritadan, bugünkü gibi |
| Her pytest süreci | 6 okuma, bir kez | 0 | |

Proje, sohbet ya da dosya sayısıyla büyümez: O(1). Önbellekli baş (`SYSTEM_PROMPT`, araç listesi)
değişmez; skill kuyrukta ve belgeler kutuda bayt bayt aynı gittiği için hiçbir isteğin token'ı değişmez.

## Ne kaybolabilir, ne bozulabilir

- **Eksik ya da okunamayan dosya:** `prompt` içe aktarılamaz, sunucu açılmaz; Python'un
  `FileNotFoundError`'u dosyanın yolunu söyler. Boş metin olarak alınmaz — boş bir skill sessizce
  talimatsız tur koşardı. Bu kullanıcının verisi değil, reponun bir parçası: eksikse repo bozuk.
- **Kullanıcının `.md`'yi düzeltmesi bir kod değişikliğidir:** `test_skills.py` ve `test_prompt.py`'nin
  içerik testleri (ilk satır, adımlar, kelime tavanları, belgelerin kuralları) bir yeniden yazımda kırmızı
  yanabilir, ve değişiklik suite'ten geçer. Sunucu yeniden açılınca görülür; Colab ancak push'tan sonra,
  notebook'un klonladığı sürümle görür. Sondaki boş satırlar atılır; BOM ve `\r` testte görünür.
- **Yazma yok:** okuyucu hiçbir şey yazmaz; iki istek aynı anda ya da çökme hiçbir şeyi bozmaz.
- **Yol:** dosya adları kodda sabit; URL'den gelen hiçbir değer bu klasörde bir yola dönmez. Belgeler
  bugünkü gibi `FileFileStore`'un haritasından, adıyla bulunur.
- **Gizli şey:** metinlerde yok.
- **GitHub'da görünüş:** skill metinlerinde ardışık satırlar (*"Step 6 -- …"*, *"Context"*) Markdown'da
  tek paragrafa birleşerek görünebilir. Metin buna göre düzenlenmez — bayt bayt aynı kalır; düz metin
  olarak, editörde satır satır okunur.

## Sınırlar

- `SYSTEM_PROMPT`, `system_prompt()`, `CHECK`, araç açıklamaları ve tek satırlık metinler kodda kalır.
- Sunucu açıkken dosya değişikliğini izleyen bir yeniden yükleme yok.
- `.gitattributes` eklenmez. Metinlerde tek kelime değişmez; yeni araç, yeni alan yok; ön yüz ve `dist`
  değişmez.

## Bitti sayılır

1. Altı `.md` `queen-agent/backend/features/workspace/skills/`'te, repoda açılıp okunuyor.
2. `tmp/m495-bytes.py` altısı için *eşit* diyor: modelin aldığı metin (`prompt`'un dört skill sabiti,
   `skills.INSTRUCTIONS`, `GUIDES`) `c1fdff97`'deki sabitlerle bayt bayt aynı, CRLF kopyadan da.
3. Ajan ve dosya paneli belgeleri dosyadan gelen metinle görüyor (`FileFileStore`'a verilen harita
   `GUIDES`, değişmeden).
4. Yeni üç test ve uyarlanan tarama yeşil; var olan metin testleri değişmeden yeşil.
5. Dört suite tek tek yeşil. QA yok: ekran değişmiyor.

## Durak 1'de kullanıcıya sorulacaklar

1. **Okuyucunun yeri:** A (öneri — `prompt.py` okur, CODE-STANDARD'ın domain cümlesine adıyla bir
   istisna) ya da B (domain kuralı aynen kalır; var olan kod yeniden yapılandırılır).
2. **Dört skill dosyasının adı:** seçicinin adlarıyla (öneri — `sdxl-start-scenario.md`, `sdxl-edit.md`,
   `krea-start-scenario.md`, `krea-edit.md`) ya da id'lerle (`start-a-scenario.md`, `edit-prompts.md`, …).
3. **CLAUDE.md satırı**, yukarıdaki metniyle.
4. **CODE-STANDARD'ın iki cümlesi**, yukarıdaki metinleriyle.
