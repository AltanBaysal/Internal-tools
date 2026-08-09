# Mira — Yol Haritası v1

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2` · **Durum:** Faz 0 başlamayı bekliyor
**Kaynak:** [Mira tasarım dokümanı v1](../specs/2026-08-09-mira-v1-design.md) — ürün kararları,
katmanlar, disk düzeni ve cevap akışı orada. Bu belge yalnız **hangi işin hangi sırayla** yapılacağını
söyler.
**Tasarım:** claude.ai/design → *Mira AI tasarımı istemi*. Davranış sözleşmesi
`Mira Handoff.dc.html`, ekranların somut hâli `Mira.dc.html`. Çelişkide handoff kazanır.

**15 faz, 32 madde.** Her madde çıktı odaklıdır (**ne çalışır** + **nasıl görülür**) ve bir öncekinin
üstüne birikir.

---

## Nasıl çalışacağız

Birim **fazdır**, madde değil. Her faz dört adımdan geçer, faz bitmeden sonrakine geçilmez:

1. **Spec** — fazın tasarım dokümanı (`docs/superpowers/specs/`). Fazın maddelerine düşen açık sorular
   burada karara bağlanır.
2. **Plan** — fazın uygulama planı (`docs/superpowers/plans/`), madde madde TDD adımlarıyla.
3. **TDD** — önce başarısız test, sonra kod; maddeler fazın içinde sırayla.
4. **Kapanış** — `pytest` ve `npm test` yeşil.

**Deneme en sonda, toplu.** Maddeler tek tek elle denenmez; hepsi Madde 32'de bir dalgada denenir.
Bunun bir sonucu var: bir maddenin *nasıl görülür* satırı o maddenin **kabul kriteridir**, sonra
yapılacak bir tur değil — testler o satırı kanıtlamalıdır. Commit'ler koşunun sonunda topluca atılır.

## Kod kuralları

Kurallar burada tekrar yazılmaz; yerleri `mira/FOUNDATION.md` ve `mira/CODE-STANDARD.md`'dir (ikisi de
Faz 0'da yazılır). Bu koşuda en çok işe karışacak olanlar:

- **Bağımlılık yönü:** `presentation → domain ← data → services`. Yasaklar istisnasız:
  `feature ↛ feature`, `service ↛ feature`, `service ↛ service`. Somut sınıflar yalnız kompozisyon
  kökünde bağlanır. Tek feature vardır: `workspace`. İki servis vardır: `store/` ve `xai/`.
- **Kural arka uçta, ön yüz görüntüdür.** Tarayıcı durumu çizer ve girdi toplar; testin doğrulayacağı
  hiçbir kararı sahiplenmez.
- **Gerçek diskte durur.** Hiçbir dosya başkasının cevabını tekrarlamaz: dosya listesi dizinin
  kendisidir, göreli zamanlar mtime'dan gelir, sayılar dizin sayımıdır.
- **Kullanıcının emeği kutsaldır.** Kullanıcı mesajı Grok'a gitmeden **önce** diske yazılır; silinen
  dosya `trash/`'e taşınır, yok edilmez.
- **Tasarım görsel şartnamedir, kaynak kod değildir.** `vendor/` klasörü yoktur; React'i biz yazarız,
  tasarımın rengine, ölçüsüne ve davranışına sadık kalarak.
- **Dil:** arayüz metni, kod, yorum, test adı ve commit mesajı **İngilizce**; bu belgeler **Türkçe**.

---

## Faz 0 — İskelet

### Madde 1 — Uygulama ayağa kalkar

- **Ne çalışır:** `mira/` klasörü kurulur; Flask app factory + `/health`, Vite ile React uygulaması,
  derlenmiş dosyaların sunucudan servisi, tek komutla açılış. CSS temeli oturur: tasarımın beş rengi,
  üç yazı tipi, odak halkası (`2px #B5623C`, 2px boşluk), kaydırma çubuğu. `mira/FOUNDATION.md` ve
  `mira/CODE-STANDARD.md` yazılır, `CLAUDE.md`'ye Mira bölümü eklenir.
