# Madde 505 · Yazma kutusu büyür — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v12 yol haritası](../roadmaps/2026-10-24-queen-agent-v12-roadmap.md#v12-2),
505 · v12-2 · **Dal:** `feat/queenagent-v12` · **Önceki:**
[504](2026-10-27-queen-agent-m504-duzenleme-kutusu-design.md) (düzenleme kutusu, `useGrowingField`) ·
**Kurallar:** [FOUNDATION](../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Yazma kutusu bugün 1'den 20 satıra kadar hep 54 px, yani 2 satır; 3. satırdan sonra yazı içinde kayıyor
ve en üstte yarım kesilmiş bir satır görünüyor. Kullanıcı: ChatGPT'deki gibi yazı uzadıkça büyüsün, bir
sınırdan sonra içinde kaysın; *"İkisi de %40 olsun."* *(27 Ekim)* — düzenleme kutusuyla aynı sınır.

**Kabul:** yazı uzadıkça kutu büyüyor; ekranın %40'ına gelince büyümesi duruyor ve yazı içinde kayıyor;
mesaj gönderilince kutu bugünkü 2 satırlık boyuna dönüyor.

## Büyüme: 504'ün parçası

`Composer` 504'ün `useGrowingField`'ını alıyor: `useGrowingField(field, draft)`. `field`, kutunun
`focus` için zaten tuttuğu ref; ikinci bir ref açılmıyor.

- **Büyüme:** her taslak değişiminde kutu yazısı kadar uzun (504'teki gibi: `auto` → çubuksuz
  `scrollHeight` → `+ kenarlık`). Kutunun kenarlığı yok, dolgusu tarayıcının varsayılanı.
- **2 satıra dönüş:** gönderince `submit` taslağı `""` yapıyor, hook yeniden ölçüyor; boş kutu `rows`
  boyunda, yani `rows={2}` — bugünkü 54 px. Ayrı bir "sıfırla" yok.
- **Sınır, iki kutu için tek kural** (reviewer'ın notu: aynı karar iki yerde iki `40vh` olursa
  ayrışabilir):

  ```css
  .msg__editing-input,
  .composer__input {
    max-height: 40vh;
  }
  ```

  504'te sınır `.msg__editing-input`'un kendi kuralındaydı; oradan bu kurala taşınıyor. Bir CSS
  değişkeni yerine tek kural, çünkü değer tek yerde yazılı kalıyor ve iki seçici yan yana "bu iki kutu
  aynı sınırı paylaşır" diyor; değişken bir isim ve bir okuma daha eklerdi.

## Genişlik değişince yeniden ölç

Aynı yazı başka bir genişlikte başka sayıda satıra kırılıyor; yükseklik yalnız yazı değişince ölçülürse
genişlik değişince yanlış kalıyor. Üç yerde görüldü:

- **Dar pencerede ilk yükleme** (QA, 27 Ekim): `useShellWidth` ilk karede genişliği bilmiyor, en geniş
  düzen çiziliyor ve kutu birkaç piksel genişliğinde kalıyor. Hook boş kutuyu o genişlikte ölçüyor;
  Chromium'un `scrollHeight`'i kırılmış yer tutucuyu sayıyor. 420×800 ve 560×800'de yeniden yüklemede
  kutu 202 px (8 satır), gerçek Chrome'da 560 genişlikte 212 px açılıyordu; taslak değişene kadar hiçbir
  şey yeniden ölçmüyordu.
- **Gizli kutu:** sohbet dolunca kutu `hidden={chat?.full}` ile gizleniyor ama taslağı koruyor
  (Continue onu geri veriyor). Gizliyken taslak değişirse (ör. reddedilen bir cevap geri dönerse) ölçüm
  0 çıkar ve kutu 2 satırla geri gelirdi.
- **Bir atanın gizlediği kutu:** dar kabukta bir dosya açıkken `.chat` `display: none`; aynı durum.
- Ve kutu açıkken pencerenin daralması ya da dosya rayının açılması.

**Seçilen: hook'ta kutunun kendisine bir `ResizeObserver`.** Kutunun genişliği değişince yeniden
ölçüyor. Gizlenip gösterilen kutu genişliği 0'dan kendi genişliğine geçtiği için bu, ilk sürümdeki
`hidden` argümanının işini de görüyor; argüman kaldırıldı ve ataların gizlediği kutu da kapsanıyor.

- **Gizliyken yükseklik korunuyor:** gözlemci gizlenen kutunun genişliğini 0 bildiriyor. 0 genişlikte
  çizilen bir şey yok, ölçülecek bir şey de yok; hook genişliği saklıyor ama ölçmüyor, kutu sahip olduğu
  yüksekliği koruyor. Ölçseydi yükseklik `auto`'ya düşerdi ve Continue'da kutu bir kare 2 satır
  boyunda çizilip sonra sıçrardı (reviewer: 6 satırlık taslak önce 54, sonra 153 px). Gösterilince
  genişlik 0'dan kendi genişliğine geçiyor ve kutu yeniden ölçülüyor; taslak gizliyken değiştiyse
  yükseklik de böyle düzeliyor.

- **Yalnız genişlik:** yükseklik hook'un kendi yazdığı şey; gözlemci ona cevap verseydi her ölçüm bir
  ölçüm daha doğururdu. Son görülen genişlik saklanıyor, aynıysa hiçbir şey yapılmıyor.
- **Bir kare sonra:** ölçüm geri çağırmanın içinde değil `requestAnimationFrame`'de. Gözlenen kutuyu geri
  çağırmada boyutlandırmak kendi bildirimini teslim edilmemiş bırakıyor ve tarayıcı bunu bir hata olarak
  bildiriyor ("ResizeObserver loop completed with undelivered notifications"). Bedeli genişlik
  değiştiğinde bir karelik eski yükseklik; ilk yüklemede o kare zaten düzenin henüz ölçülmediği kare.
- Gözlemci ilk bağlandığında bir kez bildiriyor; bu ilk ölçümü bir kez daha yapıyor (tek yerleşim
  okuması).
- `ResizeObserver` olmayan bir ortamda (jsdom) gözlem yok, yazı değişince ölçüm sürüyor.
- Yazı değişince ölçüm 504'teki gibi `useLayoutEffect`'te, ekran çizilmeden.
- Düzenleme kutusu da aynı hook'u kullandığı için aynı davranışı alıyor.

## Sohbet listesi

Liste (`.chat__scroll`, `flex: 1`) ve kutu (`.chat__composer`, `flex: none`) aynı sütunda, liste
kutunun üstünde. Kutu büyüyünce listenin görünen alanı alttan kısalıyor; `scrollTop` aynı kaldığı için
dipteki son satırlar kutunun arkasına değil, görünen alanın dışına iniyor. Kaydırma olayı olmuyor,
listeyi takip eden kod da (`following` / `toBottom`) yalnız içerik değişince çalışıyor. Yani bugün bu
durumda dibi izleyen okur son satırları kaybeder — kutu sabit 54 px olduğu için şimdiye kadar hiç
olmamıştı.

**Çözüm `ChatScreen`'de:** listeye bir `ResizeObserver`. Listenin boyu değişince, okur dibi izliyorsa
(`following`) `toBottom`. Okur yukarıdaysa yerinde kalıyor — listenin içerik kurallarıyla aynı.
Gözlemci listenin kendi kutusunu izliyor, içeriğini değil: düzenleme kutusunun (504) büyümesi onu
tetiklemiyor. Pencere daralması ve dosya rayının açılması da aynı yoldan geçiyor ve dibi izleyen okur
dipte kalıyor. `ResizeObserver` olmayan bir ortamda (jsdom) hiçbir şey yapmıyor, `useShellWidth` gibi.
Kutu `missing` dalında yok; gözlemci `missing` değişince yeniden bağlanıyor.

## Ne değişmiyor

- Kutunun tuşları, taslak kuralları, Send/Stop, gizlenme ve Continue aynı.
- Düzenleme kutusunun davranışı aynı; yalnız sınırı ortak kurala taşınıyor.

## Sınırlar

- 504'ün sınırı burada da geçerli: ölçüm sırasında kaydırmanın kırpılması Firefox'ta denenmedi.
- Sohbet doluyken reddedilen bir cevap gizli kutuya dönerse, yazı değişimi kutuyu 0 ölçüp `auto`'ya
  düşürüyor; kutu gösterildiğinde bir kare 2 satır boyunda çiziliyor, sonra genişlik gözlemiyle doğru
  boyuna geliyor. Bırakıldı (ana ajan, 27 Ekim): yalnız bu durumda ve bir kare.
- Sınırın ötesinde, kutu kendi içinde kayarken en üstte yarım satır görünebilir; ChatGPT'de de öyle.
  Bugünkü yarım satır 3. satırdan sonra çıkıyordu, artık yalnız %40'tan sonra.

## Maliyet

Disk ve ağ: yok. Her tuşta 504'teki gibi tek bir yerleşim okuması. Kutunun genişliği değişince bir
ölçüm daha; yüksekliği değişince hiçbir şey. Kutu büyüyüp listenin boyu değişince listenin gözlemcisi
bir kez çalışıyor; okur dibi izliyorsa bir `scrollTop` yazımı.

## Testler

- **`shared/useGrowingField.test.jsx`** (`ResizeObserver` ve `requestAnimationFrame` sahte): genişliği
  değişen kutu, yazısı aynıyken yeniden ölçülüyor (4 px'te 202, 560 px'te 54); 0 genişliğe gizlenen
  kutu yüksekliğini koruyor; yalnız yüksekliği değişen kutu yeniden ölçülmüyor.
- **`Composer.test.jsx`:** taslak uzayınca kutu uzuyor; gönderilince `rows` boyuna dönüyor.
- **`ChatScreen.test.jsx`:** liste kısalınca dibi izleyen okur dipte kalıyor; yukarıdaki okur yerinde.
- **`workspace.css.test.js`:** `max-height: 40vh`, `.msg__editing-input, .composer__input` ortak
  kuralında.

## Bitti sayılır

- `npm test --prefix queen-agent/frontend` yeşil; `python -m pytest queen-agent -q` dist testi dışında
  yeşil (commit'e kadar beklenen); `dist` yeniden kuruldu.
- Kabul ekranda (QA, Playwright): kutu yazdıkça büyüyor, %40'ta durup içinde kayıyor, gönderince 2
  satıra dönüyor; dipte okurken kutu büyüyünce son satırlar görünür kalıyor; dar pencerede yeniden
  yüklemede boş kutu 54 px.
