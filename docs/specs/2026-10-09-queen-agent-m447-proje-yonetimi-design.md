# Madde 447 · Proje yönetimi — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
447 · **Dal:** `feat/queenagent-v10`, ana klasörde, commit ana agent'ın · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Öncesi:** 446 — sebep ve ölçüm, `tmp/m446/` · **Ölçüm:** `tmp/m447/measure.py`, `before.txt`,
`after.txt`

## Ne, neden

Kullanıcı, 9 Ekim: *"maintain etmesi kolay, hızlı ve basit bir tasarım olması lazımdı galiba, şu anda
çok karıştı"*, *"proje listesi tek dosya okumak"*, *"bu yazmaları Flask yönetir, Drive değil; Flask'a
öyle bir özellik ekle, queue gibi … lütfen disk read and write'ları minimuma indir"*.

446 sebebi buldu: bugün projenin hiçbir bilgisi tek yerde durmuyor. Adı `project.json`'da, pini ve
arşivi ayrı boş dosyalarda (varlıkları ve mtime'ları), sohbet ve dosya sayısı klasör listelerinde, son
kullanım en yeni sohbet dosyasının mtime'ında. Bir projeyi bulmak bütün kökü taramak demek
(`get` → `list_all`), ve her tarama proje başına 6 işlem artı sohbet başına bir `stat`. Bir Archive
basışı bunu üç kez yapıyor: 30 projede 1366, 100 projede 4771 dosya işlemi; Drive'da her biri bir
gidiş-dönüş, ve 20 ms'lik bir gidiş-dönüşle 30 projede basış 29,6 saniye.

447 projenin bilgisini tek bir dosyaya, `projects.json`'a toplar; sunucu onu açılışta bir kez okur,
bellekte tutar, ve değişince tek bir arka plan yazıcısıyla diske yazar.

## Olacak

### 1 · `projects.json` — kökte, tek dosya

Proje id'siyle anahtarlı bir nesne. Her proje:

- `name`, `createdAt` — her zaman.
- `pinnedAt` — yalnız sabitliyken: sabitlendiği an. Bugün `pinned` dosyasının mtime'ıydı.
- `archived: true` — yalnız arşivliyken.
- `chats` — `[{id, title, createdAt, lastActivity}]`: kenar çubuğunun sohbet listesinin istediği
  her şey. `lastActivity` sohbetin açık kolunun son mesajının anı (`Chat.last_activity`), sohbet her
  yazıldığında yenilenir.
- `files` — `[{name, modifiedAt}]`: dosya panelinin istediği her şey. `modifiedAt` dosyanın yazıldığı
  an; bugün dosyanın mtime'ıydı.

Sohbet sayısı, dosya sayısı ve projenin son kullanımı **yazılmaz**, dizilerden hesaplanır: sayılar
dizilerin uzunluğu, son kullanım sohbetlerin en yeni `lastActivity`'si, sohbet yoksa `createdAt`.
Dosyanın uzantı çipi adından hesaplanır, bugünkü gibi.

```json
{
  "p3f9a1c2b7d40": {
    "name": "Harbour at dusk",
    "createdAt": "2026-10-01T09:12:45.120+00:00",
    "pinnedAt": "2026-10-05T18:02:11.004+00:00",
    "chats": [
      {
        "id": "c81d0e2f4a9b3",
        "title": "Write the opening scene",
        "createdAt": "2026-10-01T09:13:02.551+00:00",
        "lastActivity": "2026-10-08T21:40:19.870+00:00"
      }
    ],
    "files": [
      {
        "name": "plan.md",
        "modifiedAt": "2026-10-08T21:40:33.002+00:00"
      }
    ]
  },
  "p0a7c55e91d22": {
    "name": "Thesis",
    "createdAt": "2026-09-14T11:00:00.000+00:00",
    "archived": true,
    "chats": [],
    "files": []
  }
}
```

Girintili ve `ensure_ascii` kapalı, öbür dosyalar gibi: Drive'da bir insan açıp okuyabilir.

**İçerik yerinde kalır:** sohbetin kendisi `<id>/chats/<cid>.json`'da, dosyanın kendisi
`<id>/files/<ad>`'da, şemaları değişmeden. **Önce içerik, sonra kaydı:** bir sohbet ya da dosya önce
kendi dosyasına yazılır, `projects.json`'daki kaydı ondan sonra değişir — yazılmamış bir şeyi
gösteren kayıt hiç olmaz.

**Kalkanlar:** proje başına `project.json`, `pinned` ve `archived` dosyaları.

### 2 · Sunucu metadatayı bellekte tutar — `FileProjectStore`

- **Açılışta bir kez okunur:** `FileProjectStore` kurulurken `projects.json`'ı okur.
  - **Dosya yok** → henüz proje yok, boş liste; bir şey yazılmaz.
  - BOM'la kaydedilmiş dosya (Windows'ta bir editör) okunur; sunucu BOM'suz yazar.
  - **Okunamıyor** (JSON değil, nesne değil, bir projenin adı ya da doğuşu yok, `chats` ya da `files`
    dizi değil, diziler bozuk) →
    `ProjectsUnreadable`; `main.py` bunu yakalar ve sunucu okuyucunun kendi hatasıyla, açık bir
    mesajla durur: *"QueenAgent did not start. In <kök>: projects.json could not be read: <hata>.
    Nothing was written to it."* Dosya boş sayılmaz ve **üstüne hiç yazılmaz**.
