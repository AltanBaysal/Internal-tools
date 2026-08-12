# Queen Editor v5 · Görev 5 — Panel yeni adını alır · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 2, Görev 5 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
9, 13, 14, 61 (+ öne çekilen 42) · **Tür:** yalnız ön yüz.

## Neden

Panel bugün **yaptığı işi** söylüyor: "Üretime ekle". Tasarım v3'te aynı yerde beş panel yan yana
duracak ve her biri **ürettiği şeyi** söyleyecek — fotoğraf, video, ses. Ad ürettiği şeye dönmezse
video paneli geldiğinde iki panelin adı da eylem olur ("Üretime ekle" / "Video üretime ekle") ve
şerit okunmaz hâle gelir. Bu görev, ad kalıbını üç panelden birincisinde kurar.

Buton adı da aynı sebeple değişiyor: **"Kuyruğa ekle"** bütün panellerde aynı kalacak, panelleri
ayıran şey başlık ve butonun önündeki katman ikonu olacak.

## Bugün ne var

| Yer | Bugünkü metin |
|---|---|
| Şerit ikonunun adı (ipucu) | "Üretime ekle" |
| Panel başlığı | "ÜRETİME EKLE" (aynı dize, büyük harfe çevrilerek) |
| Ana buton | "Üretime ekle", önünde artı ikonu |
| Şerit ikonu | artı işareti |
| Boş galeri ikinci satırı | "Prompt'ları yaz, Üretime ekle'ye bas — fotoğraflar burada belirecek" |
| Boş kuyruk kartı | "Üretime ekle panelinden kare gönder." |

Butonun ara hâli "Ekleniyor…" ve önündeki dönen gösterge bugünkü hâliyle kalır (madde 14 bunu
açıkça korur).

## Ne olacak

| Yer | Yeni metin | Madde |
|---|---|---|
| Şerit ikonunun adı | "Fotoğraf üret" | 7, 13 |
| Panel başlığı | "Fotoğraf üret" (büyük harf stili korunur) | 13 |
| Ana buton | "Kuyruğa ekle", önünde fotoğraf ikonu | 14 |
| Şerit ikonu | fotoğraf çerçevesi | 9 |
| Boş galeri ikinci satırı | "Prompt'ları yaz, Kuyruğa ekle'ye bas — fotoğraflar burada belirecek" | 61 |
| Boş kuyruk kartı | "Fotoğraf üret panelinden kare gönder." | 42 |

## Kararlar

### 1. Şerit adı ile panel başlığı bu panelde aynı dizedir

Madde 40 kuyruk paneli için ikisini ayırıyor — şeritte "Kuyruğu takip et", başlıkta "Kuyruk". Foto
paneli için böyle bir ayrım hiçbir maddede yok: madde 7 şerit ikonunu "fotoğraf üret" diye anıyor,
madde 13 başlığı "Fotoğraf üret" diyor. Aynı dize.

Bu yüzden şeridin bugünkü yapısı — panel listesindeki tek ad hem ipucu hem başlık olur — **bu
görevde bozulmaz**. Ayrım gerçekten gerektiğinde (Görev 9, kuyruk paneli) orada açılır; bugün
açmak, tek kullanıcısı olmayan bir alan eklemek olur.

### 2. Başlığın büyük harf stili korunur

Madde 13 `görsel` damgalı ve **sözcüğü** değiştiriyor: "Üretime ekle" → "Fotoğraf üret". Stil için
tek işaret, maddenin bugünü betimlerken "büyük harfli küçük başlık" demesi — bir talimat değil,
bugünün tarifi.

Karşı işaret de var: madde hem bugünkü dizeyi "ÜRETİME EKLE" diye, tasarımdakini "Fotoğraf üret"
diye yazıyor. Yine de stil değiştirilmiyor, iki sebeple:

- Aynı büyük-harf kalıbı panelin **bütün alan etiketlerinde** kullanılıyor (MODEL · PROMPT LİSTESİ ·
  NEGATİF PROMPT · VARYANT). Yalnız başlığı küçük harfe indirmek, hiçbir maddenin istemediği bir
  görsel kırılma yaratır.
- Fark belgesinin kendi kuralı: cevabı yoksa uydurulmaz. Stil sorusunun cevabı yok.

**Bu karar Görev 9'da yeniden bakılır:** madde 40 kuyruk başlığına dokunduğunda iki başlık aynı
kalıbı paylaştığı için karar ikisi için birden verilir.

### 3. Madde 42 bu göreve çekilir

Yol haritası madde 42'yi (boş kuyruk kartının metni) Görev 10'a koyuyor. Ama o metin **bu görevin
yeniden adlandırdığı paneli tırnak içinde anıyor**: Görev 5'ten sonra kuyruk paneli var olmayan bir
panele yönlendirir ve bu, beş görev boyunca ekranda durur. Yeniden adlandırmanın kendi artığını
kendisi temizler; Görev 10 maddeyi yapılmış bulur ve o gözü "iş çıkmadı" diye kapatır.

Kuyruk panelinin geri kalanına (başlık, tür kartları, kart sırası) dokunulmaz — onlar Görev 9-10'un
işi.

### 4. Butonun önündeki ikon katmanın ikonudur

