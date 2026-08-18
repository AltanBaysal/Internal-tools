# QueenAgent — Yol Haritası v2

**Tarih:** 2026-08-15 · **Branch:** `fix/mira` · **Durum:** yazıldı, koşu bekliyor.
**Kaynaklar:** [fark belgesi](../research/2026-08-14-mira-tasarim-farklari.md) (madde numaraları
oradan) · [kararlar belgesi](../research/2026-08-14-mira-tasarim-kararlari.md) (19 karar) · tasarım
projesi *"Mira AI tasarımı istemi"* (`3c06e399…`, dosyalar `QueenAgent*`). Çelişkide sıra:
**kararlar belgesi > yazılı sözleşme > çizim**.

**9 faz, 35 madde.** Taban Mira v1'in bitmiş hâli; bu tur onu QueenAgent tasarım v2'ye taşır. Her
madde çıktı odaklıdır (**ne çalışır** + **nasıl görülür**) ve sırası bağımlılıktan çıkar: bir madde
yalnız kendinden önceki fazların ürettiğine yaslanır.

---

## Nasıl çalışacağız

Birim **maddedir**. Her madde dört adımdan geçer:

1. **Spec** — maddenin açık soruları karara bağlanır (`docs/superpowers/specs/`). Sorusu olmayan
   küçük maddede spec kısa düşer, atlanmaz.
2. **Plan** — TDD adımlarıyla uygulama planı (`docs/superpowers/plans/`).
3. **TDD** — iki ayrı commit: önce yalnız testler (kırmızı gider), sonra implementasyon. İstisnasız.
4. **Kapanış** — tam takım yeşil.

**Test komutu tektir ve hiç değişmez.** Koşu boyunca, her seferinde harfi harfine bu dize:

```
python -m pytest queenagent -q; npm test --prefix queenagent/frontend
```

Başına `cd`, sonuna `| grep` / `| tail` yok; tek dosya, tek test, tek suite koşmak için ayrı bir dize
kurulmaz — dize her değiştiğinde yeni bir onay penceresi açılır ve koşu durur. Kullanıcı bunu bir kez
"allow for this session" ile onaylar; gerisi durmadan akar. Çıktıdan yalnız bir satırla ilgileniyorsan
onu gözünle süz, komuta boru ekleme. Kırmızı adımda da aynı dize koşulur — beklenen kırmızı, çıktıdan
okunur.

**Varsayma, sor.** Koşu maddeler arasında durmaz — ama spec yazarken bir şey **gerçekten belirsizse**
orada durulur ve kullanıcıya sorulur. **Beceriler bunun ilan edilmiş istisnasıdır:** Madde 27'den
Madde 30'a kadar her madde, spec yazılmadan önce kullanıcıyla birlikte tasarlanır — orada koşu
durur, soru beklemez. Ölçüt "emin değilim" değil, **"iki farklı okuma iki farklı ürün
üretir"**dir. Sorulacak şeyler yalnız kullanıcı deneyimi değil, teknik de olabilir:

- Geri dönülemez olan her şey: disk düzeni ve dosya biçimi, veri göçü, kalıcı alan adları, uç nokta
  sözleşmesi, silinen bir yeteneğin geri getirilemez hâle gelmesi.
- Kullanıcının alışkanlığını bozan her şey: bir eylemin yerinin, adımının ya da sonucunun değişmesi.
- Kaynakların çeliştiği ve [kararlar belgesinin](../research/2026-08-14-mira-tasarim-kararlari.md)
  susduğu her yer.

Sorular **düz metinle** sorulur: tek soru, numaralı kısa seçenekler, bir cümlelik öneri, "hangisi?".
Cevap gelmeden o maddenin planı yazılmaz. Küçük ve geri alınabilir seçimlerde sorulmaz — makul olan
seçilir, spec'te tek cümleyle gerekçesiyle yazılır.

**Deneme en sonda, toplu:** maddeler tek tek elle denenmez, hepsi Madde 35'te bir dalgada denenir.
Bir maddenin *nasıl görülür* satırı o maddenin kabul kriteridir — testler o satırı kanıtlar.

**Silme de TDD ile yürür:** önce "artık yok" testi yazılır (uç nokta 404 döner, düğme çizilmez),
sonra kod sökülür. Ölü kod bırakılmaz: kullanılmaz hâle gelen use case, kanca ve test dosyası aynı
maddede gider.

## Kod kuralları

**Yapıyı iki dosya belirler ve ikisi de bağlayıcıdır:** `queenagent/FOUNDATION.md` (ilkeler ve yığın
kararları) ve `queenagent/CODE-STANDARD.md` (katmanlar ve dosya düzeni). Madde 1'e kadar ikisi de
`mira/` altındadır.

