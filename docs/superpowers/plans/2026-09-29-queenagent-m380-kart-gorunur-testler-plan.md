# Madde 380 — Sohbetin sonuna gelen kart görünür · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dipteki okuyanın, sohbetin altına çıkan kartı bütünüyle gördüğünü, yukarıdaki okuyanın
yerinde kaldığını tutan testler, kırmızı.

**Architecture:** `ChatScreen.test.jsx`'in kaydırma testlerinin yanına beş test. `scrollable`
yardımcısı okuyanın yerini bir `scroll` olayıyla bildirir; yeni `grow` yardımcısı kartın gelişini
içeriğin büyümesiyle anlatır.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m380-kart-gorunur-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `ChatScreen.jsx` yazılmaz. `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Kartın görünmesinin testleri, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — `scrollable` yardımcısı
  (bugün 779–787. satırlar), yeni `grow` yardımcısı, *a reader who is watching the end stays stuck to
  it* testinden sonra beş test

**Interfaces:**
- Produces: uygulama turunun karşılayacakları — `.chat__scroll` üzerindeki bir `scroll` olayı okuyanın
  yerini bildirir; `error`, `refused`, `permission` ya da `createdFiles` değişince, okuyan son
  kaydırmasında dibe 220'den yakınsa `scrollTop = scrollHeight` olur, değilse `scrollTop` değişmez.

- [ ] **Step 1: `scrollable` bir kaydırma olayı atar, `grow` eklenir**

```jsx
// jsdom lays nothing out, so the sizes are declared and what is under test is the decision: does
// the list follow the answer down, or does it leave the reader where they are? The reader is put
// there by a scroll, the way a real reader gets there.
function scrollable(container, { at }) {
  const scroll = container.querySelector(".chat__scroll");
  Object.defineProperty(scroll, "scrollHeight", { configurable: true, value: 1000 });
  Object.defineProperty(scroll, "clientHeight", { configurable: true, value: 300 });
  scroll.scrollTop = at;
  fireEvent.scroll(scroll);
  return scroll;
}

// Something new at the foot, as the list sees it: it is taller.
function grow(scroll, height) {
  Object.defineProperty(scroll, "scrollHeight", { configurable: true, value: height });
}
```

- [ ] **Step 2: Beş test**, *a reader who is watching the end stays stuck to it*'ten sonra:

```jsx
// --- a card at the chat's foot is seen (Madde 380) ------------------------------------------------
// Found in the browser: after a failed answer the list stopped 98px short of its foot, the card half
// under the box. Each card below is one that appears at the foot of the chat.

test("a reader at the foot sees a failure card whole", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1100);
  rerender(<ChatScreen project={PROJECT} chat={CHAT} error="HTTP 401" />);
  expect(scroll.scrollTop).toBe(1100);
});

test("a reader at the foot sees a refused message's card whole", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1100);
  rerender(<ChatScreen project={PROJECT} chat={CHAT} refused="A message cannot be empty." />);
  expect(scroll.scrollTop).toBe(1100);
});

test("a reader at the foot is taken down to a permission card taller than the follow distance", () => {
  // The card prints the call's arguments raw -- a write_file's whole content -- so it can be far
  // taller than 220. Measured once it has arrived, the reader who was at the foot would look like
  // one who had scrolled away.
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1600);
  rerender(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      permission={{ tool: "write_file", args: '{"name": "intro.md", "content": "..."}' }}
    />,
  );
  expect(scroll.scrollTop).toBe(1600);
});

test("a reader at the foot sees a file card the answer just made", () => {
  const { container, rerender } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Done." />,
  );
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1100);
  rerender(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      streamingText="Done."
      createdFiles={["intro.md"]}
    />,
  );
  expect(scroll.scrollTop).toBe(1100);
});

test("a reader up the page stays where they are when cards arrive at the foot", () => {
  // The same rule the answer keeps: the list follows the reader, not the other way round.
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 0 });
  grow(scroll, 1600);
  rerender(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      error="HTTP 401"
      refused="A message cannot be empty."
      permission={{ tool: "write_file", args: "{}" }}
      createdFiles={["intro.md"]}
    />,
  );
  expect(scroll.scrollTop).toBe(0);
});
```

- [ ] **Step 3: Dört satırı paralel koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı, yalnız ilk dört yeni test düşer —
`scrollTop` 700'de kalır. Beşinci test ve bugünkü üç kaydırma testi yeşil. Öteki üç süit bugünkü
hâlinde.

- [ ] **Step 4: Kırmızı commit**

```bash
git add queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx docs/superpowers/specs/2026-09-29-queenagent-m380-kart-gorunur-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m380-kart-gorunur-testler-plan.md
git commit -m "test(queen-agent): Madde 380 red -- a card at the chat's foot is scrolled to, unless the reader is up the page"
```
