# Queen Editor v5 · Görev 7 — Galeri kartının durum dili · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 2, Görev 7 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
54, 55, 56, 57 · **Tür:** yalnız ön yüz.

## Neden

Bugün bir karenin durumu **kartın görünüşünden tahmin ediliyor**: kesikli çerçeve bekliyor demek,
dönen gösterge üretiliyor, kırmızı çerçeve hata. Yazılı tek şey kartın **ortasındaki** "bekliyor" ve
"Çalışıyor" — yani durum, karenin göreceği yerin tam üstünde duruyor.

Tasarım bunu tersine çeviriyor: kartın ortası boş kalır (kesikli çerçeve zaten "piksel yok" der) ve
durum, kartın **köşesine** tek kalıpta bir hap olarak çıkar. Kazanç bu görevin ötesinde: hap
"katman + durum" der, yani video ve ses geldiğinde aynı köşede "video üretiliyor" yazacak. Bugün
tek türle kurulan kalıp, Blok 5-6'da yeni bir bileşen değil yeni bir **satır** olarak büyür.

## Bugün ne var

| Kare | Kartın ortası | Köşeler |
|---|---|---|
| Bekleyen | kesikli, %35 soluk, ortada "bekliyor" | sağ üst sıra numarası (soluk) |
| Çalışan | dönen gösterge + altında "Çalışıyor" | sağ üst sıra numarası |
| Hatalı | uyarı ikonu + "Tekrar dene" | sağ üst sıra numarası |
| Üretilmiş | fotoğraf | sağ üst sıra numarası |

Sol üstte yalnız seçim halkası var (imleç kartın üstündeyken ve seçim modunda görünür).

## Ne olacak

| Kare | Kartın ortası | Sol üst hap |
|---|---|---|
| Bekleyen | kesikli, soluk, **yazısız** | "foto kuyrukta" (soluk) |
| Çalışan | yalnız dönen gösterge, **yazısız** | "foto üretiliyor" (mor + yanıp sönen nokta) |
| Hatalı | uyarı ikonu + "Tekrar dene" (aynen) | "foto hata" (kırmızı) |
| Üretilmiş | fotoğraf | **hap yok** |

Hapın biçimi: koyu saydam zemin, 3 piksel köşe, 9 punto tek aralıklı. Bir karede aynı anda **tek**
hap olur.

Rozet düzeni üç düzleme ayrılır: sağ üst sıra numarası (bugün var), sol üst durum hapı (bu görev),
sağ alt sahiplik (Görev 18 ve 22). Seçim halkası sol üstü aldığında hap sol alta kayar.

## Kararlar

### 1. Hapın metni veri, kod değil

Hap iki sözlükten kurulur — biri katmanın sözcüğü, biri durumun sözcüğü:

| Katman | Sözcük |  | Durum | Sözcük | Renk |
|---|---|---|---|---|---|
| `photo` | foto |  | `pending` | kuyrukta | soluk |
| `video` | video |  | `running` | üretiliyor | vurgu + canlı nokta |
| `audio` | ses |  | `failed` | hata | kırmızı |

Video ve ses satırları **bugün yazılır** ama kullanılmaz: kalıbın tek olduğunu söyleyen şey bu, ve
Blok 5-6'da eklenecek şey kod değil çağrı olur. Katman anahtarları arka ucun kendi sözcükleridir
(`layers.PHOTO` · `VIDEO` · `AUDIO`) — Görev 5'te panel kimlikleri için verilen kararın aynısı.

Üretilmiş karenin hapı yoktur: tasarım üç durum sayıyor, dördüncüsünü kartın kendisi (fotoğraf)
anlatıyor. Sahiplik rozetleri sağ altta, kendi görevlerinde.

### 2. Dönen göstergenin yazısı `vendor/` içinde — o yüzden o parça kullanılmaz

"Çalışıyor" sözcüğü tasarım kitinin yükleme tutucusunun içinde yaşıyor ve `vendor/` **elle
düzenlenmez**. Sözcüğü çıkarmanın yolu dosyayı düzeltmek değil, o parçayı kullanmamak: çalışan
karenin tutucusu bizim tarafımızda çizilir — aynı sınıflar, aynı dönen gösterge, sözcük yok.

Bu, `vendor/`'ı ileride yeniden çekmenin önünü kapatmaz; kural zaten "uymayan şey bizim tarafımızda
düzeltilir" diyor.

### 3. İkisi de tek dosyanın işi

Hap ve yazısız tutucu aynı soruyu cevaplıyor: **bir karenin durumu ekranda nasıl çizilir.** İkisi de
`features/photo_generation/frame_status.jsx`'te durur; galeri ikisini de, detay sayfası tutucuyu
kullanır. Durumun sözlüğü tek yerde olunca, Blok 5-6'da video hapı eklemek o dosyaya bir satır
yazmak olur.

