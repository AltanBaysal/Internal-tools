# v14 · Görev 26 — Kuyruk panelinin görsel hizalaması · **test turu**

**Kaynak:** yol haritası 27. madde · tasarım v4 fark listesi 41–48, 50, 59 · 4. karar ·
47, 48, 49. kararlar.

G bölümünün son maddesi ve bir grup: on fark, hepsi tek panelde. Yedisi uygulanıyor, ikisi kararla
düşüyor, biri 25. maddede zaten kapandı.

**26. maddeye bağlı değil.** Onun kararı bekleme kartının *sözünü* ve kuyruğun kendiliğinden akıp
akmayacağını ilgilendiriyor; buradaki on farkın hiçbiri o cümleye ya da o davranışa dokunmuyor.
47. fark bekleme hâlinde bir düğmenin görünmesini istiyor — kuyruğun nasıl süreceğini değil.

## Uygulanan yedi fark

| # | Bugün | Olacak |
|---|---|---|
| **41** | "Foto · üretiliyor", "Video · sırada" | "Foto — üretiliyor", "Video — sırada"; üreticisi eksik tür **"— bekliyor"** |
| **42** | Kartın büyük sayısı her hâlde vurgu renginde | Çalışan türünki normal metin, sıradakinki soluk; vurgu yalnız başlık satırında |
| **43** | "Duraklat"a basılınca nokta vurgu renginde nabız atıyor | Nokta soluk tona düşüp öyle nabız atıyor, başlık da soluk |
| **44** | Bitince "n kare üretildi" yeşil | Başlık yeşil kalıyor, cümle soluk |
| **45** | "Hepsini tekrar dene" | "Tekrar dene" |
| **46** | Kırmızı hata kartı akarken de, duraklamışken de, bitmişken de var | Yalnız kuyruk tamamlandığında doğuyor |
| **47** | Üretici beklerken "Kuyruğu boşalt" çıkmıyor | Beklerken de duruyor ve basılabiliyor |

**41'in üçüncü hâli 25. maddenin üstünde duruyor.** Kart artık üreticisinin kurulu olup olmadığını
biliyor; "bekliyor" o bilginin başlığa yansıması. Tire ise ayracın kendisi — evin başka yerlerinde
`·` kalıyor, örneğin hata kartının "2 foto · 1 video" dökümünde: orası bir liste, bu bir durum.

**46'nın bedeli yazıya geçiyor.** Kart yalnız `tamamlandı` hâlinde doğduğu için, duran ya da
duraklatılmış bir koşunun hataları panelde görünmüyor; galeride kırmızı kareler ve kendi "Tekrar
dene" düğmeleriyle duruyorlar. Tasarımın "yalnız" sözü bunu kapsıyor ve farkın kendi *bugün*
listesi duraklamış hâli de şikâyet ediyor.

**47 güvenli.** Boşaltmanın tek koşulu ortada render edilen bir kare olmaması — kuyruk beklerken
motorun elinde iş yok, dolayısıyla kuyruktan çekilecek bir şey de kimsenin altından alınmıyor.

## 47 · Fark 48 düşüyor — "kare" kalıyor

Fark 48, boşaltma onayının ikinci cümlesinde "Üretilmiş **kareler** galeride kalır" yerine
"Üretilmiş **fotoğraflar**" istiyor. Bu, 4. kararın kapattığı sorunun aynısı: tasarımın kendi
terminoloji kuralı içerik birimi için "kare" diyor, çizimi bazı cümlelerde "fotoğraf" diyor, ve o
sözcük terminoloji netleşmeden önceki dilden kalmış. 4. karar boş ekran metinleri için verilmişti
(fark 7 ve 67); gerekçe sözcüğün kendisine ait, dolayısıyla burada da geçerli.

## 48 · Fark 50 düşüyor — ham çıktı kutusu kalıyor

Fark 50, durmuş koşunun kartından açılır ham çıktı kutusunun kalkmasını ve yerine tek satır teknik
neden yazılmasını istiyor.

O tek satır **zaten ilk satır**: kart bugün de kuralın kendi cümlesini üstte, servisin cevabını
altındaki kutuda gösteriyor. Kalkması istenen şey cümle değil, **kanıt**.

Kanıt atılmıyor, çünkü deponun kendi kuralı bunu yasaklıyor: *hata mesajında sebep uydurulmaz,
komutun ya da servisin gerçekte ne dediği yazılır.* Uygulama, tasarımın örnek cümlesindeki gibi
sentezlenmiş bir teşhisi ("3 kez denendi, sunucuya ulaşılamadı") üretemez — üretirse uydurmuş olur.
Elindeki iki şey var: kuralın cümlesi ve servisin sözleri. Kutu ikincisinin durduğu yer, ve
kopyalanabilir olması kullanıcının hatayı buraya taşıyabilmesinin tek yolu.

Kutu zaten uzun bir çıktının düğmeleri panelden dışarı itmemesi için yazılmıştı ve iki testi var.
Farkın sinyali tek yoldan gelen zayıf sinyal; kural ondan ağır basıyor.

## 49 · Fark 59 zaten kapandı

*"Kuyruk panelindeki Kur düğmesi her yerde yalnız 'Kur' desin."* 25. maddede o düğme koşu kartından
tür kartına indi ve orada tam olarak **Kur** yazıyor; koşu kartındaki "Video üreticisini kur" hiç
kalmadı. Yapılacak iş yok.

## Kapsam dışı

- **Tür kartlarıyla durum kartının bir arada durması** (fark 40) — 2. kararla kapandı.
- **Kuyruğu boşalt onayının butonu** (fark 49) — 3. kararla kapandı, "Boşalt" kalıyor.
- **Bağlantı kopunca çıkan kart** (fark 51) — yol haritasında yok.
- **Bekleme kartının sözü ve kuyruğun kendiliğinden sürmesi** (fark 37) — 26. madde.
- **Motor.** Python takımı 709'da kalıyor.

## Yazılacak testler

### Ön yüz — `QueuePanel.test.jsx` (6 yeni, 5 değişen)

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Akan kuyrukta kart başlığı tire ile ayrılıyor *(değişen)* | 41 |
| 2 | Duraklamış kuyrukta da öyle *(değişen)* | 41 |
| 3 | Üreticisi eksik tür "bekliyor" diyor | 41 |
| 4 | Çalışan türün sayısı normal metin, sıradakininki soluk | 42 |
| 5 | Duraklatılırken nokta soluk tonda nabız atıyor ve başlık soluk | 43 |
| 6 | Tamamlandı kartının başlığı yeşil, cümlesi soluk | 44 |
| 7 | Hata kartının düğmesi "Tekrar dene" *(değişen)* | 45 |
| 8 | Hata kartı akarken ve duraklamışken doğmuyor | 46 |
| 9 | Döküm testi tamamlanmış kuyruğa taşınıyor *(değişen)* | 46 |
| 10 | Toplu tekrar testi tamamlanmış kuyruğa taşınıyor ve yeni yazıyı okuyor *(değişen)* | 45 · 46 |
| 11 | Üretici beklerken kuyruk boşaltılabiliyor | 47 |

**Ön yüzde 6 yeni test: 541 → 547. Kırmızı duran 10 test** — altı yenisi ve dört değişeni.
9 numara doğuştan yeşil: kart bugün her hâlde çiziliyor, dolayısıyla tamamlanmış kuyrukta da
çiziliyor.

## Bitti sayılır

Dört komut da koşuyor; queen-editor'ün frontend takımında **10** kırmızı duruyor, Python takımı
**709** ile yeşil kalıyor. Testler kırmızı commit ediliyor.