- **Okumalar bellekten:** `get`, `list_all`, kenar çubuğunun sohbet listesi (`list_for`), dosya
  paneli (`list_files`), agent'ın dosya adları (`list_names`) diske gitmez.
- **Bir şeyin var olduğunu kayıt söyler:** sohbetin ya da dosyanın içeriği yalnız `projects.json`'da
  kaydı varsa okunur. URL'den gelen bir sohbet id'si ya da dosya adı ancak bellekte bulununca bir
  dosya yoluna döner; bilinmeyen bir id diske hiç gitmeden "yok" cevabını alır (bugün `exists` ile
  bir `stat`). Kaydı duran ama dosyası olmayan bir sohbet ya da dosya — yarıda kalmış bir silmenin
  izi, aşağıda — da "yok" cevabını alır (404), çökmez.
- **`add` tek bir değişiklik:** id'nin alınmış olup olmadığı değişikliğin içinde, kilidin altında
  sorulur; aynı anda iki `add` ikisi de geçemez. Klasör yaratılmaz: projeye yazılan ilk sohbet ya da
  dosya onu yaratır.
- **Değişiklik tek yerden:** `FileProjectStore._change(change)` — kilidin altında belleği değiştirir,
  sonra yazıcıya haber verir. Onu çağıranlar:
  - Port: `add`, `update(project_id, change)` (ad, pin, arşiv), `delete`.
  - Veri katmanı: `FileChatStore`'un yazması (`put_chat`), `FileFileStore`'un yazması (`put_file`)
    ve silmesi (`drop_file`). Olmayan bir projeye `put` hiçbir şey yapmaz.
- **Port değişiyor:** `ProjectStore`'un `replace`, `set_pinned`, `set_archived`'ı kalkar, yerine
  `update(project_id, change) -> Project | None`. `change` domain'in bir fonksiyonu
  (`Project → Project`); depo onun döndürdüğünün adını, `pinned_at`'ini ve `archived`'ını kayda
  yazar. **Madde 384 değişikliğin içinde:** arşive girmek de çıkmak da pini siler (`edit_project`).
  Sabitlemek `pinnedAt`'i şimdiki an yapar, zaten sabitliyse dokunmaz — bugün ikinci sabitleme
  dosyanın mtime'ını kaydırmıyordu. `edit_project` bu yüzden `now` alır; route `_now()` verir.
  `edit_project` yazdığını geri okumaz: `update` güncel projeyi döner.
