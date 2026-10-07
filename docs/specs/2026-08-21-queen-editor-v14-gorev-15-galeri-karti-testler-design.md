# v14 · Görev 15 — Galeri kartının görsel hizalaması · **test turu**

**Kaynak:** yol haritası 15. madde · tasarım v4 fark listesi 60, 61, 62, 64, 65, 69, 73, 74, 75, 76.

On fark, tek ekran: galeri karosu. Altısı çizim, dördü karara bağlanıp kapanıyor.

## On farkın bugünkü karşılığı

| Fark | Ne diyor | Bugün | Bu turda |
|---|---|---|---|
| 60 | Sahiplik rozetleri sağ alttan **sol alta** | sağ altta | test |
| 61 | Rozetten **ikon kalkar** | oynat üçgeni ve dalga rozetin içinde | test |
| 62 | **Her katman kendi kutusunu** taşır | iki kelime tek koyu kutuda | test |
| 64 | İkinci bekleyen katmanın hapı **birincinin altına** | tek hap çıkıyor, ikincisi hiç | test |
| 65 | Bekleyen hapı **soluk ton, saydam zemin, geniş iç boşluk** | en parlak mürekkep, opak zemin, dar boşluk | test |
| 69 | Sürükleme **basılı tutmayla** başlar | basar basmaz başlar | **karar 28** |
| 73 | Hover'da **numara kalkar** | zaten kalkıyor | **karar 29** |
| 74 | Bekleyen kare **bırakıldığı yerden üretilir** | sıra kaydediliyor, kartın durumu değişmiyor | **karar 30** |
| 75 | Perde **koyu kahve-siyah**, düğme **kart zemininde** | saf siyah perde, zeminsiz düğme | test |
| 76 | Karışık seçim onayının **alt satırı** | yalnız başlık var | **karar 31** |

## Karara bağlananlar

Dördü de tek yoldan gelen zayıf sinyal ve dördü de daha önce verilmiş bir kararla ya da bugünkü
kodun kendisiyle çarpışıyor. 13. maddedeki 84. fark ile aynı biçim: "sapma" sanılan şey sonradan
verilmiş bir karar.

### Karar 28 · Sürükleme basıştan itibaren açık kalıyor *(fark 69)*

14 Ağustos'ta bu tam olarak bir hata raporuydu: kullanıcı *"kart hiç kalkmıyor"* ve *"bir saniye
beklesem de olmuyor"* dedi. Sebep v12 2. görev spec'inde yazılı — tarayıcı bir basışın sürüklemeye
dönüşüp dönüşemeyeceğine `mousedown` **anında** karar veriyor; 250 ms sonra açılan `draggable` o
basışı geri kazanmıyor. Tutuşu korumanın tek yolu sürüklemeyi elle yazmak olurdu.

Tutuşun asıl derdi — kaydırayım derken sıra bozulmasın — tarayıcının kendi birkaç piksellik eşiğiyle
zaten karşılanıyor. Geri koymak, kapatılmış bir hata raporunu yeniden açmak olurdu.

### Karar 29 · Numara hover'da zaten kalkıyor *(fark 73)*

`app.css`'teki `.qe-tile:hover .qe-badge { opacity: 0 }` 13 Ağustos'ta yazıldı — fark listesinin
turundan bir hafta önce. Yerini de tasarımın istediği şey alıyor: `.qe-tile:hover .qe-check`. Kuralı
tutan test de yerinde (`hides the number wherever the stylesheet shows the ring`). Yapılacak iş yok;
gözlem bayat.

### Karar 30 · Bırakma üretim başlatmıyor *(fark 74)*

Farkın **özü zaten doğru**: motor her turda sırayı yeniden okuyor (`run_loop.snapshot`), yani öne
çekilen bekleyen kare gerçekten bırakıldığı yerden üretiliyor. Eksik olan tek şey kartın bırakma
anında "üretiliyor" yazması — ve motor hâlâ başka bir kareyi tutuyorken bu bir yalan olur. Kuyruk
duruyorsa daha da fazlası: bırakma kuyruğu başlatırdı, 6. karar ise kuyruğun kendiliğinden
sürmediğini söylüyor.

Kart, motor o kareyi gerçekten eline aldığında "üretiliyor" yazıyor. Doğru olan bu.

### Karar 31 · Karışık seçim onayı yalnız başlık *(fark 76)*

Kullanıcı bunu 12 Ağustos'ta karara bağladı: *"alt satır hiç yazılmayacak — pencerede yalnız başlık
ve butonlar kalacak."* v3 fark listesinin 64. maddesinin altında duruyor. Fark listesi aynı
wireframe'i yeniden görmüş.

## Çizilecek altı fark

### 1 · Rozetler sol alta iniyor, ikonsuz, her biri kendi kutusunda *(60, 61, 62)*

Dört köşe, dört anlam: sol üstte durum hapı, sağ üstte numara ve seçim halkası, sol altta karenin
sahip oldukları. Sağ alt **bilerek boş**.

İkon gitmiyor sadece rozetten — kararı zaten verilmiş: v4 fark listesi, karar 21, *"rozetler yalnız
kelime taşır"*.

Kutu artık katman başına. Bugün tek koyu kutunun içinde yan yana iki kelime var; bundan sonra iki
ayrı kutu, aralarında ince bir boşluk. Satırın kendisi `data-owns`, her rozet `data-own` — DOM'dan
okunabilir olması gereken şey ikisi: kutunun **köşesi** ve rozetlerin **sayısı**.

### 2 · İki bekleyen katman, iki hap *(64)*

Bugün `statusOf` tek bir cevap veriyor ve borcun ilkini seçiyor. Bundan sonra bir **liste**
veriyor: üretilen varsa yalnız o, patlayan varsa yalnız o, yoksa **borcun tamamı**.

