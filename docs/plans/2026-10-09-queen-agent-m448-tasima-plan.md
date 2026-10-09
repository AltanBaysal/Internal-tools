# Madde 448 — Eski projelerin taşınması, plan

> **Koşum:** ana klasörde, adım adım; commit ana agent'ın. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** her açılışta, `projects.json`'da olmayan eski biçimli projeler bir kez, tek yazmayla
eklenir; eski dosyalara dokunulmaz; kod tek yerde ve kolay silinir.

**Yaklaşım:** önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m448](../specs/2026-10-09-queen-agent-m448-tasima-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları İngilizce; testlerin hata mesajları Türkçe.
- `frontend/` değişmez, `dist` yeniden derlenmez.
- Eklenen her parçanın yanında *"448 onaylanınca kalkar"* yorumu.
- `git add`, commit, stash yok.

---

## Görev 1: `Store.mtime`

- [ ] `test_store.py`: `mtime` dosyanın zamanını verir. Kırmızı.
- [ ] `store.py`: `mtime`, yorumuyla. Yeşil.

## Görev 2: `FileProjectStore.take_in`

- [ ] `test_old_projects.py`'nin depo kısmı: `take_in` verileni tek değişiklikle ekler (tek yazma),
  olan id'ye dokunmaz, satırlar `put_chat` / `put_file`'ınkiyle aynı. Kırmızı.
- [ ] `file_project_store.py`: `_chat_row(chat)` ve `_file_row(name, modified_at)` ayrılır;
  `put_chat`, `put_file`, `take_in` onları kullanır; `take_in` arşivi ve pini `_keep_if` ile yazar.
  Yeşil.

## Görev 3: `data/old_projects.py`

- [ ] `test_old_projects.py`: eski düzeni tohumlayan yardımcı; spec'in *Testler*'i. Kırmızı.
- [ ] `old_projects.py`: `move_old_projects(store, projects)` — kökü bir kez listeler, kayıtta olanı,
  `trash`'i ve `projects.json`'ı adından atlar; gerisini listeler, `project.json` olanı okur (ad, doğuş,
  işaretler, sohbetler `_as_chat` ile, dosyalar ve mtime'ları); okunamayanı log'layıp atlar; bulunanı
  tek `take_in`'le verir. Yeşil.

## Görev 4: bağlama

- [ ] `test_composition.py`: `main.py` taşımayı çağırıyor. Kırmızı.
- [ ] `main.py`: `FileProjectStore`'dan hemen sonra tek satır. Yeşil.

## Görev 5: reviewer'ın bulguları

- [ ] `old_projects.py`: eski düzenin bütün adları yerel sabit (`CHATS_DIR`, `CHAT_SUFFIX`,
  `FILES_DIR`, …); `file_chat_store`'dan yalnız `_as_chat` alınır.
- [ ] `old_projects.py`: okunan her sohbetten hemen `ChatSummary` tutulur, `Chat` değil.
- [ ] `test_old_projects.py`: bir projede `mtime`'ı `OSError` veren Store → yalnız o atlanır. Kırmızı.
  `move_old_projects` `(_Unreadable, OSError)` yakalar. Yeşil.
- [ ] `test_old_projects.py`: sohbet zamanı sayı olan eski proje taşınmaz, sonraki açılış okur.
  Kırmızı. `take_in` her kaydı `_as_project` ile okur, okunamayanı `(id, hata)` olarak döner;
  taşıma log'a yazar. Yeşil.
- [ ] `test_old_projects.py`: taşıyan açılış stderr'e bir satır yazar, sonraki yazmaz. Kırmızı.
  İlk bulunan eski projede `print(..., file=sys.stderr)`. Yeşil.
- [ ] `test_notebook.py`: Serve hücresi `server.poll()`'a bakıyor. Kırmızı. Hücre (NotebookEdit):
  `server = subprocess.Popen`, sunucu yaşadıkça 10 dk'lık tavana kadar bekleme, 30 sn'de bir
  "⏳ Sunucu hâlâ açılıyor", ölünce log ve "kapandı", tavanda gerçek saniyeyle hata. Yeşil;
  `tmp/m448/serve_wait.py` ile ölen ve cevap vermeyen sunucuda denenir.

## Görev 6: QA'nın bulguları

- [ ] `test_old_projects.py`: tek sohbetin sayı olan mesaj zamanı, sayı olan sohbet doğuşu, sayı ya
  da `null` proje doğuşu → o proje taşınmaz, sonraki açılışta `list_projects` cevap verir. Kırmızı.
  `old_projects.py`'de `_time`: okunan her zaman `_read`'in korumasında metin mi diye bakılır. Yeşil.
- [ ] `test_old_projects.py`: `take_in` karşılaştırılamayan son kullanımları olan kaydı eklemez
  (ikinci çizgi, doğrudan).
- [ ] `test_old_projects.py`: yalnız okunamayan eski projeleri olan açılış "Moving projects" satırını
  basmaz, iki açılışta da.
- [ ] Spec §3: değişmeyen `projects.json` yazılmaz (`QueuedWrite`).

## Görev 7: ölçüm ve suite'ler

- [ ] `tmp/m448/measure.py`: 446'nın tohumu eski düzende; taşıyan açılışın ve ikinci açılışın işlem
  sayıları → spec'in *Ölçüm*'ü.
- [ ] Dört suite, sırayla; frontend'ler PowerShell'den, `Set-Location 'D:\Github\Internal-tools'`.
