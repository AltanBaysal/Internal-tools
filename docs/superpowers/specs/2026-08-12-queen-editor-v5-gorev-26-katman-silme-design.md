# Queen Editor v5 · Görev 26 — Sekme başına tek yıkıcı eylem · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 7, Görev 26 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
80, 83 · **Tür:** arka uç + ön yüz.

## Neden

Detay artık katman katman açılıyor (Görev 23-25) ama altındaki tek yıkıcı buton hâlâ kareyi bütün
olarak siliyor: video sekmesindeyken basılan "Sil" fotoğrafı da götürüyor. Beğenilmeyen bir videoyu
atmanın tek yolu kareyi silip baştan üretmek — tasarımın cevabı, her sekmenin kendi yıkıcı eylemi.

## Ne olacak

Açık sekme hangi katmansa yıkıcı buton onu siler: Foto'da kare (bugünkü davranış), Video'da video,
Ses'te ses. Katman silinince kare galeride kalır; silinen katmanın **üstündekiler** onunla gider,
altındakilere dokunulmaz.

## Kararlar

### 1. Katman silmek kendi use case'i olur

`remove_frames` "kareyi galeriden çıkar" sorusunun cevabı ve öyle kalır. Katman silmek başka bir
soru — kare kalıyor — ve iki soruyu tek fonksiyonda toplamak, her satırında "hangi hâldeyiz" diye
soran bir gövde demek. Yeni use case `remove_layer`, dosyayı gerçekten kimin tuttuğunu ise ikisi de
aynı yerden okur (`layers.files_to_unlink`, madde 101).

Foto bu yoldan silinemez: fotoğraf taban katman, onu silmek kareyi silmektir ve bunun kendi yolu
var. Uç nokta foto için 404 döner — kuyruğa ekleme ucunun `QUEUEABLE` kuralının aynısı.

### 2. Silinen katmanın üstündekiler onunla gider

Ses videonun üzerine bindirilir (madde 31): videosu gitmiş bir ses hiçbir şeyin üstünde durmaz. Bu
yüzden video silinince ses de silinir; ses silinince video ve foto yerinde kalır.

"Üstündeki" iki hâlde olabilir ve ikisi de kapanır:

- **üretilmiş katman** → dosyası (başka kare tutmuyorsa) diskten gider, kaydına `deleted` düşer;
- **kuyrukta bekleyen iş** → hiç üretilmedi, kaydına `removed` düşer ve kuyruk onu atlar.

İkincisi olmasa, videosu silinen karenin bekleyen ses işi sırası gelince olmayan videoyu arardı.

### 3. Kareyi adı değil kimliği gösterir

Bir fotoğraf iki kareye ait olabilir: kopya kare kaynağının resmini paylaşır (madde 102). Dosya adı
o yüzden kareyi göstermez — "0_a.png" hem kaynağın hem kopyanın satırında yazar ve dosya adıyla
sorulan bir istek ikisinden birine, hep aynısına, gider.

Bu yüzden kareye tek kare üstünde iş yapan uçlar **kimliği** ile sorulur: `{"frame": "P0_1"}`.
Detay sayfası zaten karenin kimliğini elinde tutuyor.

Aynı kusur Görev 25'in `regenerate` ucunda da var — kopya karede "Yeniden üret"e basmak kaynağın
katmanını üretirdi — ve burada kapanır: iki kardeş uç aynı dili konuşur.

Galerinin kendi silme ve tekrar deneme uçları dosya adıyla sorulmaya devam eder; orada seçilen şey
zaten karo, yani dosyanın kendisi. Detayın hangi kareyi açtığı sorusu (aynı adrese iki kare
düşünce) Görev 27'nin işi.

### 4. Uç nokta katmanın kendi adresinde durur

`POST /api/projects/<proje>/layers/<katman>/delete`, gövdesinde `{"frame": ...}`. Kuyruğa ekleme
`POST …/layers/<katman>` ile aynı adres ağacı: aynı şeyin iki fiili, iki komşu uç nokta. Cevap
`remove_frames`'in cevabı gibi gerçekte ne olduğunu söyler: `{"deleted": [dosya adları]}`.

Bilinmeyen kare 404, silinemez katman (foto ya da olmayan bir ad) 404, karenin taşımadığı katman
ise sessizce boş cevaptır — silme isteği, zaten silinmiş bir şey için hata değildir (`remove_frames`
bilinmeyen adı atlarken kurduğu kural).

