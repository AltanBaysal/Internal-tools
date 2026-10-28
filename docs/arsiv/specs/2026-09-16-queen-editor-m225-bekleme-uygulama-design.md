# Madde 225 · Beklerken ekran susmayacak — uygulamanın tasarımı

**Test turu:** [tasarım](2026-09-16-queen-editor-m225-bekleme-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Altı çivi iki dosyada karşılanıyor, ve arka uca hiç inilmiyor.

## `ProjectsScreen` — kim bekliyor

Tek bir durum: `working`, ya `null` ya da `{ name, label }` — hangi proje, ve kartında ne yazacağı.
Ad da gerekiyor çünkü listede tek bir kart bekliyor, hepsi değil.

```
handleArchive   ->  { name, label: "Arşivleniyor…" }
handleRestore   ->  { name, label: "Geri alınıyor…" }
```

Kelimeyi ekranın tutması, kartın değil: hangi hareketin yapıldığını bilen o. `ProjectCard` yalnız
verilen kelimeyi yazıyor, ve böylece bir gün üçüncü bir hareket gelse kart değişmiyor.

**Temizlenme yeri iki farklı yerde, ve bilerek:**

- **Başarıda** liste *(arşivde iki liste)* yeniden okunduktan **sonra**. Okuma da Drive'a gidiyor;
  kelimeyi cevabın gelişinde kaldırmak, o okuma boyunca ekranı yine susturur.
- **Hatada** hemen, ve yerine 223'ün hata satırı geçiyor. İki cümlenin aynı anda durması, ikisinin de
  ne dediğini bulandırırdı.

## `ProjectCard` — ne çiziliyor

Yeni bir `busy` özelliği: gösterilecek kelime, ya da `null`.

- Kelime **tarihin yerinde** duruyor. Kart iki satır: ad ve tarih. Üçüncü bir satır eklemek kartı
  büyütürdü, ve tarih bu iş bitince zaten değişecek olan şey.
- **Üç düğme de kapalı.** Yalnız ikinci bir arşivleme değil: silme ve ad değiştirme de aynı klasöre
  ve aynı işarete dokunuyor, ve ikisi de bu iş sürerken araya girmemeli.
- Kart **hâlâ tıklanabilir** — projeye girmek hiçbir şeyi değiştirmiyor, ve arşivlenen proje zaten
  çalışmaya devam ediyor *(madde 227)*.

Kelime `Mono` ile yazılıyor, tarihin kendi biçimiyle — orada duran şeyin yerini alıyor, yanına
başka bir ses koymuyor.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `frontend/src/features/projects/ProjectsScreen.jsx` | `working` durumu, iki işleyicide kurulup kaldırılması |
| `frontend/src/features/projects/ProjectCard.jsx` | `busy` özelliği: kelime ve kapalı düğmeler |
| `frontend/dist/**` | kaynakla aynı commit |