**Bu bir gate'tir, tercih değil.** Her maddede:

- **Spec yazılırken** ikisi de açılıp okunur; maddenin dokunduğu kurallar spec'te adıyla anılır.
- **Plan yazılırken** her yeni dosyanın hangi katmana düştüğü yazılır — `domain/`, `data/`,
  `presentation/`, `services/`, `web/` ya da ön yüzde `features/workspace/` veya `shared/`.
- **Kapanışta** bağımlılık yönü denetlenir: `presentation → domain ← data → services`. Yasaklar
  istisnasız: `feature ↛ feature`, `service ↛ feature`, `service ↛ service`. Somut sınıflar yalnız
  kompozisyon kökünde bağlanır.
- Bir madde bu kuralları tutturamıyorsa **madde durur ve kullanıcıya sorulur** — kural sessizce
  esnetilmez. İki belgeden birinin değişmesi gerekiyorsa o kendi başına bir karardır.

Bu koşuda en çok işe karışacak kurallar:

- **Kural arka uçta, ön yüz görüntüdür.** Seçimlerin sohbete yapışması, silme, adlandırma — hepsi
  arka uçta yaşar ve orada test edilir.
- **Kullanıcının emeği kutsaldır.** Geri alma arayüzden kalkıyor ama **diskten kalkmıyor**: silinen
  şey `trash/`e taşınır, yok edilmez. Onay + çöp, "ya onay ya geri alma" kuralını karşılar.
- **Hata mesajında sebep uydurulmaz.** Tasarımın "The connection dropped." cümlesi alınmaz; ekrana
  sunucunun gerçek sözleri çıkar. Repo kuralı tasarımı yener.
- **Görsel dilin sahibi `shared/app.css`.** Renk, yarıçap, odak halkası, animasyon — bileşen kendi
  değerini icat etmez.
- **Dil:** arayüz metni, kod, yorum, test adı ve commit mesajı **İngilizce**; bu belgeler Türkçe.

---

## Faz 0 — Ad

### Madde 1 — Mira → QueenAgent

- **Ne çalışır:** tam ad değişikliği, dört katman birden: klasör `mira/` → `queenagent/`;
  `MIRA_ROOT` → `QUEENAGENT_ROOT`; belgeler (`CLAUDE.md` bölümü, `FOUNDATION.md` ve
  `CODE-STANDARD.md` başlıkları, test komut yolları); arayüz metinleri (kelime markası, cevap
  etiketi, boş hâl cümleleri, çevrimdışı şeridi) ve modele giden "You are Mira…" yönergesi.
- **Nasıl görülür:** repoda `mira` araması yalnız tarihî belgelerde (v1 spec/plan/research) sonuç
  verir; uygulama açılır, her yerde QueenAgent yazar; `pytest` ve `npm test` yeşil.
- **Dikkat:** bu madde **tek başına, başka Claude penceresi kapalıyken** koşulur — klasör taşıma
  repodaki hemen her dosyaya dokunur, paralel commit çakışması büyük olur.
- **Spec'te karara bağlanacak:** kullanıcının diskindeki eski `MIRA_ROOT` verisinin yeni köke nasıl
  taşınacağı (kendiliğinden mi, elle mi).

---

## Faz 1 — Söküm

Her madde bağımsızdır; sıra içlerinde serbesttir.

### Madde 2 — Arama gider *(fark 6)*

- **Ne çalışır:** arama bütünüyle sökülür: kenar çubuğu düğmesi ve ⌘K rozeti, ⌘K/Ctrl+K bağları,
  katman, panel, kancası, use case'i, uç noktası, testleri. Esc sırasından arama düşer.
- **Nasıl görülür:** ⌘K'ya basmak hiçbir şey yapmaz; arama uç noktası 404 döner; kenar çubuğu adın
  altından doğrudan "New chat" ile başlar.

### Madde 3 — Home kalkar, açılış ilk projeye iner *(fark 12, 16, 17; karar 14)*

**Spec'teki iki soru kullanıcıya soruldu ve maddenin kapsamını değiştirdi.** Verilen karar: proje
seçilmeden sohbet olmaz; proje varsa açılışta **ilk proje** seçili gelir; yoksa "projen yok, bir
tane oluştur" ekranı gelir. Bunun sonucu **Home diye bir ekranın hiç kalmamasıdır** — kart ızgarası
proje varken zaten görünmeyeceği için tümüyle gider, "Home'a dönüş yolu" sorusu da kendiliğinden
düşer. Ayrıntı: [tasarım belgesi](../specs/2026-08-17-queenagent-m3-home-design.md).

