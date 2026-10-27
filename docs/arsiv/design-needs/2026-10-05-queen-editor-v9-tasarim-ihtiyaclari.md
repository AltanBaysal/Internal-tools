# Queen Editor: v9 tasarım turunun ihtiyaçları

Queen Editor tarayıcıda çalışan bir üretim aracı. Kullanıcı bir projeye prompt listesi yapıştırır,
her prompt birkaç kare açar, ve her karenin önce fotoğrafı, sonra üstüne videosu ve sesi üretilir.
Arayüz bilerek Türkçe; aşağıdaki etiketler ekranda yazdığı gibi. Prompt listesini sahibinin öteki
aracı QueenAgent yazıyor; QueenAgent'ın ihtiyaçları ayrı bir belgede.

Bu belge sahibinin bu tasarım turunda cevap istediği iki ihtiyacı anlatıyor. Çözüm değil, sorun ve
sahibinin kesinleşmiş kararları var. Burada sahibinin kararı olarak yazmayan her şey tasarımcının
kararı. Açık kalan bir şey olursa varsaymadan sahibine sorun: açık noktaları sizinle konuşmak
istiyor. Bilinen açık noktalar en sonda.

---

## Bugün: proje ekranı

İki ihtiyaç da proje ekranına dokunuyor. Ekranın bugünkü hâli:

- **Başlık.** Solda *"Queen Editor"* ve sürümü, ortada projenin adı, sağda *"Export"* ve *"Projeden
  çık"*.
- **Galeri.** Ortada, kalan bütün genişlikte, kendi içinde kayıyor.
  - Kare seçilince galerinin altında, ortada yüzen bir çubuk çıkar: *"3 seçili"*, *"Sil"*,
    *"Vazgeç"* ve öteki düğmeler.
  - Projede kare yoksa *"henüz kare yok"* ve *"Prompt'ları yaz, Kuyruğa ekle'ye bas — kareler burada
    belirecek"* yazar.
- **Sağ sütun.** Sağ kenarda dar bir ikon şeridi, solunda 320px'lik bir panel.
  - Şeritte yukarıdan aşağı: *"Fotoğraf üret"*, *"Video üret"*, *"Ses üret"*, *"Kuyruğu takip et"*,
    *"AI agent"*; en altta, ayrı, *"Üreticiler"*.
  - İkonların yanında yazı yok. Açık panelin adı panelin başında yazar (kuyruğunki *"Kuyruk"*).
  - Aynı anda tek panel açık. Açık panelin ikonuna yeniden basınca panel kapanır, ve yeri galeriye
    kalır.
  - Hangi panelin açık olduğu proje başına akılda kalır: karenin sayfasına girip galeriye dönünce
    aynı panel açık. Sayfa yenilenince *"Fotoğraf üret"* açılır.
- **Karenin sayfası.** Kutucuğa basınca proje ekranının yerine açılır. Orada şerit ve panel yok;
  başlığın sağında *"Galeriye dön"* var.

---

## 1. H3 videosunun uzunluğu

**Bugün**
- Queen Editor her çalıştırıldığında (buna oturum diyoruz) tek bir video modeliyle açılır: ya
  MiniMax H3 (kısaca H3) ya WAN 2.2. Hangisi olduğu uygulama açılmadan seçilir, ekrandan değişmez.
  Aynı proje bir oturumda H3'le, başka bir oturumda WAN'la açılabilir.
- Videonun uzunluğu sabit: H3 videosu 4 saniye, WAN videosu 5 saniye. Ekranda uzunluğu değiştirmenin
  yolu yok.
