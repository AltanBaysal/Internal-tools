# Madde 319 — Havuzun sırası, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Spec'in dört testi — kırmızı.

**Spec:** [m319 test turu](../specs/2026-09-24-queen-editor-m319-havuz-sirasi-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**. Testler dört satırla koşulur; kaynak kod değişmiyor.

---

## Görev 1: `ReferencePanel.test.jsx`

İmport satırına `within`. Dosyanın sonuna:

```jsx
describe("ReferencePanel — what a row shows (madde 319)", () => {
  const tile = (container, name) => container.querySelector(`[data-reference="${name}"]`);
  const addCard = (container, kind) => container.querySelector(`[data-add="${kind}"]`);

  it("draws each reference at 144 × 108 with its slot number on it", async () => {
    const { container } = await open(pool([
      { name: "bir.png", kind: "picture", seconds: null, slot: 1 },
      { name: "iki.png", kind: "picture", seconds: null, slot: 2 },
    ]));

    // The number a prompt calls it by: the N of <Picture N>.
    expect(within(tile(container, "iki.png")).getByText("2")).toBeTruthy();
    const face = screen.getByAltText("iki.png");
    expect(face.style.width).toBe("144px");
    expect(face.style.height).toBe("108px");
  });

  it("follows a row's last reference with one Ekle card", async () => {
    const { container } = await open();

    const card = addCard(container, "picture");
    expect(card.textContent).toContain("Ekle");
    // After the reference, not before it: a new one goes in at the end.
    expect(card.previousElementSibling).toBe(tile(container, "kedi.png"));
  });

  it("gives a full row no Ekle card", async () => {
    const { container } = await open(pool([1, 2, 3].map((slot) => (
      { name: `klip-${slot}.mp4`, kind: "video", seconds: 3, slot }))));

    expect(addCard(container, "video")).toBeNull();
    expect(addCard(container, "picture")).toBeTruthy();
  });

  it("shows an empty pool as three rows holding only their Ekle cards", async () => {
    const { container } = await open(pool([]));

    expect(["picture", "video", "audio"].map((kind) => Boolean(addCard(container, kind))))
      .toEqual([true, true, true]);
    expect(container.querySelector("[data-reference]")).toBeNull();
  });
});
```

## Görev 2: Koşu ve kırmızı commit

- [ ] Dört satır — vitest'te dört test kırmızı, öteki üç satır yeşil.
- [ ] `test(m319): …(red)`.
