# Queen Editor — Bölüm 6: Kalıcılık + iz (tasarım)

**Tarih:** 2026-08-03 · **Durum:** onay bekliyor
**Yol haritası:** [v2 · Bölüm 6](../plans/2026-08-03-queen-editor-v2-roadmap.md)
**Şemsiye:** [v2 (davranış)](2026-08-03-queen-editor-v2-design.md) · [v1 (mimari)](2026-07-24-queen-editor-v1-design.md)

## Amaç

Bugün panelin içeriği yalnız tarayıcının belleğinde: sayfayı yenileyince prompt listesi, negatif ve
varyant sıfırlanır. Üretim de hangi prompt'un hangi dosyayı ürettiğini hiçbir yere yazmıyor —
`12_a.png`'nin kaynağı hiçbir yerde durmuyor. Bu bölüm ikisini de diske taşır ve sonraki bölümlerin
(export, foto detay, kaldığı yerden devam) okuyacağı kaynağı kurar.

## Üç dosya, üç tek kaynak

Bu bölüm `FOUNDATION.md`'nin 2. ilkesinin uygulanmasıdır: *Truth lives on disk* — önemli olan her
durum kalıcı depoya dosya olarak yazılır ve uygulama yeniden başladığında kendini o dosyalardan
kurar.

Proje klasörüne üç dosya girer. Ayrımın kuralı `CODE-STANDARD.md`'nin *Separation of concerns*
bölümünde: farklı soruya cevap veren, farklı anda yazılan ve farklı ömre sahip şeyler ayrı durur.
İçerik örtüşmesi (aynı prompt metninin üçünde de geçmesi) kusur değildir.

| Dosya | Neyin **tek kaynağı** | Ne zaman yazılır | Ömrü | Sahibi |
|---|---|---|---|---|
| `settings.json` | Panelin içeriği | Üret'e basıldığı an | üstüne yazılır | projects |
| `plan.json` | Kuyruk: ne üretilecek, hangi sırayla, hangi seed'le | Üret'e basıldığı an, tek seferde | her üretimde yenilenir | photo_generation |
| `photos.jsonl` | Var olan fotoğraflar + her birinin metadata'sı | Her foto diske düştükten hemen sonra | birikir, asla değişmez | photo_generation |

### `settings.json` — panelin içeriği

```json
{
  "prompts": "[\n  \"kraliçe tahtta oturuyor, altın taç\",\n  \"kraliçe balkonda\",\n]",
  "negative": "bulanık, deforme el, düşük kalite",
  "variants": 4
}
```

`prompts` **ham metindir** — kullanıcı kutuya ne yazdıysa o, kendi biçimlendirmesiyle. Çözümlenmiş
liste saklansaydı metin yeniden üretilir ve kullanıcının satır düzeni, sondaki virgülü kaybolurdu.
Bu dosya doğrulanmaz: bozuk bir liste de olduğu gibi kaydedilir, çünkü tek işi kutuyu geri
doldurmaktır.

### `plan.json` — kuyruk

```json
{
  "negative": "bulanık, deforme el, düşük kalite",
  "frames": [
    { "number": 0, "letter": "a", "prompt": "kraliçe tahtta oturuyor, altın taç", "seed": 812634 },
    { "number": 0, "letter": "b", "prompt": "kraliçe tahtta oturuyor, altın taç", "seed": 991204 }
  ]
}
```

Karede dosya adı değil **numara + harf** durur: `<numara>_<harf>.png` şemasını bilen tek yer foto
deposudur, plan onu tekrarlamaz. Dosya adı ancak foto yazıldıktan sonra, deponun döndürdüğü hâliyle
kayda geçer.

Bu dosya ölü bir kayıt değil, **üretimin kendi kuyruğudur**: işçi kareleri buradan sırayla okur.
Bellekte ayrı bir kuyruk tutulmaz — tek liste var ve o da diskte, dolayısıyla ikisi birbirinden
ayrı düşemez. Bölüm 12'deki "kaldığı yerden devam" bu dosyayı yeniden okur ve kaydı olmayan
kareleri üretir.

**Seed plan yazılırken belirlenir**, üretim anında değil. Böylece yarıda kalan bir üretim
sürdürüldüğünde kareler baştan planlanan görüntüleri üretir. `negative` kare başına değil üretim
başlığında durur — bir üretimin tek negatifi vardır.

Kareler **işaretlenmez**: bir karenin bitip bitmediği `photos.jsonl`'da satırı olup olmadığından
bilinir. Aynı olguyu iki yere yazmak, ikisinin ayrı düşmesi demektir.

### `photos.jsonl` — var olan fotoğraflar

Satır başına bir foto (JSON Lines):

```
{"file":"0_a.png","prompt":"kraliçe tahtta oturuyor, altın taç","negative":"bulanık, deforme el","seed":812634,"createdAt":"2026-08-03T14:32:11Z"}
```

**Galerinin listesi artık bu dosyadır** — klasör taranmaz. Dosya var ama satırı yoksa ekranda
görünmez; bu bilinçli, çünkü Bölüm 7 (sıra), 8 (export) ve 10 (silme) tek bir listeyi yönetecek.

Satır **kendi kendine yeter**: prompt ve negatif burada tekrarlanır, çünkü `plan.json` her üretimde
üstüne yazılır ve kalıcı kaynak değildir. Kalıcı olması istenen her şey bu dosyada olmalıdır.

Neden JSON Lines: dosya yalnız **sonuna eklenerek** büyür, yazılmış satırlara hiç dokunulmaz. Tek
bir JSON dizisi olsaydı her fotoğrafta dosyanın tamamı yeniden yazılırdı ve Colab oturumu o an
ölseydi bütün iz gidebilirdi. Bu biçimde en kötü ihtimal, son satırın yarım kalmasıdır — okuyucu
çözümlenemeyen son satırı atlar.

