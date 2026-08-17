# Madde 2 — Arama gider · Tasarım Belgesi

**Tarih:** 2026-08-16 · **Yol haritası:**
[QueenAgent v2](../plans/2026-08-15-queenagent-v2-roadmap.md), Faz 1 · Madde 2 ·
**Fark:** [madde 6](../research/2026-08-14-mira-tasarim-farklari.md)

**Amaç:** aramayı üç parçasıyla birlikte sökmek — kenar çubuğu düğmesi, ⌘K kısayolu ve katman.
Tasarım v2 bunu "bilerek kaldırıldı, karar alınmadan geri getirilmesin" diye anıyor ve gerekçesini
veriyor: *proje yapısı zaten gezinmenin kendisi.*

Bu madde **yalnız siler**. Yerine hiçbir şey koymaz.

---

## 1 · Ne gidiyor

### 1.1 · Ön yüz

| Dosya | Ne olur |
|---|---|
| `features/workspace/SearchPanel.jsx` | **silinir** |
| `features/workspace/SearchPanel.test.jsx` | **silinir** |
| `features/workspace/useSearch.js` | **silinir** |
| `App.jsx` | `SearchPanel` ve `useSearch` içe aktarımları, `searching` durumu, `pickHit`, ⌘K dinleyicisi, `onSearch` bağlantısı ve katmanın çizimi gider |
| `features/workspace/Sidebar.jsx` | "Search" düğmesi ve "⌘K" rozeti gider; `onSearch` özelliği kalkar |
| `features/workspace/Sidebar.test.jsx` | arama düğmesine bakan testler gider |
| `features/workspace/workspace.css` | arama katmanının ve sonuç satırlarının stilleri gider |
| `App.test.jsx` | aramayla ilgili testler gider |

### 1.2 · Arka uç

| Dosya | Ne olur |
|---|---|
| `domain/usecases/search.py` | **silinir** |
| `domain/hit.py` | **silinir** — yalnız arama kullanıyor |
| `presentation/routes.py` | `/api/search` uç noktası ve `Hit` alanlarını çeviren gövde gider |
| `backend/tests/test_search.py` | **silinir** |
| `backend/tests/test_files_api.py` | dosya içeriğinde arama yapan iddia gider; dosyanın geri kalanı kalır |

### 1.3 · Klavye

⌘K/Ctrl+K'nın bağlandığı bir şey kalmaz; dinleyici tümüyle gider. **Esc** sırası bir adım kısalır:
bugün "önce arama, sonra açık dosya paneli" iken, bu maddeden sonra yalnız **açık dosya panelini**
kapatır. Esc hiçbir zaman geri gitmez — bu kural değişmiyor.

Sıranın tam hâli Madde 25'te yeniden kurulacak (proje ⋯ menüsü → onay kutusu → Skills → model →
panel). Bu maddede ara hâl budur ve testlerde bu hâl doğrulanır.

### 1.4 · Ölü yorumlar ve belgeler

- `shared/useRoute.js` — yorumdaki "…and the search results of Faz 13 need somewhere to jump to"
  cümlesi artık yanlış. Repo kuralı: bir yorum yalnız bugün doğru olanı söyler. Cümle, adres
  şekillerinin **neden** üç tane olduğunu anlatan hâliyle yeniden yazılır; arama gerekçesi çıkarılır.
- `CODE-STANDARD.md` — "Search is a use case inside `workspace`, not a feature of its own." cümlesi
  düşer. O cümlenin işi tek-feature kuralını örneklemekti; örnek artık yok. Kuralın kendisi
  ("ikinci feature ancak gerçekten ayrı bir bağlam doğduğunda açılır") olduğu gibi kalır.
- `FOUNDATION.md` — arama geçiyorsa aynı ölçüyle bakılır: ilke ya da yığın kararıysa kalır, aramaya
  bağlı bir örnekse düşer.

## 2 · Ne kalıyor

- **Dosya okuma paneli.** Arama sonucundan açılabiliyordu; artık yalnız listeden ve karttan açılır.
  Panelin kendisine dokunulmaz.
- **Adres şekilleri.** `useRoute` üç şekli tutmayı sürdürür; arama onlara yalnız bir *atlama
  sebebi*ydi, tanım değil.
- **Diğer testlerdeki "research" kelimesi.** Fikstürlerdeki `Thesis research` proje adı aramayla
  ilgisizdir; dokunulmaz.

## 3 · Katman denetimi

Silme bağımlılık yönünü **gevşetir**, sıkmaz: `presentation` bir uç nokta, `domain` bir use case ve
bir tip kaybeder. Yeni bağımlılık doğmaz, hiçbir dosya katman değiştirmez. Kompozisyon kökü
(`main.py`) arama bilmiyordu, dokunulmaz.

Tek feature kuralı korunur: `workspace` hâlâ tek feature'dır.

## 4 · Kabul ölçütü

1. `queenagent/` altında `SearchPanel`, `useSearch`, `Hit`, `/api/search` araması sonuç vermez.
2. Kenar çubuğunda ad ile "New chat" arasında hiçbir öge yoktur.
3. ⌘K/Ctrl+K hiçbir şey yapmaz; Esc yalnız açık dosya panelini kapatır.
4. `python -m pytest queenagent` ve `npm test --prefix queenagent/frontend` yeşil.
5. Ölü yorum kalmaz: `queenagent/` içinde aramaya atıf yapan tek bir yorum ya da belge cümlesi yoktur.

## 5 · Risk

Arama, `App.jsx`'in klavye dinleyicisini ve panel kapatma sırasını paylaşıyor. Sökerken **dosya
panelinin Esc ile kapanması bozulabilir** — bu davranışın testi zaten var ve yeşil kalmak zorunda;
kırmızıya dönerse söküm fazla derin gitmiş demektir.
