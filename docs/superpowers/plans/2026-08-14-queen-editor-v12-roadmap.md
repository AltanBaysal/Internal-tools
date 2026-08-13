# Queen Editor — Yol Haritası v12

**Tarih:** 2026-08-14 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 0/2
**Öncesi:** [v11](2026-08-13-queen-editor-v11-roadmap.md) — kapandı. Bu koşu onun Colab turundan
çıktı.

## Neden bu koşu var

Kullanıcı v11'i Colab'da çalıştırdı. Tur v11'in düzeltmelerini ekrana getirdi ve iki yeni şey
çıkardı.

**Ses hiç üretilemiyor.** Kuyruk bir ses işini tohumsuz planlıyor — ses işinin kendi tohumu yok,
çünkü kullanıcıya sorulan bir şey değil. Fotoğraf işleri bu duruma hiç düşmüyor (her fotoğrafın
kendi tohumu var), video tohumsuzluğu kaldırıyor, ses kaldırmıyor: ilk karede patlıyor —
*"manual_seed expected a long, but got NoneType"*. Aynı kare üç kez denendikten sonra üretim
duruyor. Yani ses üreticisi kurulu olsa bile bugün tek bir ses çıkmıyor.

**Kareler sürüklenip sıralanamıyor.** v11 galerinin sürükleme kodunun tek satırına dokunmadı — yani
bu kırılma ya v11'den eski, ya da galerinin dışında bir yerde. Nerede olduğu görevin kendi spec'inde
çıkacak.

İkisi de yine **dikişte**. Ses için: tohumun plandan üreticiye giden yolunu uçtan uca izleyen bir
test yok, her parça kendi girdisiyle ayrı ayrı sınanmış. Sürükleme için: testler sürüklemenin
başladığını varsayıp devamını sınıyor — *başlayıp başlamadığını* soran bir test yok. Bulunan her
hatanın aynı yerden çıkması tesadüf değil, o yüzden çalışma biçimi v11'deki gibi kalıyor.

## Nasıl çalışacağız

**Her görev iki döngü.** Önce yalnız testler: spec → plan → testleri yaz → commit. O commit takımı
**kırmızı bırakır** ve mesajı hangi testlerin neden düştüğünü söyler. Sonra implementasyon: spec →
plan → kodu yaz → commit; takım yeşile döner.

Sebebi: testi kodla aynı nefeste yazınca test kodun zihin modelini miras alıyor ve aynı körlüğü
taşıyor. Araya commit sınırı koymak testi davranıştan yazmaya zorluyor.

**İstisna yok.** Ön yüz değişen her görevde `dist/` implementasyon commit'ine girer. Kullanıcı en
sonda toplu Colab testi yapar; koşu boyunca durulmaz.

## Kapsam sınırı

- **Karar bekleyen iki tasarım işi dışarıda:** galeri karolarına küçük önizleme, başarısız karede
  hover karartması. İkisi de kendi tasarımını ister.
- **Bu koşu sesin patlamamasını sağlar, kulağa nasıl geldiğini değil.** Üretilen sesin kalitesi ve
  üreticinin gerçekten kurulu olduğu ancak bir Colab turuyla görülür.

## Görevler

### Görev 1 · Tohumsuz bir iş üretimi durdurmuyor

**Ne olacak:** Ses işleri tohumsuz planlanıyor ve ses üreticisi tohumsuz bir işi kaldıramıyor —
ilk karede patlayıp bütün kuyruğu durduruyor. Tohumsuz bir iş artık üretimi durdurmayacak; ses
işinin tohumu nereden gelecek — hiç gelmeyecek mi, plan mı verecek, üretici mi seçecek — görevin
kendi spec'inde kararlaşacak. Tohumun plandan üreticiye gidişi üç katman için de uçtan uca
sınanacak; bugün eksik olan tam olarak o yol.

**Bağımlılık:** Yok.

**Bitti sayılır:** Kuyruğa atılan bir ses işi baştan sona geçiyor, ve tohumsuz bir iş hiçbir
katmanda üretimi durdurmuyor.

### Görev 2 · Kareler yeniden sürüklenebiliyor

**Ne olacak:** Galeride kare sürükleyip sıra değiştirmek çalışmıyor. Çalışır hâle gelecek. Kırığın
tarayıcının sürüklemeyi hiç başlatmamasından mı, yoksa bırakılan sıranın kaydedilmemesinden mi
geldiği görevin kendi spec'inde çıkacak — test davranışı yazacağı için ikisinde de aynı test
geçerli.

**Bağımlılık:** Yok.

**Bitti sayılır:** Bir kare sürüklenip başka bir karenin yerine bırakıldığında yeni sırada kalıyor,
sayfa yenilendiğinde de orada duruyor.

## Sonraki koşuya kalanlar

Galeri karolarının küçük önizlemeleri ve başarısız karede hover karartması — ikisi de tasarım kararı
bekliyor. Bir de bu koşuyu kapatacak Colab turundan çıkacak yeni maddeler.
