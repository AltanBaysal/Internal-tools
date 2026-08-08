# Queen Editor v4 · Madde 1 — Canlı kuyruk (arka uç)

**Tarih:** 2026-08-08 · **Yol haritası:**
[v4 Madde 1](../plans/2026-08-08-queen-editor-v4-roadmap.md) · **Kapsadığı kodlar:** G12, ve
P4 · P5 · G3'ün zemini · **Katman:** yalnız arka uç

## Amaç

Kuyruk, bir koşuya ait dondurulmuş bir listeden çıkıp **sürekli açık bir sıraya** dönüyor: üretim
sürerken kare eklenebiliyor, kuyruk boşalınca üretim kendiliğinden duruyor. Aynı turda hatalı kare
de kalıcı hâle geliyor — bugün yalnız sunucunun hafızasında duruyor ve sunucu yeniden başlayınca
kayboluyor (G12).

Bunun kod tarafındaki asıl kazancı şu: bugün üretimi başlatan **üç ayrı yol** var (yeni parti,
kaldığı yerden devam, tekrar dene) ve üçü de kendi dondurulmuş kare listesini taşıyor, yani "hata
olunca ne olur, duraklayınca ne olur" kuralı üç yerde birden duruyor. Üçü tek bir şeye iniyor:
**kuyruğu değiştir, sonra işçi boştaysa çalıştır.**

## Kapsam

**İçinde:** plan dosyasının sonuna ekleme; günlüğün kare durumlarını tutması; döngünün her turda
diskten okuması; kuyruk boşalınca durma; kuyruk uç noktasının hatalı kareleri de bildirmesi; silinen
fotoğrafın kuyruğa geri düşmesi hatasının kapanması.

**Dışında:** her türlü arayüz dokunuşu (galeri Madde 5'te baştan yapılıyor, şimdi dokunmak onu iki
kez elden geçirmek olur); durma kuralının değişmesi ve tekrar denenen karenin kuyruğun **sonuna**
gitmesi (Madde 8); proje açılınca kuyruğun kendiliğinden sürmesi (Madde 8); duraklat/devam
butonlarının yüzü (Madde 4).

---

## 1 · İki dosya, iki soru

Proje klasöründeki dosya sayısı değişmiyor; yalnız ikisinin içeriği genişliyor.

| Dosya | Cevapladığı soru | Nasıl yazılır |
|---|---|---|
| **plan** | Hangi kareler, hangi sırayla, hangi metinle istendi | Sonuna eklenir; kare çıkarılmaz |
| **günlük** | Her kareye ne oldu | Satır satır eklenir; satır hiç değiştirilmez |

### Plan

Bir kare artık kendi **negatif** metnini de taşıyor:
`{"number", "letter", "prompt", "negative", "seed"}`.

Gerekçe: bugün negatif planın tepesinde, tek alan olarak duruyor — çünkü bir plan tek bir koşuya
aitti. Kuyruk sürekli açık olunca ikinci parti farklı bir negatifle gelebiliyor, dolayısıyla negatif
karenin kendi özelliği olmak zorunda.

**Geriye uyum:** `negative` alanı olmayan kare, planın tepesindeki eski alandan okur. Drive'daki
mevcut projeler elle dokunulmadan çalışmaya devam eder.

Plan artık her partide baştan yazılmıyor, sonuna ekleniyor. Kare **çıkarılmıyor**: kuyruktan çıkarma
günlüğe satır yazarak yapılıyor (aşağıda), böylece planın "ne istendi" cevabı hiç bozulmuyor ve
çıkarılan karenin numarası kendiliğinden ölü kalıyor.

### Günlük

Her satır tek bir kare hakkında tek bir olay anlatıyor ve `status` alanı taşıyor:

| `status` | Anlamı |
|---|---|
| `done` | Kare üretildi, dosyası duruyor |
| `failed` | Kare patladı |
| `removed` | Bekleyen kare kuyruktan çıkarıldı — hiç üretilmedi |
| `deleted` | Üretilmiş fotoğraf silindi |
| `queued` | Kapanmış kare yeniden sıraya alındı (Tekrar dene) |

Okuma kuralı bugünküyle aynı: **bir dosya adı hakkında en son yazılan satır geçerli.**

`removed` ile `deleted` ayrı kelimeler çünkü ayrı olaylar: biri hiç üretilmemiş bir kareyi kuyruktan
çıkarmak, diğeri var olan bir dosyayı silmek. Madde 6'daki üç ayrı onay metni bu ayrımın üstüne
kurulacak.

**Diskte olmayan iki durum var, bilerek:**

- **`pending`** — kare planda var, günlükte hiç satırı yok. Bekleyen kareyi ayrıca yazmak, planın
  zaten verdiği cevabı bayrak olarak tekrarlamak olurdu.
