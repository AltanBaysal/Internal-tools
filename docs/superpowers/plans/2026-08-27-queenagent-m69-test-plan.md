# Madde 69 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m69-dokuman-guncellenir-testler-design.md](../specs/2026-08-27-queenagent-m69-dokuman-guncellenir-testler-design.md)
**Bu turda kod yazılmaz.** Altı test kırmızıya döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## 1 · `backend/tests/test_tools.py`

### Silinen iki test

Konularını kaybediyorlar; ikisi de numaralı kopyayı tarif ediyor.

```python
def test_creating_reports_the_name_actually_used(tmp_path):   # satır 102
def test_a_created_file_reports_the_name_it_actually_got(tmp_path):   # satır 295
```

### Gelen beş test

`test_reading_a_file_that_is_not_there_is_an_answer_not_a_crash`'in altına, yani yaratmanın
testlerinin durduğu yere:

```python
# --- creating over a name that is taken (Madde 69) ------------------------------------------------
#
# It used to number: plan.md became plan-2.md and the project held two versions of one document. The
# way to change a file that exists is edit_file, and until now reaching for it was the model's own
# choice -- which is the kind of thing FOUNDATION 5 says code decides.


def test_creating_over_a_name_that_is_taken_writes_nothing(tmp_path):
    files = _with(tmp_path, "plan.md", "first")
    _call(files, "create_file", name="plan.md", content="second")
    assert _call(files, "read_file", name="plan.md") == "first"
    # And no copy beside it: refusing means one document, which was the whole point.
    assert _call(files, "list_files") == "plan.md"


def test_a_refused_create_points_at_the_tool_that_can_do_it(tmp_path):
    # The tool result is the instruction. Saying only "there is already one" would leave the model
    # to guess the next move, and guessing is what put it here.
    files = _with(tmp_path, "plan.md", "first")
    assert "edit_file" in _call(files, "create_file", name="plan.md", content="second")


def test_a_refused_create_brings_no_file_into_being(tmp_path):
    # No card: nothing was born. The same rule edit_file follows.
    files = _with(tmp_path, "plan.md", "first")
    refused = run_tool(files, "p1", "create_file", json.dumps({"name": "plan.md", "content": "x"}))
    assert refused.created is None


def test_a_refused_create_names_the_file_that_was_in_the_way(tmp_path):
    # The call was about that file, and the card says which. It used to name plan-2.md -- a file
    # that only existed because of the numbering this item took away.
    files = _with(tmp_path, "plan.md", "first")
    assert _target(files, "create_file", name="plan.md", content="second") == "plan.md"


def test_a_refused_create_does_not_say_it_saved(tmp_path):
    files = _with(tmp_path, "plan.md", "first")
    assert _outcome(files, "create_file", name="plan.md", content="second") == "Already there"
```

`_target` ve `_outcome` dosyanın ilerisinde tanımlı; bu testler onlardan sonra da durabilir, ama
konusuna göre yaratmanın yanında duruyorlar ve Python tanım sırasını umursamıyor.

### Duran testler

`test_a_taken_name_gets_a_number_rather_than_overwriting` ve
`test_a_name_with_no_extension_is_numbered_the_same_way` **yeşil kalıyor**: ikisi de `unique_name`'i
doğrudan sınıyor, ve o fonksiyon yerinde duruyor — çöp onu kullanmaya devam ediyor.

Boş bir ada yazmanın testleri de duruyor: `test_only_creating_reports_a_born_file`,
`test_creating_says_it_was_saved`, `test_listing_names_the_files`, `test_reading_gives_the_contents`,
`test_listing_says_how_many_files_there_are`. Hiçbiri dolu bir ada yazmıyor.

## 2 · `frontend/src/App.test.jsx`

Dosya kartı testlerinin yanına, `gatedSse` kullanarak:

```jsx
test("a call frame takes the dashed card down", async () => {
  // The dashed card lives between "the model asked" and "the tool answered", and a call frame is
  // the second. Until Madde 69 only a born file took it down, so a tool that wrote nothing left it
  // spinning until the turn ended -- rare then, and the ordinary case now that create_file refuses
  // a name that is taken.
  const owed = { id: "c1", title: "hello", messages: [] };
  const { response, release } = gatedSse(
    'event: chat\ndata: {"chat":"c1"}\n\n' +
      "event: file-start\ndata: {}\n\n" +
      'event: call\ndata: {"tool":"create_file","target":"plan.md","outcome":"Already there"}\n\n',
    `event: done\ndata: ${JSON.stringify(owed)}\n\n`,
  );
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") return Promise.resolve(response);
    if (path.endsWith("/chats/c1")) return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "fix the plan" } });
  fireEvent.keyDown(box, { key: "Enter" });

  // The handle is what says the tool answered -- while a turn runs it carries the newest call, and
  // the outcome itself is behind the door. Waiting for it is what makes the dashed card's absence
  // mean something: without it this would also pass on a card that never went up.
  await waitFor(() => expect(screen.getByText("⏺ create_file(plan.md)")).toBeTruthy());
  expect(screen.queryByText("creating file…")).toBeNull();
  release();
});
```

Ölçü çağrı kolunun metni, `outcome` değil. Çağrılar Madde 84'ten beri kapalı bir kapının arkasında
duruyor: koşarken kolun üstünde son çağrının başlığı yazıyor *(`ChatScreen.jsx:59`)*, `outcome` ise
ancak kapı açılınca görünüyor *(`:69`)*. Akan çağrılar bekleyen bloğun içinde *(`:292`)* — kesikli
kartın da durduğu yer, yani ikisi aynı kutuda ölçülüyor.

*İlk yazımı `"Already there"` diyordu ve test kurulum satırında düştü — iddiada değil. Ölçü
düzeltildi.*

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `..._over_a_name_that_is_taken_writes_nothing` | 1 |
| `..._points_at_the_tool_that_can_do_it` | 1 |
| `..._brings_no_file_into_being` | 1 |
| `..._names_the_file_that_was_in_the_way` | 1 |
| `..._does_not_say_it_saved` | 1 |
| `a call frame takes the dashed card down` | 1 |

**Altı.** Sayı bugünkü `tools.py:211-216` ve `useChat.js`'in `file` dışında kartı indiren bir kolu
olmamasından türetiliyor.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `tools.py` ve `useChat.js` bu turda açılmaz.
- **`dist` derlenmez.**
- **`naming.py` açılmaz.**
