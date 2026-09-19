# Madde 227 · Arşiv bir işaret olacak — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Karar

Kullanıcı 221'i denedi ve maddenin okumasının yanlış olduğunu söyledi:

> *"Arşivlenen proje düzgün kullanılabilsin, sadece projeler ekranında arşivin altında olsun. Sen çok
> daha kompleks yapmışsın."*

Yani **arşivlemek yalnız hangi listede göründüğünü değiştirir.** Proje yerinde durur; açılır, üretir,
dışa aktarır — normal bir proje gibi.

**Ekran kararı da alındı** *(aynı gün)*: bugünkü **ayrı görünüm kalıyor**. Başlıktaki düğme listeyi
değiştirir, ve arşivdeki kart **normal kart** olur — 221'in ona verdiği tek düğmelilik kalkar,
*Arşivle* kutusunun yerini *Geri al* alır.

## Bugün ne var, ve nesi gidiyor

221 arşivi bir **yer** yaptı: klasör `arsiv/` altına taşınıyor, ve taşındığı için `project_exists`
onu bulamıyor — dokuz kullanım *(`start_batch`, `run_export`, `get_settings`, `list_frames`,
`resume_batch`, `retry_frame`, `retry_failed`, `cancel_generation`, `save_settings`)* kendiliğinden
kapanıyor. **İstenen bu değilmiş**, o yüzden taşıma gidiyor.

Gidenler, hepsi taşımanın getirdiği şeylerdi:

- **Taşıma.** `rename_dir` yerine bir işaret yazılıyor.
- **`halt_project`.** Arşivlemeden önce üretimin durdurulması, taşınan klasöre yazan işçi yüzündendi.
  Klasör taşınmıyorsa yazması da sorun değil — hatta proje çalışmaya devam ediyor, ki istenen tam bu.
- **Ad çakışması kuralları.** `archive` ile `restore`'un `NameTaken`'ı: arşiv artık bir yer olmadığı
  için çakışacak bir hedef de yok. İkisi de `Project` ya da `False` döner.

## İşaret nerede duruyor

Kökte **tek bir dosya**: `arsiv.json`, içinde arşivlenen adların listesi. Her projenin kendi içinde
değil — liste çizmek için N dosya açmak Drive'da pahalı, ve bu ekran bugün de yavaş *(madde 225)*.

Okunamayan dosya **boş liste** sayılıyor, `settings.json`'ın kuralının aynısı: hiçbir bozuk dosya
proje listesini çizilemez hâle getirmemeli.

**İşaret artık diskin kendisi değil, o yüzden ada bağlı.** Üç yerde peşinden gitmesi gerekiyor:

| Olay | İşarete ne oluyor |
|---|---|
| Arşivle / Geri al | ekleniyor / çıkıyor |
| Yeniden adlandır | **eski ad gidiyor, yeni ad giriyor** — yoksa proje arşivden düşer |
| Sil | **çıkıyor** — yoksa aynı adla açılan yeni proje arşivde doğar |

Üçüncüsü en sinsisi: kalan bir ad hiçbir listeyi bozmuyor *(o adda klasör yok)*, ta ki biri o adı
yeniden kullanana kadar.

## Göç — **yazıldı, sonra kullanıcı isteğiyle kaldırıldı**

> **16 Eylül, kod yazıldıktan sonra:** *"kaldır abi, kodu basitleştir, olabildiğince
> karmaşıklaştırma."* Göç koda girmişti ve çıkarıldı — bir kerelik bir onarımın depoda temelli
> yaşaması istenmiyor. **`arsiv/` altındakileri köke taşımak artık Drive'da elle yapılıyor.**
> Aşağıdaki 10–14 olguları bu yüzden çivilenmedi; yerine tek bir çivi kaldı: **kalan `arsiv/`
> klasörü proje sayılmıyor**, yoksa ekranda `arsiv` adlı bir proje belirirdi.
>
> Bölümün kalanı o günkü tasarımın kaydı olarak duruyor.

### O günkü tasarım

Kullanıcı denedi, yani Drive'da taşınmış projeler var. İşaret onları bilmiyor, klasör de kökte
değil — yani **hiçbir listede görünmezler.** Bu yüzden depo açılırken bir onarım yapıyor: `arsiv/`
altındaki her klasör köke geri taşınıyor ve **işaretleniyor**, sonra boşalan klasör siliniyor.

