# v14 · Görev 14 — Detaydan dönünce galerinin yerinde durması · **test turu**

**Kaynak:** yol haritası 14. madde · İstek 1.2 (ham listedeki 6).

> *"Bir kareyi açıp geri gelince galeri sıfırdan yükleniyor, fotoğraflar ekrandan kayboluyor.
> Dosyalar Drive'da duruyor — kaybolan görüntü, veri değil. Olması gereken: geri dönünce sayfa
> bıraktığın yerde dursun."*

## Bugün ne kayboluyor

Bir kare açılınca yol değişiyor ve `ProjectScreen` tümüyle sökülüyor. Üç şeyden **biri** zaten
korunuyor:

| Ne | Bugün |
|---|---|
| Galerinin listesi | **Korunuyor** — `useGeneration`'daki `REMEMBERED`, proje başına son cevabı tutuyor |
| Kayma yeri | Kayboluyor — kaydırma kutusu yeniden kuruluyor ve tepeden başlıyor |
| Karoların resimleri | Kayboluyor — her `TileImage` sıfırdan doğuyor, önce görüş alanını sonra kuyruk sırasını bekliyor |

Kullanıcının gördüğü şey ikisinin toplamı: aşağıdayken bir kare açıp dönünce galeri tepede
açılıyor ve baktığı fotoğraflar orada değil.

## Verilen kararlar

### 1 · Kayma yeri proje başına hatırlanıyor

`REMEMBERED`'ın biçimi: modül düzeyinde bir eşleme, proje anahtarlı, **yalnız bellekte**. Sayfa
yenilenince unutuluyor — istenen şey bir ziyaret içinde yerinde durmak, projenin bir özelliği
değil.

Yazma anı **sökülme**: her kaydırma olayında değil, ziyaret başına bir kez. Düğüm etkinin gövdesinde
yakalanıyor, çünkü temizlik anında bir `ref`'e güvenmek gerekmiyor.

Okuma anı **yerleşim etkisi** (`useLayoutEffect`), sıradan etki değil: geri koyma tarayıcı
boyamadan önce olmalı, yoksa galeri bir kare boyunca tepede çizilip sonra zıplıyor.

Kutunun yüksekliği resimlere bağlı değil — karolar `aspect-ratio: 1/1`, yani ızgara resimler
gelmeden de doğru boyda. Bu yüzden kayma yeri ilk boyamada yerine oturuyor.

### 2 · Bir kez ekrana gelmiş resim yeniden beklemiyor

`TileImage` her doğduğunda iki kapı bekliyor: görüş alanı ve kuyruk sırası. Bekleme **doğru**, ama
yalnız ilk seferinde: baytlar tarayıcının önbelleğinde (foto URL'leri `immutable` başlıkla gidiyor),
yani ikinci kez beklenen şey verinin kendisi değil, sıranın kendisi.

Oturum boyunca ekrana gelmiş URL'ler bir kümede tutuluyor. Kümedeki bir karo iki kapıyı da atlıyor:
`src`'si ilk render'da yerinde.

**Patlamış resim hatırlanmıyor** — ekrana gelmemiş bir şeyin saklanacak bir hâli yok.

Küme kendi modülünde ve **dışa açık**: `image_queue.js`'in yanında, aynı türden bir oturum
kaynağı. Açık olması testlerin onu temizlemesini sağlıyor — modül düzeyinde sessiz bir bellek,
aynı dosyadaki testleri birbirine bağlar.

### 3 · Kaydırma kutusunun kendi işareti

Kutu bugün yalnız satır içi biçimiyle tanınıyor. `data-scroll` alıyor — `data-tile`, `data-check`,
`data-veil` ile aynı âdet.

## Yazılacak testler

### `useKeptScroll.test.jsx` — 3 *(yeni dosya)*

| # | Ne diyor |
|---|---|
| 1 | Hiç görülmemiş bir galeri tepeden başlıyor |
| 2 | Kutu bırakıldığı yere dönüyor |
| 3 | Bir projenin yeri başkasınınkine karışmıyor |

### `TileImage.test.jsx` — 2

| # | Ne diyor |
|---|---|
| 4 | Bir kez gösterilmiş resim, karo yeniden kurulunca beklemeden duruyor |
| 5 | Hiç gelmemiş resim hatırlanmıyor |

Dosyanın tamamı `beforeEach`'te kümeyi temizliyor: bugünkü testlerin hepsi aynı dosya adını
kullanıyor, ve temizlenmeyen bir bellek onları birbirine bağlardı.

### `ProjectScreen.test.jsx` — 1

| # | Ne diyor |
|---|---|
| 6 | Ekran sökülüp yeniden kurulunca galeri bırakıldığı yerde açılıyor |

**Toplam 6 test.**

## Kapsam dışı

- **Küçük önizleme** (İstek 1.1) bu madde değil. O, indirilen veriyi küçültmekle ilgili; bu madde
  ekrandan kaybolan görüntüyle.
- Sayfa yenilendiğinde yerinde durmak. İstenen şey uygulama içinde gidip gelmek.

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de 6 kırmızı duruyor. Testler kırmızı commit ediliyor.
