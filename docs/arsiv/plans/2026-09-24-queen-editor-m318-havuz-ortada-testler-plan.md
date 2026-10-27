# Madde 318 — Havuz ortada, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Spec'in 10 testi ve iki değişikliği — kırmızı; sol sütunu soran test kaldırılıyor.

**Spec:** [m318 test turu](../specs/2026-09-24-queen-editor-m318-havuz-ortada-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; arayüz metni tasarımdan harfi harfine.
- Testler dört satırla koşulur; `skip` / `xfail` / `.skip` / `.todo` yok. Kaynak kod değişmiyor.

---

## Görev 1: `LayerPanel.test.jsx`

`renderPanel`'in varsayılanlarına `poolShown={false} onShowPool={() => {}}`. Dosyanın sonuna:

```jsx
describe("LayerPanel — the pool's one button", () => {
  it("asks for the pool on Referanstan and for the cards on Kareden", () => {
    const onShowPool = vi.fn();
    renderPanel({ onShowPool });

    fireEvent.click(tab("Referanstan"));
    expect(onShowPool).toHaveBeenLastCalledWith(true);

    fireEvent.click(tab("Kareden"));
    expect(onShowPool).toHaveBeenLastCalledWith(false);
  });

  it("closes the pool from the Referanslar block while it is shown", () => {
    const onShowPool = vi.fn();
    renderPanel({ poolShown: true, onShowPool });
    fireEvent.click(tab("Referanstan"));

    fireEvent.click(screen.getByText("Referansları kapat"));

    expect(onShowPool).toHaveBeenLastCalledWith(false);
  });

  it("opens it again from the same place while the cards are shown", () => {
    const onShowPool = vi.fn();
    renderPanel({ onShowPool });
    fireEvent.click(tab("Referanstan"));

    fireEvent.click(screen.getByText("Referansları aç"));

    expect(onShowPool).toHaveBeenLastCalledWith(true);
  });

  it("gives the cards back when the panel goes", () => {
    // The pool belongs to this panel's tab: with the panel gone there is nothing it belongs to.
    const onShowPool = vi.fn();
    const view = renderPanel({ onShowPool });
    fireEvent.click(tab("Referanstan"));

    view.unmount();

    expect(onShowPool).toHaveBeenLastCalledWith(false);
  });
});
```

## Görev 2: `SidePanel.test.jsx`

317'nin raydan açılış testinin altına:

```jsx
  it("opens the video panel on Kareden again after the sound panel", async () => {
    // Two layers, two panels: the sound one does not inherit the video one's tab and words.
    vi.stubGlobal("fetch", recordServer());
    renderColumn({ frames: [] });

    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Referanstan" }));
    });
    fireEvent.click(screen.getByLabelText("Ses üret"));
    fireEvent.click(screen.getByLabelText("Video üret"));

    expect(screen.getByRole("button", { name: "Kareden" }).className).toContain("is-on");
  });
```

## Görev 3: `ProjectScreen.test.jsx`

- [ ] **Adım 1:** sahte `api.js`'e:

```jsx
  getReferenceSettings: vi.fn().mockResolvedValue({ prompts: "", variants: null }),
  saveReferenceSettings: vi.fn(),
```

- [ ] **Adım 2:** `ProjectScreen reference panel` bloğundan `opens with the pool beside the cards,
  and closes it like an editor does` kaldırılıyor; blok adı `ProjectScreen — the card panel`.
- [ ] **Adım 3:** yeni blok, onun altına:

```jsx
describe("ProjectScreen — the pool opens in place of the cards (madde 318)", () => {
  // The pool's first row heading, and the empty gallery's own sentence: one says the pool is in
  // the middle, the other whether the cards are hidden there.
  const pool = () => screen.queryByText("Fotoğraflar 0/9");
  const cardsHidden = () => Boolean(screen.getByText("henüz kare yok").closest("[hidden]"));
  const tab = (name) => screen.getByRole("button", { name });

  async function open(project) {
    renderScreen(project);
    await act(async () => {});
  }

  async function openReferanstan() {
    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(tab("Referanstan")); });
  }

  it("keeps no pool column beside the cards", async () => {
    await open("havuz-a");

    expect(screen.queryByLabelText("Referans panelini kapat")).toBeNull();
    expect(screen.queryByLabelText("Referans panelini aç")).toBeNull();
    expect(pool()).toBeNull();
    expect(cardsHidden()).toBe(false);
  });

  it("opens the pool in the middle on Referanstan, with the panel beside it", async () => {
    await open("havuz-b");

    await openReferanstan();

    expect(pool()).toBeTruthy();
    expect(cardsHidden()).toBe(true);
    expect(screen.getByRole("heading", { name: "Video üret" })).toBeTruthy();
  });

  it("closes the pool and opens it again with one button", async () => {
    await open("havuz-c");
    await openReferanstan();

    fireEvent.click(screen.getByText("Referansları kapat"));

    expect(pool()).toBeNull();
    expect(cardsHidden()).toBe(false);

    await act(async () => { fireEvent.click(screen.getByText("Referansları aç")); });

    expect(pool()).toBeTruthy();
  });

  it("gives the cards back on Kareden, and Referanstan opens a closed pool again", async () => {
    await open("havuz-d");
    await openReferanstan();
    fireEvent.click(screen.getByText("Referansları kapat"));

    fireEvent.click(tab("Kareden"));
    expect(pool()).toBeNull();

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    expect(pool()).toBeTruthy();
  });

  it("gives the cards back when another panel opens, or the panel closes", async () => {
    await open("havuz-e");
    await openReferanstan();

    fireEvent.click(screen.getByLabelText("Ses üret"));
    expect(pool()).toBeNull();
    expect(cardsHidden()).toBe(false);

    fireEvent.click(screen.getByLabelText("Video üret"));
    // A panel opened from the rail starts on Kareden (madde 317), so the cards stay.
    expect(tab("Kareden").className).toContain("is-on");
    expect(pool()).toBeNull();

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    // The video panel's own icon closes it.
    fireEvent.click(screen.getByLabelText("Video üret"));
    expect(pool()).toBeNull();
  });
});
```

## Görev 4: Koşu ve kırmızı commit

- [ ] **Adım 1: Dört satırı koş** — vitest'te 1–10 kırmızı; öteki üç satır yeşil.
- [ ] **Adım 2: Kırmızı commit** — testler, spec, plan: `test(m318): …(red)`.