**Model alanı bu bölümde yok.** Model seçimi Bölüm 13'ün işi; geldiğinde yeri belli — `plan.json`'ın
üretim başlığına bir alan, `photos.jsonl` satırına bir alan eklenir, başka hiçbir şey değişmez.

## Üretim akışı

1. **Üret'e basılır.** Panel içeriği `settings.json`'a yazılır — üretim kabul edilsin edilmesin.
   Kural tek cümle: *Üret'e bastıysan kutular kaydedilir.* (Bozuk liste yüzünden üretim reddedilse
   bile metin diskte kalır; sayfayı yenileyip düzeltmeye devam edebilirsin.)
2. **Ayarlar kaydedilemezse üretim başlamaz** ve sunucunun kendi hata metni gösterilir. İkisi de aynı
   klasöre yazıyor: ayar yazılamıyorsa foto da yazılamayacaktır.
3. **Plan kurulur:** prompt listesi çözümlenir, kareler numaralanır, her kareye seed atanır ve
   `plan.json` bir kez yazılır.
4. **İşçi planı okur**, kareleri sırayla üretir. Her başarılı karede önce PNG, hemen ardından
   `photos.jsonl`'a o karenin satırı eklenir.
5. Patlayan kare satır yazmaz — hata politikası Bölüm 5'teki gibi kalır, değişmez.

## Numaralandırma

Bir numarayı iki şey talep edebilir: **diskteki bir dosya** ve **bir planın ayırdığı ama henüz
üretilmemiş kare**. Bir sonraki üretim ikisinin de üstünden başlar.

Plandaki numaraların sayılması şart: yarıda kalan bir üretimde numaralar ayrılmış ama fotolar
üretilmemiş olur. Sayılmasaydı sonraki üretim aynı numaraları yeniden kullanır ve bir dosya adı iki
farklı prompt'a bağlanırdı — bu bölümün kurduğu izin kendisi bozulurdu.

Kayda ayrıca bakmaya gerek yok: bir satır ancak fotoğrafı yazıldıktan sonra eklendiği için kayıt,
diskte olmayan bir numarayı içeremez. Diski saymak aynı zamanda **hiçbir dosyanın üstüne
yazılmamasını** garanti eder — `FOUNDATION.md`'nin 1. ilkesi.

## Backend yüzeyi

| Uç | Feature · use case | Not |
|---|---|---|
| `GET /api/projects/<ad>/settings` | projects · get_settings | dosya yoksa boş ayarlar |
| `PUT /api/projects/<ad>/settings` | projects · save_settings | doğrulama yok, ham kayıt |
| `GET /api/projects/<ad>/photos` | photo_generation · list_photos | artık kayıttan okur, satırları döner |

Üretim uçları değişmez; plan ve kayıt yazımı `start_batch` içinde olur.

## Mimari yerleşim

- **`services/drive/storage.py`** — metin okuma/yazma ve satır ekleme ilkelleri. Şema bilmez.
- **`features/projects/`** — `settings.json` şemasını bilen tek yer; iki use case (oku, yaz).
- **`features/photo_generation/`** — `plan.json` ve `photos.jsonl` şemalarını bilen iki ayrı depo;
  `start_batch` planı yazar ve kuyruğu ondan okur, `list_photos` kayıttan okur.
- **Frontend** — ayarlar `features/projects` içindeki bir hook'la okunur/yazılır; proje ekranına
  `App.jsx` (birleştirme noktası) üzerinden geçer. İki feature birbirini import etmez.

## Doğrulama (Colab)

1. Projeye gir → prompt listesi, negatif ve varyant yaz → **Üret**.
2. Sayfayı yenile → üç kutu da dolu geliyor. Projeden çık-gir, başka sekmede aç → yine dolu.
3. Drive'da proje klasöründe üç dosya duruyor. Kayıt dosyasını aç → her satırda dosya adı, prompt,
   negatif ve seed görünüyor; galeri ile birebir aynı fotolar.
4. Plan dosyasını aç → o üretimin bütün kareleri, sırasıyla ve seed'leriyle duruyor.
5. Bozuk bir liste yapıştır → Üret → hata; sayfayı yenile → **bozuk metin kutuda duruyor** (kayıp yok).
6. Üretimi yarıda **Durdur** → tekrar **Üret** → yeni numaralar, durdurulan üretimin planladığı en
   büyük numaranın üstünden başlıyor; eski kayıt satırları değişmemiş.
7. (Geliştirici) `pytest` — depolar geçici klasörle, use case'ler sahte portlarla geçiyor.

## Bilinçli bedeller

- **Kaydı olmayan dosya görünmez.** Migration yazılmıyor: sistem henüz kullanılmadı, yalnız test
  edildi (kullanıcı kararı). Eski test fotoları Drive'da kalır, galeride çıkmaz.
- **`plan.json` her üretimde üstüne yazılır.** Yarım kalmış bir üretim varken yeni Üret'e basılırsa
  eski kuyruk unutulur (numaraları yine de tüketilmiş sayılır, çakışma olmaz). Bu etkileşimin
  kullanıcıya nasıl görüneceğini Bölüm 11/12 tanımlar.
- **Kaydın son satırı yarım kalabilir** (tam o anda oturum ölürse); okuyucu çözümlenemeyen son satırı
  atlar, önceki satırlar sağlamdır.

## Kapsam dışı (sonraki bölümlere)

Galeri sırasının saklanması (Bölüm 7) · export (8) · izin ekranda gösterilmesi (9) · silme (10) ·
duraklat/devam ve "bekliyor" kareleri (11) · kaldığı yerden devam (12) · model alanı (13).
