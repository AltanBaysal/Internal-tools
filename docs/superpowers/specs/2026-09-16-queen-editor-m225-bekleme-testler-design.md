# Madde 225 · Beklerken ekran susmayacak — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Madde daraldı

Kullanıcı kararı, 16 Eylül: *"225'te sessizliği çöz artık, uzun süreceğini sanmıyorum."* Yani
**ölçüm ve hızlandırma düştü** — 227 yavaşlığın dört adayından üçünü zaten kaldırdı *(taşıma,
taşımadan önceki 5 saniyelik bekleme, klasör açma)*, ve kalanın gözle görülür olduğu artık belli
değil. Hâlâ bekletiyorsa kendi maddesi olarak geri gelir.

Kalan yarı hızdan bağımsız: Drive'a giden bir istek anlık olmayacak, ve ekran o süre boyunca
susmayacak.

## Bugün ne oluyor

[`ProjectsScreen`](../../../queen-editor/frontend/src/features/projects/ProjectsScreen.jsx)'de
`handleArchive` ile `handleRestore` bir **meşgul durumu tutmuyor** — oradaki tek `busy` silme
penceresinin. Sonuç üç kat:

- Basıldığı andan liste değişene kadar ekranda **hiçbir şey** olmuyor.
- Düğme basılabilir kalıyor, ve ikinci basış gerçekten **ikinci bir istek** yola çıkarıyor.
- Kullanıcının gördüğü cümle yine *"basıyorum, hiçbir şey olmuyor"* — 223'ün sessiz hatasıyla aynı
  cümle, başka sebeple.

## Ne olacak

Uygulamanın bekleme dili zaten **bir kelime**: *"Siliniyor…"*, *"Kaydediliyor…"*,
*"Oluşturuluyor…"* — pencerelerin `busyLabel`'ı. Kart da aynı dili konuşuyor: iş sürerken kartın
tarih satırının yerinde **ne olduğu** yazıyor.

| Hareket | Kartta yazan |
|---|---|
| Arşivle | `Arşivleniyor…` |
| Geri al | `Geri alınıyor…` |

Ve o sürede kartın **üç düğmesi de kapalı**: yalnız ikinci bir arşivleme değil, arada bir silme ya
da ad değiştirme de engellenmeli — hepsi aynı klasöre ve aynı işarete dokunuyor.

Kelime **liste yeniden okunana kadar** duruyor, isteğin cevabı gelene kadar değil: okuma da Drive'a
gidiyor, ve orada bırakılan boşluk sessizliğin aynısı olurdu.

**Dönen bir şey yok:** hata zaten 223'te ekrana bağlandı. Burada eklenen tek şey, hata gelirse
kelimenin de kalkması.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Arşivleme sürerken kart `Arşivleniyor…` diyor | **kırmızı** |
| 2 | O sürede arşiv düğmesine ikinci kez basmak ikinci istek göndermiyor | **kırmızı** |
| 3 | O sürede silme ve ad değiştirme de kapalı | **kırmızı** |
| 4 | İş bitince kelime kalkıyor | **kırmızı** |
| 5 | Geri alma sürerken kart `Geri alınıyor…` diyor | **kırmızı** |
| 6 | Hata gelirse kelime kalkıyor, sunucunun cümlesi kalıyor | **kırmızı** |

## Bu turda değişen

Yalnız testler: `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`.

Arka uçta hiçbir şey değişmiyor — bekleme ekranın kendi meselesi.
