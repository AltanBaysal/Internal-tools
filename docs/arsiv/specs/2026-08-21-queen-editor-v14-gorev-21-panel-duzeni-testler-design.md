# v14 · Görev 21 — Sağ panelin düzeni · **test turu**

**Kaynak:** yol haritası 21. madde · tasarım v4 fark listesi 88, 89, 90, 91 · 33, 34, 35. kararlar.

Bu koşunun en kalabalık maddesi: dört fark, tek ekran. Dördü de aynı sütuna dokunduğu için tek
maddede toplandılar — ayrı ayrı yapılsalardı aynı dosya dört kez açılır, üçünün testi dördüncüsü
gelince yeniden yazılırdı.

## Bugün ne oluyor

Sağ sütun 300 piksel genişliğinde tek bir akış. İçindekiler `gap: 14` ile alt alta diziliyor,
prompt ve negatif kutuları `flex: 1` taşıyor — yani pencereden artan yeri aralarında paylaşıyorlar.
Kısa bir pencerede ikisi birden daralıyor, uzun bir pencerede ikisi birden şişiyor.

Kutuların başlıkları hangi sekmede olursa olsun aynı iki kelime: "Prompt" ve "Negatif".

Üç ayrı dikey ölçü var: bloklar arası 14, etiketle değeri arası 4, etiketle kutusu arası 6.

Panoya kopyalamanın hiçbir yolu yok.

## Verilen kararlar

### 1 · Etiket hangi katmanı okuduğunu söylüyor *(fark 88)*

| Sekme | Başlıklar |
|---|---|
| Foto | **Foto prompt'u** · **Foto negatif prompt'u** |
| Video | **Video prompt'u** |
| Ses | **Ses prompt'u** |

Kelimeler ikinci kez yazılmıyor: sekmelerin kendi etiketlerinden türüyor (`Foto`, `Video`, `Ses`),
19. maddede kurulan `LAYER_LABEL` tablosundan. Aynı katmanın sekmede bir, başlıkta başka ad taşıması
böyle imkânsız oluyor.

Etiketler kaynakta normal yazılıyor, ekranda CSS büyütüyor. Sayfanın kökü `lang="tr"` olduğu için
tarayıcı Türkçe eşlemesini uyguluyor — "Video prompt'u" ekranda **VİDEO PROMPT'U**, tasarımın
yazdığı gibi.

### 2 · Kutular kendi ölçüsünü alıyor *(fark 89)*

| Kutu | Yükseklik |
|---|---|
| Foto prompt'u | 162 |
| Foto negatif prompt'u | 96 |
| Video prompt'u · Ses prompt'u | 150 |

Ölçüler tasarımın verdiği ölçüler; öncekinin yaklaşık yarı yarıya büyüğü. Taşan metin kutunun kendi
içinde kayıyor — bu bugün de böyle ve değişmiyor.

### 3 · Her prompt başlığının sağında kopyala ikonu *(fark 90)*

İkon başlık satırının sağ ucunda, kutunun sağ kenarıyla hizalı. Negatif de bir prompt kutusu, onun
da ikonu var.

### 4 · İkon cevabını kendi adında veriyor *(33. karar)*

Tasarım yalnız *"basınca metin panoya alınır"* diyor; basıştan sonra ne olduğunu söylemiyor.
Sessizlik bir cevap değil, ve reddedilen bir pano sessizce geçerse kullanıcı metni aldığını sanır.

İkon, panelin kendi iki kelimesini alıyor — **Kopyalandı** / **Kopyalanamadı** — 2,5 saniye boyunca
erişilebilir adı olarak, ve o süre boyunca vurgu ya da tehlike rengine dönüyor. Kelimeler
`RawOutput`'un kelimeleri; süre de onun süresi.

Panele **satır eklemiyor**: başlığın yanında beliren bir kelime altındaki kutuyu aşağı iterdi ve
fark 89'un derdi tam olarak buydu.

### 5 · Kutu boşken ikon basılamıyor *(34. karar)*

Boş bir kutuyu kopyalayıp "Kopyalandı" demek yalan. İkonu gizlemek de bir cevap ama kullanıcı yazıp
sildikçe başlık seğirir. İkon duruyor ve **pasif** — evin pasif düğme dili, silik ve basılamaz.

### 6 · Sütun iki grup *(fark 91)*

