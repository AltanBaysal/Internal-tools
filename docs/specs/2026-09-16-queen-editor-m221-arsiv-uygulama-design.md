# Madde 221 · Projeler arşivlenebilecek — uygulama turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Test turu:**
[tasarım](2026-09-16-queen-editor-m221-arsiv-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Testler `f3a1c48c`'de kırmızı.

## Katman katman

**`name_rules`** — `ARCHIVE_DIR = "arsiv"`, ve `validate` bu adı **harf büyüklüğü ayırmadan**
reddediyor. Kural burada duruyor çünkü *"the single source of truth for the rules"* burası: proje
açmak, ad değiştirmek ve ekrandaki canlı ad kontrolü üçü de buradan geçiyor, yani kural bir kez
yazılınca üçünde birden var.

**`DriveStorage`** — iki küçük genişletme, ikisi de arşivi bilmeden:

- `list_dirs(subdir="")` — kökün yerine bir alt klasörü sayabiliyor. Olmayan klasör **boş liste**,
  `list_files`'ın bugünkü kuralı; kökün kendisi hâlâ `FileNotFoundError` atıyor, çünkü orada
  eksiklik bağlanmamış bir Drive demek.
- `rename_dir` hedefin **üst klasörünü açıyor**. Kökteki bir taşımada bu hiçbir şey yapmıyor
  *(üst klasör zaten kök)*; ilk arşivlemede `arsiv/`'i yaratan şey bu.

**`DriveProjectStore`** — arşivi bilen tek yer:

| | Ne yapıyor |
|---|---|
| `list()` | kökü sayıyor, `ARCHIVE_DIR`'i **atlıyor** |
| `list_archived()` | `arsiv/` içini sayıyor |
| `archive(name)` | `rename_dir(name, "arsiv/<name>")` |
| `restore(name)` | tersi |

`archive` ve `restore` `rename`'in cevaplarını olduğu gibi veriyor — **`False`** taşınacak bir şey
yok, **`None`** hedefte zaten bir şey var, yoksa `Project`. Aynı hareket, aynı üç cevap.

**Kullanım** — `archive_project.py`, üç işlev bir arada çünkü üçü de tek kavramın parçası:

- `archive_project(store, halt, name)` — **önce `halt(name)`**, `delete_project`'in kuralının
  aynısı ve aynı sebeple: taşınan klasöre yazan bir işçi projeyi yarı burada yarı orada bırakır.
  Sonra `store.archive`; `False` → `ProjectMissing`, `None` → `NameTaken`.
- `restore_project(store, name)` — `halt` yok, çünkü arşivdeki proje zaten üretemez.
- `list_archived_projects(store)` — `list_projects`'in eşi, aynı sıralama.

`NameTaken` cümleleri iki durumda ayrışıyor: geri alırken *"Bu ad zaten kullanılıyor."* — kullanıcı
canlı bir projeyle çarpışıyor ve o cümle zaten her yerde bu. Arşivlerken ise çarpışma **arşivin
içinde**, ve *"zaten kullanılıyor"* kullanıcıya nereye bakacağını söylemez: kendi cümlesi oluyor.

**Rotalar** — üç uç, kodları `delete`/`rename` ile birebir aynı:

| | |
|---|---|
| `POST /api/projects/<p>/archive` | 204 · 404 yok · 409 arşivde dolu · 500 |
| `POST /api/projects/<p>/restore` | 204 · 404 arşivde yok · 409 canlı ad dolu · 500 |
| `GET /api/projects/archived` | `{"projects": [...]}` · 500 |

Listeleme ucu `<project>` kalıbının **önüne** konuyor değil — Flask sabit segmenti zaten değişkene
tercih ediyor, ve `archived` adlı bir proje `name_rules`'a takılmıyor: ona ihtiyaç da yok, çünkü
çakışan yol `/api/projects/archived` ile `/api/projects/<project>/...` farklı derinlikte.

**Ön yüz** — `ProjectCard` bir düğme daha alıyor ve bir kip:

- Canlı kart: kalem · **arşiv kutusu** · çöp. Arşiv kutusu **ghost**, kalem gibi — hiçbir şey
  eksiltmiyor, ve kırmızı yalnız çöpte kalınca bir işaret olarak duruyor *(karar 43)*.
- `archived` kartı: yalnız **Geri al**. Arşivde silme ve ad değiştirme yok; arşiv bir yer, bir
  düzenleme ekranı değil.

`ProjectsScreen` başlıkta bir **Arşiv** düğmesi taşıyor ve tek liste çiziyor: ya projeler ya arşiv.
İki listenin yan yana durması, maddenin çözmeye çalıştığı şeyin — uzun liste — aynısını yapardı.
Arşiv boşken kendi cümlesi var; projelerin boş hâli *"ilk projeni oluştur"* diyor, ve arşivde bu
yanlış davet olurdu.

Her iki hareket de listeyi **Drive'dan yeniden okuyor** — ekranın kendi kuralı.

## Bu turda değişmeyen

Grafikler, defter, `model_groups`. Arşiv Drive'ın içindeki bir klasör; kurulumun ondan haberi yok.
