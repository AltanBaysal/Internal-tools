# Madde 323 — Prompt listesinin okunuşu, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Spec'in dört testi ve iki değişen ekran testi — kırmızı.

**Spec:** [m323 test turu](../specs/2026-09-24-queen-editor-m323-prompt-listesi-okunusu-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; cümleler tasarımdan harfi harfine. Kaynak kod değişmiyor.

---

## Görev 1: `LayerPanel.test.jsx`

*"LayerPanel — producing from the reference pool"* bloğunda,
`counts the cards the press would make`'in ardına üç yeni test:

```jsx
  it("reads a Python list with a name in front, the way the photo panel does", () => {
    // Madde 323: a list that works in the photo panel works here -- pasted out of a notebook cell,
    // in single quotes, with its name in front.
    openReference();

    fireEvent.change(promptBox(), { target: { value: "PROMPTS = ['a', 'b']" } });

    expect(screen.getByText("2 prompt × 1 varyant = 2 kart")).toBeTruthy();
  });

  it("reads a tuple, in either quote", () => {
    openReference();

    fireEvent.change(promptBox(), { target: { value: `("gotik kız", 'dans')` } });

    expect(screen.getByText("2 prompt × 1 varyant = 2 kart")).toBeTruthy();
  });

  it("leaves the blank items out of the count", () => {
    // An empty item is how a line is switched off in the photo panel's list (prompt_list.py).
    openReference();

    fireEvent.change(promptBox(), { target: { value: '["gotik kız", "", "  ", "dans"]' } });

    expect(screen.getByText("2 prompt × 1 varyant = 2 kart")).toBeTruthy();
  });
```

Değişen iki test, yerlerinde:

```jsx
  it("says nothing under the button while the box is empty or its list cannot be read", () => {
    // Madde 323: the line counts what a press would make and nothing else. What is wrong with a
    // list is the server's to say, when the button is pressed.
    openReference();
    expect(screen.queryByText(/biçiminde olmalı/)).toBeNull();

    fireEvent.change(promptBox(), { target: { value: "gotik kız" } });

    expect(screen.queryByText(/= \d+ kart/)).toBeNull();
    expect(screen.queryByText(/biçiminde olmalı/)).toBeNull();
    expect(screen.queryByText(/Format hatası/)).toBeNull();
  });

  it("sends a list it cannot read as it was typed", async () => {
    // Madde 323: the screen reads the list only to count it. The press goes whatever that reading
    // made of it, and the refusal comes back in the server's own words (prompt_list.py).
    const onQueue = vi.fn().mockResolvedValue(null);
    openReference({ onQueue });

    fireEvent.change(promptBox(), { target: { value: "gotik kız" } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "reference", "gotik kız");
    expect(screen.queryByText(/biçiminde olmalı/)).toBeNull();
  });
```

## Görev 2: `ProjectScreen.test.jsx`

İçe aktarmaya `produceFromReferences` ve `saveReferenceSettings`; API taklidine
`produceFromReferences: vi.fn()`. Madde 318'in bloğunun ardına — sona değil: dosyanın sonundaki
`keeps it quiet until the server has said something` `getStatus`'u hiç dönmeyen bir sözle bırakıyor,
ve ardından gelen her test onu miras alıyor.

```jsx
describe("ProjectScreen — a prompt list the server cannot read (madde 323)", () => {
  it("says the server's own sentence under the button", async () => {
    // The screen reads the list only to count it. What cannot be read goes to the server, which
    // refuses it in the photo panel's words, and the answer lands in the panel that was pressed.
    saveReferenceSettings.mockResolvedValueOnce(null);
    produceFromReferences.mockRejectedValueOnce(new Error("Format hatası — liste okunamadı"));
    renderScreen("liste-a");
    await act(async () => {});
    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Referanstan" })); });
    fireEvent.change(screen.getByLabelText("Prompt listesi"), { target: { value: "gotik kız" } });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(produceFromReferences).toHaveBeenCalledWith("liste-a", "gotik kız", 1);
    expect(screen.getByText("Format hatası — liste okunamadı")).toBeTruthy();
  });
});
```

## Görev 3: Koşu ve kırmızı commit

- [ ] Önce ayrı bir `cd /d/Github/Internal-tools-kol-b`, sonra dört satır paralel, yazıldığı gibi.
- [ ] Beklenen: `queen-editor` vitest'te altı test kırmızı — üç sayım testi eski cümleyi bulup
      sayıyı bulamadığı için, boş satır testi eski cümle durduğu için, iki basış testi istek ekranda
      kesildiği için. Pytest'ler ve `queen-agent` vitest'i yeşil.
- [ ] Spec, plan ve iki test dosyası tek commit'te: `test(m323): …(red)`.
