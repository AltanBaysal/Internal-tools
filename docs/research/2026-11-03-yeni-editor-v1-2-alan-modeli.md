# Yeni editör — 2. Alan modeli

Core'da ne var, ne tutar, nasıl değişir, ne asla olamaz.
[1. Dışarıya açılanlar](2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md)'daki endpoint'lerin
ihtiyacı kadar.

## Her şey için

- **Kimlik.** Her şeyin kimliğini core verir. Kimlik değişmez, yeniden kullanılmaz. Projenin
  kimliği bütün Colab'lar arasında tektir (rastgele); projedeki her şeyin kimliği o projede tektir
  (projenin sayacı). Her adres projenin altında olduğu için kare projesiyle birlikte anılır.
- **Ad ve sıra kimlik değildir.** Ad değişince kimlik ve ona bakan her şey yerinde kalır. "12. kare"
  yalnız bugünkü yerdir.
- **Ad kuralı**, proje, edit ve export adları için tek kural: boş olamaz, başında ya da sonunda
  boşluk olamaz, en çok 64 karakter, `/ \ : * ? " < > |` ve kontrol karakterleri olamaz, nokta ile
  başlayamaz ve bitemez. Uymayan ad istekte hata olur; core adı düzeltmez. Export'a verilen ad en
  çok 58 karakterdir, sonuna gelebilecek ` (n)` ile 64'ü aşmasın diye. Export'un varsayılan adı 58
  karakterde kesilir; sonda kalan boşluk ve noktalar atılır.
- **Ya hep ya hiç.** Bir istek, toplu olanı da, ya bütünüyle olur ya hiç olmaz. Olmazsa hata engel
  olan her şeyi sayar. Yarım kalmış, sonradan temizlenecek bir durum yoktur.
- **Tek tek.** Bir projenin değişiklikleri birbirinin arasına girmez; ayrı projeler aynı anda
  değişebilir. İki Colab aynı projeyi aynı saniyede değiştirirse birinin değişikliği bütünüyle
  kaybolabilir; proje bozulmaz (bkz. Sonraya kalanlar).
- **Sahiplik.** Proje kendi karelerinin, edit'lerinin, işlerinin ve export'larının sahibidir. Hiçbir
  şey başka projedeki bir şeye bakmaz.
- **Silme yalnız kendini götürür.** Core başka hiçbir şeyi düzeltmez; düzeltmeyi agent yapar.
- **Çöp kutusu.** Core hiçbir dosyayı kalıcı silmez; silinen dosyalar deponun çöp kutusuna gider
  (Drive'da Drive'ın kendi çöp kutusu). Çöpü kullanıcı boşaltır; Drive da 30 gün sonra kendisi
  boşaltır.
- **Türetilen saklanmaz.** "Silindi", "videosu üretiliyor" bir yere yazılmaz;
  okunurken kare ve işlerden çıkarılır. Böylece iki kayıt birbiriyle çelişemez.

## Proje

