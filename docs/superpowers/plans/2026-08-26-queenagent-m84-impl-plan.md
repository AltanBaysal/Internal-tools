# Madde 84 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m84-tool-callar-karta-doner-uygulama-design.md](../specs/2026-08-26-queenagent-m84-tool-callar-karta-doner-uygulama-design.md)
**Testler:** commit `17a5b21` — **14 kırmızı**, ikisi stil kilidinde.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**İki dosya:** `ChatScreen.jsx` ve `workspace.css`. Arka uç açılmıyor.
**`dist` bu turda derlenir ve aynı commit'e girer.**

---

## Sıra

### 1. `ChatScreen.jsx` — `headOf` ayrı bir isim oluyor

`ToolCalls`'un üstüne, bugün satır içinde kurulan metin bir isim alıyor — iki yerde okunacak
*(tutamak ve kart)*, ve iki yerde okunan bir ifadenin adı olur:

```jsx
// Madde 78's shape: the step's mark, the tool, and its subject in brackets. The brackets carry the
// file rather than a separator -- a call about no file in particular really has none, and a mark
// standing where a name would have been announces something that is not there.
function headOf(call) {
  return `⏺ ${call.tool}${call.target ? `(${call.target})` : ""}`;
}
```

### 2. `ChatScreen.jsx` — `ToolCalls` durum tutuyor

Bugünkü `ToolCalls` **tamamen** şununla değişiyor:

```jsx
// What the turn did before it spoke, behind one door. Above the answer, because that is the order it
// happened in.
//
// Shut, the door says which step is happening while the turn runs and how many there were once it
// is over: waiting, a reader wants to know what is going on; afterwards, what it did. Open, the
// handle stops repeating the last call -- that call is on a card right below it.
//
// A card you can press does something; a card you cannot is a record. The handle opens the list, so
// it is a button. A step that already happened opens nothing, so it is not -- Madde 78's rule, and
// the only part of it this item drops is the unspoken half, that a record has to be faint.
function ToolCalls({ calls, running }) {
  // Per message, and per box: the loop draws one of these for each, so a new answer is born shut
  // and a reload shuts them all. It is a way of looking rather than a fact about the chat, so it
  // reaches neither disk nor browser storage.
  const [open, setOpen] = useState(false);
  if (!calls?.length) return null;
  const summary = `⏺ ${calls.length} step${calls.length === 1 ? "" : "s"}`;
  return (
    <div className="tool-calls">
      <button
        type="button"
        className="tool-calls__handle"
        aria-expanded={open}
        onClick={() => setOpen((shown) => !shown)}
      >
        <span className="tool-calls__summary">
          {running && !open ? headOf(calls[calls.length - 1]) : summary}
        </span>
        <span className="tool-calls__chevron">{open ? "⌃" : "⌄"}</span>
      </button>
      {open
        ? calls.map((call, index) => (
            <div className="tool-call" key={`${call.tool}-${call.target}-${index}`}>
              <span className="tool-call__head">{headOf(call)}</span>
              {/* Absent on anything recorded before outcomes existed, and an empty half would
                  claim a result nobody wrote down. */}
              {call.outcome ? (
                <span className="tool-call__outcome">{call.outcome}</span>
              ) : null}
            </div>
          ))
        : null}
    </div>
  );
}
```

`useState` zaten dosyanın en üstünde `import { useEffect, useRef, useState } from "react"` ile
geliyor; yeni bir import yok.

### 3. `ChatScreen.jsx` — akan iki kutu `running` diyor

Saklanmış mesajın döngüsündeki çağrı **değişmiyor** — tur bitmiş, bayrak verilmiyor:

```jsx
{message.role === "ai" ? <ToolCalls calls={message.calls} /> : null}
```

Akan kutuda ve bekleyen kutuda bayrak ekleniyor:

```jsx
<ToolCalls calls={streamingCalls} running />
```

Hangi kutunun çizdiği zaten hangi durumda olduğunu söylüyor; bir geçişi izleyen efekt yok.

### 4. `workspace.css` — kap, tutamak, kart

`.tool-calls`, `.tool-call` ve `.tool-call__outcome` blokları ile üstlerindeki yorum **tamamen**
şununla değişiyor:

