# Biten koşunun raporu yenilemeyi aşmasın: TEST döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3` · **Döngü:** 1/2
**Bu döngüde kod yazılmıyor** — yalnız testler, ve takım kırmızı commit'leniyor.

## Ne oldu

Motor bir koşu bitince son durumu bellekte tutuyor ve `/api/status` onu **sonsuza dek** aynı cevapla
veriyor: yeni bir koşu başlayana kadar "Kuyruk tamamlandı — 20 kare üretildi" her yenilemede, her
sekmede geri geliyor. Kullanıcı 2026-08-14'te bunu şöyle yaşadı: ses eklemeye çalıştı, hiçbir şey
olmadı, ve yerine bir önceki **fotoğraf** turunun başarı mesajı belirdi.

## Hangi davranış doğru sayılacak

**Rapor, o sayfanın izlediği bir koşuya aittir.** Sayfa açıldığında durum zaten bitmişse (`done`) ya
da durmuşsa (`error`), o koşunun raporu çizilmez — sayfa onu görmedi. Koşu sayfa açıkken biterse
çizilir.

**Sunucu doğruyu söylemeye devam eder.** Durum bellekte kalır: ikinci bir sekme koşuyu izliyor
olabilir, ve "Kaldığı yerden devam et" ile hata metni ona bağlı. Değişen tek şey, **bu sayfanın** o
cevabı nasıl okuduğu.

**Borç ve düğmeler her hâlde kalır.** Bekleyen işler, "Kaldığı yerden devam et" ve "N kare
üretilemedi" kartı diskte yazılı gerçekler — geçmiş bir koşunun haberi değil. Raporun gitmesi
onları götürmez: bekleyen iş varsa panel yine duraklamış bir kuyruk gösterir ve devam düğmesini
verir.

**Kural, "koşan bir durum görmüş olmak".** Sayfa açıldığından beri en az bir kez bitmemiş bir durum
(`running`, `idle`, `paused`, `waiting`) görülmüşse, ondan sonraki her rapor bu sayfanındır. Hiç
görülmediyse eldeki rapor bir öncekinden kalmadır.

Bu kural dört durumu da doğru veriyor: koşarken açılan sayfa raporu görür · bitmişken açılan görmez ·
bitmişken açılıp yeni koşu başlatan yeni raporu görür · duran koşuyu devam ettiren sonraki hatayı
görür.

## Yazılacak testler

### `useGeneration.test.jsx` — kararın yaşadığı yer

1. **Bitmiş bir koşuyla açılan sayfaya ondan söz edilmiyor.** İlk yoklama `done` dönüyor; kancanın
   verdiği durum `idle`.
2. **Durmuş bir koşuyla açılan sayfaya da söz edilmiyor.** İlk yoklama `error` dönüyor; durum `idle`
   ve hata metni yok.
3. **Sayfa izlerken biten koşu raporlanıyor.** Önce `running`, sonra `done`; durum `done` ve sayısı
   yerinde.
4. **Sayfa izlerken duran koşu sebebini koruyor.** Önce `running`, sonra `error`; durum `error` ve
   sunucunun cümlesi duruyor.
5. **Kimsenin izlemediği rapor, borcu götürmüyor.** Bitmiş durumla açılan sayfada kareler hâlâ video
   borçluysa kuyruk onu saymaya devam ediyor. Bekçi.

### `ProjectScreen.test.jsx` — ekranda ne görünüyor

6. **Bitmiş bir koşuyla açılan ekran "Kuyruk tamamlandı" demiyor.** Panelde bunun yerine boş kuyruk
   cümlesi var. Kullanıcının gördüğü şeyin testi.

## Kırmızı ne olacak

1, 2 ve 6 kırmızı — bugün sunucunun cevabı olduğu gibi geçiyor. 3, 4 ve 5 yeşil: üçü de bugünkü
doğru davranışı kilitliyor, ve düzeltme onları bozmamalı.

## Kapsam dışı

- **Motorun durumu unutması.** Sunucu bellekte tutmaya devam ediyor; bu bir ön yüz kararı.
- **`waiting` durumu.** O bir rapor değil, yaşayan bir hâl: kuyruk hâlâ o üreticiyi bekliyor.
- **Raporun kendiliğinden solması.** İstenmedi.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` üç düşen test veriyor; geri kalan takım yeşil. Commit
kırmızı gidiyor ve mesajı bunu söylüyor.