`glyphs.jsx`'e girmez — orası ikonların yeri, burası durumun. `shared/`'a da girmez: ikisi de bu
feature'ın içinde kalıyor.

### 4. Aynı sözcük detay sayfasından da kalkar

Madde 55 "Çalışıyor"un **iki yerde** çıktığını söylüyor: galeri kartı ve detay sayfasının bekleme
alanı. İkisi de aynı kit parçasını kullanıyor, dolayısıyla ikisi de aynı anda düzelir. Ayrı görevlere
bölmek, aynı sözcüğü iki turda kaldırmak olurdu.

Detayın **bekleyen** hâli (kesikli tutucu + "bekliyor" + "henüz üretilmedi") bu görevde
**dokunulmaz** — onu madde 82 ele alıyor ve o satırları silmiyor, opaklığını değiştiriyor
(**Görev 23**).

### 5. Hap, halka göründüğü her an sol alttadır

Madde 57 hapın **seçim modunda** sol alta kaydığını söylüyor; sebebi, onay halkasının sol üstü
almasıdır. Ama halka seçim modundan önce de görünüyor: imleç kartın üstüne gelince beliriyor
(tasarımın kendi kuralı). Kuralı sebebine bağlamak gerekir — **halka göründüğü her an hap sol
alttadır**, yani imleçle ve seçim modunda.

Yer değiştirme, halkanın görünürlüğü gibi CSS'te yaşar (`shared/app.css`); imleç hâli JS'in
bilmediği bir şey. Halkanın kendi görünürlüğü de bugün böyle ve test edilmiyor — bu da edilmez.

### 6. Hap tıklamayı yutmaz

Kartın üstündeki her şey tıklamaya ve sürüklemeye açık; hap yalnız yazı olduğu için işaretçi
olaylarını geçirir. Yoksa kartın sol üst köşesi ölü bir alan olur ve "neden buraya basınca bir şey
olmuyor?" sorusu doğar.

## Nasıl görülür

1. Bekleyen karenin ortasında yazı yok; sol üstünde soluk "foto kuyrukta" duruyor.
2. Sıra o kareye gelince hap "foto üretiliyor"a döner, yanında nokta yanıp söner; kartın ortasında
   yalnız dönen gösterge var, "Çalışıyor" yazmıyor.
3. Kare üretilince hap kaybolur, yerini fotoğraf alır.
4. Hatalı karede sol üstte kırmızı "foto hata"; kartın içindeki Tekrar dene aynen duruyor.
5. Bir kartın üstüne gelince onay halkası sol üstte belirir, hap sol alta iner — üst üste
   binmiyorlar.
6. Detay sayfasında çalışan karenin alanında da yalnız dönen gösterge var.

## Testler

| Dosya | Test |
|---|---|
| `Gallery.test.jsx` | bekleyen kartın ortasında yazı yok · üç durumun hapları tek kalıpta doğru sözcükle · üretilmiş karenin hapı yok · bir karede en çok bir hap · çalışan kartta dönen gösterge var, "Çalışıyor" yok |
| `PhotoDetail.test.jsx` | çalışan karenin alanında dönen gösterge var, "Çalışıyor" yok |

Var olan üç Gallery testi ("bekliyor" sayan) hapın sözcüğüne çevrilir — aynı davranışı yeni dille
sorarlar. `PhotoDetail.test.jsx:229` de aynı şekilde.

## Kapsam dışı

- **Sahiplik rozetleri** (madde 58) — video için Görev 18, ses için Görev 22.
- **Hatalı kartın Tekrar dene davranışı** (madde 67-69) — **Görev 19**. Bu görevde buton bugünkü
  yerinde ve bugünkü davranışıyla kalır.
- **Detayın bekleyen hâli** (madde 82) — **Görev 23**.
- **Sürükleme kuralları** (madde 59-60) — **Görev 8**; bu görev `üretilince sıralanabilir` ipucuna
  dokunmaz.
- **"Kare" diline geçiş** (madde 104) — **Görev 31**. Hapın sözcükleri tasarımın kendi sözcükleri;
  genel dil taraması sonda.

## Riskler

- **Hapın imleçle kayması** (karar 5) maddede yazmayan bir genişletme. Gerekçesi maddenin kendi
  sebebi; bedeli tek CSS kuralı ve yanlışsa geri alması bir satır.
- **Çalışan tutucunun kendi elimizle çizilmesi** (karar 2) kitin ileride değişmesi hâlinde iki
  görünümün ayrışmasına açık. Aynı sınıflar kullanıldığı için ayrışma yalnız kitin **içeriği**
  değişirse olur, biçimi değil.
