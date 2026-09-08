# QueenAgent v8 Yol Haritası — çıkan prompt, ve koşarken görünen

**Kaynağı:** `queen-agent/BACKLOG.md`, 6 Eylül — artı **195 ve 196, koşu sürerken eklendi**
*(kullanıcı, 8 Eylül; backlog'dan değil, doğrudan)*. **On altı madde**, yedi dilim, 183'ten 199'a — **188 yok**,
taslak okunurken geri çekildi *(aşağıda)*. Numaralar 182'nin ardından gidiyor ve **hiç kaymıyor** —
yazılmış spec'ler onlara atıf yapıyor, ve çekilen bir numara boş kalır.

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
| 190 · metinlerin okunması | **kullanıcının**, ajan durdu | |

183–187, 189, 191–199 kapandı. Ajan 194'ün ardından durmuştu; koşu **195 ve 196 ile yeniden
açıldı** *(kullanıcı, 8 Eylül)*. Ardından **197 ve 198** eklendi, ikisi de denemeden çıktı: 195'in
düzenleme akışının yeri yanlış bulundu *(ve aynı yerde 195'in bıraktığı bir hizalama kusuru vardı)*,
186'nın bağlam sorusu ise sürtünme olarak görüldü. **199 da aynı yerden** geldi: 197 kalemi bubble'ın
altına indirdi, ve sürüm şeridiyle alt alta düştüğü orada görüldü. **Ajanın işi yine burada bitti**:
geriye 190 kalıyor, ve o kullanıcının kendi maddesi. 196'nın sabiti de boş — ne yazılacağı
kullanıcının.
190 hâlâ kullanıcının kendi maddesi ve en sonda. 196'nın sabiti de kullanıcıyı bekliyor: açılan yer
şimdilik boş.

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

# Dilim 7 — kapanış

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

---

## Kapsam dışı, ve nerede duruyor

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
