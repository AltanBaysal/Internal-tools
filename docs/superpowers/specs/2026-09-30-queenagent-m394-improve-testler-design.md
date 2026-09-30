# Madde 394 — Improve: ayrı bir skill olarak hazır senaryoyu kontrol eder · test turu

**Kaynak:** [yol haritasının 394'ü](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — *(kullanıcı, 30 Eylül —
"imrpove ayrı skill olacak dedik")*, *"evet abi edit prompt gibi düşün ama birebir kopyalayalım textleri baştaki
context farklı olsun ne dersin"*, ve kodu bir subagent'ın tamamlaması *("tamamdır commitle ve abi kod kısmını
tamamla ve işaretle lütfen subagentla devam et")*. Bitti sayılır: seçicide Edit prompts'tan sonra `Improve`
var, ve seçilince modele Improve'un metni gidiyor; dört satır yeşil.

**Kullanıcıdan gereken:** hiçbir şey. Improve'un metni kullanıcıyla satır satır yazıldı:
[prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py)'deki `IMPROVE` sabiti, çalışma
ağacında commit'lenmemiş duruyor. Metin Start a scenario'nun Step 6 – 10'unun birebir kopyası: 1 – 5 diye
numaralanır, inceleme dosyaları `-review-1.md` … `-review-4.md`, Step 5'in altı kuralı Context'te, ve
adımlardan önce dosyayı okuyup prompt'ları bir kez kuran bir *"Before the steps:"* bloğu. Seçicideki satırın
sözü de verildi: *"Check a scenario you already have, fix what fails, and write its negative list again."* —
tasarımcının yer tutucusundaki *"say yes after each one"* artık doğru değil, adımlar onay beklemiyor.

**Kapsam dışı:** `IMPROVE`, `START_A_SCENARIO` ve `EDIT_PROMPTS`'un tek bir kelimesi — kullanıcı onayladı.
Yol haritası, BACKLOG ve `tmp/`. Modelin Improve'u gerçekte nasıl yürüttüğü — tarayıcıda ya da gerçek bir
çağrıyla denenmez; kullanıcı sonunda dener.

## Ne kanıtlanacak

- Menü ile `INSTRUCTIONS` aynı üç adı taşır, ve `improve` boş olmayan bir metin taşır.
- Improve'un biçimi, `test_skills.py`'nin Start a scenario'yu tuttuğu gibi tutulur:
  - persona ile açılır, var olan bir senaryoyu beş adımda geliştirdiğini söyler;
  - beş adım başlıklarıyla ve çalıştıkları sırayla yazılı;
  - 1 – 4'ün her biri *Context* → *Part 1 -- review* → *Part 2 -- fix* sırasında, kendi `-review-N.md`
    dosyasını yazar, sorun yoksa yazmaz, ve yalnız o kareleri düzeltir;
  - 1 – 4 onay beklemez ve aynı turda sonraki adıma geçer;
  - 5 negatif listeyi yazar, onay anmaz, ve metin *"- Tell the user the prompts and the negative list are
    complete."* ile biter;
  - altı kural Improve'un kendi Context'inde, *"Before the steps:"*'ten önce;
  - *"Before the steps:"* dosyayı okur ve prompt'ları kurar, Step 1'den önce.
- Mevcut testler Improve'a yer açar, iddialarını bırakmadan: kontrollerin satırları yine başka hiçbir metinde
  yok — Improve hariç; *"The image model is weak"* her skill'de var; Improve'un kendi kelime tavanı var.
- Seçicide Improve üçüncü ve son satır, Edit prompts'tan sonra, verilen açıklamasıyla.

## Kararlar

1. **Improve kayıttan okunur:** `_improve()` = `instruction_for("improve")`, `_flow()` ve `_edit()` gibi.
   `prompt.IMPROVE` doğrudan okunsaydı testler kayıt yapılmadan yeşil geçerdi; bitti ölçütü modele *seçilince*
   giden metin.
2. **`IMPROVE_STEPS` beş başlık, yazılı olarak**, ve `_improve_step(number)` `_step` gibi: başlıktan sonraki
   başlığa, son adımda metnin sonuna. Anahtar içerik adımın kendi diliminde aranır; bir cümle yanlış adıma
   düşerse test kırmızı olur. Başlıklar `STEPS`'ten türetilmez — yazılı hâli okunur, ve metinle yan yana
   durur.
3. **`test_the_checks_are_written_in_the_flow_itself` `IMPROVE`'u da dışarıda bırakır.** Test ayrı bir sabitten
   birleştirilen satırı yakalar; Improve'da aynı satırların durması kullanıcının kararı — kendi skill'inde
   birebir kopya, hiçbir şeye birleştirilmez. Yorum bunu söyler. Çalışma ağacında `IMPROVE` zaten durduğu için
   bu test bugün kırmızı; dışlamayla yeşile döner.
4. **`test_every_skill_says_what_the_prompts_are_for` noktayı bırakır:** `"The image model is weak."` →
   `"The image model is weak"`. Improve bunu *"The image model is weak and draws every tag in the prompt."*
   cümlesiyle söyler; iddia — modelin zayıf olduğu söylenir — aynı kalır. Yorumdaki *"Both texts"* doğru
   olmaktan çıkar, *"Every text"* olur.
