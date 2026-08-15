# QueenAgent tasarım v2 — verilen kararlar

**Tarih:** 2026-08-14 · Kaynak: [fark belgesi](2026-08-14-mira-tasarim-farklari.md) okunduktan sonra
kullanıcının madde madde verdiği kararlar.

Bu belge **yol haritası değildir** — ne sıra verir ne iş kırar. Fark belgesi karar taşımadığı için,
kararlar burada duruyor. Bir sonraki turun spec'i bunları girdi olarak alır.

Her maddede önce tasarımın ne dediği, sonra kararın ne olduğu yazılı. Fark belgesindeki madde
numaraları parantez içinde.

---

## Tasarımı olduğu gibi kabul edenler

**1. Model düğmesinin yeri** (madde 35 — çelişki çözüldü)
Sözleşmenin metin hâli "sol alt", sayfa hâli ve çalışan örnek "sağ alt" diyordu. **Sağ alt kazandı:**
composer'ın alt satırında sırayla Skills · model · Send.

**2. Yıkıcı renk** (madde 74 — çelişki çözüldü)
Renk tablosu `#8F4A2C`, geri kalan her şey `#B23A2E` diyordu. **`#B23A2E` kazandı** — palete gerçek
bir kırmızı giriyor ve uygulamada ilk kez dolu kırmızı bir düğme görünüyor.

**3. Hareket** (madde 76 — çelişki çözüldü, madde 87 de kapanıyor)
Sözleşme 140–220ms saydamlık geçişi diyordu, kendi çalışan örneği 400/350ms ve 6px yukarı süzülme
yapıyordu. **Yazılı kural kazandı:** hareket yalnız 140–220ms'lik saydamlık geçişi, artı rayın
220ms'lik genişlik geçişi. Yerleşmiş hiçbir öğe yana ya da yukarı kaymıyor. Bu aynı zamanda bugünkü
uygulamanın Mira v1'den sapmasını da kapatıyor.

**4. Sohbet yeniden adlandırma kalkıyor** (madde 22 — çelişki çözüldü)
Sözleşme "sohbetler yeniden adlandırılamaz" diyordu ama duyarlı yerleşim tablosu 780px'te "`name`
düğmesi gizlenir" diyerek düğmenin varlığını varsayıyordu. **Kalkıyor.** Yeniden adlandırma yalnız
**projede** kalıyor — proje başlığındaki "Rename" ve kenar çubuğu satırının ⋯ menüsündeki "Rename",
iki kapı.

**5. Composer ekranın altına sabit** (madde 13)
Mesaj listesi kayar, composer yerinde durur ve kaydırılınca **kaybolmaz**. Bugün dar pencerede
composer mesajlarla birlikte yukarı kayıyor; düzelecek.

**6. Logo karesi kalkıyor** (madde 2)
Yerine bir şey konmuyor; kenar çubuğunun tepesinde yalnız serif kelime markası kalıyor.

---

## Tasarımın sustuğu yerlerde verilen kararlar

**7. Dosyasız cevap kalıyor** (madde 48)
Tasarımın çekirdek döngüsünde akış biter bitmez tek bir dosya doğuyor; dosyasız cevap diye bir hâl
yok ve tasarım bunu ne kaldırılanlar ne açık maddeler arasında anıyor — hiç konuşmuyor. **Bugünkü
davranış kalıyor:** dosya yazılıp yazılmayacağına model karar veriyor, bir turda birden çok dosya da
yazabiliyor. Gerekçe: amaç alanı serbest bir çalışma alanında her cevabın dosya doğurması projeyi
doldurur — Mira v1 bu hâli bilerek eklemişti.

**8. "Bulunamadı" ekranları kalıyor** (madde 66)
Tasarımda yoklar, ama sebebi bir karar değil: prototipin verisi bellekte duruyor ve adres çubuğu
yok, yani o durum orada oluşamıyor. Mira'nın gerçek adresleri ve gerçek diski var. **Üçü de kalıyor:**
"That project does not exist.", "That chat does not exist.", "That file is gone."

