# QueenAgent v8 — ne değişti, ve ne test edilir

**Dal:** `feat/queenagent-v8`, kapanış commit'i `543be16` *(sunucuda)*.
**Süit:** 923 arka uç + 652 ön uç, hepsi yeşil.
**Kaynağı:** [yol haritası](superpowers/plans/2026-09-06-queenagent-v8-roadmap.md) — yirmi beş madde,
183'ten 209'a, 188 ile 204 boş.

**Bu belge ne değil:** yol haritasının kopyası değil. Orası **neden** yapıldığını yazıyor; burası
**ne göreceğini**. Bir madde tıklanınca haritadaki karşılığına gidiyor.

v7'nin sorusu *"model dosyanın şeklini bilmeden senaryo kurabilir mi"*ydi. **v8'in sorusu ikisi:
çıkan prompt'un kendisi, ve koşarken ne gördüğün.**

---

## Önce şunu bil — beş beklenti değişti

Koşarken sonraki maddeler öncekilerin kararını değiştirdi. Eski hâli test edersen **çalışmadığını**
sanırsın, oysa bilerek öyle:

| Nerede | Eskiden | Bugün |
|---|---|---|
| Kareyi kim yazıyor | Grok 4.3 *(183)* | **DeepSeek** *(202)* — harcama xAI'da değil DeepSeek'te görünür |
| Akışın ilk sorusu | *"ne yapıyoruz, ne için"* bağlam sorusu *(186)* | **karakter** *(198)* — bağlam sorusu kalktı |
| Plan kutuları | onaylanan adımın kutusu doluyordu *(198)* | **hiçbir tur kutu doldurmuyor** *(203)* — kutular yazılıyor ama boş kalıyor, ve nerede kalındığını **dosyalar** söylüyor |
| Hazır pozisyon parçaları | araçla adıyla isteniyordu *(187)* | **araç ve kütüphane kalktı** *(205)* — ajan kendi kelimeleriyle yazar |
| Tek kare yazdırma | `write_frame_prompt` *(176)* | **kalktı** *(208)* — düzeltmeyi ajan `update_frame` ile kendi yapar |

Bir de **karakter önizleme** aracı kalktı *(206)*: bir karakteri tek başına görmek istersen ajan
girdisini okuyup gösterir, dosya yazmadan.

---

## Tek oturumda hepsini gören yol

Madde madde gitmek yerine bir senaryoyu baştan sona kurarsan aşağıdakilerin çoğu kendiliğinden
görünür. Sıra bu:

1. **Uygulamayı aç.** Kenar çubuğunda `QueenAgent`, altında `V8` *(209)*. Çubuğu katla, sürüm de
   gitsin.
2. **Üç proje aç.** *New project 1 / 2 / 3* diye listelensinler *(191)*.
3. **Bir sohbette *Start a scenario* seç.** İlk soru **karakter** olmalı *(198)*. Akış beş adım
   yürütür, her adım onayını bekler.
4. **Adımları yürüt** — karakterler, kıyafetler, mekânlar, sahneler. Uzun turlarda mesajın altındaki
   şeride bak: spinner döner, raund ve jeton artar, tur bitince damgaya döner *(194)*.
5. **Son adım:** boş kareler tek çağrıda dolar *(185)*, sonra prompt dosyası yazılır. Dosyayı aç,
   kopyala düğmesine bas *(193)*, ve promptun **sırasını** oku: karakterler art arda, mekân sonda
   *(184)*, etiketler Danbooru sözlüğünden *(200)*.
6. **Bir şeyi beğenme.** *Edit prompts* seç: bir karenin eylem satırını düzelttir — **tek raundda**
   bitmeli, ikinci bir modele istek gitmemeli *(201, 208)*.
7. **Bir mesajı düzenle.** Kalem bubble'ın altında, sürüm şeridiyle **aynı satırda** *(197, 199)*;
   düzeltince sohbet o noktadan yeni cevapla devam eder, `‹ 1/2 ›` ile eskisine dönülür *(195)*.

