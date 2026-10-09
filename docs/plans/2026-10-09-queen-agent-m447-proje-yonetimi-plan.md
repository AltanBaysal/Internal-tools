# Madde 447 — Proje yönetimi, plan

> **Koşum:** ana klasörde, adım adım; commit ana agent'ın. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** projenin bütün metadatası kökteki tek `projects.json`'da; sunucu onu açılışta bir kez okur,
bellekten cevaplar, tek bir arka plan yazıcısıyla diske yazar. API ve ekran değişmez.

**Yaklaşım:** her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m447](../specs/2026-10-09-queen-agent-m447-proje-yonetimi-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları İngilizce; testlerin hata mesajları — dosyalarda olduğu gibi — Türkçe.
- `frontend/` değişmez, `dist` yeniden derlenmez.
- Bir kökü ikinci bir `FileProjectStore` ile açan her test (yeniden başlatma), önce birincinin
  `flush()`'ını çağırır.
- `git add`, commit, stash yok.

---

## Görev 0: önceki ölçüm

- [x] `tmp/m447/measure.py`: 446'nın betiği, aynı tohumla, projenin her isteği için (açılış, liste,
  Archive basışı, Unarchive, Pin, Rename, proje açmak, dosya açmak, yeni proje, silmek); eski ya da
  yeni düzeni koddan anlar, yazıcıyı `flush` ile isteğin hanesinde sayar. Koşuldu → `before.txt`.
  `tmp/m446/measure.py` de yeniden koşuldu: 1366 ve 4771, 446'daki gibi.

## Görev 1: Store — klasör yalnız yoksa

Suite bu görevin sonunda yeşil: sözleşme aynı.

- [ ] `test_store.py`: var olan klasöre yazmak ve taşımak `os.makedirs` çağırmaz (monkeypatch ile
  sayılır); olmayan klasör yine yaratılır (var olan test); taşıma testi `exists` yerine `list_dir`'le
  bakar. Kırmızı.
