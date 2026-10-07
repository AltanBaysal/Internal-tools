# Madde 391 — Senaryonun geliştirilmesi: Start a scenario sonunda kontrolleri yapar · test turu

> **30 Eylül güncellemesi — metin kullanıcıyla satır satır yazıldı.** Ne değiştiği
> [uygulama spec'inin](2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-uygulama-design.md)
> başında. Testler son metne göre yeniden yazıldı; bugünkü hâli
> [test_skills.py](../../queen-agent/backend/tests/test_skills.py)'de, *"the checks the flow ends with
> (Madde 391)"* bölümünde. Aşağıdaki tablo ilk taslağın testleri; bugün tutulanlar:
>
> - Dokuz adım; dört kontrolün (6 – 9) her biri *Context*, *Part 1 -- review*, *Part 2 -- fix* sırasıyla,
>   kullanıcıya ne geliştirdiğini tek satırla söyler, build edilmiş prompt dosyasını okur, kendi
>   `-review-N.md` dosyasına yazar — sorun yoksa yazmaz — ve yalnız o kareleri düzeltir.
> - 6: tam dört saniye; bütün olaylar korunarak yeniden yaz, olmuyorsa ikiye böl; "important" yok.
>   7: tek fotoğraf; sahneye dokunmaz, sahne eklemez. 8: gizli tag, saç örneği. 9: kullanıcının sorusu.
> - 7 – 9'un Context'i modelin zayıf olduğunu söyler, 6'nınki görsel modeli anmaz; düzeltme parçanın
>   senaryo dosyasında geldiği yerde, gerekirse yeni kayıtla.
> - Kontrollerde araç adı, alan adı, zamir ve değişiklik raporu yok; akış *"Build the prompts again,
>   and tell the user the prompts are complete."* ile biter. Kelime tavanı 1220.

**Kaynak:** [yol haritasının 391'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (*"Prompt'lar yeniden —
kullanıcıyla birlikte, bu sırayla"*), ve kullanıcının istekleri kendi sözleriyle
[prompt istekleri](../research/2026-09-30-queen-agent-prompt-istekleri.md)'nde: *"2. Kullanıcının elle
sorduğu dört soru"* (1, 2 ve 4) ve *"5. Akış, Improve ve onay"*. Kullanıcının 30 Eylül'deki kararları:

- Start a scenario'nun bugünkü 1 – 5. adımları anlamca değişmez. 5. adım prompt listesini yazdıktan
  sonra üç yeni adım gelir, bu sırayla: **6 — tek an**, **7 — görünen parçalar**, **8 — çizilebilir mi**.
- **Tek an:** *"model çok zayıg ve tek bir anın fotoğrafının yapıyorum promptun veya senaryonun 1den
  fazla sahneyi analyıyorsa lütfen güncelle diyorum basit ve tek bir anı gösteicek şekilde yada bir kaç
  sahneye böl"*. Sahnesi değişen karenin aksiyonu yeniden yazılır; bölünen karenin yeni kareleri de
  kendi aksiyonlarını aynı yoldan alır.
- **Görünen parçalar:** *"ypatığın açıda o hangi karakterin hangi parçaları görünüuorsa onları yaz prompta
  yoksa model zayıf olduğu için o özellikleri öteki karakterler eklyior"*. Seçilen yol: yalnız görünenin
  ikinci bir girdisi `add_character` ya da `add_outfit` ile, ona göre adlandırılarak (`man body no face`,
  `dress from behind`); varsa yeniden kullanılır; `update_frame` karenin kadrosunu bütün girdi yerine o
  girdiyle alır; açının hiç göstermediği kişi o karenin kadrosundan çıkar. Bütün girdiler olduğu gibi
  kalır.
- **Çizilebilir mi:** kullanıcının kendi sorusu olarak — *"fotoğra üretene yapay zeka modeli çok zayıf
  sence yazdığın promptu bu yapayzeka üretevbilir"*. Çizilemeyen kısım geldiği yerde sadeleşir, an
  korunur. **Modelin ne çizemeyeceğini söyleyen açık uçlu bir satır yazılmaz** — *"ekstra compelx
  çizemez dersen geçkten gider olabilcek en basit şeyleri çizer"*.
- **Bu adımlar onay beklemez:** *"Direkt güncellesin yazsın sadece neyi değiştidğini"*. Her biri
  düzeltmesini doğrudan yapar, bir şey değiştiyse `build_prompts`'u yeniden çağırır, hangi karede neyi
  değiştirdiğini söyler, ve aynı turda sonraki adıma geçer; değişecek bir şey yoksa bunu bir satırla
  söyler. *How a step runs* her adımın onay beklediğini söylediği için her biri, 1. adımın söylediği
  gibi, onay beklemediğini kendisi söyler.
- 5. adımın bugünkü kapanışı 8. adımın sonuna, sözü değişmeden taşınır; 5. adım 1. adımın *"This step
  waits for no approval. …"* satırı gibi 6. adıma geçerek biter. Açılıştaki *"five steps"* doğru sayı
  olur.
- **Ayrı sabit yok** *("promtplarda ayrı fiedlar açma")*: her cümle Start a scenario'nun kendi metninde,
  ait olduğu adımda durur.
- Kelime tavanı yazılı bir kararla, yeni adımların gerektirdiği kadar yükselir *(kullanıcı kararı,
  28 Eylül)*.

**Kullanıcıdan gereken:** hiçbir şey. Kararların hepsi yukarıda; kullanıcı değişikliği Changes'ten okur.

**Kapsam dışı:** negatif prompt (392), Improve (394), 1 – 5. adımlarda karelerin yazılışı ve `pov_`
(393), görüntü modelinin tanımı, 4 saniye. Yeni araç yok, araç açıklaması değişmez, öteki skill ve
`WRITE_FRAME_SYSTEM_PROMPT` değişmez.

## Ne kanıtlanacak

- Akış sekiz adım: 6, 7 ve 8, 5'ten sonra, bu sırayla; açılış *"eight steps"* der.
- Her yeni adım kendi anahtar içeriğini taşır (aşağıdaki tablo), ve araçları gerçekte çalıştıkları gibi
  adlandırır.
- 5, 6, 7 ve 8 onay beklemediğini söyler; 5 – 7 aynı turda sonraki adıma geçer.
- 6, 7 ve 8 bir şey değiştiyse listeyi yeniden kurar, neyi değiştirdiğini söyler, değişiklik yoksa bir
  satırla söyler.
- Kapanış metnin sonunda, 8. adımda; metinde bir kez.
- Adımların satırları modüldeki başka hiçbir metinde yok — ayrı bir sabitten gelmiyorlar.
- Hiçbir skill metni modelin karmaşığı çizemeyeceğini ya da yalnız basiti istemeyi söylemiyor.

## Kararlar

1. **`STEPS` sekiz başlık olur:** `Step 6 -- one moment`, `Step 7 -- visible parts`,
   `Step 8 -- can it be drawn` — görevin verdiği adlar, metnin başlık biçimiyle. Sırayı bugünkü
   `test_the_steps_are_written_in_the_order_they_run` tutar; sayıyı `test_the_flow_runs_five_numbered_steps`
   `test_the_flow_runs_eight_numbered_steps` olarak tutar.
2. **Bir adımı okuyan yardımcı** `_step(number)`: başlığından sonraki başlığa, son adımda metnin sonuna.
   Anahtar içerik adımın kendi diliminde aranır, böylece bir cümle yanlış adıma düşerse test kırmızı olur.
3. **Ayrı sabit yok, test olarak:** 6 – 8. adımların her satırı için, `prompt` modülünde
   `START_A_SCENARIO` dışındaki hiçbir metin o satırı taşımaz. Bir `THE_CHECKS` gibi sabit, ya da ortak
   bir kuyruk satırı sabiti, bu testi kırmızı yapar.
4. **Açık uçlu satır yasağı, önce varlık:** 8. adımın *"very weak"* sorusu önce aranır, sonra bütün skill
   metinlerinde `complex`, `what is simple` ve `cannot draw` yokluğu — boş bir metin üstünde yokluk
   testi yeşil geçmesin diye.
5. **`test_the_flow_never_writes_an_action_by_hand`'in adı yanlış olur:** 8. adım çizilemeyen bir
   aksiyonu `update_frame` ile kendisi sadeleştirir (kullanıcının kararı). İddiaları değişmez — sahneler
   adımı aksiyon yazmaz, ilk aksiyonları `write_missing_actions` yazar —, adı
   `test_the_flow_writes_no_new_action_by_hand` olur ve yorumu 8. adımın neden yolun etrafından
   dolaşmadığını söyler: aksiyon zaten yazılmış, akış onu kurulmuş prompt'ta okumuş, ve sadeleştiriyor
   (Madde 201'in editör için gerekçesi).
6. **Kelime tavanı 450'den 800'e.** Taslak metin 799 kelime (`split()`, madde işaretleri ve ` -- `
   dahil); dosyanın tavanları gibi onluğa yuvarlanır. Gerekçe mevcut yükseltmelerin yazıldığı yorumda,
   aynı yerde. Test turunda bugünkü metinle (427) yeşil kalır.

## Testler ne tutar — `test_skills.py`

| # | Ne | Bugün |
|---|---|---|
| T1 | `test_the_flow_runs_eight_numbered_steps`: *"eight steps"* var, *"five steps"* yok, sekiz başlık da var | kırmızı |
| T2 | `test_the_steps_are_written_in_the_order_they_run` (değişmez; `STEPS` sekiz) | kırmızı |
| T3 | 6. adım: *"more than one moment"*, *"split"*, *"one frame per moment"* | kırmızı |
| T4 | 6. adım: `update_frame` ve *"empty action"*, `add_scene`; ikisi de `write_missing_actions`'tan önce | kırmızı |
| T5 | 7. adım: *"camera angle"*, *"draws it anyway"*, *"somebody else"* | kırmızı |
| T6 | 7. adım: `add_character`, `add_outfit`, `update_frame`; *"man body no face"*, *"dress from behind"*, *"already there"*, *"in place of the whole one"*, *"leaves that frame's cast"*, *"whole entries stay as they are"*; sonra `update_character` ve `update_outfit` yok | kırmızı |
| T7 | 8. adım: *"build_prompts wrote"*, *"very weak"*, *"as it is written?"* | kırmızı |
| T8 | 8. adım: *"simplify it where it comes from"*, *"keep the moment"*, `update_frame`, `update_character`, `update_outfit`, `update_location` | kırmızı |
| T9 | Hiçbir skill metninde `complex`, `what is simple`, `cannot draw` yok (önce T7'nin *"very weak"*'i) | kırmızı |
| T10 | 6, 7, 8 (parametreli): *"build_prompts again if you changed anything"*, *"which frames you changed and what"*, *"say so in a line"* | kırmızı ×3 |
| T11 | 5, 6, 7, 8 (parametreli): *"This step waits for no approval."*; 5 – 7'de *"Go on to Step N+1 in the same turn."* | kırmızı ×4 |
| T12 | Metin kapanışla biter (*"Close by naming the file … this is the last word."*), kapanış 8. adımın diliminde, *"last word"* bir kez. Bugünkü metin de kapanışla bittiği için 8. adımın dilimi olmadan bu test bugün yeşil geçerdi | kırmızı |
| T13 | 6 – 8'in satırları `prompt` modülünde `START_A_SCENARIO` dışında hiçbir metinde yok | kırmızı |
| T14 | `test_the_flow_writes_no_new_action_by_hand` (yeniden adlandırılır, iddiaları aynı) | yeşil |
| T15 | Kelime tavanı 800, gerekçesi yorumda | yeşil |

Bugünkü öteki testler yeni metinle de yeşil kalmalı; metni yazarken dikkat edilecekler: `shot`,
`framing`, `one at a time`, `scene list`, `who is in it`, `edit_file`, `schema` metne girmez; alt çizgili
her kelime bir araç adı ya da `pov_` (noktalama yalnız `.,;:` soyulur, `update_frame's` gibi iyelik
yazılmaz).

## Tutmadıkları

- Metnin tam sözleri: testler anahtar ifadeleri tutar, sözü kullanıcı Changes'ten okur.
- Modelin bu adımları gerçekten nasıl yürüttüğü — tarayıcıda ya da gerçek bir çağrıyla denenmez; kullanıcı
  sonunda dener.
- `dist` — ön uç değişmiyor.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `python -m pytest queen-agent -q`'da T1 – T13 (18 test) kırmızı,
geri kalanı yeşil; öteki üç süit yeşil. **Commit yok** — bu madde için kullanıcının kararı: değişikliği
Changes'ten okur, onaydan sonra commit'lenir.

Adım adım dökümü [test turunun planında](../plans/2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-testler-plan.md).
