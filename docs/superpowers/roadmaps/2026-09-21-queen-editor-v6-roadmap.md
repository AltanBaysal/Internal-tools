# Queen Editor — Yol Haritası v6

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queen-editor-v6` · **Durum:** 0/2
**Öncesi:** [v5](2026-09-11-queen-editor-v5-roadmap.md) — 36/36 kapandı ve `497b0a3e` ile main'e
birleşti.
**Kaynak:** İki madde de kullanıcının 21 Eylül'deki sözlerinden doğdu, backlog'a hiç uğramadan.
[BACKLOG.md](../../../queen-editor/BACKLOG.md)'deki işler yerinde duruyor: bu koşu küçük
*(kullanıcı — "v6 küçük bir koşu olucak", "bu kadar")*.

**Neden v6.** Dal sayacı: `git branch -a` queen-editor için `v1`–`v5` gösteriyor ve beşi de main'e
girmiş, sonuncusu 20 Eylül'de. Sıradaki dal `feat/queen-editor-v6` — bu belgenin başlığında yazan
dal.

**Numara kimliktir, sıra değildir.** 248 v5'in son maddesiydi; bu koşu 249'dan başlıyor.

**Sıra bağımlılığa göre: 249, 250.** İkisi aynı bindirmeyi istiyor ama aynı saati istemiyor: tekli
export süreyi videonun kendi başından sayıyor, birleşik export birleşmiş zaman çizgisinden. 249
bindirmeyi kuruyor, 250 yalnız saatini değiştiriyor — bindirme yokken sayılacak bir şey de yok.

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**Kullanıcıdan gereken tek şey disclaimer PNG'si**, ve o 249'un ilk turunun spec'inin başında
istenir — koşunun ortasında değil, başında. Dosya gelmeden kod başlamaz: PNG'nin kendi ölçüsü,
bindirmenin ekranda kapladığı yeri belirleyen şey.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 249 | **Tekli export'ta disclaimer.** *(Kullanıcı, 21 Eylül — "exportlara disclaimer eklenecek ... ben sana png olarak atıcam", "videonun başında ilk 1 dakika", "ekranın alt ortasında olacak".)* Sözü edilen düğme export ekranındaki **Videoları ayrı export et** *(`separate`)*; ekranda tam iki düğme var, başka bir video indirme yeri yok *(`ExportScreen.jsx`)*. **Bugün export videonun içine hiç dokunmuyor:** her kare kendi mp4'ü olarak yazılıyor ve akışlar kopyalanıyor — `piece()`, `-c copy` *(`data/ffmpeg_video_exporter.py`)*. **Olacak:** kullanıcının verdiği PNG videonun üstüne biniyor, **ekranın alt ortasında**, videonun **başından itibaren 60 saniye**. Bir karenin videosu grafiğin verdiği sabit uzunlukta — bugün ~5 saniye, ve uzunluk koddan değil grafikten geliyor *(`domain/usecases/export_summary.py`)* — yani 60 saniye pratikte videonun tamamını kaplıyor. Süre yine de **60 olarak yazılır**: grafiğin uzunluğu değişince kuralın değişmemesi için. **Duruşu, kullanıcıyla 21 Eylül'de align olundu:** PNG **videonun genişliğinin %80'i** olacak şekilde ölçeklenir *(sabit piksel değil: ölçü bu depoda bir kez değişti — 218 yatay yaptı, 228 dikeye döndürdü)*, alt kenardan **yüksekliğin %4'ü** kadar yukarıda durur *(dibe yapışan yazı telefonda oynatıcı çubuğunun altında kalıyor)*, ve **PNG'nin kendi saydamlığına dokunulmaz**. **Videoların hepsi taşır**, yalnız ilki değil: 22 dosyadan birinde duran disclaimer'ın orada durmasının anlamı kalmıyor. **Bedeli, ve kaçışı yok:** bindirme kopyalamayı bitiriyor, video yeniden kodlanıyor; export'un bugünkü saniyeler süren hızı buradan gidiyor. Kodlama ayarları spec'te seçilir. **Fotoğraflara dokunulmuyor:** export klasörüne videoların yanında çıkan fotoğraflar *(`domain/usecases/run_export.py`)* olduğu gibi kalıyor — istenen şey videonun başı. **Kullanıcıdan gereken** *(spec'in başında istenir)*: disclaimer PNG'si — **dikey kareye göre kesilmiş** hâli. İlk verilen dosya *(21 Eylül, `1902 × 98`)* bu iş için kullanılamadı: tek uzun bir şerit, ve 480 genişlikte %80'e ölçeklenince üst satırın ~100 karakteri 384 piksele giriyor, yani karakter başına ~3,8 piksel — o boyutta yazı okunmuyor, ve pikseller orada olmadığı için videoyu büyük ekranda açmak da kurtarmıyor. **Kullanıcı kararı, 21 Eylül:** aynı metin **4-5 satıra** bölünüp yaklaşık **960 × 300** verilecek *(480'in iki katı, küçültülünce net kalsın)*. Dosya **depoya commit'lenir** — defter depoyu klonluyor ve hiçbir şey build etmiyor; nereye ve hangi adla gireceği spec'in kararı. | Ayrı dosyalar olarak alınan bir export'tan çıkan mp4 açıldığında disclaimer ekranın alt ortasında duruyor; video kendi ölçüsünü ve üstündeki sesi kaybetmemiş. |
| 250 | **Birleşik export'ta disclaimer ilk 1 dakika.** *(Kullanıcı, 21 Eylül — "hem tekli exportlar için hem de birleşik exportta".)* **Bugün birleşik mod parçaları makinenin kendi diskinde kesiyor**, sonra `concat` ile **kopyalayarak** birleştiriyor — hiçbir kare yeniden kodlanmıyor *(madde 235; `merge()`)*. **Olacak:** disclaimer **birleşmiş dosyanın ilk 60 saniyesinde** duruyor, 60. saniyeden sonra görünmüyor. Saat parçanın değil **birleşmiş videonun** saati: her parça kendinden öncekilerin toplam süresini devralıyor, yani ~5 saniyelik karelerle ilk on iki kare bindirmeyi taşıyor, sonrakiler taşımıyor. **Sınır karesi, kullanıcıyla 21 Eylül'de align olundu:** disclaimer **tam 60. saniyede** kalkar, o kare ortasında da olsa *(kullanıcı — "bu önemli bir soru değil gibi 1 olsun")*. Bugünkü ~5 saniyelik karelerle 60 zaten on ikinci karenin bitişi; karar grafiğin uzunluğu değişince iş görecek. **Bir karar spec'e kalıyor:** yeniden kodlanmış parçalarla kopyalananların yan yana konmasının `concat`'in kopyalamasını bozup bozmayacağı. Yön belli: **kopyalama korunmaya çalışılır**, çünkü birleşik export'un hızını taşıyan şey o. | Birleşik dosya açıldığında disclaimer ilk 60 saniyede ekranın alt ortasında duruyor, 60. saniyeden sonra görünmüyor, ve dosya baştan sona tek parça oynuyor. |

---

**Bir sonraki koşu.** Kullanıcı v7'yi bu koşunun ardından birlikte yazacağını söyledi *(21 Eylül —
"sonra v7 yazıcaz senle bide")*. v7'nin maddeleri buraya girmiyor: bu koşuya sonradan iş eklenirse o
kendi numarasıyla bu tabloya girer, ikinci bir belge açılmaz.