- **Tutar:** adı, arşivde olup olmadığı, ne zaman oluşturulduğu ve değiştiği, karelerin sırası.
- **Ad** ad kuralına uyar; tek olmak zorunda değildir, edit adları gibi (kullanıcı, 4 Kasım — "aynı
  isimle iki proje olabilsin"). Projeyi kimliği tanıtır. Aynı adla başka bir proje varsa oluşturma
  ve yeniden adlandırma engellenmez; cevap o projeyi söyler.
- **Arşiv** yalnız bir etikettir, listelemede süzmek içindir. Arşivdeki projede her şey yapılabilir.
- **Silinince**, tek değişiklik olarak, bütün kareleri, edit'leri, işleri ve export kayıtları gider.
  Projenin dosyaları, history'si dahil, çöp kutusuna gider; bitmiş export'ların dosyaları projenin
  dışında olduğu için kalır.
  Bekleyen işleri kuyruktan çıkar, çalışan işi ve süren export'ları durur; başka bir Colab'dakiler en geç 30 saniye içinde.

## Kare

Bir fotoğraf ve en çok bir video.

- **Tutar:**
  - projesi (hiç değişmez)
  - sahnesi: fotoğraf istenirken verilen, karede ne olduğunun kısa açıklaması (zorunlu)
  - fotoğrafın üretildiği her şey: verilen prompt, modele giden prompt (LoRA seçiminin tetik
    kelimesiyle), negatif, model, LoRA seçimi ve o an içindeki dosyalar ile güçleri, yön, gerçekte
    üretildiği seed ve birlikte üretildiyse o üretimdeki sırası (aynısı yeniden üretilebilsin diye),
    zaman, hangi iş
  - videosu varsa onun üretildiği her şey: verilen prompt, modele giden prompt (core'un eklediği
    cümleyle), model, uzunluk, seed, mutlu son, zaman, süresi, hangi iş
  - fotoğrafı başka bir kareden geliyorsa o kare
- **Ne zaman var olur:** iş verildiği an. Kare sıraya hemen girer; fotoğrafı gelene kadar
  "üretiliyor" görünür (işinden okunur), queen-editor'daki gibi.
- Bir iş için açılmış yeni kare, işi ürününü getirmeden iptal olursa silinir: `t2i`'nin karesi
  fotoğrafı gelmeden, `i2v`'nin yeni karesi videosu gelmeden (fotoğrafı kaynak karede kalır).
  `i2v` var olan bir kareye düşecekse iptalde o kare kalır.
- **Değişen yalnız videosudur:** fotoğraf kareye bir kez, iş bitince gelir; sonra hiç değişmez. Videosu olmayan kareye video eklenir; video silinebilir, kare
  videosuz kalır ve yeniden video alabilir. Fotoğraf ve bilgileri hiç değişmez. Silinen videonun
  bilgileri history'de kalır.
- **Hiçbir zaman:** iki videolu kare; başka projeye geçen kare. Fotoğrafı olmayan kare yalnız işi
  bitmemişken vardır.
- **Video durumu** karede saklanmaz; kareyi hedefleyen işlerden okunur: bekliyor ya da üretiliyor.
- **Fotoğraf paylaşımı:** `i2v` yeni kareye düşünce iki kare aynı fotoğrafı kullanır. Fotoğraf, onu
  kullanan kare de iş de kalmayınca çöp kutusuna gider; kaynak karesi silinen `i2v` işi fotoğrafı
  böyle saklar. Video paylaşılmaz.
- **Silinince:** sıradaki yeri gider; videosu ve (başka kare ya da iş kullanmıyorsa) fotoğrafı çöp
  kutusuna gider.
  - Edit'lerdeki yerleri kalır, "silindi" gösterir.
  - Süren bir export onu kullanıyorsa kare silinmez; hata export'u söyler ve önce onun bitmesini ya
    da iptal edilmesini söyler.
  - Onu bekleyen ya da onun için çalışan bir iş varsa kare silinmez. Hata, karenin kuyrukta
    olduğunu söyler, işleri sayar ve önce onları kuyruktan çıkarmayı söyler; fotoğrafı henüz
    gelmemişse işi çıkarmak yeter, kare de silinir.

## Karelerin sırası

- Projenin her karesi sırada tam bir kez vardır.
- Yeni kare, iş verildiği an sıraya girer: `t2i`'de istekte verilen yere (baş, son ya da bir
  karenin arkası), verilmemişse sona; `i2v` yeni kareye düşecekse kaynak karenin arkasına.
- Bütün sırayı yeniden veren istek projenin bütün karelerini tam bir kez içermelidir; içermezse
  reddedilir, eksik ve fazla kareleri söyler.

## Edit ve yerleri

- **Edit tutar:** projesi, adı (tek olmak zorunda değil), yerleri sırasıyla, oluşturulduğu ve son
  değiştiği zaman (kullanıcı, 6 Kasım). Bu iki zaman history'den de çıkarılabilir, ama history'nin
  eski bloklarını indirmek gerekir; projenin zamanları gibi, edit'i değiştiren yazmada birlikte
  yazılır.
- **Yer tutar:** gösterdiği kare, sesinin kapalı olup olmadığı.
- **Yerin kimliği** vardır; taşınınca, karesi ya da sesi değişince kalır. Yer konumuyla değil
  kimliğiyle anılır: o arada sıra değişse de yanlış yer çıkarılmaz.
- Yer yalnız aynı projede var olan bir kareyi gösterebilir.
- Gösterdiği kare silinirse yer kalır ve "silindi" gösterir; agent onu çıkarana ya da başka kareye
  çevirene kadar.
- Sonra oluşan kareler edit'e kendiliğinden girmez. Boş edit olabilir.
- **Silinince** yalnız edit ve yerleri gider; kareler ve export'lar kalır.

## İş

Bir iş tek dosya üretir ve tek kareye düşer.