- **Nasıl görülür:** uygulama açılır, tarayıcıda tasarımın zemin renginde boş bir sayfa gelir;
  `pytest` ve `npm test` birer sağlık testiyle yeşil.
- **Yok:** hiçbir ekran, hiçbir veri.

---

## Faz 1 — Disk

### Madde 2 — Store servisi

- **Ne çalışır:** `store/` servisi: `MIRA_ROOT` altında oku, yaz, listele, taşı, sil. Proje/sohbet/dosya
  kavramlarının hiçbirini bilmez. Kök dışına çıkan yol reddedilir; kök yoksa oluşturulur.
- **Nasıl görülür:** `pytest` yeşil ve üç cümle kanıtlanmış — `../` içeren yol reddediliyor; taşınan
  dosyanın mtime'ı korunuyor; olmayan dizin listelendiğinde boş dönüyor, patlamıyor.

### Madde 3 — Proje oluşur ve listelenir

- **Ne çalışır:** `workspace` feature'ının ilk hâli: proje oluştur ve listele. `project.json` (`name`,
  `desc`, `hue`, `createdAt`), id üretimi, `hue` ataması, dizin düzeninin kurulması. Liste her zaman
  diskten okunur.
- **Nasıl görülür:** `pytest` yeşil — sunucu yeniden başlatıldıktan sonra da liste aynı projeleri
  döndürüyor; iki proje aynı id'yi almıyor.
- **Yok:** yeniden adlandırma (Madde 7); silme (tasarımda yok, hiç yapılmıyor).

---

## Faz 2 — Kabuk

### Madde 4 — Sidebar iskeleti

- **Ne çalışır:** 280px sabit sidebar: logo, **Search** butonu (henüz bir şey açmaz), **New chat**,
  **Projects** başlığı ve `+`, **Recent chats** başlığı. Projects en fazla %40 yükseklik kaplar ve
  kendi içinde kayar; Recent chats kalanı doldurur ve kayar. Profil satırı yok.
- **Nasıl görülür:** tasarımın sidebar'ı ekranda; iki bölüm de boşken başlıkları duruyor, düzen
  bozulmuyor.

### Madde 5 — Home: selamlama ve proje kartları

- **Ne çalışır:** Home ekranı: **"Hi"** başlığı, composer kutusu (henüz göndermez), üç öneri
  baloncuğu, **Projects** başlığı + **New project**, iki sütunlu proje kartları (renk noktası, ad,
  açıklama, "N chats · M files"). New project gerçek proje kurar; sidebar ve kartlar aynı anda
  tazelenir. Sidebar'daki **New chat** Home'a döner — sohbet, mesaj atılınca doğar, butona basınca
  değil.
- **Nasıl görülür:** proje kur → hem sidebar'da hem kartlarda belirir; sayfayı yenile → durur;
  New chat'e bas → Home'a dönülür, boş bir sohbet kaydı oluşmaz.
- **Yok:** composer'ın gönderme davranışı (Madde 8).

---

## Faz 3 — Proje ekranı

### Madde 6 — Proje ekranı

- **Ne çalışır:** `← back`, başlık, açıklama, composer (henüz göndermez) ve iki sütunlu ızgara: solda
  **Chats**, sağda **Files Mira created** (320px). İki sütun da boş; boş dosya listesi
  *"No files yet — start a chat and Mira will create one."* der.
- **Nasıl görülür:** proje kartına tıkla → ekran açılır; boş proje öğretici metni gösterir, boş bir
  panel değil.

### Madde 7 — Proje yeniden adlandırma

- **Ne çalışır:** **Rename** butonu adı değiştirir; boş girdi iptal eder. Yeni ad diske yazılır.
- **Nasıl görülür:** adı değiştir → başlık, sidebar satırı ve Home kartı aynı anda yeni adı yazar;
  yenile → durur.
- **Spec'te karara bağlanacak:** proje **açıklaması** düzenlenebilir mi. Prototip her yeni projeye
  *"Click to add a description."* yazıyor ama düzenlemenin hiçbir yolu yok — tasarımın kendi boşluğu.
  Aynı soru Madde 11'in ürettiği otomatik projeyi de bağlar.

