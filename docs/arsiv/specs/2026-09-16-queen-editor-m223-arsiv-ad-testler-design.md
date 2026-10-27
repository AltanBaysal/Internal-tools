# Madde 223 · Arşivdeki ad tutulmuş sayılacak — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcının gördüğü

221 Colab'da denendi. Bir proje arşivlendi, sonra **aynı adla yeni bir proje açıldı ve kabul edildi**.
Arşivdeki projeye *Geri al* denince **hiçbir şey olmadı** — hata da yok, hareket de. Proje arşivde
kilitli kaldı.

## Sebep — koddan okundu, tahmin edilmedi

Dört şey üst üste geldi, ve son ikisi olmasa ilk ikisi yalnız bir tuhaflık olurdu:

1. **Ada bakan tek yer kökü görüyor.**
   [`make_dir`](../../../queen-editor/backend/services/drive/storage.py) `root/<ad>` açmayı deniyor
   ve `FileExistsError`'a bakıyor. Arşiv **bir alt klasör** *(`root/arsiv/<ad>`)*, yani arşivdeki bir
   ad kökte boştur.
2. **Aynı boşluk yeniden adlandırmada da var:** `rename_dir` hedefe `os.path.exists(root/<yeni>)` ile
   bakıyor. Canlı bir projeyi arşivdeki bir ada çevirmek de bu yüzden serbest.
3. **Geri almanın kapısı yok.** Ad dolunca `rename_dir` `None` dönüyor, `restore_project` `NameTaken`
   atıyor — ve arşivdeki kartta **yalnız *Geri al*** var: ad değiştirme oraya 221'de **bilerek**
   konmadı *("arşiv bir şey koyulan yerdir, düzenlenen ikinci bir ekran değil")*. Yani proje çıkamaz.
4. **Ve ekran susuyor.** `handleArchive` ile `handleRestore`
   *([`ProjectsScreen.jsx`](../../../queen-editor/frontend/src/features/projects/ProjectsScreen.jsx))*
   `try/catch` taşımıyor; 409 yakalanmamış bir promise reddi olarak kayboluyor. Kullanıcının gördüğü
   *"basıyorum, hiçbir şey olmuyor"* tam olarak budur.

Dördüncüsü ilk üçünden **bağımsız bir kusur**: arşivin bugün **her** hatası sessiz — 404 de, Drive'ın
döndürdüğü 500 de. Bu turda o da çivileniyor, çünkü 1–3 düzelse bile bir sonraki hata yine
görünmezdi.

## Karar

**Kullanıcı, 16 Eylül: arşivdeki ad tutulmuş sayılır.** Arşivde `balo` dururken ne yeni bir `balo`
açılabilir ne de bir proje `balo`ya çevrilebilir, ve redin cümlesi adın **arşivde** olduğunu söyler —
kullanıcıyı projeler arasında aramaya göndermez.

**Elenen okuma:** çakışınca geri almanın ad sorması. Çakışmayı ancak çıkarken gösterirdi, ve arşivdeki
kartı iki düğmeli yapardı — 221'in bilerek verdiği şeyi geri alırdı.

Seçilenin bedeli açık ve kabul edildi: arşivdeki bir adı yeniden kullanmak için önce o projeyi
çıkarmak gerekiyor.

Kararın bedava verdiği sonuç: **geri alma her zaman çalışır.** `restore`'un `NameTaken`'ı da,
`archive`'ınki de yerinde kalıyor ama artık ulaşılamaz — kural onların önüne geçtiği için. İkisi de
silinmiyor: bir gün kökte elle açılmış bir klasör aynı şeyi yapabilir, ve o zaman söyleyecek cümle
duruyor.

## Nerede duracak

`DriveStorage` bilerek proje bilmiyor — *"knows no project, no JSON, no schema"*. `ARCHIVE_DIR` proje
alanının bilgisi, ve 221'den beri arşivin nerede olduğunu bilen **tek yer**
[`DriveProjectStore`](../../../queen-editor/backend/features/projects/data/project_store.py). Kural
oraya iner; klasör katmanı değişmez.

