# Madde 1 — Mira → QueenAgent · Tasarım Belgesi

**Tarih:** 2026-08-16 · **Yol haritası:**
[QueenAgent v2](../plans/2026-08-15-queenagent-v2-roadmap.md), Faz 0 · Madde 1

**Amaç:** ürünün adını dört katmanda birden değiştirmek — klasör, ortam değişkeni, belgeler, arayüz
ve model yönergesi. Bu madde **yalnız ad değiştirir**; hiçbir davranışa, hiçbir ölçüye, hiçbir
ekrana dokunmaz.

---

## 1 · Verilen karar

**Veri göçü yok.** `QUEENAGENT_ROOT` yoksa varsayılan `~/QueenAgent` olur; eski `~/Mira` klasörü
diskte kalır ve uygulama ona bakmaz. Kodda göç mantığı, yedek değişken ya da uyarı **doğmaz**.
Gerekçe: kullanıcının bugünkü kökündeki veri test verisidir ve korunması istenmiyor.

Bunun görünür sonucu: madde bittikten sonra uygulama boş bir çalışma alanıyla açılır. Beklenen
budur, hata değildir.

## 2 · Ne değişiyor

### 2.1 · Klasör

`mira/` → `queenagent/`. Taşıma `git mv` ile yapılır ki geçmiş korunsun.

### 2.2 · Ortam değişkeni ve varsayılan kök

`queenagent/backend/config.py`:

- `MIRA_ROOT` → `QUEENAGENT_ROOT`
- varsayılan `~/Mira` → `~/QueenAgent`

Bu dosyadaki başka hiçbir değer değişmez — `PORT = 8100`, `HOST`, `XAI_*` aynı kalır. Port
queen-editor'ün 8000'iyle çakışmadığı için dokunulmaz.

### 2.3 · Arayüz metinleri

Kullanıcının gördüğü her cümlede ad değişir. Tam liste:

| Yer | Bugün | Sonra |
|---|---|---|
| `Sidebar.jsx` | kelime markası `Mira` | `QueenAgent` |
| `ChatScreen.jsx` (3 yer) | mesaj etiketi `Mira` | `QueenAgent` |
| `FileRail.jsx` | "…send a message and **Mira** will create one." | `QueenAgent` |
| `HomeScreen.jsx` | "Ask anything — **Mira** saves the answer…" | `QueenAgent` |
| `OfflineStrip.jsx` | "…**Mira** will answer when the connection is back." | `QueenAgent` |
| `ProjectScreen.jsx` (2 yer) | "Files **Mira** created", "…**Mira** will create one." | `QueenAgent` |
| `index.html` | `<title>Mira</title>` | `QueenAgent` |
| `workspace.css` | yorum satırındaki `Mira's turn` | `QueenAgent's turn` |

**Yalnız ad değişir.** Etiketin büyük harfe dönmesi (`QUEENAGENT · saat`) Madde 15'in,
"You" etiketinin kalkması yine Madde 15'in, Home yer tutucusunun tümüyle silinmesi Madde 3'ün işidir
— burada hiçbiri yapılmaz.

### 2.4 · Model yönergesi ve araç açıklamaları

- `domain/prompt.py`: `"You are Mira, a small AI workspace…"` → `"You are QueenAgent, …"`; dosyanın
  docstring'i de.
- `domain/tools.py`: docstring'deki `Mira` → `QueenAgent`.

### 2.5 · Paket adı

`frontend/package.json` ve `package-lock.json`: `mira-frontend` → `queenagent-frontend`.

### 2.6 · Belgeler

Dört belge yeniden yazılır — bunlar **bugünü** anlatır, kayıt değildir:

- `queenagent/README.md` — başlık, çalıştırma komutları (`mira/` yolları), değişken tablosu
  (`MIRA_ROOT` → `QUEENAGENT_ROOT`, varsayılan `QueenAgent`), test komutları. "Ne yapılacak"
  bağlantısı v1 yol haritası yerine **v2 yol haritasını** gösterir.
- `queenagent/FOUNDATION.md` — başlık; 5. karardaki `MIRA_ROOT`; 7. karardaki "Mira inherits".
- `queenagent/CODE-STANDARD.md` — başlık; bağımsızlık paragrafı; mağaza tablosundaki "what did Mira
  produce"; tasarım paragrafı; dil paragrafı; test paragrafındaki `mira/` ve `mira/frontend/`
  yolları.
- `CLAUDE.md` — Mira bölümünün başlığı ve gövdesi; `python mira/main.py` komutu; belge bağlantıları.

### 2.7 · Testler

Ad geçen testler yeni adı bekler: `ChatScreen.test.jsx` (2 yer), `ProjectScreen.test.jsx`,
`test_store.py`'deki geçici klasör adı (`mira-root` → `queenagent-root`).

## 3 · Ne değişmiyor

- **Tarihî belgeler.** `docs/superpowers/` altındaki v1 spec'leri, v1 planları, fark araştırmaları
  ve kararlar belgesi **olduğu gibi kalır**. Onlar o gün ne olduğunun kaydıdır; adı değiştirmek
  kaydı bozar. Yol haritasının kabul ölçütü de bunu söylüyor: repoda `mira` araması yalnız tarihî
  belgelerde sonuç verir.
- **Branch adı** `fix/mira` — koşu sürerken dal adını değiştirmek açık işi böler; dokunulmaz.
- **Kullanıcı verisi.** Diskteki hiçbir proje, sohbet ya da dosya okunmaz, taşınmaz, silinmez.
- **Davranış.** Tek bir kural, ölçü, renk ya da akış değişmez.
- **`.claude/` ayarları** — `mira` geçmiyor, izin listesi kırılmıyor.
- **`pytest.ini`** — ad geçmiyor.

## 4 · Katman denetimi

`FOUNDATION.md` ve `CODE-STANDARD.md` bu maddede **içerik olarak** güncelleniyor ama **kural olarak**
değişmiyor: hiçbir dosya katman değiştirmiyor, hiçbir yeni bağımlılık doğmuyor, kompozisyon kökü
(`main.py`) aynı sınıfları aynı yerde bağlamayı sürdürüyor. Bağımlılık yönü ve üç yasak aynen
geçerli.

Tek dikkat: `config.py` hâlâ **kökün adını tek yerde tutan** dosyadır (`FOUNDATION.md` 5. karar).
Yeni değişken adı başka hiçbir dosyada geçmez.

## 5 · Kabul ölçütü

1. `queenagent/` altında `Mira`, `MIRA`, `mira` araması **sonuç vermez**.
2. `docs/superpowers/` altında arama yalnız **tarihî** belgelerde sonuç verir; v2 yol haritası ve bu
   spec yeni adı kullanır.
3. `CLAUDE.md`'de Mira geçmez.
4. `python -m pytest queenagent` yeşil; `npm test --prefix queenagent/frontend` yeşil.
5. Uygulama açılır, kenar çubuğunda `QueenAgent` yazar, çalışma alanı boştur.

## 6 · Risk

Klasör taşıma repodaki hemen her yola dokunur. Bu madde **tek başına**, aynı branch'te başka bir
oturum çalışmıyorken koşulur; commit'i de tek parça atılır ki geri alınması kolay olsun.