- **`ChatStore.list_for` artık özet döner:** yeni `ChatSummary(id, title, created_at,
  last_activity)` (`chat.py`). Kenar çubuğu yalnız bunları kullanıyordu; tam sohbeti okumak yüzünden
  bugün sohbet listesi bütün sohbet dosyalarını açıyor.
- **Sohbetin ve dosyanın deposu `FileProjectStore`'u alır** (`main.py` bağlar). `projects.json`'ın
  şemasını yalnız `file_project_store.py` bilir: öbür ikisi kayıtları `put_chat`, `put_file`,
  `drop_file`, `chats`, `files`, `file` ile ister.

### 3 · Yazıcı — `data/queued_write.py`

`QueuedWrite(store, path, render)`: bellekte duran bir durumu diskteki tek bir dosyada güncel tutar.

- `changed()` — "durum değişti". Bekleyen bir yazma işaretlenir; çalışan yazıcı yoksa bir iş
  parçacığı başlar. İstek beklemez, hemen cevap döner. İş parçacığı başlatılamazsa yazıcı "çalışmıyor"
  diye geri işaretlenir ve hata fırlar: `flush()` sonsuza dek beklemez, sonraki değişiklik yeniden
  başlatır.
- Yazıcı döngüsü: işaret varsa indirir, `render()` ile durumun **o anki** metnini alır (deponun
  kilidi altında `json.dumps`), yazar; işaret yoksa biter. Arka arkaya gelen değişiklikler böylece tek
  yazmada toplanır: yazma sürerken gelen on değişiklik, bir sonraki tek yazmada en son hâliyle gider.
- **Aynı metin yeniden yazılmaz:** son başarılı yazmayla aynı metin diske gitmez — örneğin arşivde
  olmayan projeye `archived: false`.
- **Yazma atomik**, bugünkü gibi: `Store.write_text` geçici dosyaya (`projects.json.writing`) yazar ve
  yerine koyar *(kullanıcı — "mantıklı böyle kalsın")*. `projects.json` ya eski ya yeni hâliyle
  durur, hiç yarım kalmaz.
- **Yazma başarısız olursa** kendisi yeniden dener: 5 saniye bekler, en çok 3 deneme (`TRIES`,
  `RETRY_SECONDS`), her denemede durumu yeniden alır — beklerken gelen değişiklikler de gider. Her
  başarısız deneme işletim sisteminin kendi sözüyle loglanır (`logging`, `"projects.json was not
  written (try 1 of 3): <hata>"`). Neden kendisi: kullanıcı değişikliğin başarılı olduğunu gördü, ve
  arkasından başka bir değişiklik gelmeyebilir; gelmezse yeniden başlatma onu kaybederdi. Üç deneme de
  düşerse sonraki değişiklik saymayı yeniden başlatır. Bellek her durumda doğru kalır.
- **`flush()`** yazıcı boşalana kadar bekler (denemeler dahil). Testler ve ölçüm betiği bunu
  kullanır.
- **Kapanış:** iş parçacığı daemon değildir — `daemon=False` açıkça yazılı, çünkü iş parçacığı bu
  bayrağı onu yaratandan alır, ve onu werkzeug'un daemon olan istek iş parçacıkları yaratıyor (QA'nın
  bulduğu); Python normal kapanırken onun bitmesini bekler. Ctrl+C
  normal kapanış; **defterin `pkill`'i (SIGTERM) de öyle yapılır:** `main.py` SIGTERM'e
  `sys.exit(0)` ile cevap verir. Python'un SIGTERM'e kendi cevabı hiçbir şeyi beklemeden çıkmak;
  defterin Serve hücresi her yeniden koşuşta eski sunucuyu böyle kapattığı için, yoksa her yeniden
  koşuş son değişikliği kaybedebilirdi.
