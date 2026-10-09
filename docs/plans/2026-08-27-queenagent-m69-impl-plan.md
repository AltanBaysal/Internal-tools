# Madde 69 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m69-dokuman-guncellenir-uygulama-design.md](../specs/2026-08-27-queenagent-m69-dokuman-guncellenir-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `e4659ba`'nın altı kırmızısı yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
`npm run build --prefix queen-agent/frontend`

---

## 1 · `backend/features/workspace/domain/tools.py`

### `create_file` dalı

```python
    if name == "create_file":
        wanted = safe_name(args.get("name"))
        # Asked of the names rather than by reading the file: the question is whether the name is
        # taken, and pulling a whole document back to learn that is work nobody needs.
        if wanted in file_store.list_names(project_id):
            # The sentence is the instruction. Saying only that one exists would leave the next
            # move to a guess, and a guess is what put the model here.
            return ToolResult(
                f"There is already a file called {wanted}. Use edit_file to change it, or pick "
                "another name for a new document.",
                None,
                wanted,
                "Already there",
            )
        written = file_store.write(project_id, wanted, args.get("content", ""))
        # The name it got, which is the cleaned one rather than whatever the model wished for. Not
        # repeated in the outcome: the line above already carries it.
        return ToolResult(f"Saved as {written}.", written, written, "Saved")
```

Bugünkü yorum *"The name it got, not the one it asked for"* diyor ve gerekçesi numaralandırmaydı;
gerekçe değişti, cümle de.

### Import

```python
from backend.features.workspace.domain.naming import unique_name
```

satırı gidiyor: dosyada başka kullanıcısı yok. `naming.py` açılmıyor — çöp `unique_name`'i
kullanmaya devam ediyor.

### `create_file`'ın tarifi

`TOOL_SPECS` içindeki açıklamaya bir cümle ekleniyor:

```python
            "description": (
                "Save a document into this project. Reach for it only when the user asked for "
                "something worth keeping as a file. Refuses a name that is already taken: to "
                "change a file that exists, use edit_file."
            ),
```

### `_edit`'in docstring'i

```python
def _edit(file_store, project_id, args):
    """create_file refuses a name that is taken, so this is the only way to change anything."""
```

## 2 · `frontend/src/features/workspace/useChat.js`

`call` kolu kartı da indiriyor:

```javascript
            } else if (frame.event === "call") {
              setStreamingCalls((calls) => [...calls, frame.data]);
              // The dashed card lives between "the model asked" and "the tool answered", and this
              // frame is the second. Only a born file used to take it down, so a tool that wrote
              // nothing left it up until the turn ended.
              setCreatingFile(false);
            } else if (frame.event === "file-start") setCreatingFile(true);
```

`file` kolundaki `setCreatingFile(false)` duruyor: kesikli kartın yerini alan asıl şey dosya kartı,
ve onu bir kare önce indirmek doğru olan. Sıra her zaman `file-start → (file) → call`, yani iki kere
indirmek hiçbir şeyi bozmuyor.

## 3 · Derleme

```
npm run build --prefix queen-agent/frontend
```

`useChat.js` bir ön yüz kaynağı; CLAUDE.md derlenmiş çıktının kaynakla aynı commit'te inmesini
istiyor. `queen-agent/frontend/dist` commit'e giriyor.

## 4 · Doğrulama

| Ölçü | Beklenen |
|---|---|
| `python -m pytest queen-agent -q` | yalnız `test_notebook`'un ikisi kırmızı |
| `npm test --prefix queen-agent/frontend` | hepsi yeşil |

### Koşarken çıkan bir kırmızı daha

`test_stream_answer.py`'nin `test_two_calls_in_one_round_are_both_run`'ı, test turunun envanterinde
kaçtı: iddiası *"bir turdaki iki çağrı da koşar"*, ama ölçüsü aynı adı iki kez yazıp `plan-2.md`
beklemekti — yani numaralı kopyaya yaslanmıştı.

İddia doğru ve duruyor; ölçü büyüyor. İki çağrı iki **ayrı** ada yazıyor ve iki dosya bekleniyor.
Aynı şeyi, artık olmayan bir davranışa yaslanmadan söylüyor.

### Yeşil kalması gerekenler

Boş bir ada yazmanın bütün testleri
*(`test_only_creating_reports_a_born_file`, `test_creating_says_it_was_saved`,
`test_listing_names_the_files`, `test_reading_gives_the_contents`)*, `unique_name`'in kendi iki
testi, ve `a file born mid-answer reaches the rail without a reload` — `file` karesinden sonra `call`
gelmese bile kart iniyor, çünkü o kol yerinde duruyor.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`naming.py`, `stream_answer.py`, `ChatScreen.jsx` açılmaz.**
- **`edit_file`, `write_plan`, `build_prompts` davranışları değişmez.**
- **Diskte duran numaralı kopyalar temizlenmez.**
