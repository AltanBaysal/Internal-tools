# Madde 255 · Export ekranı disclaimer adımını söyleyecek — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Cümle kullanıcının kendi sözü: *"Disclaimer ekleniyor"*.

## Bugün ne var

Birleşik export koşarken düğme iki şey söylüyor: parçalar yazılırken `7 / 22 yazıldı…`, sonra
`birleştiriliyor…` *(`ExportScreen.jsx`)*. Kullanıcı o son cümlede **beş dakikadan fazla** bekledi.
Adım gerçekten iki iş yapıyor — parçaları birleştirmek ve disclaimer'ı bindirmek — ve **süreyi
yiyen ikincisi**: bindirme yeni bir görüntü, yani kodlama *(250)*, ve 259'dan sonra kodlanan çerçeve
`1920 × 1080`. Ekran bunun hiçbirini söylemiyor.

## Bu maddenin sınırı

**Yüzde yapılmıyor**, ve bu bilerek: GPU'dan sonraki süre ölçülmedi. Birleştirme 20 saniyeye
indiyse yüzdenin değeri kalmıyor; hâlâ dakikalarsa yüzde kendi maddesi olur. Ayrıca ucuz değil —
`subprocess.run` bitmesini bekliyor, yani exporter'ın ffmpeg'i bekleme biçimi değişirdi
*(araştırmanın K6'sı)*. Canlı nokta *(`qe-dot--alive`)* yerinde kalıyor: madde 93'ün kararı.

## Katman kararı

**Arka uca dokunulmuyor.** Adımın kendisi zaten arkadan geliyor — `run_export` birleştirmeden önce
`state="merging"` bildiriyor — ve o adın söylediği şey doğru: o adımda birleştirme de oluyor.
Değişen şey **ekranda ne yazdığı**, ve bir durumun karşılığında gösterilen cümle sunum işi
*(CODE-STANDARD — "formatting, what is enabled ... stay in the UI")*. FOUNDATION 4 tersini
istemiyor: tarayıcı burada bir kural hesaplamıyor, arkanın bildirdiği duruma bir cümle veriyor.

Yani bu madde **tek satır** ve tek dosya: `ExportScreen.jsx`. Ve ön yüz değiştiği için
`frontend/dist/` aynı commit'te yeniden build'leniyor *(FOUNDATION 3'ün sonucu)*.

## Çivilenen olgular

**1 · Birleşik adım kendi adıyla görünüyor.** `merged` durumu `merging` iken düğme
**`Disclaimer ekleniyor…`** yazıyor. Kullanıcının cümlesi birebir; büyük harfli `D` de onun
*(`"Disclaimer ekleniyor densin"`)*.

**2 · `birleştiriliyor…` ekranda kalmıyor.** İki cümle birden gösterilmiyor: düğmenin içinde tek
satır var, ve kullanıcı o satırın hangi iş olduğunu soruyordu.

**3 · O adım parça saymıyor.** `22 / 22 yazıldı…` o durumda ekranda yok — sayaç parçalar
yazılırken duran şey, ve adım değiştiğinde cümle de değişiyor.

**4 · Düğme o sırada yine basılamıyor.** `merging` hâlâ koşan bir durum *(`RUNNING`)*: etiketin
adı değişiyor, adımın kendisi değişmiyor. Diğer mod yine basılabilir *(madde 93)*.

**5 · Ayrı export bu cümleyi hiç söylemiyor.** `separate` koşarken ekranda `Disclaimer` geçen
hiçbir şey yok — orada her parça kopyalanıyor ve disclaimer taşımıyor *(261)*, yani cümle yalan
olurdu.

## Kırmızı: bir, ve ikincisi doğuştan yeşil

Bugünkü `..._joining_the_pieces_...` testi 1-4'ün testine dönüşünce düştü — **bir kırmızı**.
Spec iki bekliyordu; **5. olgunun testi bugün zaten yeşil**, çünkü ekranda `Disclaimer` geçen
hiçbir şey yok. Yazılmasının sebebi de bu değildi: uygulama turu cümleyi **iki modun ortak
yerine** koyarsa ayrı export da onu söylerdi, ve o testi yeşil bulmak onun düşmeyeceğinin garantisi
değil — kırmızıya dönebilmesi bekçiliğinin kendisi.

**Yol haritasının kaydı:** bu koşuda tahmin dört kez tutmadı *(249, 252, 253, 257)*, üçünde sayı
büyüktü ve bu kez küçük. Düzeltilen şey her seferinde spec oldu, sayı değil.

## Değişmeyen

`run_export`, `ExportRunner`, `RUNNING` listesi, canlı nokta, bitiş ve hata kartları, ve ayrı
export'un sayacı.