---

## Madde madde

Kutuları işaretleyerek ilerleyebilirsin.

### Modeller ve para

- [ ] **183 · Prompt yazan model** — `PROMPT_MODEL` sabiti kuruldu. **202 bunu değiştirdi**, aşağı
  bak. Bugünkü değer `deepseek-v4-flash`.
- [ ] **202 · Kareyi yazan da DeepSeek, ve son eki taşır** — boş kareli bir dosyada
  `write_missing_actions` koştur: harcama **DeepSeek** tarafında görünsün, xAI tarafında hiçbir şey
  görünmesin. Ayrıca sistem promptunun ikinci parçası artık **kareyi yazan modele de** gidiyor.

### Çıkan prompt

- [ ] **184 · Prompt sırası** — iki kişilik bir kare derle: iki karakter bloğu **art arda**, mekân
  **en sonda**.
- [ ] **200 · Etiketler Danbooru** — bir karakter ekle, dosyaya inen satır Danbooru etiketleri olsun
  *(`1girl, long hair, black hair`)*, serbest cümle değil.
- [ ] **185 · Bütün boş kareleri dolduran araç** — yirmi kareli boş bir dosyada **tek çağrı**;
  damga bir raundun harcamasını gösterir. İkinci çağrı *"yazılacak boş kare yok"* der.
- [ ] **201 · Eylem satırını ana ajan düzeltir** — bir kareyi düzelttir, tur **tek raundda** bitsin.
- [ ] **208 · Tek kare yazan araç kalktı** — beğenilmeyen bir satırı ajan `update_frame` ile kendi
  yazar; boş kareler yine toplu dolar. İki yol yerine tek yol.

### Akış ve skill metinleri

- [ ] **186 · Edit prompts skill'i** — iki skill var: *Start a scenario* baştan sona kurar,
  *Edit prompts* var olanı düzeltir. *Generate prompts+* yok.
- [ ] **198 · Akış karakterle başlar** — ilk soru karakter. Plan dosyası `- [ ]` kutularıyla
  yazılır. **Kutuların dolması 203'te kalktı.**
- [ ] **203 · Adım işaretleme aracı kalktı** — bir adım onaylandığında plan dosyasına **hiçbir tur
  dokunmaz**. Sohbeti kapatıp yenisinde devam ettir: nerede kalındığını **projedeki dosyalar**
  söylemeli *(senaryo dosyası varsa 2. adım başlamış, prompt dosyası varsa 5. adım bitmiş)*.
- [ ] **207 · Plan yazan araç kalktı** — **plan kipinde** bir plan iste: dosya sorulmadan yazılsın
  ve tur bitsin. Tek fark araç adında, akış aynı.
- [ ] **205 · Hazır parça aracı kalktı** — bir pozisyon iste; ajan kendi kelimeleriyle yazsın.
- [ ] **206 · Karakter önizleme aracı kalktı** — bir karakteri tek başına göster dediğinde ajan
  girdisini okuyup göstersin, **dosya yazmadan**.
- [ ] **196 · Sistem promptunun ikinci parçası** — senin kendi metnin. Bir tur koştur; giden sistem
  mesajının **sonunda** durmalı. Boş bırakılırsa istek eskisinin aynısı.

### Ekranda görünen

- [ ] **191 · Yeni proje numaralanır** — üst üste üç proje: *New project 1 / 2 / 3*.
- [ ] **192 · Dosyalar tazelenir** — tur bitince yeni dosya listede belirir; açık duran bir dosyanın
  içeriği değiştiyse yenisi görünür. **Refresh** düğmesi ikisini de turdan bağımsız yapar
  *(dosya listesinde ve dosya panelinde birer tane)*.
