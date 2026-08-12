# Queen Editor v5 · Görev 2 — Dosya adları katman şemasına geçer

**Tarih:** 2026-08-12 · **Yol haritası:**
[v5 Görev 2](../plans/2026-08-12-queen-editor-v5-roadmap.md) · **Kapsadığı madde:** 97 ·
**Katman:** yalnız arka uç

## Amaç

Ad, karenin hangi prompt'tan ve hangi varyanttan geldiğini söylemekten çıkıp **hangi katmanları
taşıdığını** da söylüyor (madde 97):

```
P11_3.png                    yalnız fotoğrafı olan kare
P11_3_V1_0.mp4               videosu olan kare
P11_3_V1_0_S1_0.wav          sesi de olan kare
```

Her katman bir çift sayı taşıyor — **tur** ve **varyant**. Olmayan katman ada hiç yazılmıyor. Harf
varyantı sayıya dönüyor: `a=0, b=1, c=2, d=3`, yani bugünkü `11_d` yarın `P11_3`.

Görev 1 kimliği dosya adından ayırmıştı; bu görev **kimliğin biçimini** değiştiriyor. Tur sayıları
bu görevde hep `1` ve `0` — yeniden üretim ve varyant kopyası onları Görev 15 ve 25'te artıracak.
Buradaki iş şemanın kendisi ve okunması.

## Kapsam

**İçinde:** yeni doğan karelerin kimliğinin ve foto dosya adının yeni şemayla verilmesi; kimliğin
plana yazılması; ad ayrıştırmanın iki şemayı da okuması; numara ayırmanın iki şemada da işlemesi.

**Dışında:** tur numarasının artması (Görev 25); varyant kopyasının doğması (Görev 15); video ve ses
dosyalarının gerçekten üretilmesi (Blok 5-6); var olan dosyaların diskte yeniden adlandırılması
(aşağıda gerekçesiyle reddedildi); her türlü ekran dokunuşu.

---

## 1 · Kimlik artık hesaplanmıyor, plana yazılıyor

Görev 1'de kimlik plandaki `number` + `letter` çiftinden **hesaplanıyordu**. Şema değişince aynı
hesap eski karelere de yeni kimlik verirdi: `11_d` diye kaydedilmiş bir kare bir anda `P11_3`
olurdu ve sıra dosyasındaki `11_d` hiçbir kareyi göstermez hâle gelirdi — **kullanıcının düzenlediği
sıra kaybolurdu.**

Bu yüzden kimlik artık doğduğu anda **plan karesine yazılıyor**:

```
{"id": "P11_3", "number": 11, "variant": 3, "prompt": …, "negative": …, "seed": …, "model": …}
```

Kare artık `letter` yerine `variant` (tam sayı) taşıyor — tasarımın "harf varyantı sayıya dönecek"
kuralı budur. **Varyant üst sınırı 26'da kalıyor:** v4'te kullanıcı kararıyla konmuştu ve tasarımın
sayıya geçmesi o sınırı kaldıran bir karar değil.

**Geriye uyum:** `id` alanı olmayan bir plan karesi eski karedir; kimliği bugünkü kuralla
(`<sayı>_<harf>`) okunur ve dosyası da bugünkü adıyla durur. Migrasyon yok, yeniden adlandırma yok.

**Neden diskteki dosyalar yeniden adlandırılmıyor.** Üç sebep, üçü de ilke 1'in ("kullanıcının emeği
kutsaldır") altında: yeniden adlandırma Drive üzerinde toplu bir yazma turudur ve yarıda ölen bir
tur projeyi tutarsız bırakır; fotoğraf adresleri tarayıcıya "bu adres asla değişmez" sözüyle
veriliyor, ad değişince o söz bozulur; ve kazanç yalnız görseldir — iki şema yan yana sorunsuz
yaşar. Sonucu kullanıcı için şu: eski projelerde eski adlı kareler eski adlarıyla, o projeye yeni
eklenenler yeni şemayla görünür.

---

## 2 · Şema

| Parça | Anlamı | Bu görevde |
|---|---|---|
| `P{n}` | prompt numarası | bugünkü `number` |
| `_{v}` | foto varyantı | harf yerine sayı (`a`→0) |
| `_V{tur}_{varyant}` | video katmanı | üretim geldiğinde `V1_0` |
| `_S{tur}_{varyant}` | ses katmanı | üretim geldiğinde `S1_0` |

Kurallar:

- **Olmayan katman ada hiç yazılmaz.** Videosuz karenin adında `V` geçmez.
- **Kimlik, karenin foto parçasıdır** — `P11_3`. Katman parçaları o katmanın **dosya adına** girer,
  kimliğe değil; kimlik doğum anında verilir ve katman geldikçe değişmez (Görev 1'in kuralı).
- **Dosya adı = kimlik + katman parçaları + uzantı.** Foto `P11_3.png`, videosu
  `P11_3_V1_0.mp4`, sesi `P11_3_V1_0_S1_0.wav` — ses adı videosunun üstüne binerek büyür, çünkü ses
  o videoya bindirilidir.

## 3 · Numara ayırma iki şemayı da sayar

Bir numara bir kez kullanılır ve bir daha kullanılmaz — bugünkü kural (v4 Madde 1) aynen duruyor,
yalnız artık **iki ad biçimini birden** okumak zorunda. `11_d.png` de `P11_3.png` de 11'i tutar;
`P11_3_V1_0.mp4` de tutar, çünkü o da 11 numaralı prompt'un bir dosyasıdır.

Ayrıştırma tek yerde yaşar ve şemaya bakıp karar verir: ad `P` ile başlıyorsa yeni şema, değilse
eski. Şemaya uymayan ad (proje dosyaları, notlar) numara vermez — bugünkü davranış.

## 4 · Uç noktalar

Hiçbir uç noktanın şekli değişmiyor. Yeni üretilen dosyaların adı değişiyor, o kadar; arayüz adı
sunucudan aldığı gibi gösterdiği ve fotoğraf adresini de ondan kurduğu için dokunulacak bir şey yok.

## 5 · Testler

Arka uç `pytest`. **Full TDD:** her davranış için önce kırmızı test.

**Şema**
- Yeni kare kimliği `P{prompt}_{varyant}` biçiminde doğar; `a` varyantı 0 olur, `d` 3.
- Foto dosyası kimliğin `.png`'lisidir.
- Video dosyası kimliğe `_V1_0` ekler; ses dosyası videonun adının üstüne `_S1_0` ekler.
- Olmayan katman ada yazılmaz.

**Ayrıştırma**
- `P11_3.png` → 11; `11_d.png` → 11; `P11_3_V1_0.mp4` → 11.
- Şemaya uymayan ad numara vermez.

**Geriye uyum**
- `id` alanı olmayan plan karesi eski kimliğini korur ve dosyası eski adıyla durur.
- Eski ve yeni kareler aynı projede yan yana listelenir; sıra dosyası ikisini de tanır.
- Numara ayırma iki şemayı birden sayar: eski adlı 11 varsa yeni parti 12'den başlar.

## 6 · Kabul kriteri

`pytest` yeşil ve şu iki cümle testlerle kanıtlanmış:

1. Yeni üretilen kare `P{prompt}_{varyant}.png` adıyla iniyor ve kimliği o.
2. Eski adlı kareleri olan bir projeye yeni kare eklenince ikisi yan yana duruyor, numara
   çakışmıyor ve kullanıcının sırası bozulmuyor.
