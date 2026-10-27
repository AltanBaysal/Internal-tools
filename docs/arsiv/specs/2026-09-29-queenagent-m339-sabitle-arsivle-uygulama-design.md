# Madde 339 — Proje sabitlenir ve arşivlenir, sunucu · uygulama turu

**Kaynak:** [yol haritasının 339'u (v9-2b)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m339-sabitle-arsivle-testler-design.md) — nerede
saklandığı, neden, ve kapının biçimi orada. Bu belge kırmızı testleri yeşile getiren kodu anlatır.

**Kullanıcıdan gereken:** hiçbir şey.

## Parçalar

Katmanlar CODE-STANDARD'daki gibi: `presentation → domain ← data → services`. Servis değişmez —
`Store`'un `exists`, `write_text` ve `remove`'u yetiyor.

**`domain/project.py`** — `Project` iki alan kazanır: `pinned: bool = False`, `archived: bool = False`.
Sayılar gibi okunurken diskten türetilir, ve `project.json`'a geri yazılmaz. Varsayılan `False`,
böylece bugün `Project(...)` kuran her yer olduğu gibi kalır.

**`domain/ports.py`** — `ProjectStore` iki yöntem kazanır:
`set_pinned(project_id, pinned) -> None` ve `set_archived(project_id, archived) -> None`.

**`data/file_project_store.py`** — iki sabit, `PINNED_FILE = "pinned"` ve `ARCHIVED_FILE = "archived"`.
`list_all` her proje için iki dosyanın varlığını okur. İki yöntem aynı işi yapar, o yüzden ortak bir
`_mark(project_id, name, on)`'a gider: dosya zaten istenen hâldeyse hiçbir şey yapmaz — yeniden
sabitlemek sabitlendiği anı kaydırmaz, olmayanı silmek hata vermez —; yoksa `on` ise boş bir dosya
yazar, değilse siler. Projenin var olup olmadığını denetlemez: use case onu önceden arıyor.

**`domain/usecases/edit_project.py`** — `edit_project(store, project_id, name=None, pinned=None,
archived=None)`. `None` gönderilmemiş demek, bugünkü `name` gibi. Önce proje aranır, yoksa
`ProjectNotFound`, ve hiçbir şey yazılmaz. `name` geldiyse bugünkü kural — kırpılır, boşsa
`InvalidProjectName` — ve `store.replace` yalnız o zaman çağrılır: `project.json` oluşturulunca ve
yeniden adlandırılınca yazılır, sabitleyince değil. `pinned` ve `archived` gelirse kendi
yöntemleriyle yazılır. Use case projeyi diskten yeniden okuyup döner: sayılar ve iki işaret diskin
cevabı, ve kapı artık kendisi yeniden okumaz.

`name` önce denetlenir, işaretlerden önce: boş adla gelen bir istek hiçbir şey yazmadan reddedilir.

**`presentation/routes.py`** — `PATCH` gövdeden `pinned` ve `archived`'ı da use case'e verir, ve use
case'in döndüğü projeyi yazar. `_project_json` `"pinned"` ve `"archived"`'ı ekler; liste, oluşturma
ve düzenleme aynı fonksiyondan geçtiği için üçü de ikisini söyler.

**`CODE-STANDARD.md`** — tabloya iki satır:

| Artifact | The question it answers | Written when |
|---|---|---|
| `pinned` | is this project pinned, and since when | on pin; removed on unpin |
| `archived` | is this project archived | on archive; removed on unarchive |

Tablonun altındaki *"a field that answers a fifth question wants a fifth artifact"* artık altı dosyayla
yanlış sayıyor; cümle sayıyı bırakır: yeni bir soru kendi dosyasını ister.

## Değişmeyenler

- Ön uç ve `dist`. `useProjects`'in `editProject`'i bugünkü hâliyle v9-2q ve v9-2t'ye yetiyor.
- Liste sırası (`list_projects`) — v9-2j'nin.
- Silme: proje klasörü bütünüyle çöpe gidiyor, iki dosya da onunla.

## Nasıl görülür

CLAUDE.md'deki dört satır: queen-agent'ın arka ucu 946 yeşil, ön ucu 652; queen-editor'ün arka ucu
377'nin bilinen iki kırmızısı ve 1158 yeşil, ön ucu 749.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m339-sabitle-arsivle-uygulama-plan.md).
