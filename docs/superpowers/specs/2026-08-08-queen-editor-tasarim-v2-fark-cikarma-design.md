# Queen Editor — Tasarım v2 fark çıkarma · Tasarım

**Tarih:** 2026-08-08 · **Branch:** `feat/queen-editor-v2` · **Durum:** açık
**Bağlam:** [v3 yol haritası](../plans/2026-08-08-queen-editor-v3-roadmap.md) Madde 1 —
tasarım tamamlandı, sıra tasarımın söylediklerini uygulamanın bugünkü hâliyle karşılaştırmaya geldi.

---

## Amaç

claude.ai/design'daki **Queen Editor** projesinin **"Basit v2"** sürümü ile **bugün çalışan
uygulama** arasındaki UI/UX davranış farklarını çıkarmak. Tek çıktı bir Türkçe md.

Bu belge farkın *kendisini* değil, farkı **nasıl çıkaracağımızı** tarif eder.

## Kapsam sınırı — çıktı belgesine ne girmez

Çıktı belgesinde **kod diline ait hiçbir şey geçmez**: dosya adı, uç nokta, bileşen adı, veri
dosyası, katman adı — hiçbiri. Yalnızca kullanıcının gördüğü davranış yazılır.

Kaynağı okumak serbesttir; **yazmak yasaktır.** Bugünkü uygulamanın davranışı kaynağı okuyarak
öğrenilir — ama öğrenilen şey belgeye davranış cümlesi olarak girer, kodun izi kalmaz.

**Görsel dil de kapsamdadır.** Renk, boşluk, tipografi, ikon, ölçü — hepsi karşılaştırılır. Ama
görsel bulgular gövdeye karışmaz, **kendi bölümünde** toplanır: v2'nin çekirdeği bir akış
değişikliğidir ve ince ayarlar aralarına serpilirse asıl değişiklikler görünmez olur. Görsel bulgu
da davranış bulgusu gibi iki satırdır: *bugün ne görünüyor* → *tasarım v2'de ne görünecek*.

**Belge karar vermez.** Çelişkileri açıkça işaretler, hangisinin kazanacağını söylemez.

## İsim çakışması — belgenin başına not düşülür

Tasarım projesinin **"v2"**si, repodaki **v3 yol haritasına** karşılık gelir; tasarımın `HANDOFF.md`
belgesi bunu kendi de yazmış. Belge boyunca ikisi ayrı ayrı anılır: **tasarım v2** ve **roadmap v3**.
Kısaltılmaz, "v2" tek başına kullanılmaz.

## Kaynaklar

