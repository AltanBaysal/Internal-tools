# Madde 185 · test turu — action'ı olmayan bütün kareleri dolduran araç

**Kaynağı:** [yol haritası, Madde 185](../plans/2026-09-06-queenagent-v8-roadmap.md).
184 `d6eeaee`'de kapandı.

---

## Ne kanıtlanacak

Bugün `write_frame_prompt` tek kare alıyor — *"One frame per call"*, kendi açıklamasında yazılı.
Deneme 4'te 21 kare **21 ana ajan raundu** ve **277.6k jeton** etti. Fatura yazarın değil: her raunt
sistem promptunu, skill metnini ve **bağlam kabını** baştan gönderiyor, ve kaptaki yapı dosyası her
yazımda büyüyor.

Yeni araç bunu **tek raunda** indiriyor: dosyanın tamamına bakar, `action`'ı olanı atlar, olmayanı
yazar, ve istekler **aynı anda** gider.

## Adı: `write_missing_actions`

`write_frame_prompt`'un çoğulu olamaz — adı bir harf ayrı iki araç, ilk günden karışır; 189'da
`prompts.py` aynı sebeple reddedildi. Ad ne yaptığını söylüyor: eksik olan action'lar.

Tek kareli araç **yerinde kalıyor**. O düzeltmenin aracı: not parametresi onda, ve bir kareyi
yeniden yazdırmak onunla oluyor.

## Parametre: yalnız `file`

- **Aralık yok** *(kullanıcı kararı)*. Yapılacak işin tanımı zaten *boş kare*; bir `from`/`to`
  modele karar bindirir ve hangisinin yazıldığını iki yerden takip ettirir.
- **Not yok.** Bu ilk yazım. Not düzeltmenin şeyi, düzeltme de öteki aracın işi.

## Bir kare düşerse ötekiler durmaz

Yirmi istekten biri hata alırsa **on dokuzu yazılır**, ve cevap hangisinin yazılamadığını söyler.
Hepsini geri almak, ödenmiş bir saatlik işi tek hata için çöpe atmak olurdu. Madde 173'ün *"ya hep ya
hiç"* kuralı **yazmadan önce yapılan bir kontrole** aitti — orada geri alınacak bir şey yok, burada
var.

Aynı sebeple **dosya bir kez kaydediliyor**, hepsi bittikten sonra: yazılanlar tek yazımda diske
iner ve yarısı yazılmış bir dosya diye bir ara hâl olmaz.

## Paralellik nasıl ölçülür

Bu maddenin bütün kazancı *aynı anda*. Sıralı koşan bir uygulama da bütün testleri geçerdi — biri
hariç: **`threading.Barrier`.** Yazar, her çağrıda bariyerde bekliyor; bariyer ancak boş kare sayısı
kadar çağrı **aynı anda** orada olunca açılıyor. Sıralı koşan bir araç ilk çağrıda takılır,
bariyerin süresi dolar, ve hiçbir kare yazılmaz.

Ölçtüğü şey uygulamanın şekli değil, davranışı: kaç iş parçacığı açıldığını değil, ikisinin
aynı anda uçtuğunu.

## Testler

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | boş kareler dolar, dolu olan kımıldamaz | maddenin kendisi |
| 2 | yazar boş kare sayısı kadar sorulur | dolu kare için para ödenmiyor |
| 3 | istekler aynı anda uçar | bariyer |
| 4 | cevap kaç kare yazıldığını ve hangilerini söyler | model sonraki hamlesini buradan okur |
| 5 | ikinci çağrı *yazılacak boş kare yok* der | iş bitmiş, ve bunu söylemek bir raunt |
| 6 | düşen bir istek ötekileri durdurmaz ve adıyla anılır | kısmi başarı kayıt altında |
| 7 | boş cevap yazılmaz, o kare de anılır | tek kareli aracın kuralı, çoğulda |
| 8 | sahnesi olmayan kare atlanır, ve **sorulmaz** | ödenmeden reddedilen |
| 9 | fatura tek toplam olarak döner | damga bir raundun harcamasını gösterir |
| 10 | her istek yalnız kendi karesini taşır | ucuzluğun sebebi, Madde 176'nın kuralı |
| 11 | model yoksa söyler, hiçbir şey yazılmaz | `run_tool`'un `engine`'i isteğe bağlı |
| 12 | araç `TOOL_SPECS`'te, ve açıklaması `prompt.py`'den | 189'un nöbetçisi zaten tutuyor |
| 13 | araç adı olmayan bir dosyayı reddeder | `_opened`'ın ortak cevabı |

## Kırmızı turun tuzağı, ve on birincisi

Bu koşuda on kez görüldü. Buradaki tehlikeli hâli **5. test**: *"yazılacak boş kare yok"* cümlesi,
araç hiç yokken de bir hata cümlesiyle karşılanır. O yüzden önce **birinci çağrının gerçekten
yazdığı** ölçülüyor, sonra ikincisi soruluyor.

**On birincisi ilk koşuda çıktı.** *Her istek yalnız kendi karesini taşır* testi bir `for` döngüsü
— ve araç yokken `writer.asked` boş, yani döngü hiç dönmüyor ve test hiçbir şey iddia etmeden
geçiyor. Döngünün önüne **iki istek olduğunun** ölçümü kondu.

## Bilerek yeşil olan tek test

*Tek kareli araç düzeltme için yerinde duruyor.* Bugün de doğru, yarın da doğru olmalı — ölçtüğü
şey bir değişiklik değil, **değişmemesi gereken bir şey**. 183'te aynı durum vardı ve orada da
kayda geçmişti: kırmızı vermeyen bir test de gerekli olabilir, gerekliliği ölçtüğü şeyden gelir.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` **16 kırmızı** verdi: on üçü aracın
kendisi, üçü skill metninin. Öteki üç takım kımıldamadı — **589 · 739 · 591.**
