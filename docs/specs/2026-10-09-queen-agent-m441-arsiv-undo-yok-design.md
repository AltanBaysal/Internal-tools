# Madde 441 · Arşivde Undo yok — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
441 (eski adı v10-2) · **Dal:** `feat/queenagent-v10` · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Tasarım:** `queen-design`'ın `queen-agent-v4` dalı, madde 217 — `projects/queen-agent/BEHAVIOUR.md`'nin
*All projects* bölümü (*"Archive takes the row out at once"*) ve `projects/` sayfası.

## Ne, neden

Kullanıcı, 1 Ekim: *"arşivden undo özeeliği kaldır"*; 5 Ekim, önce bir şey sorulup sorulmayacağına:
*"çıkmasın ve doğru anlamışsınm"*. Arşivlenen proje hemen Projects'ten çıkar ve Archived'da görünür;
geri getirmenin yolu Archived'daki ⋯ → *Unarchive*, bugünkü gibi.

Bugün:

- Archive'a basınca satır, başka bir şey yapılana kadar *"<ad> archived · Undo"* satırına dönüyor
  ([ProjectRow.jsx](../../queen-agent/frontend/src/features/workspace/ProjectRow.jsx)'in `UndoRow`'u).
  [AllProjectsScreen.jsx](../../queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx)
  o projeyi `undoing`'de tutuyor: Projects listesinde, sunucu arşivledi dese de, Undo satırı olarak
  kalıyor; bir ⋯ açılınca ya da sekme değişince gidiyor. Odak Undo'da.
