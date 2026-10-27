# Madde 324 — Eksik satırı, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Takımı ve commit'i
> koordinatör koşuyor.

**Hedef:** Spec'in dokuz testi ve iki değişen test — kırmızı; 323'ün taşınan testi yeşil.

**Spec:** [m324 test turu](../specs/2026-09-24-queen-editor-m324-eksik-satiri-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; cümleler tasarımdan harfi harfine. Kaynak kod değişmiyor.
- Panelin havuzu `pool` prop'u *(sunucunun `{references, limits}` cevabı)*, üreticinin referans okuyup
  okumadığı video satırının `reads_references`'ı.

---

## Görev 1: `test_producers.py`

`test_the_video_row_names_the_model_the_notebook_installed`'ın ardına:

```python
def test_the_video_row_says_whether_its_model_makes_video_from_references():
    """Only H3 has a mode that reads the pool (madde 302), and the video panel says so before the
    press (madde 324). It reads it here rather than off the model's name: the name is a word for the
    box, and the rule is the server's."""
    for model, reads in (("h3", True), ("wan", False), ("", False)):
        assert list_producers(GROUPS, FakeFiles(), model)[1]["reads_references"] is reads, model
```

## Görev 2: `test_reference_usecases.py`

`test_a_reference_run_with_an_empty_pool_is_refused`, yerinde:

```python
def test_a_reference_run_with_an_empty_pool_is_refused():
    """Word for word the line the video panel shows above its button (madde 324): one state, one
    sentence, whichever side says it first."""
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(references.PoolLimit) as exc:
        run(store, pool, FakeOrderStore())

    assert str(exc.value) == "Havuzda referans yok — önce en az bir referans ekle."
```

## Görev 3: `LayerPanel.test.jsx`

Dosyanın sonuna yeni blok:

```jsx
describe("LayerPanel — what stops a run from the pool (madde 324)", () => {
  // The design's own sentences (V2-UPDATE §1); the second is the server's too.
  const H3_ONLY =
    "Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli kurulu.";
  const NO_REFERENCES = "Havuzda referans yok — önce en az bir referans ekle.";
  const LIMITS = { picture: 9, video: 3, audio: 3 };
  // The pool the way the server answers it.
  const pool = (references) => ({ references, limits: LIMITS });
  const EMPTY = pool([]);
  const KEDI = pool([{ name: "kedi.png", kind: "picture", seconds: null, slot: 1 }]);
  // The video row as the server gives it: whether its model reads references is the server's to say.
  const H3 = { id: "video", name: "Video üreticisi", installed: true, model: "MiniMax H3",
               reads_references: true };
  const WAN = { ...H3, model: "WAN 2.2 I2V", reads_references: false };
  const MISSING = { ...WAN, installed: false };

  const promptBox = () => screen.getByLabelText("Prompt listesi");
  const addButton = () => screen.getByText("Kuyruğa ekle").closest("button");
  const write = (text) => fireEvent.change(promptBox(), { target: { value: text } });

  // One project per test, and the same one when a test hands the panel a new pool: a rerender of
  // the same panel, as when the pool in the middle answers again.
  async function openReference(props) {
    const project = freshProject();
    const panel = (more) => (
      <LayerPanel layer="video" project={project} frames={FRAMES} selected={[]} producer={H3}
                  onQueue={() => Promise.resolve({ added: 1 })} onInstall={() => {}}
                  poolShown={false} onShowPool={() => {}} {...props} {...more} />
    );
    const view = render(panel());
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    return { again: (more) => view.rerender(panel(more)) };
  }

  it("says an empty pool before anything is pressed, between the variant box and the button",
     async () => {
    await openReference({ pool: EMPTY });

    const line = screen.getByText(NO_REFERENCES);
    // Right above the button it stops: the design's own place for it.
    expect(variantBox().compareDocumentPosition(line) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
    expect(line.compareDocumentPosition(addButton()) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
  });

  it("lets the line go the moment the pool holds one reference of any kind", async () => {
    const view = await openReference({ pool: EMPTY });
    write('["gotik kız"]');
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();
    expect(addButton().disabled).toBe(true);

    // A sound alone: one reference of any kind is enough (V2-UPDATE §1).
    view.again({ pool: pool([{ name: "kisa.wav", kind: "audio", seconds: 3, slot: 1 }]) });

    expect(screen.queryByText(NO_REFERENCES)).toBeNull();
    expect(addButton().disabled).toBe(false);
  });

  it("says H3 is needed on a session with another video model, and keeps the button closed",
     async () => {
    await openReference({ producer: WAN, pool: KEDI });
    write('["gotik kız"]');

    expect(screen.getByText(H3_ONLY)).toBeTruthy();
    expect(addButton().disabled).toBe(true);
  });

  it("says one thing at a time, in the app's order: the model before the pool", async () => {
    await openReference({ producer: WAN, pool: EMPTY });

    expect(screen.getByText(H3_ONLY)).toBeTruthy();
    expect(screen.queryByText(NO_REFERENCES)).toBeNull();
  });

  it("leaves the model to the install card while the video producer is missing", async () => {
    // With no video model there is no wrong one: the card at the top says what is missing.
    await openReference({ producer: MISSING, pool: EMPTY });

    expect(screen.queryByText(H3_ONLY)).toBeNull();
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();
  });

  it("keeps the button closed while the prompt box is empty", async () => {
    await openReference({ pool: KEDI });
    expect(addButton().disabled).toBe(true);

    write("  \n ");
    expect(addButton().disabled).toBe(true);

    write('["gotik kız"]');
    expect(addButton().disabled).toBe(false);
  });

  it("keeps the line and its locks to Referanstan", async () => {
    await openReference({ pool: EMPTY });
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();

    fireEvent.click(tab("Kareden"));

    // The frame form is as it was: nothing it lacks locks it before the press (Fark 27).
    expect(screen.queryByText(NO_REFERENCES)).toBeNull();
    expect(addButton().disabled).toBe(false);
  });
});
```

## Görev 4: `ProjectScreen.test.jsx`

İçe aktarmaya `listReferences` ve `uploadReferences`. Api taklidinde `listReferences: vi.fn()` — sabit
cevap gidiyor. `renderScreen`'in ardına, dosyanın `beforeEach`'i yerine:

```jsx
const LIMITS = { picture: 9, video: 3, audio: 3 };
const KEDI = { name: "kedi.png", kind: "picture", seconds: null, slot: 1 };

// The pool the way the server keeps it: a file that goes up is in every listing after it. The video
// panel's missing line reads the pool (madde 324), so a test that presses from it says what it holds.
function poolServer(references) {
  let held = references;
  listReferences.mockImplementation(async () => ({ references: held, limits: LIMITS }));
  // One file per pick, at the end of its own row (madde 320).
  uploadReferences.mockImplementation(async (project, [file], kind) => {
    held = [...held, { name: file.name, kind, seconds: null,
                       slot: held.filter((one) => one.kind === kind).length + 1 }];
    return { references: held, limits: LIMITS };
  });
}

beforeEach(() => {
  vi.clearAllMocks();
  poolServer([]);
});
```

323'ün testi, yorumunun sonuna bir cümle ve ilk satırı:

```jsx
    // With a reference in the pool: an empty one closes the button before any press (madde 324).
    poolServer([KEDI]);
```

323'ün bloğunun ardına yeni blok:

```jsx
describe("ProjectScreen — what stops a run from the pool (madde 324)", () => {
  const NO_REFERENCES = "Havuzda referans yok — önce en az bir referans ekle.";
  const button = () => screen.getByText("Kuyruğa ekle").closest("button");

  it("lets the line go once a reference lands in the middle, and opens the button for a list",
     async () => {
    // The pool in the middle and the line in the panel read the same pool. The wire between them is
    // what this test is for: the panel's own tests hand it the pool by hand.
    renderScreen("boş-havuz");
    await act(async () => {});
    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Referanstan" })); });
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();
    expect(button().disabled).toBe(true);

    const file = new File([new Uint8Array([1])], "kedi.png", { type: "image/png" });
    await act(async () => {
      fireEvent.change(screen.getByLabelText("fotoğraf ekle"), { target: { files: [file] } });
    });

    expect(screen.queryByText(NO_REFERENCES)).toBeNull();
    // Still closed: nothing is written in the prompt box yet.
    expect(button().disabled).toBe(true);
    fireEvent.change(screen.getByLabelText("Prompt listesi"),
                     { target: { value: '["gotik kız"]' } });
    expect(button().disabled).toBe(false);
  });
});
```

## Görev 5: Koşu ve kırmızı commit — koordinatörün

- [ ] Dört satır, kolun worktree'sinde, yazıldığı gibi ve paralel.
- [ ] Beklenen kırmızı: `test_producers.py`'de yeni test *(`KeyError: 'reads_references'`)*,
      `test_reference_usecases.py`'de değişen test *(cümle hâlâ `soldaki panele`)*; `queen-editor`
      vitest'te LayerPanel'in yedi yeni testi ve ProjectScreen'in yeni testi *(satır yok, boş kutuda
      düğme açık)*. Yeşil: 323'ün taşınan testi, geri kalan her şey, `queen-agent` vitest'i.
- [ ] Spec, plan ve dört test dosyası tek commit'te: `test(m324): …(red)`.