```css
/* What the turn did before it spoke, behind one door. Madde 78's rule holds and is written into the
   markup: the handle is a button because it opens something, a call is not because a step already
   taken opens nothing, and neither carries the accent. What 84 dropped is the unspoken half of that
   rule -- that a record has to be faint. It does not: it can sit in a bordered box and still be
   nothing to press. */
.tool-calls {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-self: flex-start;
  margin-bottom: 8px;
}

/* The door. The file card's skeleton, and the only card here that answers a press. */
.tool-calls__handle {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 340px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 11px 14px;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
}

.tool-calls__handle:hover {
  border-color: #d9d0c3;
}

.tool-calls__summary {
  flex: 1;
  min-width: 0;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-calls__chevron {
  flex: none;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
}

/* One step, on the same skeleton -- and no cursor, because it opens nothing. */
.tool-call {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 340px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 11px 14px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  animation: fadeIn 0.2s ease both;
}

/* The file card's own division of labour: the name that can run long is the one that gets cut, and
   the note beside it keeps its room. */
.tool-call__head {
  flex: 1;
  min-width: 0;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-call__outcome {
  flex: none;
  color: var(--muted);
}
```

**Dikkat:** stil kilidi `rule(".tool-call")` içinde `cursor` **aramıyor** — `not.toContain("cursor")`
diyor. `.tool-call` bloğuna hiçbir imleç satırı yazılmıyor.

### 5. `dist` derlenir

```
npm run build --prefix queen-agent/frontend
```

Kaynakla **aynı commit'e** giriyor; `test_dist_is_committed.py` bunu zorluyor.

## Turda çıkan: envanterde eksik kalan iki test

Kod bittiğinde 14 kırmızının hepsi yeşile döndü, ama **hesaba katılmamış iki test düştü**. İkisi de
aynı biçimde: **iddiası ayakta, varsayımı düşmüş** — iddianın hangi elemanda taşındığı.

**Bir:** `ChatScreen.test.jsx` · `a call seen while the answer is still running is drawn as it
arrives`. 66'nın testi, iki şey soruyordu:

```jsx
expect(container.querySelector(".tool-call")).toBeTruthy();
expect(screen.getByText("⏺ read_file(plan.md)")).toBeTruthy();
```

İkincisi hâlâ doğru — kapalı tutamak tam olarak o metni yazıyor. Birincisi artık yanlış: kapalıyken
kart yok. Birinci beklenti kaldırıldı; kalan, 66'nın söylediği şey — akışın bildirdiği çağrı, kayıt
oluşmadan önce ekranda. Hangi elemanın taşıdığını komşu test tutuyor
*(`while the answer runs the closed card says what it is doing now`)*.

**İki:** `App.test.jsx` · `a call arrives in the stream and is still there once the record lands`.
İddiası şu: iki yer bildirdi *(canlı akış ve arkasından gelen kayıt)* ama adım **bir kez** duruyor.
Kayıt indiğinde kapı kapalı olduğu için metin ekranda hiç yok. İddia kapının arkasında soruluyor
artık — önce tutamağa basılıyor, sonra bir tane olduğu doğrulanıyor.

**Neden test turunda yakalanmadı:** etkilenen testler bölüm başlığına bakarak sayıldı — `Madde 66` ve
`Madde 78` başlıklarının altındaki yedi test. Sekizincisi 67'nin bölümünün içinde, dokuzuncusu başka
bir dosyada duruyordu.

**Ders:** bir çizim değiştiğinde envanter başlıkla değil, **dokunulan sınıf ve metinle** çıkarılır,
ve **bütün test dosyalarında**. `tool-call|⏺|⎿` için tek bir arama dokuzunu birden bulurdu — turun
sonunda o arama yapıldı ve başka bir şey kalmadığını gösterdi.

## Beklenen yeşil

Arka uçta **2 failed, 430 passed** — ikisi defterin dalı, bu maddeyle ilgisiz.
Ön yüzde **505 passed**, kırmızı yok.

## Bilerek yapılmayanlar

- **Arka uca dokunulmaz.** Ne kaydedildiği 66 ile 78'in kararı.
- **`⏺` silinmez.** Adımın kendi işareti, ve tutamakta da o duruyor. Giden yalnız `⎿`.
- **Parantez kuralı değiştirilmez.** Konusu olmayan çağrının parantezi de yok.
- **Açık/kapalı `App`'e taşınmaz.** Escape'in sırasına girmiyor; `fark 67`'nin dörtlü sırası dörtte
  kalıyor.
- **`.file-card`'a dokunulmaz.** İskelet ondan ödünç alınıyor, o değişmiyor.
- **Testlere dokunulmaz.** Bir test kod yazılırken düzeltiliyorsa kırmızı yanlış yerdeydi; o zaman
  durulur ve söylenir.
