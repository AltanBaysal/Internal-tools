# Madde 84 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m84-tool-callar-karta-doner-testler-design.md](../specs/2026-08-26-queenagent-m84-tool-callar-karta-doner-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Sınıf adları:** `.tool-calls` *(kap, duruyor)* · `.tool-calls__handle` *(basılan kart, `<button>`)*
· `.tool-calls__summary` *(tutamağın metni)* · `.tool-calls__chevron` · `.tool-call` *(bir çağrının
kartı, `<div>`)* · `.tool-call__head` · `.tool-call__outcome`.

**Tutamağın metni:** kapalı + akarken son çağrının başı *(`⏺ read_file(aylin.json)`)*, diğer üç
durumda `⏺ N steps` — tek çağrıda `⏺ 1 step`.

**Arka uca dokunulmuyor.** İki dosya: `ChatScreen.test.jsx` ve `workspace.css.test.js`.

---

## Sıra

### 1. `ChatScreen.test.jsx` — kapı ve arkasındaki liste

`a stored answer draws the calls it made` **üçe bölünüyor**. `ANSWERED` sabiti olduğu gibi kalıyor
*(iki çağrı: `list_files` sonucu `No files`, `read_file(aylin.json)` sonucu `45 lines`)*:

```jsx
test("a stored answer keeps the calls it made, behind one card", () => {
  // The half the item is really about: someone reading the chat a week later sees that the answer
  // looked before it spoke. It is behind a door now rather than spread over the answer, and the
  // door says how many steps it hides.
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  expect(container.querySelectorAll(".tool-call")).toHaveLength(0);
  expect(screen.getByRole("button", { name: /2 steps/ })).toBeTruthy();
});

test("opening the card lists every call the turn made", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(container.querySelectorAll(".tool-call")).toHaveLength(2);
});

test("pressing it again puts them away", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(container.querySelectorAll(".tool-call")).toHaveLength(0);
});
```

Üçü de kırmızı: bugün iki `.tool-call` açıkta duruyor ve basılacak hiçbir şey yok.

### 2. `ChatScreen.test.jsx` — 78'in metni, artık kartın içinde

Dört test *(`a call is drawn as its tool...`, `a call about no file...`, `how the call went...`,
`a call with nothing to say...`)* şunlarla değişiyor. Metnin kendisi 78'in kararı ve değişmiyor;
değişen, önce kapının açılması ve sonucun `⎿`'sini bırakması:

```jsx
test("a call is drawn as its tool with the file in brackets", () => {
  // Asked for by its text: a missing line then names what was looked for, rather than failing
  // later on a null nobody can read.
  render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(screen.getByText("⏺ read_file(aylin.json)").className).toBe("tool-call__head");
});

test("a call about no file in particular is drawn without empty brackets", () => {
  // Listing a directory really is about no file, and a pair of empty brackets would announce
  // something that is not there.
  render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(screen.getByText("⏺ list_files").className).toBe("tool-call__head");
});

test("how the call went sits on the same card, not under it", () => {
  // The mark used to say "the result of the thing above". The card says it now: everything inside
  // one card belongs to one call.
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  const said = [...container.querySelectorAll(".tool-call__outcome")].map(
    (line) => line.textContent,
  );
  expect(said).toEqual(["No files", "45 lines"]);
});

test("a call with nothing to say leaves that side of the card empty", () => {
  // What a chat recorded before Madde 78 looks like. A blank half would claim a result that was
  // never written down.
  const older = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], calls: [{ tool: "list_files" }] }],
  };
  const { container } = render(<ChatScreen project={PROJECT} chat={older} />);
  fireEvent.click(screen.getByRole("button", { name: /1 step/ }));
  expect(screen.getByText("⏺ list_files")).toBeTruthy();
  expect(container.querySelector(".tool-call__outcome")).toBeNull();
});
```

Dördü de kırmızı: bugün basılacak bir düğme yok, ve sonuç `⎿ No files` diyor.

### 3. `ChatScreen.test.jsx` — akan tur

`a call still streaming is drawn the same way` **tamamen** şununla değişiyor, ve altına ikincisi
geliyor:

```jsx
test("while the answer runs the closed card says what it is doing now", () => {
  // The one thing a reader wants while they wait: not how many steps there have been, but which
  // one is happening. A call still in flight has no outcome yet, and that is the live half.
  render(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      streamingCalls={[
        { tool: "list_files", target: "", outcome: "No files" },
        { tool: "read_file", target: "aylin.json" },
      ]}
    />,
  );
  expect(screen.getByRole("button", { name: /read_file\(aylin\.json\)/ })).toBeTruthy();
  expect(screen.queryByText(/2 steps/)).toBeNull();
});

test("opening a running turn switches the handle to the count", () => {
  // Open, the last call is on a card of its own right below -- so the handle stops repeating it and
  // says what it is a door to.
  const { container } = render(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      streamingCalls={[
        { tool: "list_files", target: "", outcome: "No files" },
        { tool: "read_file", target: "aylin.json" },
      ]}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: /read_file\(aylin\.json\)/ }));
  expect(screen.getByRole("button", { name: /2 steps/ })).toBeTruthy();
  expect(container.querySelectorAll(".tool-call")).toHaveLength(2);
});
```