**Harf büyüklüğü işin içine karışmıyor.** `name_rules` yalnız `arsiv` adının kendisini büyük-küçük
ayırmadan reddediyor, çünkü o ad **bizim** koyduğumuz bir ad ve depo Windows'ta da geliştiriliyor.
Çakışma sorusu ise dosya sisteminin sorusu: kökteki dolu ad bugün de dosya sisteminin dediği kadar
dolu, ve arşiv aynı yoldan geçiyor. İki ayrı davranış olmuyor.

**Yazarken cevap veren kontrol değişmiyor.** [`check_name`](../../../queen-editor/backend/features/projects/domain/usecases/check_name.py)
bilerek disksiz: *"a name already taken is a clash, not a broken rule"*. Bugün de kutu dolu bir proje
adına yeşil verip red kaydederken geliyor; arşiv aynı yoldan geçiyor, yani öğrenilecek ikinci bir
davranış yok.

## Ön yüzde hata nereye düşecek

Bugün ekranda iki hata yüzeyi var ve ikisi de **yükleme** hatası için: liste yerine geçen
`StatusErrorCard`. Bir **işlem** hatası listeyi silmemeli — kullanıcının kartları yerinde kalmalı ki
tekrar deneyebilsin.

O yüzden: listenin üstünde **tek satır**, sunucunun cümlesi birebir. Sonraki başarılı işlemde ya da
liste değişince kayboluyor. Yeniden deneme düğmesi yok — tekrar denemek zaten aynı düğmeye basmak.

## Çivilenecek olgular

### Proje deposu

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Arşivde o ad varken `create` `None` dönüyor | **kırmızı** |
| 2 | …ve kökte hiçbir klasör açılmıyor — yarım iş kalmıyor | **kırmızı** |
| 3 | Arşivde o ad varken `rename` `None` dönüyor, klasör yerinde duruyor | **kırmızı** |
| 4 | Arşivde olmayan bir ad eskisi gibi açılıyor | yeşil, ve öyle kalmalı |
| 5 | Kökte dolu bir ad eskisi gibi `None` dönüyor | yeşil, ve öyle kalmalı |

İkincisi kuralın yerinin çivisi: kontrol `mkdir`'den **önce** olmalı, yoksa klasör açılır ve sonra
geri alınması gerekir.

### Kullanım

| # | Ne diyor | Bugün |
|---|---|---|
| 6 | `create_project` arşivdeki ad için `NameTaken` atıyor | **kırmızı** |
| 7 | Cümlesi adın **arşivde** olduğunu söylüyor | **kırmızı** |
| 8 | `rename_project` aynı durumda aynı cümleyi atıyor | **kırmızı** |
| 9 | Kökte dolu ad için cümle **değişmiyor** — *"Bu ad zaten kullanılıyor."* | yeşil, ve öyle kalmalı |
| 10 | Arşivdeki bir projeyi geri almak, kökte o ad boş olduğu sürece hep çalışıyor | yeşil, ve öyle kalmalı |

Yedinci ile dokuzuncu birlikte duruyor: iki farklı durum iki farklı cümle, ve biri ötekinin yerine
geçerse kullanıcı olmayan bir şeyi aramaya gider.

### Rotalar

| # | Ne diyor | Bugün |
|---|---|---|
| 11 | `POST /api/projects` arşivdeki adla **409** ve cümle arşivi söylüyor | **kırmızı** |
| 12 | `POST /api/projects/<p>/rename` aynı durumda **409** | **kırmızı** |

Yeni bir sözleşme yok: dolu ad zaten 409, ve arşivin farklı bir kod döndürmesi ön yüzde ikinci bir
hata dili doğururdu.

### Ön yüz

| # | Ne diyor | Bugün |
|---|---|---|
| 13 | Arşivleme başarısız olunca ekranda sunucunun cümlesi duruyor | **kırmızı** |
| 14 | Geri alma başarısız olunca aynı | **kırmızı** |
| 15 | Hata çıkınca **liste yerinde kalıyor** — kartlar kaybolmuyor | **kırmızı** |
| 16 | Sonraki başarılı işlemde cümle kayboluyor | **kırmızı** |

## Bu turda değişen

Yalnız testler:

- `queen-editor/backend/tests/test_project_store.py` — 1–5
- `queen-editor/backend/tests/test_project_usecases.py` — 6–10
- `queen-editor/backend/tests/test_projects_routes.py` — 11–12
- `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx` — 13–16
