# v14 · Görev 15 — Galeri kartının görsel hizalaması · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-15-galeri-karti-testler-design.md) ·
kırmızı commit `1835295` (454 testin 12'si kırmızı).

Testler ne istediğini söyledi; bu belge nereye yazılacağını.

## Üç dosya, üç konu

| Dosya | Ne değişiyor | Fark |
|---|---|---|
| `frame_status.jsx` | konum haptan **köşe kutusuna** taşınıyor, kalıbın ölçüsü ve bekleyenin tonu | 64, 65 |
| `Gallery.jsx` | rozetler sol alta, ikonsuz, katman başına kutu · borç listeye dönüyor · perde ve düğme | 60, 61, 62, 64, 75 |
| `PhotoDetail.jsx` | kendi etiketini `Corner` ile sarıyor | 64'ün yan etkisi |

## 1 · Köşe, hapın kendisinden ayrılıyor *(64)*

Bugün `PILL` hem kutucuk hem konum. İki hap alt alta dizilemiyor, çünkü ikisi de aynı `top: 6,
left: 6` noktasına yapışırdı.

```
Corner   position: absolute · top 6 · left 6 · sütun · gap 3 · pointer-events: none
  Pill   koyu zemin · yuvarlatılmış · 9px · (canlıysa) nokta + kelime
  Pill
```

`pointerEvents: none` haptan köşeye taşınıyor: ölü noktayı doğuran şey konumun kendisi, ve artık
konum köşede. Kart üzerinde hiçbir etiket sürüklemeyi ya da tıklamayı yemiyor.

`StatusPills` yeni bir dışa açık isim: eline bir hâl listesi alıyor, boşsa hiçbir şey çizmiyor,
doluysa köşeyi kuruyor. Galeri tek bir şey veriyor ona; hangi hapların doğduğu `statusOf`'un işi.

Detay sayfası `Pill`'i doğrudan kullanmaya devam ediyor, ama artık `Corner` ile sararak — o ekranda
her zaman tek etiket var, dolayısıyla `StatusPills` değil. İki ekran tek kalıpta kalıyor.

## 2 · Borç bir liste *(64)*

`statusOf` tek bir cevap yerine sıralı bir liste veriyor:

- üretilen katman varsa **yalnız o**,
- yoksa patlayan katman varsa **yalnız o**,
- yoksa **borcun tamamı**, motorun sırasında.

Üst sınır uydurulmuyor. Fotoğrafı olmayan kareye katman kuyruğa girmiyor (`frames_in_scope`), yani
foto borcu katman borcuyla aynı karede buluşamıyor ve borç en fazla ikiye çıkıyor.

## 3 · Kalıbın ölçüsü, hâlin rengi *(65)*

| | Bugün | Bundan sonra | Kim için |
|---|---|---|---|
| zemin | `rgba(10,8,7,.85)` | `rgba(10,8,7,.7)` | her hap |
| iç boşluk | `2px 5px` | `3px 7px` | her hap |
| bekleyen/kuyruktaki ton | `--ink` | `--ink-2` | yalnız o iki hâl |

Ölçü kalıbın: alt alta dizilen iki hapın farklı zeminde durması kırık görünürdü, ve bu dosyanın
kendi kuralı zaten "her katman için tek kalıp". Renk hâlin: üretiliyor ile hata anlamlarını
renklerinde taşıyor, fark da onlardan söz etmiyor.

`--ink-3` değil `--ink-2`: karşı köşedeki sahiplik rozeti aynı mürekkebi aynı boyda taşıyor, yani
9 pikselde okunabildiği kanıtlanmış olan soluk ton bu.

## 4 · Sahiplik rozetleri *(60, 61, 62)*

Satır sol alta iniyor ve zeminini bırakıyor — zemin artık rozetin kendisinde. `GLYPH` eşlemesi,
`PlayGlyph`/`SoundGlyph` içe aktarımı ve rozetin içindeki ikon gidiyor. `PlayGlyph` dosyasında
kalıyor: detay sayfasının video sekmesi onu kullanıyor.

```
OWNS   position: absolute · bottom 6 · left 6 · satır · gap 4 · pointer-events: none
  OWN  koyu zemin · yuvarlatılmış · 9px · yalnız kelime      (data-own)
  OWN
```

Sağ alt köşe boş kalıyor. Dört köşenin dördü de artık ayrı: sol üstte hap(lar), sağ üstte numara ve
seçim halkası, sol altta sahiplikler.

**Çakışma yok.** İki hap yalnız iki katman beklerken doğuyor; bir katmanı bekleyen karenin o katmanı
henüz yok, dolayısıyla iki hap ile iki rozet aynı karoda buluşamıyor.

## 5 · Perde ve altındaki düğme *(75)*

Perde `rgba(0,0,0,.55)` → `rgba(10,8,7,.55)`. Saydamlık aynı; değişen, perdenin de kartın öteki
etiketlerinin durduğu kahve-siyaha oturması.

`RetryButton` bir zemin parametresi alıyor. Perdenin altındaki `--bg-2` — kartın kendi zemini —
alıyor, boş kırmızı karonun ortasındaki bugünkü gibi zeminsiz kalıyor. Varsayılan zeminsiz: iki
çağırandan yalnız biri özel, ve özel olan kendini söylüyor.

## Değişmeyen

- `app.css` — bu maddenin hiçbir kuralı hover'a bağlı değil.
- `layer_words.js` — rozetin **kelimeleri** değişmiyor, yalnız kutusu ve yeri.
- `image_queue.js`, `TileImage.jsx` — resmin kendisi bu maddenin konusu değil.
- Sürükleme, numaranın hover'da kalkması, bırakma anı ve karışık seçim onayı: 28–31. kararlar.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 694 / 454. `dist` aynı commit'te derleniyor.
