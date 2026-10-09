# Madde 401 — Karenin senaryosu, test turunun planı

> **Koşum:** bu oturumda, satır satır. Takımı ve kırmızı commit'i maddeyi koşan ajan yapıyor
> *(yol haritası, Dalga 2)*.

**Hedef:** Spec'in yeni testleri kırmızı; dosyanın öteki testleri yeşil.

**Spec:** [m401 test turu](../specs/2026-10-01-queen-editor-m401-senaryo-testler-design.md)

## Her yere geçerli kurallar

- Tek dosya: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`. Kaynak kod
  değişmiyor.
- Test adı ve yorum **İngilizce**; ekrandaki sözler tasarımdan harfi harfine (*"Senaryo"*, *"Bu
  karenin senaryosu yok"*).
- Uygulamanın tutacağı adlar bu planda sabitleniyor: düğmenin adı `Senaryo`, hâli `aria-pressed`,
  şeridin (`[data-strip]`) son çocuğu, ikonu `[data-glyph=scenario]`; kart `[data-scenario]`.
  `data-scene` değil: o ad oynatıcının sahnesinin.

---

## Görev 1: Sabitler ve iki yardımcı

`facts`'in altına:

```js
// The frame's scenario (madde 401): the sentence QueenAgent's list gave it, for checking the
// prompts against the picture. Two of them, so a card that kept the first frame's sentence shows.
const SCENE = "Kraliçe tahtında oturuyor; salon boş ve karanlık.";
const SECOND_SCENE = "Kraliçe gece bahçede yürüyor, fenerler yanıyor.";
const scenario = () => screen.getByRole("button", { name: "Senaryo" });
const sceneCard = () => document.querySelector("[data-scenario]");
```

## Görev 2: Yeni blok

399'un bloğunun ardına, `SECOND_SOUND`'dan önce:

```js
describe("PhotoDetail — the frame's scenario (madde 401)", () => {
  // The frame carries its scenario so the user can see whether the prompts match the picture. One
  // press lays it over the picture and the next takes it away; nothing here writes it (tasarım 196).
  const SCENED = { ...LAYERED, scene: SCENE };

  it("puts a Senaryo button after the three tabs, set apart by a thin line", async () => {
    await open("P0_0", { frames: [SCENED] });

    const [line, button] = [...document.querySelector("[data-strip]").children].slice(-2);
    expect(button).toBe(scenario());
    expect(line.style.width).toBe("1px");
    expect(line.style.background).toBe("var(--border)");
    // Its own look rather than a fourth tab's: no stroke box and no ground.
    expect(button.className).not.toContain("wf-stroke");
    expect(button.style.background).toBe("none");
    expect(button.querySelector("[data-glyph=scenario]")).toBeTruthy();
  });

  it("starts closed, with nothing laid over the picture", async () => {
    await open("P0_0", { frames: [SCENED] });

    expect(scenario().getAttribute("aria-pressed")).toBe("false");
    expect(sceneCard()).toBeNull();
  });

  it("opens the frame's scenario over the picture on a press, and closes it on the next", async () => {
    await open("P0_0", { frames: [SCENED] });

    fireEvent.click(scenario());

    expect(sceneCard().textContent).toBe(SCENE);
    // Read, never written: the scenario came with QueenAgent's list and no box here holds it.
    expect(screen.queryByDisplayValue(SCENE)).toBeNull();

    fireEvent.click(scenario());

    expect(sceneCard()).toBeNull();
  });

  it("lights the button while the card is open", async () => {
    await open("P0_0", { frames: [SCENED] });
    expect(scenario().style.color).toBe("var(--ink-3)");

    fireEvent.click(scenario());

    expect(scenario().getAttribute("aria-pressed")).toBe("true");
    expect(scenario().style.color).toBe("var(--accent)");
  });

  it("lays the card along the photo's bottom edge, in the page's translucent dark", async () => {
    await open("P0_0", { frames: [SCENED] });

    fireEvent.click(scenario());

    // The owner's pick of the design's three places: the bottom edge. Inside the picture's own box,
    // so the 12 is measured from the photo and not from the stage around it.
    const card = sceneCard();
    expect(card.parentElement.contains(screen.getByAltText("P0_0.png"))).toBe(true);
    expect(card.parentElement.style.position).toBe("relative");
    expect(card.style.position).toBe("absolute");
    expect([card.style.left, card.style.right, card.style.bottom])
      .toEqual(["12px", "12px", "12px"]);
    // The same dark the page's other boxes over the picture stand on.
    expect(card.style.background).toMatch(/rgba\(10,\s*8,\s*7,\s*0?\.72\)/);
    // The player takes a click on the picture to play and pause; the card must never take it.
    expect(card.style.pointerEvents).toBe("none");
  });

  it.each(["Video", "Ses"])("lifts the card over the player's clock on the %s tab", async (name) => {
    await open("P0_0", { frames: [SCENED] });
    fireEvent.click(scenario());

    fireEvent.click(tab(name));

    // The clock and its line, or the waveform, run along the player's bottom: the card stands above
    // that strip instead of covering it.
    expect(sceneCard().parentElement.hasAttribute("data-scene")).toBe(true);
    expect(sceneCard().style.bottom).toBe("40px");
  });

  it("keeps the card on the picture while a layer is made over it", async () => {
    await open("P0_0", { frames: [{ ...RENDERING, scene: SCENE }],
                         status: { status: "running", project: "düğün",
                                   current: { id: "P0_0", type: "video" } } });
    fireEvent.click(scenario());

    fireEvent.click(tab("Video"));

    const box = sceneCard().parentElement;
    expect(box.contains(screen.getByAltText("P0_0.png"))).toBe(true);
    expect(box.querySelector("[data-making]")).toBeTruthy();
    expect(sceneCard().style.bottom).toBe("12px");
  });

  // A frame with no picture yet still has its scenario: it says what the picture is going to be.
  const HELD = { id: "P0_0", file: "P0_0.png", status: "pending", prompt: "p", negative: "",
                 layers: {}, failed: [], owed: ["photo"], prompts: {}, scene: SCENE };
  it.each([
    ["waiting", HELD, IDLE],
    ["being made", HELD, { status: "running", project: "düğün", current: { id: "P0_0" } }],
    ["broken", { ...BROKEN, scene: SCENE }, IDLE],
  ])("lays the card on the holder of a frame that is %s", async (_, frame, status) => {
    await open("P0_0", { frames: [frame], status });

    fireEvent.click(scenario());

    expect(sceneCard().parentElement.className).toContain("wf-img");
    expect(sceneCard().textContent).toBe(SCENE);
  });

  it("says so, dimmed, on a frame with no scenario", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, scene: "" }] });

    fireEvent.click(scenario());

    expect(sceneCard().textContent).toBe("Bu karenin senaryosu yok");
    // Dimmed: a notice about an absence, not a sentence of the frame's own.
    expect(sceneCard().style.color).toMatch(/rgba\(255,\s*255,\s*255,\s*0?\.55\)/);
  });

  it("keeps the card open when the tab changes", async () => {
    await open("P0_0", { frames: [SCENED] });
    fireEvent.click(scenario());

    fireEvent.click(tab("Video"));

    expect(scenario().getAttribute("aria-pressed")).toBe("true");
    expect(sceneCard().textContent).toBe(SCENE);
  });

  it("keeps the card open while the arrows walk to another frame, and reads the new one's", async () => {
    // The arrows swap the frame under a page that stays mounted. The press was the user's, not the
    // frame's, so it walks on with them -- a run of frames checked against their scenarios costs
    // one press.
    listFrames.mockResolvedValue([SCENED, { ...SECOND, scene: SECOND_SCENE }]);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(scenario());

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(scenario().getAttribute("aria-pressed")).toBe("true");
    expect(sceneCard().textContent).toBe(SECOND_SCENE);
  });
});
```

## Görev 3: Koşu ve kırmızı commit

- [ ] Dört satır, paralel. `queen-editor/frontend`: yeni blok kırmızı *(düğme yok — `getByRole`
      bulamaz)*, dosyanın öteki testleri yeşil. Öteki üç satır yeşil.
- [ ] `test(queen-editor): Madde 401 red -- …`.