**9. Projenin rengi kalkıyor, noktası kalıyor** (madde 5)
Doğrulamada çıktı ki nokta tasarımda duruyor; tasarım yalnız **projeye özel renkten** hiç söz
etmiyor. **Renk kalkıyor:** noktalar duruyor ama hepsi tek tonda. Gerekçe: görsel dilin "tek vurgu
rengi, yalnız birincil eylemi işaretler" kuralı harfiyen tutuluyor.

**10. Kullanıcı adı etiketi kalkıyor** (madde 3)
Tasarım mesajın üstünde kişinin adını çiziyor ("ALEX · 14:32") ama adın nereden geleceğini
söylemiyor; Mira v1 ise "kullanıcı adı diye bir ayar yok" diye karar vermişti. **Ad etiketi tümüyle
kalkıyor**, yerinde yalnız saat kalıyor — kimin yazdığı balonun sağa yaslı olmasından belli.

**11. Açılır menü ekrana sığmazsa** (madde 36 — çelişki çözüldü)
Sözleşmenin bir hâli "composer genişliğiyle sınırla", öteki "ekrana göre ölç, yer yoksa alta çevir"
diyordu. **İkisi de gerekmiyor:** composer her boyda ekranın altına sabit olduğu için menünün
üstünde her zaman ekranın tamamı var, yani "yer yoksa alta çevir" durumu hiç oluşmuyor. Karar:
menüye **azami yükseklik** verilir ve aşarsa **kendi içinde kayar**. Menü kendi genişliğinde (296px)
durur, düğmesine sağdan hizalanır.

**12. Dosyanın adını model söylemeye devam ediyor** (madde 4)
Tasarımın çalışan örneği adı kullanıcının cümlesinden türetiyor (ilk üç kelime, tirelerle), ama bu
kural yalnız prototipin **kodundan** okunuyor ve tasarımın kendi kuralı "prototipin kodu bağlayıcı
değil" diyor. **Bugünkü kural kalıyor:** adı model söyler, ad temizlenir, çakışırsa numaralanır.
Gerekçe: üç becerili akışta (senaryo → sahne bölme → promptlar) "ilk üç kelime" kuralı üç dosyaya da
birbirine benzeyen adlar verirdi; modelin verdiği ad ayırt edici olur.

**13. Bir haftadan eski zaman** (madde 14)
Tasarım "1 week ago"ya kadar gidip susuyor. **Bir haftadan sonra gerçek tarihe dönülüyor** ("12 Aug").
Gerekçe: arama ve sohbet yeniden adlandırma kalktığı için eski bir kaydı bulmanın kalan yolu ad ve
tarih.

---

## Tasarımdan bilerek ayrılanlar

Bunlar tasarımın açıkça söylediğinden farklı. Tasarım projesi kullanıcı tarafından sonradan
güncellenecek (karar 19); o güne kadar geçerli olan bu belgedir.

**14. Home'da composer yok** (madde 18 düşüyor, madde 37'nin Home ayağı düşüyor)
Tasarım Home'u "composer + proje ızgarası" diye tarif ediyor ve Home'dan gönderilen mesajın var olan
bir projeye düşmesini istiyor — ama hangi projeye düşeceğini söylemiyor ve `project: X` etiketini de
kaldırdığı için ekranda hiçbir işaret kalmıyor. **Karar: Home'dan mesaj gönderilmiyor.** Home yalnız
"Projects" başlığı, "New project" düğmesi ve kart ızgarasından oluşuyor. Mesaj her zaman bir projenin
içinden yazılıyor. Hiç proje yokken zaten kendi boş hâl ekranı devrede.

