# Madde 83 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m83-damga-mesajin-altina-iner-testler-design.md](../specs/2026-08-26-queenagent-m83-damga-mesajin-altina-iner-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Ekrandaki metin:** `11:05 · 13.2k tokens` — saat, ayırıcı ` · `, kısaltılmış sayı, `tokens`.
Sayı yoksa yalnız `11:05`. Sınıf adı `msg__stamp`.

**Arka uca dokunulmuyor.** İki dosya değişiyor: `ChatScreen.test.jsx` ve `workspace.css.test.js`.

---

## Sıra

### 1. `ChatScreen.test.jsx` — iki damga testi yeniden yazılır, bir üçüncüsü eklenir

Bugünkü iki test (`a user message is labelled with the time and nothing else` ve
`an answer is labelled QueenAgent`) **tamamen** şunlarla değişiyor, ve altlarına üçüncüsü geliyor:

```jsx
test("a user message is stamped with the time and nothing else", () => {
  // The design draws the person's own name there but never says where it comes from, and there is
  // no such setting. Who wrote it is already clear from the bubble sitting on the right.
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("11:04").className).toBe("msg__stamp");
  expect(screen.queryByText(/You/)).toBeNull();
});

test("an answer is stamped with the time and nothing else either", () => {
  // The name used to sit above every answer and it said nothing new: the sidebar carries it, and an
  // answer sitting on the left already says whose turn this was.
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("11:05").className).toBe("msg__stamp");
  expect(screen.queryByText(/QueenAgent/)).toBeNull();
});

test("the stamp closes a message rather than opening it", () => {
  // A note belongs under the thing it is about. Above, it is read before there is anything to read
  // it against -- and it was two notes at two ends, which is the same note said twice.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const messages = [...container.querySelectorAll(".msg")];
  expect(messages).toHaveLength(2);
  expect(messages.map((msg) => msg.lastElementChild.className)).toEqual([
    "msg__stamp",
    "msg__stamp",
  ]);
});
```

Üçü de kırmızı. Birincide sınıf bugün `msg__label`; ikincide `getByText("11:05")` hiç bulamıyor
*(metin `QueenAgent · 11:05`)* ve testin ne aradığını söyleyerek düşüyor; üçüncüde son çocuklar
bugün `msg__bubble` ile `msg__text`.

### 2. `ChatScreen.test.jsx` — bekleyen kutunun iki testi

`the waiting label carries the time the wait began` ve `that time does not move while the answer
arrives` şunlarla değişiyor:

```jsx
test("the waiting stamp carries the time the wait began", () => {
  // Today the clock only appears once the answer has been saved; the design wants the label and the
  // dots on screen together, time and all.
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(screen.getByText("14:32").className).toBe("msg__stamp");
  vi.useRealTimers();
});

test("that time does not move while the answer arrives", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  const { rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  vi.setSystemTime(new Date(2026, 7, 9, 14, 35));
  rerender(<ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here" />);
  // It answers "when was this asked for", and that answer stopped being new at 14:32.
  expect(screen.getByText("14:32")).toBeTruthy();
  expect(screen.queryByText("14:35")).toBeNull();
  vi.useRealTimers();
});
```

İkisi de kırmızı: bugünkü metin `QueenAgent · 14:32`.

### 3. `ChatScreen.test.jsx` — harcamayı soran dört test

`--- what the answer spent (Madde 68) ---` bölümündeki dördü **tamamen** şunlarla değişiyor.
`withUsage` yardımcısı olduğu gibi kalıyor:

