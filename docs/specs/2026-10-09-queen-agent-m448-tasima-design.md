# Madde 448 · Eski projelerin taşınması — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
448 · **Dal:** `feat/queenagent-v10`, ana klasörde, commit ana agent'ın · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Öncesi:** [447](2026-10-09-queen-agent-m447-proje-yonetimi-design.md) — `projects.json` ·
**Sonrası:** BACKLOG, *"448'in taşıma kodu ve eski proje dosyaları silinecek"*

## Ne, neden

Kullanıcı, 9 Ekim: *"tek seferlik ilk kez queen agent çalıştığında migrate edecek kod yazalım, startta
bir kere çalışacak, kullandıktan sonra sileceğimiz bir sonraki roadmap'te"*. 447 taşıma yapmıyordu:
kullanıcının Drive'daki projeleri — her biri kendi klasöründe, `project.json`, `pinned`, `archived`
dosyalarıyla — yeni sürümün listesinde görünmüyor.

448 onları açılışta `projects.json`'a ekler, bir kez. Kod geçicidir: kullanıcı taşımanın çalıştığını
görünce bir sonraki roadmap'te silinir, ve silinmesi kolay olsun diye tek bir yerde durur.

## Olacak

### 1 · Ne zaman — her açılışta, yalnız eksik olan