Madde 14: *"Aynı etiket video ve ses panellerinde de kullanılacak, önlerinde kendi katman
ikonlarıyla."* Etiket bütün panellerde aynı olduğuna göre butonu ayıran tek şey ikondur; artı
işareti hiçbir katmanı göstermez. Foto panelinin butonu **şeritteki fotoğraf ikonunun aynısını**
taşır — böylece "bu buton şu paneli besliyor" bağı ikonun kendisinden okunur.

### 5. İkonlar kendi dosyasına taşınır

Fotoğraf ikonu artık iki yerde çiziliyor (şerit + buton), bu yüzden tek bir yerde yaşamalı. Şeridin
üç ikonu `features/photo_generation/glyphs.jsx`'e taşınır; dosyanın cevapladığı tek soru: **bu
aracın ikonları neye benziyor.**

`vendor/` seçeneği yok — orası tasarım projesinden birebir gelen dosyaların yeri ve elle
düzenlenmez. `shared/` de bugün doğru değil: ikonların hepsi tek feature'ın içinde kullanılıyor.
Video ve ses kendi feature'ları olarak açıldığında (Blok 5-6) paylaşılan ikonlar `shared/`'a taşınır
— o taşıma, ikinci kullanıcı gerçekten var olduğunda yapılır.

### 6. Panelin iç kimliği de katmanın adına döner

Şerit panelleri bugün `add` / `queue` / `agent` kimlikleriyle anılıyor ve ikon bu kimlikten
seçiliyor. `add` artık paneli tarif etmiyor — kimlik `photo` olur, ikonun adıyla aynı. Kullanıcı
bunu görmez; kazanç, "hangi ikon hangi panelin" sorusunun tek sözcükle cevaplanması ve video/ses
panelleri geldiğinde kimliklerin katman adlarıyla (arka uçtaki `photo`/`video`/`audio`) aynı dili
konuşması.

### 7. İkonun kimliği `data-glyph` özniteliğidir

Bir SVG'nin "fotoğraf çerçevesi mi" olduğu DOM'dan okunamaz; test edilebilir olan, **hangi ikonun
çizildiği**. Her ikon `<svg data-glyph="photo">` gibi bir kimlik taşır. Erişilebilirlik açısından
ikon bugünkü gibi `aria-hidden` kalır — butonun okunabilir adı zaten var, ikonun ikinci kez
seslendirilmesi gürültü olur.

## Nasıl görülür

1. Proje açılınca sağdaki panelin başlığı "Fotoğraf üret", şeritteki ilk ikon fotoğraf çerçevesi.
2. Formun altındaki mor butonda "Kuyruğa ekle" yazıyor, önünde aynı fotoğraf ikonu; basılınca
   "Ekleniyor…" oluyor.
3. Boş projede galerinin ikinci satırı butonun yeni adını söylüyor.
4. Kuyruk paneli boşken "Fotoğraf üret panelinden kare gönder." diyor.
5. Ekranın hiçbir yerinde "Üretime ekle" geçmiyor. Eski adı anan **kod yorumları** da düzeltilir —
   yorumun koda uymaması repo kuralıyla yasak.

## Testler

Hepsi ön yüz (vitest + jsdom); arka uçta bu görevin işi yok ve `pytest` dosyalarına dokunulmaz.

| Dosya | Test |
|---|---|
| `SidePanel.test.jsx` | şerit ilk ikonun adı "Fotoğraf üret" ve açılışta o seçili · açık panelin başlığı "Fotoğraf üret" · ilk ikon fotoğraf ikonunu çiziyor |
| `GeneratePanel.test.jsx` | ana buton "Kuyruğa ekle" diyor · butonun ikonu şeritle aynı fotoğraf ikonu |
| `Gallery.test.jsx` | boş galerinin ikinci satırı butonun yeni adını söylüyor |
| `QueuePanel.test.jsx` | boş kuyruk kartı "Fotoğraf üret panelinden kare gönder." diyor |

Var olan testlerdeki "Üretime ekle" geçişleri yeni metne çevrilir — bunlar yeni test değil, aynı
davranışın yeni adıdır.

## Kapsam dışı

- Şeridin zemini, hücre ölçüsü ve seçili işareti (madde 8) — **Görev 11**.
- Video ve ses ikonları ile panelleri (madde 7'nin kalanı) — **Görev 14, 20**.
- Kuyruk panelinin başlığı, tür kartları, "Kuyruğu boşalt"ın yeri (madde 34-41) — **Görev 9**.
- Panelin hata ve onay metinleri (madde 15-18) — **Görev 6**.
- "Fotoğraf" sözcüğünün içerik birimi olarak "kare"ye dönmesi (madde 104) — **Görev 31**. Bu
  görevde boş galeri satırının **yalnız buton adı** değişir; "fotoğraflar burada belirecek" olduğu
  gibi kalır, madde 61 de yalnız onu istiyor.

## Riskler

- **Başlığın büyük harf stili** (karar 2) yanlış okunmuş olabilir. Bedeli düşük: tek satır CSS ve
  Görev 9'da iki başlık için birden verilecek karar.
- **Fotoğraf ikonunun çizimi** tasarımın birebir kopyası değil — tasarım ikonun *ne olduğunu*
  söylüyor, çizimini vermiyor. Kit'in kendi diliyle çizilir (14×14 kutu, `currentColor`, 1.5
  yuvarlatılmış çizgi) ve `vendor/` dokunulmadan kalır.
