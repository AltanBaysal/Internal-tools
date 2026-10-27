# v14 · Görev 19 — Her sekme yalnız kendi katmanını gösterir · **test turu**

**Kaynak:** yol haritası 19. madde · İstek 4.1 · tasarım v4 fark listesi 86, 87, 92 ·
23. ve 24. kararlar.

> *"Bugün açık sekmenin altındaki katmanlar da görünüyor — video sekmesinde fotoğrafın adı ve
> prompt'u da yazıyor. Üçü de aynı, sade düzene inecek: üstte kartın adı ve sırası, altında yalnız
> o sekmenin prompt'u."*

## Bugün ne oluyor

Sağ sütun **açık sekmeye kadarki bütün katmanları** çiziyor (`shown`). Video sekmesinde üst grupta
iki dosya adı satırı (`Foto` ve `Video`), altında iki prompt kutusu (video'nunki yazılabilir,
fotoğrafınki salt okunur). Ses sekmesinde üç dosya adı, üç prompt.

Gerekçesi *"bu katman neyden yapıldı görünsün"*di ve o karar geri alındı (madde 87).

## Verilen kararlar

### 1 · Üst grupta iki satır kalıyor *(fark 86, karar 23)*

Tasarım üst grupta yalnız **Sıra** bırakıyordu; 23. karar bunu kısmen tersine çevirdi: **karenin
kendi adı da kalıyor**, çünkü detay sayfasının üst şeridinin ortasında proje adı yazıyor, kare adı
değil — kimlik başka hiçbir yerde durmuyor.

Kalkan, **alt katmanların** dosya adları. Ve ad artık üç sekmede de aynı satır: etiketi hep "Dosya
adı", üretilmemiş karede "Dosya adı (planlanan)". Bugün bu etiket yalnız foto sekmesinde çıkıyor,
öteki sekmelerde satır "Foto" adını alıyordu — çünkü yanında bir de "Video" satırı vardı.

Üst grubun tamamı bir liste olarak okunuyor: bir testin ölçtüğü şey satırların **hepsi**, tek tek
varlıkları değil. Yoksa "şu satır gitti" der ama "başka satır kalmadı" diyemezdik.

### 2 · Prompt kutusu bir tane *(fark 87)*

Açık sekme yalnız kendi katmanının prompt'unu gösteriyor. Altındakiler hiç doğmuyor.

Negatif prompt foto sekmesinde kalmaya devam ediyor: o fotoğrafın kendi alanı ve video ile ses
işleri negatif taşımıyor. Bu maddede değişmiyor.

### 3 · Bekleyen katmanın kutusu *(fark 92, karar 24)*

Kutu asla boş kalmıyor — kullanıcı prompt'un silindiğini sanmasın diye. İçindeki tek satır
**ortalanıyor** ve cümlesi değişiyor:

| | |
|---|---|
| Bugün | sola dayalı · "üretim sırası gelince LLM yazacak" |
| Bundan sonra | ortalanmış · "Prompt yok — üretim sırası geldiğinde eklenecek." |

Yeni cümle kim yazacağını söylemiyor, ne olduğunu söylüyor. Hangi modelin yazdığı kullanıcının
kararı değil ve kutuda bir yer tutmasına gerek yok.

## Kapsam dışı

- **Prompt etiketlerinin katmanını söylemesi** (fark 88) 21. madde. Bu turda etiket "Prompt".
- **Kutuların sabit yüksekliği, kopyala ikonu, sütunun iki grubu** (fark 89, 90, 91) 21. madde.
- **Sekmelerin ayrılması** (fark 85) 20. madde.
- **Üretim modu satırı** (fark 93) 8. maddede kapandı ve üst grupta durmaya devam ediyor.

## Yazılacak testler

### `PhotoDetail.test.jsx` — 3 yeni, 3 düzeltilen

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Karenin adı ve sırası üç sekmede de duruyor | 86 · karar 23 |
| 2 | Üst grupta o iki satırdan başkası yok | 86 |
| 3 | Bekleyen kutunun tek satırı ortalanmış | 92 · karar 24 |

**Düzeltilen üç test:** `shows the open layer's own prompt and the ones under it` ve `repeats the
skeleton for sound` — ikisi de alt katmanların kutularını ve dosya adlarını bekliyor, ikisi de 86
ve 87 ile ters düşüyor; `opens the tab of the layer it is waiting for, with an empty box` ise eski
cümleyi arıyor.

**Toplam 3 yeni test: 478 → 481. Altısı da kırmızı.**

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de **6 kırmızı** duruyor. Testler kırmızı commit
ediliyor.