- **Tutar:** projesi, yöntemi, verilen her şey, core'un seçtiği seed, istek anahtarı, düşeceği kare,
  durumu, zamanları, üretim süresi.
- **Durumlar:** bekliyor → çalışıyor → bitti ya da iptal. İş başarısız olmaz: hata verirse kuyruk
  durur (bkz. Kuyruk). Son durumlar (bitti, iptal) hiç değişmez. Çalışan iş kesilirse, nedeni ne olursa olsun, sıranın başına,
  bekleyen iş olarak döner ve baştan üretilir.
- **Verilirken:**
  - Modelin aldıkları ve ihtiyaçlar bakılır; eksik ya da yanlışsa iş oluşmaz, hata neyi söyler.
  - Seed verilmemişse rastgele seçilir ve kaydedilir.
  - LoRA seçimi her `t2i` isteğinde verilir; varsayılan yoktur. "LoRA yok" da bir seçimdir.
  - `i2v`'de core promptun başına H3'ün başlangıç fotoğrafı cümlesini ekler.
  - Kuyruğun sonuna girer.
  - Düşeceği kare o an kesinleşir ve yanıtta söylenir:
    - `t2i`: yeni bir kare kimliği.
    - `i2v`: kaynak karenin videosu yoksa ve onu hedefleyen bekleyen ya da çalışan başka iş yoksa o
      kare; değilse yeni bir kare kimliği.
- **Varyantlar:** her varyant ayrı bir iştir, kendi seed'i vardır (`i`. varyantınki `seed+i`; seed
  verilmezse ilki rastgele seçilir) ve kendi karesine düşer.
  - Kuyrukta art arda duran varyantlar, kart kaldırıyorsa GPU'da birlikte, ilk varyantın seed'iyle
    üretilir.
  - Birlikte üretilemeyen varyant (Krea, kartın belleği yetmez, araya iş girer)
    kendi seed'iyle tek başına üretilir; böylece varyantlar hiçbir zaman aynı resim olmaz.
- **Aynı istek iki kez:** istek anahtarıyla anlaşılır. Aynı anahtar ilk isteğin işlerini döndürür;
  aynı anahtarla farklı içerik hatadır. Anahtar (idempotency key) zorunludur; MCP adaptörü ve UI
  onu kendileri ekler. Anahtar 24 saat tutulur. Aynı anahtarla gelen istek, ilki hâlâ sürüyorsa
  yeniden yapılmaz; ilki beklenir ve onun cevabı döner.
- **Verilirken** modeli kurulu olmalı ya da inmekte olmalı; değilse iş verilemez (10. adım).
- **Başlarken** ihtiyaçlarına yeniden bakılır: model hâlâ iniyorsa kuyruk bekler (bkz. Kuyruk).
  `i2v`'nin kaynak karesi o arada silindiyse iş saklanan fotoğrafla yapılır (4. adım).
- **Bitince** kareye fotoğrafı ya da videosu gelir ve iş "bitti" olur; ikisi tek değişikliktir.
- **Core yeniden başlarsa** çalışan iş sıranın başına, bekleyen iş olarak döner.
- **Kayıt** projesiyle silinir. Düştüğü kare silinse de kayıt o kimliği söyler.

## Kuyruk

Her projenin bir kuyruğu vardır; projenin içinde, Drive'da durur. Kuyruğu bir anda tek bir Colab
çalıştırır, bir Colab da bir anda tek projenin kuyruğunu; bir Colab, bir GPU. queen-editor'daki
gibi: Colab kapanırsa kuyruk projede kalır, başka bir Colab onu kaldığı yerden sürdürür.

- **Tutar:** durdurulmuş olup olmadığı, kendiliğinden durduysa nedeni, onu çalıştıran Colab, çalışan iş (en çok bir), bekleyen
  işlerin sırası. Kuyruk değişiklikleri projenin history'sine girer.
- **Çalıştırmak:** `resume` kuyruğu o Colab'a alır; Colab'ın önceki kuyruğu durur ve yerinde bekler,
  kuyruğu önceden çalıştıran Colab en geç 30 saniye içinde bırakır; o an ürettiği iş kesilir ve
  yeni Colab'da baştan üretilir. Önce eski kuyruk bırakılır, sonra yenisi alınır; arada kesilirse
  eski kuyruk durmuş, yenisi alınmamış kalır, aynı istek yeniden gönderilince tamamlanır. Boştaki bir Colab'dan
  projeye iş verilince Colab o projenin kuyruğunu çalıştırmaya başlar; başka bir kuyruğu
  çalıştıran Colab'dan verilen iş bekler, çalışan kuyruk kesilmez. Kuyruk boşalınca Colab onu bırakır
  ve boşta kalır; projeyi o an hiçbir Colab çalıştırmaz.