**Tasarım tarafı** — claude.ai/design projesi `efad1f83-69d3-4e07-89fa-3783839c81c3` ("Queen
Editor"), DesignSync ile **salt okunur** erişilir. Projeye yazma yapılmaz: `finalize_plan`,
`write_files`, `delete_files` çağrılmaz.

**Tasarım dosyaları hiçbir yere kaydedilmez** — ne repoya, ne geçici bir klasöre. Her yol
ihtiyacı olan içeriği ya doğrudan DesignSync'ten okur ya da görev metninin içinde hazır bulur;
diske hiçbir şey düşmez.

| Dosya | Ne taşır |
|---|---|
| `HANDOFF.md` | v1 davranış anlatısı + **"v2'de değişenler — sürekli kuyruk"** bölümü |
| `CLAUDE.md` | yıkıcı eylem butonu standardı |
| `Queen Editor Basit v2.html` | v2 giriş noktası — aşağıdaki JSX'leri zincirler |
| `simple-app-v2.jsx`, `simple-screens-v2.jsx` | v2 ekranları ve durumları |
| `wireframe-kit.jsx`, `tweaks-panel.jsx`, `design-canvas.jsx`, `styles.css` | ortak altyapı |
| `Queen Editor Basit v1.html`, `simple-app.jsx`, `simple-screens.jsx` | v1 karşılıkları |

**Uygulama tarafı** — repodaki `queen-editor/` (frontend ve backend). Bugünkü davranışın tek
kaynağı burasıdır.

---

## Üç yol

Üç yol, üç ayrı kaynağa demirler. Her biri **tek başına tam fark listesi** çıkarabilecek
yetkinliktedir — biri diğerinin parçası değil, sağlamasıdır. Üçü ayrı alt-ajanda, **aynı anda**
koşar ve **hiçbiri diğerinin çıktısını görmez.**

| | Yol 1 · **Anlatı** | Yol 2 · **Tasarım kaynağı** | Yol 3 · **Ters yön** |
|---|---|---|---|
| Demirlediği kaynak | tasarımın *yazısı* | v2 wireframe'inin *kendisi* | bugünkü uygulamanın *kendisi* |
| Yön | tasarım → uygulama | tasarım → uygulama | uygulama → tasarım |
| Özel yakaladığı | kararların **gerekçesi**, ekranı çizilmemiş kurallar | yazıya geçmemiş her şey — etiketler, ara durumlar, boş hâller | **öksüz davranışlar**, zaten yanlış uygulanmış olanlar |
| Kör noktası | tasarımcının yazmadığı | "neden"i bilmez | bugün hiç tutamağı olmayan yepyeni şey |

Dördüncü bir yol için dördüncü bir kaynak gerekirdi; yok.

**Körlük nasıl sağlanır.** Yol 2'nin anlatıyı okumaması bu düzenin tek kırılgan noktası, o yüzden
dileğe bırakılmaz — her yola erişim biçimiyle sınır konur:

| Yol | Tasarım tarafına nasıl erişir |
|---|---|
| Yol 1 | **DesignSync'i hiç çağırmaz.** İhtiyacı olan iki yazılı belge görev metninin içinde hazır verilir; wireframe kaynağına erişimi olmadığı için okuması da mümkün değildir |
| Yol 2 | DesignSync'i **kendisi çağırır**, yalnız v2 wireframe zinciri için. `HANDOFF.md` ve tasarım `CLAUDE.md`'sini çekmesi yasaktır — ihlal olursa çağrı kaydında görünür ve o yolun çıktısı geçersiz sayılır |
| Yol 3 | DesignSync'i kendisi çağırır, tasarım tarafının tamamı serbesttir |

### Yol 1 · Anlatı

**Okur:** `HANDOFF.md` (tümü) ve tasarım projesinin `CLAUDE.md`'si; ayrıca bugünkü uygulamanın
kaynağı.
**Okumaz:** v2 wireframe'inin kaynağı. Okursa Yol 2'nin kopyası olur ve sağlama değerini yitirir.

**Yürüyüş:** yazılı her kararı tek tek alır → bugünkü uygulamada karşılığını arar → fark varsa
yazar. `HANDOFF.md`'nin şu iki bölümü de taranır, atlanmaz:

- **"Kural olarak yazılanlar (ekran çizilmedi)"** — ekranda görünmeyen ama bağlayıcı kararlar.
- **"Değişmeyenler"** — tasarım "bu değişmedi" diyor olabilir ama uygulama oradan sapmış olabilir;
  o zaman bu bir fark değil, bir **sapma**dır ve öyle etiketlenir.
- **"Görsel dil"** — renk rolleri, tipografi, etiket biçimi; görsel bulguların yazılı kaynağı.

### Yol 2 · Tasarım kaynağı

**Okur:** `Queen Editor Basit v2.html` ve zincirlediği bütün JSX/CSS; ayrıca bugünkü uygulamanın
kaynağı.
**Okumaz:** `HANDOFF.md`, tasarım projesinin `CLAUDE.md`'si. Bu kural kesindir — yolun tüm değeri
anlatıyı görmemiş olmasından gelir.

**Yürüyüş:** v2 wireframe'inden envanter çıkarır — hangi ekran, hangi bölge, hangi kontrol, hangi
durum, durumlar arası hangi geçiş, hangi metin. Aynı envanteri bugünkü uygulamadan çıkarır. İki
envanteri satır satır karşılaştırır.

### Yol 3 · Ters yön

**Okur:** omurgası bugünkü uygulamanın kaynağı; arama için tasarım tarafının **tamamı** (wireframe
ve yazı) serbesttir.

**Yürüyüş:** bugünkü uygulamanın davranış envanterini çıkarır, sonra her maddeyi tasarım v2'de arar
ve üç kovadan birine atar:

| Kova | Anlamı |
|---|---|
| **Karşılığı var, aynı** | değişmiyor |
| **Karşılığı var, farklı** | fark — değişecek |
| **Karşılığı yok** | **öksüz davranış**: ya v2'de bilerek kaldırıldı, ya tasarım atladı. Belge hangisi olduğuna karar vermez, işaretler |

**İkinci görev — tam sadakat denetimi.** Yol 3 aynı turda ikinci bir soru sorar: *"tasarım bunu
nasıl tarif etmişti, uygulama gerçekten öyle mi yapıyor?"* Bu soru **v2'nin dokunmadığı yerlerde de**
sorulur — envanterdeki her madde, tasarımın kendisini tarif eden bölümüne karşı denetlenir. Öyle
yapmıyorsa bu bir v2 farkı değil, bir **sapma**dır; ayrı bölüme girer, çünkü v2'ye geçerken
düzeltilecekler listesine o da dahildir.

Sadakat denetimi ile v2 farkı iki ayrı listedir ve **karıştırılmaz**. "Bugün yanlış" ile "v2'de
değişecek" farklı iki iddiadır; tek listede birleşirlerse hangisinin tasarımcı kararı hangisinin
uygulama hatası olduğu okunamaz hâle gelir.

**Kapanış taraması:** envanter bugünden başladığı için, v2'de tamamen yeni olup uygulamada hiç
tutamağı olmayan bir şey kaçabilir. Yolun sonunda tek bir tarama yapılır: *"tasarım v2'de dokunulmuş
olup envanterimde hiç görünmeyen bir yer kaldı mı?"*

---

## Her üç yol için ortak kurallar

1. **Bulgu geçiş olarak yazılır, duruş olarak değil.** "Duraklat butonu var" yetersizdir;
   "Duraklat'a basınca çalışan kare bitirilir, arada *Duraklatılıyor…* görünür, sonra bekleyen sayısı
   7'den 8'e çıkar" doğrudur. Kaynağı okurken bu bilgi zaten önümüzdedir; durağan cümleye indirgemek
   bilerek bilgi atmak olur.
2. **Her bulgu iki satırdır:** *bugün ne oluyor* → *tasarım v2'de ne olacak*.
   Her bulgu ayrıca **davranış** ya da **görsel** diye etiketlenir; çakıştırmada ikisi ayrı bölümlere
   dağıtılacak.
3. **Kod dili yok** — kapsam sınırındaki kural her yol için geçerlidir.
4. **Karar verilmez.** Çelişkiye rastlanırsa iki ifade de yazılır, hangisinin doğru olduğu
   söylenmez.
5. **"Tasarım söylemiyor" etiketi:** bir davranışın tasarım v2'de cevabı yoksa madde bu etiketi
   alır. Uydurulmaz, tahmin edilmez.
6. Belge ve tüm ara çıktılar **Türkçe**.

## Sağlama — çakıştırma

Çakıştırmayı alt-ajan değil, ben yaparım; üç listeyi de gören tek yer burasıdır.

**Normalizasyon.** Aynı farkın üç farklı cümlesi tek satıra indirilir. Birleştirme kararı elle
verilir — otomatik eşleme, farklı iki bulguyu tek satıra ezebilir.

**Güven derecesi.**

| Kaç yol | Damga | Ne yapılır |
|---|---|---|
| 3/3 | kesin | listeye girer |
| 2/3 | güçlü | listeye girer |
| 1/3 | zayıf sinyal | kaynağa dönülür, elle doğrulanır |

Zayıf sinyal doğrulanırsa listeye "elle doğrulandı" notuyla girer; doğrulanamazsa **atılmaz**,
"doğrulanamayanlar" bölümüne düşer. Bir yolun tek başına gördüğü şey çoğu zaman o yolun özel
yakaladığı sınıftandır — sessizce silmek yöntemin amacını bozar.

**Çelişki.** İki yol aynı konuda farklı şey söylüyorsa madde "çelişki" damgası alır ve **her iki
ifade de** yazılır. Tek yolla asla göremeyeceğimiz şey budur.

## Çıktı belgesinin iskeleti

| # | Bölüm | İçerik |
|---|---|---|
| 0 | Başlık notu | isim çakışması — tasarım v2 = roadmap v3 |
| 1 | Özet | tasarım v2 tek paragrafta ne getiriyor |
| 2 | Doğrulama tablosu | tüm farklar, her biri kaç yolla doğrulandı |
| 3 | **Davranış farkları — ekran ekran** | Projeler · Proje paneli (ikon şeridi, *Üretime ekle*, *Kuyruğu takip et*, *AI agent*) · Galeri · Foto detay · Uygulama geneli (numaralandırma ve sıra, export) |
| 4 | **Görsel dil farkları** | renk, boşluk, tipografi, ikon, ölçü; yıkıcı eylem butonu standardı gibi kural hâline gelmiş görsel kararlar da burada |
| 5 | Roadmap v3 ile çelişkiler | tablo — karar yok |
| 6 | Öksüz davranışlar | bugün var, tasarım v2'de karşılığı yok |
| 7 | **Tasarım sadakati denetimi** | v2'den bağımsız: bugünkü uygulamanın tasarımdan sapmaları, tüm ekranlar |
| 8 | Zayıf sinyaller ve doğrulanamayanlar | atılmayanlar |
| 9 | Tasarımın cevaplamadıkları | "AI agent" panelinin boş oluşu dahil |

3 ve 4. bölümlerdeki her madde ortak kuralların 1. ve 2. maddesine uyar: geçiş cümlesi, iki satır.
7. bölüm ayrı durur — orada "v2'de değişecek" değil, "bugün zaten yanlış" iddiası vardır.

**Yer:** `docs/superpowers/research/2026-08-08-queen-editor-tasarim-v2-farklari.md` — yeni bir
`research/` klasörü. Bu belge ne bir spec'tir (karar vermiyor) ne bir plan (iş listesi değil);
`specs/` altına koymak ikisini karıştırır.

## Kapsam dışı

- Kod değişikliği — bu tur tek satır kod yazmaz.
- Roadmap v3'ün güncellenmesi — çelişkiler tespit edilir, roadmap ayrı bir turda düzeltilir.
- Çelişkilerin karara bağlanması.
- Tasarım projesine yazma; tasarım dosyalarının herhangi bir yere kaydedilmesi — ne repoya, ne
  geçici bir klasöre.
- Ekran görüntülerinin (`screenshots/`) kaynak sayılması — başka bir tasarım yönüne aitler.

## Karara bağlananlar

- Çıktı belgesinde kod dili geçmez; taban bugün çalışan uygulamadır ve kaynağı okunarak çıkarılır.
- Üç yol, üç ayrı kaynağa demirler; üçü de tek başına tam liste çıkarır; üçü aynı anda ve birbirini
  görmeden koşar.
- Yol 2 anlatıyı okumaz — kuralın kesin olması yolun tek değer kaynağıdır.
- Belge karar vermez, çelişkiyi işaretler.
- Zayıf sinyal atılmaz, ayrı bölüme düşer.
- Tasarım v1 ↔ v2 deltası ayrı bir yol değil: kaldırılanları Yol 3 zaten "öksüz davranış" olarak
  yakalıyor.
- Yolculuk/senaryo ayrı bir yol değil: kaynak okunduğunda geçişler zaten görünür olduğu için ortak
  kural hâline getirildi.
- Görsel dil kapsam içi — renk ve boşluk dahil — ama gövdeye karışmaz, kendi bölümünde toplanır.
- Sadakat denetimi tüm uygulamayı kapsar, yalnız v2'nin dokunduğu yerleri değil; ayrı bölümde durur
  ve v2 farklarıyla karıştırılmaz.
- Tasarım dosyaları **hiçbir yere kaydedilmez** — repoya da, geçici klasöre de. Körlük dosya
  yerleşimiyle değil, **erişim biçimiyle** sağlanır: Yol 1 DesignSync'i hiç çağırmaz, Yol 2
  çağırır ama yazılı belgeleri çekmesi yasaktır ve ihlali çağrı kaydında görünür.

## Açık soru

Yok.
