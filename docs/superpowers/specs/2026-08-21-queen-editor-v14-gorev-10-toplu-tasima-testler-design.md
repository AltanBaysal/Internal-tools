# v14 · Görev 10 — Toplu kart taşıma · **test turu**

**Kaynak:** [yol haritası v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) 10. madde —
[İstek 5](../plans/2026-08-20-queen-editor-istekler.md) ve
[fark listesi](../research/2026-08-20-queen-editor-tasarim-v4-farklari.md) 70, 71, 72.

## Sorun

**Fark 70:** bugün seçim varken sürükleme tamamen kapalı (`draggable={!selecting}`). Üç kare seçiliyken
biri sürüklenmeye çalışılınca hiçbir şey kalkmıyor; diziyi taşımak için seçimi bozup kartları tek tek
sürüklemek gerekiyor ve aralarındaki sıra bozuluyor.

İsteğin kendi cümlesi: *"Çoklu seçim zaten var, tek kart sürükleme de çalışıyor; eksik olan seçimin
sürüklemeye katılması. Mekanik değişmiyor."*

**Fark 72:** dağınık seçim bırakıldığı yerde yan yana geliyor, aralarındaki sıra korunuyor, aradaki
kartlar boşluğu kapatıyor.

**Fark 71:** ekrana yeni bir öğe eklenmiyor — sayı rozeti, yığın görüntüsü, özel sürükleme imgesi
yok; yuva göstergesi de aynı kalıyor.

## Kararlar

### 1 · Tek kartın kuralı olduğu gibi kalıyor, blok onun genellemesi

Bugünkü `handleDrop` şunu yapıyor: sürüklenen kartı listeden çıkar, sonra `to` indeksine yerleştir.
Sonuç şu tek cümleyle özetlenebiliyor: **kart, yuvanın gösterildiği indekse iniyor.**

Blok da aynı cümleyi izliyor: taşınan kartların hepsi çıkarılıyor, sonra **blok `to` indeksinden
başlayacak şekilde** yerleştiriliyor. Tek kart, bu kuralın bir elemanlı hâli — yani bugünkü davranış
hiç değişmiyor ve mevcut sürükleme testleri aynı kalıyor.

Alternatif "hedef kartın hemen arkasına koy" idi. Reddedildi: tek kartla bugünkünden farklı sonuç
verir, ve *"mekanik değişmiyor"* diyen bir istekte mekaniği değiştirmek olurdu.

### 2 · Taşınanların sırası galeriden okunuyor, seçim durumundan değil

`selected` tıklanma sırasında duruyor — kullanıcı 9'u, sonra 3'ü seçmiş olabilir. Taşınacak liste
galerinin kendi sırasından süzülüyor, böylece *"kendi aralarındaki sıra korunur"* tıklama sırasına
değil kartların sırasına dayanıyor.

### 3 · Sürüklenen seçili değilse yalnız o gidiyor ve seçim bozulmuyor

Karar isteğin kendisinde. Sürükleme seçime hiç dokunmuyor: ne temizliyor ne genişletiyor.

### 4 · Sunucuya yalnız gerçekten değişen sıra gidiyor

Bugünkü koruma `from === to`. Blokta yetmiyor: seçili iki kartın ikincisi birincinin üstüne
bırakılırsa `from !== to` ama sıra aynı kalıyor.

Bu yüzden koruma **sonucun karşılaştırılması** oluyor: yeni dizi eskisiyle aynıysa sunucuya
gidilmiyor. Bu, bugünkü korumayı da kapsıyor.

### 5 · Sürüklenen görünümü bloğun tamamında, yuva göstergesi olduğu gibi

Bugün `dragging = index === dragIndex`. Artık *taşınanlardan biri olmak*. Efektin kendisi
değişmiyor — Fark 71 zaten bunu istiyor.

Yuva göstergesi de aynı kuralla: bugün sürüklenen kartın üstünde doğmuyor, artık bloğun hiçbir
kartının üstünde doğmuyor. "Sürüklenen kart"ın bloğa genişlemesi, göstergenin kendisini
değiştirmiyor.

### 6 · Seçim açıkken kart sürüklenebilir oluyor

`draggable={!selecting}` gidiyor. Basış ile sürükleme çakışmıyor: tarayıcı tamamlanan bir
sürüklemeden sonra `click` üretmiyor, ve kodun bugünkü yorumu bunu zaten söylüyor.

### 7 · Yeni öğe eklenmediği, karo sayısıyla ölçülüyor

*"Yığın görüntüsü doğmaz"* bir yokluk. Ölçülebilir hâli: sürükleme sürerken ekrandaki karo sayısı
değişmiyor. Bir yığın ya da hayalet kart uygulaması burada düşer.

## Yazılacak testler

Hepsi `Gallery.test.jsx` içinde, kendi bloğunda. Beş karelik bir galeri kullanılıyor: üç kare,
dağınık bir seçimin arasında kalan kartları göstermeye yetmiyor.

1. Seçili bir kart sürüklenince seçimin tamamı blok olarak iniyor.
2. Blok kendi aralarındaki sırayı koruyor — tıklama sırası ters olsa bile.
3. Dağınık seçim yan yana geliyor ve aradaki kartlar boşluğu kapatıyor.
4. Seçili olmayan kart sürüklenince yalnız o gidiyor.
5. …ve seçim bozulmuyor.
6. Seçim açıkken kart sürüklenebiliyor.
7. Sürüklenen görünümü seçili kartların hepsinde.
8. Sürükleme sürerken ekrana karo eklenmiyor.
9. Blok bulunduğu yere inerse sunucuya gidilmiyor.

## Bitti sayılır

Dört komutun dördü de koşuyor, dokuz testin altısı kırmızı çıkıyor ve commit ediliyor. Kaynak
dosyalara bu turda dokunulmuyor.

Üçü doğuştan yeşil: 4 ve 5 (seçili olmayan kart bugün de yalnız gidiyor ve seçime dokunmuyor), 8
(bugün ekrana eklenen bir şey yok). Nöbetleri blok doğduktan sonra başlıyor.
