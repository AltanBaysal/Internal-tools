# Queen Editor — Yol Haritası v5

**Tarih:** 2026-09-11 · **Koşu dalı:** `feat/queen-editor-v5` · **Durum:** 5/8
**Öncesi:** [20 Ağustos'ta v14 adıyla kapanan koşu](2026-08-20-queen-editor-v4-roadmap.md) — neden o
adın yanlış olduğu 210. maddenin konusu.
**Kaynak:** 211–214 [queen-editor/BACKLOG.md](../../../queen-editor/BACKLOG.md)'dan çıkıp buraya
girdi ve orada kalmadı; artık tek kayıtları bu belge. 210, 215 ve 216 kullanıcının 11 Eylül'deki
sözlerinden doğdu, backlog'a hiç uğramadan.

**Numara kimliktir, sıra değildir.** Tablo iki öbek: önce tek başına biten maddeler — 210, 212,
216 — sonra kullanıcıya ihtiyaç duyanlar: 211, 215, 213, 214, 217. Koşulacak sıra bu tablonun
sırasıdır.

## Neden bu koşu v5

**queen-editor v4'te.** Dal sayacı budur ve doğru olan odur: `git branch -a` queen-editor için yalnız
`feat/queen-editor-v1`, `v2`, `v3`, `v4` gösteriyor, ve dördü de main'e girmiş — sonuncusu `e87f372`
ile 25 Ağustos'ta.

**Belge sayacı en baştan önde gidiyordu.** Her yol haritası kendi başlığında hangi dalda koştuğunu
yazmış, ve yan yana konunca kayma görünüyor:

| Yol haritası | Koştuğu dal |
|---|---|
| v3 | `feat/queen-editor-v1` |
| v4 | `feat/queen-editor-v2` |
| v5 – v13 | `feat/queen-editor-v3` |
| v14 | `feat/queen-editor-v4` |

*(v2'nin başlığında dal adı hiç yok. **v10 diye bir yol haritası da yok** — o numarada yalnız tek bir
görev dosyası duruyor.)*

Yani kayma v5'te başlamadı, **v3'te** başladı ve büyüyerek gitti: dört dal, on üç belge. On koşunun
tek bir dalda biriktiği de doğru değil — dokuzu `v3`'te, biri `v4`'te.

Kural şu: **bir v bir daldır**, dal test edilir ve main'e girer. Kayan kuralın kendisi değil, adın
dalı tutması oldu.

**Bu belge önce *"QueenAgent tarafında hiç kaymamış"* diyordu; yanlıştı** *(13 Eylül'de bakıldı —
cümle `feat/queenagent-v5`, `v7`, `v7.5`, `v8`'e bakıp oradan genel bir sonuç çıkarıyordu)*. Sekiz
belgenin dalları, bakıldığı **ve düzeltildiği** hâlleriyle:

| Yol haritası | Koştuğu dal | 13 Eylül'de |
|---|---|---|
| v1 | `feat/mira-v1` | — |
| v2 | `fix/mira` | Koşu 1 oldu |
| v3 | `fix/mira` — v2 ile **aynı dal** | Koşu 2 olarak v2'ye katıldı, **numarası boş kaldı** |
| v4 | `feat/queenagent-colab` *(numara taşımıyor)* | — |
| v5 | `feat/queenagent-v5` | — |
| v6 | `feat/v6` *(tool adı taşımıyor)* | — |
| v7 | `feat/queenagent-v7` | ikinci dalı **`feat/queenagent-v7.5`** başlığa girdi |
| v8 | hiçbir dal adı vermiyordu | `feat/queenagent-v8` başlığa girdi *(`356d605` ile merge)* |

Yani hastalık iki taraftaydı, ve **210 ikisini birden düzeltti** *(kullanıcı kararı, 13 Eylül:
backlog'a atmak bunu ertelemek olurdu, oysa maddenin işi tam bu)*. Dördüncü sandığım şey kusur
değilmiş: `feat/queenagent-v7.5` kayıp bir sürüm değil, **180–182 maddeleri v7'nin yol haritasında
duruyor** — v7 tıpkı v5 gibi iki dala yayılmış, yalnız başlığı ikincisini söylemiyormuş.
`feat/queenagent-colab` ile `feat/v6`'nın numara ya da tool adı taşımaması da kusur değil: dal adı
tarihî bir olgu, ve her birinin tek yol haritası var.

**v3 numarası kaydırılmadı.** `feat/queenagent-v5`, `v7` ve `v8` numaralarını adlarının içinde
taşıyor; aşağı kayan her belge kendi dalıyla çelişirdi. Açıklanmış bir boşluk, kaymış bir numaradan
iyidir — queen-editor'ün kaydında da *"v10 diye bir yol haritası yok"* aynı biçimde duruyor.

Bu koşu v4'ün ardından açılan **ilk yeni dal**, yani v5.

**QueenAgent'ın v sayacı ayrıdır** *(kullanıcı kararı, 11 Eylül)*. QueenAgent v8'de, queen-editor v5;
iki tool aynı v numarasını paylaşmaz.

**Madde numarası depo sayacından geliyor.** Sayaç 209'da ve v5'ten (QueenAgent, 25 Ağustos) beri depo
geneli. Sebep, yazılmış spec'lerin madde numarasına atıf yapması: sayacı ikiye bölmek aynı numaranın
iki farklı işi göstermesi demek olurdu.

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**Kullanıcıya ihtiyaç duyan maddeler sona alınır** *(kullanıcı kuralı, 11 Eylül)*. Bu koşunun
maddelerinin bir kısmı tek başına bitmiyor: bir şeyin indirilip verilmesini, üretilmiş bir çıktıya
kullanıcının bakmasını, ya da *"şuna bakar mısın"* denip cevap beklenmesini gerektiriyor. Onlar
tablonun sonunda duruyor, ve şöyle koşuluyorlar:

- **Ne gerektiği spec'in başında yazılır.** Maddenin ilk turu açılır açılmaz, kullanıcıdan ne
  isteneceği spec'in başına geçer — koşunun ortasında değil, başında.
- **Verilebiliyorsa spec'ten ya da plandan sonra verilir.** O an elde varsa orada alınır, kod ondan
  sonra başlar.
- **Koşarken fark edilirse sorulur, geçilmez.** Eksik bir şey ortaya çıkarsa durulup istenir; tahminle
  ya da atlayarak devam etmek yok.

Sebebi: eksiği koşunun ortasında fark etmek maddeyi yarım bırakıyor, ve yarım madde işaretlenemiyor —
bir maddeyi kısmen bitmiş göstermenin yolu yok.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 210 | ✅ **Sürüm karmaşasının çözülmesi.** Belge sayacı v3'ten beri dal sayacının önünde gidiyordu: on üç yol haritası dört dala dağılmış, hiçbiri adının söylediği dalda koşmamış, ve **iki dosya birden kendini v5 diye adlandırıyordu**. Sebep, koşan yol haritasına madde eklenecek yerde her koşuda yeni bir roadmap açılması. **Ad artık kaydın kendisi** *(kullanıcı kararı, 11 Eylül — ayrı bir kayıt dosyası denendi ve reddedildi)*: on üç belge beşe indi — v1, v2, v3, v4 ve bu koşu — aynı dalda koşanlar tek dosyada kendi *Koşu N* bölümleri olarak birleşti, metinleri olduğu gibi. 157 dosyadaki bağlantı yeni adlara çevrildi. Ardından **14 haritanın hepsi — üç tool birden — `docs/superpowers/roadmaps/` klasörüne taşındı** *(kullanıcı kararı, 13 Eylül)*: ad ancak bulunabildiği kadar kayıt, ve bin dosyalık bir klasörde bulunmuyordu. CLAUDE.md'nin *"en yüksek vN güncel"* cümlesi de düzeldi: bu sabahki yanlış cevap oradan çıkmıştı. **Sonra aynı soru QueenAgent'a soruldu** *(kullanıcı, 13 Eylül)* ve orada da kaymış çıktı — üstelik bu belge bir ara *"QueenAgent tarafında hiç kaymamış"* diye yazıyordu, ki yanlıştı. Üç kusur: **v2 ile v3 tek dalın** (`fix/mira`) **iki belgesi**, **v8'in başlığı hiçbir dal söylemiyor**, ve **v7 iki dala yayıldığı hâlde birini yazıyor**. Üçü de düzeliyor: v2 ile v3 tek belgede *Koşu 1* ve *Koşu 2* oluyor, ve **v3 numarası boş kalıyor** — aşağı kaydırmak `feat/queenagent-v5`, `v7`, `v8` dal adlarıyla çelişirdi, ve boşluk tam birleşmenin olduğu yerde durup kendini anlatıyor. Testin ad↔dal çivisi de yalnız `feat/queen-editor-vN` arıyordu, yani QueenAgent'ın dördü o boşlukta duruyordu; iki tool'u birden tutacak biçimde genişledi. **Son olarak bağlantı metinleri:** yeniden adlandırma her **yolu** düzeltmiş, hiçbir **metni** düzeltmemişti — 133 spec ve plan hâlâ *"v5 yol haritası"*, *"v7"*, *"v14"* diyip v3 ve v4 belgelerini açıyordu. Bağlantı çözüldüğü için hiçbir çivi görmüyordu; gören tek şey okuyucuydu, ve ona olmayan bir belge gösteriliyordu. Metinler bugünkü adı ve koşuyu söyler oldu *(`v3 Koşu 1 · Görev 12`)*, ve bir çivi daha: bir bağlantının metnindeki sürüm, gittiği belgenin sürümünden farklı olamaz — yeniden adlandırmayı anlatan cümleler *(`… adıyla`)* muaf, çünkü onların eski adı söylemesi gerekiyor. | Sorunun cevabı klasörü listelemekten okunuyor — en yüksek numaralı yol haritası v5, ve başlığı `feat/queen-editor-v5` diyor. Hiçbir sürüm numarası iki belgede geçmiyor, hiçbir ad kendi dalından başkasını söylemiyor, `plans/` altında harita kalmamış, ve bağlantılar iki yönde de çözülüyor — haritaya gidenler de haritadan çıkanlar da. **İki tool için de** böyle: her yol haritası başlığında dalını veriyor, hiçbir dalı iki belge sahiplenmiyor, ve dal adı bir numara taşıyorsa belgenin numarasıyla aynı. Deponun hiçbir yerinde, olmayan bir sürümü adlayan bir bağlantı metni kalmamış. Hepsini test tutuyor. |
| 212 | ✅ **Oynatma düğmesi video oynarken üstünde duruyor.** *(Kullanıcı bildirimi, 6 Eylül.)* Video başlayınca başlat/durdur düğmesi kaybolmuyor, görüntünün **üzerinde kalıyor** ve karenin bir kısmını örtüyor. Düğme artık oynarken hiçbir piksel çizmiyor, ve yerine **karenin kendisi tıklanıyor** *(kullanıcı kararı, 13 Eylül — seçilmeyen okuma farenin kareye gelmesiyle düğmenin geri dönmesiydi: o da örtmeyi sürdürüyor, üstelik dokunmatikte `hover` yok)*. Düğme DOM'dan **çıkmıyor**, yalnız saydamlaşıyor — çıksaydı video oynarken odaklanacak hiçbir denetim kalmaz, duraklatmak yalnız fareyle mümkün olurdu. Sahne tıklamayı aldığı için düğmenin kendi tıklaması kabarmayı durduruyor: iki kez dönen bir video başladığı yere geri gelir ve düğme ölü görünür. | Video oynarken düğme görüntünün üstünde değil, kare tamamen görünüyor; video durunca düğme geri geliyor. |
| 216 | ✅ **Video üretiminde varsayılan mod Loop olur.** *(Kullanıcı, 11 Eylül.)* Video panelindeki Üretim modu seçicisi bugün **Standart** ile açılıyor; bundan sonra **Loop** ile açılacak. Yalnız varsayılan değişiyor: üç seçenek de yerinde kalıyor, ses panelinde seçici zaten doğmuyor, ve detay sayfasındaki *Yeni mod* kutusu **değişmiyor** — onun varsayılanı o videonun kendi modu olmaya devam ediyor, çünkü orası yeni bir iş değil var olan bir videoyu yeniden üretiyor. Butonun altındaki tahmin ve eklendikten sonraki onay cümlesi zaten moda göre konuşuyor, yani kendiliğinden loop'u söyler. **Tek satır göründü ama tek satır değildi:** mod durumu iki panelde de tutuluyor, ve sunucu ses işine Standart'tan başka bir mod verilirse reddediyor — düz bir varsayılan değişikliği **ses üretimini tümüyle kırardı**, üstelik o red ekrana ulaşmadığı için kullanıcı yalnız sesin çıkmadığını görürdü. Varsayılan bu yüzden katmana soruyor, ve ses panelinin hâlâ Standart istediği kendi çivisini aldı. | Video paneli ilk açıldığında seçicide Loop yazıyor, ve hiçbir şeye dokunmadan kuyruğa eklenen video işi loop modunda kaydedilip loop olarak üretiliyor. |
| 211 | ✅ **Silinen standart videodan sonra loop eklenince ikisi birden üretiliyor gibi görünüyor.** *(Kullanıcı bildirimi, 6 Eylül.)* Kareye standart video eklendi → silindi → yerine loop video eklendi. Ekranda **ikisi birden** üretiliyormuş gibi görünüyor, standart ve loop yan yana. Sebebi **araştırılmadı**, ve buraya bir tahmin yazılmıyor: silinen işin gerçekten iptal edilmemesi de olabilir, yalnız ön yüzün eski satırı bırakması da. İkisi çok farklı yerlerde durur. **Kullanıcıdan gereken** *(spec'in başında sorulur)*: silinen video gerçekten üretilmiş miydi yoksa sırada mıydı, ekranda kaç satır göründü, ve dışa aktarmaya hangisi düştü — yani hata yalnız görüntüde mi, yoksa diske de mi ulaşıyor. **Kullanıcı 13 Eylül'de verdi:** video **kuyruktayken** silinmiş, ekranda **tek kare** ama kartın üstünde *"video üretiliyor"* alt alta iki kez — durdurup bir daha eklenince üç. Export'a bakılmamış, ve gerek de kalmadı. **Sebep:** durum kaydı (kare, katman) başına **tek hücre** tutuyor, ama plan o çift için **birden çok iş satırı** taşıyabiliyor; silme hücreyi kapatıp satırı bırakıyor, yeniden ekleme hücreyi açınca **eski satırlar da** açılıyor. Bulunan şey beklediğimden kötü çıktı: motor iki video üretmiyor — **bir** video üretiyor, ve onu **en eski satırdan** yapıyor. Yani loop isteyince silinmiş **standart** geri geliyor. Düzeltme `open_jobs`'a girdi: hücre tek ise borç da tektir, ve borçlu olunan en son istenen. Plana dokunulmadı — plan ne istendiğinin kaydı, ve üç kez istenmiş olması gerçekten olmuş bir şey. | Aynı sıra tekrarlanıyor — standart eklenip siliniyor, yerine loop ekleniyor — ve karede tek satır kalıyor; dışa aktarmaya da tek video düşüyor. |
| 215 | ✅ **Başka projeye geçip üretmeye basınca çıkan hata düzgün konuşmuyor.** *(Kullanıcı, 11 Eylül.)* Bir projede üretim başlatılıyor, oradan çıkılıp başka bir projeye giriliyor ve orada üretme basılıyor — **hata veriyor, ama mesaj düzgün değil.** Hatanın kendisi bu maddenin konusu değil; **söylediği şey** konusu. Sebebi **araştırılmadı** ve buraya bir tahmin yazılmıyor. Uydurulmuş bir sebep ekrana yazılmayacak — duran cümle, gerçekten olanı söyleyecek. **Kullanıcıdan gereken** *(spec'in başında istenir)*: o anın kendisi — ekranda duran cümle ve sunucunun döndürdüğü ham cevap. İkinci soru da kullanıcıya ait: ikinci projede üretmek **yasak mı olmalı** — o zaman mesaj sebebini söyler — yoksa **çalışması mı gerekiyordu**, ki o zaman bozuk olan mesaj değil davranış. **İkisi de koddan okundu, sorulmadan.** Karar zaten yazılı: tek işçi var, ikinci projenin koşusu bir reddir *(`run_queue`)* — *"çalışması gerekiyordu"* okuması bu maddeyi değil, ikinci bir işçiyi isterdi. Ekranda duran cümle ise **hiç yokmuş**: fotoğraf paneli bu durumu baştan beri doğru karşılıyor *(düğme kapalı, altında "Üretim sürüyor: balo — bitmesini bekle.")*, ama video/ses paneline `busyElsewhere` de `error` de geçmiyordu. Düğme kapanmıyor, basış gidiyor, 409 dönüyor, ve yan sütun bir seferde tek panel çizdiği için o cevap **açık olmayan** bir panele düşüyordu. Yani mesaj düzgün değil değildi — mesaj yoktu. Düzeltme yeni bir davranış icat etmiyor: üç prop geçiyor, ve panel fotoğraf panelinin cümlesini birebir söylüyor. | Aynı sıra tekrarlanıyor ve ekranda çıkan cümle ne olduğunu söylüyor: kullanıcı onu okuyup ne yapacağını biliyor, ve cümle sunucunun gerçekten döndürdüğüyle çelişmiyor. |
| 213 | **MiniMax eklenecek.** *(Kullanıcı, 6 Eylül.)* Hangi işi alacağı — fotoğraf mı video mu, bugünkü tarifin yerine mi yanına mı — **kararlaşmadı.** Karar maddenin kendi turunda verilir ve buraya yazılır; kod ondan sonra yazılır. **Kullanıcıdan gereken** *(spec'in başında istenir)*: bu karar, MiniMax'e nasıl erişildiği, ve çıkan üretime bakması. | Karar yazıya geçmiş, ve MiniMax kendisine verilen işte üretim yapıyor: kuyruğa giren bir iş onunla bitiyor ve çıkan dosya karesine iniyor. |
| 214 | **Slime girl videosu eklenecek.** *(Kullanıcı, 6 Eylül.)* Bir video türü — *slime girl*. Bir model değil, üretilecek bir içerik biçimi. **Kararlaşmadı:** kendi LoRA'sıyla mı geliyor, kendi üretim tarifiyle mi, yoksa yalnız prompt tarafında mı kalıyor. **Kullanıcıdan gereken** *(spec'in başında istenir)*: bu karar; yol LoRA ise dosyanın indirilip verilmesi; ve çıkan videoya bakması. | Karar yazıya geçmiş, ve o yolla üretilmiş bir slime girl videosunu kullanıcı görmüş. |
| 217 | **CLAUDE.md'nin yol haritası paragrafı toparlanacak.** *(Kullanıcı, 13 Eylül.)* Paragraf 210 boyunca beş kez düzenlendi ve **satır sarması dağıldı** — bir satır çok uzun, bir cümle ortasından kırılıp bir sonrakine biniyor. İçerik doğru, okunuşu dağınık. Aynı turda **iki kural yazıya geçecek**: bugün yalnız testte duruyorlar, yani öğrenme yolu kırmızıya çarpmak. Biri, her yol haritasının **başlığında kendi dalını yazdığı** *(QueenAgent v8 yazmıyordu)*; öteki, bir bağlantının **metnindeki sürümün gittiği belgeden farklı olamayacağı** *(133 metin olmayan sürümleri adlıyordu)*. İkisi de henüz yazılmamış belgeleri bağlayan kurallar, yani tam CLAUDE.md'lik. **Kullanıcıdan gereken** *(spec'ten önce değil, sonra)*: paragrafı okuyup onaylaması — *"şu an zamanım yok, en son okuyacağım"*. | Paragraf tek okumada anlaşılıyor ve satırları düzgün sarıyor; iki kural orada yazılı; ve kullanıcı okuyup *"tamam"* demiş. |

**211, 215, 213 ve 214'ün yargısı koda bakarak verilemiyor.** queen-editor yerelde koşmuyor: defteri
kullanıcı çalıştırıyor. 211 ile 215'in gerçekten kapandığı da, 213 ile 214'ün ne ürettiği de ancak
orada görülüyor.

**217 de kullanıcıyı bekliyor ama başka sebeple:** koda değil, bir paragrafın okunmasına bağlı. O
yüzden en sonda — yazılması beklemiyor, onaylanması bekliyor.
