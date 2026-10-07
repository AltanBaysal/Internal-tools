# Madde 344 — ChatScreen.jsx bölünür · test turu

**Kaynak:** [yol haritasının 344'ü (v9-12)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); bugünkü
kodun üstüne kurulur. Dalga 2'nin 347, 348 ve 349'u bu parçanın dosyalarının üstüne kurulur.

**Kullanıcıdan gereken:** hiçbir şey. Madde bir taşıma: ekran ve davranış değişmiyor, ve karar
verilecek bir davranış yok.

## Ne kanıtlanacak

`ChatScreen.jsx` 636 satır, ve v9'un dokuz parçası ona dokunuyor. FOUNDATION'ın 4. ilkesi: bağlamda
rahatça tutulamayacak kadar büyük bir dosya fazla iş yapıyor — bölünür. Dosyada ekranın kendisinden
önce mesajı çizen sekiz bileşen var: `ToolCalls`, `Stamp`, `LiveStrip`, `EditMessage`, `Versions`,
`MessageFoot`, `CreatingFile`, `FileCard`. *Bitti sayılır*: ekran önceki gibi, testler yeşil;
`ChatScreen.jsx`'te ekranın kendisi kalıyor, mesajın parçaları kendi dosyalarında.

## Dosyalar nasıl gruplanır

Üç yol düşünüldü:

1. **Birlikte olanlar bir dosyada, beş dosya** — seçilen. Klasörün düzeni bir dosyada bir bileşen,
   ve `FileRail.jsx` yanında bir yardımcıyı adıyla dışa veriyor (`RefreshFiles`); yani bir parça başka
   bir parçaya ait olduğunda aynı dosyada durabiliyor.
2. Her bileşene bir dosya, sekiz dosya. `Versions` yalnız `MessageFoot`'un içinde çiziliyor;
   `LiveStrip` `Stamp`'in yerinde ve onun sınıfıyla duruyor, sayıyı kısaltan kuralı onunla paylaşıyor;
   `CreatingFile` doğmak üzere olan `FileCard`'ın iskeleti. Ayrı dosyalar bu bağları dosyalar arası
   importlara çevirir.
3. Hepsi tek bir `Message.jsx`'te. 300 satırlık yeni bir dosya — bölmenin sebebini yeniden kurar.

Beş dosya:

| Dosya | Varsayılan | Adıyla | Dosyada kalan yardımcı |
|---|---|---|---|
| `ToolCalls.jsx` | `ToolCalls` | — | `headOf` |
| `Stamp.jsx` | `Stamp` | `LiveStrip` | `shorten`, `WORDS`, `WORD_MS` |
| `MessageFoot.jsx` | `MessageFoot` | — | `Versions` |
| `EditMessage.jsx` | `EditMessage` | — | — |
| `FileCard.jsx` | `FileCard` | `CreatingFile` | `extensionOf`, `CHIP_LENGTH` |

## Testler ne tutar, ne tutmaz

**Tutar:**

- **Her yeni dosyanın yanında kendi testi** (`<ad>.test.jsx`, klasörün düzeni), bileşeni yeni
  evinden import edip tek başına çizer. Her birinde, ekranda bugün çizdiğini tek başına da çizdiğini
  gösteren birkaç iddia:

  | Dosya | İddialar |
  |---|---|
  | `ToolCalls.test.jsx` | çağrı yoksa hiçbir şey çizilmez; kapalı kapı adımları sayar, açınca her çağrı `⏺ araç(hedef)` ve sonucuyla listelenir; süren turda kapalı kapı son çağrıyı söyler |
  | `Stamp.test.jsx` | zaman yoksa damga yok; bir cevabın damgası saati ve harcadığını (`1.2k tokens`) söyler; harcama sıfırsa yalnız saat; `LiveStrip` turu ve token sayısını söyler |
  | `MessageFoot.test.jsx` | kalem de sürüm de yoksa satır yok; kalem `onEdit`'i çağırır; sürüm okları yanındaki sürümü `onVersion`'a verir, ilk sürümde geri oku kapalı |
  | `EditMessage.test.jsx` | Enter kırpılmış taslağı `onConfirm`'e verir; Escape `onCancel`'ı çağırır; boş taslakta onay kapalı |
  | `FileCard.test.jsx` | kart çipi, adı ve `✓ saved to project`'i gösterir, basınca adı `onOpen`'a verir; açık kart `open` der; `CreatingFile` `creating file…` der |

- **`ChatScreen.jsx` mesajın parçalarını artık kendisi tanımlamaz:** `ChatScreen.test.jsx`'e bir
  kilit — dosya diskten okunur (`workspace.css.test.js`'in yolu), ve sekiz adın hiçbiri orada
  `function <ad>` olarak geçmez. Kilit dosyanın başında, iki düzen testinin hemen altında durur: aynı
  dalgada üç parça aynı test dosyasının sonuna yazıyor.

**Tutmaz:**

- **Ekranın davranışını yeniden tutmaz.** `ChatScreen.test.jsx`'in bugünkü testleri ekranı çizip
  davranışa bakıyor, ve taşımadan sonra aynı davranışı test etmeye devam ediyor; hiçbiri taşınmaz ve
  değişmez. Taşıma bir sınıf adını, bir yazıyı ya da bir davranışı değiştirirse onlar kırmızı olur.
- Yeni test dosyaları bileşenin her dalını tutmaz: o dallar ekranın testlerinde zaten tutuluyor.
  Yeni dosyalar bileşenin yeni evinden tek başına çizildiğini gösterir.
- **Ekranın görünüşünü tutmaz:** jsdom stil çizmiyor. `workspace.css` bölünmüyor *(kullanıcının
  kararı)*, ve sınıf adları değişmediği için ekran aynı görünür; bu, birleştikten sonra tarayıcıda
  görülür.

## Bu turda yazılmayanlar

- **`ChatScreen.jsx` değişmez, beş dosya yazılmaz:** uygulama turunda.
- **`dist` derlenmez:** yürütücü birleştirirken bir kez derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` kırmızı verir: beş yeni test
dosyası, import ettikleri dosya olmadığı için açılamadan düşer; kilit, sekiz ad `ChatScreen.jsx`'te
durduğu için kırmızı. Öteki 652 test yeşil kalır. queen-editor'ün arka ucu 377'nin bilinen iki
kırmızısıyla kalır; öteki iki süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m344-chatscreen-bolunur-testler-plan.md).
