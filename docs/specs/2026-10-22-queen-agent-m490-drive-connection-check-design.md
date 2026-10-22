# Madde 490 · Drive bağlantı kontrolü — tasarım

**Tarih:** 22 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-20-queen-agent-v11-roadmap.md),
490 · v11-1 · **Dal:** `feat/queenagent-v11` · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Kullanıcı, 20 Ekim — *"şuanlık collabmounte çöküp çkmediğini kontrunul uyaoalım çökmüşse hata
gösterelim durdurum bu yeter"*; 448'in taşıma kodu için — *"sil"*. Madde `ALIGNED`, ve yalnız beş şey:

1. **Bağlantı kontrolü** — `Store` her işlemden önce kökü bir kez stat eder ve aygıt kimliğini ilk
   kontrolde kaydettiğiyle karşılaştırır.
2. **Kök açılmaz** — `Store` kökü hiçbir zaman açmaz.
3. **Ekranda gerçek hata** — `web/app.py`'de tek bir `OSError` işleyicisi: `503 {"error": str(exc)}`.
4. **Açılış** — kontrol açılışta tutmazsa sunucu açılmaz ve gerçek cümleyi yazar.
5. **448'in taşıma kodu silinir** — `old_projects.py`, `take_in`, `Store.mtime`, `main.py`'deki satır,
   ve notebook'ta yalnız 448 için duran.

Sebep roadmap'te, *v11-1*'in başlığında: **A** — açılışta `projects.json`'a yanlışlıkla "bulunamadı"
denince 448'in taşıması onu yalnız eski projelerle yeniden yazıyordu; **B** — Drive oturum ortasında
koparsa `_into_folder` bütün klasör zincirini Colab'ın kendi diskinde yeniden açıyor, yazma oraya
düşüyor ve ekran başarılı diyor.

Queen Editor'ün 472'si aynı kontrolü kendi `Storage`'ına kurdu; yaklaşım oradan okundu, kod ya da test
paylaşılmaz — iki araç ayrı proje.

## Bugün — koddan okunanlar

- **`services/store/store.py` · `Store`** — beş açık yöntem: `read_text`, `write_text`, `list_dir`,
  `mtime`, `move`. Kurucu kökü yalnız saklar. Hiçbiri kökü yoklamıyor. `write_text` ve `move`
  `_into_folder`'dan geçiyor: işlem `FileNotFoundError` alınca `os.makedirs(dirname)` ile **bütün
  zinciri, kök dahil** açıp bir kez daha deniyor. `test_store.py`'nin
  `test_root_is_created_on_first_write_not_on_construction`'ı bunu bugünkü davranış olarak tutuyor.