`main.py`, `FileProjectStore`'u kurduktan hemen sonra tek satırla `move_old_projects(store,
projects)`'u çağırır. Kökü **bir kez** listeler; her ad için:

- `projects.json`'da olan bir id → atlanır (bellekte bir sözlük bakışı). v10'da açılmış ya da daha
  önce taşınmış her proje böyle atlanır, ve **olduğu gibi kalır** — aynı id'li eski bir klasör onu
  ezmez.
- `trash` ve `projects.json` (ve onun `.writing`'i) → atlanır, adlarından.
- Geri kalan her ad için klasör bir kez listelenir: içinde `project.json` yoksa — ya da ad bir klasör
  değilse — eski bir proje değildir, atlanır.
- İçinde `project.json` olan klasör **eski bir projedir** ve taşınır.

"`projects.json` yoksa taşı" değil *(yol haritası)*: kullanıcı v10'u aynı kökte denediyse dosya zaten
var, ve eski projeler hiç taşınmazdı. **Yarıda kesilen taşıma** — taşınanlar belleğe girdi ama
`projects.json` yazılmadan sunucu çöktü — bir sonraki açılışta aynı kuralla sürer: kayıtları
olmayanlar yine eksik görünür.

### 2 · Eski projeden ne okunur

Eski düzen, 447'den önceki `file_project_store.py`'nin (`89b5ca77`) okuduğu biçim. Adlarının hepsi
(`project.json`, `pinned`, `archived`, `chats`, `.json`, `files`) `old_projects.py`'de kendi
sabitleri olarak durur, bugünkü depolardan alınmaz: eski düzen Drive'da olduğu gibi donmuş, bugünkü
adlar değişebilir.

- **Ad ve doğuş:** `<id>/project.json`'un `name` ve `createdAt`'i. Başka alanlar (`desc`, `hue`)
  okunmaz.
- **Pin:** `<id>/pinned` varsa, mtime'ı pin anı — UTC, milisaniyeye kadar, 447'nin `pinnedAt`'i ile
  aynı biçim.
- **Arşiv:** `<id>/archived` varsa arşivli. **İkisi birden varsa arşiv kazanır ve pin yazılmaz**
  (Madde 384) — eski bir arşivin bıraktığı pin dosyası.
- **Sohbetler:** `<id>/chats/` içindeki her `.json` dosyası — başka dosyalar atlanır, eski
  `list_for` gibi. Her biri sohbet deposunun kendi okuyucusuyla (`file_chat_store`'un `_as_chat`'i)
  bir `Chat`'e döner, ve ondan hemen satırın dört alanı bir `ChatSummary` olarak tutulur — mesajlar
  yazmaya kadar bellekte beklemez (100 projede 972 sohbetin bütün mesajları). Satır 447'nin
  `put_chat`'inin kullandığı aynı fonksiyonla kurulur: id dosyanın adından, başlık ve doğuş içerikten,
  **son kullanım `Chat.last_activity`** — açık kolun son mesajının anı, 447'deki anlamı. İkinci bir
  özet kurucu yazılmaz.
- **Dosyalar:** `<id>/files/` içindeki her ad, ve mtime'ı değişme anı — eski `list_files` gibi; satırı
  `put_file`'ın aynı fonksiyonuyla.

### 3 · Nasıl eklenir — tek bir değişiklik, tek bir yazma

Bulunan bütün projeler `FileProjectStore.take_in(moved)`'a tek seferde verilir: tek bir `_change`,
yani tek bir `projects.json` yazması, 447'nin yazıcısıyla. Değişikliğin içinde id yeniden sorulur —
olan id'ye dokunulmaz. Taşınacak bir şey yoksa `take_in` hiç çağrılmaz, hiçbir şey yazılmaz.

Taşınan her zaman bir metin olmak zorunda, ve bu okurken denetlenir (§5): liste projeleri ve
sohbetleri zamanlarına göre sıralıyor, ve `projects.json`'a giren bir sayı ya da `null` sonraki her
açılışta her listeyi 500'e düşürürdü (QA, tek sohbetli bir projede `"at": 12345`).

İkinci bir çizgi olarak her yeni kayıt, eklenmeden önce **bir sonraki açılışın okuduğu gibi okunur**
(`_as_project`, 447'nin `_loaded`'ının her kayıtta yaptığı): okunamayan kayıt eklenmez, `take_in` onu
`(id, hata)` olarak döner ve taşıma log'a yazar. Zamanlar okurken denetlendiği için taşımanın kurduğu
bir kayıt buna bugün takılmaz — `_as_project`'in okuduğu her şey bir metin, bir liste ya da onlardan
hesaplanan. Hepsi reddedilseydi de hiçbir şey yazılmazdı: yazıcı (`QueuedWrite`) değişmeyen bir
`projects.json`'ı yazmaz.

### 4 · Eski dosyalara dokunulmaz

`project.json`, `pinned`, `archived`, sohbetler ve dosyalar yerinde, değişmeden kalır: taşıma yalnız
okur. Onları bir sonraki roadmap kaldırır (BACKLOG).

### 5 · Okunamayan eski proje

Bir eski projenin `project.json`'u ya da sohbetlerinden biri okunamazsa — JSON değil, `name` ya da
`createdAt` yok, sohbetin alanları eksik — **o proje bütün olarak atlanır** ve log'a dosyanın yolu ve
okuyucunun kendi sözüyle yazılır: *"Old project p… was not moved: p…/chats/c….json: JSONDecodeError(…)"*.
Sunucu durmaz, hiçbir şey yazılmaz; öbür projeler taşınır. Neden bütün olarak: yarım taşınan bir proje
bir daha taşınmazdı (kaydı artık var), ve eksik sohbeti kaybolurdu; atlanan proje, dosyası düzelince
bir sonraki açılışta bütün olarak taşınır.

Aynısı iki durumda daha:

- **Diskin kendi hatası** — bir klasör listelemesi ya da bir `mtime` reddedilir (`PermissionError`,
  Drive'da `EIO`), ya da bir dosya klasör listelendikten sonra gider. Bunlar okuyucuların korumasının
  dışında; `move_old_projects` her projeyi `(_Unreadable, OSError)` ile sarar. `NotADirectoryError`
  (kökte bir dosya) bundan önce yakalanır ve "eski proje değil" sayılır.
- **Metin olmayan bir zaman** — `project.json`'un `createdAt`'i, bir sohbetin `createdAt`'i ya da
  son kullanımı (açık kolun son mesajının `at`'i) sayı, `null` ya da başka bir şey: *"Old project p…
  was not moved: p…/chats/c1.json: TypeError("a message's at is 12345, not a time")"*. Eski uygulama
  böyle bir projeyi gösteriyordu; yeni liste onu sıralayamaz. Pin ve dosya zamanları burada
  mtime'dan basılır, hep metindir.

### 6 · Colab'da açılış süresi

Taşıyan açılış sunucu cevap vermeden önce olur: Drive'da 30 projede ~587, 100 projede ~1930 işlem
(*Ölçüm*), yani dakikalar. Defterin Serve hücresi 90 sn bekleyip vazgeçiyordu. Şimdi:

- Sunucu `server = subprocess.Popen(...)` ile tutulur; `/api/health` **sunucu yaşadıkça**
  (`server.poll() is None`) beklenir, **10 dakikalık bir tavana kadar** (`START_CAP = 600`).
- Her 30 sn'de *"⏳ Sunucu hâlâ açılıyor (N sn)"* basılır.
- Sunucu kapanırsa log'unun sonu basılır ve hemen *"❌ Sunucu kapandı (N sn sonra)"* fırlar — tavan
  beklenmez.
- Tavanda log'un sonu ve *"❌ Sunucu N sn içinde cevap vermedi"*, N gerçek saniye.
- Sunucu da ilk eski projeyi bulunca stderr'e — dolayısıyla `APP_LOG`'a — bir satır yazar:
  *"Moving projects of the old layout into projects.json; this start takes longer."* (İngilizce, kodun
  çıktısı olarak), okunabilen ilk eski proje okunduktan sonra. Taşıyacak bir şey yoksa yazmaz —
  eski projelerin hepsi okunamıyorsa da: onlar her açılışta yeniden denenir, ve satır her açılışta
  hiçbir şey taşınmadan basılırdı. Satır basıldıktan sonra `take_in`'in bir kaydı reddetmesi bugün
  olamaz (§3); olsaydı da o kayıt her açılışta yeniden denenirdi.

Tavan 448 için bu uzunlukta; taşıma kalkınca kısalabilir (yorumu hücrede).

### 7 · Tek yerde, silinmesi kolay

- **`data/old_projects.py`** — yeni modül: `move_old_projects(store, projects)` ve eski düzeni okuyan
  yardımcıları. Eski düzeni bilen tek yer.
- **`FileProjectStore.take_in(moved)`** — bulunanı tek değişiklikle ekleyen tek metod.
- **`Store.mtime`** — 447'de kaldırılmıştı; eski düzende pin anı ve dosya anı yalnız mtime'da duruyor,
  ve yalnız taşıma okuyor.
- **`main.py`'de tek satır.**
- **Serve hücresinin tavanı** (§6) — beklemenin kendisi kalır, tavan kısalabilir.

Hepsinin yanında *"448'in taşıması onaylanınca kalkar (BACKLOG)"* yorumu durur. Silmek: modül, metod,
`mtime`, satır ve testleri.

## Her işlemin bedeli

N kökteki ad sayısı (projeler, çöp, `projects.json`), M taşınan proje, her biri için C sohbet ve F dosya.

- **Her açılış, taşıyacak bir şey yokken** (ikinci açılıştan sonra hep): kök listelemesi 1, ad başına
  bir sözlük bakışı. Kayıtta olmayan her başka klasör — çöp dışı, eski olmayan — 1 listeleme daha
  (bugün: yok; bir çöküşte kaydını kaybetmiş bir v10 projesinin klasörü böyle olur). O(1) işlem, O(N)
  bellekte.
- **Taşıyan açılış:** proje başına klasör listelemesi 1, `project.json` 1, `chats/` listelemesi 1, her
  sohbet 1 okuma, `files/` listelemesi 1, her dosya 1 `mtime`, pin varsa 1 `mtime` → 4 + C + F (+1);
  sonra bütün taşıma için tek `projects.json` yazması (2). O(M + ΣC + ΣF) okuma, bir kez. Kayıtların
  `_as_project` ile okunması bellekte, disk işlemi değil. Bellekte bir anda bir sohbetin mesajları
  durur; tutulan, her sohbetin dört alanı.
- **Defterin beklemesi:** 2 sn'de bir `poll` ve bir `/api/health` isteği, makinenin içinde — Drive'a
  ya da tünele gitmez.

## Ölçüm

`tmp/m448/measure.py` (`result.txt`): 446'nın tohumu eski düzende, sonra `main.py`'nin yaptığı gibi iki
açılış; Store'un her `os` çağrısı sayılarak, yazıcı açılışın hanesinde.

| Açılış | 30 proje (267 sohbet, 192 dosya) | 100 proje (972 sohbet, 541 dosya) |
|---|---|---|
| Taşıyan | 587 — listeleme 91, okuma 298, `mtime` 196, yazma 1 + yerine koyma 1 | 1930 — listeleme 301, okuma 1073, `mtime` 554, yazma 1 + yerine koyma 1 |
| Sonraki her açılış | 2 — `projects.json` okuması 1, kök listelemesi 1 | 2 — aynı |

Taşıyan açılış formülü tutuyor: 30 projede 1 + 30 × 3 listeleme; 1 + 30 + 267 okuma (ilki
`projects.json`'un yokluğu); 192 dosya + 4 pin `mtime`'ı (beş pinden biri arşivli, Madde 384). İkinci
açılış proje sayısıyla büyümüyor. Yerel duvar saati (13 s, 45 s) bu makinede taze yazılmış dosyaları
açarken dosya başına ~40 ms'lik bir taramadan — 447'nin "önce" ölçümünde de aynısı vardı; Drive'da
belirleyici olan işlem sayısı.

## Sınırlar

- Taşıma yalnız açılışta: sunucu açıkken köke elle konan eski bir proje bir sonraki açılışta taşınır.
- Okunamayan eski proje her açılışta yeniden denenir ve her seferinde log'a yazılır, düzelene kadar.
- Eski bir projenin son kullanımı, eski sürümde sohbet dosyasının mtime'ıydı; taşınınca 447'nin
  anlamını alır — son mesajın anı. Proje listesindeki sıra bu yüzden eski sürümdekinden biraz farklı
  olabilir (447'nin spec'i, *Sınırlar*).
- Eski bir sohbetin çöpteki ya da başka yerdeki kopyaları okunmaz: yalnız `<id>/chats/*.json`.
- API ve ekran değişmez.

## Değişen dosyalar

- `queen-agent/backend/features/workspace/data/old_projects.py` — yeni.
- `…/data/file_project_store.py` — `take_in`; satır kurucular `put_chat` / `put_file`'dan ayrılır,
  ikisi ve `take_in` aynısını kullanır.
- `queen-agent/backend/services/store/store.py` — `mtime` geri gelir.
- `queen-agent/main.py` — tek satır.
- `queen-agent/queenagent.ipynb` — Serve hücresinin beklemesi (§6).
- Testler: `test_old_projects.py` (yeni), `test_composition.py`, `test_store.py`, `test_notebook.py`.

## Testler

`test_old_projects.py` eski düzeni elle tohumlar — 447'den önceki biçimde:

- Taşınan sonuç: ad, doğuş, pin anı (`pinned`'ın mtime'ı), arşiv; ikisi birden → arşivli, pinsiz;
  sohbet satırları (başlık, doğuş, son kullanım = açık kolun son mesajı); dosya adları ve anları
  (mtime); sohbet olmayan dosyalar atlanır.
- Tek yazma: taşıma `projects.json`'ı bir kez yazar.
- İkinci açılış hiçbir şey taşımaz ve hiçbir şey yazmaz; listesi aynı. Kökün kendisi bir kez
  listelenir, başka hiçbir şey okunmaz.
- Kayıtta olan bir v10 projesi — aynı id'li eski bir klasör olsa bile — olduğu gibi kalır.
- Yarıda kesilmiş taşıma: kaydı eksik olanlar taşınır, olanlara dokunulmaz.
- Eski dosyalar dokunulmadan: içerikleri ve mtime'ları önce ve sonra aynı.
- `trash/`, kökteki bir dosya, `project.json`'u olmayan bir klasör atlanır.
- Okunamayan `project.json` ya da sohbet: o proje atlanır, log'da yolu ve hatası, öbürleri taşınır,
  hata fırlamaz, dosya değişmez.
- Bir projede `mtime`'ı `OSError` veren bir Store: yalnız o proje atlanır, log'da diskin sözü, öbürü
  taşınır, açılış durmaz.
- Metin olmayan zaman — tek sohbetin sayı olan mesaj zamanı, sayı olan sohbet doğuşu, sayı ya da
  `null` proje doğuşu: o proje taşınmaz, log'da *"not a time"*; öbürü taşınır, ve bir sonraki
  açılışta liste (`list_projects`) cevap verir. QA'nın `tmp/m448-qa/odd_types.py`'si: dört durumda
  da liste cevap veriyor.
- `take_in`, karşılaştırılamayan iki son kullanımı olan bir kaydı eklemez ve `(id, hata)` döner.
- Taşıyan açılış stderr'e "Moving projects of the old layout" satırını bir kez yazar, taşıyacak bir
  şey olmayan açılış hiç yazmaz; eski projeleri yalnız okunamayanlar olan açılış da yazmaz.
- `test_composition.py`: `main.py` taşımayı çağırıyor.
- `test_notebook.py`: Serve hücresi sunucuyu `server` olarak tutuyor ve beklerken `server.poll()`'a
  bakıyor. Hücrenin kendisi `tmp/m448/serve_wait.py` ile denendi: ölen bir sunucuda 6 sn'de
  "kapandı", cevap vermeyen birinde 30 ve 62 sn'de "hâlâ açılıyor", tavanda gerçek saniyeyle hata.

## Bitti sayılır

- Testler yeşil, dört suite sırayla yeşil; `frontend/` ve `dist` değişmemiş.
- Colab'da taşıyan açılış 90 sn'yi geçse de hücre bekliyor ve her 30 sn'de söylüyor.
- Eski biçimdeki projeler adları, pinleri, arşivleri, sohbetleri ve dosyalarıyla ilk açılışta
  listede; v10 projeleri yerinde; ikinci açılışta taşınan bir şey yok; eski dosyalar diskte duruyor.
