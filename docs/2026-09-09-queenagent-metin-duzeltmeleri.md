# Modele giden metinlerin düzeltme log'u

**Ne bu:** Madde 190'ın okuması sırasında bulunan düzeltmeler. Her biri
[modele giden metinler belgesinde](2026-09-09-queenagent-modele-giden-metinler.md) **uygulandı**,
`prompt.py`'de **henüz uygulanmadı** — kod tarafı **190'ın kendi kod geçişinde** iki tur koşularak
inecek.

**Neden ayrı dosya:** okuma sürerken metin bir yerde tartışılıp bir yerde biriksin. Belge yeni hâli
gösteriyor, bu log **eskisini, yenisini ve gerekçesini** tutuyor — yani o geçişin girdisi bu dosya.
Kod düzeldiğinde satırın **Durum**'u `kodda` olur.

**Okuma 10 Eylül'de kapandı:** bekleyen karar kalmadı. Log 35 düzeltme taşıyor — son üçü *(33, 34,
35)* okumanın bulduğu çelişkiler değil, kapanıştan sonra alınan yeniden yazım kararları: üç metin
grubunun tamamı sade İngilizceye çevrildi. Numaralar kaymaz.

**Sıra böyle** *(kullanıcı kararı, 9 Eylül)*: okuma sürerken yalnız belge ve bu log değişir. Kod
ve testler **okumanın sonunda, tek geçişte** güncellenir — cümle cümle koda inmek okumayı
bölüyor.

**Bir testin sayısı da değişecek** *(20 numara)*: `test_the_texts_stay_short_enough_to_be_read`'in
düzeltme metni için tuttuğu tavan **200 → 260**. Akışın 450'si aynı kalıyor.

**Testler o geçişte gevşetilecek** *(kullanıcı kararı, 9 Eylül)*: `test_prompt.py`'nin cümle tutan
testleri, cümlenin tamamını değil **kuralın en kısa ayırt edici parçasını** tutacak — böylece
yeniden yazım kırmızı vermez, ama bir kural metinden düşerse verir. Silinmiyorlar: her biri bir
denemenin dersi *(Madde 107: tek satırlık bir mesaj sekiz araç çağrısına mal olmuştu)*.

---

## Uygulanan düzeltmeler

### 1 · `SYSTEM_PROMPT` — projeyi anlatan cümlenin öznesi

**Eski**

```text
You are inside one project. The project holds files, and every chat in it can see them.
```

**Yeni**

```text
You are inside one project. It holds files: you can see all of them, and so can every other chat in it.
```

**Neden:** cümlenin öznesi *proje*, oysa okuyan modelin bilmesi gereken iki şey var ve ikisi de onun
hakkında — **hepsini görüyor**, ve **gördüğü şey paylaşılan**. Eski hâli birinciyi hiç söylemiyor,
ikincisini de üçüncü şahıstan anlatıyor. `every chat` kısmı **duruyor**, çünkü taşıdığı bilgi kodda
görünmüyor: dosyanın kapsamı sohbet değil proje, yani bu sohbetin açmadığı bir dosya da listede
olabilir, ve buradan yazılan dosya öteki sohbetlerde görünür.

**Durum:** belgede · kodda değil

---

### 2 · `SYSTEM_PROMPT` — okuma kuralının eksiltili yarısı

**Eski**

```text
when the answer depends on one, read it first with read_file -- and nothing the answer does not need.
```

**Yeni**

```text
when the answer depends on a file, read it first with read_file. Read only what the answer needs.
```

**Neden:** ikinci yarı **eksiltili** — fiili düşmüş, ve tam okunuşu *"read nothing the answer does
not need"*. Zayıf modelin ilk düşürdüğü şey bu tür yan cümle, ve düşürdüğünde kaybolan kural
ucuz değil: açılan dosyalar bağlam kabında taşınıyor ve kap **son beş** dosyayı tutuyor
*(Madde 179)*, yani gereksiz bir okuma hem her raunt jeton yakıyor hem gerçekten lazım olanı
pencereden dışarı itiyor. Ayrı cümle olunca hem kısalıyor hem tartışmasız. `one` da `a file` oldu:
zamirin işaret ettiği şey iki cümle öncede.

**Durum:** belgede · kodda değil

---

### 3 · `SYSTEM_PROMPT` — tazeleme kuralının gerekçesi yanlış

**Eski**

```text
A fresh read is for a file somebody else may have changed since the chat last saw it, never to check your own writing: what you wrote is on disk as written.
```

**Yeni**

```text
A fresh read is only for a file that is not among your opened files: one you have never opened, or one the five have pushed out. Never read a file again to check your own writing or to see somebody else's change.
```

*(Gerekçe cümlesi burada değil artık — listenin kendi özelliği olarak bir önceki cümlede duruyor,
**4** numara.)*

