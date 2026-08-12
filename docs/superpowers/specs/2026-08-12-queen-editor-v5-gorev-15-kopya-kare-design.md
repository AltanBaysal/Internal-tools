# Queen Editor v5 · Görev 15 — Kapsam ve kopya kare kuralları · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 5, Görev 15 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
25, 26, 100, 102 · **Tür:** arka uç + ön yüz.

## Neden

Görev 14 her kareye **bir** video takıyor. Ama kullanıcı aynı fotodan birkaç video denemek
isteyebilir ve videosu olan kareye ikinci video takılamaz — yuva dolu (Görev 1). Tasarımın cevabı
**kopya kare**: fazlası yeni bir kare olarak galeriye girer, kaynağın fotoğrafını paylaşır ve kendi
videosunu alır. Hiçbir kare ezilmez.

## Ne olacak

Panelde **varyant kutusu** doğar. Kuyruğa eklenirken:

| Kare | Varyant | Sonuç |
|---|---|---|
| Videosu yok | 1 | video karenin **kendisine** takılır |
| Videosu yok | 3 | biri kendisine, **iki kopya kare** doğar |
| Videosu var | n | **n kopya kare** doğar, kaynağa dokunulmaz |
| Fotosu yok (bekleyen/çalışan) | — | atlanır |