- Her bekleyen iş sırada tam bir kez vardır; çalışan iş sırada değildir.
- **Sıra** tamamen agent'ındır: bir işi taşır ya da bütün sırayı verir. Bütün sıra, bekleyen işlerin
  hepsini tam bir kez içermelidir. O arada başlamış ya da bitmiş işler atlanır, geri kalan sıra
  uygulanır; cevap atlananları söyler. Bir isteğin varyantları art arda girer.
- **Durdurunca** yeni iş başlamaz; çalışan iş kesilir ve sıranın başına, bekleyen iş olarak döner.
  **Sürdürünce** sıradaki ilk iş başlar; kesilen iş baştan üretilir.
- **Model iniyorsa:** sırası gelen işin modeli hâlâ iniyorsa kuyruk "model iniyor" der ve bekler;
  model inince iş başlar. Model inemediyse kuyruk kendiliğinden durur ve nedenini söyler (10. adım).
  İş bekler, kaybolmaz.
- **Drive'da yer yoksa:** boş yer yetmezse iş başlamaz, kuyruk kendiliğinden durur ve nedenini
  söyler (`storage_low`, 4. adım); işler bekler, kaybolmaz. Yer açılınca `resume` ile sürdürülür.
- **Ürün yüklenemezse:** üretilen dosya yeniden denemelerden sonra da Drive'a yüklenemezse kuyruk
  kendiliğinden durur (`storage_rejected`); iş sıranın başına, bekleyen iş olarak döner.
