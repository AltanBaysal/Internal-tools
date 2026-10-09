# Madde 443 · Arşivdeki proje açılır — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
443 (eski adı v10-3) · **Dal:** `feat/queenagent-v10` · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Tasarım:** `queen-design`'ın `queen-agent-v4` dalı, madde 218 — `projects/queen-agent/BEHAVIOUR.md`'nin
*All projects* bölümü (*"An archived row opens its project"*), `projects/` sayfası ve `kit.css`.

## Ne, neden

Kullanıcı, 1 Ekim: *"arşivdeki projeler açılmıyor açılır hale getir"*. 5 Ekim, açmanın arşivden
çıkarıp çıkarmayacağı sorulunca: *"kalsın"*. Arşivdeki projede sohbet edilip edilemeyeceği sorulunca:
*"evet edwielbislin arlivde ve plamayan projeler arasındaki tek farkı farklı listede olmaları başka bir
farko lmayacak basit tut farkları"*.

Arşivdeki satıra basınca proje, öteki projeler gibi açılır: son sohbeti, sohbeti yoksa taslak.
Açmak arşivden çıkarmaz, proje Archived'da kalır. Çıkmanın tek yolu ⋯ → *Unarchive*. Projenin içinde
arşivli olduğunu gösteren bir şey yok, ve sohbet edilebilir.

Bugün:

- Archived sekmesindeki satır bir düğme değil, `.all-projects__row-text` sınıflı bir `div`
  ([ProjectRow.jsx](../../queen-agent/frontend/src/features/workspace/ProjectRow.jsx); tasarım 190,
  191). Üç sütunu Projects'teki satırla aynı, ama basılınca hiçbir şey olmuyor. Yalnız ⋯ çalışıyor.
- All projects'in aramasında Enter hiçbir sekmede bir şey yapmıyor. Madde 359 onu bilerek dışarıda
  bırakmıştı ([359'un test spec'i](2026-09-29-queenagent-m359-projelerde-arama-testler-design.md),
  Karar 7: *"Enter ve Esc bu maddede yok … açık nokta"*).

### Sunucu arşivdeki projeyi reddetmiyor — kodda bakıldı

Yol haritası işin yalnız ekranda olduğunu söylüyor. Kodda doğrulandı:

- `FileProjectStore.get`, `list_all`'dan okur, ve `list_all` arşivdekileri de döndürür. `archived`
  yalnız satırın bir alanı.
- `archived`'ı okuyan yalnız `Project.pinned`, `list_projects`'in sırası ve `edit_project`.
  `append_message`, `stream_answer`, sohbet, dosya, sürüm, kırpma, durdurma ve izin kapıları onu
  hiç okumuyor. Ajanın dosya yazan araçları da okumuyor.
- Ön uçta App, açık projeyi elindeki bütün listede arıyor; arşivdekiler de bu listede. `OpenProject`
  projenin sohbetlerini okuyup son sohbete ya da taslağa gidiyor. Bar projenin adını, kenar çubuğu
  sohbetlerini gösteriyor. Hiçbiri `archived`'a bakmıyor.

Yani sunucuya ve App'e yeni kod gerekmiyor. Arka uçta bir API testi bunu tutar (aşağıda): kullanıcının
*"başka bir fark olmayacak"* kararı bugün tesadüfen doğru. Test olmazsa, bir gün arşivdekini
reddeden bir kural sessizce girebilir.

## Olacak

### 1 · Arşivdeki satır, öteki satırların düğmesi *(tasarım 218)*

`ProjectRow`'da arşivdeki satırın ayrı gövdesi gider. Her satır aynı `all-projects__row-open`
düğmesini çizer: aynı üç sütun, aynı `title`, ve basılınca `onOpen(project.id)`. Tasarımın sayfası da
öyle: `rowOpenHtml` arşivdekine ayrı bir şey çizmiyor.

Satırın tek farkı ⋯ menüsü kalır: Rename, Unarchive, Delete. Bu 441'in ve 363'ün, ve değişmez.

Üç sütunu iki gövdeye paylaştırmak için yazılmış `Columns` bileşeninin tek kullanıcısı kalır. Bu
yüzden düğmenin içine geri döner.

### 2 · Açmak hiçbir şey yazmaz

Basış App'in `openProject`'ine gider (`/p/<id>`), Projects'teki satırınki gibi. Sunucuya PATCH gitmez,
proje Archived'da kalır. *Exit project* All projects'e döner. Ekran Projects sekmesinde açılır, ki
sekme ekranın kendi durumu. Proje orada listelenmez, Archived'da durur. Tasarım da böyle.

### 3 · Aramada Enter ilk eşleşmeyi açar, iki sekmede de *(tasarım 218)*

Yol haritası: *"Archived sekmesinin aramasında da Enter ilk eşleşmeyi açar, Projects'teki gibi"*. Ama
uygulamada Projects'in aramasında da Enter yok (yukarıda, 359'un Karar 7'si). Yalnız Archived'a
koymak, arşivdeki projeye ötekilerde olmayan bir tuş verirdi. Bu da kullanıcının *"tek fark liste"*
sözüne aykırı. Tasarım iki sekmede de Enter'la ilk eşleşmeyi açıyor, ve kullanıcı tasarımı kendi
tarafında hizaladı.