---

## Faz 4 — Composer ve sohbet kaydı

### Madde 8 — Composer davranışı

- **Ne çalışır:** Home ve proje ekranındaki metin kutusunun bütün kuralları: **Enter** gönderir,
  **Shift+Enter** satır atlar, taslak boşken buton pasif ve gri (`#E5DFD5`, `cursor:not-allowed`).
  Öneri baloncukları taslağı **doldurur, göndermez**. Mono etiket hedef projeyi yazar.
- **Nasıl görülür:** kutu boşken butona basılamaz; öneriye tıkla → kutu dolar, hiçbir yere gidilmez;
  Shift+Enter satır atlar, Enter atmaz.

### Madde 9 — Sohbet oluşur

- **Ne çalışır:** ilk mesaj sohbeti doğurur; başlık mesajın ilk 42 karakteri (uzunsa `…`).
  `chats/<chat-id>.json` yazılır, kullanıcı mesajı `role`/`at`/`text` ile diske eklenir.
- **Nasıl görülür:** `pytest` yeşil — 42 karakterden uzun mesaj başlığı kesiyor ve `…` koyuyor; sunucu
  yeniden başladıktan sonra sohbet ve mesajı yerinde.
- **Yok:** cevap (Faz 6).

---

## Faz 5 — Sohbet ekranı

### Madde 10 — Sohbet ekranı

- **Ne çalışır:** breadcrumb (`← proje adı / sohbet başlığı`), mesaj sütunu, sağa yaslı kullanıcı
  balonu (`#EDE6DC`, köşe `14px 14px 4px 14px`) ve üstünde `KULLANICI · saat` mono etiketi, altta
  composer. Mesaj gönderilince ekran sohbete geçer ve balon **anında** görünür.
- **Nasıl görülür:** Home'dan mesaj at → sohbet ekranına düş, balon dursun; sayfayı yenile → mesaj
  yerinde.
- **Yok:** dosya rayı (Madde 21); üç nokta ve cevap (Faz 6).

### Madde 11 — Otomatik proje ve sohbet

- **Ne çalışır:** hiç proje yokken Home'dan gönderilen ilk mesaj **projeyi ve sohbeti birlikte** açar;
  proje adı mesajdan türetilir. Prototipin "ilk projeye gönder" davranışı yok — proje yokken çökmez.
- **Nasıl görülür:** sıfır projeyle başla, tek mesaj at → proje ve sohbet birden doğar, sidebar ikisini
  de gösterir.

### Madde 12 — Sohbet listeleri

- **Ne çalışır:** sidebar'daki **Recent chats** bütün projelerin bütün sohbetlerini gösterir; proje
  ekranındaki **Chats** sütunu o projeninkileri ad + göreli zamanla listeler. Açık sohbet iki listede
  de işaretlidir (`#E5DFD5`). Tıklama sohbeti açar.
- **Nasıl görülür:** iki listeden de aynı sohbete giriliyor; sohbete girince satırı işaretleniyor.

---

## Faz 6 — Grok

### Madde 13 — Grok bağlantısı

- **Ne çalışır:** `xai/` servisi: anahtar ortam değişkeninden okunur, model adı ayardan gelir, akışsız
  bir istek atılır ve cevap metni döner. Hata durumunda **servisin gerçek çıktısı** (HTTP kodu +
  gövde) yukarı taşınır, uydurulmuş tek bir sebep değil. Anahtar yoksa uygulama açılır ama sohbet açık
  bir hata verir, sessizce çökmez.
- **Nasıl görülür:** `pytest` yeşil (sahte HTTP) — 401 dönen istek, gövdesiyle birlikte yukarı
  taşınıyor; anahtar yokken atılan hata anlaşılır.
- **Not:** uç nokta adresi, model id'si ve alan adları bu maddenin planında **xAI dokümanından
  doğrulanır**, ezberden yazılmaz.

### Madde 14 — Cevap gelir

