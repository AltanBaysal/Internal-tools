# Mira — Faz 13: Arama (Madde 28)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 12](2026-08-09-mira-faz-12-ad-design.md)

**Kapsam:** ⌘K / Ctrl+K ile açılıp kapanan arama paneli; proje adı, sohbet başlığı, dosya adı **ve
dosya içeriği**; en fazla 8 sonuç; her satırda mono tür çipi; Esc sıralaması.
**Kapsam dışı:** bulanık (fuzzy) eşleşme · eşleşen satırın kesiti · arama indeksi.

---

## 1 · Arama sunucuda olur

`GET /api/search?q=<query>` → en fazla 8 satır.

Tarayıcıda yapılamaz: **dosyaların içeriği diskte** ve hiçbir ekran onları toptan indirmiyor. Aramayı
tarayıcıya taşımak, tüm projelerin tüm dosyalarını her açılışta indirmek demek olurdu.

**Eşleşme:** büyük/küçük harf duymayan alt dize. Bulanık eşleşme yok — v1'de bir kelimeyi arayan
kullanıcı o kelimeyi yazıyor. Boş sorgu boş liste döner; sunucu diski hiç okumaz.

**Maliyet.** İçerik araması her projenin her dosyasını okur. Yerelde onlarca dosya için bu hiçbir şey;
yavaşladığı gün cevabı bir indekstir ve o indeks bugün yazılmaz (YAGNI). Bu kararın bedeli
ölçülebilir olsun diye burada yazılı.

## 2 · Sıra ve sayı

Satırlar **sabit bir grup sırasıyla** gelir: **proje → sohbet → dosya adı → dosya içeriği.** Ad
eşleşmesi içerik eşleşmesinden güçlü bir cevaptır. Grup içinde sıra, o şeyin uygulamada zaten
göründüğü sıradır — projeler kenar çubuğundaki gibi (eskiden yeniye), sohbetler son harekete göre,
dosyalar `mtime`'a göre. Arama kendine ikinci bir sıralama uydurmuyor.

Toplam **8**'de kesilir. Kesilen satır sessizce düşer — tasarımda "daha fazla" diye bir şey yok.
Aynı dosya hem adıyla hem içeriğiyle eşleşirse **bir kez** görünür: ad grubunda.

## 3 · Satırda ne yazar

| Alan | Proje | Sohbet | Dosya |
|---|---|---|---|
| çip (mono) | `project` | `chat` | `file` |
| etiket | proje adı | sohbet başlığı | dosya adı |
| alt satır | — | projenin adı | projenin adı |

**Alt satır neden var?** Sekiz sonuç birden çok projeden gelebiliyor; "bu hangi projede" sorusu
tıklamadan önce sorulur.

**İçerik eşleşmesinin kesiti gösterilmiyor.** Tasarımda böyle bir satır yok ve uydurmak, bulunan
yerin bağlamını doğru kırpma sözü vermek olurdu. Dosya açıldığında metnin tamamı zaten panelde.

## 4 · Tıklayınca ne olur

- **proje** → `/p/<id>`
- **sohbet** → `/p/<pid>/c/<cid>`
- **dosya** → `/p/<pid>` ve dosya panelde açılır

Her durumda arama kapanır.

## 5 · Klavye: tek sahip

**Esc ve ⌘K'nın tek bir sahibi var: `App`.** Tek bir `keydown` dinleyicisi karar verir:

1. ⌘K / Ctrl+K → aramayı açar-kapar.
2. Esc → arama açıksa **aramayı** kapatır; değilse açık dosya panelini kapatır; ikisi de yoksa hiçbir
   şey. **Asla geri gitmez.**

Faz 10'da Esc dinleyicisi `FilePanel`'in içindeydi. İki ayrı dinleyici aynı `window` olayında
sıraya giremez (`stopPropagation` kardeş dinleyiciyi durdurmaz), o yüzden dinleyici tek yere taşınıyor
ve `FilePanel`'de yalnız `←` düğmesi kalıyor. Bu, tasarımın "önce arama, sonra panel" cümlesinin
doğrudan karşılığı.

## 6 · Panel

- Girdi açılışta **otomatik odaklanır**.
- Kenar çubuğundaki **Search** düğmesi de aynı paneli açar (bugüne kadar hiçbir şey açmıyordu).
- Sonuç yoksa **"No results."**; sorgu boşken hiçbir şey yazmaz (henüz arama yapılmadı).
- **Sıra dışı yanıtlar yok sayılır.** Her tuşta bir istek gider; geç dönen eski bir yanıt yeni
  sonuçların üstüne yazmaz. Gecikmeli tetikleme (debounce) yok: yerel sunucuda beklemek, sonucu
  geciktirmekten başka bir şey yapmaz.

## 7 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain | `Hit(kind, label, project_id, project_name, chat_id, file_name)` |
| domain/usecases | `search(project_store, chat_store, file_store, query, limit=8)` |
| presentation | `GET /api/search` |
| frontend | `useSearch.js` · `SearchPanel.jsx` · `App` klavyenin tek sahibi · `Sidebar` düğmesi bağlanır |

`search` üç deponun üçünü birden okur; bu, `workspace`'in tek bir özellik olmasının aynı gerekçesi —
arama bir özellik değil, bu özelliğin bir kullanım hâli.

## 8 · Testler

1. Boş sorgu boş liste; disk okunmuyor.
2. Proje adı, sohbet başlığı ve dosya adı eşleşiyor; büyük/küçük harf duymuyor.
3. Dosya **içeriği** eşleşiyor ve satır `file` çipiyle geliyor.
4. Ad ve içerik birden eşleşen dosya bir kez görünüyor.
5. Sıra: proje, sohbet, dosya adı, dosya içeriği.
6. En fazla 8 satır dönüyor.
7. Her satır tıklanacak adresi taşıyor (`projectId`, gerekiyorsa `chatId` / `fileName`).
8. Ön yüz: ⌘K açar, tekrar basınca kapatır; girdi odaklanır.
9. Ön yüz: Esc önce aramayı, sonra paneli kapatır.
10. Ön yüz: sonuç yokken "No results."; sorgu boşken hiçbir şey.
11. Ön yüz: dosya sonucuna tıklayınca proje ekranı açılıyor ve dosya panelde.

## 9 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda: bir dosyanın içindeki kelimeyi ara → dosya sonuçlarda; tıkla →
proje ekranı açılır ve dosya panelde görünür. Panel açıkken Esc'e iki kez bas → önce arama, sonra
panel kapanır.