Üstte karenin ne olduğu (Sıra, Dosya adı, Üretim modu), altta ondan ne yapılabileceği (prompt'lar,
yeni mod, üret, sil). Aralarında ne başlık ne ayraç var — ayrım gözün dinlendiği yer, okuduğu bir
çizgi değil.

İkisi de yukarıdan hizalı. Tasarımın `space-between` denemesi geri alınmış kararlardan; artan yer
alta düşüyor, gruplar arasına değil.

### 7 · Tek dikey ritim *(fark 91)*

| | Bugün | Bundan sonra |
|---|---|---|
| Bloklar arası | 14 | **16** |
| Etiketle değeri arası | 4 | **6** |
| Etiketle kutusu arası | 6 | 6 |

Bilgi grubunun satırları 300 pikselde sarıyor, yani sardığında **iki satır arası da 16** — yoksa
"tek dikey ritim" cümlesi grubun içinde bozulurdu. Yan yana duran iki alan arasındaki 24 yatay bir
ölçü, ritme dahil değil.

### 8 · Panel kendi içinde kayıyor *(35. karar)*

Kutular sabit yüksekliğe geçince sütunun toplam boyu da sabitleniyor. Tasarım "panel uzayıp
altındaki butonları aşağı itmez" diyor ama panelden kısa bir pencerede ne olacağını söylemiyor.
Cevap: sütun kendi içinde kayıyor. Yoksa silme düğmesi ekranın altında, ulaşılamayacak bir yerde
kalırdı.

## Kapsam dışı

- **Oynatıcı, dalga, sahnenin boşlukları, hap ve düğme metinleri** (fark 98–117) 22. madde.
- **Bekleyen kutunun ortalanmış satırı** (fark 92) 19. maddede kapandı.
- **"Üretim modu" satırı** (fark 93) 8. maddede kapandı; bilgi grubunda kalıyor.
- **Negatifin düzenlenebilir olması** (fark 117) 22. madde. Bu turda salt okunur.

## Yazılacak testler

### `PhotoDetail.test.jsx` — 10 yeni test, `the right column` bloğu

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Her prompt başlığı kendi katmanının adını taşıyor | 88 |
| 2 | Foto sekmesinin iki kutusu kendi yüksekliklerini alıyor | 89 |
| 3 | Video ve ses kutuları aynı ölçüde | 89 |
| 4 | Her prompt başlığının yanında bir kopyala ikonu var | 90 |
| 5 | İkon kutunun kendi metnini kopyalıyor ve söylüyor | 90 · karar 33 |
| 6 | Pano reddedince bunu da söylüyor | 90 · karar 33 |
| 7 | Kutu boşken ikon basılamıyor | 90 · karar 34 |
| 8 | Sütun iki gruba ayrılıyor, aralarında hiçbir şey yok | 91 |
| 9 | Sütun boyunca tek dikey ritim | 91 |
| 10 | Panel kendi içinde kayıyor | 89 · karar 35 |

**Düzeltilen üç test.** Üçü de `Negatif` kelimesini arıyor:

- `shows the negative next to the prompt` ve `draws the box even when there is no negative` —
  yeni başlığı arıyorlar, **kırmızı**.
- `shows the open layer's own prompt and nothing under it` — video sekmesinde negatifin
  **yokluğunu** arıyor. Yeni adla da yok, yani düzeltilmiş hâli bugün de yeşil. Kırmızıya
  sayılmıyor; adı düzeltiliyor çünkü aradığı kelime artık ekranda hiç geçmiyor ve bir testin
  yokluğunu ölçtüğü şeyin var olabilmesi gerekir.

### Doğan tutamaklar

Dördü de **uygulama turunda** doğuyor; testler kırmızıyken yoklar.

| Tutamak | Ne | Neden |
|---|---|---|
| `data-side` | sağ sütun | ritmi ve kaymayı sütunun kendisinden okumak |
| `data-group` | iki grup (`info`, `production`) | grupların sayısı ve sırası |
| `data-box` | metnin durduğu kutu | yüksekliği kutudan okumak; biri `div` biri `textarea` |
| `aria-label` | kopyala ikonu | ikonun adı; ekran okuyucunun da tek bildiği şey |

**Toplam 10 yeni test: 484 → 494. On ikisi kırmızı** (10 yeni + 2 düzeltilen).

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de **12 kırmızı** duruyor. Testler kırmızı commit
ediliyor.
