# Madde 355 — Sohbet açılırken açılmış gibi görünür · test turu

**Kaynak:** [yol haritasının 355'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2l);
kararları v9-2'nin; tasarım: `queen-agent-v3`'ün 194'ü. 340'ın spinner'ının ve 347'nin başlığının
üstüne kurulur.

**Kullanıcıdan gereken:** hiçbir şey. Görünüş tasarımda yazılı, madde hizalandı.

## Ne kanıtlanacak

Bir sohbet açılırken, kaydı gelene kadar, bugün `ChatScreen`'in `if (!chat)` dalı çiziliyor: sol
üstte tek başına `← back`, altında parlayan iki blok (`Skeleton variant="message"`). Başlık, yazma
kutusu ve dosya paneli yok.

Tasarımın 194'ü (`DESIGN-STANDARD.md`, *Chat — Not yet read*; `chat/index.html`, `chatScreen()`;
`kit.css`):

- **Aynı `chat` ve dosya paneli durur.** Kaydı gelmiş bir sohbetin çerçevesi: başlık, mesajların
  kaydırılan sütunu, yazma kutusu, yanda dosya paneli.
- **Başlık kenar çubuğundaki satırın adı** (`loadingTitle`: sohbet listesi zaten okunmuş, satır aynı
  adı taşıyor); satır da gelmemişse boş.
- **`chat__column`'da yalnız `chat__spinner`**, mesajların yerinde, içinde 340'ın halkası.
  `.chat__spinner`: `display: flex`, `justify-content: center`, `padding: 40px 12px`.
- **Yazma kutusu kapalı:** yazı alanı ve seçiciler `disabled`, `.composer__input:disabled,
  .picker:disabled { cursor: default; opacity: 0.4; }` — kit'teki öteki kapalı düğmeler gibi soluk.
- **Açılış bir tur çizmez:** tasarımda yüklenen kayıt tur çalıştırmaz. Uygulamada başka bir sohbete
  gidip, cevabı hâlâ gelen sohbete dönülünce kayıt yeniden okunurken akış görünür olabiliyor; açılış
  çerçevesinde sütunda yine yalnız spinner durur.
- **`← back` kalkar.** Yalnız açılışta: 404 alan sohbet (`That chat does not exist.`) tasarımda da
  `← back`'in altında kalır.

## Kararlar (kullanıcı yok, koşunun onayıyla verildi)

- **Kutudaki yazı sohbetler arasında taşınmaz.** Bugün açılış dalı yazma kutusunu söküyor, bu yüzden
  bir sohbette yazılıp gönderilmemiş cümle öteki sohbete geçmiyor; tasarım da açılışta kutuyu yeniden
  çiziyor (*the box ... start afresh*). Çerçeve açılışta da durunca React aynı kutuyu tutabilir, ve
  cümle öteki sohbete taşınır. Bugünkü davranış bir testle bekçiye alınır; bugün yeşildir.
- **Okunamayan sohbet (404 dışı hata)** `APP-BUGS.md`'nin 30'u, tasarımda çizilmiyor: bugün sonsuza
  kadar iskelet, bundan sonra sonsuza kadar spinner. Bu parçada test edilmez, değiştirilmez.
- **Uygulamanın testleri** bugün "kutu çıktıysa kayıt okunmuştur" diye yazılmış: `Reply...` kutusunu
  ya da seçicileri bulunca yazıp basıyorlar. Kutu artık açılışta da, kapalı duruyor; kapalı kutuya
  yazılan kayıt gelince kaybolur, kapalı seçiciye basılmaz. Bu testler, kayıt okununca açılan kutuyu
  bekleyen tek bir yardımcıyla (`chatOpened`) bekler. Bugün de yeşildirler: kutu bugün yalnız
  açıkken var.

## Testler ne tutar

| # | Dosya | Ne |
|---|---|---|
| 1 | `ChatScreen.test.jsx` | Açılan sohbette başlık kenar çubuğunun adı, dosya paneli dosyasıyla yerinde, yazma kutusu `Reply...` duruyor |
| 2 | `ChatScreen.test.jsx` | Sütunda yalnız `chat__spinner` ve içinde spinner; iskelet yok — bir tur akıyorken bile (ne noktalar ne akan yazı) |
| 3 | `ChatScreen.test.jsx` | Yazı alanı ve üç seçici `disabled` |
| 4 | `ChatScreen.test.jsx` | `← back` yok (tek başına duran geri düğmesi) |
| 5 | `ChatScreen.test.jsx` | Satırı da gelmemiş sohbetin başlığı boş |
| 6 | `ChatScreen.test.jsx` | Bir sohbetin kutusunda kalan cümle, açılıştan sonra öteki sohbetin kutusunda yok — bugün yeşil, bekçi |
| 7 | `ChatScreen.test.jsx` | Var olmayan sohbet: `That chat does not exist.`, `← back` var, spinner yok (bugünkü testin iskelet sorusu spinner'a döner) |
| 8 | `App.test.jsx` | Kaydı gelmeyen sohbet uygulamada: başlık kenar çubuğundaki satırın adı, spinner, kapalı kutu, dosya paneli, `← back` yok |
| 9 | `workspace.css.test.js` | `.chat__spinner` ortalar, `padding: 40px 12px` |
| 10 | `workspace.css.test.js` | `.composer__input:disabled, .picker:disabled`: `cursor: default`, `opacity: 0.4` |
| 11 | `workspace.css.test.js` | `.skeleton--message` stil sayfasında yok — tek kullanıcısı gidiyor |

Bugünkü *a chat still on its way draws blocks* testi kalkar: tuttuğu davranış kalkıyor.

`App.test.jsx`'te kayıt okunmuş sohbette yazan ya da seçici açan testler `chatOpened()`'ı bekler
(yukarıdaki karar).

## Tutmaz

- All projects'in, proje ekranının ve ilk yüklemenin iskeletleri 353'ün ve 364'ün; `Skeleton.jsx`
  ve testleri değişmez.
- CODE-STANDARD'ın hareket paragrafı 379'un; bu parça yeni bir animasyon eklemez, 340'ın halkasını
  kullanır.
- Halkanın döndüğü ve soluk kutunun görünüşü jsdom'da görülmez; tarayıcıda görülür.

## Bu turda yazılmayanlar

- `ChatScreen.jsx`, `Composer.jsx`, seçiciler, `App.jsx` ve `workspace.css` değişmez; uygulama
  turunda.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` kırmızı: 1–5, 8, 9, 10 ve 11
düşer; 6 ve 7 ve `chatOpened`'a geçen testler yeşil. Öteki üç süit bugünkü hâlinde. Kırmızı hâliyle
commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m355-sohbet-acilisi-testler-plan.md).