- **Ne çalışır:** mesaj → Grok → cevap. Kullanıcı mesajı **Grok'a gitmeden önce** diske yazılır; cevap
  tamamlanınca `role:"ai"` mesajı olarak eklenir. Ekranda `MIRA · saat` etiketi ve cevap gelene kadar
  üç yanıp sönen nokta.
- **Nasıl görülür:** soru sor → üç nokta → cevap gelir; sayfayı yenile → soru da cevap da yerinde.
- **Yok:** akış (Madde 15); araçlar ve dosya (Faz 8).

---

## Faz 7 — Akış

### Madde 15 — Cevap akar

- **Ne çalışır:** cevap SSE ile parça parça gelir; **ilk parçada üç nokta söner** ve metin yazılmaya
  başlar. Yarım metin diske yazılmaz — kayıt yalnız cevap tamamlanınca düşer.
- **Nasıl görülür:** cevap harf harf birikiyor; akış sürerken sayfa yenilenirse yarım cevap
  kaydedilmemiş oluyor.

### Madde 16 — Hata hâli

- **Ne çalışır:** akış ölürse kullanıcı mesajı yerinde kalır ve sıcak tonlu hata kartı çıkar
  (`#FBF1EC` zemin, `#E7D3C8` çerçeve) + **Try again**. Try again son kullanıcı mesajını yeniden
  gönderir.
- **Nasıl görülür:** bağlantıyı kes → kart çıkar, mesaj durur; **Try again** → cevap gelir, mesaj
  ikinci kez yazılmaz.

---

## Faz 8 — Ajan döngüsü

### Madde 17 — Döngü ve `list_files`

- **Ne çalışır:** ajan döngüsü: model araç çağırır → **sunucu** çalıştırır → sonuç modele geri verilir
  → model devam eder. İlk araç `list_files`: projedeki dosyaların adlarını döndürür. Sabit bir **tur
  sınırı** vardır; sınıra gelince döngü kesilir ve model elindekiyle cevap verir.
- **Nasıl görülür:** "bu projede neler var" diye sor → cevap gerçek dosya adlarını sayar; ekranda ek
  bir gösterge çıkmaz, üç nokta yanıp söner.
- **Spec'te karara bağlanacak:** tur sınırının sayısı; ara turlarda ekranda bir gösterge olup olmayacağı
  (tasarımda karşılığı yok).

### Madde 18 — `read_file`

- **Ne çalışır:** model bir dosyanın içeriğini isteyebilir. Yol kararı sunucunundur: yalnız o projenin
  `files/` dizini okunur, `trash/` ve kök dışı erişilemez.
- **Nasıl görülür:** var olan bir dosyanın içeriğine dayanan bir soru sor → cevap içeriği bilerek
  geliyor; olmayan dosya istendiğinde döngü patlamıyor, model bilgilendiriliyor.

### Madde 19 — `create_file`

- **Ne çalışır:** model dosya yazar; sunucu `files/` altına kaydeder. Ad çakışırsa **üstüne yazılmaz**,
  sonuna sayı eklenir. Model bu aracı hiç çağırmayabilir — o zaman dosya doğmaz.
- **Nasıl görülür:** "bunu bir dosyaya yaz" de → dosya diskte; aynı adı ikinci kez üret → ikisi de
  duruyor; "merhaba" de → hiç dosya doğmuyor.
- **Spec'te karara bağlanacak:** Grok'un sistem yönergesi ve dosya adı üretme kuralı; formatın `.md`
  dışına çıkıp çıkmayacağı.

---

## Faz 9 — Dosya görünür

### Madde 20 — Kesikli kart, dolu kart, dosya listesi

- **Ne çalışır:** `create_file` çağrıldığı anda üç noktanın altında kesikli **"creating file…"** kartı
  belirir; dosya yazılınca yerini dolu dosya kartına bırakır (uzantı çipi + ad + `✓ saved to project`).
  Proje ekranındaki **Files** sütunu dosyayı en üstte gösterir. Karta tıklamak dosyayı açar.
