# Madde 451 · Unarchive'dan sonra odak — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
451 · **Dal:** `feat/queenagent-v10`, ana klasörde, commit ana agent'ın · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Öncesi:** [441](2026-10-09-queen-agent-m441-arsiv-undo-yok-design.md) (Archive'da odağın devri,
tasarım 217), [450](2026-10-09-queen-agent-m450-arsiv-sirasi-design.md) (Unarchive satırı hemen
çıkarır)

## Ne, neden

441'i deneyen QA'nın bulduğu; kullanıcı, 9 Ekim: *"onları da bu roadmap'te çöz"*.

**Bugün** Archived sekmesinde ⋯ → *Unarchive*'a basınca satır gidiyor — 450'den beri basışta, cevabı
beklemeden — ve basılan ⋯ onunla gidiyor. Odağı kimse devralmıyor; tarayıcı onu sayfanın gövdesine
düşürüyor, ve Tab sayfanın başından başlıyor.

[AllProjectsScreen.jsx](../../queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx)'te
odağı devreden `handOverFrom(id)` 441'den beri var, ama yalnız Archive'da çağrılıyor:
`if (toArchive) handOverFrom(id)`. 450 bu koşulu bilerek bıraktı: *"Unarchive'dan sonra odak 451'in
maddesi"*.

Tasarım (217) odağın devrini yalnız Archive için yazıyor; prototipin `unarchive`'ı satırı çıkarıp
yeniden çiziyor, odağa dokunmuyor. Buradaki kural tasarımda yok: madde onu, Archive'ınkini örnek alarak
istiyor.

## Olacak

### 1 · Unarchive da odağı devreder

Unarchive'da odak, Archive'daki gibi gider: basılan ⋯'nin satırından sonra çizilen satırın ⋯'sine —
arama açıksa aramanın bıraktıkları içinde —, sonraki satır yoksa aramaya. Archived bir başlıksız tek
liste olduğu için "sonraki" orada yalnız listenin bir aşağısı.

