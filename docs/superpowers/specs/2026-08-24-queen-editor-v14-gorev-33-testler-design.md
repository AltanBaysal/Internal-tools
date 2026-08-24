# v14 Görev 33 — Ekran bilmediğini söylemez: TEST döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** teşhis, aynı gün
**Öncesi:** [Görev 32 uygulama spec'i](2026-08-24-queen-editor-v14-gorev-32-uygulama-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 33

## Sorun

Kuyruk paneli, sunucu ilk cevabını vermeden **"Kuyruk boş"** diyor ve altına *"Fotoğraf üret
panelinden kare gönder."* yazıyor. Akan bir üretim varken bile. Bir kareye girip çıkan biri bunu her
seferinde bir poll boyunca görür.

Bu bir gecikme değil, **yanlış bir cümle**: kuyruğun boş olduğu söyleniyor, oysa bilinen tek şey
kimsenin henüz sormadığı.

Bugün göze çarpmıyor çünkü geri dönüşte açık panel de sıfırlanıp fotoğraf paneline dönüyor — yani
kuyruk paneli zaten kapalı oluyor. **34. madde onu açık bırakacak.** Bu yüzden 33, 34'ün önünde
duruyor: sıra ters olsaydı yanlış cümle ilk kez o zaman ekrana çıkardı.

## Cevap kodda zaten var

`useGeneration` `known` adında bir bayrak tutuyor: sunucu bu mount'ta bir kez cevap verdi mi.
Yorumu tam bu maddeyi tarif ediyor:

> *"idle is a placeholder, not an answer, and a screen that acts on it decides on a state nobody
> reported."*

Bayrak hesaplanıyor, dışa da veriliyor — ama **hiçbir tüketici okumuyor.** Ne `ProjectScreen` ne
`PhotoDetail` onu alıyor. Yapılacak iş yeni bir şey icat etmek değil, yazılmış olanı bağlamak.

## Kararlaştırılan davranış

Sunucu bu mount'ta henüz konuşmadıysa kuyruk paneli **hiçbir şey söylemez** ve kendi sütununda bir
halka gösterir — 31'in fotoğraf paneline verdiği aynı biçim. Cevap gelince panel bugünkü hâline
döner, hiçbir cümlesi değişmeden.

Bir bilgi kartı da, bir tahmin de yok: bilinmeyen bir durum hakkında söylenecek doğru cümle yok.

## Kapsam: yalnız kesin bir iddia düzeltiliyor

Galerinin hapları da bilmeden konuşuyor: sunucu cevap vermeden borçlu bir katman *"kuyrukta"* değil
*"bekliyor"* okunuyor, ve cevap gelince kelime değişiyor.

**Bu madde ona dokunmuyor.** İkisi aynı sınıfta değil: kuyruk paneli *kuyruğun boş olduğunu* söylüyor,
ki bu doğrudan yanlış olabilir; galerinin iki kelimesi de "henüz üretilmedi" demek ve aralarındaki
fark bir söz veriştir. Onu düzeltmek üçüncü bir kelime tasarlamayı gerektirir, ve o kelime bu koşuda
kararlaştırılmadı.

## Sabitlenecek davranış

| # | Ne | Nerede |
|---|---|---|
| **B1** | Sunucu konuşmadan kuyruk paneli susar ve kendi halkasını gösterir | `QueuePanel.test.jsx` |
| **B2** | Sağ sütun bu bilgiyi kuyruk paneline geçirir | `SidePanel.test.jsx` |
| **B3** | Proje ekranı, ilk cevap gelmeden açılan kuyruk panelinde "Kuyruk boş" demez | `ProjectScreen.test.jsx` |

B3 kablonun kendisini sınıyor: `useGeneration` → `ProjectScreen` → `SidePanel` → `QueuePanel`.
Bugün o kablo hiç yok, ve sessizce eksik kalması tam olarak bu maddenin sebebi.

## Mevcut 47 test ne olacak

`QueuePanel.test.jsx`'in yardımcısı bayrağı **bilinir** olarak verecek. Kırk yedi testin hepsi
panelin *bildiğinde* ne dediğini sınıyor; anlamları aynen korunuyor ve tek satır kurulum değişiyor.

Bayrağın kendisi varsayılan almıyor: "bilmiyorum"u sessizce varsayılan yapmak, çağıranın unuttuğu
her yerde paneli susturur — ve unutulan bir kablo zaten bu maddenin doğuş sebebi.

## Kapsam dışı

- **Kuyruğun hatırlanması.** Durum canlı; eski bir sayı göstermek ayrı bir karar ve 32'nin kuralı
  buraya uzanmıyor.
- **Galerinin hapları** — yukarıda anlatıldı.
- **Açık panelin hatırlanması** — 34. madde.
- **Kod bu döngüde değişmiyor.** Testler kırmızı bırakılır.
