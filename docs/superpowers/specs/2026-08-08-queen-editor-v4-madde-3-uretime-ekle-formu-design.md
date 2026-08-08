# Queen Editor v4 · Madde 3 — Üretime ekle formu

**Tarih:** 2026-08-08 · **Yol haritası:**
[v4 Madde 3](../plans/2026-08-08-queen-editor-v4-roadmap.md) · **Kapsadığı kodlar:** P4-P11, P13,
G9 · **sapma:** format hatasının fazlasını söylemesi · **Katman:** ön yüz + arka uçta iki metin

## Amaç

Form paneli "üretimi başlatan yer" olmaktan çıkıp **kuyruğa iş atan yer** oluyor. Madde 1 arka uçta
bunu zaten mümkün kıldı; bu madde ekranı ona uyduruyor.

## 1 · Buton

**Üret** → **Üretime ekle**, parıltı ikonu yerine **artı**. Basınca buton kısa süre pasifleşir,
yanında dönen gösterge çıkar ve yazısı **"Ekleniyor…"** olur. Alanlar açık kalır — bugün üçü birden
kapanıyor.

Buton yalnız üç durumda pasiftir: liste boşken, ekleme sürerken, ve başka bir proje işçiyi tutarken.
**Üretim sürerken pasif değildir** — panelin hiç kilitlenmemesi bu maddenin ana kararı.

## 2 · Panel hiç kilitlenmez

`wf-panel--locked` kalkar. Kuyruk akarken prompt yazılıp eklenebilir; alanlar soluklaşmaz,
tıklanabilir kalır. Bunun arkasını Madde 1 hazırladı: aynı projenin akan kuyruğuna ekleme artık
reddedilmiyor.

`shared/app.css`'teki "dördüncü bloğu geri parlat" kuralı da kalkar — kilit olmayınca karşılığı
kalmıyor.

## 3 · Ekleme onayı ve hatası

Butonun altında, birbirini dışlayan iki satır:

| Durum | Görünen |
|---|---|
| Eklendi | Yeşil kart: **"✓ 48 kare kuyruğa eklendi"** — birkaç saniye sonra kendiliğinden kaybolur |
| Eklenemedi | Tek kırmızı satır: **"Kuyruğa eklenemedi"** |

Kaybolma süresi **4 saniye**. Tasarım "birkaç saniye" diyor; sabit bir sayı gerekiyor ve okumaya
yetip yolu tıkamayan aralık bu.

**Sayı sunucudan gelir.** Kaç kare eklendiğini uygulama kendi sayımıyla söylemez: `POST …/generate`
cevabına eklenen kare sayısı konur ve kart onu yazar. Sebep: paneldeki prompt sayacı bilerek
"önizleme, kural değil" olarak yazılmıştı; onaya rakam veren yer kuralın kendisi olmalı.

**Ekledikten sonra prompt listesi temizlenmez.** Kullanıcının yazdığı liste geri alınamaz biçimde
kaybolmamalı; yanlışlıkla ikinci kez eklemeyi yeşil onay kartı görünür kılar.

## 4 · Prompt × varyant hesabı kalkıyor

Butonun altındaki "12 prompt × 4 varyant = 48 foto" satırı kaldırılıyor. Yerini ekleme onayı
alıyor — ve onay gerçek sayıyı söylediği için tahmini satır zaten gereksizleşiyor.

## 5 · Format hatası tek satır

Kutu kırmızı çerçevelenir, altında **tek satır** durur ve **detay verilmez** — beklenen biçim,
örnek liste ve ham Python hatası artık basılmıyor. Metin sunucudan gelir (kural arka uçta):

| Sunucunun durumu | Metin |
|---|---|
| Metin okunamadı (liste değil, öğeler metin değil, sözdizimi bozuk) | `Format hatası — liste okunamadı` |
| Metin gerçekten boş ya da içinde dolu prompt yok | `Prompt listesi boş.` |

İkincisi arayüzden erişilemez (liste boşken buton pasif), ama sunucunun kendi kapısı olarak durur.

**Akan kuyruk etkilenmez:** hata form panelinin içinde kalır, hiçbir kare kuyruğa girmez, üretim
kesilmez. Bugün bu durum zaten oluşamıyordu çünkü panel kilitliydi.

Kutuya yazmaya başlayınca uyarı temizlenir (bugünkü davranış korunuyor).

## 6 · Varyant kutusu

**Aralık 1–26.** Tasarım 1–8 diyordu, kullanıcı 2026-08-08'de reddetti ve 26'yı tuttu; maddenin
geri kalanı tasarımın kuralıdır:

- Kutuya **26'dan büyük ya da 0** yazılamaz — tuş vuruşu kabul edilmez, değer olduğu gibi kalır.
- Yalnız rakam kabul edilir.
- Kutu boşaltılabilir (yazarken gerekli), ama **odak çıkınca boşsa 1'e döner**.
- **Hata durumu yoktur.** Varyant alanı kırmızıya dönmez, altına uyarı yazılmaz.

Sunucudaki 1–26 doğrulaması yerinde kalır — kural orada yaşıyor ve arayüz onun görüntüsü. Ama
arayüz artık geçersiz değer gönderemediği için o hata pratikte doğmaz; yine de gelirse "Kuyruğa
eklenemedi" satırında görünür.

## 7 · Boş galeri metni

*Bugün:* "Prompt'ları yaz, **Üret'e** bas — fotoğraflar burada belirecek."
*Bundan sonra:* "Prompt'ları yaz, **Üretime ekle**'ye bas — fotoğraflar burada belirecek."

## 8 · Testler

**Ön yüz** (`npm test`)
- Buton "Üretime ekle" diyor ve artı ikonu taşıyor.
- Üretim sürerken alanlar açık ve buton basılabilir.
- Basınca buton "Ekleniyor…" olup pasifleşiyor, alanlar açık kalıyor.
- Başarılı eklemede yeşil kart sunucunun verdiği sayıyı yazıyor; 4 saniye sonra kayboluyor.
- Başarısız eklemede tek satır "Kuyruğa eklenemedi" çıkıyor, yeşil kart çıkmıyor.
- Prompt × varyant satırı hiçbir durumda çıkmıyor.
- Varyant kutusuna 27 yazılamıyor; boş bırakılıp odak çıkınca 1 oluyor; kırmızı çerçeve olmuyor.
- Format hatasında kutu kırmızı, altında sunucunun tek satırı.
- Boş galeri yeni butonun adını anıyor.

**Arka uç** (`pytest`)
- Okunamayan liste tek satırlık "Format hatası — liste okunamadı" veriyor; örnek ve Python hatası
  metinde geçmiyor.
- `POST …/generate` cevabı eklenen kare sayısını taşıyor.

## 9 · Kabul kriteri

`pytest` ve `npm test` yeşil, `npm run build` koşuldu ve `dist/` aynı commit'te. Üç cümle
kanıtlanmış:

1. Kuyruk akarken forma yazılıp ikinci parti eklenebiliyor, alanlar hiç kilitlenmiyor.
2. Ekleme onayı sunucunun saydığı kare sayısını yazıyor ve kendiliğinden kayboluyor.
3. Format hatası tek satır; ne örnek liste ne Python hatası görünüyor.
