# Madde 384 — Arşiv sabitlemeyi sunucuda siler; Archived yalnız son kullanıma göre · uygulama turu

**Kaynak:** [yol haritasının 384'ü](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); test turu
[spec'i](2026-09-30-queenagent-m384-arsiv-sabitlemeyi-siler-testler-design.md) ve kırmızı commit'i
`c8efd4a2`. Uygulama o testlerin tuttuğunu yapar, fazlasını değil.

## Düşünülen yollar

1. **Kural kullanım durumunda (seçilen).** `edit_project` arşiv işareti değişince sabitlemeyi siler;
   `Project.pinned` arşivdeki projeyi sabitli okumaz; `list_projects` blokları `pinned`'le kurar.
   Kural domain'de, `data/` yalnız dosyaları yazar (CODE-STANDARD).
2. **Mağazanın `set_archived`'ı `pinned` dosyasını da silsin.** Daha az satır, ama bir kural `data/`'ya
   girer, ve sahte portla test edilemez. Reddedildi.
3. **Eski dosyaya dokunmamak** — yalnız arşivde silmek. En az kod, ama 382 döneminden kalmış bir proje
   `Archived`'da öne dizilir ve `Unarchive`'la sabitli döner: maddenin düzelttiği hata aynen kalır
   (A3 testi). Reddedildi.

## Sunucu

- **`edit_project.py`:** `archived` gönderildiyse ve projenin bugünkü hâlinden farklıysa — arşive giriyor
  ya da çıkıyor — `store.set_pinned(project_id, False)`. Girişte bu 384'ün kuralı; çıkışta yeni verilerde
  silinecek bir şey yoktur (`_mark` yoksa dokunmaz), eski bir dosya ise temizlenir. Arşivde olmayan
  projeye gelen `archived=False` hiçbir şey değiştirmez. 382'nin `archived is False and current.archived
  and not pinned` özel durumu ve yorumu kalkar: `Undo` artık sabitleme istemiyor.
- **`project.py`:** `pinned` `bool(self.pinned_at) and not self.archived` kalır, ama işi değişir:
  arşivdeki proje hiçbir zaman sabitli değildir — diskte önceki kuralın bıraktığı bir dosya olsa da.
  Yorumu buna göre, 382'nin "Undo'nun geri verdiği yer" cümlesi kalkar.
- **`list_projects.py`:** bloklar yeniden `project.pinned`'le kurulur (382'den önceki hâli); `pinned_at`'e
  bakan özel durum ve yorumu kalkar. Arşivdekiler böylece son kullanıma göre dizilir.
- **`file_project_store.py`:** `PINNED_FILE`'ın yorumundan *"and why an archive leaves it too…"* kalkar.
- **CODE-STANDARD'ın `pinned` satırı:** *on pin; removed on unpin, on archive and on unarchive — an
  archived project is never pinned*. (Unarchive'daki silme yalnız eski bir dosyada iş yapar, ama satır
  diskte ne olduğunu değil kodun ne yaptığını söylüyor.)

## Tarayıcı

- **`AllProjectsScreen.jsx`:** `undoing` yeniden yalnız id. `Undo` → `onArchiveProject(id, false)`, cevap
  gelene kadar satır durur (363'ün kuralı). `onRestoreProject` prop'u ve `{ ...project, pinned:
  undoing.pinned }` eşlemesi kalkar: satır sunucunun listesinin onu koyduğu yerde durur, ve sunucu arşivde
  sabitlemeyi sildiği için bu `Recent`. `undoing`'in yorumu bunu söyler.
- **`App.jsx`:** `onRestoreProject` satırı kalkar.

## Değişmeyen

- Tasarımdan ayrılış (`Undo` sabitlemeyi geri vermez) — kullanıcının kararı; test spec'inde yazılı.
- Arşiv isteği dönmeden önceki birkaç milisaniyede `Undo` satırı projenin eski yerinde görünür; tarayıcı
  sunucunun kuralını kopyalamaz (FOUNDATION, Karar 4). Raporda açık nokta.
- `dist` — koşuyu yöneten derler.

## Nasıl görülür

Dört satır, paralel: dört süit yeşil. Commit: `feat: Madde 384 -- …`.