- **Çağıranlar** — `FileProjectStore` (`projects.json`'u açılışta bir kez okur; `FileNotFoundError`'ı
  "hiç proje yok" sayar), `QueuedWrite` (her hatayı log'a yazar, üç kez dener), `FileChatStore.get` ve
  `FileFileStore._text` (`FileNotFoundError` → bulunamadı), iki `delete` (`move`'un
  `FileNotFoundError`'ı → zaten taşınmış). Hepsi `except FileNotFoundError` diyor: kopmuş bağlantı
  `FileNotFoundError` olarak gelirse "yok"a dönüşür.
- **`web/app.py`** — hata işleyicisi yok. Route'lar hiçbir `OSError` yakalamıyor: bir disk hatası
  Flask'ın HTML 500 sayfası olur, ekran `failure.js`'in kuralıyla *"HTTP 500: <!doctype html>…"* der.
- **Ekran** — `failure.js` cevabın `body.error`'unu okuyor; 503 için özel bir yol yok (tarandı).
  `useProjects`, `useChat` bu cümleyi gösteriyor. **Ekran ve `dist` değişmez.**
- **Süren tur** — `run_turn`'ün döngüsündeki her `Exception` `EngineFailed` olur; döngüden sonraki
  cevap yazması (`append_message`) da `LiveTurns._run`'ın `except Exception`'ına düşer; ikisi de turu
  `error` ile bitirir ve `events`'in son karesi `{"turn": null, "error": "<cümle>"}` olur. Kod
  değişmez; yeni hata bu yoldan gelir.
- **`main.py`** — `Store(config.ROOT)`; `FileProjectStore(store)` `ProjectsUnreadable`'da
  `SystemExit` ile açılışı durduruyor; sonra `move_old_projects(store, projects)`.
- **448** — `data/old_projects.py` (tamamı), `FileProjectStore.take_in`, `Store.mtime`, `main.py`'nin
  import'u ve satırı; testler: `test_old_projects.py` (tamamı), `test_store.py`'nin `mtime` testi,
  `test_composition.py`'nin `test_old_projects_are_moved_at_start`'ı.
- **Notebook, Serve hücresi** — 448 bekleme sınırını 90 saniyeden (45 × 2 sn) `START_CAP = 600`'e
  çıkardı, yorumu 448'i adlıyor, ve uzun bekleme için yarım dakikada bir *"⏳ Sunucu hâlâ açılıyor"*
  satırı ekledi. Aynı commit sunucunun düştüğünü beklemeden görmeyi de ekledi (`server.poll()`).

## Ne değişir

### 1. `Store` — bağlantı kontrolü

`store.py`'de yeni bir hata: **`RootUnreachable(OSError)`**.

- **`OSError`**, ki tek işleyici (3) onu da yakalasın ve `QueuedWrite`, `LiveTurns` onu bugünkü gibi
  log'a ve turun hatasına yazsın.
- **`FileNotFoundError` değil**, bilerek: çağıranların `except FileNotFoundError`'u kopmuş bağlantıyı
  "bulunamadı"ya, `FileProjectStore` "hiç proje yok"a çevirmesin. Kök yokken stat'ın kendisi
  `FileNotFoundError` verse de dışarıya `RootUnreachable` olarak çıkar.

Her açık yöntem, yolun kök sınırından (`_full`) geçtikten sonra ve diske dokunmadan önce, **bir kez**
`_reached()`'i çağırır — `move` iki yol alsa da bir kez:

1. `os.stat(kök)`. Hata — Errno 107, `FileNotFoundError`, EIO, ne olursa — →
   `RootUnreachable("The root cannot be reached: <OS'un cümlesi>")`, OS'un hatası sebep
   olarak zincirlenir. OS'un cümlesi kökün yolunu zaten taşıyor.
2. `st_dev` **ilk başarılı kontrolde** kaydedilir — kurulumda değil: kurucu bugünkü gibi diske
   dokunmaz. Uygulamada ilk kontrol açılıştaki `projects.json` okuması. Sonraki her kontrolde farklıysa
   → `RootUnreachable("The root is on another device than when it was first reached: <kök>
   (device <eski>, now <yeni>)")`. Bağlantı kopup yerinde Colab'ın kendi diskinde bir klasör açılmışsa
   stat başarılı olur; onu ayırt eden aygıt kimliği. Yeniden bağlanma yok.

İki istek aynı anda ilk kontrolü yaparsa ikisi de aynı stat'ın aygıtını yazar; kilit gerekmez.

### 2. `Store` — kök açılmaz

`_into_folder` `Store`'un yöntemi olur ve `os.makedirs` gider:

- İşlem `FileNotFoundError` alınca ve hedefin klasörü **kökün kendisi** ise hata olduğu gibi yükselir —
  kök kontrolden hemen sonra gitmiş demektir, ve açılmaz.
- Değilse klasörler **kökün altından hedefin klasörüne doğru, birer birer `os.mkdir` ile** açılır;
  var olan (`FileExistsError`) geçilir. Kök yoksa ilk `mkdir` `FileNotFoundError` verir: kök hiçbir
  yoldan açılmaz — kontrol ile yazma arasında kopan bir bağlantıda da. Sonra işlem bir kez daha denenir.
- Proje klasörü, `chats/`, `files/`, `trash/` ve `trash/<id>/` bugünkü gibi ilk yazmada ya da taşımada
  açılır (447). Klasör zaten oradaysa bu yol hiç yürümez.

### 3. `web/app.py` — tek işleyici

`create_app` `@app.errorhandler(OSError)` kaydeder: `503`, `{"error": str(exc)}`, ve sunucunun
log'una isteğin yöntemi, yolu ve cümle bir satır olarak. Log satırı şu yüzden: işleyici Flask'ın
kendi traceback log'unu da susturur, ve sebebi sonradan aramak log'dan başlar (roadmap,
*"Sebebi bulmak için açık kalanlar"*). Cümlede gizli bir şey yok: dosya yolları ve OS'un sözü;
anahtar hiçbir dosya yolunda geçmiyor.

`PathOutsideRoot` bir `OSError` değil ve değişmiyor: kökten kaçan bir yol bizim kodumuzun hatası, 500
kalır.

### 4. `main.py` — açılış

`FileProjectStore(store)`'u saran `except` `ProjectsUnreadable`'ın yanına `OSError`'ı da alır:
`SystemExit("QueenAgent did not start. In <kök>: <cümle>. Nothing was written to it.")`. Açılışta
diske dokunan tek şey bu okuma, ve onun ilk işi bağlantı kontrolü; kök yoksa ya da bağlantı kopuksa
sunucu kalkmaz, notebook'un Serve hücresi sunucunun düştüğünü görüp son log satırlarını — bu cümleyi —
basar. Boş bir proje listesi hiçbir zaman çizilmez. `RootUnreachable` adıyla değil `OSError` olarak
yakalanır: açılıştaki başka bir disk hatası da (EIO) traceback yerine aynı cümleyle durur, ve
`main.py`'nin store'un hatasını bilmesi gerekmez.

### 5. 448'in silinmesi

- `features/workspace/data/old_projects.py` ve `tests/test_old_projects.py` silinir.
- `FileProjectStore.take_in` silinir.
- `Store.mtime` ve testi silinir.
- `main.py`: import ve `move_old_projects(store, projects)` satırı; `test_composition.py`:
  `test_old_projects_are_moved_at_start`.
- **Notebook, Serve hücresi:** `START_CAP = 600` → `90` (448'den önceki sınır), 448'i adlayan yorum
  gider, yarım dakikalık *"⏳"* satırı ve sayacı gider — üçü de uzun açılış içindi. **`server.poll()`
  kalır:** 448'le geldi ama yalnız onun için değil; bundan sonra kökü bulamayan sunucunun cümlesi
  ekrana onunla, beklemeden gelir. Yorumu ve testinin docstring'i bunu söyler.

Eski dosyalar — `project.json`, `pinned`, `archived` — Drive'da dokunulmadan kalır; backlog'da
silinmeyi bekliyorlar.

### 6. Belgeler

- **CODE-STANDARD**, *Services*, `store/` satırı: her işlemden önce kökü yoklar, kökü hiç açmaz.
- **README**, *Run it*: kök önceden var olmalı; uygulama açmaz.

## Maliyet

Koddan sayıldı, ölçülmedi. Her satır bir dosya sistemi çağrısı = Colab'da Drive'a bir gidiş dönüş.
Hepsi proje, sohbet ve dosya sayısından bağımsız, O(1). Listeler bugünkü gibi bellekten, sıfır.

| İşlem | Bugün | Sonra |
|---|---|---|
| Her `Store` işlemi | — | +1 (kök stat) |
| `read_text` | `open` = 1 | stat + `open` = 2 |
| `write_text`, klasör varken | `open` + `replace` = 2 | stat + 2 = 3 |
| `write_text`, klasör yokken | 1 + `makedirs` (seviye başına ~2) + 2 | stat + 1 + `mkdir` seviye başına 1 + 2 |
| `list_dir` | `listdir` = 1 | 2 |
| `move` | `replace` = 1 | 2 |
| Açılış | `projects.json` + 448'in kök listesi (+ yeni bir eski proje başına ~20) | stat + `projects.json` = 2 |
| Bir mesaj (soru + cevap yazması) | 4 | 6 |
| Proje silmek | `list_dir` + `move` + `write_text` = 4 | 7 |
| Dosya silmek | 2 | 4 |
| Proje listesi, sohbet listesi, dosya paneli | 0 | 0 |

`QueuedWrite`'ın `projects.json` yazması bir `write_text`: +1. Kontrolün bedeli işlem başına bir
çağrı; yavaş gelirse 472'nin roadmap'indeki yol açık: kontrol yalnız yazmalarda.

## Ne kaybolabilir, ne bozulabilir

- **Bağlantı oturum ortasında koparsa** — sonraki işlemin stat'ı düşer ya da aygıt farklı çıkar; işlem
  diske dokunmadan durur, ekran OS'un cümlesini 503 ile gösterir. Hiçbir yazma kökü açmadığı için
  Colab'ın diskine bir şey yazılmaz.
- **Kontrol ile yazma arasında kopan bağlantı** — yazma kendisi `FileNotFoundError` alır, klasör açma
  kökü açmadan düşer, hata 503 olur. Hiçbir şey yazılmaz.
- **Süren tur** — cevabın yazması düşer; tur `events`'in son karesinde cümleyle biter, soru diskte
  kalır, sohbet "unanswered" okunur ve Try again onu yine sorar (461).
- **Bellekte kalan proje değişiklikleri** — bir istek yalnız `projects.json`'u değiştiriyorsa (ad,
  iğne, arşiv, yeni proje) istek bellekte başarılı olur; kuyruğun yazması kontrole takılır ve yalnız
  log'a yazılır (447'nin kuyruğu, roadmap: *olduğu gibi kalan*). Sonraki bir disk işlemi hatayı
  ekranda gösterir.
- **Proje listesi** — bağlantı koptuktan sonra da bellekteki listeyi gösterir: diske gitmiyor. Boş bir
  liste gösterilmez.
- **İki istek aynı anda yeni bir projeye yazarsa** — ikisi de aynı klasörü açmaya çalışır; ikincinin
  `FileExistsError`'ı geçilir.
- **Bilgisayardaki ilk açılış** — `python main.py` varsayılan kökte (`~/QueenAgent`) klasör yoksa
  artık açılmaz ve kökü yolunu söyler; klasör elle açılır (README). Kullanıcının bilgisayarında kök
  zaten var.
- **Bu maddenin değil, açık kalan** — kök stat'ı başarılıyken `projects.json`'a yanlışlıkla
  "bulunamadı" denirse (colabtools #5970) `_loaded` hâlâ boş başlar; 448'in yeniden yazması gittiği
  için ilk değişikliğe kadar diske bir şey yazılmaz, ama ilk yeni proje `projects.json`'u yalnız onunla
  yazar. Notebook kökün gerçekten Drive'da olduğuna bakmıyor, sağlık kontrolü kökü yoklamıyor. Hepsi
  backlog'daki büyük tasarımın.

## Bu maddenin kararları

Maddenin bırakıp spec'in verdiği kararlar:

1. **`RootUnreachable(OSError)`**, `store.py`'de, kontrolün iki hatası için tek tür.
2. **Aygıt kimliği ilk başarılı kontrolde** kaydedilir; kurucu diske dokunmaz.
3. **İşlem başına bir kontrol**, yol sınırından sonra; `move` da bir kez.
4. **Kökün altındaki klasörler birer birer `os.mkdir`** ile, yukarıdan aşağı, yalnız eksik çıktıklarında;
   hedefin klasörü kökse hata olduğu gibi yükselir.
5. **İşleyici bir log satırı da yazar**; `PathOutsideRoot` 500 kalır.
6. **`main.py` `OSError`'ı yakalar**, `RootUnreachable`'ı adıyla değil.
7. **Notebook:** `START_CAP` 90'a döner, *"⏳"* satırı gider, `server.poll()` kalır.

## Sınırlar

- Yalnız bu beş şey. 447'nin kuyruğu, `list_dir`'in olmayan klasörü boş sayması, silmede
  "bulunamadı"nın yok sayılması, sağlık kontrolü ve notebook'un CONFIG hücresi değişmez.
- Frontend ve `dist` değişmez.
- queen-editor'e dokunulmaz; iki aracı bağlayan test yok.

## Bitti sayılır

1. Testler gösteriyor ki:
   - kökün stat'ı Errno 107 verince `Store`'un **her** açık yöntemi `RootUnreachable` ile duruyor,
     hata `FileNotFoundError` değil, cümlesi OS'unki, ve bir şey yazılmıyor; sonradan eklenen bir
     yöntem listeye girmeden test geçmiyor;
   - kök yokken her işlem `RootUnreachable` veriyor ve kök açılmıyor;
   - aygıt kimliği değişince işlem `RootUnreachable` ile duruyor ve iki kimliği söylüyor;
   - kurulum diske dokunmuyor; her işlem kökü bir kez stat ediyor;
   - kök kontrolden sonra giderse yazma ve taşıma kökü açmıyor; kökün içindeki eksik klasörler yine
     açılıyor, var olanlara klasör açılmıyor;
   - bir `OSError` 503 ve `{"error": "<cümle>"}` dönüyor; kök gidince bir mesaj 503 ve cümleyle
     reddediliyor, kök açılmıyor; süren bir tur cümleyle bitiyor;
   - `python main.py` olmayan bir kökle açılmıyor, cümleyi yazıyor ve kökü açmıyor;
   - 448'in kodu yok; notebook'un sınırı 90 saniye ve sunucunun düştüğünü görüyor.
2. Var olan projeler değişiklikten sonra aynı listeleniyor: `projects.json`'un şeması ve okunuşu
   değişmedi, `test_file_project_store.py` ve API testleri yeşil.
3. İki satır yeşil: `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend`.
4. **Colab denemesi — kullanıcının, roadmap bitince:** uygulama açıkken yeni bir hücrede
   `from google.colab import drive; drive.flush_and_unmount()`; sonra bir mesaj göndermek ya da bir
   proje silmek ekranda *"The root cannot be reached: …"* gösteriyor, süren bir tur aynı
   cümleyle duruyor, `/content/drive/MyDrive/<DRIVE_FOLDER>` Colab'ın diskinde açılmamış. Serve hücresi
   Drive bağlı değilken yeniden çalışınca sunucu açılmıyor ve cümleyi basıyor.
