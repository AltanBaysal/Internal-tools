# Queen Editor v5 · Görev 27 — Hata ve kopya kare detayı · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 7, Görev 27 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
79, 81 · **Tür:** arka uç + ön yüz.

## Neden

Detayın açamadığı iki hâl kaldı. **Hatalı kare** kesikli kırmızı bir kutu gösteriyor ama sebebini
yazmıyor ve oradan tekrar denenemiyor. **Kuyruktaki kopya kare** ise hiç açılamıyor: adresi
kaynağının fotoğraf adı olduğu için sayfa kaynağı buluyor — iki kare, tek adres.

## Ne olacak

Kare artık her yerde **kimliğiyle** adreslenir; kopya kare kendi sayfasını açar. Hatalı katmanın
alanı sebebini yazar ve sağ sütunda "Tekrar dene" durur. Bekleyen katmanın sekmesi de açılır: canlı
rozet, boş prompt kutusu ve onay sormayan "Kuyruktan çıkar".

## Kararlar

### 1. Kareyi kimliği adresler — her yerde

Bir fotoğraf iki kareye ait olabilir (madde 102), o yüzden dosya adı kareyi göstermez. Görev 26 iki
ucu kimliğe geçirmişti; bu görev işi bitirir:

| Nerede | Bugün | Bundan sonra |
|---|---|---|
| Detay adresi | `/projects/<p>/photos/P0_0.png` | `/projects/<p>/photos/P0_1` |
| Galeri karosu (anahtar, seçim, sürükleme) | dosya adı | kimlik |
| Sıra kaydı (`PUT …/order`) | dosya adları | kimlikler |
| Tekrar dene (`POST …/retry`) | `{"file": …}` | `{"frame": …}` |
| Kare silme (`POST …/frames/delete`) | `{"files": [...]}` | `{"frames": [...]}` |

Sıra dosyası zaten kimlik tutuyordu — sunucu gelen adları kimliğe çeviriyordu; artık çevirecek bir
şey yok. Dosya adı ekranda görünen ve `/photos/...` ile sunulan şey olarak kalır.

Eski bir adres (kaydedilmiş `…png` bağlantısı) artık kare bulmaz ve sayfa bugünkü "Fotoğraf
bulunamadı" kartını gösterir. İki kural yerine tek kural: adres kimliktir.

### 2. Hatanın sebebi kaydın kendi cümlesidir (madde 79)

Üretim başarısız olunca kayda düşen satır zaten hatayı taşıyor; kimse okumuyordu. Artık:

- motor, satırı **kaç denemeden sonra** pes ettiğini de yazar: `CUDA out of memory — 3 kez denendi`;
- galeri satırı katman katman `errors` alanını taşır;
- detay, açık katmanın hatasını kırmızı alanın içinde **tek satır** olarak yazar.