Tahmin satırı çarpmayı söyler: 3 kare × 3 varyant → "9 video üretilecek" (madde 23'ün örneği).

Kopya kare kaynağın **hemen yanında** durur, foto **dosyasını paylaşır**, ve yalnız üretilen
katmana kadarını taşır: video kopyası foto + video olur, **ses gelmez**.

## Kararlar

### 1. Kopya kare gerçek bir karedir — kaydı da öyle

Kopya, kaynağın fotoğraf dosyasını gösteren kendi **foto satırıyla** doğar. Böylece galeri onu
kendiliğinden çizer, detay sayfası açar, sıralaması tutulur ve silme kuralları (Görev 1) olduğu
gibi işler: paylaşılan dosya, onu tutan son kare gidene kadar diskte kalır.

Yeni bir "kopya" kavramı, bayrağı ya da alanı **açılmaz**. Kopya olmanın tek izi, foto dosyasının
başka bir kareyle aynı olması — ve o zaten dosya adının kendisinde duruyor.

### 2. Kimliği kaynağın prompt numarasının bir sonraki varyantıdır

Kopya `P{numara}_{varyant}` şemasında kaynağın **numarasını** korur ve o numaranın **en büyük
varyantının bir fazlasını** alır. Ad böylece hangi prompt'tan geldiğini söylemeye devam eder —
adlandırma şemasının zaten söylediği şey (Görev 2).

Aradaki boşluklar doldurulmaz, hep tepeden devam edilir: numaraların kuralı da bu (`next_number`) ve
sebebi aynı — silinmiş bir varyantın adı yeniden kullanılırsa aynı ad iki ayrı işi gösterir, üstelik
tarayıcı eski fotoğrafı kalıcı önbellek başlığıyla tutuyor olabilir.

Kullanılan varyantlar plandaki ve kayıttaki **bütün** kimliklerden okunur: silinmiş kare de kaydında
durduğu için adını korumaya devam eder.

### 3. Kopya kaynağın hemen üstüne yazılır

"Kopyalar orijinalin hemen yanında duracak" — galeri sırası artık üretim sırası da olduğuna göre
(Görev 8) bu yalnız görünüş değil, **sıra** kararı. Kopya, sıra dosyasında kaynağın hemen **üstüne**
girer. İki sebep: galerinin kendi kuralı en yeni üstte ve kopya kaynağından yenidir; üretim galeriyi
ayağından okuduğu için de sıra kaynak → kopyaları olur, panelin ima ettiği sıranın aynısı.

Sıra dosyasına o anki **galeri sırasının tamamı** yazılır, kopyalar araya girmiş hâliyle. Sebebi:
hiç sürüklenmemiş projede sıra dosyası boştur ve yalnız kopyalar yazılsaydı geri kalan her kare
"sırada yok" sayılıp galerinin tepesine çıkardı. Yazılan şey kullanıcının zaten baktığı sıra —
`save_order` sürüklemede ne yapıyorsa o.

### 4. Varyant yalnız üretilen katmana kadarını taşır

Video kopyası foto + video taşır, **ses taşımaz** (madde 102). Bu görevde uygulanışı basit: kopya
yalnız foto satırıyla doğar ve video işi kuyruğa girer. Sesin kopyaya gelmemesi, hiçbir şey
yapmamakla sağlanır — bir şey kopyalanmıyor, yeni kare kendi katmanlarını kendi üretiyor.

### 5. Videolu kare kapsama yalnız seçimle girer

Panelin iki kapsamı var ve adları kararı kendileri veriyor: **"Videosu olmayanlar"** videosu olan
kareyi almaz — adı bunu söylüyor. **"Seçili kareler"** ise fotosu inmiş her kareyi alır, videosu
olsun olmasın: kullanıcı bir kareyi eliyle işaretlediyse "bunu" demiştir, ve madde 25'in "zaten
videosu olan karenin bütün varyantları" cümlesinin başka yolu yok.

Sunucu tarafında tek fark bu: `files=None` videosuzları, verilmiş liste ise fotosu inmiş her seçileni
kapsar.

### 6. Kapsamın "atlanır" kuralı zaten yerinde

Madde 26 (bekleyen ve çalışan kareler atlanır) Görev 14'te kuruldu: kapsam yalnız fotosu inmiş
kareleri alıyor. Bu görevde iş çıkmıyor, teyit ediliyor.

### 7. Galeri kare başına tek satır çizer

Görev 14'ten kalan bir kusur: plan artık kare başına birden çok iş tutuyor (foto işi + video işi) ve
galeri planı satır satır okuduğu için videosu kuyruğa girmiş kare **iki kez** çiziliyor. Kural
`list_frames`'in kendi cümlesinde zaten yazılı — "bir karenin galeride olup olmadığına yalnız foto
yuvası karar verir" — kod onu uygulamıyor: galeri yalnız **foto işlerinden** satır üretir, video ve
ses işleri o karenin katmanı olarak zaten görünür.

Kopya karenin planda foto işi yok; o, kayıttaki foto satırından çiziliyor (karar 1) — yani bu kural
kopyayı galeriden düşürmez.

## Nasıl görülür

1. Panelde varyant kutusu var; 1 yazıp videosuz kareye eklenince kopya doğmuyor, video kareye
   takılıyor.
2. 3 yazınca galeride kaynağın hemen üstünde iki kopya kare beliriyor, ikisi de kaynağın fotoğrafını
   gösteriyor.
3. Videosu olan kare galeride seçilip 1 varyant istenince kaynağa dokunulmuyor, bir kopya doğuyor.
4. Kopya karenin adı kaynağın prompt numarasını taşıyor, varyantı farklı.
5. Kopya kare silinince paylaşılan foto dosyası, kaynak durduğu sürece diskte kalıyor.

## Testler

**Arka uç:** varyant 1 videosuz kareye kopya doğurmaz · varyantın fazlası kopya doğurur · videolu
karenin bütün varyantları kopya olur · videolu kare yalnız seçimle kapsama girer · kopya kaynağın
foto dosyasını paylaşır · kopyanın kimliği kaynağın numarasının bir sonraki varyantı · kopya sıra
dosyasında kaynağın hemen üstüne girer ve dosyaya galerinin tamamı yazılır · kopya yalnız foto
satırıyla doğar (ses satırı gelmez) · varyant 1-26 dışındaysa reddedilir · galeri, videosu kuyruğa
girmiş kareyi bir kez çizer.

**Ön yüz:** varyant kutusu 1-26 arasını kabul eder · tahmin satırı kare × varyant sayar · seçim
kapsamı videolu kareyi de sayar · gönderim varyantı taşır.

## Kapsam dışı

- **Videonun üretilmesi** (Görev 17) ve **prompt'un yazılması** (Görev 16).
- **Kopya karenin galerideki hâli** — "video kuyrukta" hapı Görev 7'nin kalıbından geliyor, rozet
  **Görev 18**.
- **Yeniden üret ile doğan kopyalar** (madde 98, 99) — **Görev 25**.

## Riskler

- **Sıra dosyasına yazmak** `queue_videos`'u sıra dosyasının ikinci yazarı yapıyor. Kural
  bozulmuyor: yazdığı şey yine "kareler hangi sırada" — yeni bir kare doğuran her yol o soruyu
  cevaplamak zorunda. Bugün tek yazar olan `save_order` ile aynı soruyu, aynı biçimde cevaplıyor.
- **Boş sıra dosyasının dolması.** Kopya doğduğu an dosya artık galerinin tamamını tutuyor; bundan
  sonra gelen yeni kareler yine tepeye giriyor (`apply_order`'ın kuralı değişmedi), yani kullanıcı
  için görünen bir fark yok. Fark, sıranın artık yazılı olması — zaten baktığı sıra.
- **Kopya, kuyruk reddedilse bile doğmuş olur.** Başka projenin üretimi sürüyorsa `run_queue`
  reddediyor, ama kopya kareler ve işleri o an yazılmış oluyor. Görev 14'ün planı da aynı sırada
  çalışıyor: iş önce yazılıyor, sonra koşu isteniyor. Kaybolan bir şey yok — işler kuyrukta duruyor
  ve koşu tekrar başlatılınca yapılıyor.
