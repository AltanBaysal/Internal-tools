# Madde 380 — Sohbetin sonuna gelen kart görünür · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dipteki okuyan sohbetin altına çıkan her kartı bütünüyle görür; yukarıdaki okuyan yerinde
kalır.

**Architecture:** `ChatScreen` okuyanın dipte olup olmadığını kaydırdığı anda bir ref'e yazar; cevabın
yazısı ya da bir kart geldiğinde, ref doğruysa liste dibe iner. Yeni mesajın her zaman dibe inmesi
değişmez.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m380-kart-gorunur-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Testlere dokunulmaz: kırmızı commit'teki testler ne diyorsa o.
- Kod ve yorum İngilizce; yorum NEDEN'i söyler.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Tek izleme kuralı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` — `scroll`/`toBottom` ve iki
  etki (83–97. satırlar), `.chat__scroll`'un açılış etiketi (137. satır)

**Interfaces:**
- Consumes: test turunun `scrollable` yardımcısı `.chat__scroll`'da `scroll` olayı atar.

- [ ] **Step 1: Ref, `onScroll` ve tek etki**

83–97. satırların yerine:

```jsx
  const scroll = useRef(null);
  const toBottom = () => {
    const list = scroll.current;
    if (list) list.scrollTop = list.scrollHeight;
  };

  // Whether the reader was at the foot when they last scrolled. Taken then rather than once the foot
  // has grown: a card taller than STICK_WITHIN -- a permission card printing a whole file -- would
  // otherwise make a reader at the foot look like one who had scrolled away.
  const following = useRef(true);
  const onScroll = () => {
    const list = scroll.current;
    following.current = list.scrollHeight - list.scrollTop - list.clientHeight <= STICK_WITHIN;
  };

  // A message the user just sent is theirs to see, so the list always jumps.
  useEffect(toBottom, [chat?.messages.length]);

  // Whatever else lands at the foot -- the answer as it arrives, and the cards under it (Madde 380)
  // -- follows the reader rather than the other way round. The files' count rather than the list:
  // an absent list is a fresh [] on every render.
  useEffect(() => {
    if (following.current) toBottom();
  }, [streamingText, createdFiles.length, permission, refused, error]);
```

137. satır:

```jsx
        <div className="chat__scroll" ref={scroll} onScroll={onScroll}>
```

- [ ] **Step 2: Dört satırı paralel koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü yeşil.

- [ ] **Step 3: Commit**

```bash
git add queen-agent/frontend/src/features/workspace/ChatScreen.jsx docs/superpowers/specs/2026-09-29-queenagent-m380-kart-gorunur-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m380-kart-gorunur-uygulama-plan.md
git commit -m "feat: Madde 380 -- a card at the chat's foot is scrolled to, unless the reader is up the page"
```
