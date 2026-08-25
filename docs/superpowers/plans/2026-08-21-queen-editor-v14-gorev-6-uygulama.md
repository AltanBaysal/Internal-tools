# v14 Görev 6 — Tahmin ve onay metinleri moda göre değişiyor: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı on testi yeşile döndürmek: tahmin ve yeşil onay seçilen
modun kelimeleriyle yazsın, kapsamda o katmanı taşıyan kare varsa uyarı modun kuyruğunun yerine
geçsin.

**Architecture:** Tek dosya. İki sözlük (katmanın kelimeleri, modun kelimeleri) ve onları birleştiren
üç satırlık bir hesap; onayın durumu sayıdan sayı-artı-moda genişliyor.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-6-mod-metinleri-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- **`owed` değişmiyor.** Bağlı modda motorun atladığı kare panelde yeniden hesaplanmıyor; sebebi
  uygulama spec'inde ve test turunun 5. kararında.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/LayerPanel.jsx` | iki sözlük, cümle, onayın durumu | `WORDS.held`, `MODE_WORDS`, cümle, `added` |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Katmanın ve modun kelimeleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Produces: `WORDS[layer].held` (string) ve `MODE_WORDS[id] -> { noun, tail } | undefined`. Task 2
  ikisini de okuyor.

- [ ] **Step 1: `WORDS`'e `held` ekle**

Video bloğunda `own`'ın altına:

```jsx
    // The adjective for a frame that already carries this layer. Only the copy warning needs it,
    // and the two panels say it differently enough that neither can be built from the other.
    held: "videolu",
```

Ses bloğunda, `own: "sesini",`'in altına:

```jsx
    held: "sesi olan",
```

- [ ] **Step 2: `MODE_WORDS`'ü yaz**

`WORDS`'ün hemen altına:

```jsx
/** What a mode calls what it makes, and what it promises about it.
 *
 * No row for the plain mode: its words are the layer's own -- video / ses, videosunu / sesini --
 * and this table has no layer, so writing it here would mean writing those words a second time,
 * once per panel. A mode with no row falls back to the layer, which is what plain means.
 */
const MODE_WORDS = {
  [LOOP]: { noun: "loop video", tail: "her video kendine döner." },
  [LINKED]: { noun: "bağlı video", tail: "her video sıradaki karede biter." },
};
```

`LOOP` bugün `production_modes.js`'ten dışa verilmiyor — `MODES` listesinde düz dize olarak duruyor.
O dosya artık üçünü de adıyla veriyor:

```js
export const STANDARD = "standard";
export const LOOP = "loop";
export const LINKED = "linked";

export const MODES = [
  { id: STANDARD, label: "Standart" },
  { id: LOOP, label: "Loop" },
  { id: LINKED, label: "Sonrakine bağla" },
];
```

Panelin import satırı: `import { LINKED, LOOP, MODES, STANDARD } from "./production_modes.js";`

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: on kırmızı duruyor — kelimeler yazıldı ama onları okuyan cümle henüz yok.

---

### Task 2: Cümlenin kurulması

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Consumes: Task 1'in `WORDS[layer].held` ve `MODE_WORDS`'ü.
- Produces: `said` (`{ noun, tail }`) — Task 3'ün yeşil onayı `noun`'unu okuyor.

- [ ] **Step 1: Kopya sayısını ve kelimeleri hesapla**

`owed`'ın hemen altına, `linkingClosed`'ın üstüne:

```jsx
  // Frames in scope that already carry this layer. Production does not write over one -- it makes
  // a copy frame beside it -- and nothing on screen said so until now. Read from the scope rather
  // than the raw selection: Videosu olmayanlar leaves those frames out by its own definition, so
  // the count is zero there without a second rule about which scope may warn.
  const copies = scoped.filter((frame) => (frame.layers || {})[layer]).length;
  const said = MODE_WORDS[mode] || { noun: words.noun,
                                     tail: `her kare kendi ${words.own} alır.` };
```

- [ ] **Step 2: Tahmin satırını yaz**

Bugünkü tahmin satırının yerine:

```jsx
        ) : owed ? (
          <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
            {owed} {said.noun} üretilecek — {copies
              ? `${words.held} ${copies} kare için yeniler kopya kare olur, eskisi durur.`
              : said.tail}
          </Note>
        ) : (
```

Kopya uyarısı modun kuyruğunu alıyor, başını değil: mod cümlenin isminde zaten söylendi, dolayısıyla
kaybolan tek şey hemen üstteki işaretli satırın tekrarı.

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: sekiz test yeşile döner. İki tanesi kırmızı kalır — yeşil onayı ölçenler.

---

### Task 3: Yeşil onay gönderildiği modu hatırlıyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Consumes: Task 2'nin `said`'i yalnız tahmin için; onay kendi anlık kopyasını tutuyor.

