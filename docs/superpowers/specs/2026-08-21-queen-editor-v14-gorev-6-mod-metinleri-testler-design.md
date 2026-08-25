# v14 · Görev 6 — Tahmin ve onay metinleri moda göre değişiyor · **test turu**

**Kaynak:** [yol haritası v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) 6. madde —
[İstek 3](../plans/2026-08-20-queen-editor-istekler.md) ve
[fark listesi](../research/2026-08-20-queen-editor-tasarim-v4-farklari.md) 25 ile 26.

## Sorun

Panelin butonunun altındaki iki cümle bugün moddan habersiz. Tahmin her zaman
*"9 video üretilecek — her kare kendi videosunu alır."*, yeşil onay her zaman
*"9 video kuyruğa eklendi"*. Kullanıcı loop seçip kuyruğa eklediğinde ekranda loop diye bir kelime
geçmiyor — modun gerçekten gittiğinin tek kanıtı üretimin sonunda çıkan video.

İkinci sorun aynı iki cümlede: **zaten videosu olan bir kare seçiliyken de cümle değişmiyor.** O kare
için üretim eskisini yazmıyor, yanına kopya bir kare doğuruyor. Bugün bunu söyleyen hiçbir şey yok;
kullanıcı galeride kare sayısının arttığını görene kadar öğrenmiyor.

## Kararlar

### 1 · Modu cümlenin başı söylüyor, sonu değil

Cümle iki parça: **baş** (*"6 bağlı video üretilecek"*) ve **kuyruk** (*"— her video sıradaki karede
biter."*). Mod ikisini de değiştiriyor.

| Mod | Baş | Kuyruk |
|---|---|---|
| Standart | `N video` / `N ses` | `her kare kendi videosunu alır.` / `…sesini alır.` |
| Loop | `N loop video` | `her video kendine döner.` |
| Sonrakine bağla | `N bağlı video` | `her video sıradaki karede biter.` |

Standart'ın kelimeleri katmanın kendi kelimeleri — bugün `WORDS` içinde duran `noun` ve `own`. Yeni
bir tablo yalnız öteki iki modu taşıyor; standart oraya yazılsa aynı kelimeler katman başına ikinci
kez yazılmış olurdu.

### 2 · Kopya uyarısı modun kuyruğunu alıyor, başını değil

Seçili kapsamda o katmanı zaten taşıyan kare varsa kuyruk yerine şu geçiyor:

> `videolu 1 kare için yeniler kopya kare olur, eskisi durur.`

Ses panelinde `sesi olan 1 kare için…`. İkisinin farkı tek kelime, ve o kelime `WORDS`'e yeni bir
alan olarak giriyor.

**Neden kuyruğu alıyor:** mod cümlenin başında zaten söylenmiş durumda — *"1 loop video üretilecek —
videolu 1 kare için…"* hâlâ loop diyor. Kaybolan bir şey yok. Kaybolan tek şey modun kuyruğu, ve o
kuyruk hemen üstteki işaretli satırın tekrarı; kopya uyarısı ise hiçbir yerde görünmeyen bir haber.

**Neden iki cümle değil:** butonun altında tek satır var ve iki uzun yan cümle onu sarmalayıp
düğmeyi aşağı iterdi.

### 3 · Kopya sayısı kapsamdan çıkıyor

Ham seçimden değil, kapsamdan: *"Videosu olmayanlar"* kapsamı zaten o katmanı taşıyan kareleri
dışarıda bırakıyor, dolayısıyla orada sayı kendiliğinden sıfır ve uyarı hiç doğmuyor. Kapsamı
okumak, "yalnız seçili kapsamda uyar" diye ayrı bir koşul yazmaktan kısa — ve o koşul bir gün
kapsamlar değişirse yanlış tarafa bakardı.

### 4 · Yeşil onay gönderildiği modu hatırlıyor

Onay kartı on saniye duruyor. O sürede kullanıcı mod satırını değiştirebilir. Kart canlı modu
okusaydı, standart gönderilmiş bir kuyruk için *"2 loop video kuyruğa eklendi"* yazardı — yani
kullanıcıya olmamış bir şeyi söylerdi.

Bu yüzden onayın durumu artık yalnız sayı değil, **sayı ile mod birlikte**. İkisi de isteğin
gönderildiği andan.

### 5 · Tahmindeki sayı `owed` olarak kalıyor

Bağlı modda motor, filmde sonrası olmayan kareyi atlıyor — dolayısıyla kuyruğa giren sayı tahminden
düşük olabilir. Panel bunu yeniden hesaplamıyor.

Sebebi: "bir karenin filmde sonrası hangisi" kuralı motorda (`queue_layer._frame_after`) yaşıyor ve
onu panele kopyalamak tek kuralı ikiye çıkarır — kopya olan da bayatlar. Doğru sayı bir tuş sonra
zaten geliyor: yeşil onay sunucunun kendi sayısını yazıyor.

Bu bir sınır, bir eksiklik değil; buraya yazıldı ki bir sonraki tur onu keşif sanmasın.

## Yazılacak testler

Hepsi `LayerPanel.test.jsx` içinde, iki yeni blokta.

**Tahmin modu söylüyor**

1. Loop seçilince tahmin loop'un kelimeleriyle yazıyor.
2. Bağla seçilince tahmin bağlının kelimeleriyle yazıyor.
3. Bir mod seçildikten sonra eski tek kalıptan ekranda iz kalmıyor.
4. Yeşil onay modun kelimeleriyle yazıyor.
5. Onay, gönderildiği modu tutuyor — arkasından satır değişse de.

**Tahmin kopyayı haber veriyor**

6. Kapsamda o katmanı taşıyan kare varsa uyarı çıkıyor.
7. Uyarı yalnız kapsamdaki taşıyanları sayıyor, kapsamın tamamını değil.
8. *"Videosu olmayanlar"* kapsamında uyarı hiç doğmuyor.
9. Uyarı modun kuyruğunun yerine geçiyor, başına dokunmuyor.
10. Ses paneli uyarıyı kendi kelimesiyle yazıyor.

**Değişen tek eski test:** *"counts a selected frame that already has a video"* — videosu olan bir
kareyi seçiyor, yani bugünden sonra kopya cümlesini üreten durum o. Beklentisi yeni cümleye
çevriliyor; ölçtüğü şey (sayının 1 olması) değişmiyor.

## Bitti sayılır

Dört komutun dördü de koşuyor, ön yüz takımı on kırmızı veriyor ve o kırmızılar commit ediliyor.
Kaynak dosyaya bu turda dokunulmuyor.

On bir testin biri — 8. sıradaki, *"Videosu olmayanlar"* kapsamında uyarının hiç doğmaması —
doğuştan yeşil. Ölçtüğü şey bir yokluk ve o yokluk bugün de doğru, çünkü kopya cümlesi henüz hiçbir
kapsamda yok. Nöbeti uygulama turundan sonra başlıyor.
