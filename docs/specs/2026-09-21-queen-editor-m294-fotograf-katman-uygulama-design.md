# Madde 294 — Fotoğraf da silinebilir bir katman, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m294 test turu](2026-09-21-queen-editor-m294-fotograf-katman-testler-design.md),
`a4748173` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## İki dosya

**1. `domain/usecases/list_frames.py` — kartı kim açar.**

Madde 292 *"planda o kimlikle görünen ilk iş"* dedi. Bu madde bir sıfat ekliyor: **yuvası hâlâ
kapanmamış** ilk iş. Kapanmış bir katman *(`deleted`, `removed`)* kart adına konuşamaz.

Bugün iki ayrı yerde yapılan iki iş tek yere iniyor: *"kartı hangi iş açıyor"* ve *"kart galeride mi"*
aynı soru oluyor. Bugünkü kod önce açan işi buluyor, sonra onun durumuna bakıp kartı eliyor; artık
**kapanmış işleri atlayarak** açan işi arıyor, ve hiçbiri kalmamışsa kart zaten yok. *"Boş kutu
yaşamaz"* ayrı bir kontrol olarak yazılmıyor — aynı cümlenin diğer ucu.

`file` alanı fotoğraf yuvasını yalnız **duruyorken** okur: `layers.is_taken` süzgeci eklenir. Zaten
`layers` sözlüğü *(`_taken_files`)* aynı süzgeçten geçiyor; fark, `file`'ın onu atlamış olmasıydı.

**1b. Aynı dosyanın ikinci döngüsü.** Plan yazarken görülmeyen bir şey kapı açılınca çıktı: bir
kopya kartın taşıdığı katmanların **planda işi yoktur** — `copy_frame` onları doğrudan kayda yazar,
ve yalnız üretilecek katmanın plan satırı vardır. O tek iş silinince kart plan tarafından hiç
açılmaz; bugüne kadar galeride kalmasını sağlayan şey, ikinci döngünün *"planın bilmediği
fotoğraflar"* kuralıydı — yani **fotoğrafı** olan kopyalar kalıyor, yalnız videosu kalanlar
kayboluyordu.

Kural *"son katman gidince kutu gider"* olduğuna göre ikinci döngü de aynı cümleye bağlanır:
**planın açmadığı ama hâlâ bir katman tutan** her kart çizilir. Fotoğraf satırı olanlar bugünkü
sıralarını ve alanlarını korur — liste önce `record.list`'ten, sonra kaydın kalanından yürünür.

İki döngünün gövdesi aynılaştığı için tek bir `card()` yardımcısına iner; aralarındaki fark üçe
düşer: satırın kaynağı *(plan işi ya da kayıt satırı)*, prompt'un hangi katmana yazılacağı, ve durum.

**2. `presentation/routes.py` — kapı.** `REMOVABLE` fotoğrafı da alır. Yanındaki yorum, kuralı değil
**ekranın** bugün ne sunduğunu anlatacak şekilde düzeltilir.

## Değişmeyenler

- **`QUEUEABLE`.** Fotoğraf hâlâ katman olarak kuyruğa verilemiyor: fotoğraf kendi promptlarıyla
  istenir, var olan bir karta asılmaz. Bu maddenin konusu silme.
- **`remove_frames`.** Kartın tamamını silmek hâlâ kendi kullanım senaryosu. Fotoğrafı silmek kartı
  silmenin *yerine geçmiyor*; yan yana duruyorlar.
- **Ekran.** Fotoğraf silme düğmesi eklenmiyor.
- **Planın bilmediği fotoğraflar** *(ikinci döngü)* olduğu gibi duruyor.

## Bitti sayılır

Dört satırın dördü de koşulur; `queen-editor` yeşil — turun beş kırmızısı döner ve 964 testin hiçbiri
düşmez.
