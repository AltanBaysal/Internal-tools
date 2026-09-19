# Madde 223 · Arşivdeki ad tutulmuş sayılacak — uygulamanın tasarımı

**Test turu:** [tasarım](2026-09-16-queen-editor-m223-arsiv-ad-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı duran on bir çivi *(yedi arka uçta, dördü ekranda)* bunları istiyor.

## 1 · Kural: arşivi bilen yer soruyor

[`DriveProjectStore`](../../../queen-editor/backend/features/projects/data/project_store.py) 221'den
beri arşivin nerede olduğunu bilen **tek yer** — `_in_archive` orada duruyor. Kural da oraya iniyor:

```
is_archived(name)  ->  storage.dir_exists(_in_archive(name))
create(name)       ->  is_archived ise None, yoksa eskisi gibi
rename(old, new)   ->  is_archived(new) ise None, yoksa eskisi gibi
```

`DriveStorage` **değişmiyor.** O katman proje bilmiyor *("knows no project")*, ve `ARCHIVE_DIR` proje
alanının bilgisi. Arşivi oraya söylemek, kökün altındaki bir klasörün adını dosya katmanına
öğretmek olurdu.

**Kontrol `mkdir`'den önce.** Sonra olsaydı klasör açılır, sonra geri alınırdı — bir an var olmuş
bir proje, ve geri almanın kendisi de yarıda kalabilir. Çivi bunu tutuyor
*(`test_a_refused_name_leaves_no_folder_in_the_root`)*.

**Dönüş değeri yeni değil:** ikisi de `None` dönüyor, yani *"dolu"*. Çağıranların sözleşmesi
değişmiyor; değişen yalnız hangi adların dolu sayıldığı.

## 2 · Cümle: iki durum, iki söz

Redin sebebini `None` taşımıyor, o yüzden **yalnız red yolunda** ikinci bir soru soruluyor:

```python
if project is None:
    raise NameTaken(name_rules.archive_taken(name) if store.is_archived(name)
                    else "Bu ad zaten kullanılıyor. Başka bir ad dene.")
```

Başarılı bir açılış hiçbir şey sormuyor — Drive'da her soru bir gidiş geliş *(madde 225)*.

Cümlenin kendisi [`name_rules`](../../../queen-editor/backend/features/projects/domain/name_rules.py)'a
giriyor, `ARCHIVE_DIR`'ün yanına: ad kurallarının Türkçe sözleri zaten orada, ve **iki kullanım onu
paylaşıyor** — proje açmak ve yeniden adlandırmak. Metni:

> Arşivde `<ad>` adlı bir proje var. Başka bir ad seç ya da önce onu arşivden çıkar.

Kullanıcıyı ne yapacağına dair iki kapıya birden yolluyor, çünkü ikisi de geçerli: başka bir ad, ya
da arşivden çıkarmak.

**`archive_project`'in kendi cümlesi duruyor** *("Arşivde zaten … Önce onu geri al ya da adını
değiştir.")*. O red artık kullanıcının yürüyebildiği bir yolda değil — ama kökte elle açılmış bir
klasör aynı çakışmayı yine doğurabilir, ve o gün söylenecek söz orada.

## 3 · Ekran: hata bir satır, liste yerinde

[`ProjectsScreen`](../../../queen-editor/frontend/src/features/projects/ProjectsScreen.jsx) bugün
arşivin **hiçbir** hatasını göstermiyor: `handleArchive` ile `handleRestore` `try/catch` taşımıyor,
ve tarayıcıda yakalanmamış bir promise reddi ekrana hiçbir şey yazmıyor.

- `actionError` — son işlemin cümlesi, ya da `null`.
- İki işleyici de `try/catch`: yakalarsa `err.message`, tutarsa `null`. `api.js` zaten sunucunun
  kendi cümlesini fırlatıyor, yani burada uydurulacak bir sebep yok.
- Çizim: listenin **üstünde** tek satır — `Icon.Warn` + `Note size={13}`, `var(--danger)`.
  Uygulamanın başka yerlerinde duran satırın aynısı *(`PhotoDetail`, `ExportScreen`)*.

**Liste silinmiyor.** `StatusErrorCard` listenin **yerine** geçiyor ve o doğru davranış — ama
*yükleme* hatası için. Bir işlem hatasında kartlar duruyor, çünkü kullanıcı birazdan aynı düğmeye
basacak.

**Arşive girip çıkmak da temizliyor:** `toggleArchive` satırı siliyor — bir listenin hatası ötekinin
üstünde durmamalı.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `backend/features/projects/data/project_store.py` | `is_archived`, ve `create`/`rename`'in onu sorması |
| `backend/features/projects/domain/name_rules.py` | `archive_taken(name)` |
| `backend/features/projects/domain/usecases/create_project.py` | red yolunda cümleyi seçmek |
| `backend/features/projects/domain/usecases/rename_project.py` | aynısı |
| `frontend/src/features/projects/ProjectsScreen.jsx` | `actionError`, iki `try/catch`, bir satır |

`DriveStorage`, rotalar ve `archive_project` **değişmiyor** — 409'u zaten `NameTaken` doğuruyor, ve
rotalar onu zaten çeviriyor.