- Sunucu arşivle pini zaten kaldırıyor, ve Unarchive pini geri getirmiyor (Madde 384,
  [edit_project.py](../../queen-agent/backend/features/workspace/domain/usecases/edit_project.py);
  CODE-STANDARD'ın tablosu: `pinned` arşivde ve arşivden çıkışta silinir). Ön uç yalnız
  `{ archived }` ister, ve proje sunucunun sırasında durur: Unarchive onu Recent'e, son kullanımının
  yerine getirir. **Bu kısım değişmez**; tasarımın *"Archiving also unpins the project"*'i bugün
  sunucunun kuralı, ve App'in testi onu tutuyor.
- Son proje arşivlenince Projects sekmesi zaten *"Every project is archived."* diyor
  (`ProjectList`'in boş hâli). Yeni olan, bunun Archive'ın hemen ardından görünmesi.

## Olacak

### 1 · Undo satırı her yerden kalkar

`UndoRow`, ekrandaki `undoing` ve onu bırakan iki sarmalayıcı (`openMenu`, `switchTab`) silinir;
`workspace.css`'teki `.all-projects__undo` kuralları da — tasarım onları `kit.css`'ten sildi. Archive
soru sormaz, yerine bir şey çizmez.

### 2 · Archive satırı hemen çıkarır *(tasarım 217)*

Archive'a basılınca proje o anda Projects'ten çıkar ve Archived'da görünür; iki sekmenin sayısı da o
anda değişir. Sunucuyu beklemek olmaz: arşivleme yavaş (446), ve bugün basılır basılmaz Undo satırı
çıkıyordu — beklense menü kapanır, satır saniyelerce yerinde durur, ve basış hiçbir şey yapmamış gibi
görünür.

Bunun için ekran, Archive'ı sorulmuş ama cevabı gelmemiş projeleri `leaving`'de tutar ve onları,
sunucunun listesinde, arşivli çizer. Cevap — `editProject` listeyi yeniden okuyup döndüğünde — gelince
proje `leaving`'den çıkar ve yeri artık sunucunun listesinin:

- **arşivlendiyse** Archived'da, sunucunun sırasında;
- **reddedildiyse** Projects'e geri döner, ve sunucunun sözü listenin üstündeki satırda
  (`writeError`, bugünkü gibi). Kullanıcı olmayan bir arşivi görmez.

Bu, beklerken ne gösterildiği; kural değil (FOUNDATION, Karar 4): projenin nerede durduğu ve pinin ne
olduğu sunucunun cevabından okunur. Arka arkaya iki Archive, her biri kendi cevabına kadar `leaving`'de
durur.

Unarchive bugünkü gibi sunucuyu bekler: madde onu istemiyor.

### 3 · Odak *(tasarım 217)*

Basılan ⋯ satırıyla gider. Odak, onun yerine gelen satırın ⋯'sine geçer — listede çizildiği sırayla
bir sonraki, Pinned'dan Recent'e geçerek, arama açıksa aramanın bıraktıkları içinde —; arşivlenen son
satırsa, ya da tek satırsa, aramaya. Satır çıkmadan önce, Archive'ın kendi basışında verilir: sonraki
satır o anda zaten çizili, ve arama her zaman yerinde.

Sonraki ⋯'yi bulmak için ⋯'ler projelerinin kimliğini `data-project`'te taşır; ekran kendi
sütunundaki `[data-project]`'leri çizildikleri sırayla okur. Tasarımın sayfası da böyle bulur
(`data-address`).

Sonraki ⋯ pencereyi kaydırmaz (`preventScroll`, tasarımdaki gibi): bakılan yere o gelir. Arama ise
kaydırılarak görünür: uzun, aşağı kaydırılmış bir listenin son satırı arşivlenince arama ekranın çok
yukarısında kalabilir, ve klavye görünmeyen bir yerde kalmamalı. Burada tasarımdan ayrılıyoruz;
tasarımın sayfası aramayı da kaydırmadan odaklar.

Beklerken proje, sunucunun sırasındaki yerinde arşivli çizilir: pinli olan bir proje cevap gelene kadar
Archived'ın en üstünde durur ve cevapla son kullanımının yerine geçer. Bu bir hata değil.

### 4 · Son proje

Son açık proje arşivlenince Projects hemen *"Every project is archived."* der, sayılar `0` ve
hepsinin sayısı; odak aramada. Yeni kod yok: `leaving` sayılara ve listeye girdiği için bugünkü boş hâl
o anda görünür.

## Sınırlar

- Arka uç değişmez. Pinin arşivle gitmesi ve Unarchive'ın Recent'e getirmesi Madde 384'ten beri
  sunucuda. Yalnız `test_pin_archive.py`'deki bir testin adı ve sözleri Undo'dan Unarchive'a geçer:
  davranışı aynı, Undo artık yok.
- FOUNDATION'ın 1. ilkesi (*"either explicitly confirmed or explicitly undoable"*) bozulmaz: arşiv bir
  şey silmez, ve Archived'daki *Unarchive* onu geri alır.
- Arşivdeki satırın açılması 443'ün; burada Archived satırı bugünkü gibi.
- queen-editor'e dokunulmaz.

## Değişen dosyalar

- `frontend/src/features/workspace/ProjectRow.jsx` — `UndoRow` gider; ⋯ `data-project` taşır; üst
  yorum.
- `frontend/src/features/workspace/AllProjectsScreen.jsx` — `undoing` yerine `leaving`; Archive'da
  odağın devri; aramaya ve sütuna birer ref.
- `frontend/src/features/workspace/workspace.css` — `.all-projects__undo` kuralları gider.
- Testler: `AllProjectsScreen.test.jsx`, `ProjectRow.test.jsx`, `App.test.jsx`,
  `workspace.css.test.js` ve `shared/app.css.test.js` (Undo satırının testleri gider),
  `backend/tests/test_pin_archive.py` (ad ve sözler).
- `frontend/dist` yeniden derlenir.

## Testler

**Ekran (`AllProjectsScreen.test.jsx`):** Archive soru sormaz ve `onArchiveProject(id, true)` ister;
sunucu daha cevap vermeden proje Projects'te yok, Archived'da var, sayılar değişmiş, Undo satırı yok;
odak sonraki satırın ⋯'sinde — Pinned'dan Recent'e geçerek, aramada aramanın bıraktığı sonraki satırda,
`preventScroll`'la; son satırda ve tek satırda aramada, kaydırarak (jsdom yerleşim yapmaz: test
`focus`'un hangi seçenekle çağrıldığına bakar, kaydırmanın kendisini tarayıcı gösterir); son proje arşivlenince *"Every project is archived."* hemen;
sunucu reddederse proje Projects'e döner; cevap gelince sunucunun listesi geçer; arka arkaya iki
Archive ikisini de çıkarır; Unarchive geri ister ve Undo bırakmaz.

**Satır (`ProjectRow.test.jsx`):** ⋯ projesinin kimliğini taşır.

**App (`App.test.jsx`):** Archive soru sormadan projeyi çıkarır, PATCH yalnız `{ archived: true }`,
Archived'da görünür, Undo yok; pinli proje arşivlenip — arşivin cevabı, yeniden okunan liste,
geldikten sonra — Unarchive'la döndüğünde Recent'te (bugünkü test, cevabı bekleyerek); reddedilen
arşivde proje Projects'e döner ve sunucunun sözü görünür.

**CSS (`workspace.css.test.js`, `app.css.test.js`):** Undo satırının kurallarına bakan testler gider;
yokluğunu bekleyen bir test yazılmaz — silinmiş bir şeyin bekçisi sonsuza kadar kalır.

**Arka uç (`test_pin_archive.py`):** davranış aynı, testin adı Unarchive'ı söyler.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: Projects'te arşivlenen proje soru sorulmadan hemen listeden çıkıyor ve
  Archived'da görünüyor, iki sayı değişiyor; Undo satırı hiçbir yerde yok; odak yerine gelen satırın
  ⋯'sinde, satır kalmadıysa aramada; son proje arşivlenince *"Every project is archived."*; pinli proje
  arşivlenip Unarchive'la Recent'e dönüyor.
