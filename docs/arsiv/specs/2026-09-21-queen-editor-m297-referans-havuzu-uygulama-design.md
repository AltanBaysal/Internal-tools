# Madde 297 — Referans havuzu diskte, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m297 test turu](2026-09-21-queen-editor-m297-referans-havuzu-testler-design.md),
`68285f01` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Katmanlar

Hepsi **`features/photo_generation/`'ın içinde**. Referanslar kendi özelliği olamaz: CODE-STANDARD
*özellik ↛ özellik* diyor, ve 302–305'te video üretimi havuzu okuyacak. Kartlarla aynı özelliğin
içinde, ayrı dosyalarda.

**`domain/references.py`** — saf kural, üç şey:
- `PICTURE / VIDEO / AUDIO` ve uzantı tablosu. Sözcükler H3'ün etiketleri; havuz onları beslemek
  için var.
- `kind_of(name)` — uzantıdan tip, ya da None.
- `free_name(name, taken)` — tarayıcıdan gelen adı havuzun içinde tutan ve dolu bir adı ezmeyen ad.

**`domain/ports.py`** — `ReferenceStore`: `save`, `names`, `delete`.

**`domain/usecases/`** — üçü de proje yokluğunda `ProjectMissing` atar *(`start_batch`'ten, öteki
senaryoların yaptığı gibi)* ve **havuzun son hâlini** döndürür: ekran zaten sırada onu soracaktı.
- `add_references(store, pool, project, files)` — `files` `(ad, baytlar)` çiftleri. **Önce hepsi
  karara bağlanır, sonra tek bir dosya yazılır**; `remove_frames` ve `remove_layer` de böyle
  çalışıyor. Tanınmayan bir uzantı `UnknownReference` atar ve hiçbir şey yazılmaz.
- `list_references(store, pool, project)` — tipi okunamayan dosya listede yok.
- `remove_reference(store, pool, project, name)`.

**`data/reference_store.py`** — `DriveReferenceStore`: `<proje>/referans/` altına yazar, okur,
siler. `names` **zaman damgasına, eşitlikte ada** göre sıralar: sıra bu katmanın bildiği bir şey,
çünkü dosya sistemi onun. `dir_path` Flask'ın dosyayı diskten servis etmesi için.

**`presentation/reference_routes.py`** — kendi blueprint'i, dört kapı:
`POST/GET /api/projects/<project>/references`, `POST …/references/<name>/delete`, ve
`GET /references/<project>/<filename>`. Çeviri dışında iş yok; cümleler domain'den geldiği gibi
çıkar.

## Sıra kuralı turun ortasında değişti

Test turu *"liste yükleme sırasında"* demişti ve sırayı dosyanın zaman damgasından okumayı
öngörüyordu. **Gerçek diskte tutmadı:** tek bir yüklemenin iki dosyası bazen aynı damgayı alıyor,
bazen almıyor — aynı test iki koşuda iki farklı sıra verdi. Dosya damgası yazma işleminden daha
kaba, ve bu makineye göre de değişiyor.

Yükleme sırası **diskte yazılı değil**, yani okunamaz. Havuz bu yüzden **ada göre** okunuyor: bir
klasörün gerçekten söz verebildiği tek sıra bu. Kullanıcının istediği sıra zaten ayrı bir soru ve
**300**'ün kendi belgesine gidiyor — CODE-STANDARD'ın *"dördüncü soruya dördüncü dosya"* kuralı.

İki test bu yüzden düzeltildi *(`test_the_pool_lists_in_one_stable_order` ve rotaların uçtan uca
testi)*. Kod testi tutturmak için değil, test diskin veremeyeceği bir sözü verdiği için.

## Ayrıntılar

**Boş yükleme bir sonuçtur, hata değil.** Dosyasız bir istek havuzu olduğu gibi geri verir —
`queue_layer`'ın *"boş kapsam bir sonuçtur"* kuralı.

**Önbellek.** Fotoğraf sonsuza kadar önbelleklenir, çünkü numarası asla tekrar kullanılmaz. Referans
öyle değil: silinen ad yeniden verilebilir, o yüzden `no-store`.

**`main.py`** havuz deposunu kurar ve ikinci blueprint'i kaydeder.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil; turun on altı testi döner.
