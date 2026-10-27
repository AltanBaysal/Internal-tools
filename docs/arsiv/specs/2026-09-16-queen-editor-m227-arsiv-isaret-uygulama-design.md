# Madde 227 · Arşiv bir işaret olacak — uygulamanın tasarımı

**Test turu:** [tasarım](2026-09-16-queen-editor-m227-arsiv-isaret-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## 1 · İşaretin dosyası

Kökte `arsiv.json`, içinde `{"arsiv": [ad, ad, …]}`. Dosya `settings.json`'ın kurallarıyla okunuyor:
**okunamayan hiçbir şey listeyi çizilemez yapmaz** — bozuk JSON, sözlük olmayan gövde, liste olmayan
alan, hepsi boş arşiv sayılıyor.

Neden kökte tek dosya, projelerin içinde değil: liste çizmek N dosya açardı, ve bu ekran Drive'da
bugün de yavaş *(madde 225)*.

## 2 · Depo

```
_marks()                 arsiv.json'daki adlar (okunamazsa [])
list()                   kökteki klasörler eksi işaretliler
list_archived()          kökteki klasörler kesişim işaretliler
archive(name)  -> bool   klasör yoksa False; varsa işarete ekliyor
restore(name)  -> bool   işaretli değilse False; işaretten çıkıyor
is_archived(name)        işarete bakıyor
```

**Dönüş değeri `Project`'ten `bool`'a iniyor.** Taşıma varken geri dönen tarih bir anlam taşıyordu;
artık hiçbir şey kıpırdamıyor, ve çağıranın tek sorduğu *"böyle bir proje var mıydı"*. Olmayan bir
cevabı taşımak için `list_dirs`'i bir kez daha okumak, Drive'da bedava değil.

**Taşımayla birlikte giden iki ret:** `archive` ile `restore`'un `None`'ı. Arşiv bir yer olmadığı için
çakışacak bir hedef de yok.

**İşaret ada bağlı, o yüzden iki yerde peşinden gidiyor:**

- `rename` — taşıma başarılıysa eski ad çıkıyor, yeni ad giriyor.
- `delete` — klasörle birlikte işaret de düşüyor. Yoksa o adla açılan bir sonraki proje **arşivde
  doğar**, ve bunu hiçbir liste bozulmadan yapar.

`create` ile `rename`'in 223'te eklenen ön kontrolleri **kalkıyor**: proje kökte durduğu için ad zaten
dolu, `make_dir` ve `rename_dir` kendiliğinden reddediyor. Kalan yalnız `is_archived`, ve o da
**redin cümlesini seçmek** için — 223'teki yerinde duruyor.

## 3 · Eski `arsiv/` klasörü

**Göç yoktu, yazıldı, ve kullanıcı isteğiyle çıkarıldı** *("kaldır abi, kodu basitleştir")*.
Bir kerelik bir onarımın depoda temelli yaşaması istenmedi: `arsiv/` altındaki projeleri köke
taşımak **Drive'da elle** yapılıyor, ve taşınınca normal *(arşivlenmemiş)* proje olarak görünüyorlar.

Koddan geriye **tek satır** kalıyor: `list()` `arsiv` adını atlıyor. Sebebi, 221'den kalma bir
kurulumda o klasörün hâlâ duruyor olması — ve kökteki her klasörün proje sayılması. Atlanmasaydı
ekranda `arsiv` adlı bir proje belirirdi.

`arsiv` **ayrılmış ad olarak kalıyor**, aynı sebeple. Cümlesi artık sebebini söylemiyor *("Bu ad
ayrılmış, başka bir ad dene.")*: eski cümle *"arşivlenen projeler orada duruyor"* diyordu, ve bugün
orada bizim koyduğumuz hiçbir şey durmuyor.

## 4 · Kullanım ve rotalar

- `archive_project(store, name)` — **`halt` parametresi gidiyor.** Taşınmayan bir klasöre yazan işçi
  sorun değil; üstelik projenin çalışmayı sürdürmesi maddenin istediği şeyin ta kendisi.
- `restore_project` aynı biçime giriyor.
- Rotalardan arşiv/geri alma uçlarının `NameTaken` yakalaması kalkıyor: artık atılmıyor, ve
  yakalanmayan bir şeyi yakalamak sonradan okuyana olmayan bir yol gösterir.
- `main.py` artık `halt_project`'i arşive bağlamıyor. Silme tarafında **aynen duruyor** — orada klasör
  gerçekten yok oluyor.

## 5 · Ekran

`ProjectCard`: arşivdeki kart **normal kart** oluyor — kalem, **Geri al**, çöp. Orta düğme yer
değiştiriyor, ötekiler yerinde kalıyor.

`ProjectsScreen` değişmiyor: 224'te ayrılan başlık, 223'te eklenen hata satırı ve iki liste olduğu
gibi kalıyor.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `backend/features/projects/data/project_store.py` | işaret dosyası, beş metot, ve göç |
| `backend/features/projects/domain/name_rules.py` | ayrılmış adın cümlesi |
| `backend/features/projects/domain/usecases/archive_project.py` | `halt` gidiyor, `NameTaken` gidiyor |
| `backend/features/projects/presentation/routes.py` | iki uçtan `NameTaken` yakalaması |
| `backend/main.py` | arşiv artık `halt_project` almıyor |
| `frontend/src/features/projects/ProjectCard.jsx` | arşivdeki kart normal kart |
| `frontend/dist/**` | kaynakla aynı commit |