- **`running`** — çalışan kare işçinin hafızasından geliyor, diske hiç yazılmıyor. Süreç ölürse
  gerçekten hiçbir şey çalışmıyordur; diske yazılsaydı ölü bir süreç "çalışıyor" görünürdü.

**Geriye uyum:** `status` alanı olmayan eski satırlar da okunur — `deletedAt` varsa `deleted`, yoksa
`done` sayılır. Migrasyon yok.

**Neden plana değil de günlüğe.** Plan tek parça yazılan bir dosya: bir karenin durumunu oraya
yazmak, her karede kırk karelik dosyayı baştan yazmak demek. Colab makinesi tam o anda ölürse plan
yarım kalır, okunamaz hâle gelir ve okunamayan plan boş plan sayıldığı için **kuyruğun tamamı**
gider. Günlükte aynı ölüm en fazla son satırı götürür. Ayrıca durumu hem plana hem günlüğe yazmak
aynı gerçeğe iki yazıcı vermek olurdu: fotoğraf inip günlüğe satırı yazıldıktan sonra plan
güncellenmeden ölünürse plan "bekliyor" der ve kare ikinci kez üretilir.

---

## 2 · Kuyruk kuralı: kapanmış kare geri dönmez

**Bugünkü kural:** kuyrukta kalan = plan eksi **var olan fotoğraflar**.

**Bunun bugün ürettiği hata:** bir fotoğrafı silince günlükteki silme satırı onu "var olanlar"dan
düşürüyor, dolayısıyla kare "hiç üretilmemiş" görünüyor ve kuyruğa geri giriyor. Bugün nadiren
görülüyor çünkü her yeni parti planı baştan yazıyor — plan kısa ömürlü. Plan kalıcı ve büyüyen bir
kuyruğa dönüşünce hata sürekli tekrarlar: silinen her fotoğraf yeniden üretilmeye kalkar.

**Yeni kural:** bir karenin günlükte satırı varsa **kapanmıştır** ve kuyruğa dönmez — `done`,
`failed`, `removed`, `deleted`, hepsi kapanıştır. Kareyi yalnız `queued` satırı yeniden açar.

```
açık (bekliyor)  = planda var, günlükte hiç satırı yok  ·  ya da son satırı queued
kapalı           = son satırı done | failed | removed | deleted
```

Döngü sıradaki işi bu kuralla buluyor: **planın sırasında, açık olan ilk kare.** Açık kare yoksa
duruyor.

---

## 3 · Tek döngü

Bugün `start_batch`, `resume_batch` ve `retry_frame` üçü de kendi kare listesini hazırlayıp döngüye
veriyor. Döngü listeyi bir kez alıyor ve sonuna kadar geziyor — bu yüzden koşu sürerken kuyruğa iş
eklenemiyor.

Yeni hâlde döngü listeyi almıyor, **her turda diskten soruyor**: plan ve günlük okunur, açık olan
ilk kare üretilir, satırı yazılır, tur biter. Üretim sürerken plana eklenen kare bir sonraki turda
kendiliğinden görünür — canlı kuyruğun tek mekanizması bu.

Üç kullanım şu ikiliye iniyor:

| İşlem | 1. adım: kuyruğu değiştir | 2. adım |
|---|---|---|
| Yeni parti | plana kareleri ekle | işçi boştaysa çalıştır |
| Kaldığı yerden devam | (değişiklik yok) | işçi boştaysa çalıştır |
| Tekrar dene | günlüğe `queued` satırı yaz | işçi boştaysa çalıştır |
| Kuyruğu boşalt | açık her kareye `removed` satırı yaz | — |

Tekrar denenen kare bu maddede **planın kendi sırasında** üretilir; kuyruğun sonuna gitmesi Madde
8'in işi.

**Bir turun sırası** (değişmiyor, sadece nereden okuduğu değişiyor):

1. Duraklat istendiyse dur.
2. Açık ilk kareyi bul; yoksa bitir.
3. Durumu bildir (çalışan kare, bekleyenler, hatalılar).
4. Render et.
5. Dosyayı yaz, **sonra** günlüğe `done` satırını ekle. Sıra önemli: satır "bu fotoğraf burada"
   demektir, dosya olmadan yazılamaz.
6. Patlarsa günlüğe `failed` satırını ekle ve devam et; durma kuralı `policy.stop_reason`'da, bu
   maddede değişmiyor.

---

## 4 · Değişmeyen kurallar

**Numara ayırma.** Bir numara üç yerden birine takılıysa yeniden kullanılmaz: diskteki dosya, planın
ayırdığı kare, günlüğün gördüğü ad. `removed` ve `deleted` satırları da bir dosya adı taşıdığı için
o numaraları sonsuza dek ölü tutar. Kural aynen duruyor ve şimdi bir tarafı daha kapanıyor:
bugün "kuyruğu boşalt" planı temizleyerek numaraları serbest bırakıyor; artık `removed` satırı
yazdığı için bırakmıyor. Gerekçe: fotoğraflar tarayıcıya "bu adres asla değişmez" sözüyle veriliyor,
aynı ad ikinci bir prompt'a bağlanırsa tarayıcı eski görüntüyü göstermeye devam eder.

