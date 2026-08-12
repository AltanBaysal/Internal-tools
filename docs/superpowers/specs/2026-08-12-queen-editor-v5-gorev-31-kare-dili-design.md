# Görev 31 — "Kare" dili genele

**Maddeler:** 104, 62, 63, 64, 65
**Roadmap:** [v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) · Blok 9
**Fark belgesi:** [v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)

## Sorun

Aynı ekranda iki sözcük birden dolaşıyor. Kuyruk kartı "8 kare bekliyor" derken boş galeri "henüz
fotoğraf yok" diyor; kuyruk boşaltma onayı "Üretilmiş fotoğraflar galeride kalır", seçim onayı ise
"3 fotoğraf silinsin mi?" diyor. Kullanıcı için ikisi aynı şey — ama artık aynı şey değil: v3'ten
sonra içerik birimi **kare**, fotoğraf ise onun bir katmanı. Bir kareyi silmek fotoğrafını değil,
üç dosyasını birden siliyor; "3 fotoğraf silinsin mi?" bunu söylemiyor.

## Kararlar

1. **İçerik birimi "kare".** "Fotoğraf" yalnız foto katmanını kastederken kalır: "Fotoğraf üret"
   paneli, "Fotoğraf üreticisi", katman sütunundaki "Foto". İçeriği sayan, gösteren ya da silen
   her cümle "kare" der.
2. **Üretilmiş seçim onayı katmanları sayar** *(madde 62)*. Alt satır önce ne gideceğini söyler,
   sonra geri alınamazlığı: `Karelerin videosu ve sesi de birlikte silinir (2 video · 1 ses). Bu
   işlem geri alınamaz.`
   - **Sıfır olan tür yazılmaz** — 2 video, 0 ses varsa parantez `(2 video)` olur. Bu, ekranın geri
     kalanının kuralı: sıfırlık bir sayı satır yazmaz *(madde 89)*.
   - **İkisi de sıfırsa ilk cümle hiç yazılmaz** — geriye yalnız "Bu işlem geri alınamaz." kalır.
     Yalnız fotoğrafı olan kareler için "videosu ve sesi de birlikte silinir" bir yalan olurdu.
   - **Cümlenin öznesi de sayıya uyar**: yalnız video varsa "…videosu da birlikte silinir",
     yalnız ses varsa "…sesi de birlikte silinir". Cümle şu üç parçadan kurulur: özne (bir kare
     seçiliyken "Karenin", çoğunda "Karelerin") + sahip olunan türlerin adı ("videosu ve sesi" /
     "videosu" / "sesi") + bağlaç ("da" video ile biterken, "de" ses ile biterken) +
     "birlikte silinir (sayılar)."
   - Sayılan şey karenin **sahip olduğu** katman: dosyası olan ve kırmızıya düşmemiş olan. Galeri
     karosundaki rozetlerin kuralıyla aynı (`OWNED`), böylece kullanıcı gördüğü rozetleri sayar.
3. **Yalnız-bekleyen onayının alt satırı üretilmiş kareyi korur** *(madde 63)*: "Bu kareler
   üretilmeyecek. Üretilmiş karelere ve dosyalarına dokunulmaz." Korunan şey fotoğraf değil,
   kare ve bütün dosyaları.
4. **Karışık seçimde alt satır hiç yazılmaz** *(madde 64, kullanıcı kararı 2026-08-12)*. Pencerede
   yalnız başlık ve butonlar kalır; başlık kare dilini konuşur: "2 kare silinsin, 2 bekleyen kare
   kuyruktan çıkarılsın mı?"
5. **Seçim barındaki buton her senaryoda "Sil"** *(madde 65)*. Değişen yalnız açılan pencerenin
   metni; pencerenin kendi butonu ne yaptığını söylemeye devam eder (yalnız-bekleyen seçiminde
   "Çıkar", diğer ikisinde "Sil").
6. **Detay ekranındaki tek kare silme onayı da bu dile geçer.** Bugün "Bu fotoğraf silinsin mi?" /
   "Bu işlem geri alınamaz." diyor; kodda bu görevi bekleyen bir not duruyor. Yeni metni tekil
   sayan biçim: "Bu kare silinsin mi?" + "Karenin videosu ve sesi de birlikte silinir (1 video).
   Bu işlem geri alınamaz." Aynı kural: sıfır tür yazılmaz, ikisi de yoksa ilk cümle yazılmaz.
7. **Proje ekranı bu görevin dışında.** Proje silme onayının metni madde 1'in konusu ve Görev 32'ye
   ait; buradan yalnız proje ekranının boş hâli ("fotoğrafların burada toplansın") kare diline
   geçer, çünkü onu adlandıran başka madde yok.