Bir karenin borcu en fazla iki olabiliyor — fotoğrafı olmayan kareye katman kuyruğa girmiyor
(`frames_in_scope`), yani foto borcu ile katman borcu aynı karede buluşamıyor. Üçüncü bir hap
doğuracak bir hâl yok; kod bir üst sınır uydurmuyor.

Sıra motorun sırası: `owed` zaten kuyruğun yapacağı sırada geliyor, ve haplar o sırada okunuyor.

**Hapların köşesi ayrı bir şey oluyor.** Bugün konum `Pill`'in kendi içinde. İki hap alt alta
dizilecekse konumun onları saran kutuya geçmesi gerekiyor: `Corner` — sol üst, sütun, aralarında
boşluk. `Pill` yalnız kutucuğun kendisi kalıyor. Detay sayfası `Pill`'i doğrudan kullanıyor, o da
`Corner` ile sarılıyor; iki ekran tek kalıpta kalıyor.

### 3 · Bekleyen hapın tonu ve ölçüsü *(65)*

Bugünkü yorum en parlak mürekkebi savunuyor: *"9 pikselde soluk ton yumuşak bir etiket değil,
okunmayan bir etikettir."* Tasarımın istediği soluk ton `--ink-3` değil `--ink-2` olarak yazılıyor —
karşı köşedeki sahiplik rozeti aynı mürekkebi aynı boyda zaten taşıyor, yani okunabilirliği
kanıtlanmış olan ton bu.

**Ölçü kalıbın, renk hâlin.** Zemin (`.85` → `.7`) ve iç boşluk (`2px 5px` → `3px 7px`) her hapta
değişiyor; ton yalnız bekleyen ve kuyruktaki hapta. Sebebi: bu dosyanın kendi kuralı — *"her katman
için tek kalıp"* — ve alt alta dizilen iki hapın farklı zeminde durması kırık görünürdü. Üretiliyor
ve hata kendi renklerini taşımaya devam ediyor; fark onlardan söz etmiyor.

### 4 · Perde ve altındaki düğme *(75)*

Perde saf siyahtan uygulamanın kendi kahve-siyahına dönüyor: `rgba(10,8,7,…)` — numara rozetinin,
sahiplik rozetinin ve durum hapının üstünde durduğu tonun ta kendisi. Saydamlığı değişmiyor,
değişen yalnız ton.

Perdenin altındaki *Tekrar dene* kart zeminini alıyor (`--bg-2`). Boş kırmızı karonun ortasındaki
aynı düğme zeminsiz kalıyor: o zaten kendi kartının üstünde duruyor, fark da yalnız *"perdenin
altındaki"* düğmeden söz ediyor.

## Yazılacak testler

### `Gallery.test.jsx` — 10 yeni, 1 silinen, 5 düzeltilen

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Karenin sahip oldukları sol altta, karşı köşe boş | 60 |
| 2 | Rozetin yanında ikon yok | 61 |
| 3 | Her katman kendi kutusunda, aralarında boşlukla | 62 |
| 4 | İki katman bekleyen kare iki hap taşıyor | 64 |
| 5 | İkinci hap birincinin altında | 64 |
| 6 | Bir katman üretilirken hap yine tek | 64 |
| 7 | Hapın zemini daha saydam, içi daha geniş | 65 |
| 8 | Perde uygulamanın kahve-siyahı | 75 |
| 9 | Perdenin altındaki düğme kart zemininde | 75 |
| 10 | Boş kırmızı karodaki düğme zeminsiz | 75 |

**Silinen:** `never puts two pills on one frame` — kuralı 64. fark değiştiriyor.

**Düzeltilen beş test:** ikisi hapın konumunu ölçüyor (`puts the state pill in the top left`,
`does not move the pill when the selection mode opens`) ve ölçtükleri şey `Corner`'a taşındığı için
adresi değişiyor; biri bekleyen hapın rengini söylüyor (`writes a waiting frame's label in the
brightest ink there is`) ve 65 onu ters çeviriyor; ikisi rozetin ikonunu bekliyor (`marks a frame
that has a video`, `marks a frame that has a sound as well`) ve o beklenti düşüyor.

### `PhotoDetail.test.jsx` — 1 yeni

| # | Ne diyor | Neden |
|---|---|---|
| 11 | Sahnenin kendi etiketi köşesinde duruyor | `Pill` konumunu bırakıyor; onu bu ekranda tutan tek şey `Corner` |

**Toplam 11 yeni test, biri siliniyor: 444 → 454.**

## Doğuştan yeşil iki test

6 ve 10 bugün de geçiyor. İkisi de bir **sınır** çiziyor: 6, borcun listeye dönmesinin üretilen
katmanı bastırmadığını; 10, kart zemininin her *Tekrar dene* düğmesine yayılmadığını. Zorla
kırmızıya çevrilmiyorlar — ölçtükleri şey bugün doğru, ve yarın yanlış olursa bunu söyleyecekler.

## Kapsam dışı

- **Loop rozeti** (fark 63) 7. maddede kapandı; buradaki üç rozet farkı onun kelimesine dokunmuyor.
- **Hapta "bekliyor" sözcüğü** (fark 66) 18. kararla kalıyor.
- **Boş galeri metni** (fark 67) 4. kararla kalıyor.
- **Galeri yükleme göstergesi** (fark 68) 13. kararla kalıyor.
- **Toplu taşıma** (70, 71, 72) 10. maddede kapandı.

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de **12 kırmızı** duruyor (11 yeninin dokuzu ile
düzeltilen üçü). Testler kırmızı commit ediliyor.