- **Ne çalışır:** `/` bir ekran değil bir **çataldır** — liste geldikten sonra proje varsa ilk
  projeye iner (`replaceState`, geçmişe yazılmaz), yoksa boş hâl ekranını çizer, liste gelemezse
  sunucunun hata cümlesini gösterir. Boş hâl: "No projects yet" + tek cümle + dolu "+ New project".
  Home ekranı, kart ızgarası, selamlama, üç öneri hapı ve Home composer'ı gider;
  `start_chat_in_new_project` zinciri (`POST /api/chats` dahil) sökülür. Hiç proje yokken kenar
  çubuğundaki "New chat" gizlenir.
- **Nasıl görülür:** sıfır projeyle açılışta boş hâl ekranı ve kenar çubuğunda "New chat" yok; en az
  bir projeyle açılışta doğrudan o projenin ekranı ve adres `/p/<ilk>`.
- **Konusuz kalanlar:** fark 15 (sayaçların tekil hâli), 16, 17, 19 (Home sütununun üst boşluğu) ve
  Madde 33'ün "< 780px'de Home kartları tek sütuna iner" ayağı — hepsinin öznesi silindi.

### Madde 4 — Proje açıklaması gider *(fark 20)*

- **Ne çalışır:** açıklama hem veri alanı hem arayüz olarak sökülür: proje ekranındaki paragraf,
  karttaki ikinci satır, düzenleme yolu, `project.json`'daki alan, use case'teki dalları.
- **Nasıl görülür:** yeni proje açıklamasız doğar; kart iki satırdır — nokta+ad, sayaç; eski
  `project.json`'lardaki alan okunursa sessizce yok sayılır.

### Madde 5 — Yeniden adlandırmalar, `← back`, yardım notları gider *(fark 21, 22, 23, 30, 37; karar 7)*

- **Ne çalışır:** sohbet ve dosya satırlarındaki "name" düğmeleri, use case'leri ve uç noktaları
  sökülür — yeniden adlandırma yalnız projede kalır. Proje ekranındaki `← back`, composer
  ayaklarındaki mono notlar ve dosya listesinin altındaki "Chats create the files…" satırı gider.
- **Nasıl görülür:** sohbet/dosya satırında yalnız aç ve sil kalır; proje ekranı başlıkla başlar;
  composer ayağında yalnız düğmeler durur.

### Madde 6 — Kenar çubuğu kuralı ve logo *(fark 2, 8, 9; karar 15, 18)*

- **Ne çalışır:** "New chat" ve "Recent chats" yalnız **bir proje seçiliyken** görünür; seçili
  değilken kenar çubuğunda kelime markası ve proje listesi kalır. "New chat" basınca **bulunulan
  projede** yeni sohbet açar, Home'a uğramaz. "Recent chats" yalnız o projenin sohbetlerini, en çok
  8 tanesini listeler. Logo karesi gider; tepe yalnız serif kelime markası.
- **Nasıl görülür:** Home'dayken kenar çubuğunda ne "New chat" ne "Recent chats" var; projedeyken
  "New chat" boş bir sohbet ekranı açıyor; listede en çok 8 satır.

### Madde 7 — Kenar çubuğu daralma basamakları *(fark 10)*