**Ad çakışabilir.** 223'ten önce arşivdeki bir adla yeni proje açmak serbestti — kullanıcının
bildirdiği hata tam buydu, yani böyle bir çift gerçekten olabilir. Geri gelen proje o zaman **boş bir
ada** iniyor: `<ad> (arşiv)`, dolusa `<ad> (arşiv 2)`… Ad değişiyor ama **hiçbir şey kaybolmuyor**,
ve yeni ad neden değiştiğini söylüyor.

**`arsiv` ayrılmış ad olarak kalıyor.** Sebebi değişti: artık orada bir arşiv olduğu için değil,
**onarımın ona bakacağı** için. `arsiv` adlı bir proje açılabilseydi, onarım onun alt klasörlerini
proje sanıp köke taşırdı.

## Çivilenecek olgular

### Proje deposu

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Arşivlemek klasörü **yerinde bırakıyor** — dosyalarıyla birlikte | **kırmızı** *(bugün taşıyor)* |
| 2 | Arşivlenen proje `dir_exists`'e **görünüyor** — üretim ve dışa aktarma açık | **kırmızı** *(bugün kapalı)* |
| 3 | Arşivlenen proje `list()`'te yok, `list_archived()`'da var | yeşil, ve öyle kalmalı |
| 4 | Geri almak işareti kaldırıyor, klasöre dokunmuyor | **kırmızı** |
| 5 | Olmayan bir projeyi arşivlemek `False` | yeşil, ve öyle kalmalı |
| 6 | Yeniden adlandırmak işareti **yeni ada taşıyor** | **kırmızı** |
| 7 | Silmek işareti düşürüyor — aynı adla açılan yeni proje arşivde doğmuyor | **kırmızı** |
| 8 | Bozuk `arsiv.json` boş liste sayılıyor, liste yine çiziliyor | **kırmızı** |
| 9 | `is_archived` işarete bakıyor | **kırmızı** *(bugün klasöre bakıyor)* |

### Göç

| # | Ne diyor | Bugün |
|---|---|---|
| 10 | `arsiv/` altındaki proje köke dönüyor ve işaretleniyor | **kırmızı** |
| 11 | Dosyaları eksiksiz geliyor | **kırmızı** |
| 12 | Kökte aynı ad varsa boş bir ada iniyor, hiçbir şey kaybolmuyor | **kırmızı** |
| 13 | Boşalan `arsiv/` klasörü siliniyor | **kırmızı** |
| 14 | `arsiv/` hiç yoksa hiçbir şey olmuyor | **kırmızı** |

### Kullanım

| # | Ne diyor | Bugün |
|---|---|---|
| 15 | Arşivlemek çalışan üretimi **durdurmuyor** | **kırmızı** *(bugün durduruyor)* |
| 16 | Arşivlenen projenin ayarları okunup yazılabiliyor | **kırmızı** |
| 17 | Arşivlenen projede üretim başlatılabiliyor | **kırmızı** |

On altı ile on yedi maddenin bütün meselesi: 221 bu ikisini **kapatmıştı**, ve kullanıcının istediği
tam tersi.

### Ön yüz

| # | Ne diyor | Bugün |
|---|---|---|
| 18 | Arşivdeki kartta **kalem** ve **çöp** var | **kırmızı** *(bugün yok)* |
| 19 | Arşivdeki kartta *Arşivle* yerine **Geri al** var | yeşil, ve öyle kalmalı |
| 20 | Arşivdeki karta tıklamak projeyi açıyor | **kırmızı** |

## Bu turda değişen

Yalnız testler. 221'in çivilerinden **taşımayı** anlatanlar sorularını değiştiriyor, çünkü artık
başka bir şey doğru:

- `test_project_store.py` — 1–14
- `test_project_usecases.py` — 15
- `test_projects_routes.py` — 16–17
- `test_name_rules.py` — `arsiv`'in neden ayrıldığının cümlesi *(kural aynı, sebep başka)*
- `ProjectsScreen.test.jsx`, `ProjectCard.test.jsx` — 18–20
