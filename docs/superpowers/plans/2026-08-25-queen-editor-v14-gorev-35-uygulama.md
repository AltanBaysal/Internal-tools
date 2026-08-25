# v14 Görev 35 — Yazılmış ama gönderilmemiş metin geri dönüşte duruyor: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in iki kırmızı testini yeşile döndürmek, iki tutucuyu yeşil bırakarak.

**Architecture:** İki dosya. `GeneratePanel.jsx` modül seviyesinde proje anahtarlı bir taslak deposu,
onu mount'ta bir kez okuyan bir fonksiyon ve değişimi yazan bir effect kazanıyor; `SidePanel.jsx` tek
bir prop satırı ekliyor.

**Tech Stack:** React 18, Vite, Vitest + jsdom.

**Spec:** [Görev 35 uygulama spec'i](../specs/2026-08-25-queen-editor-v14-gorev-35-uygulama-design.md)

## Global Constraints

- **Test dosyası değişmiyor.** `GeneratePanel.test.jsx` bir önceki commit'te ne yazıldıysa o kalır.
- **Depo proje anahtarlı** ve **bellekte** — diske hiçbir şey yazılmıyor.
- **Depo render sırasında okunmuyor** — tembel bir `useState` içinde, mount'ta bir kez.
- **Yazma tek effect'te**, dört setter'ın içinde değil.
- **`shownProject` benzeri bir ref eklenmiyor** — gerekçesi spec'te.
- Dil: kod ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- Test: `npm test --prefix queen-editor/frontend` · Derleme:
  `npm run build --prefix queen-editor/frontend` · **`dist` aynı commit'e girer.**

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx` | fotoğraf üret formu ve dört kutusu | depo + okuyan fonksiyon + yazan effect + yeni prop |
| `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx` | sağ sütun ve açık panel | tek satır: `project` prop'unu geçir |

Depo, onu okuyan tek bileşenin yanında duruyor — `SidePanel`'in `REMEMBERED`'ı, `useKeptScroll`'un
`KEPT`'i ve `useModels`'in yuvası da öyle. Ayrı bir modüle çıkarmak, tek tüketicisi olan bir şeyi
paylaşılıyor gibi göstermek olurdu.

---

### Task 1: Taslak deposu, mount'taki okuma ve yazan effect

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx:49-60`

**Interfaces:**
- Consumes: dosyanın 1. satırında zaten içe aktarılmış olan `useEffect`, `useRef`, `useState`; ve
  dosyada zaten duran `FIRST_VARIANTS` sabiti (`"2"`).
- Produces: `GeneratePanel` artık `project` adında bir prop okuyor (dize; proje adı). Modül içinde
  `REMEMBERED` (`Map`) ve `opening(project, settings)` doğuyor; ikisi de dışa açılmıyor.

- [ ] **Step 1: Depoyu ve okuyan fonksiyonu yaz**

`CONFIRM_MS` sabitinin **altına**, `acceptsVariants` fonksiyonunun **üstüne**:

```jsx
// What each project's boxes were last holding. Opening a frame's detail replaces the whole project
// screen, so this panel is torn down and built again on every step in and out; without this the
// boxes would come back on what was last sent, and everything typed since would be gone (madde 35).
// Keyed by project: half-written work belongs to one project, never to the app.
//
// Memory only, like the seven stores before it: a reload fills the boxes from the record again.
const REMEMBERED = new Map();

/** What the four boxes open with.
 *
 * A draft the user left behind wins over the project's record. The record is only written when the
 * queue button is pressed, so a draft is by definition the newer of the two -- it is exactly what
 * was typed after the last send.
 *
 * This is also the one place the record's shape becomes the boxes' shape: the boxes carry text, the
 * record carries a number that may be null and a model that may be empty.
 */
function opening(project, settings) {
  const draft = REMEMBERED.get(project);
  if (draft) return draft;
  return {
    prompts: settings.prompts,
    negative: settings.negative,
    model: settings.model || "",
    variants: settings.variants === null ? FIRST_VARIANTS : String(settings.variants),
  };
}
```

- [ ] **Step 2: Prop listesine `project`'i ekle**

Bugünkü imza:

```jsx
export default function GeneratePanel({ job, error, errorField, busyElsewhere, settings,
                                        models = null, modelsError = null, producer = null,
                                        onGenerate, onClearError, onInstall }) {
```

Yerine — `settings`'in hemen ardına, çünkü ikisi birlikte kutuları dolduruyor:

```jsx
export default function GeneratePanel({ job, error, errorField, busyElsewhere, settings, project,
                                        models = null, modelsError = null, producer = null,
                                        onGenerate, onClearError, onInstall }) {
```

- [ ] **Step 3: Dört kutuyu tek okumadan tohumla**

Bugünkü hâli (49–60. satırların gövde kısmı):

```jsx
  // Initial values only: the screen mounts after the settings have loaded, so there is nothing to
  // sync afterwards and typing is never overwritten.
  const [prompts, setPrompts] = useState(settings.prompts);
  const [negative, setNegative] = useState(settings.negative);
  const [model, setModel] = useState(settings.model || "");
  // Text, not a number: the field has to survive being cleared while typing.
  const [variants, setVariants] = useState(
    settings.variants === null ? FIRST_VARIANTS : String(settings.variants),
  );
```

Yerine:

```jsx
  // Read at mount and never again: the store lives at module level, and asking it on every render
  // would make the render itself impure. One question, four answers.
  const [boxes] = useState(() => opening(project, settings));
  // Initial values only: nothing is synced afterwards, so typing is never overwritten. The boxes
  // all carry text -- the variant one has to survive being cleared while it is typed in.
  const [prompts, setPrompts] = useState(boxes.prompts);
  const [negative, setNegative] = useState(boxes.negative);
  const [model, setModel] = useState(boxes.model);
  const [variants, setVariants] = useState(boxes.variants);
```

Yorumun eski hâlindeki "the screen mounts after the settings have loaded" cümlesi gidiyor: madde
31'den beri panel kaydı beklemeden değil, kaydı gelene kadar `SidePanel`'in halkasının ardında
duruyor — cümle bugün için doğru ama söylediği şey artık bu satırların sebebi değil.

- [ ] **Step 4: Yazan effect'i ekle**

`useEffect(() => () => clearTimeout(fade.current), []);` satırının **altına**:

```jsx
  // Whatever the boxes hold is what a later mount starts from. One effect rather than a write in
  // each of the four setters: the model box has a second writer -- it fills itself from the
  // renderer's list when nothing was saved -- and a store written in five places would be five
  // chances to forget one.
  useEffect(() => {
    REMEMBERED.set(project, { prompts, negative, model, variants });
  }, [project, prompts, negative, model, variants]);
```

Mount'ta da bir kez yazıyor ve bu zararsız: o an taslak, kutuların kayıttan aldığı değerin aynısı.

- [ ] **Step 5: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`

Expected: `GeneratePanel.test.jsx` **33 tests, 0 failed.**

Takımın kalanında **`SidePanel.test.jsx`'in düşmesi beklenmiyor** — o dosyanın yardımcısı
`project="düğün"` zaten geçiriyor, ve panel henüz `SidePanel`'den bir şey almadığı için `project`
`undefined` olsa bile depo tek anahtar altında çalışırdı. Yine de bir düşen olursa Task 2'ye
geçmeden dur ve oku.

- [ ] **Step 6: Commit yok**

Bu görev tek başına commit edilmiyor: sütun prop'u geçirmeden özellik yarım kalır. Task 2 ile tek
commit'e girer.

---

### Task 2: Sütun projeyi panele geçirsin, derle ve commit'le

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx:170-175`

**Interfaces:**
- Consumes: Task 1'in eklediği `project` prop'u. `SidePanel` bu değeri bugün zaten prop olarak
  alıyor (imzasında `project` var) ve `QueuePanel`'e zaten veriyor.
- Produces: dışarıya bir şey değil. `SidePanel`'in kendi prop listesi değişmiyor.

- [ ] **Step 1: Prop'u geçir**

Bugünkü hâli:

```jsx
          <GeneratePanel job={job} error={error} errorField={errorField}
                         busyElsewhere={busyElsewhere} settings={settings}
                         models={models} modelsError={modelsError}
                         producer={(producers?.producers || []).find((p) => p.id === "photo")}
                         onGenerate={onGenerate} onClearError={onClearError}
                         onInstall={producers?.install} />
```

Yerine — tek fark `project`:

```jsx
          <GeneratePanel job={job} error={error} errorField={errorField}
                         busyElsewhere={busyElsewhere} settings={settings} project={project}
                         models={models} modelsError={modelsError}
                         producer={(producers?.producers || []).find((p) => p.id === "photo")}
                         onGenerate={onGenerate} onClearError={onClearError}
                         onInstall={producers?.install} />
```

`GeneratePanel`'i çizen tek yer burası — başka bir çağrı yeri yok.

- [ ] **Step 2: Takımın tamamen yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed**, 579 tests.

- [ ] **Step 3: Ön yüzü derle**

Run: `npm run build --prefix queen-editor/frontend`

Expected: hatasız biter ve `queen-editor/frontend/dist/` tazelenir.

- [ ] **Step 4: Arka yüz takımının da yeşil olduğunu gör**

Run: `python -m pytest queen-editor -q`

Expected: **711 passed.** Bu döngü arka yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 5: Yol haritasını işaretle**

Modify: `docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md`

35. maddenin satırındaki iş adının başına `✅ ` ekle — 33 ve 34'ün satırlarındaki biçimin aynısı:

```
| 35 | ✅ **Yazılmış ama gönderilmemiş metin geri dönüşte duruyor.** …
```

Aynı belgenin başlığındaki ilerleme sayısını da bir artır: `32/34` yazan yer `33/34` olur.

**Not:** Madde bu adımda kodda bitiyor ama turda bitmiyor — 30. maddenin Colab turu onu görecek. 34
için de aynısı yapılmıştı.

- [ ] **Step 6: Colab turu listesine satır ekle**

Modify: `docs/superpowers/plans/2026-08-24-queen-editor-v14-colab-turu.md`

31–34 için satır taşıyan tabloya 35'in satırını, aynı biçimde ekle. Denenecek şey: fotoğraf üret
panelinin bir kutusuna bir şey yaz, göndermeden bir kare aç ve geri dön; yazdığın kutuda durmalı.

- [ ] **Step 7: Değişen her şeyi gör**

Run: `git status --short`

Expected: `GeneratePanel.jsx`, `SidePanel.jsx`, `dist/` altındakiler, `docs/superpowers` altındaki
iki yeni belge ve iki değişen belge. `GeneratePanel.test.jsx` bu listede **olmamalı.**

- [ ] **Step 8: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the form comes back holding what was typed into it

Typing into the photo form and then looking at a frame cost the text. The boxes
were seeded from the project record at mount and the record is written only
when the queue button is pressed, so everything typed since the last send lived
in component state alone -- and the address swaps the whole screen, which is
React dropping the state of a component that no longer exists.

The four boxes now open on this project's draft when there is one, and on the
record when there is not. The draft wins because it is the newer of the two by
definition: the record is what was last sent, the draft is what was typed
after.

One form, one loss, so all four boxes travel together. Remembering the prompt
and forgetting the negative, the model and the count under it would be
remembering half of an unfinished piece of work.

Read once at mount, inside a lazy initializer -- the store lives at module
level and asking it on every render would make the render impure. That one read
is also where the record's shape becomes the boxes': they carry text, it
carries a count that may be null and a model that may be empty.

Written by one effect rather than by the four setters. The model box has a
second writer, the one that fills an empty box from the renderer's list, and a
store written in five places would be five chances to forget one.

Nothing is cleared after a send: at that moment the draft and the record hold
the same text.

Keyed by project, so a half-written prompt never appears in another one. Memory
only, like the seven stores before it -- a reload fills the boxes from the
record again. This is the eighth, and the last of the five items the tour
opened.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Depo modül seviyesinde, proje anahtarlı | Task 1 Step 1 |
| Taslak kaydı yeniyor | Task 1 Step 1'in `opening()` fonksiyonu ve yorumu |
| Tek okuma, dört kutu | Task 1 Step 3 |
| Normalleştirme tek yerde | Task 1 Step 1 |
| Yazan taraf tek effect | Task 1 Step 4 |
| Gönderdikten sonra silinmiyor | Commit mesajı — koda bir şey eklenmiyor, eklenmemesi kararın kendisi |
| Yeni prop `project` | Task 1 Step 2 ve Task 2 Step 1 |
| Ömür bellek kadar | Task 1 Step 1'in yorumu |
| `shownProject` ref'i yok | Global Constraints |
| Test dosyası değişmiyor | Global Constraints, Task 2 Step 7 |
| Derlenmiş çıktı aynı commit'te | Task 2 Step 3 ve Step 8 |

Spec'te olup planda karşılığı olmayan madde yok. Yol haritası ve Colab turu adımları spec'te değil,
CLAUDE.md'nin numaralandırma ve tur kuralından geliyor.

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var; beklenen sayılar (33,
579, 711) yazılı.

**Ad tutarlılığı:** `REMEMBERED` ve `opening()` iki görevde de aynı yazımla geçiyor. `opening()` adı
`SidePanel` ve `useProjectSettings`'teki aynı işi yapan fonksiyonlarla bilerek aynı; üçü ayrı modülde
durduğu için çakışmıyorlar ve okuyanın üçünü bir kalıp olarak görmesini sağlıyor. `boxes` adı yalnız
bu bileşende geçiyor ve `FIRST_VARIANTS` ile karışmıyor.

**Bilerek dışarıda:** `LayerPanel` ve `PhotoDetail`. Kutuları var ama madde 35 fotoğraf panelini
söylüyor, ve detayın kuralı (madde 76) bilerek başka.