- **İş hata verirse** (ComfyUI işi reddetti ya da üretim süresi doldu; 7. adım) iş başarısız olmaz: kuyruk kendiliğinden durur, iş sıranın başına, bekleyen iş olarak
  döner, kaybolmaz (kullanıcı, 5 Kasım — "o case zaten kuyruğun durması acayip düşük, öyle olursa da
  dursun queue, çünkü öyle bir problem varsa çözmesek daha fazlasında olabilir"; "olsun"). Sorun
  geçiciyse agent `resume` der, aynı iş baştan üretilir. İşin kendisi bozuksa (ör. promptu) agent
  işi siler, düzeltilmiş olanı verir (`t2i`'de yeni karesinin yeri `at` ile), yeni işi
  `PATCH …/queue` ile kuyruğun başına taşır, sonra `resume` der.
  Bedeli: bozuk tek bir iş, agent ya da kullanıcı bir şey yapana kadar arkasındaki her şeyi
  durdurur; agent bunu `queue/wait`'ten hemen görür.
- **Kendiliğinden durunca** (işin hatası, ComfyUI, model inemedi, Drive'da yer yok, ürün yüklenemedi) nedeni dört alanlı hatasıyla
  kuyrukta durur. `GET …/queue`, `…/queue/wait` ve projeye iş veren isteğin cevabı onu söyler; iş yine
  kabul edilir. Agent kullanıcıya söyler, neden düzelince `resume` (kullanıcı, 5 Kasım — "hata
  mesajı da dönsün istek gelirse ya da bilgi, böylece agent bana söyler").
- **Boşaltınca** bekleyen bütün işler iptal olur; çalışan iş ve ürünü gelmiş kareler kalır; iş için
  açılmış, ürünü gelmemiş kareler gider.
- `DELETE /projects/{p}/jobs/{id}` çalışan işi de durdurur. İş "iptal" olur, yarım kalan sonucu atılır.

## Export

- **Export tek bir birleşik videodur.**
- **Tutar:** adı (son hali), klasörünün adı ve Drive bağlantısı, projesi, edit'i, başladığı andaki yerlerin kopyası (kare ve ses), durumu,
  hatası, çıkardığı dosyalar.
- **Durumlar:** çalışıyor → bitti, başarısız ya da iptal. Export'u yapan Colab yarıda kapanırsa
  export, o core yeniden başlayınca ya da başka bir Colab iptal edince, birleşik videosu tam
  yüklenmişse bitti, değilse başarısız olur.
- **Başlarken** edit'in o anki yerleri alınır; sonra edit değişse ya da silinse de export başladığı
  haliyle sürer.
- **Başlamaz**, hata yerleri sayar: silinmiş yer, videosu olmayan kare, boş edit.
- **Önizleme** hiçbir şey oluşturmaz, kaydedilmez.
- **Ses:** her yerde videonun kendi sesi çalar; sesi kapalı yerde hiç ses olmaz.
- **Görünümü** (bugün):
  - 1920×1080 yatay çerçeve; dikey klipler kenarlarında bantla yerleşir.
  - Saniyede 24 kare, H3'ün kendi hızı. Sabit değildir: başka hızda üreten bir model gelince
    değişebilir.
  - İlk 60 saniye boyunca uyarı görseli, genişliğin %80'i kadar.
  - İleride başka çıktı biçimleri eklenebilir.
- **Fotoğraflar:** export'ta videoların yanında fotoğraflar klasörü de bulunur; her fotoğraf bir kez
  girer ve videosuyla aynı numarayı taşır. Fotoğrafların dahil olup olmaması ileride export'un bir
  seçeneği olabilir; şimdilik dışarıya açılmaz.
- **Dosyaları** projenin dışında, ayrı bir export klasöründe, her export kendi tarihli klasöründe
  durur. Klasör `<YYYY-MM-DD HH-MM> <ad>/`, video `<ad>.mp4`. Aynı adlı klasör varsa adın sonuna
  `(1)` eklenir, o da varsa `(2)`, böyle sürer, Windows'taki gibi. Adın son hali hem klasörde hem
  videoda kullanılır: `2026-11-04 14-30 final (1)/final (1).mp4`. Karşılaştırma klasörün bütün
  adıyladır, tarih ve dakikası dahil: dünkü "final" bugünkünü "final (1)" yapmaz. Büyük/küçük harfe
  bakmaz; core buna her export'ta export klasörünü listeleyerek bakar: başka Colab'ların ve elle
  açılmış klasörler de sayılır. İki Colab aynı dakikada aynı adı verirse aynı adlı iki klasör
  olabilir; ikisi de bütündür. Klasör adındaki
  tarih ve saat UTC'dir, Colab'ın verdiği gibi; Türkiye saatinin 3 saat gerisindedir.
- Core bitmiş bir export'un dosyalarını hiç silmez; onları kullanıcı siler. `DELETE /projects/{p}/exports/{id}`
  yalnız süren bir export'u iptal eder ve o ana kadar yazdıklarını geri alır.

## History kaydı

- **Tutar:** sıra numarası, zaman, kimin yaptığı (agent, UI ya da core), ne yapıldığı, neye
  yapıldığı, değişenlerin öncesi ve sonrası (veriler; dosyalar değil).
- Her projenin kendi sırası vardır. Her kayıt hangi Colab'da yapıldığını söyler; zamanı kaydı
  yazan Colab'ın saatidir.
- **Bir istek bir kayıttır**, birçok şeyi değiştirse de (ör. birçok kare silmek).
- **Kaydedilen:** isteklerin her değişikliği ve işlerin sonucu (kareye fotoğraf geldi, kareye video eklendi;
  yapan core).
- **Kaydedilmeyen:** okumalar, önizlemeler, reddedilen istekler; işin çalışmaya başlaması ve bitmesi
  (bunlar işin kendi kaydındadır).
- Kimin yaptığını isteği yapan söyler.
- Kayıt değişmez, silinmez; proje silinince projeyle birlikte çöp kutusuna gider ve okunmaz
  (kullanıcı, 5 Kasım).

## Modeller

- Core'daki model listesinden gelir; core yalnız okur. Kurulu olup olmadığı bu Colab'ın diskinden
  gelir (10. adım).
- **Tutar:** her ana modelin ne olduğu, fotoğraf mı video mu, boyutu, çalıştığı ekran kartları,
  dosyaları ve nereden indiği; yöntemleri ve aldığı parametreler; sunduğu LoRA seçimleri (dosyaları,
  sabit güçleri, tetik kelimesi); yönler, video uzunlukları, en çok varyant sayısı.
- **Durum:** kurulu, iniyor, inemedi ya da kurulu değil; Colab'a göredir, depoda tutulmaz.
- **Kimlik:** adları.
- Kare, kullandığı model ve LoRA seçiminin o anki içeriğini kendinde tutar; model listesi değişse
  de karenin bilgisi değişmez.