Bu yüzden 443, 359'un açık bıraktığı Enter'ı da kurar. İki sekmede de Enter ilk eşleşmeyi açar
*(koordinatör, 9 Ekim — seçenek 1)*:

- **İlk eşleşme, çizilen ilk satır:** arama listeyi daralttıktan sonra, açık sekmede en üstte duran
  proje. Projects'te Pinned Recent'ten önce gelir. Sunucunun sırası zaten önce pinlileri dizer
  (`list_projects.py`), ve ekran bu sırayı yalnız böler. Bu yüzden eşleşenlerin ilki çizilen ilk
  satırdır.
- **Boş kutuda Enter** sekmenin ilk satırını açar, tasarımdaki gibi.
- **Eşleşme yoksa** (`No projects match …`), proje hiç yoksa ya da liste yükleniyorsa Enter bir şey
  yapmaz.
- **Escape eklenmez:** satır onu istemiyor. Tasarımda Escape aramayı boşaltıyor; bu madde onu
  almıyor.

Eşleşmeyi bugün `ProjectList` kendi içinde hesaplıyor. Enter da aynı listeyi istediği için hesap
ekrana çıkar, ve `ProjectList` eşleşenleri hazır alır. Böylece listenin gösterdiği ile Enter'ın
açtığı tek bir hesaptan gelir, ve ayrışamaz.

### 4 · CSS

`workspace.css`'teki `.all-projects__row-text` kuralı silinir. Tasarım onu `kit.css`'ten sildi.
Arşivdeki satır artık `.all-projects__row-open`'ı giyiyor.

## Sınırlar

- Arka uçta kod değişmez; yalnız bir test eklenir.
- App değişmez: `openProject` ve `OpenProject` arşivdeki projeyi zaten açıyor.
- Proje içinde arşivi gösteren bir iz eklenmez: bar, kenar çubuğu, sohbet ve dosyalar aynı.
- Escape eklenmez (3'te).
- queen-editor'e dokunulmaz.

## Değişen dosyalar

- `frontend/src/features/workspace/ProjectRow.jsx` — arşivdeki gövde gider, `Columns` düğmeye
  döner, üst yorum.
- `frontend/src/features/workspace/AllProjectsScreen.jsx` — eşleşenlerin hesabı ekrana çıkar;
  aramada Enter; üst yorum.
- `frontend/src/features/workspace/workspace.css` — `.all-projects__row-text` gider.
- Testler: `ProjectRow.test.jsx`, `AllProjectsScreen.test.jsx`, `App.test.jsx`,
  `workspace.css.test.js`, `backend/tests/test_pin_archive.py`.
- `frontend/dist` yeniden derlenir.

## Testler

**Satır (`ProjectRow.test.jsx`):** arşivdeki satırın *"açılmaz"* testi yerine: arşivdeki satır,
Projects'teki gibi `all-projects__row-open` düğmesi. Üç sütunu ve `title`'ı aynı, basınca
`onOpen("p2")`, ve ⋯ hâlâ yanında.

**Ekran (`AllProjectsScreen.test.jsx`):**

- Archived'daki satır `all-projects__row-open` ve basınca `onOpenProject`'i projenin kimliğiyle
  çağırır. Bugünkü *"none of them opens"* testinin o kısmı bunu söyler.
- Projects'te Enter, aramanın bıraktığı ilk satırı açar. Pinli bir eşleşme varsa o açılır.
- Archived'da Enter, aramanın bıraktığı ilk arşivli satırı açar.
- Boş kutuda Enter sekmenin ilk satırını açar.
- Eşleşme yoksa, ya da liste yüklenirken, Enter bir şey açmaz.

**App (`App.test.jsx`):** Archived'daki satıra basınca projenin son sohbeti açılır (`/p/p2/c/<son>`).
Bar projenin adını taşır, PATCH gitmez. Sohbette yazılan mesaj o projeye gider
(`POST /api/projects/p2/messages`). *Exit project*'ten sonra proje Projects'te yok, Archived'da duruyor.
Sohbeti olmayan arşivdeki proje taslakta açılır.

**CSS (`workspace.css.test.js`):** `.all-projects__row-text`'in testi gider. Yokluğunu bekleyen bir
test yazılmaz (441'deki gibi).

**Arka uç (`test_pin_archive.py`):** arşivlenmiş bir projede, API üzerinden ve sahte motorla, şunlar
yapılır:

- mesaj gönderilir, cevap kayda yazılır;
- sohbetler listelenir ve sohbet okunur;
- projede duran bir dosya listelenir ve okunur.

Hiçbir kapı reddetmez. Sonunda proje hâlâ arşivde.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: Archived'daki satıra basınca proje son sohbetinde, sohbeti yoksa
  taslakta açılıyor. İçinde sohbet edilebiliyor, ve içinde arşivli olduğunu gösteren bir şey yok.
  *Exit project*'ten sonra proje hâlâ Archived'da. Aramada Enter iki sekmede de çizilen ilk satırı
  açıyor.