**Neden:** öncekiler yazımdı, bu **davranış**. Cümle *"başkası değiştirmiş olabilir diye tekrar
oku"* diyor, oysa bağlam kabı açılmış her dosyayı **her raunt diskten okuyor**
*(`stream_answer.py`'nin kutuyu kuran döngüsü; `OPENED_FILES` da zaten "with their contents as they
are now" diyor)*. Yani kaptaki bir dosya kullanıcı elle değiştirse bile bir sonraki raundda yeni
hâliyle görünüyor — o çağrı boşa gidiyor, ve bir raunt ile jeton yakıyor. Tekrar okumanın gerçek
sebebi tek: **dosya kapta değilse** — hiç açılmamışsa, ya da son beşlik pencereden düşmüşse
*(Madde 179)*. Yeni hâli o sebebi söylüyor, ve iki gereksiz sebebi birlikte kapatıyor.

**Yeni hâlin kendisi bir kez daha yazıldı** *(9 Eylül, okuma sürerken)*. İlk denemesi şöyleydi:

```text
A fresh read is for a file that is not on that list -- one never opened, or one the five have pushed out. Not to check your own writing, and not to see somebody else's change: what is listed is read from disk every round.
```

Üç yerden yanlış anlaşılabiliyordu: **"that list"** hangi liste belli değildi *(promptta iki liste
var — projenin dosya adları, ve açık dosyalar)*, ve birincisi anlaşılırsa cümle tam tersini söyler;
**"not to see somebody else's change"** tek başına *"göremezsin"* diye okunuyordu; ve yapı yine
**fiilsizdi** — 2 numarada eleştirilen şeyin aynısı. Yenisinde her parçanın fiili var ve liste
adıyla anılıyor.

**Durum:** belgede · kodda değil

---

### 4 · `SYSTEM_PROMPT` — açık dosyalar listesinin hep güncel olduğu söylenir

**Eski**

```text
the file itself is listed among your opened files, kept as it is on disk.
```

**Yeni**

```text
the file itself is listed among your opened files, where it is read from disk again every round -- what stands there is always current.
```

**Neden** *(kullanıcı, 9 Eylül)*: *"kept as it is on disk"* bir **durum** anlatıyor, listenin
**davranışını** değil — model bundan "orada bir kopya var" sonucunu çıkarır, kopyanın tazelendiğini
çıkarmaz, ve tazelemek için tekrar okur. Cümle bunu doğrudan söyleyince 3 numaradaki iki yasağın
gerekçesi de kendiliğinden orada duruyor: yasaklar artık kendi gerekçelerini taşımıyor, kısalıyor.

İlk yazımında son parça `what stands there is always the file as it is now, whoever last wrote it`
diyordu. `whoever last wrote it` **çıkarıldı** *(kullanıcı, 9 Eylül)*: kapattığı durum — başkasının
ya da kullanıcının elle yaptığı değişiklik — bir sonraki cümlede zaten **kural** olarak duruyor
*(`or to see somebody else's change`)*. Aynı şeyi bir ipucu ve bir kural söylüyorsa kalması gereken
kuraldır.

**Durum:** belgede · kodda değil

---

### 5 · `SYSTEM_PROMPT` — her değişiklik `edit_file`'dan geçmiyor

**Eski**

```text
a change goes through edit_file, and a new file is for a new thing
```

**Yeni**

```text
a change goes through edit_file, or through the tool that owns that kind of file, and a new file is for a new thing
```

**Neden:** yanlış bilgi. Yapı dosyaları `edit_file`'a **kapalı** *(Madde 171)*: `_shut` uzantıya
bakıp *"it is not written or changed as text"* diye reddediyor, ve değişiklik `add_`/`update_`/
`remove_` araçlarından geçiyor. Cümleye inanan model bir raundu ret yiyerek harcıyor.

**Neden bu kadar genel yazıldı:** `test_the_base_names_no_task`, taban metnin `scenario` ya da
`structure file` gibi iş kelimelerini taşımamasını istiyor — taban *nasıl çalışılır*ı anlatır, *iş
nedir*i değil. İstisna bu yüzden adıyla değil, **sahipliğiyle** söyleniyor.

**Durum:** belgede · kodda değil

---

### 6 · `SYSTEM_PROMPT` — düzeltme kuralı: tespit değil tarif, ve yalnız düzeltme değil

**Eski**

```text
A correction the user makes afterwards reaches the file too; one that lands only in the chat leaves the file saying the older thing, and the file is what gets read next.
```

**Yeni**

```text
When the user asks you to change something that is in a file, make the change in the file.
```

**Neden:** eski hâli **haber cümlesi** — *"kullanıcının düzeltmesi dosyaya da ulaşır"*, yani
kendiliğinden olan bir şeyi anlatıyor gibi okunuyor. Oysa bu modele verilmiş bir iş: düzeltmeyi
dosyaya **o** yazacak. Tespit diye okuyan model hiçbir şey yapmaz, ve dosya eski hâliyle kalır —
kuralın önlemeye çalıştığı şeyin ta kendisi.

**Ve hatayı anlatmıyor, yapılacak şeyi söylüyor** *(kullanıcı kararı, 9 Eylül)*. Ara denemelerden
biri hatayı adıyla anıyordu — *"sohbette 'haklısın' deyip bırakmak dosyayı yanlış bırakır"*. Doğruydu
ama uzundu, ve Madde 200'de `writing-skills`'in ölçtüğü şey şunu söylüyor: yanlış **şekil** üreten
bir modelde yasak/hata anlatan biçim pazarlığa açık, **tarif** eden biçim değil.

**Kural `correction`dan geniş** *(kullanıcı, 9 Eylül)*: aynı hata ilk istekte de oluyor — model
sohbette *"şunu şöyle yapıyorum"* diye anlatıp dosyaya inmiyor. `correction` kelimesi kuralı
gereksiz yere dar tutuyordu; şartı `belongs in a file` olunca hem düzeltmeyi hem ilk isteği
kapsıyor, ve `an ordinary reply is not a file` kuralıyla çelişmiyor.

**Öznesi somut** *(kullanıcı, 9 Eylül)*: ara hâllerden biri `When what the user asks for belongs in
a file…` diyordu — öznesi soyut *("kullanıcının istediği şey")* ve `belongs in` "ait olmak" gibi
okunuyordu. Son hâlde şart fiil-özne-nesne olarak duruyor, ve eylem cümlesi **hedefi** adlandırıyor:
`make the change in the file` — bu kuralın tamamı zaten o, değişiklik sohbette değil dosyada.
`already` kelimesi de atıldı: `is in a file` zaten var olanı anlatıyor.

**Sohbet yarısı buraya konmadı.** *"Ne yaptığını sohbette söyle"* kuralı son paragrafta zaten var
*(`always write your answer in the chat as well. End by saying what you did…`)*, ve bir kuralı iki
yerde söylemek bu koşunun kovaladığı şey. Aynı sebeple `-- the file is what gets read next, not the
chat` gerekçesi de düştü: sohbet **her raunt modele gidiyor**, yani o cümle olduğu gibi doğru
değildi — dosyadan okuyan şey araçlar ve öteki sohbetler.

**Durum:** belgede · kodda değil

---

### 7 · `START_A_SCENARIO` — döngünün kuralları madde madde

**Eski** *(tek paragraf)*

```text
Every step runs one loop: ask, write what you heard to disk, show it, and wait for the yes -- a step ends when the user approves it, never before. Nothing becomes a placeholder -- never stop the flow waiting for a description. A delegation -- you decide -- answers only the question that was asked: choose for that step, show it, and the step still ends when the user approves it; the next step's question is asked as ever, and the plan records it with the step it closed, never as a standing authority. An approved step is closed with mark_step_done, which fills that step's box and touches nothing else.
```

**Yeni** *(başlık + dört madde)* — tam hâli
[belgede](2026-09-09-queenagent-modele-giden-metinler.md), `How a step runs:` altında.

**Neden** *(kullanıcı, 9 Eylül)*: o paragrafta **beş ayrı kural** üst üste duruyordu — döngünün
kendisi, adımın onayla bitmesi, placeholder yasağı, *"sen karar ver"*in nasıl ele alınacağı, ve
`mark_step_done`. Bir modelin en kolay atladığı şey böyle bir yığın; her kural kendi satırında
olunca hem bulunuyor hem sayılıyor. Adımlar zaten numaralıydı, orası aynen duruyor.

**Rol cümlesi prose kaldı** — Madde 123'ün bulgusu: *"sen bir uzmansın"* açılışı zayıf modeli kural
listesinden daha iyi tutuyor, ve maddeye dönerse o etki gidiyor. Açılış paragrafına yalnız
`Five steps, in order; you walk the user through them by asking.` cümlesi katıldı, çünkü aynı şeyi
söylüyordu.

**Gerekçeler düşmedi:** `never before`, `never stop the flow waiting for a description`,
`never as a standing authority`, `touches nothing else` — hepsi kendi satırının sonunda duruyor.
Madde hâline getirirken en kolay kaybolan şey `because…` kısmı, ve zayıf modeli tutan da o.

**Ölçülmedi, ve kayda öyle geçiyor:** *"liste daha iyi okunur"* gerekçeli bir tahmin. Kesin bilmek
aynı işi iki metinle koşup hatayı saymak demek.

**Küçük iki dokunuş:** `A delegation -- you decide --` yerine `"You decide"` *(tırnak içinde,
kullanıcının söylediği söz olarak)*; ve 2. adımda `Each also gets` → `Each character also gets`,
çünkü `Each` bir önceki cümlenin öznesi olan kıyafetlere de bağlanabiliyordu.

**Durum:** belgede · kodda değil

---

### 8 · `START_A_SCENARIO` — döngü maddelerinin kendisi

7 numara paragrafı maddelere böldü; bu, maddelerin **içindeki** üç sorunu düzeltiyor.

**Yeni hâl** *(dördü birden)*

```text
How a step runs:
- Ask, write it into the file, show what you wrote, and wait for their yes. A step ends when they approve it, never before.
- Never write a placeholder, and never stop the flow to wait for a description: ask for what is missing, and carry on when it is answered.
- "You decide" covers that step only. Choose, show it, and still wait for the yes. Ask the next step's question as usual -- one "you decide" is not permission for the rest.
- Close an approved step with mark_step_done. It fills that step's box and touches nothing else.
```

**1. madde — biçim hakkında hiçbir şey söylemiyor** *(kullanıcı, 9 Eylül)*. Eskisi
`write what you heard to disk`, ara denemesi `write their answer into the file` diyordu; ikisi de
**kullanıcının cümlesini** dosyaya yazmayı ima ediyor. Oysa haritalara giren şey **İngilizce
etiket** — Türkçe *"25'lerinde, uzun siyah saçlı"* dosyaya `1girl, mature female, long hair,
black hair` diye inmeli. Biçimi her adımın **kendi aracı** belirliyor: `SDXL_PROMPT_RULES`
`add_character`/`add_outfit`/`add_location`'ın üstünde duruyor, ve tek istisna 4. adımın sahne
cümlesi *(`in their own language`)*. Döngü maddesi bu yüzden nötr: `write it into the file`.
Ayrıca `wait for the yes` ile `A step ends when the user approves it` aynı şeyi söylüyordu; ikincisi
yalnız `never before` için duruyor, o yüzden özneyi tekrarlamıyor.

**2. madde — iki kural, iki nokta üst üste ile birbirine bağlanmıştı.** `Nothing becomes a
placeholder: never stop the flow waiting for a description` — ikinci parça birinciyi açıklıyor gibi
duruyor ama ayrı bir kural, ve ilk okunuşta çelişik: *placeholder da yazma, beklemeyi de bırakma —
o zaman ne yapayım?* Cevap bir alt maddedeydi, burada yazmıyordu. Yenisi ikisini `and` ile ayırıyor
ve **çıkış yolunu** söylüyor: eksik olanı sor, cevaplanınca devam et.

**3. madde — dört şey bir aradaydı**, ve biri **yapılamayan bir şeydi**: `the plan records it with
the step it closed`. Planı işaretleyen araç `mark_step_done`, ve kuralı `touches nothing else` —
yani o kaydı yapacak yol yok *(planı `edit_file` ile elle değiştirmek dışında, ki onu hiçbir yer
söylemiyor)*. Cümle Madde 198'den önce yazılmış, araç değişince kalmış. **Düştü:** yetki zaten
devretmiyor, o yüzden kaydedilmemesi bir şey kaybettirmiyor. `never as a standing authority` de
somutlaştı: `one "you decide" is not permission for the rest`.

**Durum:** belgede · kodda değil

---

### 9 · `START_A_SCENARIO` — beş adım da aynı biçime geçti

**Eski:** her adım tek paragraf, `1. The plan. …` diye başlıyor ve adımın bütün işi o paragrafın
içinde akıyordu.

**Yeni:** her adım `Step N -- the plan` gibi bir başlık, altında yapılacak işler **madde madde**.
Tam hâli [belgede](2026-09-09-queenagent-modele-giden-metinler.md).

**Neden** *(kullanıcı, 9 Eylül)*: 7 numara döngü kurallarını maddelere böldü, adımlar paragraf
kaldı — aynı metnin içinde iki ayrı biçim. Ve adımların içinde de **sıra** var: 2. adımda önce
`start_scenario`, sonra `add_character`, sonra kıyafetler, sonra `pov_` girdisi. Paragrafta bu sıra
görünmüyor, maddede görünüyor.

**Hiçbir cümle atılmadı** — yalnız satır başları eklendi, ve 4. adımın *"sor, sonra yaz"* cümlesi
iki maddeye ayrıldı, çünkü iki iş.

**Kelime tavanı:** 450, ve başlıklar on kelime kadar ekliyor. Kodda uygulanırken
`test_the_texts_stay_short_enough_to_be_read` bunu söyleyecek; aşarsa tavan yükselmez, iki yerde
aynı şeyi söyleyen bir cümle silinir.

**Durum:** belgede · kodda değil

---

### 10 · `START_A_SCENARIO` — 1. adım: iki durum, ve planı yazan araç

**Eski**

```text
Step 1 -- the plan
- A chat's first turn opens with write_plan; later turns carry on from what the chat already knows.
- A plan already there when the chat opened is that memory: read it and carry on from the first step whose box is empty; with several, ask which.
- This step waits for no approval; the next question follows at once.
```

**Yeni**

```text
Step 1 -- the plan
- Do this on the chat's first turn only. Later turns carry on from where the chat already is.
- If the project holds no plan for this work, write one with create_file: one line per step, each written as - [ ] 1. and what that step is.
- If a plan is already there, read it and carry on from the first step whose box is still empty. If there is more than one plan, ask which.
- This step waits for no approval. Ask Step 2's question in the same turn.
```

**İki durum ayrıldı, ve koşul eylemden önce geliyor.** Eski birinci madde planı **koşulsuz** yazdırıyor
*("ilk tur `write_plan` ile açılır")*, var olan planın durumu ise ancak **ikinci** maddede geliyordu.
Sırayla okuyan model ilk turda planı yazar, ve `write_plan` aynı adın **üzerine yazıyor**
*(`tools.py`, `write_plan` dalı)* — işaretli kutular gider. Koşul önce dizilince o ihtimal kapanıyor,
ve iki durum aynı hizada duruyor.

**`with several, ask which` fiilsizdi** — 2 ve 3 numarada eleştirilen yapının aynısı, ve zayıf modelin
ilk düşürdüğü şey. Her parçası fiilli bir cümleye döndü.

**`later turns` kendi satırına çıktı:** söylediği şey *"bu adımı her turda tekrarlama"*, ve yazma
kuralına yapışık dururken kayboluyordu.

**Planı `create_file` yazıyor** *(kullanıcı kararı, 9 Eylül)*. `write_plan` ile `mark_step_done`
akışın yaslandığı iki özel araçtı; Madde 203 ikincisini zaten kaldırıyor, ve akış metni bir daha
kalkacak araçların üstüne kurulmuyor. Temel araçlar modelin **her istekte** gördüğü araçlar.

**Bunun bedeli yazılıyor:** araç iki şeyi bedavaya taşıyordu — dosyanın adı *(`plan_name`, hep
`<ad>-plan.md`)* ve aynı adın üzerine yazması. `create_file` ikisini de yapmıyor: ad modelin, ve
ikinci bir yazım eskisini ezmek yerine `-2` ile numaralanır *(Madde 179'un dosya adı kuralı)*. Buna
karşılık kutu biçimi artık maddenin kendi cümlesinde duruyor — `WRITE_PLAN`'in tarifine bağlı
değil, yani akış o aracı hiç çağırmasa da `- [ ] 1.` sabit. Ve numaralanma ihtimalini birinci madde
kapatıyor: plan yalnız ilk turda, yalnız ortada plan yokken yazılıyor.

**`write_plan` aracı duruyor:** bu bir metin kararı, kip kararı değil. Plan kipinde sormadan koşan
tek yazma odur ve turu bitiren çift odur *(`modes.py`)* — aracın kendisi kalkacaksa kendi maddesini
ister.

**Kutu ifadesi 203'ten sonra da doğru:** `box is still empty` biçime bağlı, `mark_step_done`'a değil.
Döngünün dördüncü maddesi aracı anmaya devam ediyor, çünkü onu `edit_file`'a çevirmek 203'ün işi.

**Kelime tavanı:** yaklaşık 20 kelime biniyor. Sıkışırsa ilk kısaltılacak yer üçüncü maddenin son
cümlesi.

**Durum:** belgede · kodda değil

---

### 11 · `START_A_SCENARIO` — nerede kalındığını kutu değil dosyalar söyler

10 numaranın üçüncü maddesi *"ilk boş kutudan devam et"* diyordu; bu, **nereye bakılacağını**
değiştiriyor.

**Eski**

```text
- If a plan is already there, read it and carry on from the first step whose box is still empty. If there is more than one plan, ask which.
```

**Yeni**

```text
- If a plan is already there, read it and carry on from where the work stopped. The project's files are what say how far it got; the plan's boxes are only a note. If there is more than one plan, ask which.
```

**Neden** *(kullanıcı, 9 Eylül)*: kutu artık **garanti değil**. Planı `create_file` yazınca ve
Madde 203'ten sonra işareti `edit_file` koyunca, işaretleme modelin atlayabileceği bir iş — ve
atlandığında *"ilk boş kutu"* hep 1. adımı gösterir, yani akış baştan başlar. Dosyalar ise iddia
değil olgu: `bar-scene.json` yoksa 2. adım hiç başlamamış, `…-prompts.md` varsa 5. adım bitmiş.

**Neden senaryo dosyası değil de projenin dosyaları** *(kullanıcı kararı, 9 Eylül)*: ad listesi
**her istekte zaten gidiyor** *(`FILES_HELD`)*, yani bu cevap hiçbir şey açmadan orada. Senaryo
dosyası ise 1. adımda henüz var olmayabilir *(onu 2. adım açıyor)* ve adı da o an belli değil.
Cümle `The project's files` diyerek modelin elindeki listeyi **adıyla** anıyor — 3 numaranın dersi:
işaret edilen liste adsız kalırsa model hangisi olduğunu tahmin ediyor.

**Bugünün ölçüsüne bağlı, ve kayda öyle geçiyor:** ad listesi okunur, çünkü bir projede az dosya
duruyor. Dosya sayısı büyürse adlar tek başına adım seviyesini söylemekte zorlanır, ve cümle o zaman
senaryo dosyasını adıyla anmak zorunda kalır. Adımın **içindeki** yeri — kaç kare yazıldığı gibi —
bu cümle zaten söylemiyor; onu o adımın kendi aracı açtığında görüyor, ve 1. adımın sorusu
*"hangi adım"*.

**Planın kalan işi daraldı:** nerede kalındığını dosyalar söylüyorsa, plan *"hangi senaryo, ne
için"*e iniyor. Madde 203'ün işaretleme maddesini yeniden yazma gerekçesi de bu kadar zayıflıyor —
o madde koşarken bakılacak.

**Kelime tavanı:** 10 numaranın üstüne ~13 kelime daha. Sıkışırsa ilk gidecek yer birinci maddenin
ikinci cümlesi.

**Durum:** belgede · kodda değil

---

### 12 · `START_A_SCENARIO` — 2. adım emir kipine geçer, ve kopya kurallardan kurtulur

**Eski**

```text
Step 2 -- the characters
- start_scenario opens the file here, once, named after what is being built, so every step after this writes into a file that exists.
- add_character puts each of them into it.
- Clothes are their own entries the moment they are described: add_outfit, named after the garment.
- Each character also gets a pov_ entry: what a frame through their own eyes holds of them, no count and no outfit.
- Offer build_character_prompts as a look at one character; carry on if declined.
```

**Yeni**

```text
Step 2 -- the characters
- Ask who is in this scenario, then open the file with start_scenario, once, named after what is being built: every step after it writes into a file that exists.
- Write each character in with add_character.
- Write a garment as its own entry with add_outfit the moment it is described.
- Give each character a pov_ entry as well, again with add_character: what a frame through their own eyes holds of them.
- Offer build_character_prompts as a look at one character on its own; carry on if they decline.
```

**Öznesi araç değil model artık.** *"start_scenario opens the file"*, *"add_character puts each of
them into it"* — ikisi de aracın ne yaptığını **anlatıyor**, modele iş vermiyor. 6 numaranın bulgusu
buydu: haber cümlesi diye okuyan model hiçbir şey yapmıyor. 10 numara 1. adımı emir kipine geçirdi,
ve bu adım anlatım kalınca aynı metinde iki ses duruyordu.

**Sorulacak soru eksikti.** Başlık *"the characters"* diyor, ama hiçbir madde **kim oldukları
sorulsun** demiyordu — `each of them` zamirinin öncülü metinde yoktu *(2 numarada düzeltilen sorunun
aynısı)*. 4. adım zaten `Ask how many scenes` diye açılıyor; bu adım da kendi sorusuyla açılıyor.

**`pov_` girdisinin aracı yazılmamıştı.** O giriş de `add_character` ile yazılıyor — adı `pov_…`
olan bir karakter girdisi — ama madde aracı anmıyordu, ve model kendi yolunu arıyordu.

**İki cümle `SDXL_PROMPT_RULES`'un kopyasıydı.** *"Clothes are their own entries… named after the
garment"* orada neredeyse birebir duruyor, `no count` da orada — ve o metin `add_character`'ın
tarifinin altında **her istekte** gidiyor. Akışın söyleyeceği tek şey kuralın kendisi değil,
**zamanlaması**: kıyafet tarif edildiği anda yazılır. Kopyalar düştü, zamanlama kaldı.

**Kelime tavanı:** iki cümle uzadı, iki cümle kısaldı — net ~8 kelime biniyor.

**Durum:** belgede · kodda değil

---

### 13 · `START_A_SCENARIO` — 3. adım: `the same loop` düşer, adım kendi işini söyler

**Eski**

```text
Step 3 -- the places
- add_location, the same loop.
```

**Yeni**

```text
Step 3 -- the places
- Ask where this scenario happens, and write each place in with add_location.
```

**Metindeki en uç fiilsiz satırdı** — öznesi de yok, yüklemi de. 12 numara 2. adımı emir kipine
geçirince bu satır tek başına kaldı.

**`the same loop` iki türlü okunuyordu.** Ya üstteki `How a step runs`, ya da **2. adımın sırası**.
İkincisi okunursa model mekân için kıyafet ya da `pov_` karşılığı arar — öyle bir şey yok, ve
aramak bir raunt yakar. Birincisi okunursa cümle gereksiz: o döngü zaten her adımı bağlıyor, ve
yalnız burada anılması ötekilerde geçerli değilmiş izlenimi veriyor. İki okunuşun ikisi de zararlı
olduğu için ifade düştü, karşılığında bir şey konmadı.

**Sorusu eklendi**, ve 2. adımın açılışıyla aynı kalıpta: `Ask who is in this scenario` →
`Ask where this scenario happens`. Aynı işi yapan iki adımın aynı biçimde açılması, modelin
adımlar arasında yolunu kaybetmemesi için.

**Mekân kuralı buraya konmadı:** *"kimse içinde olmaz"* kuralı `ADD_LOCATION_TAGS`'te duruyor
*(`Nobody is in it -- who is there is the frame's business`)* ve araç şemasıyla **her istekte**
gidiyor. 12 numaranın kuralı: akış kuralı değil zamanlamayı söyler.

**Kelime tavanı:** ~7 kelime biniyor.

**Durum:** belgede · kodda değil

---

### 14 · `START_A_SCENARIO` — 4. adım: şema tekrarı düşer, yasak emir kipine geçer

**Eski**

```text
- Ask how many scenes and which moments matter.
- Write them with add_scene: one sentence per scene, in their own language, and with each one who is in it, what they are wearing and where it happens.
- A frame is born with no action -- that sentence belongs to the model kept for writing them, never to you.
```

**Yeni**

```text
- Ask how many scenes and which moments matter.
- Write them with add_scene: one sentence each, in the language the user is writing in.
- Write no actions here. A frame is born without one, and the model kept for writing them fills it in Step 5.
```

**İkinci madde `add_scene`'in parametrelerini yeniden anlatıyordu:** *"one sentence per scene"*,
*"who is in it, what they are wearing"*, *"where it happens"* — üçü de `ADD_SCENE_SCENE`,
`ADD_SCENE_CHARACTERS` ve `ADD_SCENE_LOCATION`'da duruyor ve araç şemasıyla **her istekte** gidiyor.
12 numaranın kuralı burada da geçerli.

**Dil kısmı kaldı, ve sebebi var:** `add_scene`, ötekilerin aksine `SDXL_PROMPT_RULES` taşımıyor —
yani üç etiket aracıyla çalışan model sahne cümlesini de etiketleştirmeye çekilebilir. Tek cümlelik
hatırlatma o çekimi tutuyor. `their own language` **zamiri belirsizdi** *(kimin dili — sahnenin mi,
kullanıcının mı?)*; yeni hâli taban sistem mesajının kendi ifadesine bağlanıyor
*(`in the language the user writes in`)*.

**Üçüncü madde de yarı tekrardı:** *"a frame is born without its action, and write_frame_prompt is
what writes one"* zaten `ADD_SCENE`'in son cümlesi. Akışa özgü olan tek şey **yasak** — bu adımda
aksiyonu model yazmaz — ve o, haber cümlesi hâlinde duruyordu. Emir kipine geçti; gerekçesi
yanında kaldı, çünkü 7 numaranın bulgusu zayıf modeli tutan şeyin `because…` kısmı olduğunu
söylüyor.

**`never to you` neden `here` oldu:** Madde 201'den beri yasak **her yerde** doğru değil —
`UPDATE_FRAME` *"a line that reads wrong is corrected here, in your own words"* diyor, yani düzeltme
modelin işi. Yasak yalnız karenin **doğduğu** adım için geçerli, ve yeni cümle onu adımına
bağlıyor.

**Kelime tavanı:** bu adım ~8 kelime **kazandırıyor** — 10, 11 ve 13'ün bindirdiğinin bir kısmını
geri veriyor.

**Durum:** belgede · kodda değil

---

### 15 · `START_A_SCENARIO` — 5. adım: sıra emir olur, üst üste binen yasaklar ayrılır

**Eski**

```text
- write_missing_actions fills every waiting frame in one call, then build_prompts writes the list.
- The closing message is the file by name and that it is ready; the prompts are never printed back, it offers nothing and asks nothing, and it is the last word.
```

**Yeni**

```text
- Fill the waiting frames with write_missing_actions, then write the list with build_prompts.
- Close by naming the file and saying it is ready. Do not print the prompts back, offer nothing, and ask nothing: this is the last word.
```

**Birinci madde aracın kendi cümlesiydi:** *"fills every waiting frame in one call"* —
`WRITE_MISSING_ACTIONS` zaten *"the action of every frame … that is still without one, in one call"*
diyor. Akışa özgü olan tek şey **sıra**: önce aksiyonlar, sonra derleme. Madde artık onu söylüyor,
ve iki iş de emir kipinde.

**İkinci maddede üç yasak yan yanaydı, ve ikisi aynı şeydi:** *"offers nothing and asks nothing"* ile
*"it is the last word"* — soru sorulmayan bir mesaj zaten son sözdür. Yeni hâlde ikisi ayrıldı: iki
yasak emir olarak duruyor, *"son söz"* ise onların **gerekçesi** olarak sonda. 7 numaranın kuralı:
gerekçe düşmez, ama emrin yerine de geçmez.

**Açılışı haber cümlesiydi** *("The closing message is…")*. Kapanışı yazacak olan model, ve cümle
ona iş vermiyordu — 6 ve 12'de düzeltilen kusurun aynısı.

**C satırına dokunulmadı:** `WRITE_MISSING_ACTIONS`'ın kendi metnindeki *"rewriting one is
write_frame_prompt's job"* çelişkisi Madde 201'le ilgili ve **kararı bekleyenler** tablosunda
duruyor; bu madde akış metnini düzeltiyor, aracın metnini değil.

**Kelime tavanı:** bu adım da ~5 kelime kazandırıyor.

**Durum:** belgede · kodda değil

---

### 16 · Bir outfit girdisi **komple bir görünüm**, tek parça değil

İki metni birden değiştiriyor, çünkü tek karar: akışın 2. adımı *(12 numaranın üçüncü maddesi)* ve
`SDXL_PROMPT_RULES`'un 3. paragrafı.

**Eski**

```text
- Write a garment as its own entry with add_outfit the moment it is described.
```
```text
they are an outfit of their own, named after the garment rather than after whoever wears it
```

**Yeni**

```text
- Write each outfit as one entry with add_outfit the moment it is described: everything worn in that look, together.
```
```text
they are an outfit of their own, named after the clothes rather than after whoever wears it
```

**Aracın kendi metni zaten bunu söylüyordu** — çelişen taraf akış metniydi. `ADD_OUTFIT` *"a set of
clothes with a name"* diyor, `ADD_OUTFIT_TAGS`'in örneği tek parça değil bir görünüm
*(`white nightgown, lace trim, bare shoulders`)*, ve devamı *"One entry dresses one person; two
people dressed differently are two outfits."*

**`garment` yanlış okumayı besliyordu.** Kural cümlesi **adın ne olacağını** söylüyor — giyeni değil
giysiyi anlat — ama `garment` *tek parça* çağrıştırdığı için *"her parça ayrı girdi"* diye
okunabiliyordu. 12 numaranın maddesi de o okumayı taşıyordu. `clothes` kelimesi kuralı olduğu gibi
bırakıyor ve tek parça imasını kaldırıyor.

**Neden komple görünüm doğrusu** *(kullanıcı kararı, 9 Eylül)*: `build_character_prompts` *"one
prompt for every outfit"* diyor — girdi komple bir görünümse önizleme giyinik bir insan, parça
parçaysa yalnız ayakkabı giymiş bir insan. Ve bileşim yine mümkün: kare, karakteri **outfit
listesiyle** yazıyor *(`ADD_SCENE_CHARACTERS`)*, yani görünüm + aksesuar gerektiğinde birleşiyor.
Değişen şey varsayılan, kaybolan bir yetenek değil.

**Bedeli yazılıyor:** aynı ceket üç görünümde geçiyorsa üç girdide tekrarlanır, ve düzeltmesi üç
`update_outfit` çağrısı olur. Parça parça tasarımda tek çağrıydı — *"one change reaches every frame
naming it"* kazancı burada daralıyor.

**D satırı bundan etkilenmiyor:** `white nightgown` örneğinin sorunu Danbooru'nun etiketi bölme
biçimi, girdinin kapsamı değil.

**Durum:** belgede · kodda değil

---

### 17 · `START_A_SCENARIO` — karaktere isim uydurulmaz, betimleyici İngilizce ad konur

Yalnız karakterler. Kıyafet ve mekân adlarına dokunulmadı *(kullanıcı kararı, 9 Eylül)*: örnekleri
zaten betimleyici — `nightgown`, `bedroom` — ve üçünü tek kurala bağlamak, bir karakter sorununu
üç haritaya yayıyordu.

**Eski** *(akışın 2. adımı, ve `ADD_CHARACTER_NAME`'in örneği)*

```text
- Write each character in with add_character.
```
```text
What this character is called in this scenario, as in aylin. Frames name them by it.
```

**Yeni**

```text
- Write each character in with add_character, named as the user named them or, where they did not, in English for what they are -- young man, bartender.
```
```text
What this character is called in this scenario, as in young man. Frames name them by it.
```

**Neden** *(kullanıcı kararı, 9 Eylül)*: kullanıcı bir ad vermediyse model bir ad **uyduruyor**, ve o
ad dosyanın anahtarı olarak kalıyor — kullanıcının hiç söylemediği bir kişi adı, her karede ve her
düzeltmede karşısına çıkıyor. Betimleyici bir ad hem kullanıcının söylediği şeyin kendisi, hem de
sonradan okununca kimden bahsedildiği belli.

**Kural akışta duruyor,** çünkü adı veren şey akışı koşan ajanın kendi kararı, ve o karar bu adımda
bir kez veriliyor. `ADD_CHARACTER_NAME`'de yalnız **örnek** değişti: `aylin` bir kişi adıydı ve
kuralın tersini gösteriyordu, `young man` ise onu gösteriyor. Kural cümlesi oraya kopyalanmadı —
12 numaradan beri aynı şey iki metinde durmuyor.

**Kullanıcının verdiği ad öncelikli:** yasak ad değil, **uydurma**. Kullanıcı *"adı Aylin"* dediyse
ad Aylin'dir.

**İngilizce, ve yalnız burada:** ad görüntü modeline gitmiyor *(`build_prompts` haritadaki etiketleri
birleştiriyor, anahtarı değil)*, ama dosyanın geri kalanı İngilizce ve `pov_` öneki de öyle — ad
Türkçe olunca haritalar iki dile bölünüyor.

**Kelime tavanı:** ~21 kelime biniyor.

**Durum:** belgede · kodda değil

---

### 18 · `START_A_SCENARIO` — 2. adım `build_character_prompts` teklifini bırakır

**Kaldırılan madde**

```text
- Offer build_character_prompts as a look at one character on its own; carry on if they decline.
```

**Neden** *(kullanıcı kararı, 9 Eylül)*: akışın işi beş adımı yürütmek, ve bu madde adımın ortasına
**işin gerektirmediği** bir soru koyuyordu — kabul edilse de edilmese de senaryo aynı yerde kalıyor.
Her adım zaten bir onay bekliyor; araya bir teklif daha girince adım iki soruyla uzuyor.

**Araç duruyor, ve ne zaman çağrılacağını kendi metni söylüyor:** `BUILD_CHARACTER_PROMPTS`
*"Reach for it when the user wants to look at one character on its own, before any frame"* diyor.
Yani kullanıcı isterse yol açık; akışın onu teklif etmesi gerekmiyor.

**Kelime tavanı:** ~15 kelime kazandırıyor.

**Durum:** belgede · kodda değil

---

### 19 · `EDIT_PROMPTS` — arıza tablosu madde madde, ve fiilleri yerine gelir

**Eski** *(rol paragrafından sonrası)*

```text
Read the file the complaint is about; with several, ask which. Where the fault lives is what decides the fix.

One frame's action reads wrong: correct it yourself with update_frame. A line wanted afresh from the scene is write_frame_prompt again, with a note.

Somebody looks wrong, or a place does, wherever they appear: that is their entry -- update_character, update_outfit or update_location -- and one change reaches every frame naming it.

Who is in a frame, what they wear or where it happens: update_frame. A frame seen through somebody's own eyes names their pov_ entry instead of them, because their whole entry would be drawn onto whoever the picture holds.

Then build_prompts again. The prompt file is rebuilt rather than patched. The built file is the answer: its prompts are never printed back.
```

**Yeni**

```text
Read the file the complaint is about. If there is more than one, ask which. Where the fault lives is what decides the fix:
- A frame's action reads wrong: correct it with update_frame, or call write_frame_prompt again with a note to have it rewritten from the scene.
- Somebody looks wrong, or a place does, wherever they appear: change their entry with update_character, update_outfit or update_location -- one change reaches every frame naming it.
- Who is in a frame, what they wear, or where it happens: change it with update_frame. A frame seen through somebody's own eyes names their pov_ entry instead of them, because their whole entry would be drawn onto whoever the picture holds.

Then call build_prompts again -- the file is rebuilt rather than patched -- and do not print its prompts back.
```

**Bu metin bir sıra değil, bir arıza tablosu:** belirti → hatanın yeri → araç. Üç durum zaten
belirtiyle açılıyordu, yani düzeni vardı; madde hâline gelince model doğru satırı **tararken**
buluyor. Akıştaki kadar büyük bir kazanç değil, ve kayda öyle geçiyor — 7 numaradaki gibi ölçülmüş
değil. Rol paragrafı prose kaldı *(Madde 123)*.

**Asıl düzelen şey fiiller.** Üç satır da modele iş vermiyordu: *"Who is in a frame … : update_frame"*
fiilsizdi *(13 numarada düşen `add_location, the same loop` ile aynı yapı)*, *"that is their entry"*
tespitti *(6 ve 12)*, ve *"A line wanted afresh from the scene is write_frame_prompt again"*ın öznesi
bir isim öbeğiydi. Üçü de emir kipine geçti.

**`with several, ask which` gitti** — 10 numarada aynen düzeltilen ifade, burada da duruyordu.

**Kapanış tek cümle oldu:** *"the built file is the answer"* ile *"its prompts are never printed
back"* aynı şeyin iki söylenişiydi; yasak kaldı, tarif düştü.

**B ve C satırları bu metinle çelişmiyor, onlar eskimiş:** düzeltmenin `update_frame`, yeniden
yazımın `write_frame_prompt` olduğunu **doğru söyleyen** metin bu. Kalan iş `WRITE_FRAME_PROMPT` ile
`WRITE_MISSING_ACTIONS`'ın kendi cümlelerini buna uydurmak, ve o iki satır tabloda duruyor.

**Kelime tavanı:** bu metin tavana yakın — ~190, tavan **200**. Yeni hâl kabaca başa baş: madde
başlarının ve `If there is more than one` cümlesinin eklediğini kapanış ile ikinci madde geri
veriyor.

**Ölçüm yanlıştı, ve 20 numara düzeltiyor.** Elle sayınca eski metin tam **200**, bu hâli **~205**
çıkıyor — yani kodda olsa `test_the_texts_stay_short_enough_to_be_read` kırmızı verirdi. Ayrıca iki
testin tuttuğu cümle düşmüştü: `"yourself"` *(Madde 201'in testi)* ve `"The built file is the
answer"` *(Madde 130'un testi)*. Maddenin biçim ve fiil gerekçeleri duruyor, düzenlemesi 20'de
yeniden yazıldı.

**Durum:** belgede · **20 tarafından değiştirildi**

---

### 20 · `EDIT_PROMPTS` — akışla aynı adım formatı, ve tavan 260'a çıkar

19 numara metni madde madde yaptı ama tek bloktu; bu, akışın **adım** biçimine geçiriyor
*(kullanıcı kararı, 10 Eylül)*: önce doğru kareyi bul, sonra düzelt, sonra kullanıcıya söyle.

**Yeni** *(metnin tamamı)*

```text
You are an expert SDXL prompt writer, and what you fix already exists: a scenario's prompts, one frozen frame each, and something in them is wrong. Do not assemble or patch a prompt by hand: the code builds every prompt from the entries in the structure file.

Step 1 -- what the complaint is about
- Read the scenario file the complaint names. If more than one could be it, ask which.
- Find what the user means: the frames, the person, the place or the outfit they are unhappy with. If nothing matches, say so; where something close is there, ask whether that is the one.

Step 2 -- the fix
- A frame's action reads wrong: correct it yourself with update_frame. For a line written afresh from the scene, call write_frame_prompt again with a note.
- Somebody looks wrong, or a place does, wherever they appear: change their entry with update_character, update_outfit or update_location -- one change reaches every frame naming it.
- Who is in a frame, what they wear, or where it happens: update_frame, once for each frame the complaint reaches.
- A frame seen through somebody's own eyes names their pov_ entry instead of them, because their whole entry would be drawn onto whoever the picture holds.

Step 3 -- the answer
- Call build_prompts again: the prompt file is rebuilt rather than patched.
- Say what you changed and which frames it reached. The built file is the answer: its prompts are never printed back.
```

**Eksik olan aşama arama aşamasıydı** *(kullanıcı, 10 Eylül)*: metin *"şikâyetin olduğu dosyayı
oku"* diyordu, ama kullanıcının hangi kareden bahsettiğini **bulmayı** hiç söylemiyordu. Model
şikâyeti eşleştiremeyince ya rastgele bir kareyi düzeltir ya da soruyu hiç sormaz. 1. adım şimdi
üç şeyi ayırıyor: bulunursa düzelt, benzeri varsa *"bu mu?"* diye sor, hiçbiri yoksa bulamadığını
söyle — seçmek modelin işi değil.

**Şikâyet tek kareyle sınırlı değil** *(kullanıcı, 10 Eylül)*: *"şu adamı bazı karelerden çıkar"*
gibi bir istek yapı dosyasında birden çok kareye dokunuyor, ve `update_frame` kareyi numarasıyla
alıyor — yani çağrı kare başına. 2. adımın üçüncü maddesi bunu açıkça söylüyor.

**3. adım yeni:** *"ne değiştiğini kullanıcıya söyle"*. Taban metin *"ne yaptığını söyle"* diyor
ama hangi karelere dokunulduğu bu işin kendine ait bilgisi, ve kullanıcı prompt dosyasını açmadan
görebileceği tek yer orası.

**Tavan 200'den 260'a çıktı** *(kullanıcı kararı, 10 Eylül)*. Madde 186 tavanı 300'den 200'e
indirmişti, gerekçesi *"bu metin işinin yarısını akışa verdi"*; şimdi geri aldığı şey bir iş
değil, **biçim**: üç adım başlığı, arama aşaması ve kullanıcıya söyleme adımı eskisinde yoktu.
Yeni metin elle sayıldığında **~251**, yani tavanın dokuz kelime altında. Kodda
`test_the_texts_stay_short_enough_to_be_read`'in `_edit()` satırı 200'den 260'a çekilecek — akışın
450'si **değişmiyor**.

**Testlerin tuttuğu cümleler yerinde:** `yourself`, `write_frame_prompt` + `note`,
`rebuilt rather than patched`, `build_prompts again`, `pov_`, `do not assemble`, `already`,
`wrong`, ve `The built file is the answer` + `never printed back`. `start_scenario`, `add_scene`
ve şema anahtarları metne girmedi.

**Rol paragrafı kısaldı:** *"prompts for an SDXL-family image model"* açıklaması düştü — açılış
cümlesi zaten *"expert SDXL prompt writer"* diyor — ve yapı dosyasını anlatan cümle tek cümleye
indi. Kazanılan yer adımlara gitti.

**Durum:** belgede · kodda değil

---

### 21 · `EDIT_PROMPTS` — iş bir hata değil, bir değişiklik isteği

**Eski** *(20'nin açılışı, ve `complaint` geçen üç yer)*

```text
... a scenario's prompts, one frozen frame each, and something in them is wrong.
Step 1 -- what the complaint is about
- Read the scenario file the complaint names. ...
- ... once for each frame the complaint reaches.
```

**Yeni**

```text
... a scenario's prompts, one frozen frame each, and the user wants something in them changed.
Step 1 -- what the request is about
- Read the scenario file the request names. ...
- ... once for each frame the request reaches.
```

**Neden** *(kullanıcı, 10 Eylül)*: `wrong` ile `complaint` bu skill'in işini **hataya** daraltıyordu.
Oysa gelen istek çoğu zaman hata değil: *"bu sahnede gecelik yerine elbise olsun"* düzgün yazılmış
bir kareyi değiştirmek. Dar okuyan model *"burada yanlış bir şey yok"* deyip işi geri çevirebilir,
ya da olmayan bir hata arar.

**`wrong` metinden düşmedi:** 2. adımın kendisi hatayı anlatan üç maddeyle açılıyor
*(`reads wrong`, `looks wrong`)*, yani `test_the_editor_starts_from_a_complaint_rather_than_a_blank_page`'in
aradığı kelime yerinde. Değişen şey **ön kabul**: iş hata olabilir de olmayabilir de.

**`one frozen frame each` duruyor** *(kullanıcı sordu, 10 Eylül)*: Madde 201'den beri bir aksiyon
satırını **editörün kendisi** düzeltiyor, ve kareyi yazan modelin kendi promptu *(donmuş an kuralı
orada)* besteciye hiç gitmiyor. Yani düzeltilen satırın bir hareket dizisi değil tek bir an olduğunu
söyleyen tek yer bu dört kelime.

**Kelime tavanı:** ~2 kelime biniyor, toplam ~253 — tavan 260.

**Durum:** belgede · **22 tarafından yeniden yazıldı** *(rol paragrafı)*

---

### 22 · `EDIT_PROMPTS` — rol paragrafı kısa cümlelere bölünür

**Eski**

```text
You are an expert SDXL prompt writer, and what you fix already exists: a scenario's prompts, one frozen frame each, and the user wants something in them changed. Do not assemble or patch a prompt by hand: the code builds every prompt from the entries in the structure file.
```

**Yeni**

```text
You are an expert SDXL prompt writer. The prompts you work on are already written: one per frame, each one a frozen moment. The user wants something in them changed. Do not assemble or patch a prompt by hand -- the code builds them from the characters, outfits and locations in the structure file.
```

**Neden** *(kullanıcı, 10 Eylül)*: ilk cümle tek nefeste dört şey söylüyordu — rol, promptların
var olduğu, karenin ne olduğu, ve kullanıcının bir değişiklik istediği. Dördü dört cümle oldu.

**Öznesi somutlaştı:** *"what you fix already exists"* soyut bir özne — 6 numarada aynı kusur
düzeltilmişti. *"The prompts you work on are already written"* aynı şeyi söylüyor ve öznesi
metinde duran bir şey.

**Donmuş an kendi cümlesine çıktı:** eskisinde `one frozen frame each` promptların arkasına
iliştirilmiş bir ek öbekti; zayıf modelin en kolay atladığı yapı. Şimdi `each one a frozen moment`
diye kendi yargısında.

**`the entries` adlarıyla anıldı:** *"entries"* hangi girdiler olduğunu söylemiyordu; artık
`characters, outfits and locations` diyor — 3 numaranın dersi, işaret edilen şey adıyla anılır.

**Testlerin tuttuğu şeyler yerinde:** metin hâlâ `You are an expert SDXL prompt writer` ile
başlıyor, `already` ve `do not assemble` duruyor.

**Kelime tavanı:** ~4 kelime biniyor, toplam ~257 — tavan 260.

**Durum:** belgede · rol paragrafı **23'te bir kez daha kısaldı**

---

### 23 · `EDIT_PROMPTS` — rol paragrafından `frozen moment` çıkar

**Eski**

```text
The prompts you work on are already written: one per frame, each one a frozen moment.
```

**Yeni**

```text
The prompts you work on are already written: one per frame.
```

**Neden** *(kullanıcı kararı, 10 Eylül)*: cümle **bütün promptlar** hakkında konuşuyor, oysa donmuş
an yalnız **karenin aksiyon satırı** için doğru. Karakterin, kıyafetin ve mekânın girdisi bir an
değil, bir tarif — ve `build_character_prompts`'ın yazdığı önizleme promptu da bir kare değil.
Genel bir cümle olarak yanlış yere oturuyordu.

**Kuralın kendisi açıkta kaldı, ve kayda öyle geçiyor:** 21 numara bu dört kelimeyi *"düzeltilen bir
aksiyon satırının tek bir an olduğunu söyleyen tek yer"* diye tutmuştu. Kareyi yazan modelin kendi
promptunda kural duruyor ama o metin editöre gitmiyor, ve `UPDATE_FRAME`'in kendi tarifi yalnız
*"a line that reads wrong is corrected here, in your own words"* diyor.

**Düzeltme *(10 Eylül, F satırı okunurken)*:** *"tek yer"* değilmiş. `action` alanının kendi tarifi
— `UPDATE_FRAME_ACTION` — *"What is happening in this **frozen instant** and the shot it is seen
through"* diyor, ve editör o alanı her doldurduğunda onu okuyor. 26 numaranın envanteri de bunu
zaten sayıyordu. Yani açıkta kalan **sıfat değil, sıfatın taşıdığı kural**: 26 numaranın bulgusu
burada birebir geçerli — `frozen` bir sıfat, ve *"model tek resim çiziyor, birkaç ana yayılan bir
satır çizilemiyor"* cümlesini hiç söylemiyor.

**Karar: sıfat yetiyor** *(kullanıcı kararı, 10 Eylül)*. `UPDATE_FRAME_ACTION` olduğu gibi kalıyor,
`EDIT_PROMPTS`'a da bir şey eklenmiyor — editörün metni şu hâliyle iyi. F satırı bu kararla kapandı.
26 numaranın öteki iki metni *(`START_A_SCENARIO`, `WRITE_FRAME_PROMPT`)* de aynı sebeple açılmadı.

**Kelime tavanı:** ~5 kelime kazandırıyor, toplam ~252.

**Durum:** belgede · kodda değil

---

### 24 · `EDIT_PROMPTS` — yasak yerine tarif: elle prompt yazma kuralı

**Eski**

```text
Do not assemble or patch a prompt by hand -- the code builds them from the characters, outfits and locations in the structure file.
```

**Yeni**

```text
The code builds every prompt from the structure file -- its characters, outfits, locations and frames -- so make your change there.
```

**Neden** *(kullanıcı, 10 Eylül)*: 6 numaranın kuralı burada uygulanmamıştı — *"yanlış şekil üreten
bir modelde yasak biçimi pazarlığa açık, tarif eden biçim değil"*. Eski cümle **yapmayacağı şeyi**
söylüyor ve doğru yolu ancak ima ediyordu; yenisi mekanizmayı söylüyor ve sonunda **yapılacak
şeyi**: `make your change there`.

**`frames` de sayıldı:** eski cümle üç haritayı anıyordu, oysa aksiyon satırı ve kadro **karenin
kendisinde**. Editörün en sık dokunduğu yer sayılmıyordu.

**Bir test bu maddeyle değişecek:** `test_the_editor_forbids_assembling_a_prompt_by_hand`
`"do not assemble"` cümlesini birebir tutuyor, ve o cümle metinden kalktı. Testin yorumu
*"bu olmadan skill'i ayıran tek şey gider"* diyor, ve gitmiyor: kural duruyor, biçimi değişti. Kod
geçişinde testin tuttuğu şey **kuralın olumlu hâli** olacak — prompt'un koddan doğduğu ve
değişikliğin yapı dosyasına gittiği. Aynı testin `build_prompts` araması etkilenmiyor, o kelime
3. adımda duruyor.

**Kelime tavanı:** ~2 kelime kazandırıyor, toplam ~250.

**Durum:** belgede · kodda değil

---

### 25 · `WRITE_FRAME_SYSTEM_PROMPT` — dört paragraf yedi maddeye bölünür

**Eski:** dört paragraf, tam hâli
[belgenin §4'ünde](2026-09-09-queenagent-modele-giden-metinler.md) *(artık yeni hâliyle)*.

**Yeni** *(rol cümlesi + yedi madde)*

```text
You write the action line of one frozen frame, for an SDXL-family image model. You are handed a scene in one sentence, who is in the frame, and where.

- Answer with the action line and nothing else: no preamble, no quotes around it, and nothing about having written it.
- Write what is happening in this one frozen instant, and the shot it is seen through. There is no camera field, so the framing and the angle live inside your line -- close-up, from below, over the shoulder, wide shot.
- Give neighbouring frames of one scenario a framing and angle of their own, because the same framing twice is one picture twice.
- The body and the face are yours: what the body is doing in this instant, and the expression the face wears. Neither could live in a map, because the same person is calm in one frame and not in the next.
- Name what is visible of them rather than writing around it -- erect penis, penis penetrating vagina, mouth on penis -- because the model draws what is named and invents whatever a euphemism left out, which is how a frame comes back with a body that melts.
- Do not describe anybody's looks, their clothes or the place: those are written once in the file's own maps and the code puts them into every prompt already, so a second copy here is the one that contradicts the first.
- You are handed them so your line fits what is there -- somebody in a long coat does not shrug it off in your sentence, and somebody wearing no outfit is already bare without you saying so.
```

**Dört paragrafta altı kural iç içeydi:** çıktının biçimi, donmuş an + çekim, komşu karelerin ayrı
çekimi, harita sınırı, beden ile yüz, ve çıplaklığın kimin işi olduğu. 7 ve 9 numaranın gerekçesi
burada daha da güçlü: bu metnin okuyucusu **ayrı bir model** *(Madde 202'den beri DeepSeek)*, tek
işi var, ve kodun kendi yorumu *"en sade cümleleri alan taraf budur"* diyor.

**Sıra değişti, ve olumlu olan öne geçti.** Eskisinde önce *"şunları yazma"* geliyordu, *"şunlar
senin"* sonra. Şimdi beden ile yüz maddesi sınırdan **önce** duruyor — Deneme 4'ün hatası zaten
modelin kendi payını yazmaktan çekinmesiydi.

**Çıktı biçimi olumluya döndü:** *"you answer with the action line alone: no preamble, no
explanation, no quotes…"* dört yasaktı; `Answer with the action line and nothing else` bir emir, ve
arkasındaki iki örnek gözlenmiş sızıntılar olduğu için duruyor. `no explanation` düştü: `nothing
else` onu zaten kapsıyor.

**Kıyafet/görünüş/mekân kuralı bilerek yasak kaldı** *(6 numaranın istisnası)*: bu bir **sınır**, ve
hata biçimi eksik yazmak değil **fazla** yazmak — o kuralın doğal şekli yasaktır. Olumlu ikizi
zaten bir üstteki maddede duruyor.

**Hiçbir test kırılmıyor.** Bu metnin her cümlesi bir teste bağlı ve hepsi yerinde:
`framing and angle`, `action`, `camera`, `name what is visible`, `penis` ve `vagina`, `euphemism`,
`expression`, `already bare`, `do not describe` + `clothes`. Cümleler yeniden yazılmadı — sırası ve
biçimi değişti. 24 numaradan farkı bu.

**Kelime tavanı yok:** tavanı tutan test yalnız akış ile düzeltme metnini ölçüyor. Yine de metin
uzamadı; `no explanation` ve tekrar eden bir yan cümle düştü.

**Durum:** belgede · kodda değil

---

### 26 · `WRITE_FRAME_SYSTEM_PROMPT` — `frozen` sıfatı yerine kuralın kendisi

**Eski**

```text
- Write what is happening in this one frozen instant, and the shot it is seen through. There is no camera field, so ...
```

**Yeni**

```text
- Write what is happening in one single moment: the model draws one picture, and a line that runs through several moments cannot be drawn at all.
- The shot is yours as well. There is no camera field, so the framing and the angle live inside your line -- close-up, from below, over the shoulder, wide shot.
```

Rol cümlesi `one frozen frame` diye **duruyor**.

**Kelime silinmedi, kural eklendi** *(kullanıcı kararı, 10 Eylül)*. İlk yazımda `frozen` rol
cümlesinden de çıkarılmıştı; geri kondu, çünkü orada bir sıfat değil **birimin adı**: beş metin
aynı şeyi aynı kelimeyle anıyor, ve ortak terim modelin aynı istekte okuduğu metinleri birbirine
bağlamasının yolu. 23 numaranın `EDIT_PROMPTS`'tan çıkarma sebebi burada geçerli değil — orada
cümle bütün promptlar için konuşuyordu, burada üretilen her şey zaten bir kare.

**Neden kural yazıldı** *(kullanıcı sordu, 10 Eylül)*: `frozen` bir **sıfat**, ve taşıdığı kuralı
hiç söylemiyor.
Kural şu: model tek bir resim çiziyor, yani *"içeri girer, oturur ve gülümser"* gibi birkaç ana
yayılan bir satır çizilemiyor — model onu ortalıyor, ve Deneme 4'te eriyen gövdeler böyle geldi.
Sıfatı okuyan modelin bu sonucu kendi çıkarması gerekiyordu; artık cümle söylüyor.

**Videoyla ilgisi yok, ve olsa bile tersini gerektirmiyor:** kare sonradan i2v ile videoya
dönüyor, ve o model **tek bir başlangıç karesinden** gidiyor — bulanık bir "orta an" kötü bir
başlangıç karesi demek. Yani tek an kuralı video yüzünden gevşemiyor, sıkılaşıyor.

**İki kural ayrıldı:** eski cümle *"şu anda ne oluyor"* ile *"hangi çekimden görünüyor"*u tek
yargıda taşıyordu. İkisi ayrı iş, ve ikincisi kendi maddesine çıktı.

**Aynı sıfat üç metinde daha duruyor:** `START_A_SCENARIO`'nun açılışı *(`one frozen frame at a
time`)*, `UPDATE_FRAME_ACTION` ve `WRITE_FRAME_PROMPT`. Kararı buraya yazıldı, o üçüne
uygulanmadı — ayrı bir madde.

**Durum:** belgede · kodda değil

---

### 27 · `WRITE_FRAME_SYSTEM_PROMPT` — çekim kelimeleri de etikettir

**Eski**

```text
- The shot is yours as well. There is no camera field, so the framing and the angle live inside your line -- close-up, from below, over the shoulder, wide shot.
```

**Yeni**

```text
- The shot is yours as well: there is no camera field, so the framing and the angle live inside your line, written as tags like everything else -- close-up, from below, from behind, wide shot.
```

**Neden** *(kullanıcı, 10 Eylül)*: madde çekimi *"satırının içinde yaşar"* diye anlatıyordu ama
**hangi biçimde** yazılacağını söylemiyordu. Model bunu serbest bir cümle parçası sanabilir, oysa
kare promptu baştan sona etiket. `written as tags like everything else` o boşluğu kapatıyor.

**Danbooru kuralı buraya kopyalanmadı:** `SDXL_PROMPT_RULES` bu promptun **sonuna ekleniyor** ve ilk
cümlesi *"trained on the tags of Danbooru, so a tag is one that vocabulary has rather than a
description"* diyor. Madde yalnız *"bunlar da etiket"* deyip o metne bağlanıyor — aynı kuralı iki
yerde söylemek bu koşunun kovaladığı şey.

**`over the shoulder` → `from behind`:** birincisinin Danbooru'da bir karşılığı olduğundan emin
değilim, ikincisininki var. D satırının tam olarak bu — kuralın kendisi *"sözlüğün etiketi"* derken
örneğin sözlükte olmaması. Doğrulanmadan bir örnek bırakmaktansa kesin olanı yazdım; kalan üç örnek
*(`close-up`, `from below`, `wide shot`)* aynı sebeple gözden geçirilmeli, ve o **G satırı**.

**Durum:** belgede · kodda değil

---

### 28 · `WRITE_FRAME_SYSTEM_PROMPT` — komşu kare maddesi düşer, çünkü uyulamıyor

**Eski**

```text
- Give neighbouring frames of one scenario a framing and angle of their own, because the same framing twice is one picture twice.
```

**Yeni:** madde tümüyle düşer, yedi madde altıya iner. Kalan altısına dokunulmadı.

**Neden** *(kullanıcı sordu, 10 Eylül)*: modelin bu kurala uyması **mümkün değil**. `_frame_seen`
writer'a yalnız o karenin sahnesini, kadrosunu, mekânını ve notunu veriyor — komşu karelerin
kadrajı orada yok. Her kare de ayrı bir `write_once`, yani daha önce ne yazdığının hafızası yok.
Model neyi tekrar etmemesi gerektiğini bilemiyor, ve bilemediği bir kural ona yalnız gürültü olarak
gidiyor.

**Kural yanlış değil, yeri yanlış.** Aynı kadrajın iki kez çıkması gerçek bir sorun; ama çözecek
taraf komşuların kadrajını **görebilen** taraf: ya `_frame_seen` onları da gösterir, ya kareyi
seçen model istediği kadrajı notta söyler. İkisi de kod işi ve ikisi de ayrı madde.

**Bir test bu maddeyle değişecek:** `test_the_craft_rules_left_the_texts_with_the_work`
`"framing and angle"` dizgesini tutuyor, ve o birebir dizge **yalnız bu maddede** geçiyor — çekim
maddesi *"the framing and the angle"* diyor. Kod geçişinde testin tutacağı şey `"framing"` olacak.
Testin asıl işi kuralın skill'lerde değil writer'ın kendi prompt'unda olması, ve o iş sürüyor.

**33 numaradan sonra bu gevşetme gereksiz:** yeniden yazım çekim maddesini *"write the framing and
angle into your line"* yaptı, yani birebir dizge metne geri döndü. Test olduğu gibi kalıyor.

**Bu koşuda bakılıp kesilmeyenler.** Metnin tamamı fazlalık için okundu; kalanların hepsinin
kayıtta bir sebebi çıktı:

| Aday | Neden kaldı |
|---|---|
| `already bare` | Bir tekrarı değil **sahipliği** yasaklıyor: kod kıyafetsiz kadro için hiçbir etiket yazmıyor, yani çıplaklık kadronun işi *(5 Eylül kararı, `test_being_bare_is_the_casts_doing_and_not_the_writers`)*. |
| Tek an maddesi | 26 numaranın kendisi. `frozen` bir sıfat, kuralı söyleyen cümle bu. |
| `written as tags like everything else` | 27 numaranın kendisi. |
| `no preamble`, `no quotes` | Gözlenmiş sızıntılar *(25 numara)*. |
| Gerekçe yan cümleleri | *"Sebebi yazılı bir kural, kimsenin saymadığı bir duruma da uygulanır"* — `test_the_writer_is_told_why_a_euphemism_costs_something`. |

**Durum:** belgede · kodda değil

---

### 29 · `SYSTEM_PROMPT` — planı hangi aracın yazdığı kipe bağlanır

**Eski**

```text
A job of several steps starts with write_plan: the plan is where the work keeps its place, and a fresh chat picks it up from the step left open.
```

**Yeni**

```text
A job of several steps starts with a plan file: the plan is where the work keeps its place, and a fresh chat picks it up from the step left open. In plan mode write_plan writes it; in any other mode create_file does.
```

**Neden** *(kullanıcı kararı, 10 Eylül)*: 10 numara akışın 1. adımını `create_file`'a çevirdi ama
taban metnine dokunmadı, ve aynı istekte duran iki metin aynı işi iki ayrı araca veriyordu
*(§8'in 5. maddesi)*. Karar: cümle silinmiyor, **koşulu yazılıyor**.

**Bu bir kip meselesi, ve tabloda öyle yazmıyordu.** `modes.py` plan kipinde `create_file`'ı onaya
bağlıyor, `write_plan`'i bağlamıyor *(`test_plan_mode_writes_a_plan_without_asking_and_asks_for_the_rest`)*.
Sebebi testin kendi yorumunda: `create_file` verilirse model planı ve işin kendisini aynı turda
yazabilir, ki bu planlamak değil işi yapmaktır. Yani taban metnindeki `write_plan` süs değil —
plan kipindeki **skill'siz** bir sohbetin planını yazabilmesi ona bağlı, ve araç adını tümüyle
atmak *(§8'in andığı "araçsız yazım")* o sohbeti onay kapısına çarptırırdı.

**`create_file` de anılıyor:** koşul yalnız plan kipini söyleseydi cümlede *"öteki kiplerde ne
yazıyor"* boşluğu kalırdı. Akış kendi metninde zaten `create_file` diyor, ama taban metni tam da
**akışsız** sohbet için var.

**10 numaranın gerekçesiyle çelişmiyor:** orada akış metni kalkacak araçlara yaslanmasın denmişti ve
203 `mark_step_done`'ı kaldırıyor. `write_plan` kalkmıyor — 10 numaranın kendi satırı *"write_plan
aracı duruyor: bu bir metin kararı, kip kararı değil"* diyor.

**Hiçbir test kırılmıyor:** `test_the_base_starts_a_long_job_with_the_plan` `"write_plan"` ile
`"keeps its place"` tutuyor, ikisi de cümlede duruyor.

**Kelime tavanı yok:** tavanı tutan test yalnız akış ile düzeltme metnini ölçüyor. Cümle ~7 kelime
uzadı.

**Bu kayıt geçersiz kılındı** *(10 Eylül, aynı gün)*: **Madde 207** `write_plan` aracını
kaldırıyor, yani cümlenin ayırdığı iki yol tek yola iniyor. Kod geçişi bu kaydın hâlini değil,
207'nin bıraktığı hâli indirir — *"A job of several steps starts with a plan file… create_file
writes it."* Buradaki gerekçe yine de duruyor: plan kipinde `create_file`'ın kapıya takılmaması
gerektiğini söyleyen şey buydu, ve 207 onu kipin listesine taşıyarak çözüyor.

**Durum:** belgede · kodda değil · **207 geçersiz kıldı**

---

### 30 · Bütün metinlerden etiket örnekleri kalkar

**Neden** *(kullanıcı kararı, 10 Eylül)*: bekleyen kararlarda üç satır aynı şeyi söylüyordu — **A**
*(`1girl, woman in her mid 20s` bir tarif)*, **D** *(`white nightgown` Danbooru'da yok)*, **G**
*(çekim örnekleri doğrulanmadı)*. Üçü de örneğin **yanlış** olduğunu söylüyor, ve doğrusunu bulmak
Danbooru'ya bakmayı gerektiriyor. Karar örnekleri tek tek düzeltmek değil: **şimdilik hiç örnek
olmasın.** Kural yerinde kalıyor, modeli yanlış yöne çeken örnek kalmıyor.

**Kalkanlar** — sekiz yer, beş metin. Her birinde yalnız örnek kalkıyor, kuralı taşıyan cümle
olduğu gibi duruyor:

| Metin | Kalkan | Kalan |
|---|---|---|
| `SDXL_PROMPT_RULES` 1. paragraf | ` -- looking at viewer, sitting, couch, window` | `…rather than a description of the same thing.` |
| `SDXL_PROMPT_RULES` 1. paragraf | `: long hair, black hair, green eyes` | `…divided the way the vocabulary divides it.` |
| `SDXL_PROMPT_RULES` 2. paragraf | ` -- 1girl, woman in her mid 20s -- ` | `…belongs in that entry and nowhere else, because…` *(A)* |
| `WRITE_FRAME_SYSTEM_PROMPT` | ` -- close-up, from below, from behind, wide shot` | `…written as tags like everything else.` *(G)* |
| `ADD_CHARACTER_TAGS` | `As in 1girl, mature female, long hair, black hair, green eyes, narrow waist.` | `…their age, body, hair and face. No clothes here -- those are outfits.` |
| `ADD_OUTFIT_TAGS` | `: white nightgown, lace trim, bare shoulders` | `The clothes as tags, and nothing else.` *(D)* |
| `ADD_LOCATION_TAGS` | `: bedroom, indoors, curtains, sunlight, window` | `The place as tags. Nobody is in it…` |
| `START_A_SCENARIO` 2. adım | ` -- young man, bartender` | `…in English for what they are.` |

**Kalanlar, ve neden kaldıkları:**

| Kalan | Sebep |
|---|---|
| `erect penis, penis penetrating vagina, mouth on penis` | Kullanıcı kararı. Bedeli ölçülmüş: Deneme 4'te ilkeyi bilen model yine etrafından dolaştı ve yirmi kare elle düzeltildi. |
| `as in notes.md`, `as in bar-scene`, `as in aylin`, `as in nightgown`, `as in bedroom`, `as in cowgirl` | Bunlar prompt değil, **dosya ve girdi adı** örneği. Karar prompt örnekleri hakkında. |
| `- [ ] 1.` | Biçim tarifi, örnek değil. |
| §7'nin hazır parçaları | Depoda duran **veri**, metnin içindeki örnek değil. |

**Beş test bu maddeyle değişecek** *(liste 10 Eylül'de üçten beşe çıkarıldı: ilk taraması yalnız
`_rules()` yardımcısı üzerinden koşan testleri görmüş, sabiti doğrudan `import` eden ikisini
kaçırmıştı)*:

| Test | Ne olacak |
|---|---|
| `test_the_rules_put_the_count_in_the_characters_own_entry` | `"1girl"` iddiası düşer, `"count"` kalır — kural yerinde duruyor |
| `test_the_count_rule_the_exception_is_carved_out_of_is_still_there` | `"1girl"` iddiası düşer, `"the one place a count lands"` kalır — istisnanın oyduğu kural o cümle |
| `test_the_rules_split_a_tag_into_the_tags_the_vocabulary_has` | `"long hair, black hair"` iddiası düşer; yerine kuralın cümlesi tutulur, ve `"long black hair" not in` olduğu gibi kalır |
| `test_the_character_example_is_written_in_that_vocabulary` | Tuttuğu tek şey örnekti; **silinir** |
| `test_the_place_example_is_written_in_that_vocabulary` | Aynısı; **silinir** |

`ADD_OUTFIT_TAGS`'in örneği, 1. paragraftaki `looking at viewer…` dizisi, çekim örnekleri ve
`young man, bartender` hiçbir teste bağlı değil.

**Bunun bedeli yazılıyor:** silinen iki testin yorumu örneklerden yana — *"Örnekler kuraldan daha
dikkatli okunuyor: modelin bir girdinin gerçekte neye benzediğini gördüğü tek yer burası."* Karar
bunu bilerek veriyor, ve anatomi listesi tam bu sebeple kapsam dışında bırakıldı: orada örneğin
değeri bir denemeyle ölçülmüştü, ötekilerde ölçülmedi.

**Kelime tavanı:** akış metni ~3 kelime kazanıyor; ötekilerin tavanı yok.

**Durum:** belgede · kodda değil

---

### 31 · `WRITE_FRAME_PROMPT` — yeniden yazmak ile düzeltmek ayrılır

**Eski**

```text
Written over whatever was there, so calling this again on the same frame is how an action is changed -- with a note when there is something to fix, and the note is the whole of what the writer hears about it. One frame per call.
```

**Yeni**

```text
Written over whatever was there, so calling this again on the same frame writes the line afresh from the scene -- with a note when there is something to fix, and the note is the whole of what the writer hears about it. A line that only reads wrong is corrected with update_frame instead. One frame per call.
```

**Neden** *(kullanıcı kararı, 10 Eylül; tabloda B satırıydı)*: Madde 201 bir satırı **düzeltmeyi**
`update_frame`'e verdi, `write_frame_prompt`'a ise satırı **sahneden yeniden yazmak** kaldı. Tarif
bu ayrımı bilmiyordu ve hâlâ *"değiştirmenin yolu benim"* diyordu — iki metin aynı soruya iki cevap.

**Ayrımın doğru hâli zaten yazılı:** `EDIT_PROMPTS`'un 2. adımının ilk maddesi *"correct it yourself
with update_frame. For a line written afresh from the scene, call write_frame_prompt again with a
note"* diyor. Tarif ona hizalandı, tersi değil — `_write_frame_prompt`'un kendi yorumu da aynı
ayrımı yazıyor.

**Hiçbir test kırılmıyor:** bu cümleye bağlı test yok.

**Durum:** belgede · kodda değil

---

### 32 · `WRITE_MISSING_ACTIONS` — aynı ayrımın ikinci kopyası

**Eski**

```text
Frames that already have an action are left exactly as they are -- rewriting one is write_frame_prompt's job, with a note.
```

**Yeni**

```text
Frames that already have an action are left exactly as they are -- writing one afresh is write_frame_prompt's job, with a note, and correcting a line that reads wrong is update_frame's.
```

**Neden** *(tabloda C satırıydı)*: 31 numaranın cümlesinin ikinci kopyası, aynı sebeple ve aynı
şekilde düzeliyor. İki tarif tek bir ayrımı anlatıyor, ve ikisi de artık aynı şeyi söylüyor.

**Hiçbir test kırılmıyor.**

**Durum:** belgede · kodda değil

---

### 33 · `WRITE_FRAME_SYSTEM_PROMPT` — metnin tamamı sade İngilizceyle yeniden yazılır

**Eski** *(30 numaradan sonraki hâli, yedi madde)*

```text
You write the action line of one frozen frame, for an SDXL-family image model. You are handed a scene in one sentence, who is in the frame, and where.

- Answer with the action line and nothing else: no preamble, no quotes around it, and nothing about having written it.
- Write what is happening in one single moment: the model draws one picture, and a line that runs through several moments cannot be drawn at all.
- The shot is yours as well: there is no camera field, so the framing and the angle live inside your line, written as tags like everything else.
- The body and the face are yours: what the body is doing in this instant, and the expression the face wears. Neither could live in a map, because the same person is calm in one frame and not in the next.
- Name what is visible of them rather than writing around it -- erect penis, penis penetrating vagina, mouth on penis -- because the model draws what is named and invents whatever a euphemism left out, which is how a frame comes back with a body that melts.
- Do not describe anybody's looks, their clothes or the place: those are written once in the file's own maps and the code puts them into every prompt already, so a second copy here is the one that contradicts the first.
- You are handed them so your line fits what is there -- somebody in a long coat does not shrug it off in your sentence, and somebody wearing no outfit is already bare without you saying so.
```

**Yeni** — [belgenin §4'ünde](2026-09-09-queenagent-modele-giden-metinler.md), sekiz madde.

**Neden** *(kullanıcı kararı, 10 Eylül)*: metnin okuyucusu **küçük** bir model
*(`deepseek-v4-flash`, 202'den beri)* ve kodun kendi yorumu ondan *"en sade cümleleri alan taraf"*
diye söz ediyor. Cümleler o sadelikte değildi. **Hiçbir kural düşmedi** — biçim değişti.

**Beş şey değişti:**

| Ne | Neden |
|---|---|
| Emir başa, sebep arkaya ayrı cümleye | Kural bir yan cümlenin içindeydi: *"The shot is yours as well: there is no camera field, so…"*. Zayıf model önce ne yapacağını okumalı. |
| Mimari dili kalktı | *"Neither could live in a map"* — okuyan modelin `map` diye bir şeyden haberi yok. Yerine bildiği şey yazıldı: *"nothing else in the prompt says what this person is doing or feeling in this frame."* |
| Sahiplik deyimi kalktı | *"The body and the face are yours"* bir mülkiyet ifadesi, emir değil → *"Write what the body is doing…"* |
| Gözlem emre döndü | *"somebody wearing no outfit is already bare without you saying so"* bir tespit gibi duruyordu → *"Do not write that anybody is naked."* **Madde sayısı bu yüzden 7'den 8'e çıktı**: cümle kendi maddesini hak ediyor. |
| Belirsiz zamirler açıldı, `--` bölündü | *"those are written once in the file's own maps"* → *"Other text already puts all three into the prompt."* Uzun tire kuralı cümlenin ortasına gömüyordu. |

**Birinci madde ayrıca içerik kazandı** *(kullanıcı sordu, 10 Eylül: "bu chatte cevap verirken mi?")*.
Hayır — ve sorunun kendisi maddenin eksiğini gösterdi: **cevabın nereye gittiğini hiç
söylemiyordu.** Bu modelin sohbeti yok *(`engine.write_once`, tek istek; `_write_frame_prompt`'un
yorumu: "Nothing of the answer reaches the chat")*, ve `tools.py` cevabı yalnız `.strip()`'leyip
`frame["action"]`'a yazıyor. Tırnak, giriş cümlesi, *"işte satır:"* — hiçbiri temizlenmiyor. Madde
artık yasağı **sonucuyla** söylüyor: fazladan yazılan şey image prompt'unun içine giriyor.

**Kısalmadı, netleşti:** ~190 → ~200 kelime. Bir emir cümlesi, gömülü bir yan cümleden uzun; burada
istenen şey kısalık değil yanlış anlaşılmaması.

**Örnek eklenmedi** *(30 numaranın kararına uyularak)*. Küçük bir modelde en çok işe yarayan şey bir
karşıtlık örneği olurdu; 30 numara örnekleri kaldırdığı için yazılmadı. Anatomi listesi kendi
kararıyla duruyor.

**Hiçbir test kırılmıyor.** Bu metnin tuttuğu dizgeler bilerek korundu: `action`, `camera`, `shot`,
`framing and angle`, `name what is visible`, `penis`, `vagina`, `euphemism`, `expression`,
`already bare`, `do not describe`, `clothes`. Hepsi yeni metinde birebir geçiyor — 28 numaranın
`"framing and angle"` için öngördüğü gevşetme de artık gereksiz, dizge geri geldi.

**25–28 numaranın cümleleri artık yalnız log'da.** Belgedeki blok bu maddenin hâlidir; o dört kayıt
neyin neden değiştiğini anlatmaya devam ediyor ama metnin son hâli burasıdır.

**Durum:** belgede · kodda değil

---

### 34 · `SDXL_PROMPT_RULES` — dört paragraf sade İngilizceyle yeniden yazılır

33'ün aynısı, öteki metin için — ve bu kayıt iki şeyi birden tutuyor: cümlelerin **nasıl
yazıldığını**, ve **nerede duracaklarını**. İkincisi bir ara Madde 204 diye ayrı yazılmıştı, sonra
190'ın içine alındı *(kullanıcı kararı, 10 Eylül)*: bölme bir metin kararı, ve 190 zaten metinleri
okuyor. Numara [yol haritasında geri çekildi](superpowers/plans/2026-09-06-queenagent-v8-roadmap.md).

**Neden bölünüyor.** Metin altı araca birden ekleniyor — `add_character`, `update_character`,
`add_outfit`, `update_outfit`, `add_location`, `update_location` — ve dört paragrafının ikisi
**girdiye özgü**. Yani `add_location` her istekte karakter girdisinin sayı kuralını ve kıyafet
girdisinin adlandırma kuralını okuyor. `prompt.py`'nin kendi yorumu hem bedeli hem karşılığını
yazıyor: *"six copies is roughly a thousand tokens on every request… **the rule sits beside the
parameter it governs**."* 2. ve 3. paragraf o karşılığı vermiyor. Yedinci okuyucu olan kareyi yazan
model ise hiç girdi yazmıyor; ona da boşuna gidiyorlar.

**Kural sayısı değişmiyor, yeri değişiyor.** Altı kopya ödenen bir kural tek kopyaya iniyor, çünkü
her alan tarifi tek bir araca ait. Ortak metin ~285 kelimeden ~115'e; alan tariflerine eklenen ~200
kelime birer kez ödeniyor.

**Eski** *(30 numaradan sonraki hâli)*

```text
How to write the tags. They are read by an SDXL-family image model trained on the tags of Danbooru, so a tag is one that vocabulary has rather than a description of the same thing. They are English, written with spaces where the site writes underscores, and each carries one thing, divided the way the vocabulary divides it. Where it has no tag for it, a few plain words in the same shape -- an article is not a tag, and neither is a sentence.

How many people a character entry draws belongs in that entry and nowhere else, because that is the one place a count lands beside the person it counts. The word solo does not go there: the same character stands alone in one frame and beside somebody in the next, so an entry claiming it is wrong in half of them. An entry for somebody only part of the way into shot -- a pov_ one, hands and arms and no face -- carries no count at all, because there is no whole person in the picture to count.

Clothes are never in a character's entry; they are an outfit of their own, named after the clothes rather than after whoever wears it, because two characters can wear the same one. One entry dresses one person: its text is handed whole to whoever wears it, so one entry covering two people puts the man in the dress. A location has nobody in it and no count -- who is there is the frame's business, and a person written into a place is drawn into every frame set there.

No quality tags anywhere: code writes those at the front of every prompt, and yours would be printed twice. No or inside a value -- the model draws one picture and cannot toss a coin, so pick one.
```

**Yeni — ortak kalan** *(`SDXL_PROMPT_RULES`, altı araç ve kareyi yazan model)*

```text
An SDXL-family image model reads these tags, and it was trained on Danbooru's own tags.

- Write tags, never sentences. An article is not a tag either.
- Use a tag that the Danbooru vocabulary already has, rather than a description of the same thing. The model has seen a real tag many times, and has never seen a paraphrase of it.
- Write the tags in English, with spaces where the site writes underscores.
- Put one thing in each tag, split the way the vocabulary splits it. Do not join two tags into one longer phrase.
- When the vocabulary has no tag for it, write a few plain words in the same short form.
- Never write quality tags. The code already puts them at the front of every prompt, so yours would be printed twice.
- Never write the word or inside a tag. The model draws one picture and cannot toss a coin between two choices, so pick one and write only that.
```

**Yeni — alanlarına inenler** *(ortak metinden inen kurallar, aynı sadelikte)*

`add_character` / `update_character` → `tags`:

```text
Write the character as tags: how many people this entry draws, their age, body, hair and face. The count goes here and nowhere else, because this is the one place a count sits next to the person it counts. Do not write solo: the same character stands alone in one frame and next to somebody in the next, so an entry claiming solo is wrong in half of them. A pov_ entry shows only hands and arms and no face, so it carries no count at all. Do not write clothes here -- those are outfits.
```

`add_outfit` / `update_outfit` → araç tarifine bir cümle:

```text
Name an outfit after the clothes, not after the person wearing them, because two characters can wear the same outfit.
```

`add_outfit` / `update_outfit` → `tags`:

```text
Write the clothes as tags and nothing else. Do not write a person here: no count, no body, no hair. One entry dresses one person. Its text is handed whole to whoever wears it, so an entry covering two people would put the man in the dress.
```

`add_location` / `update_location` → `tags`:

```text
Write the place as tags. Nobody is in it and it carries no count. Who is in the frame is decided elsewhere, and a person written here would be drawn into every frame set in this place.
```

**`update_*` araçları bugün taşımadıklarını taşıyor.** Üçü de `AN_ENTRYS_NEW_TAGS` sabitini
paylaşıyor, ve o sabit yalnız **değiştirme anlamını** söylüyor: *"the whole entry as it should now
read -- this replaces the text rather than adding to it."* Şekil kuralını bugün ortak metinden
alıyorlar, ve ortak metin kısalınca almaz olurlar. Var olan sabitler birleştirilerek çözülüyor —
`ADD_*_TAGS` + `AN_ENTRYS_NEW_TAGS` — yeni metin yazılmadan. Kodda `tools.py`'nin üç `tags` alanı
yeni sabitlere bağlanıyor; `new_name` alanları olduğu gibi kalıyor.

**Ortak metin de madde madde yazıldı** *(kullanıcı kararı, 10 Eylül)*, 33'teki gibi: 1. paragraf
tek nefeste beş kural taşıyordu, ve zayıf modelin ortadakileri düşürdüğü yer orası. Yedi kural,
yedi madde. Başlıktı — *"How to write the tags."* — artık niçin öyle yazıldığını söyleyen bir cümle,
ve bütün maddelerin arkasında duruyor.

**Bir madde, kaldırılan örneğin işini üstlendi:** *"Do not join two tags into one longer phrase."*
30 numaranın sildiği `long hair, black hair` tam olarak bunu gösteriyordu. Kural artık kendi
cümlesiyle söyleniyor.

**Beş şey değişti:**

| Ne | Neden |
|---|---|
| Başlık cümlesi emre döndü | *"How to write the tags."* bir başlıktı, kural değil → *"Write tags, not sentences."* İlk cümle artık en çok ihlal edilen kuralı söylüyor. |
| Şema dili kalktı | *"No or inside a value"* — okuyan model "value" yazmıyor, etiket yazıyor → *"Never write the word or inside a tag."* |
| Yasak önce, deyim sonra | *"cannot toss a coin"* tek başına emir değildi; arkasına *"pick one and write only that"* geldi. |
| Neyin iki kez yazılacağı belirsizdi | *"yours would be printed twice"*un önüne *"The code already puts them at the front"* geçti. |
| Elliptik yapılar açıldı | *"a tag is one that vocabulary has"* → *"use a tag that vocabulary already has"*; *"in the same shape"* → *"in the same short form"*. |

**Bir bedeli yine de duruyor:** yukarıdaki madde kuralı **anlatıyor**, ama örnek onu
**gösteriyordu**. 30 numaranın sildiği örnekler içinde bedeli en yüksek olan buydu, ve bir cümle
bir örneğin yerini tam olarak tutmuyor.

**Hiçbir test kırılmıyor.** Tutulan dizgeler yerinde: `danbooru`, `rather than a description`,
`underscores`, `no tag for it`, `article`, `sentence`, `tags`, `quality`, `twice`, ` or `, `coin`.
`solo`, `pov_`, `carries no count`, `the one place a count`, `clothes` ve `nobody` de taşındıkları
metinlerde duruyor — kod geçişinin test turu bunları yeni evlerinde tutacak. Ayrıca `action` ve `camera`
kelimeleri ortak metinde **geçmiyor**: `test_the_rules_say_nothing_about_a_frames_action` bunu
tersinden tutuyor.

**Durum:** belgede · kodda değil

---

### 35 · §6'nın araç metinleri sade İngilizceyle, madde madde yeniden yazılır

33 kareyi yazan modelin promptunu, 34 ortak SDXL kurallarını sadeleştirdi. Aynı muamele modele
giden **en büyük** bloğa uğramamıştı: **23 araç tarifi**, `prompt.py`'de ~1785 kelime, ve altısı
ayrıca SDXL kurallarını taşıyor. Blok **her istekte** gidiyor.

**Yazım sözleşmesi** *(33 ve 34'ten çıkan kurallar, bu kez araç metinlerine)*:

1. **Emir başa, sebep arkaya ayrı cümle.** Kural bir yan cümlenin içinde durmaz.
2. **Bir madde, bir kural.** Tek kuralı olan araç madde almaz — `read_file` tek cümle kaldı.
3. **Şema ve mimari dili yok.** `map`, `value`, `field` modelin yazdığı şeyi adlandırmıyor.
4. **Belirsiz zamir yok.** `those`, `them`, `it` neye bağlandığı belirsizse açılır.
5. **`--` ile gömülü kural yok.** Uzun tire kuralı cümlenin ortasına gömüyordu; noktaya bölündü.
6. **Örnek yok** *(30 numaranın kararı)*. Ad örnekleri — `as in notes.md`, `as in bedroom` —
   kapsam dışı: onlar prompt değil, dosya ve girdi adı.
7. **Ayrıntı düzeyi örnekle değil kategori sayarak verilir.**
8. **Ret cümlesi kendi maddesine.** *"Refuses a name that is already there"* bir kural, yan cümle
   değil — ve öznesi belirsizdi, artık `This tool refuses…` diyor.

**Biçim:** araç tarifi madde madde; **parametre metni düz kalıyor.** Tek alanın tarifinde madde
işaretine gerek yok, sözleşme yine geçerli.

**22 araç yazıldı, biri yazılmadı.** `mark_step_done` elden geçmedi: **Madde 203 aracı tümüyle
kaldırıyor**, ve bugün yazılan metin silinecek metin olurdu. Belgede de bu notla duruyor.

**Dört aracın yazımı koda inmeyecek** *(10 Eylül, bu kayıttan sonra karar verildi)*. Burada yeniden
yazıldılar, ama dördü de kaldırılıyor:

| Araç | Kaldıran madde |
|---|---|
| `read_prompt_piece` | **205** — araç ve `PROMPT_PIECES` kütüphanesi birlikte |
| `build_character_prompts` | **206** — önizleme, senaryonun çıktısına girmiyor |
| `write_plan` | **207** — `create_file` ile plan kipi yetiyor |
| `write_frame_prompt` | **208** — kuruluş sebebi 201'de düştü; düzeltmeyi `update_frame`, ilk yazımı `write_missing_actions` yapıyor |

Kod geçişi o dört maddeden sonra koştuğu için bu yazımlar hiç uygulanmayacak. Kayıtta duruyorlar,
çünkü silinen şeyin son hâli de kayıttır. `mark_step_done` zaten baştan kapsam dışıydı *(203)* —
yani §6'nın 23 aracından **beşi** kalkıyor, ve geriye **18** kalıyor.

**Aynı kayıt iki eksiği kapattı.**

*Birincisi, 34'ün birleştirmesinden kalan kırık cümle.* Üç `update_*` alanı şöyle bitiyordu:

```text
…those are outfits. The whole entry as it should now read -- this replaces the text rather than adding to it.
```

*"The whole entry as it should now read"* eskiden cümlenin **başıydı** ve orada çalışıyordu; sona
yapışınca yüklemsiz bir parça oldu. Yenisi:

```text
…those are outfits. Give the whole entry as it should now read: this replaces the text rather than adding to it.
```

*İkincisi, ayrıntı düzeyinin yalnız karakterde olması.* `add_character.tags` beş kategori sayıyor
*(sayı, yaş, beden, saç, yüz)* ve örneksiz ayakta durdu; öteki ikisi durmadı — 30 numaranın sildiği
örnekler ayrıntı düzeyini **gösteriyordu**. Karakterin yaptığı yapıldı, örnek eklenmeden:

```text
add_outfit / update_outfit → tags
Write the clothes as tags and nothing else: the garments, their colour, their material, and what they leave bare.

add_location / update_location → tags
Write the place as tags: what kind of place it is, whether it is indoors or out, what stands in it, and the light.
```

**Yeni metinlerin tamamı** [belgenin §6'sında](2026-09-09-queenagent-modele-giden-metinler.md).

**Teste bağlı dizgeler korundu.** Araç tarifleri `_said_by()` üzerinden **23 yerde** okunuyor.
Yeniden yazım bir kuralı düşürmediği için hiçbirinin değişmesi gerekmiyor; tutulanlar tek tek
kontrol edildi:

| Araç | Tutulan |
|---|---|
| `edit_file` | `without the line numbers` · `if this turn has not seen it` · `already in front of you` · `replace_all` |
| `write_plan` | `if this turn has not seen it` |
| `add_scene` | `before` · `write_frame_prompt` |
| `write_frame_prompt` | `note` |

**Yokluğu tutulanlar da bozulmadı:** `so read the file first` ve `so read it first` metinde
**geçmiyor** *(ikisi de koşulsuz emri yasaklayan negatif iddialar)*; `write_frame_prompt`
`update_frame`'in tarifinde **geçmiyor**; `penis`, `vagina` ve `expression` üç etiket aracının
tarifinde **geçmiyor**.

**Kelime bütçesi:** hedef, toplamın bugünkü ~1785'i aşmaması. Madde biçimi kelime ekler, gömülü yan
cümlelerin bölünmesi ve öznesi belirsiz ret cümlelerinin toparlanması ise kelime kazandırır.
**Ölçüm kod geçişinde yapılacak**, çünkü tavan `prompt.py`'deki sabitlerin toplamı — belgedeki §6
Türkçe notlar da taşıyor ve doğru terazi o değil. Aşılırsa kesilecek yer sebep cümleleri değil,
tekrar eden tariflerdir.

**Durum:** belgede · kodda değil

---

## Kararı bekleyenler — hepsi kapandı

Bunlar **çelişki ya da fazlalık**tı, yazım değil: iki metin aynı soruya iki cevap veriyor, ya da bir
metin okuyucusuna ait olmayan bir kural taşıyordu. Okuma sekiz tane açtı, ve **sekizi de karara
bağlandı** — 10 Eylül'de kapandı.

| # | Neydi | Nerede kapandı |
|---|---|---|
| A | `SDXL_PROMPT_RULES` 2. paragrafın örneği bir tarifti | **30** — örnek kalktı |
| B | `WRITE_FRAME_PROMPT` hâlâ *"düzeltme yolu benim"* diyordu | **31** — yeniden yazmak ile düzeltmek ayrıldı |
| C | `WRITE_MISSING_ACTIONS`'ta aynı cümlenin kopyası | **32** — aynı ayrım |
| D | `ADD_OUTFIT_TAGS`'in örneği Danbooru'da yoktu | **30** — örnek kalktı |
| E | Planı hangi araç yazıyor | **29** — kipe bağlandı: plan kipinde `write_plan`, ötekilerde `create_file` |
| F | Düzeltilen satırın tek bir an olduğu editöre gidiyor mu | **23'ün sonu** — sıfat yetiyor, hiçbir metin değişmedi |
| G | Çekim örnekleri Danbooru'da doğrulanmamıştı | **30** — örnek kalktı |
| H | 2. ve 3. paragraf girdi yazmayan okuyuculara da gidiyor | **34** — ortak metin ikiye bölündü, girdinin kuralı alanına indi |

Sekizi de bu log'da duruyor. H bir ara ayrı bir madde *(204)* diye yazılmıştı; 190'ın içine alındı
ve numarası [yol haritasında geri çekildi](superpowers/plans/2026-09-06-queenagent-v8-roadmap.md) —
bölme bir metin kararı, ve metinleri okuyan zaten 190.

Ayrıca kodun kendi yorumunda, modele gitmeyen ama yanlış olan bir cümle: `run_tool`'un docstring'i
*"the other eighteen"* diyor, oysa **23** araç var.