- **Gerçek bir çöküş** — `kill -9`, Colab'ın runtime'ı düşerse, elektrik: o an henüz yazılmamış
  değişiklikler kaybolur *(kullanıcı — "flask tak diye kapanırsa kaybolsun sıkıntı yok")*. Pencere bir
  yazmanın süresi kadar. Kaybolanın ne olduğu:
  - pin, arşiv, ad, yeni proje: sunucu yeniden açılınca eski hâliyle;
  - yeni bir sohbet ya da dosya: içeriği diskte, ama kaydı yok — listede görünmez, silinmez de;
    `<id>/chats/` ya da `<id>/files/` içinde elle bulunur. Agent aynı adla yeni bir dosya yaratırsa
    onun üstüne yazar (adların listesi kaydı bilmiyor). **Bu kabul edildi** *(9 Ekim, reviewer'ın
    sorusu, ana agent'ın kararı)*: kullanıcı ani ölümün son anda yazılanı götürmesini kabul etti, ve
    SIGTERM artık normal kapanış olduğu için bu yalnız gerçek bir çöküşte olur;
  - var olan sohbetin yeni mesajı: içerikte duruyor, yalnız `lastActivity` eski;
  - bir silme: içerik çöpe taşındı ama kaydın düşmesi yazılmadı. Kayıt yeniden açılınca listede durur,
    okununca "yok" der, ve silinince temiz silinir — taşıma "zaten yok"u başarı sayar, kayıt yine
    düşer.

### 4 · Disk işlemleri en aza — `services/store/store.py`

- **`write_text` ve `move` klasörü yalnız yoksa yaratır:** önce doğrudan yazar; klasör yoksa
  (`FileNotFoundError`) yaratır ve bir kez daha dener. Bugün her yazma `os.makedirs` çağırıyor — klasör
  dururken de, Drive'da üç sistem çağrısı. Sözleşme aynı (eksik klasör yine yaratılır), çağıranlar
  değişmez.
- **Kalkanlar:** `exists`, `mtime`, `remove` — artık hiçbir şey çağırmıyor.

### 5 · Silmek

**Proje:** klasör bütün olarak `trash/<id>`'ye taşınır, bugünkü gibi; ardından kaydı **o klasöre
`project.json` olarak yazılır**, sonra `projects.json`'dan düşer. Neden: `projects.json`'dan düşen
kayıt projenin adını, doğuşunu, pinini götürürdü — FOUNDATION'ın 1. ilkesi (*"No scenario may lose
work the user already did"*) silinen projenin de bütün durmasını istiyor, ve çöp bugün de adıyla
duruyor. Seyrek bir işlemde bir yazma.

**İçerik zaten yoksa silme yine başarılıdır:** taşıma `FileNotFoundError` verirse — projeye hiç
yazılmamış, ya da bir çöküş önceki silmenin kayıt düşürmesini götürmüş — taşınacak bir şey yoktur;
kayıt yine düşer, ve projenin kaydı yine çöpe yazılır. Yoksa kayıt hiçbir şeyin silemeyeceği bir şeyi
gösterirdi. **Dosya** da aynı: içeriği yoksa kayıt düşer, silme başarılı döner.

### 6 · Kurallar — FOUNDATION ve CODE-STANDARD

- **FOUNDATION, 2. ilke** (*"Truth lives on disk"*) metadata için gevşer, yazılı olarak: sunucu
  `projects.json`'ın tek yazıcısıdır, onu bellekte tutar ve değişikliği bir an sonra diske yazar;
  gerçek bir çöküş son değişiklikleri götürebilir (kullanıcının 9 Ekim kararı), bir durdurma
  götürmez; bir köke bir sunucu; ve elle düzenlemeler — aşağıda, *Sınırlar*.
- **CODE-STANDARD, depolama tablosu** yeniden yazılır: `projects.json` satırı, `project.json`,
  `pinned`, `archived` satırları gider; çöpler eklenir. "Hiçbir dosya ötekinin cevabını tekrarlamaz"
  kuralı *(Madde 346)* gevşer: `projects.json` bir listenin istediğini — sohbetin başlığı ve
  anları, dosyanın anı — bilerek tekrarlar, aynı anda ve aynı yazıcıyla; sayılar ve son kullanım hâlâ
  yazılmaz.

## Her işlemin bedeli

N proje sayısı, C bir projenin sohbet sayısı, F dosya sayısı. Sayılar `tmp/m447/measure.py`'den,
ölçülmüş — 446'nın tohumuyla aynı kök (30 projede 267 sohbet, 192 dosya; 100 projede 972 sohbet, 541
dosya), Store'un yaptığı her `os` çağrısı sayılarak, yazıcının yazması da isteğin hanesinde
(`flush`). Ölçülen proje 15 sohbetli ve 1 dosyalı.