- **Ne çalışır:** tek adımlı 280→208 daralma, dört basamağa çıkar: 280 → 226 → 198 → 172px; iç
  boşluk yalnız en dar basamakta sıkışır. (Yerleşimin geri kalan eşikleri Madde 33'te.)
- **Nasıl görülür:** pencere daraldıkça kenar çubuğu üç eşikte kademeli iner, içerik kırılmaz.

---

## Faz 2 — Zemin

### Madde 8 — Renkler *(fark 74, 75; karar 2, 9)*

- **Ne çalışır:** palete yıkıcı aile girer: `#B23A2E` (hover `#973026`), çerçeve `#EBCFC9`, yumuşak
  zemin `#FDF4F2`. Vurgu ayrışır: dolu vurgu düğmesi hover'da `#9E5232`, bağlantı `#8F4A2C` kalır.
  Proje noktaları tek tona iner; `project.json`'daki renk alanı ve üretimi sökülür. Hepsi
  `shared/app.css` değişkenlerinde.
- **Nasıl görülür:** silme yüzeyleri kırmızı ailededir; bütün noktalar aynı tondadır; iki proje
  yan yana ayırt edilmez renkle, adla ayrılır.

### Madde 9 — Yarıçaplar, çip, dosya satırı *(fark 38, 54, 56, 77; sapma 88, 89 kapanır)*

- **Ne çalışır:** yarıçap kümesi üçe toplanır — denetim 8px, kart 12–14px, hap 20px; composer 14px
  olur (Home'unki yok artık), kenar çubuğu denetimleri 9'dan 8'e iner. Uzantı çipi 30×30 sabit kare
  olur (`#F0E7DE`, 7px, ortalanmış 9.5px mono). Dosya satırı iki satıra açılır: ad üstte, altında
  mono "project file · 2h ago". Kenar çubuğundaki dosya sayısı rozeti sıfırken yazısını
  saydamlaştırıp yerini korur *(fark 15)*.
- **Nasıl görülür:** yan yana duran köşeler eşleşir; uzun uzantı satır hizasını bozmaz; dosya satırı
  dosyanın kime ait olduğunu kendisi söyler.

### Madde 10 — Hareket bandı *(fark 76; sapma 87 kapanır; karar 6)*

- **Ne çalışır:** hareket 140–220ms'lik saydamlık geçişlerine iner; ekran ve kart girişlerindeki
  yukarı süzülmeler gider; ray genişlemesi 220ms kalır. `app.css`'teki animasyon seti buna göre
  sadeleşir.
- **Nasıl görülür:** ekranlar yerinden oynamadan belirir; hiçbir yerleşmiş öğe kaymaz.

### Madde 11 — Kaydırma sözleşmesi *(fark 13; karar 10)*

- **Ne çalışır:** kabuk `100dvh`e sabitlenir (600px tabanı gider), zincirdeki her sütun
  `min-height: 0` taşır, kayan tek şey iç listelerdir; composer her pencere boyunda ekranın altına
  sabittir ve kaydırmayla kaybolmaz. Hiçbir genişlikte yatay kaydırma çıkmaz.
- **Nasıl görülür:** en kısa pencerede bile sayfa kaymaz, composer yerindedir; mesaj listesi kendi
  içinde kayar.

### Madde 12 — Odak halkası her yerde *(sapma 86 kapanır)*

- **Ne çalışır:** composer'ın metin alanı dahil her odaklanabilir öğe 2px vurgu renkli halkayı alır;
  hiçbir bileşen kendi odak stilini yazmaz.
- **Nasıl görülür:** sekmeyle dolaşırken odak hiçbir durakta görünmez olmaz.

---

## Faz 3 — Metin

### Madde 13 — Markdown ve iki ölçek *(fark 39, 40)*

- **Ne çalışır:** cevaplar Markdown çizilir: dört düzey başlık, kalın/eğik/üstü çizili, satır içi
  kod, çitli kod bloğu, listeler, tablo, alıntı, yatay çizgi, bağlantı. Sohbette **balon ölçeği**
  (h1 19.5 / h2 17 Newsreader, h3 14.5 DM Sans 600). **Kullanıcı mesajı ham kalır.**
- **Nasıl görülür:** `**test**` kullanıcı balonunda yıldızlarıyla, cevapta kalın görünür; tablo
  mono başlıklı çizilir.

### Madde 14 — Akış görselleri *(fark 41, 42, 43)*

- **Ne çalışır:** akan metin her parçada yeniden ayrıştırılır; kapanmamış kod çiti çizim sırasında
  kapatılır. Metnin ucunda 7×15 yanıp sönen blok imleç durur, akış bitince kaybolur. Otomatik
  kaydırma: yeni mesajda liste dibe atlar; akış sürerken yalnız kullanıcı dibe 220px'ten yakınsa
  yapışır.
- **Nasıl görülür:** yarım gelen kod bloğu düzeni bozmaz; yukarı çıkıp okuyan biri hiç kesilmez.

### Madde 15 — Mesaj etiketleri ve bekleme bloğu *(fark 3, 46, 47; sapma 80 kapanır; karar 9)*

- **Ne çalışır:** kullanıcı balonunun etiketi yalnız **saat** olur — ad yok. Cevap tarafı
  "QUEENAGENT · saat" olur ve saat beklemenin başından itibaren durur; üç nokta ile etiket arası
  10px. "creating file…" kutusu üç noktanın hemen altına, bekleme bloğunun içine taşınır; solunda
  30×30 boş rozet yeri, genişliği en çok 340px.
- **Nasıl görülür:** bekleme anında etiket saatlidir; dosya doğarken kesikli kutu ile noktalar
  birlikte durur ve kutu doğacak kartın iskeletini taşır.

### Madde 16 — Hata dili *(fark 63; sapma 81, 82 kapanır)*

- **Ne çalışır:** tarayıcının istek yolu sunucunun gövdesini atmaz: ekrana çıkan hata, sunucunun
  kendi cümlesidir (HTTP kodu + gövde). Reddedilen mesaj tek satır hatayla anlatılır, "Couldn't get
  a response." kartı yalnız akış öldüğünde çıkar; kartın altında sunucunun gerçek sözleri durur —
  tasarımın "The connection dropped." cümlesi **alınmaz** (repo kuralı: sebep uydurulmaz).
- **Nasıl görülür:** ad çakışması gibi bir redde sunucunun cümlesi okunur, "failed with 409" değil.

---

## Faz 4 — Yıkıcı eylemler

### Madde 17 — Onay kutusu bileşeni *(fark 26'nın görsel yarısı; karar 1)*

- **Ne çalışır:** ekranı karartan tek onay kutusu deseni: serif başlık, sonucu anlatan cümle,
  "Cancel" + dolu kırmızı onay düğmesi; Esc ve karartıya tıklama iptal sayılır. Uygulamadaki tek
  onay dili budur — tarayıcı kutusu hiçbir yerde kalmaz.
- **Nasıl görülür:** kutu açıkken arka plan kararır; Esc iptal eder; onay düğmesi `#B23A2E` doludur.

### Madde 18 — Proje silinir *(fark 26, 28; karar 16)*

- **Ne çalışır:** proje silme gelir: arka uçta silme, içerik `trash/`e taşınarak; arayüzde iki kapı —
  proje başlığında "Rename"in yanında kırmızı çerçeveli "Delete", kenar çubuğu satırında hover'da
  beliren ⋯ düğmesi ve 176px menüsü ("Rename" / kırmızı "Delete project"; ekrana kıstırılır, Esc ve
  dış tıklama kapatır). Onay kutusu «Delete "X"?» + "The N chats and N files…" (tekilde "1 chat")
  der. İçinde bulunulan proje silinirse kalan ilk projeye (yoksa boş ekrana) geçilir; başka proje
  silinirse açık sohbet ve kaydırma kıpırdamaz. **Geri alma yok** — şerit de yok. Başlık satırı
  yeni düğmeyle sığmazsa sarar; sığmayan düğmeler alt satıra iner *(fark 25)*.
- **Nasıl görülür:** iki kapı da aynı kutuyu açar; onaydan sonra proje listeden düşer, diskte
  `trash/` altında durur.
- **Spec'te karara bağlanacak:** projenin çöp düzeni (`trash/` altında iç yapısı) ve çöpün elle
  boşaltılma yolu.

### Madde 19 — Sohbet ve dosya silme onaya geçer *(fark 27, 29, 31; karar 16, 17)*

- **Ne çalışır:** sohbet silme tarayıcı kutusundan Madde 17'nin kutusuna geçer ("Its files stay in
  the project." cümlesi kalır). Dosya silme **onay sorar** olur: anında silme ve "File deleted. /
  Undo" şeridi kalkar, geri yükleme uç noktası sökülür. İkisi de `trash/`e taşımayı sürdürür.
  Sohbet satırındaki "×" artık hover beklemez: her zaman görünür durur (`#B5ADA2`), üstüne gelince
  kırmızılaşır *(fark 24)*.
- **Nasıl görülür:** her silme aynı dili konuşur — sor, sonra sil; hiçbir yerde Undo yok; silinen
  şey diskte `trash/` altında.

---

## Faz 5 — Ray ve dosya

### Madde 20 — Ray katlanır *(fark 50, 51)*

- **Ne çalışır:** ray başlığı katlama düğmesi olur: "Project files" + dosya sayısı + şevron. Basınca
  ray 46px dikey şeride iner (etiket döndürülmüş, sayı okunur), şeride basmak geri açar; geçiş
  220ms. Durum oturum boyunca sohbetler ve projeler arasında korunur; bir dosyayı açan her eylem
  rayı zorla açar.
- **Nasıl görülür:** katla → daralır; başka sohbete geç → katlı kalır; transkriptte karta tıkla →
  kendiliğinden açılır.

### Madde 21 — Ray satırı ve zemin *(fark 45'in satır yarısı, 52, 57)*

- **Ne çalışır:** raydaki satır sadeleşir — yalnız çip, ad, ikincil satır; tek işi dosyayı açmak
  (silme yalnız proje ekranındaki listede). Ray kendi zeminini alır (`#FBF9F5`). Açık dosyanın
  satırı `#EFEBE4` zeminle seçili durur, hover `#F0ECE5`.
- **Nasıl görülür:** rayda × ve "name" yok; hangi dosyanın açık olduğu listeden okunur.

### Madde 22 — Dosya kartı kapı olur *(fark 44, 45'in kart yarısı)*

- **Ne çalışır:** cevabın altındaki kart düğmedir: sağında mono "Open ›", basınca dosya panelde
  açılır (ray katlıysa önce açılır). Açık dosyanın kartı `#F4EFE7` zemin + `#CFC3B2` çerçeve alır ve
  ipucu "open" olur. Kart en çok 340px, 12px yarıçap.
- **Nasıl görülür:** karta tıkla → panel o dosyayı gösterir; panelin hangi dosyada olduğu hem karttan
  hem ray satırından okunur.

### Madde 23 — Okuyucu *(fark 58, 59, 60)*

- **Ne çalışır:** dosya içeriği **belge ölçeğiyle** Markdown çizilir (h1 25 / h2 20 / h3 15.5;
  14.5px, 1.8, 26/28 iç boşluk). Başlık tepeye, alt bilgi dibe sabitlenir; alt bilgi "2h ago ·
  project file" der. Proje ekranındaki panelin başlığı: ad, "Download", sağda "×" — geri oku yok;
  sohbet rayındaki panel "←" ile kalır.
- **Nasıl görülür:** uzun dosya kayarken başlık ve alt bilgi yerinde durur; içerik biçimli çizilir.

### Madde 24 — Panel açıkken dosya sütunu kalkar *(fark 61)*

- **Ne çalışır:** proje ekranında panel açıkken dosyalar sütunu hiç çizilmez; solda başlık, composer
  ve sohbet listesi kalır. Panel kapanınca sütun geri gelir.
- **Nasıl görülür:** aynı liste iki yerde birden durmaz.

---

## Faz 6 — Seçiciler

### Madde 25 — Menü deseni *(fark 35, 36, 67, 68; karar 4, 11)*

- **Ne çalışır:** ortak açılır menü deseni: tetikleyicisine **sağdan** hizalanır, composer'ın
  üstüne açılır, azami yüksekliği vardır ve aşarsa içinden kayar; ekranı kaplayan görünmez
  yakalayıcıyla dışa tıklama kapatır. Esc sırası yeniden bağlanır: proje ⋯ menüsü → onay kutusu →
  Skills → model → açık panel.
- **Nasıl görülür:** kısa pencerede menü ekrandan taşmaz, içinden kayar; Esc her basışta yalnız bir
  şey kapatır.

### Madde 26 — Model seçici *(fark 32, 34)*

- **Ne çalışır:** composer'ın sağ altında (Send'in solunda) model düğmesi: kapalıyken ad + şevron,
  hover'da soluk dolgu. Menü: mono "MODEL" başlığı, dört satır — Grok 4 (varsayılan), Grok 4 Fast,
  Grok 4 Heavy, Grok Code — birer satır açıklama, seçilide ✓. Seçim **sohbete yazılır** (arka uçta,
  sohbet kaydında), konuşma ortasında değiştirilebilir, son seçim yeni sohbetin varsayılanıdır;
  motor cevabı o sohbetin modeliyle üretir.
- **Nasıl görülür:** iki sohbette iki ayrı model seç, gidip gel → her biri kendininkini hatırlar;
  yeniden başlat → seçimler durur.

### Madde 27 — Skills seçici arayüzü *(fark 33; karar 3, 18'in arayüz yarısı)*

> **Dur ve birlikte tasarla.** Becerilerin tasarımı — Madde 27'den Madde 30'a kadar hepsi —
> kullanıcıyla konuşularak yapılır. Bu maddeye gelindiğinde spec yazılmadan önce durulur; koşu
> maddeleri arka arkaya götürmez. Karar 18 kümeyi (üç beceri) veriyor, geri kalanını kullanıcı
> veriyor.

- **Ne çalışır:** model düğmesinin solunda "Skills" düğmesi; menüde üç beceri: **Create scenario**,
  **Split into scenes**, **Generate prompts** (İngilizce etiketler spec'te kesinleşir). Tek seçim;
  seçiliye tekrar basmak temizler; seçiliyken düğme sıcak tonla boyanır ve becerinin adını taşır.
  Seçim sohbete yazılır; iki menü birbirini kapatır. Bu maddede beceri **yalnız kayıt edilir** —
  cevabı henüz değiştirmez.
- **Nasıl görülür:** beceri seç → düğme adını alır ve renklenir; sohbet değiştir → seçim sohbetle
  gider.

---

## Faz 7 — Beceriler

> **Dur ve birlikte tasarla.** Madde 27'de başlayan kural burada da geçerli: her becerinin
> yönergesi, beklenen çıktısı ve dosya biçimi kullanıcıyla konuşularak kararlaştırılır, sonra spec
> yazılır. Madde 30'un Python listesi zaten böyle işaretliydi; artık üçü de öyle.

Üç beceri de aynı mekanikle çalışır: seçili beceri, o sohbetin sistem yönergesine kendi ekini
koyar; model gerekirse projedeki dosyaları `list_files`/`read_file` ile okur. Beceriler
**bağımsızdır** — zinciri kullanıcı kurar: hangi dosyayla çalışılacağını mesajında söyler. Yeni araç
yoktur; motor tarafına dokunulmaz.

### Madde 28 — Senaryo oluştur

- **Ne çalışır:** ilk becerinin yönergesi yazılır ve seçiliyken cevabı yönlendirir: model bir
  senaryo üretir ve dosya olarak kaydeder.
- **Nasıl görülür:** beceri seçiliyken "bir senaryo yaz" → projeye senaryo dosyası düşer.
- **Spec'te karara bağlanacak:** yönergenin tam metni; senaryonun beklenen yapısı.

### Madde 29 — Senaryoyu parçalara böl

- **Ne çalışır:** ikinci beceri: projedeki bir senaryoyu okuyup sahnelere böler, her sahneye kaç
  prompt düşeceğini yazar; sonucu dosya olarak kaydeder.
- **Nasıl görülür:** senaryo dosyası olan projede beceriyi seç, "şu senaryoyu böl" → sahne listesi
  dosyası düşer.
- **Spec'te karara bağlanacak:** yönergenin tam metni; sahne/prompt sayısı biçimi.

### Madde 30 — Promptları oluştur

- **Ne çalışır:** üçüncü beceri: sahne listesini okuyup promptları üretir; **çıktı bir Python
  listesidir** ve dosya olarak kaydedilir.
- **Nasıl görülür:** sahne listesi olan projede beceriyi seç → Python listesi biçiminde prompt
  dosyası düşer.
- **Spec'te karara bağlanacak:** listenin tam biçimi (tek liste mi, sahne başına mı; değişken adı;
  dosya uzantısı) — **bu maddeye gelindiğinde kullanıcıyla birlikte detaylı tasarlanır.**

### Madde 31 — Belgeler ürünü yakalar

- **Ne çalışır:** `CLAUDE.md`'nin QueenAgent bölümü ve `FOUNDATION.md` güncellenir: "hiçbir üretim
  hattına bağlı değil" ve "amaç alanı serbesttir" cümleleri düşer; üç beceri ve amaçları yazılır.
- **Nasıl görülür:** belgeler ürünün yaptığı işi anlatıyor, eskisini değil.

---

## Faz 8 — Uçlar

### Madde 32 — Kalan sapmalar kapanır *(sapma 79, 83, 84, 85)*

- **Ne çalışır:** çekilemeyen liste boş liste gibi konuşmaz — hata satırı gösterir, boş hâl cümlesi
  yalnız yükleme başarıyla bittiğinde çıkar. Açık dosya proje değişince **kapanır**, gizlenip geri
  gelmez. Model `.md` dışında uzantı isterse `.md`'ye çevrilir. (Sapma 78 ve 79'un Home ayağı
  Madde 3'te kendiliğinden düştü.)
- **Nasıl görülür:** ağı koparıp proje aç → "No files yet" değil hata satırı; başka projeye gidip
  dön → panel kapalı; "report.txt iste" → `report.md` doğar.

### Madde 33 — Duyarlı yerleşim *(fark 70, 71, 72, 73)*

- **Ne çalışır:** ölçü pencereden **kabuğun ölçülen genişliğine** geçer (ResizeObserver); üç eşik:
  1000px — ray sohbetin altına iner (%44, en çok 250 en az 150, katlanınca tek başlık satırı), proje
  ekranı tek sütuna düşer, açılan panel alanın tamamını alır; 780px — yatay dolgu 32→20, başlıklar
  42→31 / 36→27, sohbet satırının zamanı gizlenir; 640px — kenar çubuğu son basamağına iner. Hiçbir
  genişlikte yatay kaydırma yoktur. *(Fark 71'in "Home kartları tek sütuna iner" ayağı Madde 3'te
  konusuz kaldı — ızgara yok.)*
- **Nasıl görülür:** pencereyi kademeli daralt → her eşikte tarif edilen olur, düzen kırılmaz.

### Madde 34 — Durum ekranları ve erişilebilirlik *(fark 64, 65, 69)*

- **Ne çalışır:** ilk yüklemede içerik alanının tamamı tek iskelet düzenine döner (çubuk + blok,
  1.4s kademeli; kart ızgarası Madde 3'te silindi), kenar çubuğu normal çalışır. Çevrimdışı şeridi kızılımsı olur
  (`#F5E9E3` / `#E7D3C8` / `#8A5237`), solda 7px vurgu noktası, metin "You're offline — messages are
  saved and will send when you reconnect." Sohbet ve dosya satırları gerçek düğme olur (sekme +
  Enter), yıkıcı denetimler hover'da okunan `title` taşır.
- **Nasıl görülür:** yavaş açılışta tek iskelet; ağ kesilince yeni şerit; klavyeyle her satıra
  girilir.

### Madde 35 — Uçtan uca tur

Kod bittikten sonra tek dalgada elle koşulur:

| # | Ne yapılır | Beklenen |
|---|---|---|
| 1 | Sıfırdan aç | Boş hâl ekranı: "No projects yet" + New project |
| 2 | Proje kur, New chat'e bas | Projede boş sohbet açılır; başka bir ekrana uğranmaz |
| 3 | Mesaj at, cevabı izle | Saatli "QUEENAGENT · saat" etiketi, akan Markdown, uçta imleç |
| 4 | "Bunu dosyaya yaz" de | Noktaların altında kesikli kutu → kart; karta tıkla → panel açılır |
| 5 | "Merhaba" de | Dosya doğmaz |
| 6 | Rayı katla, sohbet değiştir, karta tıkla | Katlı kalır → kart rayı zorla açar |
| 7 | Model değiştir, ikinci sohbette başka model seç | Her sohbet kendi modelini hatırlar |
| 8 | "Create scenario" ile senaryo üret | Senaryo dosyası düşer |
| 9 | "Split into scenes" ile böl | Sahne listesi dosyası düşer |
| 10 | "Generate prompts" ile promptları al | Python listesi dosyası düşer |
| 11 | Dosya sil | Onay kutusu; Undo yok; dosya `trash/`te |
| 12 | Sohbet sil | Aynı kutu; dosyaları kalır |
| 13 | Projeyi iki kapıdan sil | Başlıktan ve ⋯ menüsünden aynı kutu; içindeyken silince ilk projeye düşülür |
| 14 | Anahtarı boz, mesaj at | Sunucunun gerçek cümlesi ekranda; Try again çalışır |
| 15 | Ağı kes | Kızılımsı şerit; composer açık |
| 16 | Pencereyi 1000/780/640 altına daralt | Eşikler tarif edildiği gibi; composer hep altta |
| 17 | Sunucuyu kapat-aç | Projeler, sohbetler, model seçimleri, dosyalar yerinde |
| 18 | Olmayan adrese git | "That project does not exist." |

---

## Sıra özeti

| Faz | Maddeler | Görülür çıktı | Neden burada |
|---|---|---|---|
| 0 · Ad | 1 | Her yerde QueenAgent | her şey yeni adın üstüne biner |
| 1 · Söküm | 2-7 | Küçülmüş yüzey | kimse kimseyi beklemez; sonraki her iş küçülür |
| 2 · Zemin | 8-12 | Doğru renk, ölçü, hareket, kaydırma | her yeni bileşen bu zemine doğar |
| 3 · Metin | 13-16 | Markdown, akış, dürüst hata | seçiciler ve okuyucu bu çizime yaslanır |
| 4 · Yıkıcı eylemler | 17-19 | Tek onay dili, proje silme | ray ve satırlar silme dilinin son hâline göre yazılır |
| 5 · Ray ve dosya | 20-24 | Katlanan ray, kapı olan kart, okuyucu | zemin + metin + silme dili hazır |
| 6 · Seçiciler | 25-27 | Model ve Skills | composer son hâlinde, menü deseni tek |
| 7 · Beceriler | 28-31 | Üç beceri iş görür | seçici arayüzü ve sohbete yapışma hazır |
| 8 · Uçlar | 32-35 | Sapmalar, duyarlılık, durumlar, tur | en çok şeye bağımlı işler en sonda |

## Kapsam dışı

Dosya sürümleme · dosya listesini sıralama/filtreleme · dosya yükleme · paylaşım, kimlik, çok
kullanıcı · tasarım projesinin güncellenmesi (kullanıcı yapacak, karar 19) · zaman damgası kuralı
(bugünkü davranış kalıyor, karar 13) · "bulunamadı" ekranları (kalıyor, karar 8) · dosya adlandırma
kuralı (kalıyor, karar 12).

## Açık sorular

Her biri ilgili maddenin spec'inde kapanır; yol haritası hiçbirini beklemez: eski kökteki verinin
taşınması (M1) · açılış ekranı ve Home'a dönüş (M3) · projenin çöp düzeni (M18) · üç becerinin
yönerge metinleri ve çıktı biçimleri (M28-30).