- [ ] **Step 1: `added`'i genişlet**

Durumun kendisi değişmiyor, taşıdığı şey değişiyor:

```jsx
  // What the queue took and what it was told to make: both from the moment the request went out.
  // The card stands for ten seconds and the mode row is one click away, so reading the live mode
  // would let it report a run nobody asked for. null still means no card.
  const [added, setAdded] = useState(null);
```

`handleAdd` içinde, `mode`'u istekle birlikte donduruyor:

```jsx
  function handleAdd() {
    setSubmitting(true);
    setAdded(null);
    clearTimeout(fade.current);
    const sent = mode;
    onQueue(scope === "selected" ? inSelection.map((frame) => frame.file) : null, Number(variants),
            sent)
      .then((body) => {
        if (body && typeof body.added === "number") {
          setAdded({ count: body.added, mode: sent });
          fade.current = setTimeout(() => setAdded(null), CONFIRM_MS);
        }
      })
      .finally(() => setSubmitting(false));
  }
```

- [ ] **Step 2: Onay kartını yaz**

```jsx
        {added !== null ? (
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            <Note size={12} style={{ color: "var(--ok)" }}>✓</Note>
            <Note size={12} style={{ color: "var(--ok)" }}>
              {added.count} {(MODE_WORDS[added.mode] || words).noun} kuyruğa eklendi
            </Note>
          </div>
        ) : owed ? (
```

`MODE_WORDS[added.mode] || words` — iki sözlüğün de `noun` alanı var, dolayısıyla satırın kendisi
hangisinden okuduğunu sormuyor.

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 4: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

6. maddenin **İş** hücresi ✅ ile başlar, sayaç `5/31` → `6/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the estimate and the confirm say which mode was picked

Three modes, three sentences. The head names what comes out -- 2 loop video, 2 bagli
video -- and the tail says what that means: a loop returns to itself, a linked video
ends on the next frame. The plain mode keeps the line it had, because its words are the
layer own words and it has no table row of its own.

A frame in scope that already carries this layer takes the tail instead. Production
makes a copy frame beside it rather than writing over it, and nothing said so until now;
the mode is still named in the head, so the tail is the cheapest place to put news the
user cannot hear anywhere else. Counted from the scope, so the scope that leaves those
frames out warns without being asked not to.

The green card now carries the mode it was sent with. It stands for ten seconds and the
row is one click away.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört parçası — `WORDS.held`, `MODE_WORDS`, cümlenin kurulması, onayın
durumu — sırayla Task 1, 1, 2 ve 3'te.

**Tip tutarlılığı:** `MODE_WORDS[id]` ile `WORDS[layer]` ikisi de `noun` taşıyor, onay satırı bu
yüzden ikisinden birini ayrım yapmadan okuyabiliyor. `said` ise `{ noun, tail }` — `WORDS`'te `tail`
yok, o yüzden yedek nesne elde kuruluyor, `words`'ün kendisi verilmiyor.

**Kontrol edilen tuzak:** `handleAdd` içinde `sent = mode` isteğin **öncesinde** okunuyor. `.then`
içinde `mode` okunsaydı kapanış o anki değeri değil, çağrının kurulduğu render'ın değerini
taşırdı — bu örnekte doğru sonucu verirdi ama sebebi tesadüf olurdu, ve `mode`'un ne zaman
okunduğunu okuyan kişi kapanışın ömrünü hesaplamak zorunda kalırdı.

**Kontrol edilen tuzak 2:** `added !== null` kontrolü olduğu gibi kalıyor. `added &&` yazılsaydı
aynı işi görürdü ama `count: 0` bir gün mümkün olsaydı sessizce kaybolurdu; sunucu bugün 0
döndürebiliyor ve o durumda kart doğru biçimde çıkıyor.

**Kontrol edilen tuzak 3:** kopya sayısı `scoped`'tan, `chosen`'dan değil. `chosen` galerideki ham
seçim ve o katmanın hiç asılamayacağı kareleri de taşıyabiliyor — fotoğrafı üretilmemiş bir kare
sayıya girer, oysa kuyruğa hiç gitmiyor.

**Kontrol edilen tuzak 4:** `MODE_WORDS` anahtarları hesaplanmış (`[LOOP]`, `[LINKED]`), düz dize
değil. Kimliğin tek sahibi `production_modes.js` kalıyor.

**Kapsam dışı kalan, bilerek:** bağlı modda `owed` sunucunun ekleyeceği sayıdan büyük olabiliyor.
Panelde düzeltmek, motorun "filmde sonrası hangisi" kuralını ikinci kez yazmak demekti. Doğru sayı
yeşil onayda zaten sunucudan geliyor.
