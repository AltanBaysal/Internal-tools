# Madde 389 — Sohbet aramasında Esc yalnız aramayı boşaltır · test turu planı

> **Ajan için:** Bu plan tek oturumda, sırayla uygulanır. Adımlar `- [ ]` ile işaretlenir.

**Amaç:** `Search chats`'te yazı varken Esc'in aramayı boşaltıp açık dosyayı açık bıraktığını, boş
kutuda ise Esc'in açık dosyayı bugünkü gibi kapattığını isteyen iki testi yazmak.

**Mimari:** Testler `App.test.jsx`'te, "Escape closes the reading panel"ın hemen altında; Esc'in
sırası App'in tek `window` dinleyicisinde. Esc kutunun üstünde basılır (`fireEvent.keyDown(kutu)`),
olay `window`'a kadar kabarır — tarayıcıda olduğu gibi. Kutu, dosyanın 365 bloğundaki `chatSearch()`
yardımcısıyla bulunur. Dosyayı açan kurulum iki testte ortak: bir yardımcıya (`openPlan`) alınır.

**Teknoloji:** vitest, jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-30-queenagent-m389-arama-esc-testler-design.md)

## Genel kısıtlar

- Yalnız `queen-agent/frontend/src/App.test.jsx` değişir; `App.jsx` ve `Sidebar.jsx` bu turda
  değişmez.
- Hiçbir test susturulmaz (`.skip`, `.todo`).
- Testler CLAUDE.md'deki dört satırla, olduğu gibi ve paralel koşulur.
- Kod, yorum ve test adları İngilizce.

---

### Görev 1: Arama kutusundaki Esc

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/App.test.jsx` — "Escape closes the reading panel" testinin hemen
  altı.

- [ ] **Adım 1: Yardımcıyı ve iki testi ekle:**

```jsx
// Madde 389: Escape closes one thing a press, innermost first. In Search chats with something typed,
// that thing is the query -- trying 365 found the same press also shutting the file on the right.
// With the box empty there is nothing of its own to close, so Escape goes on as it does elsewhere.
async function openPlan() {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const fetch = vi.fn().mockImplementation((path) => {
    if (path.endsWith("/files/plan.md")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...file, size: 4, text: "body" }),
      });
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
    }
    return ok(path === "/api/projects" ? [PROJECT] : []);
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());
}

test("Escape in Search chats empties the search and leaves the open file open", async () => {
  await openPlan();
  fireEvent.change(chatSearch(), { target: { value: "intro" } });

  fireEvent.keyDown(chatSearch(), { key: "Escape" });
  expect(chatSearch().value).toBe("");
  expect(screen.getByText("body")).toBeTruthy();
});

test("Escape in an empty Search chats goes on to close the open file", async () => {
  await openPlan();

  fireEvent.keyDown(chatSearch(), { key: "Escape" });
  await waitFor(() => expect(screen.queryByText("body")).toBeNull());
});
```

- [ ] **Adım 2: Dört satırı paralel koş.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend`'te bir kırmızı — birinci test, `body` bulunamaz
(bugün aynı basış dosyayı da kapatıyor). İkinci test yeşil: bugünkü davranışı kilitliyor. Öteki üç
süit koşudan öncekiyle aynı.

- [ ] **Adım 3: Kırmızı hâliyle commit et** — spec, bu plan ve test dosyası:

```
git add docs/specs/2026-09-30-queenagent-m389-arama-esc-testler-design.md docs/plans/2026-09-30-queenagent-m389-arama-esc-testler-plan.md queen-agent/frontend/src/App.test.jsx
git commit -m <mesaj>
```

Mesaj: `test(queen-agent): Madde 389 red -- Escape in Search chats leaves the open file open` ve son
satırı `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
