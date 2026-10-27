# Madde 344 — ChatScreen.jsx bölünür · uygulama turu

**Kaynak:** [yol haritasının 344'ü (v9-12)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m344-chatscreen-bolunur-testler-design.md) ve onun
kırmızı commit'i.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne yapılır

Mesajı çizen sekiz bileşen `ChatScreen.jsx`'ten, test turunun seçtiği beş dosyaya **taşınır**. Taşıma
saf: bir işaret, bir sınıf adı, bir yazı, bir davranış değişmez. Her bileşenin gövdesi ve yorumu
olduğu gibi gider; değişen yalnız `export` sözleri ve her dosyanın kendi importları.

| Yeni dosya | Taşınanlar (bugünkü `ChatScreen.jsx` satırları) | Import |
|---|---|---|
| `ToolCalls.jsx` | `headOf` (26–32), `ToolCalls` (34–76) — varsayılan | `useState` |
| `Stamp.jsx` | `shorten` (78–82), `Stamp` (84–100) — varsayılan, `WORDS`, `WORD_MS`, `LiveStrip` (102–153) — adıyla | `useEffect`, `useState`, `clockTime` |
| `EditMessage.jsx` | `EditMessage` (157–210) — varsayılan | `useState` |
| `MessageFoot.jsx` | `Versions` (212–245), `MessageFoot` (247–275) — varsayılan | — |
| `FileCard.jsx` | `CHIP_LENGTH` (14), `extensionOf` (19–24), `CreatingFile` (277–284) — adıyla, `FileCard` (286–302) — varsayılan | — |

**Tek yer değiştirme:** bugün 155–156. satırlardaki yorum — *"The skeleton of the card about to be
born…"* — `EditMessage`'ın üstünde duruyor, ama `CreatingFile`'ı anlatıyor. `CreatingFile`'la birlikte
taşınır ve onun üstüne girer. Yorumun sözü değişmez.

**`ChatScreen.jsx`'te kalan:** `STICK_WITHIN` ve yorumu, ekranın kendisi, ve importlar. `clockTime`
importu çıkar (yalnız `Stamp` kullanıyordu); beş yeni import mevcut sıraya, yola göre alfabetik
girer. `ChatScreen` fonksiyonunun gövdesine dokunulmaz: aynı dalgada üç parça (341'in `caret`'i, 343'ün
göstergesi, 336'nın model seçicisi) o gövdeye yazıyor, ve yürütücü onların değişikliklerini
birleştirirken taşır. Dosya 636 satırdan 350 civarına iner.

## Neden böyle

- **Gruplar test turunun kararı:** birlikte çizilen, birlikte duran — `Versions` yalnız
  `MessageFoot`'un içinde, `LiveStrip` `Stamp`'in yerinde ve `shorten`'ını paylaşıyor, `CreatingFile`
  `FileCard`'ın iskeleti. `FileRail.jsx` + `RefreshFiles` klasörde aynı düzen.
- **Kod baytı baytına aynı:** dalga 2'nin 347, 348 ve 349'u bu dosyaların üstüne kurulur; taşıma
  sırasında bir satırın değişmesi, birleştirmede kimin değişikliği olduğunu okunmaz yapar.
- **CODE-STANDARD:** yeni dosyalar `features/workspace/`'te, yani çizdikleri özelliğin içinde; hiçbiri
  bir özellik import etmiyor, `Stamp.jsx` yalnız `shared/time.js`'i. CODE-STANDARD'ın tabloları
  deponun dosyalarını sayıyor, ön ucun bileşenlerini değil — güncellenecek tablo yok. Hiçbir belge bu
  bileşenleri adıyla anmıyor.
- **`workspace.css` değişmez** *(kullanıcının kararı)*.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` yeşil: 652 eski test ve 17 yeni
(16'sı beş dosyada, biri kilit). queen-editor'ün arka ucu 377'nin bilinen iki kırmızısıyla kalır.
`dist` derlenmez: yürütücü birleştirirken derler. Tarayıcıda sohbet ekranı önceki gibi görünür.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m344-chatscreen-bolunur-uygulama-plan.md).
