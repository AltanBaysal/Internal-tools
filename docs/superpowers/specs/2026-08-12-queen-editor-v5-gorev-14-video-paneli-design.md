# Queen Editor v5 · Görev 14 — Video üret paneli · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 5, Görev 14 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
23, 24, 28, 29 · madde 7'nin ikinci adımı · **Tür:** arka uç + ön yüz.

## Ne olacak

Şeride **video ikonu** ve **"Video üret"** paneli gelir:

- model satırı (bilgi, seçim değil), **kapsam radyosu** — "Videosu olmayanlar" ve "Seçili kareler",
  her satırın sağında o kapsamdaki kare sayısı; seçili olan vurgulu, öteki soluk,
- sabit süre bilgisi (**her video 5 saniye**, ayarı yok),
- mor **"Kuyruğa ekle"**, altında tahmin satırı ("9 video üretilecek — her kare kendi videosunu
  alır."),
- en altta "Video prompt'u otomatik: LLM her fotonun kendi prompt'undan yazar. Detayda okunur,
  düzenlenir.",
- ara hâl (buton pasif + "Ekleniyor…"), yeşil onay kartı ("6 video kuyruğa eklendi"), ve boş kapsam
  cümlesi ("Tüm karelerin videosu var — üretilecek bir şey yok.") — hata rengi yok.

Galeride seçim varken radyo kendiliğinden "Seçili kareler"e geçer; seçim yokken o satır soluktur.

## Kararlar

### 1. Bu feature zaten üretim feature'ı — video ikinci bir tane açmaz

Kuyruk, katmanlar, adlandırma ve motor Görev 3'ten beri **üç türün de** kuralları ve hepsi
`photo_generation`'ın domain'inde. Video için ikinci bir feature açmak, o feature'ın bunları import
etmesi demek olurdu — `feature ↛ feature` yasağının tam ortası.

Video'nun paneli ve "şu işleri kuyruğa koy" senaryosu bu yüzden **aynı feature'a** girer. Klasörün
adı artık dar kalıyor (`photo_generation`, oysa içerik üretimin kendisi); **adlandırma borcu olarak
kaydedilir** ve bu koşuda yeniden adlandırılmaz — kırk dosyalık bir import taşıması, sırada duran
işin hiçbirini ilerletmez.

### 2. Varyant kutusu bu görevde yok — kopya kareyle birlikte gelir

Tasarımın panelinde varyant kutusu var, ama varyantın fazlası **kopya kare doğurmak** demek (madde
25) ve bir kareye ikinci video takılamaz (Görev 1'in yuva kuralı). Yani kutu, kopya kare kuralı
olmadan yalan söyler: kullanıcı 3 yazar, iş 1 tane girer.

Kutu ve kopya kuralı **birlikte, Görev 15'te** gelir. Bu görevde her kare **bir** video işi alır ve
tahmin satırı bunu birebir söyler.

### 3. Kapsam sunucunun cevabı, panelin tahmini değil

"Videosu olmayanlar" kaç kare eder — bunu bilen yer galeriyi ve katmanları gören arka uçtur. Panel
sayıyı **galeri listesinden** okur: liste zaten her karenin taken katmanlarını (`layers`) taşıyor,
dolayısıyla "videosu yok" sorusunun cevabı ekranda hazır. Yeni uç açılmaz.

Seçili kapsamın sayısı da aynı listeden: galeride seçili kareler, videosu olmayanlarla kesişir.

### 4. Boş kapsam hata değildir

Kapsam boşken buton pasif ve tahmin satırının yerinde "Tüm karelerin videosu var — üretilecek bir
şey yok." durur. Kırmızı yok: yapılacak iş kalmaması bir arıza değil, bir sonuç.

### 5. Seçim paneli değil galeriyi izler

Radyo galerideki seçime uyar (madde 24). Seçim galerinin kendi durumu; panel onu **prop olarak**
alır, çünkü iki yerde iki seçim tutmak ikisinin ayrışması demektir.

## Nasıl görülür

1. Şeritte fotoğraf ikonunun altında video kamera ikonu var; basınca "Video üret" paneli açılıyor.
2. Videosu olmayan 9 kare varken kapsam satırı "9" diyor, tahmin satırı "9 video üretilecek — her
   kare kendi videosunu alır." diyor.
3. Galeride kare seçilince radyo kendiliğinden "Seçili kareler"e geçiyor.
4. "Kuyruğa ekle"ye basınca buton "Ekleniyor…" oluyor, sonra yeşil "9 video kuyruğa eklendi" kartı
   çıkıyor.
5. Bütün karelerin videosu varken buton pasif ve cümle "üretilecek bir şey yok" diyor.

## Testler

**Arka uç:** videosu olmayan kareler için video işi planlanır ve kuyruğa girer · videosu olan kare
kapsama girmez · seçim verildiğinde yalnız o kareler · kapsam boşken sıfır iş eklenir ve kuyruk
başlatılmaz · eklenen işler `type: "video"` taşır ve foto işlerinin arkasına girer.

**Ön yüz:** panel kapsam sayılarını gösterir · seçim varken radyo ona geçer · boş kapsamda buton
pasif ve cümle doğru · ekleme ara hâli ve onay kartı · şeritte video ikonu ve paneli.

## Kapsam dışı

- **Varyant kutusu ve kopya kare** (25, 26) — **Görev 15**.
- **Prompt'un yazılması** (27) — **Görev 16**; bu görevde panelin dip notu bunu söyler, iş
  prompt'suz kuyruğa girer.
- **Videonun gerçekten üretilmesi** (23'ün üretim yarısı) — **Görev 17**.
- **Galerideki "video kuyrukta" hapı ve rozet** (58) — **Görev 18**; hap kalıbı Görev 7'de kuruldu,
  video işi kuyruğa girince kendiliğinden çizilecek veri Görev 18'de gelir.

## Riskler

- **Klasör adının borç kalması** (karar 1) belgelerle koda arasında bir tutarsızlık bırakıyor.
  Kayıt altında; taşıma, roadmap bitince tek mekanik commit'te yapılabilir.