Bunun için ikinci bir devir yazılmaz: `archive` her basışta `handOverFrom(id)`'yi çağırır, koşul
kalkar. Bu doğru, çünkü iki basış da satırı **o anda gösterilen sekmeden** çıkarır: Archive'ı yalnız
Projects'teki satırın ⋯'si taşır, Unarchive'ı yalnız Archived'dakinin (`ProjectRow`'un menüsü
`project.archived`'a bakar). Hangisine basılırsa basılsın, satır sütundan gider ve onun yerine
sonraki gelir.

`handOverFrom`'un geri kalanı değişmez:

- Sonraki ⋯ `preventScroll`'la odaklanır: bakılan yere o gelir.
- Arama kaydırılarak odaklanır: uzun, aşağı kaydırılmış bir Archived listesinin son satırı geri
  alınınca arama ekranın yukarısında kalabilir, ve klavye görünmeyen bir yerde bırakılmaz (441'in
  tasarımdan tek farkı, aynen).
- Devir satır çıkmadan önce, basışın kendisinde verilir: o an sonraki satır hâlâ çizili.

Tab oradan sürer: odak gerçek bir düğmede (ya da aramada), tarayıcı sıradakini oradan bulur.

### 2 · Reddedilen Unarchive

Sunucu reddederse satır Archived'a, eski yerine geri gelir ve sunucunun sözü listenin üstündeki
satırda görünür (450, `writeError`). **Odak yerinden oynamaz:** basışta nereye verildiyse — sonraki
satırın ⋯'si ya da arama — orada kalır. 441 reddedilen Archive'da da böyle yaptı: devir basışta bir
kez verilir, cevap odağa dokunmaz.

Neden geri çekilmez: cevap saniyeler sonra gelebilir (446), ve o arada kullanıcı başka bir yere
geçmiş olabilir — aramaya yazıyor, başka bir satırın menüsünü açmış. Cevapla odağı geri çekmek onu
kullanıcının gittiği yerden koparır; arama kutusunun autoFocus'u da aynı nedenle liste gelince
yeniden verilmiyor. Odağın kaldığı yer zaten anlamlı: sonraki satırın ⋯'si, geri gelen satırın hemen
altında; arama, listenin başında. Geri gelen satıra dönmek isteyen için Shift+Tab iki adım: önce sonraki satırın
kendi açma düğmesi, sonra geri gelen satırın ⋯'si.

Bunun için kod yok: `archive` cevaptan sonra yalnız `asked`'deki kendi kaydını siler.

### 3 · Bulunamayan satır

`handOverFrom` basılan satırı ⋯'sinin `data-project`'iyle bulur. Bulamazsa `findIndex` -1 döner, ve
bugün `mores[0]` — listenin ilk ⋯'si — sessizce odağı alır. Bugün bir yoldan ulaşılmıyor ve 451'den
eski; reviewer'ın onayıyla burada kapanır: satır bulunamazsa sonraki de yoktur, odak aramaya gider.
Tasarımın sayfası da böyle korur (`at === -1`).

### 4 · Archive beklerken Unarchive

450'nin durumu: Archive'a basılır, Archived'a geçilir, aynı projede cevap gelmeden Unarchive'a
basılır. Satır Archived'dan çıkarken odak, oradaki sonraki satırın ⋯'sine ya da aramaya geçer —
herhangi bir Unarchive gibi. Özel bir dal yok.

## Her işlemin bedeli

Ağ ve disk değişmez: odak tarayıcının içinde. Unarchive basışı 450'deki gibi 1 PATCH + 1
`GET /api/projects`, sırayla; sunucunun diskinde istekte 0, yazıcıda O(1).

Devir sayfanın kendisini okur: sütundaki `[data-project]` düğmelerini bir kez sorgular ve basılanın
yerini arar — gösterilen satır sayısıyla O(N), bellekte, basış başına bir kez. Archive'da 441'den beri
aynı bedel.

## Sınırlar

- Yalnız `AllProjectsScreen.jsx` değişir: `archive`'daki koşul kalkar, `handOverFrom` bulunamayan
  satırda aramaya gider (§3), ve yorumlar iki basışı söyler.
- Arka uç değişmez. queen-editor'e dokunulmaz.
- jsdom Tab'a basmayı yürütmez: test odağın hangi öğede olduğuna bakar; Tab'ın oradan sürdüğünü
  tarayıcıdaki deneme gösterir.

## Değişen dosyalar

- `queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx` — `archive` devri her basışta
  yapar; `handOverFrom` bulunamayan satırda aramaya gider; `handOverFrom`'un üstündeki yorum iki
  basışı, `archive`'ın üstündeki reddi söyler.
- `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx` — Unarchive'ın odak testleri.
- `queen-agent/frontend/dist` yeniden derlenir.

## Testler

**Ekran (`AllProjectsScreen.test.jsx`):**

- Archived'da Unarchive'dan sonra odak sonraki satırın ⋯'sinde, `preventScroll`'la.
- Aramada, aramanın bıraktığı sonraki Archived satırının ⋯'sinde.
- Son Archived satırında — ya da tek satırda — odak aramada, kaydırarak (`focus` seçeneksiz
  çağrılır); tek satırda *"No archived projects."* görünür.
- Reddedilen Unarchive'da satır geri gelir, odak basışta verildiği ⋯'de kalır.
- Basılan satırın ⋯'si çizili ⋯'ler arasında yoksa odak aramaya gider, ilk ⋯'ye değil (test ⋯'nin
  `data-project`'ini kaldırarak kurar).
- 441'in Archive odak testleri ve 450'nin testleri değişmeden geçer.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite sırayla yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: Archived'da klavyeyle ⋯ → *Unarchive* yapınca odak sıradaki satırın
  ⋯'sinde, satır kalmadıysa arama kutusunda; Tab oradan sürüyor. Reddedilen bir Unarchive'da satır
  geri geliyor, odak olduğu yerde.