**Duraklatma.** Bayrak + ComfyUI interrupt, bugünkü gibi. Kesilen kare günlüğe satır yazmadığı için
açık kalır ve devam edilince yeniden üretilir — fark belgesi 8.1'deki karar bu.

**Tek işçi.** Başka bir projede üretim sürerken bu projeye ekleme yine reddedilir ("Zaten bir üretim
sürüyor"). Tasarım bu kısıttan hiç söz etmiyor, kaldıran bir karar da yok.

**Durma kuralı.** `policy.stop_reason` aynen kalıyor (üst üste 3 başarısız kare · model yükleyici
hatası). Tasarımın "aynı iş 3 kez denenir" kuralına geçiş Madde 8'de.

---

## 5 · Uç noktalar

Şekiller korunuyor; `/api/status`'ün alanları aynen duruyor ki mevcut arayüz çalışmaya devam etsin.

| Uç nokta | Değişen |
|---|---|
| `POST …/generate` | Aynı proje çalışırken artık 409 dönmez — kareler kuyruğun sonuna eklenir. 409 yalnız **başka** proje çalışıyorsa |
| `POST …/resume` | "Kalanları hesapla ve koş" değil, "işçiyi çalıştır". Açık kare yoksa 409 |
| `POST …/cancel` | Planı temizlemek yerine açık kareler için `removed` satırı yazar. Üretim akarken reddedilmesi (409) aynen kalıyor — bu, o an render edilen karenin yanlışlıkla `removed` yazılmasını da engelliyor, çünkü çalışan kare henüz satırsızdır ve "açık" görünür |
| `POST …/retry` | Günlüğe `queued` satırı yazar, işçi boştaysa çalıştırır |
| `GET …/queue` | `{pending, total}` → **`{pending, failed, total}`** — G12'nin kanıtlanabildiği yer |
| `POST …/photos/delete` | `deletedAt` satırı yerine `status: "deleted"` satırı yazar |
| `GET /api/status` | Alan listesi aynı |

**Geçici tuhaflık, bilerek bırakılıyor.** `total` artık "planda şimdiye kadar istenmiş her kare"
anlamına geliyor, dolayısıyla arayüzdeki "17 / 48" sayacı büyümeye devam eder. Payda Madde 4'te
zaten kalkıyor ("N kare bekliyor"); şimdi düzeltmek aynı kartı iki kez elden geçirmek olur.

---

## 6 · Testler

Arka uç `pytest`, sahte port'larla — ComfyUI yok, Drive yok, iş parçacığı yok (`spawn` senkron).

**Kuyruk kuralı**
- Silinen fotoğrafın karesi kuyruğa **dönmez** (bugünkü hata).
- `removed` satırı olan kare kuyrukta görünmez ve üretilmez.
- `failed` satırı olan kare kendiliğinden yeniden denenmez.
- `queued` satırı kareyi yeniden açar.
- `status` alanı olmayan eski satırlar doğru okunur (`deletedAt` → `deleted`, yoksa `done`).

**Canlı kuyruk**
- Döngü koşarken plana eklenen kare aynı koşuda üretilir.
- Kuyruk boşalınca döngü kendiliğinden biter.
- Aynı proje çalışırken ikinci ekleme 409 vermez; başka proje çalışırken verir.

**Kalıcılık**
- Patlayan kare günlüğe yazılır; işçi sıfırlandıktan sonra kuyruk uç noktası onu `failed` diye
  bildirir.
- Kesilen (duraklatılmış) kare satır yazmaz, açık kalır.

**Numara ayırma**
- `removed` satırı olan karenin numarası yeni partide yeniden kullanılmaz.
- `deleted` satırı olan fotoğrafın numarası yeniden kullanılmaz (bugünkü test korunur).

**Negatif**
- Kare kendi negatifiyle üretilir; farklı negatifle eklenen ikinci parti kendi negatifini kullanır.
- Negatifi olmayan eski kare planın tepesindeki alandan okur.

---

## 7 · Kabul kriteri

`pytest` yeşil ve şu üç cümle testlerle kanıtlanmış:

1. Üretim sürerken atılan ikinci parti kesinti olmadan kuyruğun sonuna diziliyor.
2. Sunucu yeniden başladıktan sonra da kuyruk uç noktası patlamış kareyi `failed` diye bildiriyor.
3. Silinen bir fotoğrafın karesi kuyruğa geri dönmüyor.

Arayüz bu maddede hiç değişmediği için ekranda görülecek bir şey yok; kırmızı karenin sayfa
yenilendikten sonra da yerinde durması Madde 5'te görünür hâle gelecek.