| İşlem | Bugün N=30 | Bugün N=100 | Bugün | 447 N=30 | 447 N=100 | 447 |
|---|---|---|---|---|---|---|
| Açılış | 0 | 0 | O(1) | 1 | 1 | O(1) işlem, O(N+ΣC+ΣF) bayt |
| Proje listesi (`GET /api/projects`) | 454 | 1589 | O(N+ΣC) | 0 | 0 | O(1) — bellek |
| Archive basışı (PATCH + liste) | 1366 | 4771 | O(N+ΣC) | 2 | 2 | O(1) |
| Unarchive / Pin / Rename (PATCH) | 909–911 | 3179–3181 | O(N+ΣC) | 2 | 2 | O(1) |
| Proje açmak (sohbetler + dosyalar + bir sohbet) | 35 | 35 | O(C+F) | 1 | 1 | O(1) |
| Bir dosyayı açmak | 3 | 3 | O(1) | 1 | 1 | O(1) |
| Yeni proje | 4 | 4 | O(1) | 2 | 2 | O(1) |
| Proje silmek | 4 | 4 | O(1) | 6 | 6 | O(1) |

- 447'nin PATCH'lerindeki 2 işlem yazıcının: `projects.json.writing`'i açıp yazmak ve yerine koymak.
  İsteğin kendisi diske hiç gitmiyor; arka arkaya basışlar tek yazmada toplanabilir. Hiçbir şeyi
  değiştirmeyen bir PATCH 0.
- Proje açmak 447'de yalnız açılan sohbetin içeriğini okur (1); listeler bellekten. Bugün sohbet
  listesi projenin bütün sohbet dosyalarını açıyordu (bu projede 15).
- Proje silmek: çöpün listesi, taşıma, kaydın çöpe yazılması (2), `projects.json` (2) — 6. Bugün 4:
  çöpe kayıt yazılmıyordu, çünkü `project.json` klasörle gidiyordu. Çöp klasörü hiç yoksa (ilk
  silme) taşıma bir kez düşer, klasör yaratılır ve yeniden dener: +2.
- Yeni proje: yalnız `projects.json` (2); klasörü ilk yazma yaratır. Bugün `exists`, `makedirs` ve
  yazma (4).

**Bir tur:** sohbet okumak 2 → 1 (`exists` + okuma → okuma), sohbet yazmak 3 → 2 (`makedirs` gider),
agent'ın her turdaki dosya adları 1 → 0, kutudaki her açık dosya 2 → 1, agent'ın yazdığı dosya 3 → 2.
**Eklenen:** her sohbet ve dosya yazmasının ardından bir `projects.json` yazması (2 işlem, arka
planda). Bir mesaj gönderip cevap almak böylece en az iki `projects.json` yazması demek — kullanıcının
mesajı ve cevap arasında model düşündüğü için ikisi genelde birleşmez.

**Bayt:** `projects.json` her yazmada bütün olarak yazılır: bu tohumla 30 projede 70 KB, 100 projede
245 KB. Yazma bayt olarak O(N+ΣC+ΣF), işlem olarak O(1).

**20 ms'lik gidiş-dönüşle, 30 projede** (`before.txt` / `after.txt`'in son bölümü): Archive basışı
bugün 29,6 s; 447'de 0,04 s — o da yazıcının iki işlemi, isteğin kendisi diske gitmiyor. Proje listesi
10,1 s → 0, proje açmak 1,5 s → 0,06 s.

