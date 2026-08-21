# v14 · Görev 17 — Panelin görsel hizalaması · **test turu**

**Kaynak:** yol haritası 17. madde · tasarım v4 fark listesi 30, 31, 32, 33 · 17. karar
(*"Paneldeki Süre bloğu kalkar"*).

Dört fark, tek ekran: katman paneli. Hiçbiri davranış değil — panel aynı işi yapıyor, başka
görünüyor.

## Dört fark

| Fark | Bugün | Bundan sonra |
|---|---|---|
| 30 | Kapsam satırı "Videosu olmayanlar" | "Videosu olmayan kareler" |
| 31 | Satırda yalnız metin ve sayı; seçili olan çerçeve renginden belli | Solunda daire — seçilide kalın ve vurgu renginde, ötekinde ince ve soluk — ve satır daha ferah |
| 32 | Model, seçilemeyen soluk bir metin satırı | Fotoğraf panelindekiyle aynı açılır kutu |
| 33 | Varyantın altında "Süre" bloğu | Blok yok |

## Verilen kararlar

### 1 · Kapsam satırının adı *(fark 30)*

Bu bir sapma, tercih değil: uygulamanın kendi tarifi satırı **"Videosu olmayan kareler"** diye
yazmıştı ve ses tarafındaki eşi ("Videosu olup sesi olmayan kareler") tam yazılırken video tarafı
kısalmış. Sayı satırın sağında duruyor — tarifteki `· N` ayracın kendisi değil, satırın nasıl
okunduğu.

**Üç yorum bu adı anıyor ve üçü de düzeltiliyor:** `queue_layer.py`, `test_photo_usecases.py` ve
`LayerPanel.jsx`'in kendi iki satırı. Kodla çelişen yorum kodla eşitlenir.

### 2 · Seçim dairesi *(fark 31)*

Daire **kapsam satırına** giriyor — yol haritasının yazdığı yer orası. Seçilide 2 piksel vurgu
rengi, ötekinde 1 piksel soluk gri.

**Ferah iç boşluk her iki satır ailesine de gidiyor.** `ModeRow`'un kendi yorumu *"bir kapsam satırı
nasıl çiziliyorsa öyle"* diyor; ölçüyü yalnız birine vermek o cümleyi yalan yapardı ve panelde
8 piksellik satırların altında 10 piksellik satırlar bırakırdı. Daire gitmiyor: mod satırının kendi
görünümü 4. maddede karara bağlandı, ve fark 23 ona başka bir işaret veriyor.

Satırın ortak kılığı tek bir sabite çıkıyor, ki ikisi bir daha ayrışmasın.

### 3 · Model kutusu *(fark 32)*

Kutu gerçek bir `select`, fotoğraf panelininkiyle aynı sınıf ve aynı çerçeve. İçinde **tek seçenek**
var, çünkü katman başına tek model var: video WAN 2.2 I2V, ses MMAudio v2. Kuyruğa giden işte model
alanı zaten boş — motor kendi seçiyor.

Tek seçenekli bir kutu bir yalan değil: açılıyor ve olan tek şeyi gösteriyor. Çerçevesiz bir metni
kutuya benzetmek ya da tıklanmayan bir kutu çizmek olurdu yalan olan.

### 4 · Süre bloğu *(fark 33, karar 17)*

Blok gidiyor, iki cümlesiyle birlikte. Gerekçe 17. kararın kendisi: kural yazılı belgede duruyor,
panelde yer tutmasına gerek yok.

Kalan bloklar — **Model, Kapsam, Üretim modu (yalnız video), Varyant** ve buton. Maddenin "bitti
sayılır"ı tam olarak bu, ve bir test onu bir liste olarak okuyor.

## Kapsam dışı

- **Mod satırının kendi görünümü** (fark 23) 4. maddede kapandı.
- **Kurulum kartı** (fark 18, 19) 5. kararla defterde; 38. maddesi 25. görev.
- **Panelin hata dili** 16. maddede kapandı.
- **Fotoğraf paneli** — dört farkın hiçbiri onun değil; model kutusu orada zaten var.

## Yazılacak testler

### `LayerPanel.test.jsx` — 9 yeni, 1 silinen, 2 düzeltilen

Yeni bir blok: `LayerPanel — the panel's own shape`.

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Kapsam satırının adı tam yazılıyor | 30 |
| 2 | Her kapsam satırının başında daire var, seçilideki kalın ve vurgu renginde | 31 |
| 3 | Satırlar daha ferah — kapsam ve mod aynı ölçüde | 31 |
| 4 | Model, fotoğraf panelinin kullandığı kutuda | 32 |
| 5 | Süre bloğu yok | 33 |
| 6 | Panelde yalnız dört blok kaldı | 33 |

`LayerPanel — sound` bloğuna üç:

| # | Ne diyor | Fark |
|---|---|---|
| 7 | Kendi kapsam adı zaten tam yazılı | 30 |
| 8 | Kendi modeli de aynı kutuda | 32 |
| 9 | Onun Süre cümlesi de yok | 33 |

**Silinen:** `says the length is not a choice in this version` — 33 onu düşürüyor.

**Düzeltilen iki test:** kapsam satırını kısa adıyla arayan iki arama (`counts the frames a video
can still be hung on` ve `clears the reason when another scope is picked`).

**Toplam 9 yeni, 1 silinen: 467 → 475.**

## Doğuştan yeşil bir test

7 bugün de geçiyor — ve geçmesi maddenin kendi gerekçesi: ses tarafı tam yazılmış, video tarafı
kısalmış. Video satırının neye benzetildiğini söyleyen çıpa bu, ve o çıpanın kayması 30. maddeyi
sessizce geri alırdı.

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de **10 kırmızı** duruyor — dokuz yeninin sekizi ve
kısa adı arayan iki düzeltilmiş test. Testler kırmızı commit ediliyor.