- **Nasıl görülür:** dosya isteyen bir mesaj at → kesikli kart → dolu kart; proje ekranına dön → dosya
  listede en üstte, `2h ago` benzeri göreli zamanıyla.
- **Spec'te karara bağlanacak:** dosyası silinmiş bir mesajın kartı ne gösterir.

### Madde 21 — Sohbetteki ray

- **Ne çalışır:** sohbet ekranının sağında kalıcı 320px ray: **Project files** başlığı ve proje
  dosyalarının listesi, kullanıcı yazarken neyin var olduğunu görsün diye hep açık. Boşken
  *"No files yet — send a message and Mira will create one."*
- **Nasıl görülür:** sohbette sağda liste duruyor; yeni dosya üretilince listeye ve rayın en üstüne
  aynı anda düşüyor.

---

## Faz 10 — Okuma

### Madde 22 — Okuma paneli (sohbet)

- **Ne çalışır:** raydaki bir dosyaya tıklamak rayı **320 → 560px** genişletir (220ms geçiş) ve
  içeriği gösterir: üstte `←` + dosya adı, ortada düz metin, altta tek satır mono meta. `←` listeye
  döner, **Esc** paneli kapatır. Sohbet sütunu daralır — hiçbir şeyin üstü örtülmez.
- **Nasıl görülür:** dosyayı aç → sohbet okunmaya devam ediyor, sadece daralıyor; Esc kapatıyor.
- **Yok:** tam ekran okuyucu (tasarım yasaklıyor); dosya üzerinde `←` ve Download dışında eylem.

### Madde 23 — Okuma paneli (proje ekranı)

- **Ne çalışır:** proje ekranında dosyaya tıklamak sağdan 560px'lik panel açar ve ızgara **tek sütuna**
  iner. Panelin içeriği sohbettekiyle aynıdır.
- **Nasıl görülür:** proje ekranında dosyaya tıkla → panel açılır, sohbet listesi tam genişliğe geçer;
  `←` kapatınca ızgara geri gelir.

### Madde 24 — Download

- **Ne çalışır:** **Download** butonu dosyayı indirir; indirme sürerken içine spinner girer ve etiket
  **"preparing…"** olur. Buton yerinden oynamaz.
- **Nasıl görülür:** indir → dosya diske iner, içeriği panelde görünenle aynı; buton düzeni kaymaz.

---

## Faz 11 — Silme

### Madde 25 — Dosya silme ve Undo

- **Ne çalışır:** dosya satırındaki `×` dosyayı **anında** kaldırır ve listenin üstünde
  **"File deleted. / Undo"** şeridi çıkar — modal yok. Silme fiziksel değildir: dosya `trash/`'e taşınır.
  **Undo** onu geri taşır; mtime korunduğu için dosya **eski sırasına** döner.
- **Nasıl görülür:** ortadaki bir dosyayı sil → şerit çıkar → Undo → dosya **aynı sırada** geri gelir,
  en üste zıplamaz.
- **Spec'te karara bağlanacak:** şeridin ömrü (basılana kadar mı, süreli mi).

### Madde 26 — Sohbet silme

- **Ne çalışır:** sohbet satırındaki `×` **onay ister**; onaylanınca sohbet ve mesajları gider.
  Sohbetin ürettiği dosyalar **kalır** — dosya projeye aittir. Yıkıcı eylem dili uygulama genelinde
  aynıdır: dolu kırmızı buton hiçbir yerde yoktur.
- **Nasıl görülür:** dosya üretmiş bir sohbeti sil → onay sorar; sohbet gider, dosyaları listede durur.

---

## Faz 12 — Yeniden adlandırma

### Madde 27 — Sohbet ve dosya adı

- **Ne çalışır:** sohbet satırındaki **name** butonu başlığı değiştirir; boş girdi iptal eder. Dosya da
  yeniden adlandırılabilir (handoff'un açık maddesi, v1'e alındı) — yeni ad diskteki dosyanın adıdır,
  çakışma kuralı Madde 19'unkiyle aynıdır.
- **Nasıl görülür:** sohbeti yeniden adlandır → iki listede de yeni ad; dosyayı yeniden adlandır →
  listede, rayda ve açık panelde yeni ad.