**446'nın betiği:** `tmp/m446/measure.py` eski kodda yeniden koşuldu ve aynı sayıları verdi (30
projede 1366, 100 projede 4771). Yeni kodda olduğu gibi koşamaz — eski düzeni tohumluyor ve artık
olmayan `set_archived`'ı sarıyor —; uyarlaması `tmp/m447/measure.py`: aynı tohum, aynı sayım, düzeni
koddan anlıyor, ve her isteği ölçüyor. Tablodaki iki sütun onun `before.txt`'i ve `after.txt`'i.

## Olmayacak

- **Taşıma yok** *(kullanıcı — "migration yapmıcaz")*: eski projeler — kökteki `<id>/project.json`'lu
  klasörler — okunmaz, yeni sürümde liste boş başlar. Klasörler yerinde kalır, hiçbir şey silinmez.
- API'nin cevapları ve ekran değişmez; `frontend/` ve `dist` değişmez.
- Sohbet ve dosya içeriklerinin şeması değişmez.

## Sınırlar

- **Bir köke bir sunucu.** İki sunucu aynı köke yazarsa son yazan öbürünün değişikliklerini siler.
  Defter ikinciyi başlatmadan önce birinciyi `pkill` ile kapatıyor.
- **Elle düzenleme, Drive'da** — üç ayrı durum:
  - `projects.json`'ı elle değiştirmek sunucu yeniden başlayınca görülür; sunucu açıkken yapılan,
    sunucunun bir sonraki yazmasıyla ezilir.
  - Bir projenin `files/` klasörüne elle bırakılan dosya **hiç görünmez**: projenin neyi tuttuğunu
    yalnız `projects.json` söylüyor. Elle silinen bir dosya ya da sohbet listede kalır, açılınca "yok"
    der, silinince temiz silinir.
  - Bir sohbetin ya da dosyanın **içeriğini** elle değiştirmek hemen görülür: içerik her seferinde kendi
    dosyasından okunuyor.
- **Ekranda görünen tek değişiklik — son kullanım:** bugün en yeni sohbet dosyasının mtime'ı — yani
  sohbetin her yazılması projeyi öne alıyordu. 447'de sohbetlerin en yeni `lastActivity`'si, yani açık
  kolun son mesajının anı. Bu yüzden **Continue here projeyi artık öne almıyor**, ve **sürüm
  değiştirmek projeyi iki yöne de oynatabilir** (daha eski bir kola geçmek son kullanımı geri çeker).
  Konuşmak projeyi öne alır, bugünkü gibi. Kenar çubuğu sohbetleri zaten bu anla diziyordu, artık
  proje listesi de.
- **Dosyanın anı** artık dosyanın mtime'ı değil, sunucunun onu yazdığı an. Drive'da elle değiştirilen
  bir dosyanın anı değişmez.
- `projects.json` büyüdükçe her yazma büyür (yukarıda, bayt); 100 projede bile Drive için küçük.
- Gerçek bir çöküşte kaybolanlar — *Yazıcı*'da.

## Değişen dosyalar

- `queen-agent/backend/services/store/store.py` — klasör yalnız yoksa; `exists`, `mtime`, `remove`
  gider.
- `…/features/workspace/data/queued_write.py` — yeni.
- `…/data/file_project_store.py` — yeniden yazılır.
- `…/data/file_chat_store.py`, `…/data/file_file_store.py` — `FileProjectStore`'u alır; listeler ve
  varlık bellekten, yazma kaydı koyar.
- `…/domain/ports.py` — `ProjectStore.update`; `ChatStore.list_for` özet döner.
- `…/domain/chat.py` — `ChatSummary`. `…/domain/project.py` — yorumlar.
- `…/domain/usecases/edit_project.py` — değişiklik fonksiyonu, `now`.
- `…/presentation/routes.py` — `edit_project`'e `now`.
- `queen-agent/main.py` — bağlama; okunamayan `projects.json`'da açık mesajla durmak; SIGTERM normal
  kapanış.