### 5. Her sekmede tek buton, sözleri tasarımın (madde 80)

| Sekme | Buton | Onay başlığı | Onay metni |
|---|---|---|---|
| Foto | bugünkü "Sil" / "Kuyruktan çıkar" | bugünkü "Bu fotoğraf silinsin mi?" | bugünkü "Bu işlem geri alınamaz." |
| Video | "Videoyu sil — kare kalır" | "Video silinsin mi?" | "Bu video ve üzerindeki ses kalıcı olarak silinir — bu geri alınamaz. Kare ve fotoğrafı galeride kalır." |
| Ses | "Sesi sil — video kalır" | "Ses silinsin mi?" | "Bu ses kalıcı olarak silinir — bu geri alınamaz. Video ve kare kalır; video sessiz oynar." |

Fark belgesi katman metinlerinin başını "…" ile geçiyor; eksik baş "Bu video …" / "Bu ses …" olarak
tamamlandı — cümlenin gerisi belgede birebir yazılı.

Foto sekmesinin sözlerine dokunulmaz. Onun "fotoğraf" demesi madde 104'ün işi ve Görev 31'de bütün
ekranlarla birlikte "kare"ye geçecek; burada tek başına değiştirmek aynı cümleyi iki kez yazmak
olur. Madde 80'in foto sekmesinden istediği tek şey zaten karşılanıyor: kareyi tümden silmek yalnız
orada.

Katman onayları 400 piksel (madde 80); foto onayı bugünkü 320'de kalır — pencere genişliğini metne
göre ayarlamak Görev 33'ün işi (madde 105).

### 6. Yıkıcı buton her yerde dolgusuz (madde 83)

Detaydaki Sil butonu kırmızı metin ve çerçeve taşıyor ama arka planını temizlemiyor; uygulamanın
geri kalanı temizliyor. Üç butonun üçü de `background: none` alır — dolu kırmızı buton hiçbir yerde
yok.

### 7. Katman silinince sayfa karenin üstünde kalır

Silinen sekme artık yok: sayfa Foto sekmesine döner ve kare yerinde durur. Nereye gidileceği sorusu
yalnız kare silmenin sorusu — o bugünkü hâliyle kalır (sonraki kare, yoksa önceki, yoksa galeri).

## Nasıl görülür

1. Video sekmesinde buton "Videoyu sil — kare kalır" diyor; basınca 400 piksellik onay çıkıyor.
2. Onaylanınca kare galeride duruyor, rozetlerinden video ve ses gidiyor, fotoğrafı yerinde.
3. Ses sekmesinde silmek videoyu bırakıyor: video sekmesi açık kalıyor, sessiz oynuyor.
4. Üç butonun da arkası boş.

## Testler

**Arka uç:** video silinince ses de gider · ses silinince video ve foto kalır · silinen katmanın
dosyası diskten gider · başka karenin tuttuğu dosya diskte kalır · üstündeki bekleyen iş kuyruktan
düşer · karenin taşımadığı katman boş cevap · foto katmanı 404 · bilinmeyen kare 404 · silinen
katman galeri satırından düşer · kaynağıyla aynı fotoğrafı taşıyan kopya karede istenen katman
kopyanınki olur (aynısı `regenerate` için de).

**Ön yüz:** her sekmede kendi butonu · video butonu onay soruyor ve metni tasarımın · ses butonu
kendi metniyle onay soruyor · onaylanınca `removeLayer` açık katmanla çağrılıyor · silindikten
sonra Foto sekmesi açık · üç butonun arka planı yok · sunucu reddederse sayfa kalıyor ve söylüyor.

## Kapsam dışı

- **Hata ve kopya kare detayı** — Görev 27 (hatalı katmanın sekmesi zaten açılmıyor).
- **Silme onaylarının "kare" diline geçmesi** — Görev 31 (madde 104, 62-65): foto sekmesinin onayı
  ve galeri seçiminin onayları bugünkü sözleriyle kalır.
- **Pencere genişliğinin metne göre değişmesi** — Görev 33 (madde 105).

## Riskler

- **Yarış:** silinen videonun sesi tam o sırada üretiliyorsa iş kendi satırını yazar ve kayıt son
  satırı doğru sayar — ses geri gelir. Kareyi silmenin bugünkü davranışıyla aynı; tasarım bunu
  ayrıca ele almıyor.
