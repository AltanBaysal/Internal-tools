# Madde 506 · Projeleri toplu arşivle/sil — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v12 yol haritası](../roadmaps/2026-10-24-queen-agent-v12-roadmap.md#v12-4),
506 · v12-4 · **Dal:** `feat/queenagent-v12` · **Kurallar:** [FOUNDATION](../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Bugün her proje kendi ⋯ menüsünden tek tek arşivleniyor ya da siliniyor; ekranda çoklu seçim yok.
Kullanıcının kararları *(27 Ekim)*: Projects'te arşivleme ve silme, Archived'da arşivden çıkarma ve
silme; kutucuk *"⋯ menüsü gibi"* fare satırın üstüne gelince görünür, *"biri seçilince kutucuklar açık
kalsın diğerindede"*; onay *"Yalnız silmede"*; hepsini seç yok, *"shift iler gurplı seçlebilsin"*,
*"yada ctrl ile tek tek"*, *"windwo doyas kullanım ıgibi"*; tek tıklama projeyi açmaya devam eder.

**Kabul:**
- Projects'te seçilenler tek işlemle arşivleniyor ya da siliniyor; Archived'da arşivden çıkıyor ya da
  siliniyor.
- Kutucuk satırın üstüne gelince görünüyor; bir proje seçilince bütün satırlarda açık kalıyor.
- Kutucuğa tıklamak ya da satıra Ctrl ile tıklamak seçimi değiştiriyor; Shift ile tıklamak son
  seçilenle tıklanan arasındakilerin hepsini seçiyor; düz tıklama projeyi açıyor.
- Toplu silme soruyor: *"Delete 3 projects? The 12 chats and 40 files in them are deleted with them.
  This can't be undone."*; toplu arşivleme ve arşivden çıkarma sormuyor.
- Sekme değişince seçim temizleniyor.

## Bugün

- `AllProjectsScreen` sekmeleri, aramayı ve satırları çiziyor; Projects'te `Pinned` ve `Recent`
  bölümleri, Archived'da tek liste. Sıra sunucunun (`list_projects`): önce sabitliler, sonra son
  kullanılanlar. `found` (aranmış, sekmeye göre süzülmüş liste) çizilen sırayla aynı.
- Tek Archive: `asked` haritası satırı anında taşıyor (Madde 446), `editProject` bir `PATCH` atıyor ve
  sırasının içinde listeyi `GET` ile yeniden okuyor. Yani tek proje = 2 istek.
- Tek Delete: `App.askToDelete` `ConfirmDialog`'u açıyor; sayılar zaten elde olan listeden
  (`project.chats`, `project.files`); onaylanınca bir `DELETE`, liste elle süzülüyor.
- Sunucu: `projects.json` bellekte (Madde 447). Arşiv bir bellek değişikliği; diske kuyruktaki tek
  yazıcı yazıyor ve arka arkaya gelen değişiklikleri tek yazıda topluyor. Silme ise proje başına:
  çöpü listele, klasörü taşı, kaydı çöpe yaz, satırı sil.

## Sunucu

### İki kapı

| Kapı | Gövde | Cevap |
|---|---|---|
| `PATCH /api/projects` | `{"ids": [...], "archived": true\|false}` | `200`, liste (`GET /api/projects` ile aynı biçim) |
| `POST /api/projects/delete` | `{"ids": [...]}` | `200`, liste |

- **Cevap liste**, bellekten. Tarayıcı ikinci bir `GET` atmıyor: bir toplu işlem tek gidiş-dönüş.
- `PATCH` tek projenin `PATCH`'iyle aynı alanı çoğa uyguluyor. Silme `POST`: kimlikler gövdede gidiyor;
  `DELETE`'in gövdesini bir ara katmanın taşıyacağı belli değil ve `deleteJson` gövde göndermiyor.
- `ids` boş olmayan bir dizgi listesi değilse (ya da gövde nesne değilse) `400`
  `"ids must be a list of project ids"`; `archived` `true`/`false` değilse `400`
  `"archived must be true or false"`.
- **Bilinmeyen kimlik atlanıyor.** İstenen zaten olmuş ya da olamaz; cevaptaki liste doğruyu söylüyor.
  İki sekmeden aynı toplu silme gelirse ikisi de başarılı.
- **Çalışan sohbet:** toplu silmede projelerden birinin sohbetinde tur dönüyorsa istek bütünüyle `409`
  `"a chat in one of these projects is still answering -- try again once it has finished"` ve hiçbir
  şey taşınmıyor (hepsi ya da hiçbiri). Arşivde bugün böyle bir kural yok (arşivdeki proje Madde 443'ten
  beri her proje gibi kullanılıyor); toplu arşive de eklenmedi.
- Kimlik yalnız bellekteki listede aranıyor; diske yalnız listenin taşıdığı bir kimlik ulaşıyor.

### Kullanım durumları

- `archive_projects(store, ids, archived, now)` (`edit_project.py`): her kimlik için `edit_project` —
  tek basışın kuralı (arşiv sabitlemeyi götürür, Madde 384); `ProjectNotFound` atlanıyor.
- `delete_projects(store, turns, ids)` (`delete_project.py`): önce bütün kimliklerin turuna bakıyor,
  biri dönüyorsa `ProjectAnswering`; sonra `store.delete_many(ids)`.
- `delete_project` (tek) artık `delete_many([id])` çağırıyor; davranışı ve testleri aynı.

### Depo: `delete` yerine `delete_many` *(ana ajanın onayıyla, 27 Ekim)*

Port'un `delete(id)`'si `delete_many(ids) -> {id: çöpteki ad}` oldu. `FileProjectStore.delete_many`:

1. Kimlikleri tekilleştirir, listede olmayanları atar, kayıtları kilit altında okur.
2. Çöpü **bir kez** listeler. Her proje için `unique_name` o listeyle ve bu çağrının aldığı adlarla
   hesaplanır, aynı çağrıdaki iki proje aynı yere düşmez.
3. Her proje: klasörü taşı (klasör yoksa geç), kaydı çöpe yaz.
4. Çöpe kaydı yazılmış bütün satırları döngüden sonra **tek** `_change` ile listeden siler — bir
   `finally` içinde: disk yarıda düşerse çöpe gidenler listeden çıkar, gitmeyenler listede kalır,
   diskte de durdukları gibi. Neden tek: yazıcı iki taşıma arasında işini bitiriyor; satır başına
   bir değişiklik `projects.json`'ı 20 projede 20 kez yazdı, tek değişiklik bir kez (reviewer ölçtü).
   Bedeli: taşınmış bir proje döngü bitene kadar — yaklaşık 2N gidiş-dönüş — `GET /api/projects`'te
   görünmeye devam ediyor.

Neden: bir döngüde eski `delete` çağrılsaydı çöp her proje için yeniden listelenirdi — bir istekte aynı
şeyi N kez okumak.

## Maliyet

N = seçilen proje sayısı.

| İşlem | Tarayıcı → sunucu | Disk (her biri Drive'da bir gidiş-dönüş, önünde kökün stat'ı) |
|---|---|---|
| Toplu arşiv / arşivden çıkarma | 1 istek, 0 ayrı liste okuması | `projects.json` en çok 2 kez yazılır (kuyruktaki yazıcı N değişikliği toplar: ilk değişiklik yazıcıyı başlatır, o yazarken gelenler ikinci yazıda gider) |
| Toplu silme | 1 istek, 0 ayrı liste okuması | 1 çöp listesi + N taşıma + N kayıt yazımı + `projects.json` en çok 2 yazım |
| Silme sorusu | 0 istek | 0 — sayılar elde olan listeden toplanır |

Eskiden N proje = N `PATCH` + N `GET` (446'nın bulduğu sorun) olurdu; şimdi 1 istek. Silmenin N taşıması
ve N kaydı kaçınılmaz: her klasör kendi yerine gidiyor, her kaydı yanına yazılıyor.

## Tarayıcı

### Seçim (`AllProjectsScreen`)

- `picked` bir kimlik kümesi, `anchor` Shift'in saydığı proje. İkisi de ekranın kendi durumu; bir
  işlem basılana kadar sunucuya gitmiyor.
- **Seçilen ve çizilen** (`chosen = found ∩ picked`): çubuğun saydığı ve üzerinde çalıştığı. Aramanın
  gizlediği seçili satır seçili kalıyor, ama sayılmıyor ve işleme girmiyor; arama boşalınca yine seçili
  görünüyor. Arşivlenip sekmeden çıkan satır kendiliğinden düşüyor; arşiv reddedilirse geri gelip yine
  seçili duruyor (yeniden denemeye hazır).
- **Kutucuk / Ctrl (Mac'te Cmd) ile tıklama:** o projeyi seçer ya da bırakır; `anchor` o proje olur
  (Windows gibi, bırakmak da `anchor`'ı taşır).
- **Shift ile tıklama** (satırda ya da kutucukta): seçim, `anchor`'dan tıklanana kadarki aralıkla
  **değiştirilir** — Windows gibi *(kullanıcı: "windwo doyas kullanım ıgibi"; reviewer'ın düzeltmesi)*.
  Aramanın gizlediği seçimler de bırakılır.
- **Ctrl+Shift ile tıklama:** aralık seçime **eklenir**, öncekiler kalır.
- İkisi de `anchor`'ı yerinde bırakır. Aralık **çizildiği sırayla**: `found` çizilen sırada (önce
  `Pinned`, sonra `Recent`), yani aralık **Pinned'dan Recent'e sınırı geçerek** ekrandaki sırayla akar —
  Windows Gezgini'nde grupları aşan seçim gibi. `anchor` çizili değilse (yok, arama gizledi, satır gitti)
  aralık yalnız tıklanan satırdır ve yeni `anchor` o olur.
- Shift'le basışta, satırda da kutucukta da, `mousedown` engelleniyor: yoksa tarayıcı sayfadaki metin
  seçimini oraya uzatır.
- **Düz tıklama** satırı açıyor, seçim dursa da.
- **Sekme değişince** seçim ve `anchor` temizleniyor; açık sekmeye basmak bir şey değiştirmiyor.

### Kutucuk (`ProjectRow`)

Satırın başında `<input type="checkbox" aria-label="Select <ad>">`. CSS: `opacity: 0`; satırın
`:hover`'ında, kendi `:focus-visible`'ında ve satır `is-picking` iken (herhangi bir satır seçiliyken
bütün satırlar) `opacity: 1` — ⋯ gibi. Seçili satır `is-picked`, hafif zeminli. İşareti `--accent`
değil (o yalnız birincil eylemin), satırın kendi gri-kahvesi. `app.css.test.js`'teki
"focus-visible yalnız görünürlük için" sayımı 2'den 3'e çıktı, kutucuk adıyla.

### Çubuk

Seçim varken başlık satırında, `+ New project`'in solunda: `N selected · Archive|Unarchive · Delete`.
Listenin üstünde değil: ilk kutucuk işaretlenince liste aşağı kaymasın, sıradaki kutucuğa uzanan
farenin altından kaçmasın. `Delete` `--destructive` renginde.

- **Archive / Unarchive:** sormuyor. Klavye önce aramaya geçiyor (çubuk satırlarla birlikte gidiyor),
  satırlar `asked` haritasıyla hemen taşınıyor, `onArchiveProjects(ids, archived)` tek istek atıyor.
  Tek basışın `asked` işlemesi ortak bir `asking(ids, …)`'e alındı; tek ⋯ basışı da onu kullanıyor,
  davranışı aynı.
- **Delete:** `onDeleteProjects(ids)` → `App.askToDeleteMany`, `ConfirmDialog` ile:
  - başlık `Delete 3 projects?` / `Delete 1 project?` (`countOf`);
  - gövde `The 12 chats and 40 files in them are deleted with them. This can't be undone.`; tek
    projede `in it are deleted with it`; `countOf` tekil/çoğul;
  - sayılar elde olan listeden toplanıyor (`chats`, `files` her satırda zaten geliyor) — istek yok;
  - Cancel hiçbir şey göndermiyor ve seçim kalıyor; onay tek `POST`.
- Sıra: `ids` çizildiği sırada, seçilme sırasında değil.

### `useProjects`

`archiveProjects(ids, archived)` ve `removeProjects(ids)`: ikisi de kuyrukta (Madde 450), tek istek,
cevaptaki liste `projects` olur. Ret: `writeError` listenin üstündeki satırda, ve liste bir kez `GET`
ile yeniden okunur — ret yarıda gelmiş olabilir (bazı projeler taşındıktan sonra disk düştü), ekran
sunucunun gerçek listesini göstersin. Bedeli bir `GET`, yalnız bir şey düşünce.

## Ne değişmiyor

- Tek projenin ⋯ menüsü, onun Archive/Unarchive/Delete'i ve tek silmenin sorusu.
- Satıra düz tıklama projeyi açıyor; arama Enter'ı ilk satırı açıyor.
- Hepsini seç yok.

## Sınırlar ve açık noktalar

- **Clear yok, Escape seçimi temizlemiyor** — madde istemedi. Seçimden çıkmanın yolu kutucukları
  tek tek bırakmak ya da sekme değiştirmek. Kullanıcının koşu sonu denemesinde bakılacak açık nokta.
- Aynı anda başka bir sekmeden bir silme, bu sekmenin toplu arşivinin arasına düşerse o proje
  atlanır; cevaptaki liste doğruyu gösterir.
- **409 bakışı ile taşıma arasındaki yarış:** toplu silme bütün projelerin turuna bir kez bakıp sonra
  klasörleri tek tek taşıyor (~2N gidiş-dönüş). Bu sırada başka bir sekmeden taşınmış bir projeye mesaj
  gelirse tur projenin eski yerine yazar ve kökte sahipsiz bir klasör açar; listede görünmez, çöpteki
  proje bütün kalır. Tek silmede de var (BACKLOG, 461). Önerilen çözüm BACKLOG'da:
  `LiveTurns.reserve` silinmekte olan projeyi kendi kilidi altında reddeder.
- Bir proje çöpe taşındı ama kaydı yazılamadıysa listede kalır; bir sonraki silme onu "klasör yok"
  yolundan temizler (bugünkü tek silmenin davranışı).
- Fark edilen, dokunulmayan (ikisi de BACKLOG'da): var olan kapılar gövde nesne değilse (`[...]` gibi)
  `payload.get` ile 500 veriyor, yeni kapılar bunu 400'le karşılıyor; tek ⋯ Archive hâlâ `PATCH` +
  `GET`, toplu kapıdan tek istekte gidebilir.

## Testler

- **`test_file_project_store.py`:** eski `delete` testleri `delete_many([id])` ile; yeni: çöp bir kez
  listelenir (`CountingStore`), bilinmeyen ve tekrarlanan kimlik, aynı çağrıda numaralandırma
  (`pa-3`), disk yarıda düşünce yalnız çöpe gidenlerin satırı silinir, olmayan proje diske gitmez.
- **`test_delete_project.py`:** çok projeli silme; birinde tur dönüyorsa hiçbiri silinmez.
- **`test_pin_archive.py`:** toplu arşiv sabitlemeyi götürür, bilinmeyen kimliği atlar; arşivden
  çıkarma.
- **`test_projects_api.py`:** iki kapı listeyle cevaplar; `409`; `ids` ve `archived` için `400`'ler.
- **`AllProjectsScreen.test.jsx`:** kutucuk, `is-picking`, Ctrl/Cmd, düz tıklama, Shift aralığı
  (Pinned→Recent, iki yönde, seçimin yerine, `anchor` yerinde, `anchor` yokken), Ctrl+Shift ekleme,
  satırda ve kutucukta Shift `mousedown`, çubuğun düğmeleri ve yeri,
  sekme temizliği, toplu arşiv (çizilme sırasıyla, anında, klavye aramada), ret, arşivden çıkarma,
  Delete'in teslimi, aramanın gizlediği seçim.
- **`App.test.jsx`:** toplu arşiv tek `PATCH` ve ardından `GET` yok; silme sorusu sayılarla, tekil
  biçim; Cancel; onay tek `POST` ve `GET` yok; ret mesajı, ardından bir `GET`, satırlar yerinde.
- **`workspace.css.test.js`, `app.css.test.js`:** kutucuğun görünürlüğü, Delete'in rengi, üçüncü
  `:focus-visible`.

## Bitti sayılır

- `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend` yeşil (dist testi
  commit'e kadar kırmızı, beklenen).
- `dist` yeniden kuruldu.
- QA ekranda: kutucuk hover'da, seçimle kalıcı; Ctrl/Shift; çubuk; silme sorusu; ağda tek istek.
