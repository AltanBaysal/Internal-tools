# QueenAgent v8 Yol Haritası — çıkan prompt, ve koşarken görünen

**Kaynağı:** `queen-agent/BACKLOG.md`, 6 Eylül — artı **195 ve 196, koşu sürerken eklendi**
*(kullanıcı, 8 Eylül; backlog'dan değil, doğrudan)*. Taslak **yirmi maddeydi**, sekiz dilim, 183'ten
203'e — **188 yok**, taslak okunurken geri çekildi *(aşağıda)*. Koşarken **beş madde daha** eklendi
*(205–209, 10 Eylül; 204 aynı gün geri çekildi)*, ve koşu **yirmi beş** maddeyle kapandı. Numaralar
182'nin ardından gidiyor ve **hiç kaymıyor** — yazılmış spec'ler onlara atıf yapıyor, ve çekilen bir
numara boş kalır.

**Numara kimliktir, sıra değildir.** 189 taslak sırasında öne alındı ve numarası bırakıldığı yerde
kaldı *(kullanıcı kararı, 6 Eylül: konuşma boyunca numaralarla anıldılar, kaydırmak onları
okunmaz kılardı)*. Koşulacak sıra bu dosyanın sırasıdır.

v7'nin sorusu *"model dosyanın şeklini bilmeden senaryo kurabilir mi"*ydi ve cevabı evet çıktı.
v8'in sorusu başka: **çıkan prompt'un kendisi**, ve **kullanıcının koşarken ne gördüğü.**

---

## Nerede kalındı

Her madde iki tur: testler kırmızı commit'lenir, sonra kod yeşile getirilir. Aşağıdaki hash
**kapanış** commit'i — o maddenin yeşili. Bu tablo her kapanışta güncelleniyor.

| Madde | Durum | Kapanış |
|---|---|---|
| 183 · Grok 4.3 | **kapandı** | `793fd38` |
| 189 · metinler tek dosyada | **kapandı** | `356cdf4` |
| 184 · prompt sırası | **kapandı** | `d6eeaee` |
| 185 · toplu action aracı | **kapandı** | `2a1304e` |
| 186 · altı adım, Edit prompts | **kapandı** | `d32a5bb` |
| 187 · hazır prompt parçaları | **kapandı** | `a390078` |
| 191 · New project 1/2/3 | **kapandı** | `7a052b1` |
| 192 · dosyalar tazelenir | **kapandı** | `4f50ab8` |
| 193 · kopyala düğmesi | **kapandı** | `efac34c` |
| 194 · canlı tur şeridi | **kapandı** | `5e3c6e5` |
| 195 · mesaj düzenlenir, sohbet sürümlenir | **kapandı** | `769fa8d` |
| 196 · sistem promptunun ikinci parçası | **kapandı** | `39ae4c7` |
| 197 · düzenleme mesajın kendi yerinde | **kapandı** | `ca57b0f` |
| 198 · akış karakterle başlar, plan işaretlenir | **kapandı** | `b9dbc67` |
| 199 · şerit ve kalem tek satırda | **kapandı** | `74a078d` |
| 200 · etiketler Danbooru olur | **kapandı** | `7c4c82c` |
| 201 · eylemi ana ajan düzeltir | **kapandı** | `9a76352` |
| 202 · kareyi yazan da DeepSeek | **kapandı** | `1d9e491` |
| 205 · hazır parça aracı kalkar | **kapandı** | `5500cd0` |
| 206 · karakter önizleme aracı kalkar | **kapandı** | `8eaac5d` |
| 207 · plan yazan araç kalkar | **kapandı** | `8045510` |
| 208 · tek kare yazan araç kalkar | **kapandı** | `9eabb06` |
| 190 · metinlerin okunması | **kapandı** | `2d11881` |
| 203 · adım işaretleme aracı kalkar | **kapandı** | `edfdecc` |
| 209 · sürüm arayüzde görünür | **kapandı** | `ef24a3e` |

**Yirmi beş maddenin hepsi kapandı**, 183'ten 209'a — 188 ile 204 boş, ikisi de geri çekildi, ve
numaraları kaymadı. **Koşu 11 Eylül'de kapandı** *(kullanıcı kararı)*: test geçişinin bulduğu her
şey [backlog'a](../../../queen-agent/BACKLOG.md) yazıldı, çünkü kapanmış bir koşuya madde eklemek
onu kapanmamış yapar.

183–187, 189, 191–202 kapandı. Ajan 194'ün ardından durmuştu; koşu **195 ve 196 ile yeniden
açıldı** *(kullanıcı, 8 Eylül)*. Ardından **197 ve 198** eklendi, ikisi de denemeden çıktı: 195'in
düzenleme akışının yeri yanlış bulundu *(ve aynı yerde 195'in bıraktığı bir hizalama kusuru vardı)*,
186'nın bağlam sorusu ise sürtünme olarak görüldü. **199 da aynı yerden** geldi: 197 kalemi bubble'ın
altına indirdi, ve sürüm şeridiyle alt alta düştüğü orada görüldü. **200–202 de denemeden çıktı**,
ama bu kez ekranın değil çıkan işin kendisinden: etiketler Danbooru sözlüğüyle daha iyi geliyor, ve
DeepSeek artık isteneni yazdığı için eylem satırını ayrı bir modele yazdırmanın sebebi kalmadı.
196'nın açtığı yeri de kullanıcı doldurdu *(8 Eylül)*: sabit artık boş değil, ve 202'den sonra
kareyi yazan modele de gidiyor.

**Koşu 10 Eylül'de yeniden açıldı.** 190'ın okuması bitti — 35 düzeltme, bekleyen karar yok — ve
okuma dört aracın **kaldırılmasını** getirdi: her biri her istekte tarifini ödüyor, hiçbiri kendi
sebebinin üstünde durmuyordu. **Dördü de kapandı** *(205–208)*, ve dördü de 190'ın kod geçişinden
önce koştu — çünkü kalkacak bir metni önce koda indirmek işi iki kez yapmaktır.

Araç sayısı **23'ten 19'a** indi. Ardından 190'ın kod geçişi koştu: 35 düzeltme `prompt.py`'ye
indi, 18 araç tarifi dahil. Geçiş iki şey daha buldu — test turunun kaçırdığı üç test, ve akış
metninin tavanı **480/450** ile aşması. İkincisinin kararı okumada zaten yazılıydı *(9 numara:
tavan yükselmez, iki yerde söylenen cümle düşer)*, ve üç cümle düştü — üçü de bir araç tarifinde
zaten duruyor. **Belge ile kod artık eşit.**

Ardından **203** koştu ve beşinci aracı aldı: araç sayısı **18**. Okumanın 11 numarası kutuları
*"yalnız bir not"*a indirmişti, ve bu madde onu sonuna kadar götürdü — kutu biçimi duruyor, onu
dolduran tur yok. Burada da yol haritasından **saptı**: kendi *"Ne çalışır"*ı kapanış maddesinin
`edit_file`'ı anmasını istiyordu, kullanıcı maddenin tümüyle düşmesini seçti *(10 Eylül)*.

**209 koşuyu kapattı:** kenar çubuğunda, adın altında `V8`. Sırası serbestti ve sona kaldı, çünkü
hiçbir maddeye dayanmıyordu.

**Test geçişi 11 Eylül'de koştu, ve koşu orada kapandı** *(kullanıcı kararı)*. Geçişin bulduğu üç
şey — sürümün adın yanında durması, kalem ile saatin uyuşmaması, ve yeni proje/sohbet açmanın
karmaşıklığı — [backlog'a](../../../queen-agent/BACKLOG.md) yazıldı. Buraya değil: bir koşu
kapandıktan sonra ona madde eklemek kapanışı geri alır, ve üçü de kendi koşusunu bekleyecek kadar
kendi başına duruyor.

**Koşunun kendi sayıları:** yirmi beş madde, araç sayısı **23 → 18**, ve giden beşinin tarifi her
istekte ödeniyordu. Modele giden metinlerin tamamı bir oturumda okundu, 36 düzeltme aldı, ve
[okuma kopyası](../../2026-09-09-queenagent-modele-giden-metinler.md) ile kod **eşit** — belge
bundan sonra kodun aynası olarak tutulur. Süit **923 arka uç + 652 ön uç**.

> **194'ün hash'i düzeltildi:** tablo `deb0a9e` diyordu, ama 7 Eylül'ün şerit sırası düzeltmesi o
> commit'ten **sonra** indi. Bir maddenin kapanışı, o maddenin son yeşilidir.

---

## Koşunun bağlayıcı kuralları

**Bir kural tek yerde durur.** v7 on altı madde boyunca metin ekledi, ve her biri kendi turunda
doğruydu — ama hiçbiri ötekinin yanında nasıl okunduğuna bakmadı. 182'de kelime tavanı kırmızı verdi
ve bir cümlenin silinmesiyle geçildi; o silinen cümle `add_character`'ın kendi metninin kopyasıydı.
Bu koşuda aynı sorunun peşine düşülüyor: iki yerde anlatılan bir kural, tek yerde anlatılana
indirgenir. Tavan yükselmez.

**Deneme ucuz olmalı.** Deneme 4'te 21 karelik bir düzeltme 21 raunt ve 277.6k jeton yedi. Pahalı
deneme az deneme demek, az deneme de geç görülen hata demek. 185 bu yüzden erken duruyor: kendisi
küçük bir madde, ama ondan sonraki her denemenin fiyatını düşürüyor.

**Prompt'un şeklini kod bilir.** `build_prompts` saf: yapıyı alır, string döndürür, ve kuralların
dışına konuşulamaz. 184 o şekli değiştiriyor — ama yine **kodda**, dosyada değil. Kendi sırasını
seçebilen bir yapı dosyası, *"bu kare neden farklı çıktı"* sorusuna *"değişiyor"* diye cevap verir.

---

# Dilim 1 — zemin

Sonraki her maddenin üstüne basacağı iki şey: **kim yazıyor**, ve **metinler nerede duruyor.** İkisi
de en başta, çünkü sonradan yapılırsa aradaki her madde yanlış varsayımla yazılmış olur — biri başka
bir modele söylenmiş kurallar, öteki yanlış dosyaya konmuş metinler.

## Madde 183 — Prompt yazan model Grok 4.3 olur

- **Sorun:** `config.PROMPT_MODEL` bugün `grok-build-0.1`. Kullanıcı kararı bunun Grok 4.3 olması.
  **Sırada ilk** olmasının sebebi 181: eylem satırının kuralları bugünkü yazara göre yazıldı, ve
  model sonradan değişirse o kurallar başka bir okuyucuya söylenmiş olur. Sonraki bütün metin
  maddesi *(190)* koşacak modelin üstünde ölçülmeli.
- **Ne çalışır:** `PROMPT_MODEL = "grok-4.3"`, ve `MODELS`'te `grok-build-0.1` satırı **kalkıp**
  yerini `grok-4.3`'e bırakır *(kullanıcı kararı: kimse kullanmayacak bir satır ölü yapılandırma)*.
  Adres ve anahtar aynı: `https://api.x.ai/v1`, `XAI_API_KEY`. O satırdaki string **doğrudan xAI'a
  gidiyor** — `client.py`'nin `payload["model"]`'i — yani takma ad değil, sağlayıcının kendi adı.
- **Kimlik doğrulandı:** `grok-4.3`, xAI'ın model listesinde *(docs.x.ai/docs/models, 6 Eylül)*.
- **Neden 4.3:** listede `grok-4.5` ve `grok-4.6` de var, ikisi daha yeni ve daha pahalı. Kullanıcı
  kararı 4.3 — ve `config.py`'nin kendi yorumu zaten *"nasıl akıl yürüttüğü için değil, ne yazacağı
  için seçilir"* diyor, yani yenisi kendiliğinden daha iyi değil.
- **Nasıl görülür:** bir kare yazdırılır ve cevap gelir. Damgadaki harcama xAI tarafında görünür.
- **Değişen:** `config.py`'nin iki satırı; `test_config.py`'nin sabiti pinliyor olması.

## Madde 189 — Modele giden her metin tek dosyada toplanır

- **Sorun:** metinler bugün **dörde dağılmış** durumda: `prompt.py`, `skills.py`, `tools.py`'nin
  `TOOL_SPECS`'i *(araç açıklamaları ve parametre metinleri, hacmin yarısı)*, ve araçların cevap
  cümleleri `run_tool`'un içinde. Hepsini okumak isteyen dört dosyada geziyor, ve iki yerde aynı şeyi
  söyleyen bir kural **görülemiyor** — 182'de silinen cümle böyle bir kopyaydı ve kelime tavanı
  kırmızı verene kadar kimse fark etmedi.
- **Ne çalışır:** modele giden her metin tek bir modülde, **adlandırılmış sabitler** olarak, ve kod
  onları çağırır — metin koda gömülü durmaz *(kullanıcı kararı: Flutter'ın `app constants`'ı gibi)*.
- **Python, Markdown değil.** Bu dosya metinlerin **kaynağı**, kopyası değil. Bir `.md`, koddan ayrı
  yaşayan ve ilk değişiklikte bayatlayan ikinci bir nüsha olurdu; deponun kendi kuralı da bu *(bir
  doc kodun söylediğini tekrarlamaz, dosyayı adıyla anar)*.
- **Kural test edilir:** *"depoda başka hiçbir yerde prompt yok."* Bu maddenin asıl kazancı bu —
  temenni değil, kırmızı verecek bir nöbetçi. `tools.py`'de üç tırnaklı uzun bir metin belirdiği anda
  takım düşer, ve bir sonraki madde metni doğru yere yazmak zorunda kalır.
- **Nasıl görülür:** kullanıcı tek dosyayı baştan sona okur ve modelin gördüğü her şeyi görür.
  `TOOL_SPECS` metinleri sabitlerden okur.
- **Bedeli, ve bilerek ödeniyor:** bugün araç açıklaması tarif ettiği şemanın **yanında** duruyor, ve
  o komşuluk metni doğru tutan şeylerden biri. Dışarı çıkınca gidiyor. Karşılığında tekrarın
  saklandığı yer aydınlanıyor — 190 zaten onu aramaya gidiyor, ve dağınık hâlde arayamaz.
- **Değişen:** yeni modül; `prompt.py`, `skills.py`, `tools.py` metinlerini oradan alır; testlerin
  `from ... import` satırları; ve yeni nöbetçi test.
- **Neden bu kadar erken, ve toplamakla okumanın farkı:** ilk taslakta bu madde 190'ın hemen
  önündeydi, yani sonda. Yanlıştı. **Toplamak mekanik bir iş** ve erken yapılırsa 185'in yeni araç
  açıklaması, 186'nın yeni skill metinleri ve 187'nin parçaları **doğduğu anda doğru dosyaya** iner.
  Sonda yapılsaydı üçü de eski dağınık yerlere yazar, 189 hepsini bir daha taşırdı. **Okumak** ise
  taramanın kendisi ve o gerçekten sonda kalmalı — 190 orada duruyor.

---

# Dilim 2 — yazan taraf

Prompt'a giden yol: hangi sırada diziliyor, ve kaç raunda mal oluyor.

## Madde 184 — Prompt sırası: karakterler önde, mekân sonda

- **Sorun:** bugün mekân ve action **iki karakterin arasına** giriyor *(`build_prompts.py`)*: kalite,
  lider ve kıyafeti, mekân, action, kamera — sonra `BREAK` ve her ek karakter kendi bloğunda.
  Araya girme, iki tarifi birbirinden uzaklaştırmak içindi. Ama ayırma işini `BREAK` zaten yapıyor
  *(Madde 138/139: encoder o literal string'den bölüyor)*, ve mesafe onun yanında zayıf ikinci bir
  önlem — karşılığında **action'ı ikinci karakter tanıtılmadan önce** okutuyor.
- **Ne çalışır:**
  ```
  kalite, karakter 1 + kıyafetleri BREAK karakter 2 + kıyafetleri BREAK … , action, kamera, mekân
  ```
  Karakterlerin hepsi başta ve her biri kendi `BREAK` bloğunda; sonra action ve kamera; en sonda
  mekân. Kıyafet yine sahibinin **hemen yanında** — görüntü modeline kıyafetin kimin olduğunu
  söyleyen tek şey o komşuluk.
- **Nasıl görülür:** iki kişilik bir kare derlenir ve iki karakter bloğu **art arda** çıkar, mekân
  en sonda.
- **Değişen:** `build_prompts`'un `lead`/`blocks` kuruluşu ve sıranın gerekçesini anlatan yorum;
  sırayı okuyan testler.
- **Action/kamera/mekân kendi `BREAK` bloğunu alır** *(kullanıcı kararı, 6 Eylül)*. Son karakterin
  bloğuna binerse **ona** bağlanır, ve iki kişilik bir eylem tek kişinin eylemi olur — bugün action'ın
  lidere bağlanmasının sebebi de bu, yalnız ters yönden. Kendi bloğunda kimseye özel bağlanmıyor.
- **Bedeli, ve neden küçük:** tek kişilik karelerde de artık bir `BREAK` olacak, ve CLIP her parçayı
  ayrı kodladığı için action kendi parçasında **öznesiz** kalıyor. Ama parçalar kodlandıktan sonra
  birleşiyor ve UNet hepsini görüyor; kadroda tek kişi varsa karıştırılacak kimse de yok. Kural tek
  kalıyor: *"kaç kişi varsa ona göre değişir"* diyen bir düzen, **bu kare neden farklı çıktı**
  sorusuna cevap veremez.
- **Ölçülmemiş, ve kayda öyle geçiyor:** yukarıdaki akıl yürütme, ölçüm değil. Denemede görülecek —
  tek kişilik bir kareyi iki türlü derleyip bakmak yetiyor.
- **Düzeltme, 7 Eylül:** *"Nasıl görülür"* satırı *tek kişilik bir karede `BREAK` hiç geçmez* diyordu
  ve bu, hemen altındaki kullanıcı kararıyla çelişiyordu — action kendi bloğunu alınca tek kişilik
  karede de bir `BREAK` oluyor, ve bunun bedeli zaten bir alt maddede yazılı. Çelişen cümle kalktı;
  bağlayıcı olan karar.

## Madde 185 — Action'ı olmayan bütün kareleri dolduran araç

- **Sorun:** `write_frame_prompt` tek kare alıyor *("One frame per call", kendi açıklamasında)*.
  Deneme 4'te 21 kare **21 ana ajan raundu** ve **277.6k jeton** etti. Fatura Grok değil: her raunt
  sistem promptunu, skill metnini ve **bağlam kabını** baştan gönderiyor, ve kaptaki yapı dosyası
  her yazımda büyüyor — 21. raunt 1. raunttan ağır.
- **Ne çalışır:** `action`'ı olmayan bütün kareleri dolduran ayrı bir araç. Ana ajan tarafında **tek
  raunt**, istekler paralel. Tek kareli olan yerinde kalır — o düzeltmenin aracı.
- **Aralık yok** *(kullanıcı kararı, 6 Eylül)*: dosyanın tamamına bakar, `action`'ı olanı **atlar**,
  olmayanı yazar. Yapılacak işin tanımı zaten boş kare; bir `from`/`to` modele karar bindirir ve
  hangisinin yazıldığını iki yerden takip ettirir.
- **Not parametresi yok.** Bu ilk yazım; not düzeltmenin şeyi, ve düzeltme tek kareli aracın işi.
- **Bir kare düşerse ötekiler durmaz.** Yirmi istekten biri hata alırsa on dokuzu yazılır ve cevap
  **hangisinin yazılamadığını** söyler. Hepsini geri almak, bir saatlik işi tek hata için çöpe atmak
  olurdu — ve 173'ün *"ya hep ya hiç"* kuralı yazmadan önce yapılan bir kontrole aitti, burada
  ödenmiş bir işi geri almaya değil.
- **Nasıl görülür:** yirmi kareli boş bir dosyada tek çağrı, ve damga bir raundun harcamasını
  gösterir. İkinci çağrı *"yazılacak boş kare yok"* der.
- **Değişen:** `tools.py`'de yeni bir araç ve `run_tool`'un dalı; `stream_answer`'ın çağrıları
  **sırayla** koşması *(paralel gitmesi bu maddenin işi)*; skill metinlerinde hangisinin ne zaman
  çağrıldığı.
- **Kapsam dışı:** **dolu** kareleri toplu yeniden yazmak. Deneme 4'ün pahalı işi aslında oydu, ama
  181 o düzeltmenin sebebini ortadan kaldırdı; gerekirse ayrı madde.
- **186 buna dayanıyor**, ve sebebi aşağıda.

---

# Dilim 3 — akış

Skill'lerin şekli. 185 bittikten sonra, çünkü birleşmenin önündeki tek engel onun çözdüğü şey.

## Madde 186 — Generate prompts+ kalkar, yerine prompt düzenleme gelir

- **Sorun:** bugün iki skill var ve action yazma işi ikincisinde. Kullanıcı kararı: o iş **Start a
  scenario**'nun içine girsin, ve boşalan yere **var olan promptları düzeltmek** için ayrı bir şey
  gelsin — düzeltme kendi başına bir iş.
- **Neden 185'ten sonra:** Deneme 3'te 23 karenin action'ı **tek tura sığmadı**, araya bir saat
  girerek ikiye bölündü. Akışın kuralı *"bir adım kullanıcı onaylayınca biter"* — sığmayan bir aşama
  o kuralın içinde yaşayamaz. 185 aşamayı tek çağrıya indirdiği anda sığıyor, ve birleşme mümkün
  oluyor. Sırası tersine dönerse madde kendi kuralını çiğneyerek doğar.
- **Yeni skill'in adı: *Edit prompts*** *(kullanıcı kararı)*. Ne yaptığını söylüyor ve kalkan adla
  karışmıyor. Metni İngilizce, QueenAgent'ın geri kalanı gibi.
- **Akışın yeni şekli** *(kullanıcı kararı, 6 Eylül)* — bugünkü beş adım altıya dönüyor ve **sıra
  değişiyor**:

  | | Adım | Bugünden farkı |
  |---|---|---|
  | 1 | **Bağlam sorulur** — ne yapılıyor, ne için | **yeni**; bugün böyle bir adım yok |
  | 2 | Plan yazılır | bugün 1. adım, ve bağlamı **model tahmin ediyor** |
  | 3 | Karakterler *(+ kıyafetler)* | aynı |
  | 4 | Mekânlar | aynı |
  | 5 | Sahneler | aynı |
  | 6 | **Promptlar üretilir ve iş biter** | bugün burada **devir** var |

  Asıl kazanç 1 ile 2'nin sırasında: planın açılış satırı bugün *"ne yapılıyor, ne için"* diyor ama o
  satırı model **hiçbir şey bilmeden kendi yazıyor**. Sorulunca plan bir tahmini değil bir cevabı
  taşıyor — ve plan taze sohbetin belleği olduğu için o tahmin bugün sonraki turlara da miras
  kalıyor.
- **`start_scenario` 2. adıma iner** *(kullanıcı kararı)*, bugün durduğu karakter adımından. Dosyanın
  adını veren şey zaten bağlam, ve erken açılınca sonraki her adım hazır bir dosyaya yazıyor. Bedeli
  kabul ediliyor: bağlamı söyleyip vazgeçen bir kullanıcı ardında boş bir `.json` bırakır.
- **6. adım 185'i çağırır**, sonra `build_prompts`. Devir mesajı ortadan kalkıyor: gidilecek başka
  skill yok.
- **Nasıl görülür:** tek skill seçilerek bir senaryo baştan sona kurulur ve promptları çıkar — ilk
  soru karakter değil bağlam olur. Sonra *Edit prompts* seçilip bir kare düzeltilir.
- **Metinler `superpowers:writing-skills` ile gözden geçirilir** *(kullanıcı isteği)*. O rehber Claude
  Code'un kendi skill dosyaları için yazıldı, yani her kuralı geçmez; geçen kısmı **bir modelin
  gerçekten uyduğu talimat nasıl yazılır** kısmı, ve iki metin de tam olarak o.
- **Değişen:** `skills.py`'nin iki metni ve `INSTRUCTIONS`'ın anahtarları; frontend'in `skills.js`'i
  *(ikisi ayrı yerde ve ayrılırsa skill hiç metin taşımaz — `test_skills.py` bunu tutuyor)*;
  `test_skills.py`'nin pinlediği cümlelerin çoğu.
- **Kelime tavanı:** *Start a scenario* **tam 450'de**, boşluk yok. Bu madde iki metni birleştiriyor,
  yani tavanların yeniden konuşulması onun işi — ama **yükselterek değil**, birleşen iki metinde
  aynı şeyi söyleyen cümleleri teke indirerek.

## Madde 187 — Hazır prompt parçaları

- **Sorun:** bilinen şeyler — pozisyonlar gibi — her seferinde yeniden yazdırılıyor. Kullanıcı
  isteyince modelin hazır olanı **doğrudan göstermesi** isteniyor.
- **Rastgelelik değil:** içlerinden biri seçilmiyor, istenen gösteriliyor. `SDXL_PROMPT_RULES`'un
  *"model yazı tura atamaz"* kuralı yerinde kalıyor.
- **Nerede durur:** 189'un modülünde, **adlandırılmış sabitler** olarak *(kullanıcı kararı)*. Bu
  ortak bilgi, projeye özel değil — aynı pozisyon her senaryoda aynı. Depoda durunca herkeste aynı
  oluyor, sürüm kontrolüne giriyor, ve öteki metinler gibi gözden geçiriliyor. 189'un *"depoda başka
  yerde prompt yok"* nöbetçisi de bu maddeyi kendiliğinden kapsıyor.
- **Nasıl ulaşılır:** bir araçla, **prompta gömerek değil.** Gömülürse her raundda para yakar ve
  liste büyüdükçe büyür — 185'in bütün dersi bu. Araç olunca yalnız sorulduğunda ödeniyor.
  Bilinmeyen bir ad istenirse cevap **bilinenleri sayar**, `build_prompts`'un bugünkü kalıbı gibi.
- **Gösterdiğini kareye koymaz.** Göstermek göstermektir; kareye koymak `update_frame`'in işi. Bu
  deponun fiil ayrımı zaten böyle, ve bir araç iki iş yaparsa hangisini yaptığı cevapta kaybolur.
- **Nasıl görülür:** kullanıcı bir pozisyonu ister, model onun yazılı hâlini gösterir — yazdırmadan.
- **Madde 130 ile çelişmiyor, ve 190'da bu yazılacak:** *"derlenmiş prompt geri basılmaz"* kuralı
  **üretilmiş sonuç** için. Hazır parça bir **referans metin**, ve kullanıcının görmek istediği şeyin
  ta kendisi. Ayrım bugün hiçbir yerde yazılı değil.

---

# Dilim 4 — yüzey

Kullanıcının gördükleri. Hiçbiri ötekine dayanmıyor; bir arada duruyorlar çünkü dördü de frontend'e
dokunuyor ve `dist` bir kez derleniyor.

## Madde 191 — Yeni proje adı numaralanır

- **Sorun:** her yeni proje **"New project"** adıyla doğuyor *(`create_project.py`'nin
  `NEW_PROJECT_NAME`'i)*, ve aynı adı taşıyan üç proje kenar çubuğunda ayırt edilemiyor.
- **Ne çalışır:** **her proje numaralı doğar** — *New project 1*, *New project 2*, *New project 3*
  *(kullanıcı kararı, 6 Eylül)*. Sıradaki boş numarayı alır: 2 silinip yenisi açılırsa boşluk
  dolar.
- **Emsal var ama birebir değil, ve fark bilerek:** `naming.py`'nin `unique_name`'i **ilkine
  dokunmuyor** ve ikinciden itibaren **tireyle** numaralıyor — `plan.md` sonra `plan-2.md`. Burada
  ilki de numara alıyor, ve ayırıcı **boşluk**. İkisinin de sebebi var: tire dosya adının işareti,
  proje başlığının değil; ve numarasız ilk proje **sonsuza kadar özel** kalır — yeniden
  adlandırıldığı gün numaralamada delik açar.
- **Nasıl görülür:** üst üste üç proje açılır ve *New project 1/2/3* diye listelenir.
- **Değişen:** `create_project.py`; `test_projects_api.py`'nin `"New project"` bekleyen satırı.

## Madde 192 — Dosyalar tazelenir: hem liste, hem detay

- **Sorun:** ekran kendi kendine tazelenmiyor, ve **iki yerde** — dosya listesinde ve bir dosyanın
  detayında *(kullanıcı, 6 Eylül)*. İkisinden ağır olanı detay: **liste bayatlayınca bir ad gizlenir,
  detay bayatlayınca yanlış içerik gösterilir.**
- **Emsali modelde var:** Madde 129 bağlam kabını tam bu yüzden diskten okutuyor — bir kopya, yazıldığı
  anda bayatlıyor. Kullanıcının ekranında o kural yok.
- **Ne çalışır — ikisi birden** *(kullanıcı kararı)*: tur bitince **kendiliğinden** tazelenir, artı
  elle basılacak bir **düğme**. Kendiliğinden olan sık durumu halleder; düğme gerisini, çünkü dosyayı
  yazan şey her zaman bir tur değil — kullanıcı Drive'dan elle bir dosya koyabilir, ya da uzun bir
  turun ortasına bakmak isteyebilir.
- **Nasıl görülür:** tur bitince yeni dosya listede belirir, ve açık duran bir dosyanın içeriği
  değiştiyse yenisi görünür. Düğme her ikisini turdan bağımsız yapar.
- **Değişen:** frontend'in dosya listesi ve dosya detayı; `dist`.

## Madde 193 — Dosyanın üstünde kopyala düğmesi

- **Sorun:** `build_prompts` promptları bir dosyaya yazıyor ve sohbete basmıyor *(Madde 130, ve o
  kural yerinde kalıyor)*. Prompt'u almanın tek yolu elle seçmek.
- **Ne çalışır:** dosyanın üstünde bir kopyala ikonu; basınca **dosyanın tamamı** panoya gider
  *(kullanıcı kararı, 6 Eylül)*.
- **Her dosyada, yalnız prompt dosyasında değil.** `.py`'ye özel yapmanın sebebi yok, ve genel olunca
  plan da senaryo da kopyalanabiliyor.
- **Prompt başına düğme bilerek yapılmıyor.** Dosya düz metin olarak gösteriliyor; promptları tek tek
  tanımak, `render_module`'ün yazdığı şeklin ön yüzde **ikinci bir okuyucusu** demek — ve o okuyucu
  yazıcıdan ayrıldığı gün düğmeler yanlış metni kopyalar. `.json`'dan okumak da çözüm değil: o zaman
  kopyalanan şey `build_prompts`'un ürettiği değil, ön yüzün kendi kurduğu olur, ve **iki yerde
  derleme iki farklı sonuçtur.**
- **Madde 130 ile çelişmiyor:** kopyalamak, prompt'u sohbete basmak değil. Kural metnin **modele geri
  dönmemesi** hakkında; pano modelin göremediği bir yer.
- **Nasıl görülür:** dosya açılır, ikona basılır, içerik panodadır.
- **Değişen:** frontend'in dosya görünümü; `dist`.

## Madde 194 — Koşan tur mesajın altında canlı görünür

- **Sorun:** damga turun **sonunda** düşüyor. Uzun bir tur boyunca ekranda ilerlemeyi gösteren
  hiçbir şey yok.
- **Ne çalışır:** **damganın bugün durduğu yerde**, tek satır, hepsi yan yana — sütun ya da sağ/sol
  ayrımı yok *(kullanıcı kararı, 6 Eylül)*:

  ```
  raund 4/16 · 12.3k jeton · ⠹ Ideating…
  ```

  > **Düzeltme, 7 Eylül** *(kullanıcı kararı)*: bu çizim ilk yazıldığında spinner baştaydı. Sıra
  > tersine döndü — satırın taşıdığı iki bilgi öne, dekoratif olan sona. Aşağıdaki *donmuş
  > görünmemek* gerekçesi ikisinde de aynı ölçüde geçerli: spinner'ın işi kımıldamak, ve nerede
  > durduğu kımıldamasını değiştirmiyor.

- **Donmuş görünmemesi asıl mesele.** Sayı otuz saniye kıpırdamayabilir; ekranı canlı tutan şey
  kelimenin dönmesi değil, **sürekli dönen spinner**. Kelime birkaç saniyede bir değişir.
- **Kelime Claude Code'daki gibi olur** *(kullanıcı kararı)*: dönen, ilginç, ve ne yapıldığını
  söylemeye çalışmayan — o üsluptan *(gerundlu, esprili)* bir liste yazılır. Araç adından türetilen
  bir metin **istenmedi**; bilgi taşıyan iki parça zaten yanında duruyor.
- **Gösterilen sayı: `sent + cached + answered`**, yani turun **toplam hacmi** — tek sayı, ve
  Deneme 4'te rahatsız eden **277.6k** tam olarak buydu. Yalnız `sent` işin yarısını gizlerdi:
  `cached` de gidiyor, sadece ucuza. Şerit *"bu tur ne kadar büyüdü"* sorusunu cevaplıyor, faturayı
  değil — fatura turun sonunda damgada duruyor.
- **Tur bitince şerit damgaya dönüşür**: aynı yer, aynı tasarım, spinner durur, sayı donar. İki ayrı
  şeyin yer değiştirmesi göze zıplardı.
- **Nasıl görülür:** çok raundlu bir tur koşarken spinner döner, kelime değişir, raund ve jeton artar;
  tur bitince aynı satır damga olur.
- **Değişen:** `stream_answer`'ın akışa ne koyduğu *(raundları zaten tek tek koşuyor ve harcamayı
  topluyor; eksik olan bunun ön yüze **ulaşması**)*; `useChat.js` ve `ChatScreen.jsx`; `dist`.

---

# Dilim 5 — geri dönüş

Söylenmiş bir şeyin geri alınması. Kendi dilimi, çünkü Dilim 4'ün dördü yalnız ön yüze dokunuyor ve
195 sohbetin **diskteki şeklini** değiştiriyor. 197 onun üstüne biniyor: aynı iş, ama kullanıcının
onu yaptığı yer. 199 da öyle — 197'nin taşıdığı kalemin, 195'in şeridiyle nasıl durduğu.

## Madde 195 — Düzenlenen mesaj sohbeti sürümler

- **Sorun:** yanlış istenmiş bir mesajın bugün tek çaresi yenisini yazmak. Yanlış cümle sohbette
  kalıyor, ve kalmakla da bitmiyor — sonraki her tur bütün konuşmayı yeniden gönderdiği için o cümle
  modele tekrar tekrar gidiyor. Bir noktaya dönüp **başka bir yol denemek** mümkün değil.
- **Ne çalışır:** kullanıcı mesajında bir **Edit** düğmesi. Cümle yazı kutusuna düşer, düzeltilip
  gönderilince o noktadan **yeni bir sürüm** açılır ve tur oradan koşar. Mesajın altında
  `‹ 2/3 ›` — sürümler arasında gezilir, ve açık olan sürüm sayfayı yenilemeye dayanır.
- **Emsali ChatGPT'nin sitesi** *(kullanıcı kararı, 8 Eylül)*: düzenlenen mesaj eskisinin yerine
  geçmiyor, yanına ikinci bir sürüm olarak duruyor.
- **Dönülecek nokta kullanıcı mesajıdır** *(kullanıcı kararı)*. Bir turun sınırı zaten orası: ajanın
  cevabı tek bir cümle değil, kendi araç çağrılarıyla birlikte bir tur, ve ortasına dönmenin diskte
  bir karşılığı yok.
- **Eski sürüm silinmez.** FOUNDATION'ın 1. ilkesi *(kullanıcının işi kutsaldır)* bu maddeye
  doğrudan biniyor: sürüm açmak, sonrasını **kesip atmak** olsaydı, o turlar hiçbir yerde kalmazdı.
  Ayrılan yol yenisinin yanında duruyor, ve `‹ › ` ile geri dönülüyor.
- **Diskte, ve neden kopya değil:** `chats/<id>.json` bugünkü `messages`'ını **ilk çizgi** olarak
  tutar. Her yeni sürüm **nereden ayrıldığını** *(hangi çizginin kaçıncı mesajı)* ve **yalnız kendi
  mesajlarını** yazar; hangisinin açık olduğu da sohbetin kendi alanı. Ayrılma noktasına kadarki
  konuşma böylece **tek nüsha** kalıyor — sürümler tam kopya olsaydı aynı mesaj üç dosyada üç kez
  dururdu, ve bu deponun kaçındığı şey tam olarak o.
- **Göç yok:** `versions` alanı olmayan bir sohbet, bugünkü tek çizgi olarak okunur. Alan da ancak
  bir sürüm açılınca yazılır — boş bir liste diskte gürültüdür, ve `FileChatStore`'un bütün alanları
  zaten böyle davranıyor.
- **Sohbeti okuyan her şey açık çizgiyi okur:** `is_owed_an_answer`, `last_context`/`is_full`'un
  tavanı, başlık, ve kabın gönderdiği konuşma. Kapalı bir sürümdeki turlar tavana **girmez** — o
  turlar artık gönderilmiyor, ve gönderilmeyen bir şeyin bağlamı büyütmesi yanlış olurdu.
- **Nasıl görülür:** üç mesajlık bir sohbette ikinci mesaj düzenlenir; sohbet o noktadan yeni bir
  cevapla devam eder, `‹ 1/2 ›` ile eskisine dönülür ve eski cevap olduğu gibi durur. Sayfa
  yenilenince açık sürüm hâlâ açıktır.
- **"Yeniden cevapla" yok** *(kullanıcı kararı)*. Mekanizması aynı olurdu, ama faydası ayrı bir soru:
  aynı cümle çoğunlukla aynı cevabı getiriyor, ve bu ajanın turu pahalı — Deneme 4'te tek tur
  16 raunt ve 277.6k jeton. Gerekirse ayrı madde.
- **Dosyalar geri gitmiyor, ve bu bilerek** *(kullanıcı kararı, 8 Eylül)*. Madde ilk taslakta Claude
  Code'un menüsüydü — *sohbeti çatalla / dosyaları geri al / ikisi birden* — ve dosya yarısı her turun
  öncesini saklayan bir kopya düzeni istiyordu. İstenen şeyin yanında büyük kaldı ve geri çekildi;
  `BACKLOG.md`'ye yazıldı. **Sonucu yazılı olsun:** eski bir sürümden koşan tur **bugünkü** dosyaları
  görür *(Madde 129: bağlam kabı diskten okuyor)*. Sürümler konuşmayı geri alıyor, **işi değil.**
- **Değişen:** `chat.py`'nin `Chat`'i ve çizgiyi türeten yeni işlevi; `FileChatStore`'un şeması;
  `append_message` ve `stream_answer`'ın hangi çizginin sonuna yazdığı; `routes.py`'de sürüm açan ve
  açık sürümü değiştiren uçlar; `useChat.js` ile `ChatScreen.jsx`; `dist`.

## Madde 197 — Düzenleme mesajın kendi yerinde olur

- **Sorun, iki parça.** Birincisi 195'in bıraktığı bir kusur: kalem bubble'ın **yanında** duruyor ve
  ikisi bir satır sarmalayıcısında *(`.msg__said`)*. `.msg` bir sütun ve kullanıcı mesajlarında
  `align-items: flex-end`, yani sağa yaslanan şey artık **sarmalayıcı**; bubble'ın `max-width: 78%`'i
  de `.msg`'in değil onun genişliğine göre çözülüyor. Sonuç, her mesajın sağ kenarının başka yere
  düşmesi — ekranda **kaymış** görünüyor *(kullanıcı, 8 Eylül)*.
- **İkincisi akış:** düzenlenen cümle **sohbet kutusuna** düşüyor, yani mesaj ekranın bir ucunda,
  düzeltmesi öteki ucunda. Kullanıcı kararı: düzenleme mesajın **kendi yerinde** olsun.
- **Ne çalışır:**
  - **Kalem bubble'ın altında** — sarmalayıcı kalkıyor, `.msg`'in sütunu geri geliyor, ve bubble'ın
    genişliği yine `.msg`'e göre ölçülüyor. Kusur böylece yapısal olarak kapanıyor; ayrı bir yama
    değil, aynı işin öteki yüzü.
  - **Basınca bubble'ın içi yazılabilir** oluyor: metin yerinde duruyor, kutuya taşınmıyor.
  - Altında **iki ikon** — ✓ ve ✕ *(kullanıcı kararı, 8 Eylül: kelime değil ikon)*. Adları
    `aria-label` ve `title` ile yazılı kalıyor, `Refresh` ve sürüm okları gibi: adı olmayan bir ikon
    ne klavyeye görünür ne teste.
  - **✓ bugünkü işi yapıyor** — o noktadan yeni sürüm açılır ve tur koşar *(Madde 195'in kapısı,
    `from` alanıyla)*. **✕** her şeyi eski hâline bırakır.
- **Kutuya doldurma yolu kalkıyor.** 195 metni `Composer`'a düşürüyordu ve o yol bu maddeyle
  ortadan kalkıyor — `Composer`'ın `filled` alanı da onunla birlikte, çünkü var olma sebebi buydu.
  İki yol bir işi yaparsa hangisinin koştuğu cevapta kaybolur.
- **Klavye kutununkiyle aynı** *(karar bu maddede)*: Enter onaylar, Shift+Enter satır açar, Escape
  vazgeçer. İki ayrı yazı alanının iki ayrı alışkanlık istemesi, ikisini de yanlış kullandırır.
- **Nasıl görülür:** bir mesajın altındaki kaleme basılır, bubble yazılabilir olur, düzeltilip ✓'e
  basılır — sohbet o noktadan yeni cevapla devam eder. ✕ ise mesajı olduğu gibi bırakır. Ve
  bubble'ların sağ kenarı, kalem varken de yokken de **aynı hizada** durur.
- **Değişen:** `ChatScreen.jsx`'in mesaj çizimi; `Composer.jsx`'ten `filled`; `workspace.css`'te
  `.msg__said` yerine düzenleme hâlinin kendi kuralları; `ChatScreen.test.jsx` ile `App.test.jsx`'in
  195'te yazılan düzenleme testleri; `dist`.

## Madde 199 — Sürüm şeridi ile kalem tek satırda durur

- **Sorun:** ikisi de bubble'ın altında, ama **alt alta** *(kullanıcı, 8 Eylül)*. Sebep 197'nin
  bıraktığı bir eksik değil, `.msg`'in kendisi: bir sütun, ve her çocuğu kendi satırını alıyor. 195
  şeridi, 197 kalemi ayrı ayrı oraya koydu, ve ikisi hiç yan yana gelmedi.
- **Ne çalışır:** bubble'ın altında **tek bir satır** — solda `‹ 2/3 ›`, sağında kalem, ikisi
  birlikte mesajın kendi yönünde yaslı. Emsali yine ChatGPT'nin sitesi, 195'in aldığı yerden.
- **Bubble sarmalanmıyor.** 197'nin kapattığı hizalama kusuru tam olarak bubble'ın bir sarmalayıcıya
  girmesiydi; buradaki satır yalnız **altındaki iki notu** tutuyor, bubble `.msg`'in doğrudan çocuğu
  kalıyor ve `78%`'i yine sütuna göre ölçülüyor.
- **Sıra: şerit solda, kalem sağda.** Göz önce nerede olduğunu okuyor, sonra değiştirme yoluna
  geliyor. Ters dizilseydi kalemin yeri şeridin var olup olmamasına göre kayardı — bir düğme, aynı
  mesajda iki ayrı yerde durur.
- **Satır boşken doğmuyor.** Cevabın altında ne kalem var ne şerit; boş bir `div` orada yalnız
  sütunun boşluğunu büyütürdü.
- **Düzenleme açıkken şerit kalıyor**, kalem çekiliyor *(197'nin kuralı)*. Satır tek başına şeritle
  duruyor: hangi sürümün düzeltildiği, düzeltilirken de okunabilir olmalı.
- **Nasıl görülür:** iki sürümlü bir mesajın altında `‹ 2/2 ›` ile kalem **yan yana** durur, ve tek
  sürümlü bir mesajın altında yalnız kalem kalır — ikisi de aynı satırda, aynı hizada.
- **Değişen:** `ChatScreen.jsx`'te bubble'ın altındaki satır; `workspace.css`'te satırın kuralı ve
  şeridin kendi payının kalkması; `ChatScreen.test.jsx`, `workspace.css.test.js`; `dist`.

---

# Dilim 6 — modele söylenen

Modele giden metinler: sistem promptunun kullanıcıya ait olan yarısı, ve akışı anlatan skill'in
kendisi.

## Madde 196 — Sistem promptunun ikinci parçası

- **Sorun:** besteci aynı işi bazen yapıyor, bazen reddediyor *(kullanıcı, 8 Eylül)*. Bugün sistem
  promptu araçları, dosyaları ve sohbeti anlatıyor — **ne için çalışıldığına dair tek cümle yok**,
  ve model açık etiketlerle hiçbir çerçeve olmadan bir sohbetin ortasında karşılaşıyor.
- **Ne çalışır:** `prompt.py`'de ikinci bir sabit, ve bestecinin sistem mesajı `SYSTEM_PROMPT`'un
  **arkasına** eklenerek kurulur. Önek değil **son ek** *(kullanıcı kararı, 8 Eylül)*.
- **İçeriğini kullanıcı yazar** *(kullanıcı kararı)*. Madde sabiti **boş** doğuruyor; ne yazacağı
  deponun değil, kullanıcının işi — ve bu yüzden metnin kendisi bu maddenin kapsamında değil.
- **Boşken hiçbir şey değişmez.** Boş bir son ek isteğe ne satır ne boşluk ekler; giden mesaj
  bugünküyle **bayt bayt aynı** kalır. Sebebi temizlik değil: sistem promptu servisin sabit önek
  olarak sakladığı baş, ve fazladan bir boş satır o öneki daha ilk günden kaydırırdı.
- **189'un modülünde, öteki metinlerin yanında** *(kullanıcı kararı)*. Depo dışında bir dosya da
  konuşuldu ve seçilmedi: nöbetçi test *"depoda başka hiçbir yerde prompt yok"* diyor, ve dışarıda
  duran bir metin o kuralın etrafından dolaşırdı. Bedeli, metnin git'e girmesi.
- **Boş kalma hakkı var, ve nöbetçinin bunu bilmesi gerekiyor:**
  `test_the_prompt_module_holds_the_texts_the_others_gave_up` listelediği her adın **dolu** olmasını
  istiyor. Bu sabit o listeye **girmez** — girerse madde kendi testini kırmızı doğurur.
- **Yalnız besteci.** Kareyi yazan modelin sistem metni ayrı ve ona dokunulmuyor *(`write_once`,
  Madde 175: orası araçların değil, tek cümlelik bir işin metni)*.
- **Nasıl görülür:** sabit doldurulur, bir tur koşulur, ve giden sistem mesajının **sonunda** o metin
  durur. Boş bırakılırsa istek eskisinin aynısıdır.
- **Ölçülmemiş, ve kayda öyle geçiyor:** çerçevenin reddi azaltacağı bir beklenti, ölçüm değil.
  Bugün elimizde tek bir sayı yok — ne kadarının değiştiğini görmek için aynı işin birkaç kez
  koşulması gerekir, ve o ayrı bir iş.
- **Değişen:** `prompt.py`'ye yeni sabit; `xai_engine._for_xai`'nin sistem mesajını kurması;
  `test_prompt.py` ve `test_xai_engine.py`.

## Madde 198 — Akış karakterle başlar, ve plan yapıldıkça işaretlenir

- **Sorun, birincisi 186'nın kendi kararı:** akış bir **bağlam sorusuyla** açılıyor — *ne yapılıyor,
  ne için*. Gerekçesi doğruydu *(plan o satırı bilmeden yazınca uyduruyor)*, ama kullanılınca bedeli
  görüldü: iş başlamadan önce cevaplanacak bir soru. **Kullanıcı kararı, 8 Eylül: kalksın, ilk soru
  karakterler olsun.**
- **İkincisi plan:** işaretlenmesi **zaten yazılı** — *"An approved step's line in the plan is marked
  done with one edit_file"*. Tutmamasının sebebi talimat değil, **biçim**: işaretlenmiş bir adımın
  neye benzediğini hiçbir yer söylemiyor, model her turda kendi işaretini uyduruyor, ve sonraki tur
  onu tanımıyor. Planın bütün değeri taze bir sohbetin *"nerede kalındı"* sorusuna cevap vermesi —
  tanınmayan bir işaret o cevabı vermiyor.
- **Ne çalışır — beş adım:**

  | | Adım | 186'dan farkı |
  |---|---|---|
  | 1 | Plan yazılır | 2. adımdı; bağlam satırı **düşüyor** |
  | 2 | Karakterler *(+ kıyafetler)* | `start_scenario` **buraya dönüyor** |
  | 3 | Mekânlar | aynı |
  | 4 | Sahneler | aynı |
  | 5 | Promptlar üretilir ve iş biter | aynı |

- **`start_scenario` karakter adımına dönüyor** *(kullanıcı kararı, 8 Eylül)*, 186 öncesindeki
  yerine. Dosyanın adını veren şey bağlamdı ve o gidiyor; ilk karakter geldiğinde dosya doğuyor.
  186'nın kabul ettiği bedel de tersine dönüyor: bağlamı söyleyip vazgeçen kullanıcı artık ardında
  boş bir `.json` bırakmıyor.
- **Plan kalıyor, ve sebebi kullanıcının kendi sebebi** *(8 Eylül)*: sohbet değişince nerede
  kalındığını bilen tek şey o. Kalkan yalnız **açılış bağlam satırı** — model kendisine
  söylenmemiş bir şeyi yazmaz.
- **Adımlar kutulu, ve işareti kod koyar:** plan `- [ ]` satırlarıyla yazılıyor, ve onaylanan bir
  adımı **kendi aracı** işaretliyor — `edit_file` ile serbest bir düzenleme değil. Bu deponun
  ilkesi bunu zaten söylüyor *(FOUNDATION 5: modelin her seferinde aynı çıkarması gereken şeyi
  deterministik bir işlev yapar)*, ve kazancı iki taraflı: işaret her turda aynı, ve **bir sonraki
  sohbet onu okuyabiliyor.**
- **Nasıl görülür:** yeni bir sohbette *Start a scenario* seçilir ve ilk soru **karakter** olur.
  Plan dosyası açılınca adımlar kutulu durur; bir adım onaylanınca o adımın kutusu **dolu** olur, ve
  sohbeti kapatıp yenisinde plan okununca ilerleme aynen görünür.
- **Değişen:** `prompt.py`'de `START_A_SCENARIO`'nun adımları ve `WRITE_PLAN`'in plan biçimi;
  `tools.py`'de adımı işaretleyen yeni araç ile `run_tool`'un dalı; `modes.py`'nin hangi modda
  çağrılabildiği; `test_skills.py`, `test_tools.py`, `test_modes.py`.
- **186 ile ilişkisi:** o madde duruyor ve numarası yerinde; bu madde onun **1. adımını** kaldırıyor
  ve `start_scenario`'yu geri taşıyor. Bir karar, kullanılınca değişti — kayıt ikisini de tutuyor.

---

# Dilim 7 — çıkan etiket, ve onu yazan

Üçü de aynı denemeden çıktı *(kullanıcı, 8 Eylül)*: etiketler **Danbooru sözlüğüyle** yazıldığında
görüntü belirgin şekilde daha iyi çıkıyor, ve DeepSeek artık istenen işi yapıyor — yani eylem
satırını ayrı bir modele yazdırmanın sebebi kalmadı.

## Madde 200 — Etiketler Danbooru sözlüğüyle yazılır

- **Sorun:** `SDXL_PROMPT_RULES` bugün *"kısa, virgülle ayrılmış parçalar"* diyor ve **hangi
  sözlükten** olduğunu hiç söylemiyor. Örnekleri de yarı serbest cümle — `woman in her mid 20s`,
  `cozy bedroom, morning light through curtains`. Model iyi bir etiket yazdığında bu tesadüf, kural
  değil.
- **Neden önemli, ve mekanizma:** anime tarafındaki SDXL checkpoint'leri *(Pony, Illustrious,
  NoobAI, Animagine)* Danbooru görsellerini **o sitenin etiket dizisi caption olarak** eğitildi.
  `looking at viewer` modelin gördüğü stringin ta kendisi; aynı şeyin serbest tarifi ise eğitimde
  hiç geçmedi ve metin kodlayıcıda dar bir yere değil, yakın gördüklerinin **ortalamasına** düşüyor.
  Ortalama bulanık demek. Üstüne Danbooru'nun sözlüğü **kontrollü**: bir kavramın tek yazılışı var,
  eşanlamlı yarışmıyor — ve 77 token'lık pencerede etiket, cümleden kat kat yoğun.
- **Ne çalışır:** kural, etiketlerin **Danbooru etiketleri** olduğunu söyler, ve örnekleri o sözlükten
  verir. Karakter, kıyafet ve mekân parametrelerinin örnek metinleri de aynı dile çevrilir.
- **Metin `superpowers:writing-skills` ile gözden geçirilir** *(kullanıcı isteği, 186'daki gibi)*.
- **Kapsam dışı, ve bilerek:** kalite önekleri. `build_prompts` onları zaten prompt'un başına
  koyuyor, ve kural modele *"sen kalite etiketi yazma"* demeye devam ediyor.
- **Gerçekçi checkpoint'ler için değil, ve kayda öyle geçiyor:** base SDXL, Juggernaut, RealVis gibi
  foto modelleri BLIP tarzı **doğal cümlelerle** caption'landı; orada bu kural yanlış yöne çeker. Bu
  deponun ürettiği görselin modeli anime tarafında, ve kural ona göre yazılıyor.
- **Nasıl görülür:** bir karakter eklenir ve dosyaya inen satır Danbooru etiketleridir.
- **Değişen:** `prompt.py`'de `SDXL_PROMPT_RULES` ve üç `*_TAGS` metni; `test_tools.py`'nin o
  cümleleri pinleyen testleri.

## Madde 201 — Eylem satırını ana ajan kendi düzeltir

- **Sorun:** `update_frame` bugün action'a **bilerek dokunmuyor** — *"A frame's action is not among
  these"* — ve düzeltmenin tek yolu `write_frame_prompt`'u notla yeniden çağırmak, yani ikinci bir
  modele gitmek. Madde 175 bunu bir sebeple böyle kurmuştu, ve o sebep kalktı: **DeepSeek artık
  isteneni yazıyor** *(kullanıcı, 8 Eylül)*.
- **Ne çalışır:** `update_frame` bir `action` alanı alır, ve *Edit prompts* düzeltmeyi ajanın kendi
  turunda yaptırır. Ajan cümleyi zaten okuyor ve kullanıcının ne istediğini zaten biliyor; bugünkü
  yol o bilgiyi bir nota sıkıştırıp başka bir modele veriyor, ve **not, yazarın duyduğu her şey.**
- **İki yol değil, tek cümleyle söylenebilir bir ayrım:** **ilk yazım** uzman modelin
  *(`write_frame_prompt`, ve toplu hâli `write_missing_actions`)*, **düzeltme** ajanın. Boş bir kare
  ile yanlış bir kare aynı iş değil: birinde yazılacak bir şey yok, ötekinde okunacak bir cümle ve
  ona söylenmiş bir itiraz var.
- **Nasıl görülür:** bir karenin eylem satırı düzeltilir ve tur **tek raundda** biter — ikinci bir
  modele istek gitmez, ve damgada o harcama görünmez.
- **Değişen:** `tools.py`'de `update_frame`'in şeması ve dalı; `prompt.py`'de `UPDATE_FRAME`,
  `EDIT_PROMPTS` ve `WRITE_FRAME_PROMPT` metinleri; `test_tools.py`, `test_skills.py`.

## Madde 202 — Kareyi yazan model de DeepSeek olur, ve son eki taşır

- **Sorun:** `write_missing_actions` her kare için ayrı istek atıyor ve hepsi **Grok 4.3**'e gidiyor
  *(`config.PROMPT_MODEL`, Madde 183)*. Kullanıcı kararı, 8 Eylül: orası da DeepSeek olsun.
- **Ne çalışır:** `PROMPT_MODEL = "deepseek-v4-flash"`. Tek sabit, yani `write_frame_prompt` de
  onunla birlikte taşınıyor — ikisi zaten aynı yazarı çağırıyor, ve birini bırakıp ötekini taşımak
  aynı işi iki modele böler.
- **Ve o isteğe `SYSTEM_PROMPT_SUFFIX` eklenir** *(kullanıcı kararı, 8 Eylül: yoksa çalışmaz)*.
  `WRITE_FRAME_SYSTEM_PROMPT` son eki taşır. Bu **196'nın kararını tersine çeviriyor** — orada
  *"yalnız besteci, kareyi yazan modelin metnine dokunulmuyor"* yazıyordu, ve gerekçesi yazarın
  başka bir servis olmasıydı. Yazar artık aynı servis, ve çerçevesiz karşılaşan taraf o.
- **196'nın boşluk kuralı burada da geçerli:** son ek boşken istek **bayt bayt** bugünküyle aynı
  kalır.
- **`grok-4.3` satırı `MODELS`'te kalıyor**, ve bu 183'ün *"kimse kullanmayacak satır ölü
  yapılandırma"* kuralına bilerek verilen bir istisna: satırı silmek `XAI_API_KEY`'i ve notebook'un
  üç sırrını da peşinden sürüklerdi, ve bu koşu *"modeli değiştirelim"* diye açıldı. Geri dönüş tek
  sabit. Eylem satırları DeepSeek'te kötü çıkarsa yol açık duruyor.
- **Nasıl görülür:** boş kareli bir dosyada `write_missing_actions` koşulur ve harcama **DeepSeek**
  tarafında görünür, xAI tarafında hiçbir şey görünmez.
- **Değişen:** `config.py`'nin bir satırı; `prompt.py`'de kareyi yazanın sistem metnini kuran işlev;
  `test_config.py`, `test_prompt.py`, `test_tools.py`.

---

# Dilim 8 — kapanış

Koşunun son işi, ve **kullanıcının kendi işi.**

## Madde 190 — Modele giden her metin tek oturumda okunur

> **Bu maddeyi kullanıcı yapıyor, ajan değil** *(kullanıcı kararı, 6 Eylül)*. Koşu buraya gelince
> ajan **durur ve haber verir**; kendi başına başlamaz.

- **Sorun:** hepsi madde madde yazıldı. Her biri kendi turunda doğruydu; **hiçbir tur ötekinin
  yanında nasıl okunduğuna bakmadı.**
- **Ne okunur:** 189'un topladığı dosyanın tamamı — `SYSTEM_PROMPT`, `LAST_ROUND`, skill metinleri,
  araç açıklamaları ve parametre metinleri, `SDXL_PROMPT_RULES`, `WRITE_FRAME_SYSTEM_PROMPT`, hazır
  parçalar, ve araçların cevap cümleleri.
- **Hem temizlik hem geliştirme** *(kullanıcı kararı)*. Temizlik: çelişen iki cümle, iki yerde
  anlatılan aynı kural, bir metnin ötekinin işini yapması. Geliştirme: kalan cümlelerin daha iyi
  yazılması. İkisi bir arada, ve sınırı çizen kullanıcı.
- **Nasıl görülür:** silinen her cümle için, onu gereksiz kılan öteki metin adıyla gösterilir.
- **En sonda, ve sebebi:** 183 yazarın kimliğini, 186 skill metinlerini değiştiriyor, 189 hepsini tek
  yere taşıyor, 187 yenilerini ekliyor. Bunlardan önce yapılan bir okuma, dördünden sonra yeniden
  yapılmak zorunda kalırdı. 191–195 modele giden metne hiç dokunmuyor, yani onların arkasında
  beklemesinin bir maliyeti yok — ve beklerken ajan tarafındaki hiçbir işi bloklamıyor. 196 sistem
  promptuna bir son ek **yeri** açıyor ama içini doldurmuyor, ve dolduran metin kullanıcının kendi
  metni: bu okumanın konusu deponun yazdığı metinler, o değil. Yine de önce koşuyor, ki okuma
  yapılırken mekanizma yerinde olsun.
- **Nasıl koşuyor** *(kullanıcı kararı, 9 Eylül)*: okuma sürerken **yalnız belge** değişiyor —
  düzeltilen cümle [okuma kopyasında](../../2026-09-09-queenagent-modele-giden-metinler.md) yeni
  hâliyle duruyor, eskisi ve gerekçesi
  [düzeltme log'unda](../../2026-09-09-queenagent-metin-duzeltmeleri.md). **Kod ve testler okumanın
  sonunda, tek geçişte** güncelleniyor: cümle cümle koda inmek okumayı bölüyor. O geçişte
  `test_prompt.py`'nin cümle tutan testleri **kuralı tutacak** şekilde gevşetilecek — silinmeyecek,
  çünkü her biri bir denemenin dersi.
- **Kod geçişi koştu ve kapandı** *(10 Eylül; `1a4cbf3` kırmızı, `5bb0f94` kırmızı, `2d11881`
  yeşil)*. Okuma kullanıcıyla bitmişti; ajanın işi kararlaştırılmış cümleleri koda indirmekti, ve
  hiçbir metin kararı bu geçişte verilmedi. Testler gerçekten gevşetildi, hiçbiri silinmedi.
  Geçişin kendi iki bulgusu: test turunun kaçırdığı üç test *(altı indeks testi çevrilmişti,
  yedincisi eski başlığı elle tutuyordu)*, ve akış metninin **480/450** ile tavanı aşması — kararı
  9 numaralı düzeltme önceden vermişti, ve kesim [36 numarada](../../2026-09-09-queenagent-metin-duzeltmeleri.md)
  yazılı.

## Madde 203 — Adımı işaretleyen araç kalkar

> **190'dan sonra** *(kullanıcı kararı, 9 Eylül)*. Okuma sırasında bu araç soruldu; kararı okuma
> bitmeden koşmuyor.

- **Sorun:** `mark_step_done` yalnız bir kutuyu dolduruyor, ve bunu `edit_file` de yapabilir.
- **Kurulduğu gerekçenin yarısı artık geçerli değil.** 198 iki şeyi birden yaptı: planı `- [ ]`
  kutularıyla **yazdırdı**, ve kutuyu dolduran aracı ekledi. Aracın asıl gerekçesi *"model her
  turda kendi işaretini uyduruyor, sonraki tur tanımıyor"*dı — ama onu çözen şey **kutu biçimi**,
  araç değil. Biçim sabitlendiği andan itibaren `edit_file`'ın çapası da sabit: `- [ ] 3.` →
  `- [x] 3.`, ve model bu iki dizeyi **dosyayı okumadan** kurabiliyor.
- **Aracın kalan kazancı, ve kaydı dürüst olsun:** cevapları *(`Ticked`, `Already done`,
  `Nothing to tick`, `No plan by that name`)*, ve tek satırdan fazlasına dokunamaması. `edit_file`
  ile bunlar ret cümlelerine dönüşür — çapa bulunamazsa *"o metin yok"* der, ve hangi adımın zaten
  dolu olduğunu model kendi okumasından çıkarır.
- **Kip kapısı değişmiyor:** `edit_file` de `mark_step_done` da yalnız EDIT'te sormadan koşuyor,
  yani plan kipi iki yolda da adım kapatamıyor.
- **Ne çalışır:** araç, şeması, `run_tool` dalı ve `modes.py` satırı kalkar; `START_A_SCENARIO`'nun
  kapanış maddesi ile `WRITE_PLAN`'in kutu cümlesi `edit_file`'ı anar; `_ticked` ve testleri gider.
- **Nasıl görülür:** bir adım onaylanır, plan dosyasında o adımın kutusu dolar, ve dosyanın gerisi
  değişmemiştir — tek fark araç adında.
- **Değişen:** `tools.py`, `modes.py`, `prompt.py`; `test_tools.py`, `test_modes.py`,
  `test_skills.py`, `test_prompt.py`.
- **Sapma, ve kullanıcının kararı** *(10 Eylül)*: yukarıdaki *"kapanış maddesi `edit_file`'ı anar"*
  **olmadı** — madde tümüyle düştü. Gerekçe 11 numaralı düzeltme: nerede kalındığını dosyalar
  söylüyor, kutular *"yalnız bir not"*, ve bir notu dolduran madde 36 numarada üç cümle kesilen bir
  metinde yer tutuyordu. Kutu biçimi duruyor — plan `- [ ]` diye yazılmaya devam ediyor, insan
  okusun diye. Böylece *"nasıl görülür"* de değişti: bir adım onaylanır, akış bir sonrakine geçer,
  ve plan dosyasına hiçbir tur dokunmaz.
- **Kaldırma kuyruğu:** `plan_name`'in son çağıranı bu aracın geri düşüşüydü *(207'nin bıraktığı)*;
  araçla birlikte o da gitti. 206'nın `folded`'ıyla aynı biçim.
- **Kapandı** *(10 Eylül; `0e631bf` kırmızı, `edfdecc` yeşil)*. Araç sayısı **19 → 18**.

---

## Madde 205 — Hazır parça aracı ve kütüphanesi kalkar

> **190'ın kod geçişinden önce** *(kullanıcı kararı, 10 Eylül)*. Tersi sıra, birkaç gün sonra
> silinecek bir metni önce koda indirmek olurdu — 35 numara bu aracın tarifini de yeniden yazmıştı,
> ve bu madde onu tümüyle kaldırdığı için o yazım koda hiç inmeyecek.

- **Sorun:** `read_prompt_piece` **hiçbir skill metninde geçmiyor** — ne `start-a-scenario` ne
  `edit-prompts` ondan söz ediyor. Tarifi yine de her istekte gidiyor, ama yalnız kullanıcı bir
  parçayı adıyla isterse çağrılıyor.
- **Kütüphane üretilen hiçbir kareye değmiyor.** `_frame_seen` kareyi yazan modele yalnız sahneyi,
  kadroyu ve mekânı veriyor; yedi parçayı görmüyor. Yani depoda özenle yazılmış, sürüm kontrollü
  yedi pozisyon var ve tek okuyucuları, kullanıcının adıyla sorması hâlinde çalışan bir arama aracı.
- **187'nin gerekçesinin yarısı ayakta, yarısı değil.** *"Bilinen şey her seferinde yeniden
  yazdırılıyor, ve iki kez yazılan şey iki türlü okunuyor"* doğruydu ve doğru kalıyor. Tutmayan
  kısım, o ortak metnin akışın **içine** hiç girmemiş olması: ne skill onu anıyor, ne yazar görüyor.
- **Kütüphane de kalkıyor** *(kullanıcı kararı, 10 Eylül)*. Araç gidince `PROMPT_PIECES`'ı okuyan
  kimse kalmıyor, ve okuyucusu olmayan bir prompt metni ölü koddur — 189'un *"depoda başka yerde
  prompt yok"* nöbetçisiyle de gerilim yaratırdı.
- **Pozisyonlar ileride gerekirse doğru biçim başka:** parçaları **kareyi yazan modele** vermek.
  O ayrı bir madde, ve taşınmamış bir tasarım sorusu taşıyor — hangi parçanın hangi sahneye uyduğunu
  kim seçecek: yazar yedisini birden mi görecek, yoksa ajan notta mı söyleyecek?
- **Ne çalışır:** araç, şeması, `run_tool` dalı ve `modes.py`'nin `READS` girdisi kalkar;
  `prompt.py`'den `PROMPT_PIECES` ile `READ_PROMPT_PIECE` metinleri gider; `_read_prompt_piece` ve
  testleri gider. Belgenin §7'si kapanır, §6'dan bir araç düşer.
- **Nasıl görülür:** araç listesinde bir araç eksik, ve her istek onun tarifi kadar kısalıyor.
  Kullanıcı bir pozisyon isterse ajan onu kendi kelimeleriyle yazıyor — 187'den önceki hâl.
- **Değişen:** `prompt.py`, `tools.py`, `modes.py`; `test_tools.py`, `test_modes.py`; belgenin
  §6 ve §7'si.

---

## Madde 206 — Karakter önizleme aracı kalkar

> **190'ın kod geçişinden önce** *(kullanıcı kararı, 10 Eylül)*, 205'in sebebiyle: 35 numara bu
> aracın tarifini de yeniden yazdı, ve kalkacak bir metni önce koda indirmek işi iki kez yapmaktır.

- **Sorun:** `build_character_prompts` bir karakteri, dosyadaki her kıyafetle, kare dışında
  gösteriyor. Bir **önizleme**, yani senaryonun çıktısına hiçbir şey katmıyor: yazdığı dosya
  `build_prompts`'un yazdığı listeye girmiyor, ve hiçbir kare ondan beslenmiyor.
- **Akış artık onu sunmuyor.** Kodun bugünkü `START_A_SCENARIO`'su hâlâ
  *"Offer build_character_prompts as a look at one character; carry on if declined"* diyor, ama
  okumanın düzelttiği hâlinde o cümle yok. Yani araç zaten akıştan düşmüş durumda ve yalnız
  kullanıcı adıyla isterse çağrılıyor — 205'in `read_prompt_piece` için yazdığı durumun aynısı.
- **Bedeli her istekte ödeniyor:** tarifi ve iki parametresi, kimse önizleme istemese de gidiyor.
- **Ne çalışır:** araç, şeması, `run_tool` dalı ve `modes.py`'nin EDIT listesindeki girdisi kalkar;
  `build_prompts.py`'den `build_character_prompts` fonksiyonu, `prompt.py`'den tarifi ve
  parametreleri gider; `START_A_SCENARIO`'nun onu sunan cümlesi gider; testleri gider.
- **Nasıl görülür:** kullanıcı bir karakteri tek başına görmek isterse ajan ona karakterin
  girdisini okuyup gösterir — dosya yazmadan. Senaryonun çıktısı değişmez, çünkü bu araç ona zaten
  girmiyordu.
- **Değişen:** `prompt.py`, `tools.py`, `modes.py`, `build_prompts.py`; `test_tools.py`,
  `test_modes.py`, `test_build_prompts.py`; belgenin §3 ve §6'sı.

---

## Madde 207 — Plan yazan araç kalkar, kipin kendisi yeter

> **190'ın kod geçişinden önce** *(kullanıcı kararı, 10 Eylül)*. Bu madde 29 numaralı düzeltmenin
> cümlesini **geçersiz kılıyor**: taban metni bugün *"In plan mode write_plan writes it; in any
> other mode create_file does"* diyor, ve araç kalkınca o ayrım kalmıyor. Kod geçişi 29'u değil bu
> maddenin bıraktığı hâli indirir.

- **Sorun:** `write_plan` bir dosya yazıyor, ve `create_file` de bir dosya yazıyor. Aracın kendi
  başına taşıdığı tek şey kutu biçimiydi *(`- [ ] 1.`)*, ve **10 numaralı düzeltme onu zaten
  akışın kendi cümlesine taşıdı** — akış planını `create_file` ile yazıyor.
- **Kalan gerekçe araç değil kip.** Aracın bugün taşıdığı iki ayrıcalık `modes.py`'de duruyor:
  plan kipinde sormadan koşan tek yazma odur, ve turu bitiren çift odur *(`ends_the_turn`)*.
  İkisi de **kipin** davranışı, aracın değil.
- **Ne çalışır:** plan kipinin listesi `READS + ("create_file",)` olur, ve `ends_the_turn` plan
  kipinde `create_file`'ı gösterir. Böylece plan kipi bugünkü davranışını birebir korur: sormadan
  bir dosya yazar, ve o dosyayla turu bitirir.
- **Testin uyardığı şey böylece kapanıyor:** *"create_file verilirse planı ve işin kendisini aynı
  turda yazabilir"* — yazamaz, çünkü ilk yazma turu bitiriyor.
- **Bir davranış farkı var, ve kaydı dürüst olsun:** `write_plan` aynı adın **üzerine yazıyordu**;
  `create_file` alınmış adı reddedip `-2` ile numaralandırıyor *(Madde 179)*. 10 numara bu bedeli
  zaten yazdı ve kapatan kuralı da yazdı: plan yalnız ilk turda, yalnız ortada plan yokken yazılır.
- **Ne çalışır (devamı):** araç, şeması, `run_tool` dalı, `prompt.py`'deki tarifi ve parametreleri
  kalkar; taban sistem mesajının plan cümlesi *"a plan file… create_file writes it"* hâline iner;
  `WRITE_PLAN`'e yaslanan testler kipin testlerine döner.
- **Nasıl görülür:** plan kipinde bir plan istenir, dosya sorulmadan yazılır, tur biter — bugünkü
  akışın aynısı, tek fark araç adında.
- **Değişen:** `prompt.py`, `tools.py`, `modes.py`; `test_tools.py`, `test_modes.py`,
  `test_prompt.py`; belgenin §1 ve §6'sı.

---

## Madde 208 — Tek kare yazan araç kalkar, düzeltme aracı yeter

> **190'ın kod geçişinden önce** *(kullanıcı kararı, 10 Eylül)*, 205–207'nin sebebiyle.

- **Kuruluş sebebi düştü.** 174 aksiyonu dışarıda tuttu çünkü **ana model o cümleyi yazmıyordu**;
  176 yazacak bir modele verdi. 201'in kendi yorumu bunun artık doğru olmadığını yazıyor:
  *"That is no longer true of the model running the conversation."* Araç, kalkmış bir sebebin
  üstünde duruyor.
- **Ajanın elinde zaten her şey var.** `_frame_seen` yazara sahneyi, kadronun etiketlerini ve
  mekânı gösteriyor — üçü de ajanın kendi yazdığı, önünde duran şeyler. Satırı kendisi yazınca
  **tek çağrı** oluyor, ve ikinci sağlayıcıya para gitmiyor.
- **Not yolu kendi kendini çürütüyor:** bugün not, satırı **hiç okumamış** bir modele yazılıyor.
  201 bunu zaten *"bir düzeltmenin tamamını, satırı okumamış birine not olarak taşımak"* diye
  eleştirmişti; kalan yol o eleştirinin kendisi.
- **Toplu araç kalıyor, ve bu madde ona dokunmuyor.** `write_missing_actions` ilk yazımı toplu,
  paralel ve ucuz yapıyor — yirmi kare için ajanın yirmi turu yerine yirmi ucuz istek. Akışın
  5. adımı odur. `_frame_seen` ile yazarın sistem mesajı da onun için yerinde kalır; yalnız
  `_frame_seen`'in `note` parametresi ölür, çünkü toplu yol oraya hep `None` geçiyor.
- **Ses tutarlılığı, ve kaydı dürüst olsun:** kareler DeepSeek'ten geliyor, ajanın yazdığı bir kare
  öbürleriyle aynı üslupta olmayabilir. Bu ayrımı 201 açtı; bu madde onu **genişletiyor**, açmıyor.
- **Ne çalışır:** araç, şeması, `run_tool` dalı, `_write_frame_prompt`, `WRITE_FRAME_PROMPT` ve
  `WRITE_FRAME_PROMPT_NOTE` kalkar; `modes.py`'nin EDIT satırı kalkar; editör skill'inin
  *"sahneden yeniden yazılacak satır"* maddesi `update_frame`'e iner; `add_scene`'in *"a frame is
  born without its action, and write_frame_prompt is what writes one"* cümlesi
  `write_missing_actions`'ı anar; `write_missing_actions`'ın tarifindeki *"the same model
  write_frame_prompt asks"* kendi ayakları üstünde yazılır.
- **Nasıl görülür:** bir karenin satırı beğenilmezse ajan onu `update_frame` ile kendi yazar; boş
  kareler yine `write_missing_actions` ile toplu dolar.
- **Değişen:** `prompt.py`, `tools.py`, `modes.py`; `test_tools.py`, `test_modes.py`,
  `test_skills.py`; belgenin §3 ve §6'sı.

---

## Madde 209 — Sürüm arayüzde görünür

> **Sıra serbest** *(kullanıcı kararı, 10 Eylül)*. Öteki maddelerin hiçbirine dayanmıyor ve
> hiçbirini bloklamıyor; yalnız frontend'e dokunuyor.

- **Sorun:** koşudan koşuya atlıyoruz — V6, V7, V8 — ve **arayüzde hiçbir yerde görünmüyor.**
  Ekrana bakan biri hangi kuşağı çalıştırdığını bilmiyor.
- **Tek parça: koşu numarası, büyük harfle** — `V8`. Elle yazılan bir sabit, çünkü elle verilen bir
  karar: bir koşu başlarken değişiyor, başka hiçbir şeyle değişmiyor.
- **Derleme tarihi kapsam dışı** *(kullanıcı kararı, 10 Eylül)*. Taslakta vardı: notebook depoyu
  klonlayıp hiç derlemediği için bayat bir klonu ele verecek işaret oydu. O ihtiyaç duruyor ama bu
  maddenin işi değil — gerekirse kendi maddesini ister.
- **Nerede durur:** kenar çubuğunun wordmark'ının altında, `Sidebar.jsx`'te. Ad zaten orada, ve
  sürüm adın bir parçası gibi okunuyor. Çubuk katlanınca sürüm de katlanıyor — kendi başına bir
  yer açmıyor. **Test geçişi bu satırı reddetti** *(kullanıcı, 11 Eylül)*: altında değil **yanında**,
  aynı boyda ve kalın. Yeni hâli koşuyu değil [backlog'u](../../../queen-agent/BACKLOG.md) bekliyor.
- **Ne çalışır:** bir `VERSION` sabiti eklenir, `Sidebar` onu wordmark'ın altında gösterir, ve bir
  test sürümün ekranda olduğunu tutar.
- **Nasıl görülür:** uygulama açılır, kenar çubuğunda `QueenAgent` yazısının altında `V8` okunur.
- **Derleme kuralı geçerli:** frontend değiştiği için `dist` **aynı commit'te** derlenip
  commitlenir, yoksa notebook tarafında hiçbir şey değişmez.
- **Değişen:** `frontend/src/features/workspace/Sidebar.jsx` ve bir sürüm sabiti; `App.test.jsx`
  ya da `Sidebar`in kendi testi; ve `frontend/dist`.
- **queen-editor ayrı:** onun da kendi koşu numarası var ve aynı sorun orada da duruyor. Bu koşu
  yalnız QueenAgent — o kendi `BACKLOG.md`'sinin işi.

---

## Kapsam dışı, ve nerede duruyor

- **Madde 204 — ortak SDXL metninin bölünmesi.** Ayrı madde olarak yazıldı ve aynı gün geri
  çekildi *(kullanıcı kararı, 10 Eylül)*: iş **190'ın kendi içinde** yapılıyor, çünkü bölme bir
  metin kararı ve 190 zaten metinleri okuyor. Numarası boş kalıyor — 188'in sebebiyle. Kararın
  kendisi [düzeltme log'unun 34 numaralı kaydında](../../2026-09-09-queenagent-metin-duzeltmeleri.md):
  hangi cümlenin nereye gittiği de, nasıl yazıldığı da orada. Kod tarafı 190'ın kod geçişinde,
  ötekilerle aynı geçişte iniyor.
- **Madde 188 — promptların etiketleşmesi.** Taslak okunurken geri çekildi *(kullanıcı kararı,
  6 Eylül)* ve `BACKLOG.md`'ye döndü. Numarası boş kalıyor: bir numara bir kez verilir, ve boşluk
  onun geri çekildiğini söyler. Konuşmada varılan yer maddenin kendisinde yazılı — kısaca: sert bir
  kelime tavanı yanlış yol, ayırt edici işaret **özne, ad ve çekimli fiil.**
- **Dolu kareleri toplu yeniden yazmak** — 185'in kapsam dışı; 181 sebebini kaldırdı.
- **Dosyaların bir tur öncesine geri sarılması** — 195'in ilk taslağında vardı, tasarım konuşulurken
  geri çekildi *(kullanıcı kararı, 8 Eylül)* ve `BACKLOG.md`'ye döndü. Numarası hiç verilmedi: madde
  195 olarak yazılmadan önce ayrıldı.
- **queen-editor'ün maddeleri** — kendi `BACKLOG.md`'sinde: iki hata, üç LoRA işi, editör kısmı,
  MiniMax ve slime girl. Bu koşu yalnız QueenAgent.
- **Merge'den önce:** `queenagent.ipynb` ve `test_notebook.py`'nin `BRANCH`'i bu dala çevrilir, ve
  birleşmeden önce `main`'e döner. İkisi tek testle bağlı.