- **Spec'te karara bağlanacak:** yeniden adlandırılan dosyaya bakan mesaj kartı ne yapar.

---

## Faz 13 — Arama

### Madde 28 — ⌘K

- **Ne çalışır:** **⌘K / Ctrl+K** arama panelini açar-kapar; girdi otomatik odaklanır. Sonuçlar proje
  adlarını, sohbet başlıklarını, dosya adlarını **ve dosya içeriklerini** kapsar, en fazla **8** tane.
  Her satır türünü mono bir çip olarak yazar. **Esc** önce aramayı kapatır, sonra açık dosya panelini;
  asla geri gitmez. Sonuç yoksa *"No results."*
- **Nasıl görülür:** bir dosyanın **içindeki** kelimeyi ara → dosya sonuçlarda çıkar; tıkla → proje
  ekranı açılır ve dosya panelde görünür. Panel açıkken Esc'e iki kez bas → önce arama, sonra panel
  kapanır.

---

## Faz 14 — Durumlar ve doğrulama

### Madde 29 — Yükleniyor

- **Ne çalışır:** içerik alanı yüklenirken iskelet bloklar çizilir; **sidebar normal çalışır**, gezinme
  hiçbir an engellenmez.
- **Nasıl görülür:** yavaş yanıtta içerik alanında iskelet bloklar var, sidebar'dan başka bir projeye
  geçilebiliyor.

### Madde 30 — Çevrimdışı

- **Ne çalışır:** içerik alanının üstünde bir şerit: mesajlar saklanır ve bağlantı dönünce gönderilir.
  Composer **açık kalır**.
- **Nasıl görülür:** ağı kes → şerit çıkar, yazmaya devam edilebilir; ağ dönünce şerit kaybolur.

### Madde 31 — 1100px altı

- **Ne çalışır:** dar ekranda ray bir overlay'e döner, sidebar katlanır. Düzen kırılmaz, yatay kaydırma
  oluşmaz.
- **Nasıl görülür:** pencereyi 1100px'in altına daralt → sohbet okunabilir kalır, ray üstten açılır.

### Madde 32 — Uçtan uca tur

Kod tarafı bittikten sonra tek dalgada elle koşulur.

| # | Ne yapılır | Beklenen |
|---|---|---|
| 1 | Sıfırdan aç, Home'dan mesaj at | Proje **ve** sohbet birlikte doğar, balon anında görünür |
| 2 | Cevabı bekle | Üç nokta → metin akar → cevap tamamlanır |
| 3 | "Bunu bir dosyaya yaz" de | Kesikli "creating file…" → dolu kart "✓ saved to project" |
| 4 | "Merhaba" de | Dosya doğmaz, cevap tek başına kalır |
| 5 | "Az önceki dosyada ne yazıyor" diye sor | Cevap içeriğe dayanır (model dosyayı okudu), ekranda ek gösterge çıkmaz |
| 6 | Raydaki dosyaya tıkla | Ray 320 → 560px, sohbet daralır, hiçbir şeyin üstü örtülmez |
| 7 | Download | Dosya iner; buton "preparing…" olur ve yerinden oynamaz |
| 8 | Proje ekranında ortadaki dosyayı sil, sonra Undo | Dosya **aynı sırada** geri gelir |
| 9 | Dosya üretmiş bir sohbeti sil | Onay sorar; sohbet gider, **dosyaları kalır** |
| 10 | Dosyayı yeniden adlandır | Liste, ray ve açık panel yeni adı yazar |
| 11 | ⌘K → dosya içindeki bir kelimeyi ara | Dosya sonuçlarda; tıkla → panelde açılır |
| 12 | Panel açıkken Esc'e iki kez bas | Önce arama, sonra panel kapanır; geri gidilmez |
| 13 | Anahtarı boz, mesaj at | Kullanıcı mesajı durur, hata kartı + **Try again** |
| 14 | Anahtarı düzelt, Try again | Cevap gelir, mesaj ikinci kez yazılmaz |
| 15 | Ağı kes | Çevrimdışı şeridi çıkar, composer kapanmaz |
| 16 | Pencereyi 1100px altına daralt | Ray overlay olur, düzen kırılmaz |
| 17 | Sunucuyu kapat-aç | Projeler, sohbetler, mesajlar ve dosyalar yerinde |

