# Queen Editor — Yol Haritası v5

**Tarih:** 2026-09-11 · **Koşu dalı:** `feat/queen-editor-v5` · **Durum:** 0/7
**Öncesi:** [20 Ağustos'ta v14 adıyla kapanan koşu](2026-08-20-queen-editor-v14-roadmap.md) — neden o
adın yanlış olduğu 210. maddenin konusu.
**Kaynak:** 211–214 [queen-editor/BACKLOG.md](../../../queen-editor/BACKLOG.md)'dan çıkıp buraya
girdi ve orada kalmadı; artık tek kayıtları bu belge. 210, 215 ve 216 kullanıcının 11 Eylül'deki
sözlerinden doğdu, backlog'a hiç uğramadan.

**Numara kimliktir, sıra değildir.** 215 ve 216 en son doğdu ama 213'ün önünde duruyorlar: önce üç
hata — 211, 212, 215 — sonra ekranda bir varsayılan, en sonda kararı verilmemiş iki yeni iş.
Koşulacak sıra bu tablonun sırasıdır.

## Neden bu koşu v5

**queen-editor v4'te.** Dal sayacı budur ve doğru olan odur: `git branch -a` queen-editor için yalnız
`feat/queen-editor-v1`, `v2`, `v3`, `v4` gösteriyor. v5'ten v14'e kadar anılan on koşu **kendi dalını
hiç açmadı** — hepsi `feat/queen-editor-v4` üstünde koştu, ve o dal `e87f372` ile 25 Ağustos'ta
main'e girdi.

Kural depoda zaten işliyordu, yalnız queen-editor'de kaymıştı: **bir v bir daldır**, dal test edilir
ve main'e girer. QueenAgent tarafında hiç kaymamış — `feat/queenagent-v5`, `v7`, `v7.5`, `v8` dalları
belgeleriyle birebir tutuyor, merge commit'leri de (`25ad6b7 merge(v7)`, `356d605 merge(v8)`) öyle.

Bu koşu v4'ün ardından açılan **ilk yeni dal**, yani v5.

**QueenAgent'ın v sayacı ayrıdır** *(kullanıcı kararı, 11 Eylül)*. QueenAgent v8'de, queen-editor v5;
iki tool aynı v numarasını paylaşmaz.

**Madde numarası depo sayacından geliyor.** Sayaç 209'da ve v5'ten (QueenAgent, 25 Ağustos) beri depo
geneli. Sebep, yazılmış spec'lerin madde numarasına atıf yapması: sayacı ikiye bölmek aynı numaranın
iki farklı işi göstermesi demek olurdu.

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 210 | **Queen-editor'ün sürüm karmaşasının çözülmesi.** Bugün on belge kendini v5–v14 diye adlandırıyor ama hiçbirinin dalı olmadı; queen-editor v4'ten v5'e geçiyor. Düzeltmenin **dosya adlarını değiştirmemesi** koşul: yazılmış spec'ler ve görev planları bu adlara atıf yapıyor, ve bir kopya ada dokunmak yüzlerce bağlantıyı kırar. Kayıt, adları yerinde bırakıp neyin ne olduğunu söyleyerek düzeltilir. Aynı düzeltmeye v14 belgesinin kapanmamış sayacı da girer: başlığı 36/37 diyor ve 30. maddesi *(Colab turu)* işaretsiz, oysa dal 25 Ağustos'ta main'e girdi. | Queen-editor'ün hangi sürümde olduğu tek bir yerden okunuyor, o yer v4'ün ardından v5 geldiğini söylüyor, ve eski on belgeden herhangi birine düşen biri hangi dalda koştuğunu görüyor. Hiçbir dosya adı değişmemiş. |
| 211 | **Silinen standart videodan sonra loop eklenince ikisi birden üretiliyor gibi görünüyor.** *(Kullanıcı bildirimi, 6 Eylül.)* Kareye standart video eklendi → silindi → yerine loop video eklendi. Ekranda **ikisi birden** üretiliyormuş gibi görünüyor, standart ve loop yan yana. Sebebi **araştırılmadı**, ve buraya bir tahmin yazılmıyor: silinen işin gerçekten iptal edilmemesi de olabilir, yalnız ön yüzün eski satırı bırakması da. İkisi çok farklı yerlerde durur. **Ele alınırken kullanıcıya sorulacak:** silinen video gerçekten üretilmiş miydi yoksa sırada mıydı, ekranda kaç satır göründü, ve dışa aktarmaya hangisi düştü — yani hata yalnız görüntüde mi, yoksa diske de mi ulaşıyor. | Aynı sıra tekrarlanıyor — standart eklenip siliniyor, yerine loop ekleniyor — ve karede tek satır kalıyor; dışa aktarmaya da tek video düşüyor. |
| 212 | **Oynatma düğmesi video oynarken üstünde duruyor.** *(Kullanıcı bildirimi, 6 Eylül.)* Video başlayınca başlat/durdur düğmesi kaybolmuyor, görüntünün **üzerinde kalıyor** ve karenin bir kısmını örtüyor. | Video oynarken düğme görüntünün üstünde değil, kare tamamen görünüyor; video durunca düğme geri geliyor. |
| 215 | **Başka projeye geçip üretmeye basınca çıkan hata düzgün konuşmuyor.** *(Kullanıcı, 11 Eylül.)* Bir projede üretim başlatılıyor, oradan çıkılıp başka bir projeye giriliyor ve orada üretme basılıyor — **hata veriyor, ama mesaj düzgün değil.** Hatanın kendisi bu maddenin konusu değil; **söylediği şey** konusu. Sebebi **araştırılmadı** ve buraya bir tahmin yazılmıyor: ilk iş, o anda sunucunun gerçekte ne döndürdüğünü görmek. Uydurulmuş bir sebep ekrana yazılmayacak — duran cümle, gerçekten olanı söyleyecek. | Aynı sıra tekrarlanıyor ve ekranda çıkan cümle ne olduğunu söylüyor: kullanıcı onu okuyup ne yapacağını biliyor, ve cümle sunucunun gerçekten döndürdüğüyle çelişmiyor. |
| 216 | **Video üretiminde varsayılan mod Loop olur.** *(Kullanıcı, 11 Eylül.)* Video panelindeki Üretim modu seçicisi bugün **Standart** ile açılıyor; bundan sonra **Loop** ile açılacak. Yalnız varsayılan değişiyor: üç seçenek de yerinde kalıyor, ses panelinde seçici zaten doğmuyor, ve detay sayfasındaki *Yeni mod* kutusu **değişmiyor** — onun varsayılanı o videonun kendi modu olmaya devam ediyor, çünkü orası yeni bir iş değil var olan bir videoyu yeniden üretiyor. Butonun altındaki tahmin ve eklendikten sonraki onay cümlesi zaten moda göre konuşuyor, yani kendiliğinden loop'u söyler. | Video paneli ilk açıldığında seçicide Loop yazıyor, ve hiçbir şeye dokunmadan kuyruğa eklenen video işi loop modunda kaydedilip loop olarak üretiliyor. |
| 213 | **MiniMax eklenecek.** *(Kullanıcı, 6 Eylül.)* Hangi işi alacağı — fotoğraf mı video mu, bugünkü tarifin yerine mi yanına mı — **kararlaşmadı.** Karar maddenin kendi turunda verilir ve buraya yazılır; kod ondan sonra yazılır. | Karar yazıya geçmiş, ve MiniMax kendisine verilen işte üretim yapıyor: kuyruğa giren bir iş onunla bitiyor ve çıkan dosya karesine iniyor. |
| 214 | **Slime girl videosu eklenecek.** *(Kullanıcı, 6 Eylül.)* Bir video türü — *slime girl*. Bir model değil, üretilecek bir içerik biçimi. **Kararlaşmadı:** kendi LoRA'sıyla mı geliyor, kendi üretim tarifiyle mi, yoksa yalnız prompt tarafında mı kalıyor. | Karar yazıya geçmiş, ve o yolla üretilmiş bir slime girl videosunu kullanıcı görmüş. |

**213 ve 214'ün yargısı koda bakarak verilemiyor.** İkisi de üretilmiş bir çıktı istiyor, queen-editor
de yerelde koşmuyor: defteri kullanıcı çalıştırıyor ve sonucu kullanıcı görüyor.
