# Madde 382 — Arşive giden projenin sabitlemesi kalkar · uygulama turu

**Kaynak:** [yol haritasının 382'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); test turu
[2026-09-30-queenagent-m382-arsiv-sabitleme-testler-design.md](2026-09-30-queenagent-m382-arsiv-sabitleme-testler-design.md)
ve onun kırmızı commit'i. Kararlar orada; bu belge onları hangi dosyanın nasıl taşıdığını söyler.

**Kullanıcıdan gereken:** hiçbir şey.

## Sunucu

1. **`domain/project.py`** — `pinned` özelliği `bool(self.pinned_at) and not self.archived`.
   `pinned_at` diskteki sabitleme anı olarak kalır (arşivde de); yorumu bunu söyler: arşivdeki
   projenin anı sabitlilerin arasındaki yeri, ve `Undo` onu geri verir.
2. **`domain/usecases/list_projects.py`** — sabitliler bloğu `project.pinned_at`'la kurulur, sabitli
   okunmayan arşivdekiler de o yerde durur; sıralama anahtarı değişmez. Yorum neden: `Undo` satırı
   orada durur, ekran sıra kurmaz.
3. **`domain/usecases/edit_project.py`** — `archived is False and current.archived and not pinned`
   ise `store.set_pinned(project_id, False)`: `Unarchive` sabitlemeyi geri getirmez, `pinned: true`
   ile gelen `Undo` getirir. `current` zaten okunuyor; port değişmez.
4. **`data/file_project_store.py`** — değişmez. `PINNED_FILE`'ın üstündeki yorum sabitleme dosyasının
   arşivde kaldığını da söyler.
5. **Rotalar** değişmez: `PATCH` `pinned` ve `archived`'ı zaten ikisini birden alıyor.

## Tarayıcı

6. **`AllProjectsScreen.jsx`** — `undoing` `{ id, pinned }` olur; `Archive`'da satırın `pinned`'ı
   `projects`'ten okunur. Projeler sekmesinde `Undo` satırının projesi `pinned: undoing.pinned` ile
   gösterilir, böylece `Pinned`'de ya da `Recent`'te — sunucunun sırasıyla — durur. `undo`
   `onRestoreProject(id, pinned)`'ı bekler. "the server moves no row for an archive" yorumu bugünü
   söyler: sunucu sabitlemeyi bırakır ama projeyi sabitlemesinin yerinde listeler.
7. **`App.jsx`** — `onRestoreProject={(id, pinned) => editProject(id, { archived: false, pinned })}`.
8. **`ProjectRow.jsx`** değişmez: `Unarchive` `onArchive(id, false)` kalır.

## Belge

9. **`CODE-STANDARD.md`** — tablonun `pinned` satırı: *on pin; removed on unpin and on unarchive —
   an archive leaves it, as the place Undo gives back, and an archived project reads as unpinned*.

## Tutmadıkları

- `dist` — koşuyu yöneten derler (görev tanımı).
- `Archived` sekmesinin sırası (test turunun Karar 2'si) — açık nokta.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel; dördü de yeşil. Adım adım dökümü
[uygulama planında](../plans/2026-09-30-queenagent-m382-arsiv-sabitleme-uygulama-plan.md).