- Video paneli (*"Video üret"*), yukarıdan aşağı:
  - iki sekme: *"Kareden"* ve *"Referanstan"*
  - iki sekmede de *"Model"* kutusu, tek seçenekli: oturumun video modeli, H3 oturumunda *"MiniMax
    H3"*, WAN oturumunda *"WAN 2.2 I2V"*. Sunucu cevap verene kadar boş.
  - *"Kareden"* sekmesinde *"Kapsam"* (*"Videosu olmayan kareler"*, *"Seçili kareler"*, yanlarında
    sayıları) ve *"Üretim modu"* (*"Standart"*, *"Loop"*, *"Sonrakine bağla"*)
  - *"Referanstan"* sekmesinde *"Referanslar"* (*"Referansları aç"* ortadaki galerinin yerine
    projenin referans havuzunu açar) ve *"Prompt listesi"*
  - iki sekmede de *"Varyant"* ve *"Kuyruğa ekle"*; düğmenin altında ne üretileceği yazar (*"6 loop
    video üretilecek — her video kendine döner."* gibi)
- İki oturumun paneli arasında iki fark var: *"Model"* kutusunun yazdığı ad, ve *"Referanstan"*.
  *"Referanstan"* yalnız H3'le üretir; WAN oturumunda düğmenin üstünde *"Referanstan üretim için H3
  gerekiyor — bu oturumda başka bir video modeli kurulu."* yazar, ve düğmeye basılamaz.
- Projeye kaydedilen seçimler: fotoğraf panelinin kutuları (*"Model"*, *"LoRA"*, *"Prompt
  listesi"*, *"Negatif prompt"*, *"Varyant"*) *"Kuyruğa ekle"* düğmesine basılınca projeye
  kaydedilir, ve proje yeniden açılınca yerindedir. Video panelinde yalnız *"Referanstan"*
  sekmesinin *"Prompt listesi"* ve *"Varyant"*ı böyle kaydedilir. *"Kareden"* sekmesi hiçbir şey
  kaydetmez: panel her açılışta *"Loop"* seçili ve varyant 1 ile başlar.
- Uzunluk ekranda iki yerde, dolaylı görünüyor: karenin sayfasındaki oynatıcının çubuğunun sağ
  ucunda (*"0:04"*), ve export ekranının özetinde toplam olarak (*"22 video export edilecek · 1:50
  dk"*). Karenin sayfasındaki *"Üretim süresi"* başka bir şey: katmanın ne kadar sürede üretildiği.

**İhtiyaç.** Sahibinin sözleriyle: "4, 8, 12 arasında seçebilmek video uzunluğunu." H3 videosunun
uzunluğunu kullanıcı kendisi seçecek.

**Sahibinin kararları**
- Yalnız H3 ("H3'e özel"). WAN bugünkü gibi kalır: WAN oturumunda seçim yok, ve WAN videosu 5
  saniye.
- Video panelinde tek seçim ("tek seçim video panelinde").
- Üç uzunluk: 4, 8 ve 12 saniye.
- Varsayılan 8 saniye ("varsayılan 8 olsun"): hiç seçim yapılmamış projede 8 seçili.
- Seçim projeye kaydedilir ve hatırlanır ("evet, hatırlansın"): proje yeniden açılınca aynı uzunluk
  seçili.
- Seçilen uzunluk, o projede kuyruğa eklenen H3 videosunun uzunluğu.

**Tasarımcıya kalan**
- Seçimin video panelinde nerede durduğu, adı ve nasıl göründüğü. İki sekmeyle ilişkisi açık
  noktalardaki bir cevaba bağlı.
- Adının karenin *"Üretim süresi"*yle karışmaması: uygulamada "süre" bugün bir katmanın ne kadar
  sürede üretildiğini anlatıyor.

**Tasarlanması gereken durumlar**
- **H3 oturumunda yeni proje:** 8 saniye seçili.
- **H3 oturumunda 4, 8 ya da 12 seçili.**
- **Proje yeniden açıldı:** son seçilen uzunluk yerinde.
- **WAN oturumu:** seçim yok; panel bugünkü gibi.
- **H3'te 12 seçilmiş proje WAN oturumunda açıldı:** seçim yok. Proje sonra yine H3'le açılınca 12
  yerinde.
- **Oturumun modeli henüz okunmadı:** *"Model"* kutusu boşken panel H3 mü WAN mı henüz bilmiyor.

---

## 2. Agent'la sohbet

**Bugün**
- Queen Editor'de sohbet yok.
- Şeritteki *"AI agent"* ikonu bugün de var. Açtığı panelin başlığı *"AI agent"*; içinde, ortada
  yalnız *"Agent buradan çalışacak."* yazıyor. Önceki bir tasarım turu bu paneli bilerek boş bıraktı.

**İhtiyaç.** Sahibinin sözleriyle: "Queen Editor'e basic agent ekle, en basic hâliyle." Açık projeyi
okuyan ve soruları cevaplayan bir sohbet: "sorduğum soruları cevaplasın, şimdilik bu kadar." Bu
agent QueenAgent değil: Queen Editor'ün içinde, açık projeye bakan ayrı bir agent.

**Sahibinin kararları**
- Yalnız açık proje ("sadece açık projeye erişebilir"). Agent başka bir projeyi görmez.
- Projeyi kare kare görür: prompt'larını okur, görsellerine bakar ("projedeki prompt'ları
  okuyabilsin, projedeki görselleri görebilsin").
- QueenAgent gibi çalışır ("QueenAgent gibi agentic çalışabilsin"): bir soruyu cevaplarken projeye
  birden çok adımda bakabilir.
- Hiçbir şeyi değiştiremez ("yani bir değişiklik yapamasın"). Yalnız okur ve cevaplar.
- Sohbet kaydedilmez: sayfa yenilenince boşalır.
- Agent cevap veremezse sohbet boş kalmaz, bir mesaj gelir: model soruyu reddettiyse "Model hata
  döndü, farklı şekilde dene" gibi genel bir mesaj; internet yok ya da sunucu hatası gibi teknik bir
  hatada hatanın kendi metni.

**Tasarımcıya kalan**
- Sohbetin nerede durduğu.
- Nasıl göründüğü: sorunun yazıldığı yer, sorular ve cevaplar, agent çalışırken, ve cevap
  veremediğinde.

**Tasarlanması gereken durumlar**
- **Boş sohbet:** henüz soru yok. Sayfa yenilenince de böyle.
- **Soru gönderildi, agent çalışıyor.**
- **Cevap geldi:** bütün olarak, tek seferde; kelime kelime akmaz.
- **Uzun cevap.**
- **Birkaç soru ve cevap alt alta.**
- **Karesi olmayan proje:** galeri *"henüz kare yok"* derken sohbet.
- **Agent cevap veremedi:** genel mesaj ya da teknik hatanın kendi metni.
- **İstek sunucuya ulaşmadı:** uygulama bugün her istekte bu durumda *"Sunucuya ulaşılamadı —
  bağlantıyı kontrol et."* diyor.

---

## Çalışmaya devam etmesi gerekenler

- Video panelinin bugünkü seçimleri bugünkü gibi kalır: iki sekme, *"Model"*, *"Kapsam"*, *"Üretim
  modu"*, *"Varyant"*, *"Kuyruğa ekle"*. Uzunluk bunlara eklenir.
- WAN oturumunda video paneli bugünkü gibi.
- Export ekranının özetindeki toplam süre doğru kalır: farklı uzunlukta videoları olan projede her
  videonun kendi uzunluğu toplanır.
- Sohbet nerede durursa dursun, *"Fotoğraf üret"*, *"Video üret"*, *"Ses üret"*, *"Kuyruk"* ve
  *"Üreticiler"* panelleri bugünkü gibi açılır.

---

## Sahibine sorulacak açık noktalar

- **Uzunluk (1):**
  - *"Referanstan"* sekmesinden üretilen videolar da seçili uzunlukta mı çıkar? Bu sekme yalnız
    H3'le üretiyor. Cevap seçimin yerini değiştirir: yalnız *"Kareden"* sekmesinde mi, iki sekmenin
    de gördüğü bir yerde mi.
  - Karenin sayfasından üretilen H3 videosu (*"Yeniden üret — yeni kare"*, *"Tekrar dene — bu
    kareye"*) projenin seçili uzunluğunda mı çıkar?
  - Kuyrukta bekleyen videolar: uzunluk o arada değişirse, kuyruğa eklendikleri uzunlukta mı
    çıkarlar, yenisinde mi?
- **Sohbet (2):**
  - Agent çalışırken ekranda ne görünür: yalnız çalıştığı mı, yoksa o an ne yaptığı da mı (bir kareyi
    okuyor, bir görsele bakıyor)?
  - Agent çalışırken yeni soru yazılabilir mi, ve çalışan agent durdurulabilir mi?
  - Sohbet sayfa yenilenmeden de boşalır mı: panel kapanıp açılınca, karenin sayfasına girip
    galeriye dönünce, başka bir projeye geçip geri gelince? Her projenin kendi sohbeti mi var?
  - Sohbeti sayfayı yenilemeden temizlemenin bir yolu olacak mı?
  - Agent'ın bir soruda atabileceği adım sayısı sınırlı. Sınıra gelip cevaba ulaşamazsa ekranda ne
    görünür?
