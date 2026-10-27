# v14 · Görev 25 — Uyarı kendi kartına geçiyor · **test turu**

**Kaynak:** yol haritası 25. madde · tasarım v4 fark listesi 38 · 46. karar.

G bölümünün ilk maddesi. Fark `davranış` damgalı ve gerçekten davranış değiştiriyor — ama
beklenmedik bir yerde.

## Fark ne diyor

> **Bugün:** yalnız bir türün üreticisi eksikken kuyruk paneli bütünüyle bekleme hâline geçer;
> uyarı ve "Kur" ortak kartta durur, diğer türlerin kartları soluklaşır.
>
> **Tasarım v4'te:** yalnız o türün kartı kendi içinde "Üretici kurulu değil." ve küçük bir "Kur"
> gösterir; panelin geneli etkilenmez, diğer türler normal akar ve sıra o türe gelince motor bekler.

## 46 · Cümlenin motor yarısı zaten doğru

*"Sıra o türe gelince motor bekler"* ve *"diğer türler normal akar"* bugün de böyle, ve tesadüfen
değil:

`queue.ORDER` foto → video → ses. Motor bir türü bitirmeden ötekine başlamıyor ve `queue.py`'nin
kendi başlığı sebebini yazıyor — her tür kendi üreticisini yüklüyor, aralarında zıplamak her turda
bir model yeniden yüklerdi; ve bir video, üstüne asıldığı fotoğrafın önce var olmasını istiyor.
`run_loop` sırayı gelen ilk işte kesiyor, ötesine **bilerek** atlamıyor, ve bunu koruyan bir test
var: `test_the_engine_does_not_skip_past_the_type_it_is_waiting_for`.

Yani ses üreticisi eksikken fotoğraflar ve videolar bugün de üretiliyor; kuyruk yalnız ilk ses
işinde duruyor. **Bu madde motora dokunmuyor**; o testler ve o sıra yerinde kalıyor.

## Değişen ne

Değişen, **panelin ne zaman ve nerede konuştuğu.**

Bugün panel eksikliği ancak motor o türe geldiğinde öğreniyor: `job.status === "waiting"` gelene
kadar hiçbir şey söylenmiyor. Yani ses üreticisi eksikken kullanıcı kırk fotoğrafın ve kırk videonun
üretilmesini bekliyor, ve ancak en sonda "bekliyor — üretici kurulu değil" cümlesiyle karşılaşıyor.
Oysa cevap ilk andan beri elde: hangi üreticinin kurulu olduğu uygulama açılırken bir kez soruluyor
ve değişmiyor (`useProducers`; kurulum defterde, uygulama koşmadan önce).

Bundan sonra: **eksiklik, o türün kendi kartında, öğrenildiği anda yazıyor.** Kuyruk akmaya devam
ediyor, foto kartı canlı duruyor, ses kartı kendi içinde "Üretici kurulu değil." ve küçük bir "Kur"
taşıyor. Yol haritasının kabul cümlesi de bu: *"Ses üreticisi eksikken foto ve video kartları
akıyor, uyarı yalnız ses kartında duruyor."*

**Söyleyecek sözü olan kart soluklaşmıyor.** Bugün canlı olmayan her kart `opacity: .55` ile
duruyor; bir uyarıyı o tonda yazmak onu okunmaz yapar. Canlı kart vurgulu çerçevesini, sırada
bekleyen kart solukluğunu koruyor; arada üçüncü bir hâl doğuyor — bekliyor ama söyleyecek bir şeyi
var.

**"Kur" hiçbir şey kurmuyor**, ve bu maddenin getirdiği bir sapma değil: uygulamanın temel kararı
(FOUNDATION 9, fark listesinin 5. kararı) indirmeyi deftere bırakıyor. Düğme, o üreticinin satırına
uygulamanın tek cevabını yazıyor — *"Bu üretici Colab defterinden kurulur…"* — ve cümle aynı kartta
okunuyor. Panelin diğer iki "Kur"u da (üretim panelleri, üreticiler paneli) tam bunu yapıyor.

## Koşu kartından ne iniyor

Uyarı ve kurulum düğmesi tür kartına taşındığı için koşu kartının `waiting` dalından ikisi de
çıkıyor. Kartın kendisi **kalıyor**: başlığı, sayısı ve devam yolu yerinde. Fark 37 — 26. madde —
o kartın üstüne bir cümle daha yazacak, yani karta hâlâ ihtiyaç var.

**`producerReady` bayrağı da düşüyor.** Panel artık üretici satırlarının kendisini görüyor;
"bu türün üreticisi kurulu mu" sorusunun cevabını hem satırlarda hem yanında taşınan bir `boolean`da
tutmak aynı kuralı iki sahipli yapar. Hesap panelin içine iniyor, `ProjectScreen`'den ve
`SidePanel`'in imzasından çıkıyor — 13 Ağustos 2026 kararını anlatan yorum da onunla birlikte, artık
açıkladığı düğmenin yanına.

## Kapsam dışı

- **Motor.** 46. karar; Python takımı 709'da kalıyor.
- **Kurulum bitince kuyruğun kendiliğinden sürmesi** (fark 37) — 26. madde. Koşu kartındaki
  *"Üretici kurulduktan sonra kuyruğu sen sürdürürsün."* cümlesi bu turda olduğu gibi kalıyor.
- **Tür kartının başlık dili ve büyük sayısının rengi** (fark 41, 42) — 27. madde.
- **Uygulamanın indirme yapması** — 5. kararla kapalı.

## Yazılacak testler

### Ön yüz — `QueuePanel.test.jsx` (7 yeni, 2 değişen)

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Üreticisi eksik tür bunu kendi kartında söylüyor | 38 |
| 2 | Karttaki Kur o türün üreticisini istiyor | 38 |
| 3 | Söyleyecek sözü olan kart soluklaşmıyor | 38 |
| 4 | Üreticisi yerinde olan türler bir şey söylemiyor | 38 |
| 5 | Kuyruk akmaya devam ediyor: foto kartı canlıyken ses kartı uyarısını taşıyor | 38 |
| 6 | Uygulamanın cevabı aynı kartta okunuyor | 38 · karar 5 |
| 7 | Üretici listesi gelmeden hiçbir şey söylenmiyor | 38 |
| 8 | Koşu kartı artık kurulum düğmesi taşımıyor *(değişen)* | 38 |
| 9 | Devam yolu bayraktan değil satırlardan çıkıyor *(değişen)* | 38 |

### Ön yüz — `SidePanel.test.jsx` (1 yeni)

| # | Ne diyor |
|---|---|
| 10 | Kuyruk paneline üretici satırları veriliyor |

**Ön yüzde 8 yeni test: 533 → 541. Kırmızı duran 8 test.** 4 ve 7 doğuştan yeşil: ikisi de bir
**yasağı** koruyor — panel bugün üreticilerden hiç söz etmiyor, dolayısıyla kaldırılacak bir
karşılıkları yok.

## Bitti sayılır

Dört komut da koşuyor; queen-editor'ün frontend takımında **8** kırmızı duruyor, Python takımı
**709** ile yeşil kalıyor. Testler kırmızı commit ediliyor.
