# Queen Editor — Yol Haritası v6

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queen-editor-v6` · **Durum:** 4/4
**Öncesi:** [v5](2026-09-11-queen-editor-v5-roadmap.md) — 36/36 kapandı ve `497b0a3e` ile main'e
birleşti.
**Kaynak:** İki madde de kullanıcının 21 Eylül'deki sözlerinden doğdu, backlog'a hiç uğramadan.
[BACKLOG.md](../../../queen-editor/BACKLOG.md)'deki işler yerinde duruyor: bu koşu küçük
*(kullanıcı — "v6 küçük bir koşu olucak", "bu kadar")*.

**Neden v6.** Dal sayacı: `git branch -a` queen-editor için `v1`–`v5` gösteriyor ve beşi de main'e
girmiş, sonuncusu 20 Eylül'de. Sıradaki dal `feat/queen-editor-v6` — bu belgenin başlığında yazan
dal.

**Numara kimliktir, sıra değildir.** 248 v5'in son maddesiydi; bu koşu 249'dan başlıyor.

**Sıra bağımlılığa göre: 249, 250, 251.** 249 ile 250 aynı bindirmeyi istiyor ama aynı saati
istemiyor: tekli export süreyi videonun kendi başından sayıyor, birleşik export birleşmiş zaman
çizgisinden. 249 bindirmeyi kuruyor, 250 yalnız saatini değiştiriyor — bindirme yokken sayılacak bir
şey de yok. **251 sonradan geldi** *(kullanıcı, 21 Eylül, 249'un ortasında — "hatta workflowları da
oraya koyabilirsin")* ve sona kondu: kimseyi beklemiyor, ama 249'un açtığı klasörün var olmasını
bekliyor. **252, 251'in yolunda çıktı** ve sona girdi — defterin hangi dalı klonladığı 251'in defter
hücresine dokunurken görüldü. En sonda olması yerinde: kullanıcının koşu sonundaki testi ona bağlı,
ve öncesindeki maddelerin hepsinin commit'lenmiş olması gerekiyor.

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**Kullanıcıdan gereken tek şey disclaimer PNG'si**, ve o 249'un ilk turunun spec'inin başında
istenir — koşunun ortasında değil, başında. Dosya gelmeden kod başlamaz: PNG'nin kendi ölçüsü,
bindirmenin ekranda kapladığı yeri belirleyen şey.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 249 | ✅ **Tekli export'ta disclaimer.** *(Kullanıcı, 21 Eylül — "exportlara disclaimer eklenecek ... ben sana png olarak atıcam", "videonun başında ilk 1 dakika", "ekranın alt ortasında olacak".)* Sözü edilen düğme export ekranındaki **Videoları ayrı export et** *(`separate`)*; ekranda tam iki düğme var, başka bir video indirme yeri yok *(`ExportScreen.jsx`)*. **Bugün export videonun içine hiç dokunmuyor:** her kare kendi mp4'ü olarak yazılıyor ve akışlar kopyalanıyor — `piece()`, `-c copy` *(`data/ffmpeg_video_exporter.py`)*. **Olacak:** kullanıcının verdiği PNG videonun üstüne biniyor, **ekranın alt ortasında**, videonun **başından itibaren 60 saniye**. Bir karenin videosu grafiğin verdiği sabit uzunlukta — bugün ~5 saniye, ve uzunluk koddan değil grafikten geliyor *(`domain/usecases/export_summary.py`)* — yani 60 saniye pratikte videonun tamamını kaplıyor. Süre yine de **60 olarak yazılır**: grafiğin uzunluğu değişince kuralın değişmemesi için. **Duruşu, kullanıcıyla 21 Eylül'de align olundu:** PNG **videonun genişliğinin %80'i** olacak şekilde ölçeklenir *(sabit piksel değil: ölçü bu depoda bir kez değişti — 218 yatay yaptı, 228 dikeye döndürdü)*, alt kenardan **yüksekliğin %4'ü** kadar yukarıda durur *(dibe yapışan yazı telefonda oynatıcı çubuğunun altında kalıyor)*, ve **PNG'nin kendi saydamlığına dokunulmaz**. **Videoların hepsi taşır**, yalnız ilki değil: 22 dosyadan birinde duran disclaimer'ın orada durmasının anlamı kalmıyor. **Bedeli, ve kaçışı yok:** bindirme kopyalamayı bitiriyor, video yeniden kodlanıyor; export'un bugünkü saniyeler süren hızı buradan gidiyor. Kodlama ayarları spec'te seçilir. **Fotoğraflara dokunulmuyor:** export klasörüne videoların yanında çıkan fotoğraflar *(`domain/usecases/run_export.py`)* olduğu gibi kalıyor — istenen şey videonun başı. **Kullanıcıdan gereken** *(spec'in başında istenir)*: disclaimer PNG'si — **dikey kareye göre kesilmiş** hâli. İlk verilen dosya *(21 Eylül, `1902 × 98`)* bu iş için kullanılamadı: tek uzun bir şerit, ve 480 genişlikte %80'e ölçeklenince üst satırın ~100 karakteri 384 piksele giriyor, yani karakter başına ~3,8 piksel — o boyutta yazı okunmuyor, ve pikseller orada olmadığı için videoyu büyük ekranda açmak da kurtarmıyor. **Kullanıcı kararı, 21 Eylül:** aynı metin **4-5 satıra** bölünüp yaklaşık **960 × 300** verilecek *(480'in iki katı, küçültülünce net kalsın)*. Dosya **depoya commit'lenir** — defter depoyu klonluyor ve hiçbir şey build etmiyor; nereye ve hangi adla gireceği spec'in kararı. **Kapandı** *(`c87e6ebb` kırmızı, `746e4a1c` yeşil)*. **Yeniden kesim gelmedi:** kullanıcı aynı dosyayı kullandırdı *(21 Eylül — "abi dosya zaten group 5 png, o yani")*, yani disclaimer bugün alt ortada ince bir şerit ve yazısı okunmuyor. Bilerek bırakıldı, ve bedeli yok: resim koda girmiyor, `config.DISCLAIMER_PATH`'in gösterdiği dosya — 4-5 satırlık versiyon geldiğinde tek dosya değişiyor, hiçbir satır değişmiyor. Yeri de kullanıcının seçimi: `queen-editor/assets/disclaimer.png` *("queen editor altında asset diye klasör açıp koyabilirsin")* — 251 o klasörden doğdu. | Ayrı dosyalar olarak alınan bir export'tan çıkan mp4 açıldığında disclaimer ekranın alt ortasında duruyor; video kendi ölçüsünü ve üstündeki sesi kaybetmemiş. |
| 250 | ✅ **Birleşik export'ta disclaimer ilk 1 dakika.** *(Kullanıcı, 21 Eylül — "hem tekli exportlar için hem de birleşik exportta".)* **Bugün birleşik mod parçaları makinenin kendi diskinde kesiyor**, sonra `concat` ile **kopyalayarak** birleştiriyor — hiçbir kare yeniden kodlanmıyor *(madde 235; `merge()`)*. **Olacak:** disclaimer **birleşmiş dosyanın ilk 60 saniyesinde** duruyor, 60. saniyeden sonra görünmüyor. Saat parçanın değil **birleşmiş videonun** saati: her parça kendinden öncekilerin toplam süresini devralıyor, yani ~5 saniyelik karelerle ilk on iki kare bindirmeyi taşıyor, sonrakiler taşımıyor. **Sınır karesi, kullanıcıyla 21 Eylül'de align olundu:** disclaimer **tam 60. saniyede** kalkar, o kare ortasında da olsa *(kullanıcı — "bu önemli bir soru değil gibi 1 olsun")*. Bugünkü ~5 saniyelik karelerle 60 zaten on ikinci karenin bitişi; karar grafiğin uzunluğu değişince iş görecek. **Bir karar spec'e kalıyor:** yeniden kodlanmış parçalarla kopyalananların yan yana konmasının `concat`'in kopyalamasını bozup bozmayacağı. Yön belli: **kopyalama korunmaya çalışılır**, çünkü birleşik export'un hızını taşıyan şey o. **Kapandı** *(`ddaec988` kırmızı, `eefcab2e` yeşil)*, ve o risk hiç doğmadı: bindirme parçalara değil **birleştirmenin kendi çağrısına** bindi — `concat` girdisinin üstüne, aynı ffmpeg okumasında. Parçaların hepsi temiz kopya kaldı, kodlama birleşmiş akışın üstünde bir kez oldu, ve `t` birleşmiş videonun saati olduğu için 60. saniye kararı parça sınırına hiç bakmadan çalışıyor. **Yolda bir yalan düzeltildi:** ölçüler uyuşmadığında çıkan cümle *"birleştirme yeniden kodlamıyor"* diyordu — bu maddeyle kodluyor. Cümle artık gerçekten yanlış olanı söylüyor: tek dosyanın tek oranı olur, ve hangisinin istendiğini kimse söyleyemez. | Birleşik dosya açıldığında disclaimer ilk 60 saniyede ekranın alt ortasında duruyor, 60. saniyeden sonra görünmüyor, ve dosya baştan sona tek parça oynuyor. |

| 251 | ✅ **Grafikler de `assets/` altına girecek.** *(Kullanıcı, 21 Eylül, 249 koşarken — "hatta workflowları da oraya koyabilirsin".)* 249 disclaimer için `queen-editor/assets/` açtı; beş grafik JSON'u hâlâ `queen-editor/` kökünde duruyor — `workflow_api.json`, `workflow_video_api.json`, `workflow_video_first_last_api.json` ve iki H3 grafiği. **Olacak:** beşi de `assets/`'e taşınıyor. Yollarını söyleyen tek yer `config.py`'nin beş sabiti; onların dışında dosya adını **defterin bir hücresi** *(üçünü adıyla anıyor)* ve **üç test dosyası** taşıyor. **Bu madde davranışı hiç değiştirmiyor**, yani bitişini gösteren şey de ekranda bir şey değil: takımın yeşil kalması, ve kökte JSON kalmaması. | `queen-editor/` kökünde grafik JSON'u kalmamış, beşi `assets/` altında, dört satır yeşil, ve defterin grafikleri anan hücresi hâlâ duran dosyaları adlıyor. **Kapandı** *(`762fa021` kırmızı, `aae187d3` yeşil)*. `test_producer_contract.py` kendi üç yolunu bıraktı ve `config`'in sabitlerine geçti: taşımanın onu kırması, yolun neden tek evi olması gerektiğinin kanıtı. |

| 252 | ✅ **Defter koşulan dalı klonlayacak.** *(251'in yolunda çıktı, 21 Eylül.)* Defterin CONFIG hücresi `BRANCH = "feat/queen-editor-v5"` diyor, ve `test_notebook_clones_its_branch.py` aynı adı taşıyor — **ikisi de v5 koşusunun denemesinden kalmış**. O dosyanın kendi kuralı *"merge'den önce ikisi de `main`'e döner"* diyor; v5 merge'inde dönmemişler. **Sonucu bu koşuyu doğrudan vuruyor:** Colab depoyu klonluyor, yani defter bugün açılırsa v5'in ağacını indirir ve v6'nın üç maddesinin hiçbiri görünmez — kullanıcının koşu sonundaki testi yanlış kodu test eder. **Olacak:** iki yer birden `feat/queen-editor-v6` olur. **Ve borç yazıya geçer:** merge'den önce ikisi de `main`'e döner, bu maddenin satırında. | Defter ve testin sabiti aynı dalı söylüyor, o dal bu koşunun dalı, ve dört satır yeşil. **Kapandı** *(`f96765e3` kırmızı, `94b61baf` yeşil)*. Sabit v6'ya döndüğünde **iki test birden** düştü — ikincisi *"defterde başka dal adı kalmamış"*, çünkü defterdeki v5 o anda ikinci ad oldu; ikisi de defterin tek satırıyla yeşile döndü. **Ödenecek borç:** merge'den önce defterin `BRANCH` satırı ve `test_notebook_clones_its_branch.py`'nin sabiti birlikte `main`'e döner. |

---

**Koşu bitti, kullanıcının testi kaldı** *(döngünün 10. adımı)*. Dört madde de kapandı, takımın dört
satırı yeşil — queen-editor 925, ön yüzü 666, queen-agent 923 ve 652. Colab'da denenmeden bilinmeyen
tek şey **bindirmenin gerçek ffmpeg'de nasıl göründüğü ve export'u ne kadar yavaşlattığı**: testler
komutu okuyor, bu makinede ffmpeg yok, ve buraya bir tahmin yazılmıyor.

**Merge'den önce:** 252'nin satırındaki iki satır `main`'e döner.

**Bir sonraki koşu.** Kullanıcı v7'yi bu koşunun ardından birlikte yazacağını söyledi *(21 Eylül —
"sonra v7 yazıcaz senle bide")*. v7'nin maddeleri buraya girmiyor: bu koşuya sonradan iş eklenirse o
kendi numarasıyla bu tabloya girer, ikinci bir belge açılmaz.