5. **Kelime tavanı: Improve için 1480.** Metin `split()` ile 1463 kelime (elle sayıldı: açılış ve Context 397,
   *Before the steps* 35, adımlar 193 + 199 + 215 + 186 + 238). Tavan bunun ve birkaç kelimelik payın toplamı —
   bir sonraki cümleye yer değil. Gerekçe, dosyanın öteki tavanlarının gerekçeleriyle aynı yorumda yazılı
   (kullanıcının kuralı: tavan yalnız yazılı bir kararla oynar). Test turunda `_improve()` boş olduğu için
   yeşil; uygulama turunda gerçek metni tutar, ve sayım yanlışsa pytest gerçek sayıyı gösterir.
6. **`test_prompt.py`'nin `MUST_BE_FULL`'u `IMPROVE`'u da sayar.**
7. **Ön uç:** `skills.test.js` sırayı üç satır olarak tutar, ve Improve'un en sonda verilen ad ve açıklamayla
   durduğunu tutar; *"the two rows"* başlığı doğru olmaktan çıktığı için *"the rows"* olur. `SkillPicker.test.jsx`
   seçici açıkken satır adlarının sırasını okur: Edit prompts'tan hemen sonra Improve, son satır, açıklamasıyla.
   `App.test.jsx` ve `ChatScreen.test.jsx` satırları saymıyor, listelemiyor — değişmez.

## Testler ne tutar

`queen-agent/backend/tests/test_skills.py`:

| # | Ne | Çalışma ağacında bugün |
|---|---|---|
| T1 | `ALL_SKILLS` `improve`'u taşır → `test_every_skill_in_the_menu_carries_an_instruction[improve]` | kırmızı |
| T2 | `test_the_menu_and_the_instructions_carry_the_same_names` (üç ad; yorum üçü söyler) | kırmızı |
| T3 | `test_every_skill_says_what_the_prompts_are_for[improve]` (noktasız) | kırmızı |
| T4 | `test_improve_opens_as_a_persona`: persona ile başlar, *"You improve an existing scenario JSON"* | kırmızı |
| T5 | `test_improve_runs_five_numbered_steps`: *"five steps"* var, *"ten steps"* yok, beş başlık var | kırmızı |
| T6 | `test_improves_steps_are_written_in_the_order_they_run` | kırmızı |
| T7 | 1 – 4 (parametreli): Context → Part 1 → Part 2, kendi `-review-N.md`'si, *"write no review file"*, *"Fix only the frames in the review file."* | kırmızı ×4 |
| T8 | 1 – 4 (parametreli): *"This step waits for no approval."*, *"Go on to Step N+1 in the same turn."* | kırmızı ×4 |
| T9 | 5: *"write the negative list"* başlığı, `-negative.md`, metin `LAST_WORD` ile biter, 5'te *"approval"* yok | kırmızı |
| T10 | Altı kural Improve'un Context'inde, *"Before the steps:"*'ten önce | kırmızı |
| T11 | *"Before the steps:"* dosyayı okur ve prompt'ları kurar, Step 1'den önce | kırmızı |
| T12 | `test_the_checks_are_written_in_the_flow_itself` `IMPROVE`'u dışarıda bırakır | kırmızı → yeşil |
| T13 | Kelime tavanı: `len(_improve().split()) <= 1480`, gerekçesi yorumda | yeşil (metin boş) |

`test_no_instruction_sends_the_model_to_fetch_a_shape[improve]` de yeni bir parametre olarak gelir; boş metin
*schema* taşımadığı için bugün de yeşil.

`queen-agent/backend/tests/test_prompt.py`:

| # | Ne | Çalışma ağacında bugün |
|---|---|---|
| T14 | `MUST_BE_FULL` `IMPROVE`'u sayar | yeşil (sabit çalışma ağacında var) |

`queen-agent/frontend/src/features/workspace/`:

| # | Ne | Bugün |
|---|---|---|
| T15 | `skills.test.js`: satırlar `start-a-scenario`, `edit-prompts`, `improve` sırasında | kırmızı |
| T16 | `skills.test.js`: son satır `{ id: "improve", name: "Improve", detail: … }` | kırmızı |
| T17 | `SkillPicker.test.jsx`: açık seçicide satır adları Start a scenario, Edit prompts, Improve; Improve'un açıklaması görünür | kırmızı |

## Tutmadıkları

- Metnin tam sözleri: testler biçimi ve anahtar cümleleri tutar; sözü kullanıcı zaten onayladı.
- Improve'un satırlarının Start a scenario'nunkilerle birebir aynı kaldığı — kopyanın kendisi kullanıcının
  kararı, ve iki metnin ileride ayrılması da kullanıcının kararı olur; bir eşitlik testi o günü kırmızı yapardı.
- `dist` — bu turda yalnız test dosyaları değişir, ve test dosyaları bundle'a girmez.

## Nasıl görülür

CLAUDE.md'deki dört satır, yazıldığı gibi, paralel; iki `npm` satırı arka planda. Beklenen:
`python -m pytest queen-agent -q`'da T1 – T11 (17 test) kırmızı, geri kalanı yeşil — T12 dahil;
`npm test --prefix queen-agent/frontend`'de T15 – T17 (3 test) kırmızı; queen-editor'ün iki süiti yeşil.

Commit: testler, bu spec ve planı; `prompt.py` staged edilmez. Commit'lenen ağaçta `IMPROVE` olmadığı için
orada T14 ve Improve'un testleri de kırmızıdır — kırmızının sebebi aynı: Improve henüz yok.

Adım adım dökümü [test turunun planında](../plans/2026-09-30-queenagent-m394-improve-testler-plan.md).
