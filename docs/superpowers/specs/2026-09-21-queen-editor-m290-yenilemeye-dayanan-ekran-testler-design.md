# Madde 290 · Ekran açılışta koşan export'u görecek — test turunun tasarımı

**Tarih:** 2026-09-21 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

**Alındı.** Tek soru vardı — açılışta bitmiş bir koşu da görünsün mü — ve kullanıcı cevapladı
*(21 Eylül — "zaten önceden bittiyse gösterme, gerek yok ona; devam ediyorsa göster çünkü butonu
kullanamıyoruz")*.

## Bugünkü durum, koddan

Ekran export durumunu **yalnız düğmeye basıldıktan sonra** öğreniyor:

- `runs` boş başlıyor *(`useState({})`)*.
- Yoklama `going` doğruyken kuruluyor
  *([ExportScreen.jsx:112](../../../queen-editor/frontend/src/features/photo_generation/ExportScreen.jsx#L112))*.
- `going` ise `runs`'tan doğuyor, ve `runs`'a ilk yazan şey **basışın iyimser satırı**.

Yani zincirin başlangıcı basış. Sayfa yenilenince `runs` sıfırlanıyor ve o zincir bir daha
kurulmuyor — **ekran koşan export'a kör kalıyor**.

**Kullanıcının gördüğü** *(21 Eylül, Colab)*: düğmeler boştaymış gibi, adım süreleri yok, ve tekrar
basınca sunucunun 409'u *"Export başarısız"* kırmızı kartıyla çıkıyor. **Export düşmedi**; 409 tam
tersini söylüyor — *"bu export zaten sürüyor"*
*([routes.py:243](../../../queen-editor/backend/features/photo_generation/presentation/routes.py#L243))*.

## Kural: açılışta sorulur, ve yalnız koşan benimsenir

Ekran açılırken durumu bir kez soruyor. Gelen cevaptan **yalnız meşgul modlar** alınıyor; `done`,
`error` ve `idle` görmezden geliniyor.

**Kullanıcının gerekçesi maddenin sınırını da çiziyor:** *"butonu kullanamıyoruz"*. Ekranın
açılışta bir şey söylemesinin sebebi düğmenin ölü olması; bitmiş bir koşuda düğme çalışıyor, yani
söylenecek bir şey yok. Durum sunucuda oturum boyunca duruyor — bitmişi de benimsemek, bir saat
önce biten bir export'un yeşil kartını her açılışta göstermek olurdu.

**Ve bu kural bir yarışı da kapatıyor**, bedavaya: açılışta başlayan sorunun cevabı, kullanıcı
düğmeye bastıktan **sonra** dönebilir. Cevap `idle` taşıyorsa benimsenmiyor, yani basışın iyimser
satırını silemiyor. Meşgul taşıyorsa zaten doğruyu taşıyor.

## Çivilenen olgular

**1 · Açılışta durum bir kez soruluyor.** Hiçbir düğmeye basılmadan `getExportState` çağrılıyor.

**2 · Koşan export benimseniyor.** Sunucu *"birleşik export `merging`, biten adımları şunlar"*
diyorsa, ekran **basmadan** düğmede *"Disclaimer ekleniyor…"* gösteriyor, düğme basılamıyor, ve
biten adımların süreleri ekranda duruyor.

**3 · Bitmiş koşu benimsenmiyor.** Sunucu `done` diyorsa yeşil kart çıkmıyor ve düğme basılabilir
kalıyor.

**4 · Hata vermiş koşu benimsenmiyor.** Sunucu `error` diyorsa kırmızı kart çıkmıyor.

## Yoklama neden ayrıca çivilenmiyor

Yoklama `going`'e bakıyor, `going` de düğmenin ölü olmasıyla **aynı yerden** çıkıyor: `busy(run)`.
2. olgu onu zaten kanıtlıyor. Sahte saatle kurulacak ayrı bir test, kendi kuralımızı değil
React'in efekt kurmasını sınardı *(FOUNDATION 3)*.

## Ayarlanan testler

Bugün *"koşarken ekran ne diyor"* sorusunu soran testler o duruma **düğmeye basarak** geliyor —
çünkü basmaktan başka yolu yoktu. Bu maddeden sonra `open()` tek başına yetiyor, ve basış artık
**imkânsız**: düğmenin yazısı adımın cümlesine döndüğü için eski etiket ekranda kalmıyor.

O yüzden altı test **ayarlanıyor, silinmiyor** — soruları aynı, yalnız duruma geliş yolları
kısalıyor. Bu, maddenin kendi kazancının testlerdeki yüzü: koşan bir export'u görmek için artık
bir şey yapmak gerekmiyor.

## Kapsam dışı, ve bilerek

**409'un *"Export başarısız"* etiketi.** Kullanıcının sözü açık: *"sadece şunu çöz"*. Düğme
basılamaz hâle geldiği için o kart pratikte çıkmıyor; etiketin kendisi bir gün iki sekme açık
kalırsa yine yanlış olur, ve o gün kendi maddesi olur.
