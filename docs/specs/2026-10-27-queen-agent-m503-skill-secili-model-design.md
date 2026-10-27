# Madde 503 · Skill seçili modeli söyler — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v12 yol haritası](../roadmaps/2026-10-24-queen-agent-v12-roadmap.md#v12-3),
503 · v12-3 · **Dal:** `feat/queenagent-v12` · **Önceki:** v11'de
[492](../arsiv/specs/2026-10-22-queen-agent-m492-krea-prompts-design.md) (iki model, dört skill) ve
[495](../arsiv/specs/2026-10-23-queen-agent-m495-skill-md-design.md) (skill'ler `.md`) ·
**Kurallar:** [FOUNDATION](../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Kullanıcı, 27 Ekim — *"İlk cevapta. SDXL start scenario'yu seçip ilk mesajı gönderince ajan hemen
soruyor."* Ajan "Krea mı, SDXL mi?" diye soruyor. Kullanıcının kararı: *"bu bnece prompt 1 cümleyele
çözeriz başta neyin seçildiğini"*; *"bence hepsini ekelyelim krea ve sdxl editler start senayolar
vs"*. Dört skill'in başına, hangi modelin seçildiğini söyleyen birer cümle.

## Skill modele nasıl ulaşıyor

- Seçici bir id gönderir; `domain/skills.py` id'yi metne eşler, metin `domain/prompt.py`'nin
  `skills/` klasöründen import anında bir kez okuduğu `.md` dosyasıdır.
- `run_turn._asked` metni isteğin **sonuna**, ayrı bir system mesajı olarak koyar: konuşma, dosya
  adları, açık dosyalar, sonra skill; turun son raundunda yalnız `LAST_ROUND` notu onun arkasına
  gelir. Yani skill'in ilk satırı, modelin bu turda okuduğu son metinlerden birinin başıdır.
- Model her turda **bütün araçları** görür; yalnız SDXL'e ait olanların açıklaması `SDXL scenario:`
  ile, yalnız Krea'ya ait olanlarınki `Krea scenario:` ile başlar; ikisinin ortak iki aracı
  (`remove_frame`, `build_prompts`) `SDXL or Krea scenario:` der. Dosyalar `.sdxl.json` ve
  `.krea.json`.
- System prompt'un "Asking" kuralı: *"never guess what only they can decide (a number, a name, which
  meaning), and never guess what they asked for when you are not sure: ask."* SDXL start'ın metni işi
  yalnız *"scenario JSON"* diye anıyor; model hangi modelin seçildiğini bir yerden okuyamıyor, o yüzden
  bunu kullanıcının karar vereceği bir şey sayıp soruyor.

## Cümle

SDXL'in iki skill'inde:

> The user has already chosen the image model, SDXL: the scenario is an SDXL scenario, a .sdxl.json file, so never ask which model.

Krea'nın iki skill'inde:

> The user has already chosen the image model, Krea: the scenario is a Krea scenario, a .krea.json file, so never ask which model.

Neden bu sözler:

- **"The user has already chosen"**: soru kuralı *"what only they can decide"* için soruyor; cümle o
  kararın verildiğini söylüyor, yani kuralın kendisi artık sormayı istemiyor. "Selected" yerine
  "chosen by the user", çünkü seçen bir arayüz değil kullanıcı, ve kural kullanıcının kararından
  söz ediyor.
- **"an SDXL scenario" / "a Krea scenario"**: araçların açıklamaları tam bu sözle başlıyor
  (`SDXL scenario: …`, `Krea scenario: …`). Cümle modeli doğrudan kendi araçlarına bağlıyor. Araç adı
  yazılamaz: skill'ler hiçbir aracı adıyla anmaz (madde 393, `test_no_instruction_names_a_tool`).
- **".sdxl.json" / ".krea.json"**: düzenleme skill'inde proje iki türü de tutabilir; dosya türü hangi
  dosyanın kastedildiğini de söylüyor. Start'ta açılacak dosyanın türü.
- **"so never ask which model"**: sorulmaması gereken şeyi açıkça adlandırıyor. Diğer modelin adı
  geçmiyor: her modelin kuralları yalnız kendi yerinde durur (madde 492; SDXL metninde "krea", Krea
  metninde "sdxl" geçmez, testler tutuyor).
- Aynı modelin start'ı ve edit'i aynı cümleyi taşıyor: "the scenario" ikisinde de doğru — start onu
  açıyor, edit onu değiştiriyor. Bir cümle, iki yer; dört ayrı metin değil.

## Nereye

Her skill'in **ilk satırı**, rehber satırının hemen önü:

```
The user has already chosen the image model, SDXL: …, so never ask which model.
Read sdxl-prompt-writing.md first.

You are an expert scenario writer …
```

- Kullanıcı "başta" dedi. Model önce hangi modelle çalıştığını, sonra o modelin rehberini okuyor;
  rehber satırının "first" demesi hâlâ doğru, çünkü rehber işten önce okunuyor.
- İki satır bir paragraf: ikisi de "hangi model ve onun kuralları nerede" diyor. Persona bunların
  arkasında başlıyor, eskisi gibi.
- `Context` bölümüne konmadı: "başta" değil, ve madde 492'nin kuralı rehber satırının skill'in
  açılışı olmasıydı; açılış şimdi seçili modeli ve rehberi birlikte söylüyor.

Cümle dışında skill metinlerinde hiçbir şey değişmiyor (kullanıcı: *"prompt 1 cümleyele çözeriz"*).
`prompt.py`'de skill'lerin açılışını anlatan yorum, bugün doğru olanı söylesin diye güncelleniyor.

## Testler (`queen-agent/backend/tests/test_skills.py`)

- **Yeni:** `test_every_skill_opens_by_saying_which_model_the_user_chose` — her skill tam bu cümleyle
  başlıyor. Cümle testte bir sabit olarak yazılı: skill'ler modelin girdisi, testler onları sabit gibi
  okur (madde 495).
- **Değişen:** `test_every_skill_opens_by_sending_the_model_to_its_guide` — rehber satırı artık
  cümlenin hemen arkasında; açılış = cümle + rehber satırı. `FIRST_LINE` iki sabite ayrılır
  (`MODEL_CHOSEN`, `GUIDE_LINE`) ve açılış onlardan kurulur; persona testleri açılışın arkasına bakar.
- **Kelime sınırları:** dört metin 2012, 263, 531 ve 314 kelime; cümle 23 kelime ekliyor ve dördü de
  sınırı aşıyor. Sınır yalnız yazılı bir kararla yükselir; bu kararı kullanıcı 27 Ekim'de verdi (cümle
  dört skill'e de girsin). Yeni sayılar 2035, 286, 554, 337; sınırlar 2040, 295, 560, 345 — kural ne
  istiyorsa o: metnin geldiği yer ve birkaç kelime pay, bir sonraki cümleye yer değil.
- **Daralan:** `test_every_skill_says_what_the_prompts_are_for`. 393'ün kuralı *(30 Eylül)*: skill
  metninde "SDXL" geçmez, çünkü Context modelin adını değil nasıl olduğunu söyler. O gün tek model
  vardı; 492'den beri iki model var ve onları ayıran şey adları. Ana ajanın kararıyla *(27 Ekim, yol
  haritasında "Yapılırken kararlaşan")* kural artık açılışın arkasındaki gövdeye bakıyor: açılış
  cümlesi "SDXL" diyebilir, metnin geri kalanı yine demez.
- Var olan "diğer modeli anmaz" ve "araç adı yok" testleri cümleyi de kapsıyor ve geçiyor.

## Maliyet ve risk

Çalışma anında değişen bir şey yok: metinler import anında bir kez okunuyor, her istekte skill ~23
kelime (~30 token) uzuyor. Disk ya da ağ çağrısı eklenmiyor. Skill isteğin sonunda durduğu için önbellek
öneki değişmiyor.

Risk: cümle "never ask which model" diyor; kullanıcı SDXL edit seçiliyken bir `.krea.json` dosyasını
anarsa model artık sormaz. Bu, yanlış skill'in seçili olduğu durum; kullanıcının seçtiği skill'e
uymak maddenin istediği şey, seçiciyi düzeltmek kullanıcının.

## Bitti sayılır

- Dört skill'in ilk satırı bu cümle; `python -m pytest queen-agent -q` yeşil.
- Kabul (kullanıcının, koşunun sonunda canlı modelle): SDXL start scenario seçilip başlatılınca ajan
  "Krea mı, SDXL mi?" diye sormuyor. Ekranda denenmez (ana ajan, 27 Ekim).