- `queen-agent/FOUNDATION.md`, `queen-agent/CODE-STANDARD.md`.
- Testler: `test_store.py`, `test_queued_write.py` (yeni), `test_composition.py`,
  `test_file_project_store.py`,
  `test_edit_project.py`, `test_pin_archive.py`, `test_last_activity.py`, `test_delete_project.py`,
  `test_projects_api.py`, `test_file_chat_store.py`, `test_append_message.py`, `test_chats_api.py`,
  `test_stream_answer.py`, `test_files_api.py`, `test_read_file.py`, `test_delete.py`,
  `test_tools.py`.

## Testler

**Store:** var olan klasöre yazmak `makedirs` çağırmaz; olmayan klasör yine yaratılır; taşıma da öyle;
olmayan bir şeyi taşımak yine hata verir.

**Yazıcı (`test_queued_write.py`):** `changed()` beklemeden döner ve `flush()`'tan sonra dosyada son
durum var; yazma sürerken gelen değişiklikler tek bir sonraki yazmada toplanır (en son hâl); üzerine
kurulduğu durum ve aynı metin yeniden yazılmaz; başarısız yazma beklenip yeniden denenir, her deneme
hatanın sözüyle loglanır; yeniden deneme en son durumu yazar; denemeler sınırlı, sonraki değişiklik
yeniden başlar; başlatılamayan iş parçacığı `flush()`'ı kilitlemez; yazıcı daemon değil ve boşalınca
biter. **Bileşim (`test_composition.py`):** `main.py` SIGTERM'i yakalıyor.

**Depo (`test_file_project_store.py`):** dosya yoksa boş, bir şey yazılmaz; okunamayan dosya
`ProjectsUnreadable`, dosya olduğu gibi kalır; kurulduktan sonra `get`, `list_all`, `chats`, `files`
diske gitmez (sayan bir Store ile); `projects.json`'ın şekli — yalnız gereken alanlar, sayılar ve
son kullanım yazılmaz; `flush` + yeni örnek (yeniden başlatma) her şeyi geri getirir; sayılar ve son
kullanım dizilerden; `put_chat` aynı id'yi yeniler, yenisini ekler; olmayan projeye `put` hiçbir şey
yapmaz; `drop_file`; `update` olmayan projede `None`; aynı id `ProjectIdTaken`, aynı anda sekiz
`add`'den yalnız biri geçer; yeni proje klasör yaratmaz; silmek klasörü taşır, kaydı çöpe yazar ve
listeden düşürür; klasörü olmayan (hiç yazılmamış ya da zaten çöpte) proje de silinir.

**Kullanım durumları:** `edit_project` değişikliği — sabitlemek `now`, ikinci sabitleme anı
kaydırmaz, arşive girmek ve çıkmak pini siler, olmayan arşivi geri istemek pine dokunmaz.

**Sohbet ve dosya depoları:** yazınca kayıt gelir, içerik kayıttan önce yazılır; kaydı olmayan sohbet
ya da dosya diske gitmeden `None`; kaydı olup içeriği olmayan sohbet ya da dosya `None` (404);
içeriği zaten gitmiş dosya silinir ve kaydı düşer; liste bellekten; silinen dosyanın kaydı düşer.

**API:** var olan testler bugünkü cevapları tutuyor ve değişmeden geçer; yalnız kurulumları yeni
bağlamayı kullanır ve bir kökü ikinci kez açmadan önce `flush` eder.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite sırayla yeşil; `frontend/` ve `dist` değişmemiş.
- `tmp/m447/measure.py` önce (`before.txt`) ve sonra (`after.txt`) koşulmuş, sayılar yukarıdaki
  tabloda: 100 projede liste 0, Archive / Pin / Rename isteğin kendisinde 0 ve yazıcıda 2, ve sayılar
  proje sayısıyla büyümüyor.
- Sunucu yeniden başlayınca projeler, pinler, arşivler, sohbet ve dosya listeleri yerinde.
- Okunamayan `projects.json`'la sunucu açık bir mesajla duruyor, dosya değişmiyor.