**15. "New chat" yalnız proje seçiliyken var** (madde 9'un kuralı sıkılaşıyor)
Tasarım "New chat"i yalnız **hiç proje yokken** gizliyor. **Karar: proje seçili değilken de
gizleniyor.** Sohbetler projeye bağlı olduğu için, proje seçili değilken böyle bir seçenek hiç
görünmemeli. Basınca **bulunulan projede** yeni sohbet açıyor; Home'a uğramıyor. Proje seçili
değilken kenar çubuğunda "Recent chats" de yok — yalnız kelime markası ve proje listesi kalıyor.

**16. Geri alma tümüyle kalkıyor** (madde 27 ve 31 düşüyor)
Tasarım dosya silmeyi onaysız ve geri alınabilir, proje silmeyi onaylı ve geri alınabilir yapıyor —
asimetriyi bilerek kuruyor. **Karar: ikisi de sorar, hiçbirinde geri alma yok.** Dosya silmede
"emin misin" onayı gelir, satır içi "File deleted. / Undo" şeridi kalkar. Proje silmede modal kalır,
ekranın altındaki koyu şerit ve "Undo" kalkar.

**Diskte hiçbir şey kaybolmuyor:** silinen dosya `trash/` klasörüne taşınmaya devam ediyor.
`FOUNDATION.md`'nin "ya onay ya geri alma, asla ikisi de değil" kuralı onay tarafından karşılanıyor.

**17. Sohbet silme onay soruyor** (madde 29)
Tasarım "× basılır basılmaz gider, ne soru ne geri alma" diyor — ama aynı belge "sohbet silmeden önce
onay"ı kendi **açık maddesi** olarak sayıyor, yani karar verilmemiş. **Karar: onay soruluyor**, ve
tarayıcının kendi kutusuyla değil, **tasarımın modal'ıyla** — proje silmedekiyle aynı dil. Böylece
uygulamada tek bir onay dili oluyor.

---

## Skills

**18. Beceriler** (madde 33)
Tasarımın çizdiği dört seçenek (Web search, Deep research, Data & tables, Code) **yer tutucudur.**
Gerçek küme:

1. **Senaryo oluştur**
2. **Senaryoyu parçalara böl** — hangi sahne kaç prompt olacak
3. **Promptları oluştur**

Üçü de **bağımsız** seçimdir: kullanıcı her mesajda birini seçer. Zincir gibi çalışırlar ama zinciri
kullanıcı kurar — her beceri projedeki dosyaları okuyarak bir öncekinin çıktısıyla çalışır ve hangi
dosyayla çalışacağını kullanıcı mesajında söyler.

**Yeni araç gerekmiyor.** Üçü de modele verilen yönergeden ibaret; `list_files` ve `read_file` zaten
var. Motor tarafına dokunulmuyor.

**Bunun bir sonucu var:** bu beceri kümesi ürünü genel amaçlı bir çalışma alanı olmaktan çıkarıp bir
üretim hattının ön yüzüne çeviriyor. `CLAUDE.md`'nin "hiçbir üretim hattına bağlı değil" cümlesi ve
Mira v1'in "amaç alanı serbesttir" cümlesi artık doğru değil; ikisi de güncellenmeli.

---

## Süreç

**19. Tasarım projesini kullanıcı güncelleyecek.**
Tasarım projesine dokunulmuyor. Yukarıdaki ayrılıklar bu belgede taşınıyor; kullanıcı tasarımı kendi
zamanında güncelleyecek. O güne kadar tasarım tek kaynak değil — bu belge onun üstüne biniyor.

---

## Henüz karar verilmemişler

Fark belgesinde duran, bu turda sorulmamış ya da bir sonraki tura bırakılmış konular:

- **Ürün adı değişikliğinin ne zaman ve nasıl yapılacağı** (madde 1) — klasör adı, `MIRA_ROOT`,
  `CLAUDE.md` bölümü, iki belge başlığı, arayüz metinleri. Karar yol haritası turuna kaldı.
- **Bölüm 3'teki 12 sapmanın** (madde 78–89) ne zaman düzeltileceği. Bir kısmı tasarım v2 o yeri
  baştan yazdığı için kendiliğinden düşecek (yarıçaplar, hareket süreleri); hata dili ve `loading`
  gibi olanlar bağımsız.
- Tasarımın cevaplamadığı küçük konular: dosya adı ikinci kez aynı çıkarsa ne olacağı ("numaralanır"
  kararı verildi ama tasarım susuyor), proje yaratmanın yollarının yazıya geçmemiş olması.
