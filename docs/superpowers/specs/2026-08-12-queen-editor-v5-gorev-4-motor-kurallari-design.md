# Queen Editor v5 · Görev 4 — Motor kuralları: duraklatma ve deneme

**Tarih:** 2026-08-12 · **Yol haritası:**
[v5 Görev 4](../plans/2026-08-12-queen-editor-v5-roadmap.md) · **Kapsadığı maddeler:** 44, 45 ·
**Katman:** yalnız arka uç

## Amaç

Zeminin son iki kuralı, ikisi de kullanıcı kararı:

- **Duraklat çalışan işi keser ve yarım işi kuyruğa iade eder** — sayı 7'den 8'e çıkar
  *(karar 44)*. Bekleyen sayısı çalışan işi hiç saymaz.
- **Aynı iş üç kez hata verince kırmızıya döner** *(karar 45)* — bugün üretici "bu kare düştü"
  dediği anda tek denemeyle kırmızı oluyor.

## Kapsam

**İçinde:** bekleyen sayısının çalışan işi dışlaması; çalışan karenin adının kimlikten kurulması;
duraklatmanın yarım işi borçta bırakması; üç deneme kuralının **her** başarısızlık türüne
uygulanması.

**Dışında:** kuyruk panelinin görünümü ve büyük sayının rengi (Görev 9-10); "Hepsini tekrar dene"
(Görev 10).

---

## 1 · Bekleyen sayısı çalışan işi saymaz

Bugün sayı galeri listesinden çıkıyor: `pending` durumlu kareler sayılıyor. Üretilmekte olan
karenin **diskte satırı yok** — olmaması bilinçli, ölü bir süreç "çalışıyor" bırakmamalı — dolayısıyla
o da `pending` görünüyor ve sayıya giriyor. 8 yazarken gerçekte 7'si bekliyor, biri üretiliyor.

Düzeltme çıkarma işlemidir: **çalışan iş bekleyenlerden düşülür.** Hangi işin çalıştığı kararı
sunucunundur ve zaten yayınlanıyor (`/api/status` → `current`); ekran o kararı okuyup listesinden
çıkarıyor. Kural yer değiştirmiyor, yalnız sayım doğruluyor.

Duraklatınca `current` boşalıyor ve yarım iş borçta olduğu için sayı kendiliğinden bir artıyor —
tasarımın istediği 7 → 8 tam olarak bu.

**Bununla birlikte kapanan bir regresyon.** Ekran çalışan karenin dosya adını hâlâ eski şemadan
kuruyor (`sayı_harf.png`); Görev 2 kareyi kimliğe geçirdiği için o ad artık üretilemiyor ve
üretilen kare galeride "çalışıyor" diye işaretlenemiyor. Ad artık işin **kimliğinden** kuruluyor.
Bu, Görev 2'nin arka uçta bıraktığı ve testlerin göremediği tek açık uçtu.

## 2 · Duraklatma yarım işi iade eder

Kural zaten böyle kurulmuştu ve bu görevde **açıkça sınanıyor**: duraklatma sırasında kesilen iş
günlüğe satır yazmaz, dolayısıyla açık kalır ve devam edilince baştan yapılır.

Sayının 7'den 8'e çıkması bunun görünen yüzü: çalışan iş sayıdan düşülmüşken (7), duraklatma onu
tekrar bekleyenlerin arasına koyar (8).

**Yarım dosya bırakılmaz.** Kesilen iş dosyasını yazmadan biter; dosya ancak üretim tamamlandığında
yazılır ve satır ondan sonra gelir — bugünkü sıra.

## 3 · Üç deneme her başarısızlığa uygulanır

Bugün iki yol var:

| Başarısızlık | Bugün | Yarın |
|---|---|---|
| Üretici "bu iş düştü" dedi | **tek denemede** kırmızı | üç deneme, sonra kırmızı |
| Cevap hiç gelmedi | üç deneme, sonra **koşu durur** | değişmedi |

Yani ayrım kalkmıyor — kaç deneme hakkı olduğu eşitleniyor. İkisi de aynı işi üç kez deniyor;
farkları **üçüncüden sonra ne olduğu**: işin kendi hatası kareyi kırmızıya döndürüp kuyruğu
sürdürüyor, cevapsızlık koşuyu durduruyor.

**Neden ayrım kalıyor.** Cevapsızlık kuyruğun tamamını ilgilendirir — sunucu ölmüşse sıradaki iş de
düşer, o yüzden durmak doğrudur. İşin kendi hatası yalnız o işi ilgilendirir; kuyruğu durdurmak
kullanıcının öteki işlerini rehin almak olur.

**Denemeler diske yazılmaz.** Sayaç işçinin hafızasında durur: ölü bir süreç deneme sayısı
bırakmamalı ve yeniden başlatılan bir koşu üç taze hak etmeli — bugünkü kural, aynen.

## 4 · Testler

**Full TDD**, arka uç `pytest`.

**Bekleyen sayısı**
- Üretim sürerken kuyruk uç noktası çalışan işi bekleyenlerden düşer.
- Duraklatınca sayı bir artar — yarım iş borçta.
- Kuyruk boşken sayı sıfırdır.

**Duraklatma**
- Kesilen iş günlüğe satır yazmaz ve açık kalır.
- Devam edilince aynı iş yeniden yapılır.

**Üç deneme**
- Üreticinin "bu iş düştü" cevabı ilk iki denemede kırmızı yazmaz.
- Üçüncüden sonra kırmızı satır yazılır ve kuyruk sıradaki işe geçer.
- Araya giren başarı sayacı sıfırlar (bugünkü kural korunur).
- Cevapsızlıkta davranış değişmez: üç denemeden sonra koşu durur ve iş satırsız kalır.
- Her iş kendi üç hakkını alır.

## 5 · Kabul kriteri

`pytest` yeşil ve şu iki cümle testlerle kanıtlanmış:

1. Üretim sürerken bekleyen sayısı çalışan işi saymıyor; duraklatınca bir artıyor.
2. Üreticinin düşürdüğü bir iş ancak üçüncü denemeden sonra kırmızıya dönüyor.