---

## Sıra özeti

| Faz | Maddeler | Görülür çıktı | Yeni kazanım |
|---|---|---|---|
| 0 · İskelet | 1 | Tasarımın zemininde boş sayfa | bir şey ayakta |
| 1 · Disk | 2-3 | Yeniden başlatmaya dayanan proje listesi | gerçek diskte durur |
| 2 · Kabuk | 4-5 | Sidebar + Home + proje kurma | uygulama gezilebilir |
| 3 · Proje ekranı | 6-7 | Proje ekranı ve yeniden adlandırma | projenin kendi yeri |
| 4 · Composer ve sohbet kaydı | 8-9 | Kuralına uyan composer, diske düşen sohbet | mesaj kalıcı olur |
| 5 · Sohbet ekranı | 10-12 | Sohbet ekranı ve iki liste | sohbet gezilebilir |
| 6 · Grok | 13-14 | İlk gerçek cevap | uygulama cevap verir |
| 7 · Akış | 15-16 | Akan metin, hata kartı | bekleme görünür olur |
| 8 · Ajan döngüsü | 17-19 | Model bakar, okur, yazar | Mira gerçekten çalışır |
| 9 · Dosya görünür | 20-21 | Kesikli kart, dosya listesi, ray | dosya ürünün parçası olur |
| 10 · Okuma | 22-24 | Panel ve indirme | dosya okunur hâle gelir |
| 11 · Silme | 25-26 | Undo şeridi, onaylı sohbet silme | yıkıcı eylem güvenli olur |
| 12 · Yeniden adlandırma | 27 | Sohbet ve dosya adı | isimler kullanıcının olur |
| 13 · Arama | 28 | ⌘K, içerikte arama | her şey bulunur |
| 14 · Durumlar ve doğrulama | 29-32 | Skeleton, çevrimdışı, dar ekran, tur | uçlar kapanır |

## Neden bu sıra

- **Disk önce (1):** her ekran diskteki gerçeği çiziyor. Depolama oturmadan çizilen ekran, kaynağı
  değişince ikinci kez elden geçer.
- **Kabuk sohbetten önce (2, 3):** sohbetin yaşayacağı yer proje; proje ekranı olmadan sohbetin
  breadcrumb'ı bir yere işaret edemez.
- **Composer sohbetten ayrı (8, 9):** composer'ın kuralları (Enter, boş taslak, öneriler) motordan ve
  kayıttan bağımsız test edilebilir; birleştirmek maddeyi şişirir.
- **Motor → akış → araçlar (6, 7, 8):** üçü de aynı uç noktaya dokunuyor ama her biri bir öncekini
  görünür kılıyor. Akışı araçlardan önce yapmak, ajan turlarının ekranda nasıl göründüğünü tartışmayı
  mümkün kılar.
- **Ray dosyadan sonra (21):** gösterecek dosya olmadan ray boş bir vaattir; boş hâli de ancak dolu
  hâli varken doğrulanır.
- **Silme, arama, yeniden adlandırma listeden sonra (25-28):** üçü de dosya listesinin var olduğunu
  varsayıyor.
- **1100px altı en sonda (31):** düzen yerine oturmadan kırmak aynı işi iki kez yaptırır.
- **Tur en sonda (32):** kullanıcının zamanı sınırlı; tek dalgada denenir.

## Kapsam dışı

Dosya sürümleme (v1/v2 + diff) · dosya listesini sıralama ve filtreleme · dosya yükleme (tasarımın
kararı: kullanıcı okur, yüklemez) · paylaşım · kimlik ve çok kullanıcı · **proje silme** (tasarımda
hiç yok).

## Açık sorular

Hepsi ilgili fazın spec'inde kapanır; listesi tasarım dokümanının 11. bölümündedir. Roadmap hiçbirini
beklemez.