- [ ] `store.py`: `write_text` ve `move` önce dener, `FileNotFoundError`'da klasörü yaratıp bir kez
  daha. Yeşil. (`exists`, `mtime`, `remove` Görev 3'te, son çağıranları gidince.)

## Görev 2: yazıcı — `data/queued_write.py`

Suite yeşil: yeni modül, henüz kimse kullanmıyor.

- [ ] `test_queued_write.py` (yeni): spec'in *Yazıcı* testleri. Yazmayı tutan bir sahte Store
  (`threading.Event` ile yazmayı ortasında bekletebilen) ile: `changed()` beklemez; `flush()`'tan
  sonra dosyada son durum; yazma sürerken üç değişiklik tek bir sonraki yazma; aynı metin yeniden
  yazılmaz; başarısız yazma beklenip (testin kendi `pause`'u) en çok `TRIES` kez yeniden denenir,
  her deneme `caplog`'da hatanın sözüyle; başlatılamayan iş parçacığı `flush()`'ı kilitlemez;
  `flush()`'tan sonra yazıcının iş parçacığı yok. Kırmızı.
- [ ] `queued_write.py`: `QueuedWrite(store, path, render, pause=time.sleep)`, `changed()`,
  `flush()`. Yeşil.
- [ ] `main.py`: SIGTERM → `sys.exit(0)`, yazıcı beklensin diye; `test_composition.py` tutar.

## Görev 3: tek dosya — depo, port, sohbet ve dosya depoları, bağlama

Bu görevin alt adımları arasında suite yeşil kalamaz: sayılar ve son kullanım artık sohbet ve dosya
depolarının koyduğu kayıtlardan geliyor, ve üç depo birlikte değişiyor. Her alt adımın kendi test
dosyası kendi adımında yeşil; suite görevin sonunda yeşil.

### 3a · Domain

- [ ] `chat.py`: `ChatSummary(id, title, created_at, last_activity)`.
- [ ] `ports.py`: `ProjectStore` — `add`, `get`, `list_all`, `update(project_id, change)`, `delete`;
  `ChatStore.list_for` → `list[ChatSummary]`. Belgeleriyle.
- [ ] `test_pin_archive.py`'nin kullanım durumu bölümü ve `test_edit_project.py`: sahte port
  `update`'i tutar ve değişikliği uygular; sabitlemek `now`'ı yazar, ikinci sabitleme anı kaydırmaz,
  arşive girmek ve çıkmak pini siler, arşivde olmayana `archived=False` pine dokunmaz, olmayan proje
  `ProjectNotFound` ve `update` hiç değişiklik uygulamaz, boş ad reddedilir. Kırmızı.
- [ ] `edit_project.py`: `edit_project(store, project_id, now, name=None, pinned=None,
  archived=None)` — bir değişiklik fonksiyonu, Madde 384 içinde; `update`'in döndüğünü döner.
  `project.py`: yorumlar (alanlar `projects.json`'dan, sayılar dizilerden). Yeşil.

### 3b · `FileProjectStore`

- [ ] `test_file_project_store.py` yeniden yazılır — spec'in *Depo* testleri; sayan bir Store
  sarmalayıcısıyla "kurulduktan sonra okuma yok". Kırmızı.
- [ ] `file_project_store.py`: açılışta okuma ve denetim (`ProjectsUnreadable`), bellek ve kilit,
  `_change`, port (`add` tek değişiklik, id denetimi içinde, klasörsüz), veri katmanının `put_chat` /
  `put_file` / `drop_file` / `chats` / `files` / `file`, `flush`, `QueuedWrite` ile yazma; silmede
  kaydın çöpe yazılması, içeriği zaten yoksa da. Yeşil.

### 3c · `FileChatStore` ve `FileFileStore`

- [ ] `test_file_chat_store.py`: depo `FileChatStore(store, projects)`, `p1` projesi doğmuş olarak
  (yerel yardımcı); elle yazılan eski biçimli sohbetler kayıtlarıyla birlikte; yeni testler — yazınca
  kayıt gelir (başlık, anlar), içerik kayıttan önce, kaydı olmayan sohbet diske gitmeden `None`,
  liste bellekten; "sohbet olmayan dosyalar atlanır" testi kayıt kuralına döner.
- [ ] `test_files_api.py`, `test_read_file.py`, `test_delete.py`, `test_tools.py`: `_files` yardımcısı
  projeyi doğurup `FileFileStore(store, projects)` döner; yeni testler — yazınca kayıt ve an, kaydı
  olmayan dosya `None`, silinince kayıt düşer. `test_files_api`'nin `time.sleep`'i an artık sunucunun
  saatinden geldiği için kalır (iki yazma aynı milisaniyeye düşmesin). Kırmızı.
- [ ] `file_chat_store.py`, `file_file_store.py`: kurucuya `projects`; varlık ve listeler bellekten,
  yazma içerikten sonra kaydı koyar, silme kaydı düşürür. Yeşil.
- [ ] `store.py`: `exists`, `mtime`, `remove` gider (son çağıranlar gitti).

### 3d · Kapı ve bağlama

- [ ] `routes.py`: `edit_project(..., now=_now())`.
- [ ] `main.py`: `projects = FileProjectStore(store)`, `ProjectsUnreadable`'da `SystemExit` ile açık
  mesaj; `FileChatStore(store, projects)`, `FileFileStore(store, projects)`.
- [ ] Kurulumu değişen API ve kullanım durumu testleri — yeni bağlama, yeniden açmadan önce `flush`,
  dosyanın şeklini değil davranışı tutan yerler:
  - `test_pin_archive.py` — depo bölümü `projects.json`'a döner (`pinnedAt`, `archived`, ikinci
    sabitleme anı kaydırmaz); eski arşivin bıraktığı pin dosyası testi kalkar (taşıma yok, öyle bir
    dosya artık okunmuyor).
  - `test_last_activity.py` — depo bölümü: son kullanım sohbetlerin en yeni `lastActivity`'si, pin
    anı `pinnedAt`; mtime'a dokunan testler kalkar.
  - `test_delete_project.py` — tek `FileProjectStore`; çöpte `chats`, `files`, `project.json`.
  - `test_projects_api.py` — kökteki yabancı dosya proje değil (artık kök taranmıyor; test kalır).
  - `test_append_message.py`, `test_chats_api.py`, `test_stream_answer.py` — bağlama; ayrı bir
    `FileChatStore` ile sohbet ekleyen yerler istemcinin depolarını kullanır.
- [ ] Dört suite'ten Python olanı yeşil.

## Görev 4: kurallar

- [ ] `FOUNDATION.md`, 2. ilke: metadatanın istisnası, nedeniyle (spec 6).
- [ ] `CODE-STANDARD.md`, *Separation of concerns*: tablo ve altındaki paragraf (spec 6).

## Görev 5: sonraki ölçüm

- [ ] `python tmp/m447/measure.py after` → `after.txt`; spec'in tablosundaki sayılar ve
  `projects.json`'ın boyu ondan.

## Görev 6: suite'ler

- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