Sebep uydurulmaz: motorun kendi çıktısı ile deneme sayısı, başka hiçbir şey. Galeride sebep
görünmez — orada yalnız hap durur (madde 79'un son cümlesi).

Kırmızı alanın içi tasarımın dediği gibi olur: uyarı ikonu + **"Bu kare üretilemedi"** + sebep;
çerçeve ve zemin kırmızı (bugünkü kesikli kutu gider).

### 3. Sekme, katman hangi hâlde olursa olsun açılır

Bugün sekme yalnız katman üretilmişse açılıyor. Bundan sonra sekme, katman **plana girmişse**
açılır ve içeriği hâline göre değişir:

| Katmanın hâli | Görsel alan | Sağ sütun |
|---|---|---|
| üretildi | oynatıcı / fotoğraf | prompt düzenlenebilir + "Yeniden üret" |
| kuyrukta | karenin taşıdığı fotoğraf + canlı "<katman> kuyrukta" rozeti | boş prompt kutusu, ipucu: "üretim sırası gelince LLM yazacak" |
| üretiliyor | dönen gösterge + canlı rozet | boş prompt kutusu |
| hata | kırmızı alan + sebep | prompt salt okunur + "Tekrar dene" |

Hiç istenmemiş katmanın sekmesi (kare video istemediyse Video) bugünkü gibi pasif kalır.

### 4. Tekrar dene aynı işi tekrar dener; prompt oynanmaz

"Tekrar dene" karenin kırmızı katmanını olduğu gibi kuyruğa geri koyar — "üret = ekle"nin tek
istisnası (madde 68), bugünkü davranış. Buton mor, onay sormaz, basıldıktan sonra "Kuyruğa eklendi"
deyip pasifleşir; Görev 25'in butonuyla aynı kalıp.

**Madde 79'un "prompt düzenlenip denenebilecek" yarısı bu görevde karşılanmıyor** ve bilerek
bırakılıyor: işin prompt'u planda duruyor, "Tekrar dene" planı hiç yeniden yazmıyor. Kutuyu
düzenletip eski sözlerle üretmek, kullanıcıya yalan söylemek olurdu. Düzenlenmiş sözlerle üretmenin
yolu zaten var — Görev 25'in "Yeniden üret — yeni kare"si — ama o üretilmiş bir katman ister; hatalı
karede yoktur. Planın işini yerinde değiştirmek plan deposuna yeni bir yetenek eklemek demek ve bu
görevin işi değil. Kırmızı karede kutu salt okunur.

### 5. Kopya kare kuyruktayken kendi sayfasını gösterir (madde 81)

Kopya kare fotoğrafı kaynağından paylaşır, o yüzden görsel alan zaten dolu görünür — tasarımın
istediği bu. Üstüne canlı rozet gelir ("video kuyrukta"), bekleyen katmanın prompt kutusu boş durur
ve neden boş olduğunu söyler. Gezinme dizisi değişmez: kopya kareler dizide, kendi kimlikleriyle.

### 6. Yıkıcı buton üç hâli ayırır

Madde 80 kareyi tümden silmeyi Foto sekmesine bağlamış, iki istisna saymıştı. Kural iki sorudan
çıkar — kopya olduğunu söyleyen bir bayrak yok, olması da gerekmiyor:

**Silmek diskten bir dosya götürüyor mu?** Yalnız fotoğrafı kendinin olan karede götürür
(`P0_1.png` gibi kendi adını taşıyan dosya). Kopyanın tuttuğu fotoğrafı kaynağı da tutuyor, bekleyen
karenin ise hiç dosyası yok (madde 101).

**Bir şey bekliyor mu?** Bekleyen katmanı olan kare kuyruktadır; hatalı olan değildir.

| Kare | Buton | Onay |
|---|---|---|
| fotoğrafı kendinin | "Sil" | sorar (bugünkü) |
| kendi dosyası yok, katman bekliyor (kuyruktaki kopya, bekleyen kare) | "Kuyruktan çıkar" | sormaz |
| kendi dosyası yok, bekleyen de yok (hatalı kare, hatalı kopya) | "Kareyi sil" | sormaz |

Son satır bugünkü davranışı değiştirir: hatalı kare bugün "Kuyruktan çıkar" diyor, oysa kuyrukta
değil — üretimi bitti ve başarısız oldu. Tasarımın hatalı kare için kullandığı sözcük "Kareyi sil"
(madde 80) ve bu görev hatalı karenin detayını yazdığı için düzeltme buraya ait.

Üçü de dolgusuz kırmızı (madde 83).

## Nasıl görülür

1. Kopya kareyi galeriden aç → adres kimliğini taşıyor, sayfa kopyayı gösteriyor: kaynağın
   fotoğrafı, canlı "video kuyrukta" rozeti, boş video prompt kutusu.
2. "Kuyruktan çıkar" → onay çıkmıyor, kopya galeriden gidiyor, kaynağın videosu yerinde.
3. Hatalı kareyi aç → kırmızı alanda "Bu kare üretilemedi" ve altında motorun kendi cümlesi + kaç
   kez denendiği.
4. "Tekrar dene" → onay yok, buton "Kuyruğa eklendi" oluyor, kare kuyruğa dönüyor.

## Testler

**Arka uç:** hata satırı deneme sayısını da yazar · galeri satırı katmanın hatasını taşır · silme
kimlikle çalışır ve aynı fotoğrafı paylaşan iki kareden yalnız isteneni gider · tekrar dene kimlikle
çalışır · sıra kimlik listesi kaydeder · bilinmeyen kimlik 404.

**Ön yüz:** galeri kareyi kimliğiyle açar · kopya karenin sayfası kaynağın fotoğrafını ve canlı
rozeti gösterir · bekleyen katmanın sekmesi açılıyor ve kutusu boş, ipucu yazıyor · hatalı katmanın
alanı sebebi yazıyor · "Tekrar dene" çağrılıyor ve basınca "Kuyruğa eklendi" · kendi dosyası olmayan
kare onay sormadan çıkıyor · buton metni üç hâlde ayrışıyor.

## Kapsam dışı

- **Prompt'u düzenleyip aynı kareyi tekrar denemek** — karar 4.
- **Galeri karosunun görünüşü** — kopya kare galeride bugünkü kalıbıyla çizilir; bu görev detay
  sayfasının işi.
- **"Kare" dili ve pencere genişliği** — Görev 31 ve 33.

## Riskler

- **Adres değişikliği geniş dokunuyor:** galeri, sıra, tekrar dene ve silme aynı anahtara geçiyor.
  Testler her ucu ayrı tuttuğu için kırılan yer sessiz kalmaz; yine de bu görevin en büyük parçası
  bu.
- **Eski bağlantılar ölür.** Uygulama yerel bir araç, adresler paylaşılmıyor; karşılığında iki
  ayrı adresleme kuralı taşımaktan kurtuluyoruz.