Birincisi kırmızı *(bugün iki satır birden açıkta ve düğme yok)*, ikincisi de.

### 4. `ChatScreen.test.jsx` — kart bir kapı değil, ve kapı açık olduğunu söylüyor

`an answer that called nothing draws no list at all` testinin **üstüne**, o dokunulmadan:

```jsx
test("a call card is a record rather than a door", () => {
  // The handle is pressable because it opens something. A step that already happened opens nothing,
  // so it is not a button and offers no cursor -- Madde 78's rule, kept while the drawing changes.
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(container.querySelector(".tool-call").tagName).toBe("DIV");
});

test("the handle says whether it is open", () => {
  render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  const handle = screen.getByRole("button", { name: /2 steps/ });
  expect(handle.getAttribute("aria-expanded")).toBe("false");
  fireEvent.click(handle);
  expect(handle.getAttribute("aria-expanded")).toBe("true");
});

test("one call is one step rather than one steps", () => {
  // An interface that writes "1 steps" looks like it never read the number.
  const once = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], calls: [{ tool: "list_files" }] }],
  };
  render(<ChatScreen project={PROJECT} chat={once} />);
  expect(screen.getByText("⏺ 1 step")).toBeTruthy();
});
```

Üçü de kırmızı.

### 5. `workspace.css.test.js` — iki yeni test

`the stamp reads as a note in the same voice as the line above it` testinin **altına**:

```js
test("a call is drawn on the card the repo already has", () => {
  // Not a second card language: the file card settled what a card looks like here, and a call
  // borrows its skeleton rather than inventing one beside it.
  const card = rule(".tool-call");
  expect(card).toContain("border-radius: 12px");
  expect(card).toContain("border: 1px solid var(--line)");
  expect(card).toContain("max-width: 340px");
});

test("only the handle offers to be pressed", () => {
  // A card you can press does something; a card you cannot is a record. Madde 78's rule, kept.
  expect(rule(".tool-call")).not.toContain("cursor");
  expect(rule(".tool-calls__handle")).toContain("cursor: pointer");
});
```

İkisi de kırmızı: `.tool-call` bugün kart değil ve `.tool-calls__handle` hiç yok — `rule()`
bulamayınca `expect(start).toBeGreaterThan(-1)` düşüyor, `TypeError` değil.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `ChatScreen.test.jsx` — kapı ve liste | 3 |
| `ChatScreen.test.jsx` — 78'in metni | 4 |
| `ChatScreen.test.jsx` — akan tur | 2 |
| `ChatScreen.test.jsx` — kayıt, `aria-expanded`, tekil | 3 |
| `workspace.css.test.js` | 2 |

Arka uçta değişiklik yok: bugünkü **2 failed, 430 passed** aynen kalır.

Ön yüzde bugün **497 passed**. Sekiz yeni testle toplam **505**, ve **14 failed, 491 passed**
beklenir.

**Kırmızının okunabilir olması şart.** Metin beklentileri `screen.getByText(...)` ya da
`getByRole(...)` ile yazılıyor; ikisi de bulamayınca ne aradığını söyleyerek düşüyor.
`container.querySelectorAll(...)` yolu boş liste döndürüyor, `TypeError` değil — tek `querySelector`
çağrısı *(`.tool-call` bir `DIV` mi)* kapı açıldıktan sonra var olacak bir elemana bakıyor ve bugün
de var olan bir elemana bakıyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `ChatScreen.jsx` ve `workspace.css` bu turda açılmıyor.
- **`dist` derlenmez.** Kaynak değişmiyor.
- **Arka uca dokunulmaz.** Ne kaydedildiği 66 ile 78'in kararı ve değişmiyor.
- **`ANSWERED` sabiti değiştirilmez.** İki çağrısı bu maddenin de ihtiyacı olan iki çağrı: biri
  konusuz, biri konulu.
- **`an answer that called nothing draws no list at all` değiştirilmez.** Çağrısız cevabın üstünde
  hiçbir şey olmadığını tutan tek test o, ve kural değişmiyor.
- **Escape testi yazılmaz.** Açık liste bir katman değil; Escape'in sırasına girmiyor.