```jsx
test("an answer says what it spent, beside when it was said", () => {
  // One number rather than the breakdown: the owner asked for a plain total under each answer, and
  // what it is made of stays on disk for the context work rather than being drawn here.
  render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 12400, cached: 9100, answered: 842 })} />,
  );
  // Asked for by its text rather than by its class: a missing element then names what was looked
  // for, instead of failing later on a null nobody can read.
  expect(screen.getByText("11:05 · 13.2k tokens").className).toBe("msg__stamp");
});

test("a small answer is not dressed up as a big one", () => {
  render(<ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />);
  expect(screen.getByText("11:05 · 342 tokens").className).toBe("msg__stamp");
});

test("an answer nobody measured still says when it was said", () => {
  // Zero is what an answer from before this existed reads back as, and a count under it would claim
  // a measurement nobody took. The time is not a measurement -- it was said at a time either way.
  render(<ChatScreen project={PROJECT} chat={withUsage({ sent: 0, cached: 0, answered: 0 })} />);
  expect(screen.getByText("11:05").className).toBe("msg__stamp");
  expect(screen.queryByText(/tokens/)).toBeNull();
});

test("the user's own message never carries a count", () => {
  // Spending is what an answer does. A number under the question would read as its price.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />,
  );
  expect(screen.getByText("11:04").className).toBe("msg__stamp");
  expect(container.querySelector(".msg--user").textContent).not.toContain("tokens");
});
```

Dördü de kırmızı. Üçüncüsü **ters yönde**: bugün ölçülmemiş cevabın altında hiçbir satır yok, yarın
saat taşıyan bir damga var. Sayının yokluğu artık satırın yokluğu demek değil.

Bölüm başlığındaki yorum da düzeliyor — sayı 68'in, ama durduğu yer artık 83'ün.

### 4. `workspace.css.test.js` — iki yeni test

`the stopped line reads as a note, not as the answer` testinin **altına**, o dokunulmadan:

```js
test("the stamp reads as a note in the same voice as the line above it", () => {
  // What it says is a clock and maybe a count. Neither has a case, so the uppercase the label above
  // the message used to carry goes with the label.
  const stamp = rule(".msg__stamp");
  expect(stamp).toContain("var(--font-mono)");
  expect(stamp).toContain("color: var(--muted)");
  expect(stamp).not.toContain("text-transform");
});

test("the two lines the stamp replaces are gone", () => {
  // Madde 83 folded a label above the message and a count below it into one line under it. Either
  // name left behind would style something nothing draws any more.
  expect(CSS).not.toContain(".msg__label");
  expect(CSS).not.toContain(".token-count");
});
```

Birincisi kırmızı: `rule()` bulamayınca `expect(start).toBeGreaterThan(-1)` düşüyor — okunur bir
kırmızı, `TypeError` değil. İkincisi de kırmızı: iki ad da bugün dosyada.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `ChatScreen.test.jsx` — damga ve yeri | 3 |
| `ChatScreen.test.jsx` — bekleyen kutu | 2 |
| `ChatScreen.test.jsx` — harcama | 4 |
| `workspace.css.test.js` | 2 |

Arka uçta değişiklik yok: bugünkü **2 failed, 430 passed** aynen kalır, ve o iki kırmızı defterin
dalı.

Ön yüzde bugün **494 passed**. Üç yeni testle toplam **497**, ve **11 failed, 486 passed** beklenir.

**Kırmızının okunabilir olması şart.** `container.querySelector(...).textContent` yolu eleman yoksa
`TypeError` veriyor ve testin ne beklediğini gizliyor; 68 ile 78'de iki kez oldu. Buradaki bütün
metin beklentileri `screen.getByText(...)` ile yazılıyor, ve tek `querySelector` bugün de var olan
bir elemana (`.msg--user`) bakıyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `ChatScreen.jsx` ve `workspace.css` bu turda açılmıyor.
- **`dist` derlenmez.** Kaynak değişmiyor.
- **Arka uca dokunulmaz.** Damga zaten diskteki `at` ve `usage` alanlarından çiziliyor; ikisi de
  yerinde.
- **`shorten` testleri değiştirilmez.** `13.2k` ile `342` biçimleri 68'in kararı; bu madde onlara
  dokunmuyor, yalnız başlarına saati ekliyor.
- **Kenar çubuğunun `QueenAgent`'ı aranmaz.** `Sidebar.test.jsx` ile `App.test.jsx`'teki üç
  `getByText("QueenAgent")` yerinde ve yeşil kalmalı — kelime uygulamadan silinmiyor, mesajın
  üstünden siliniyor.
- **Testin adı yalan söylerse değişir.** `an answer is labelled QueenAgent` artık olmayacak bir şeyi
  anlatıyor; yalan söyleyen bir ad testten uzun yaşar.