8. **`ProgressPanel.jsx` silinir, metni düzeltilmez.** İçinde "{failed} fotoğraf üretilemedi"
   duruyor ama dosyayı hiçbir yer çağırmıyor: yerini kuyruk paneli aldı ve orada aynı cümle zaten
   "3 kare üretilemedi — 2 foto · 1 video" diye yazıyor. Ölü bir dosyanın metnini düzeltmek onu
   canlıymış gibi gösterirdi; bırakmak ise "fotoğraf sözcüğü içerik birimi olarak kalmıyor"
   ölçütünü yalanlardı.
9. **Pencere genişlikleri bu görevde değişmez.** Alt satır uzadı ama genişliğin metne uyması madde
   105'in işi ve Görev 33'e ait; burada bir sayı elle değiştirilmez.

## Ne değişiyor

| Yer | Bugün | Yarın |
|---|---|---|
| Boş galeri | "henüz fotoğraf yok" | "henüz kare yok" |
| Boş galeri, alt satır | "…fotoğraflar burada belirecek" | "…kareler burada belirecek" |
| Seçim: yalnız üretilmiş | "3 fotoğraf silinsin mi?" · "Bu işlem geri alınamaz." | "3 kare silinsin mi?" · "Karelerin videosu ve sesi de birlikte silinir (2 video · 1 ses). Bu işlem geri alınamaz." |
| Seçim: yalnız bekleyen | "…Galerideki fotoğraflara dokunulmaz." | "…Üretilmiş karelere ve dosyalarına dokunulmaz." |
| Seçim: karışık | "2 fotoğraf silinsin, …" + açıklama satırı | "2 kare silinsin, …" · alt satır yok |
| Seçim barı butonu | "Sil" / "Çıkar" | her zaman "Sil" |
| Kuyruk boşaltma onayı | "Üretilmiş fotoğraflar galeride kalır." | "Üretilmiş kareler galeride kalır." |
| `ProgressPanel.jsx` ("3 fotoğraf üretilemedi") | çağrılmıyor | dosya silinir *(karar 8)* |
| Detay: kare bulunamadı | "Fotoğraf bulunamadı" | "Kare bulunamadı" |
| Detay: silinemedi | "Fotoğraf silinemedi" | "Kare silinemedi" |
| Detay: silme onayı | "Bu fotoğraf silinsin mi?" · "Bu işlem geri alınamaz." | "Bu kare silinsin mi?" · katman sayan alt satır |
| Proje ekranı, boş hâl | "fotoğrafların burada toplansın" | "karelerin burada toplansın" |

Değişmeyenler: "Fotoğraf üret" panel başlığı ve yan menü etiketi, "Fotoğraf üreticisi", detay
sütunundaki "Foto" sözcüğü, `/photos` yolu ve `photo` katman anahtarı. Bunlar foto katmanının kendi
adı; kare dili onların yerini almaz.

## Testler

Ön yüz, hepsi mevcut dosyalara:

- `Gallery.test.jsx` — boş galeri "henüz kare yok" der; üç seçim onayı üç metnini birebir yazar;
  katman sayan satır sıfır türü atlar; hiç katmanı olmayan seçimde ilk cümle yazılmaz; tek kare
  seçiminde "Karenin" der; karışık seçimde pencerede alt satır yoktur; bar butonu her üç senaryoda
  "Sil" der.
- `QueuePanel.test.jsx` — boşaltma onayı "Üretilmiş kareler galeride kalır" der.
- `ProgressPanel.test.jsx` — "3 kare üretilemedi" der.
- `PhotoDetail.test.jsx` — silme onayı "Bu kare silinsin mi?" der ve karenin katmanlarını sayar;
  bulunamayan kare "Kare bulunamadı" der.
- `ProjectsScreen.test.jsx` — boş hâl "karelerin burada toplansın" der.

Arka uçta bir şey değişmiyor: bu görevin tamamı arayüz metni.

## Öz eleştiri

- *"Karelerin videosu ve sesi de birlikte silinir" ile parantez çakışıyor mu?* — Hayır ama cümle
  sıfır türü atlarken tek başına kalabiliyordu: 2 video 0 ses iken "videosu ve sesi" demek yanlış
  olurdu. Cümlenin öznesi de sayıya uyar: yalnız video varsa "videosu", yalnız ses varsa "sesi".
  Karar 2'ye bu ek yazıldı.
- *Detay ekranındaki onay gerçekten bu görevin işi mi?* — Evet: koddaki not ("Görev 31'e kadar
  kendi sözcüklerini korur") bu görevi adlandırıyor ve madde 104 içerik birimini her yerde
  değiştiriyor. Karar 6 bunu açık yazıyor, yoksa not asılı kalırdı.
- *Sayım kuralı hangisi: diskte dosya var mı, yoksa kullanıcı sahip mi?* — İkisi ayrı düşebiliyor
  (kırmızıya düşmüş bir katmanın dosyası olabilir). Galeri rozetleriyle aynı kuralı seçtim; başka
  türlüsü kullanıcının gördüğü rozetlerle onay penceresinin sayısını çelişkiye sokardı.
