# v14 · Görev 16 — Panel hata dili · **test turu**

**Kaynak:** yol haritası 16. madde · İstek 4.3 · tasarım v4 fark listesi 27, 28, 29, 35 ·
25. karar (*"buton hiçbir eksik alan için pasifleşmez"*).

Kullanıcının şikâyeti tek cümleydi:

> *"Seçilen karelerin henüz fotoğrafı yokken panel 'Tüm karelerin videosu var — üretilecek bir şey
> yok' diyor. Sebep o değil."*

Panel yanlış sebebi söylüyor, çünkü **tek bir sebebi** var.

## Bugün ne oluyor

`LayerPanel` kapsamı sayıyor, sıfırsa butonu kilitliyor ve altına katmanın tek boş-kapsam cümlesini
yazıyor:

| Gerçek durum | Bugünkü cümle |
|---|---|
| Her karenin videosu var | "Tüm karelerin videosu var — üretilecek bir şey yok." |
| Projede hiç üretilmiş kare yok | aynı cümle |
| Seçili kareler henüz fotoğraf değil | aynı cümle |
| Varyant kutusu boş | aynı cümle *(buton yine kilitli)* |

Dördü de aynı cümleyi görüyor ve dördünde de buton **basılmadan önce** kilitli — kullanıcı neden
basamadığını denemeden öğrenemiyor.

## Verilen kararlar

### 1 · Buton eksik alan için pasifleşmiyor *(fark 27)*

Basmadan önce panel sakin: kırmızı çerçeve yok, uyarı satırı yok, kilit yok. Basınca yeşil onay
kartının **kırmızı ikizi** doğuyor — aynı kutu, aynı yer, öbür renk.

Buton yalnız **süren işlemde** pasif: `Ekleniyor…` halinde.

**Bir istisna kalıyor: üretici yoksa buton yine pasif.** Tasarımın kendi istisnası bu — *"üretici
kuruluyorken"* — ve 5. karar kurulumu deftere bıraktığı için uygulamada o hâlin karşılığı "üretici
henüz burada değil". Panelin tepesindeki kurulum kartı bunu zaten yazıyor. Eksik bir alan değil,
süren bir engel.

### 2 · Sebep katman başına üç cümle *(fark 28, 35)*

| Neden basılamadı | Video paneli | Ses paneli |
|---|---|---|
| Bu katmanın asılabileceği hiçbir kare yok | "Henüz üretilmiş kare yok." | "Videosu olan kare yok." |
| Seçili karelerde o kare yok | "Seçili karelerin fotoğrafı henüz üretilmedi." | "Seçili karelerin videosu henüz üretilmedi." |
| Hepsinde bu katman zaten var | "Tüm karelerin videosu var." | "Tüm karelerin sesi var." |

Dördüncüsü katmandan bağımsız: **"Varyant sayısı girilmedi — en az 1 yaz."**

`— üretilecek bir şey yok` kuyruğu hiç yazılmıyor.

**Tasarımın dört cümlesinin karşılığı burada.** Farkın listelediği *"Henüz üretilmiş kare yok."*
video panelinin ilk satırı; ses panelinde aynı yerde *"Videosu olan kare yok."* duruyor, çünkü
sesin altında olması gereken şey fotoğraf değil video. Boş bir projede ses paneli de bunu yazıyor —
doğru, ve eksik olan asıl şeyi gösteriyor.

**Sıra, bir insanın bakacağı sıra:** önce gözünün önündeki kutu (varyant), sonra projede hiç
malzeme var mı, sonra ne seçtiği, en sonda kapsamın kendi cevabı.

### 3 · Varyant kutusu boşken kırmızı *(fark 29)*

Kutu boşken kırmızı çerçeveye dönüyor. Odaktan çıkınca sessizce 1'e dönmesi **kalkıyor** — yoksa
kutu hiçbir zaman kırmızı kalamazdı.

Sebep, **panelde bir şey değişince** siliniyor: varyant kutusuna yazınca, başka bir kapsam
seçilince, galerideki seçim değişince. Sebep bir basışa verilmiş cevap; o basışın saydığı kareler
ya da okuduğu sayı değiştiğinde bayat bir cevap oluyor.

### 4 · Sakin panel

Yapacak iş yokken butonun altında hiçbir şey yazmıyor. Tahmin cümlesi yalnız yapacak iş varken
duruyor; boş kapsamın kendi cümlesi (`words.empty`) tümüyle gidiyor.

## Kapsam dışı

- **Fotoğraf paneli.** Fark listesinin "Fotoğraf üret" bölümünde butonla ilgili tek madde yok; üç
  yol da orada bir fark görmedi. Prompt listesi boşken butonun kilitli olması bu maddenin değil.
- **Kapsam satırının adı, radyo dairesi, model kutusu, Süre bloğu** (fark 30–33) 17. madde.
- **Kurulum uyarısının kendi kartına geçmesi** (fark 38) 25. madde.
- **Yeşil kartın ömrü** (fark 21) 8. kararla 10 saniye.

## Yazılacak testler

### `LayerPanel.test.jsx` — 15 yeni, 2 silinen

Yeni bir blok: `LayerPanel — why the press was refused`.

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Yapacak iş yokken buton basılabilir ve altında hiçbir şey yazmıyor | 27 |
| 2 | Basınca "Tüm karelerin videosu var." diyor | 28 |
| 3 | Reddettiği isteği sunucuya göndermiyor | 27 |
| 4 | Projede üretilmiş kare yokken bunu söylüyor | 28 |
| 5 | Seçili kareler fotoğraf değilken bunu söylüyor | 28 · İstek 4.3 |
| 6 | Varyant kutusu boşken bunu söylüyor | 28, 29 |
| 7 | Varyant kutusu boşken kırmızı | 29 |
| 8 | Sayı yazılınca sebep siliniyor | 29 |
| 9 | Başka kapsam seçilince sebep siliniyor | 29 |
| 10 | Sebep, yeşil kartın kırmızı ikizi | 27 |
| 11 | Sebep dururken buton hâlâ basılabilir | 27 |
| 12 | Buton yalnız istek yoldayken kilitli | 27 |

`LayerPanel — sound` bloğuna üç:

| # | Ne diyor | Fark |
|---|---|---|
| 13 | "Tüm karelerin sesi var." | 35 |
| 14 | Videosu olan kare yokken bunu söylüyor | — |
| 15 | Seçili karelerin videosu yokken bunu söylüyor | — |

**Silinen iki test:** `says there is nothing to do rather than treating it as a fault` ve
`says there is nothing to do in its own words` — ikisi de bugünkü tek cümleyi ve kilitli butonu
ölçüyor, ikisi de 27 ve 28 ile düşüyor. Yerlerine 1 ve 13 geçiyor.

**Toplam 15 yeni, 2 silinen: 454 → 467.**

## Doğuştan yeşil iki test

3 ve 12 bugün de geçiyor. 3 bugün başka bir sebeple geçiyor — buton kilitli olduğu için tıklama
zaten hiçbir şey yapmıyor — ama ölçtüğü kural yarın da geçerli: reddedilen bir basış sunucuya
gitmez. 12 ise farkın ikinci yarısını tutuyor: bugün doğru olan tek kilit `Ekleniyor…`, ve o
kilidin kalkmadığını söyleyen bir test yoktu.

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de **13 kırmızı** duruyor. Testler kırmızı commit
ediliyor.