- [ ] **193 · Kopyala düğmesi** — dosyayı aç, ikona bas, içerik panoda.
- [ ] **194 · Canlı tur şeridi** — çok raundlu bir tur koşarken spinner döner, kelime değişir, raund
  ve jeton artar; tur bitince aynı satır **damga** olur.
- [ ] **195 · Düzenlenen mesaj sohbeti sürümler** — üç mesajlık sohbette ikinciyi düzenle: sohbet o
  noktadan yeni cevapla devam etsin, `‹ 1/2 ›` ile eskisine dönülsün, eski cevap **olduğu gibi**
  dursun. Sayfayı yenile: açık sürüm hâlâ açık olmalı.
- [ ] **197 · Düzenleme mesajın kendi yerinde** — kaleme bas, **bubble'ın kendisi** yazılabilir
  olsun; ✓ gönderir, ✕ olduğu gibi bırakır. Bubble'ların sağ kenarı kalem varken de yokken de
  **aynı hizada**.
- [ ] **199 · Şerit ve kalem tek satırda** — iki sürümlü bir mesajın altında `‹ 2/2 ›` ile kalem
  **yan yana**; tek sürümlüde yalnız kalem, aynı satırda.
- [ ] **209 · Sürüm görünür** — kenar çubuğunda adın altında `V8`; çubuk katlanınca o da gider.

### Görünmeyen ama önemli

Bunlar ekranda görünmez; **kod ve metin** tarafı, ve testleri tutuyor.

- [ ] **189 · Modele giden her metin tek dosyada** — `prompt.py` baştan sona okunabilir, ve modele
  giden her cümle orada.
- [ ] **190 · Metinlerin okunması** — hepsi tek oturumda okundu, **36 düzeltme** aldı.
  [Okuma kopyası](2026-09-09-queenagent-modele-giden-metinler.md) kodun aynası: bir cümlenin ne
  dediğini merak edersen oradan oku, ve gerekçesini
  [düzeltme log'undan](2026-09-09-queenagent-metin-duzeltmeleri.md).
- [ ] **187 · Hazır prompt parçaları** — eklendi, ve **205'te kaldırıldı**. Numarası kayıtta duruyor.

---

## Test ederken göze çarpması gerekenler

Bunlar tek bir maddenin değil, koşunun **toplamının** sonucu:

- **Araç sayısı 23'ten 18'e indi.** Her aracın tarifi **her istekte** gidiyordu, yani beş aracın
  kalkması her turu kısalttı. Model bir araç adı uydurup *"böyle bir araç yok"* cevabı almamalı.
- **Metinler madde madde yazıldı** *(emir başa, sebep arkaya)*. Zayıf bir modelin ortayı atlaması
  bu koşunun asıl derdiydi — akış ve düzeltme metinleri artık başlık + madde biçiminde.
- **Ajan iki kere sormamalı.** Akışın her adımı onay bekliyor, ama *"sen karar ver"* dendiğinde
  **yalnız o adım** için geçerli; bir sonraki adımın sorusu yine sorulmalı.
- **Kapanış mesajı bir menü olmamalı.** Son adım dosyayı adıyla söyler, hazır olduğunu söyler, ve
  **hiçbir şey teklif etmez**.

---

## Bir şey ters giderse

- **Metin yanlış geliyorsa** — cümlenin bugünkü hâli
  [okuma kopyasında](2026-09-09-queenagent-modele-giden-metinler.md), gerekçesi
  [log'da](2026-09-09-queenagent-metin-duzeltmeleri.md). İkisi de kodla eşit; kod değişirse doğru
  olan koddur.
- **Bir madde neden böyle diye sorarsan** — [yol haritası](superpowers/plans/2026-09-06-queenagent-v8-roadmap.md),
  her maddenin *Sorun / Ne çalışır / Nasıl görülür* satırları.
- **Ön uçta bir şey görünmüyorsa** — `dist` her ön uç commit'inde derlendi; notebook depoyu klonlar
  ve hiç derlemez, yani orada gördüğün şey son push'un `dist`'idir.
