# Madde 419 — Kutunun araçlı isteği, test turunun planı

> **Koşum:** bu oturumda, satır satır, madde 419'un kendi dalında. Testler yazılır, dört satır
> koşulur, yeni testlerin kırmızısı görülür, ve kırmızı hâliyle commit'lenir.

**Hedef:** Kutunun konuşmayı ve araçları da DeepSeek'e olduğu gibi gönderdiğini; cevabı bütün —
metni ya da araç çağrıları — döndüğünü; araç çağrısının kontrolsüz geçtiğini, metnin 418'deki gibi
kontrol edildiğini; hata ve retten sonra aynı konuşmanın aynı beşten yeniden gittiğini; ve başarısız
cevabın ret mi teknik mi olduğunu söylediğini anlatan testler.

**Yaklaşım:** 416 ve 418'in testleri gibi: kutu gerçek istemciyle ve `Answers`'la; araç çağrılı cevap
DeepSeek'in biçiminde (`content` `null`, `tool_calls` listesi).

**Araçlar:** pytest (`parametrize`).

**Spec:** [m419 test turu](../specs/2026-10-06-queen-editor-m419-aracli-istek-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; kullanıcının gördüğü metin Türkçe.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.
- Hiçbir test ağa çıkmaz.
- Kutu kullanıldığı yerde içe aktarılır (`asking`), bugünkü gibi: `converse` yokken testler
  çağırdıkları yerde kırmızıya düşer, toplanırken değil.
- Cümle testlerde harfi harfine durur: `Model hata döndü, farklı şekilde dene.`

**Arayüz — uygulama turunun vereceği:**
- `Box(client).converse(messages, tools=()) -> Answer`; `tools` boşsa istekte `tools` yok.
- `Answer(text, failed=False, refused=False, tool_calls=[])` — `tool_calls` DeepSeek'in gönderdiği
  çağrılar, yoksa `[]`; `refused` başarısızlık retse `True`.
- `Box.ask(system, text="", images=())` aynen.

---

## Görev 1: `backend/tests/test_deepseek_box.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_deepseek_box.py`

- [ ] **Adım 1: Modül belgesi 419'u anar.**

```python
"""The box every request to Queen AI goes through (madde 416), the check it puts every answer
through (madde 418), and the conversation with tools it carries for the agent (madde 419).

Tried with the real one-request client underneath, so the failures the box sees are the very ones the
client raises: the server answers each request with the next of a list -- the check's request among
them -- and the box is asked once.

The box is imported where it is used rather than at the top: a module that cannot be imported would
fail collection, and pytest stops the whole session on a collection error.
"""
```

- [ ] **Adım 2: Dosyanın sonuna 419'un sabitleri ve testleri.**

```python
# --- Madde 419: the conversation with tools ------------------------------------------------------

# A conversation the way the agent's loop holds it (madde 420): its instruction, the user's question,
# a tool call the model made and what the tool said back.
READ_FRAME = {"id": "call_1", "type": "function",
              "function": {"name": "read_frame", "arguments": '{"frame": 3}'}}
HISTORY = [{"role": "system", "content": "talimat"},
           {"role": "user", "content": "3 numaralı karede ne var?"},
           {"role": "assistant", "content": "", "tool_calls": [READ_FRAME]},
           {"role": "tool", "tool_call_id": "call_1", "content": "Kare 3: kırmızı elbiseli kadın"}]
TOOLS = [{"type": "function",
          "function": {"name": "read_frame", "description": "Reads one frame of the open project.",
                       "parameters": {"type": "object",
                                      "properties": {"frame": {"type": "integer"}},
                                      "required": ["frame"]}}}]
# The calls the model makes next.
LOOK = {"id": "call_2", "type": "function",
        "function": {"name": "look_at_frame", "arguments": '{"frame": 3}'}}
READ_NEXT = {"id": "call_3", "type": "function",
             "function": {"name": "read_frame", "arguments": '{"frame": 4}'}}
SAID = "Kare 3'te kırmızı elbiseli bir kadın var."


def calling(*calls, text=None):
    """DeepSeek answering with tool calls, the way it sends them: with no words, the content is
    null."""
    return FakeResponse({"choices": [{"message": {"role": "assistant", "content": text,
                                                  "tool_calls": list(calls)}}]})


def test_the_conversation_and_the_tools_go_to_deepseek_as_they_are():
    http = Answers([answering(SAID), APPROVED])

    asking(http).converse(HISTORY, TOOLS)

    asked = http.calls[0]
    assert asked["url"] == URL
    assert asked["headers"]["Authorization"] == "Bearer k-1"
    assert asked["timeout"] == 120
    assert asked["body"] == {"model": "deepseek-flash", "messages": HISTORY, "tools": TOOLS}


def test_without_tools_the_request_offers_none():
    """QueenAgent's last round is offered nothing to call, and 420 does what QueenAgent does at the
    step limit (v9-4)."""
    http = Answers([answering(SAID), APPROVED])

    asking(http).converse(HISTORY)

    assert http.calls[0]["body"] == {"model": "deepseek-flash", "messages": HISTORY}


def test_a_tool_call_comes_back_whole_and_unchecked():
    """Only words are checked (v9-3): an answer that calls a tool goes back with no check request."""
    http = Answers([calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.tool_calls == [LOOK]
    assert answer.text == ""
    assert answer.failed is False and answer.refused is False
    assert len(http.calls) == 1


def test_words_beside_tool_calls_come_back_with_them_unchecked():
    http = Answers([calling(LOOK, READ_NEXT, text=" Kareye bakıyorum. ")])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.text == "Kareye bakıyorum."
    assert answer.tool_calls == [LOOK, READ_NEXT]
    assert len(http.calls) == 1


def test_a_text_answer_is_checked_the_way_a_prompt_is():
    http = Answers([answering(SAID), APPROVED])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.text == SAID and answer.tool_calls == []
    assert answer.failed is False and answer.refused is False
    asked, check = http.calls
    assert check["url"] == asked["url"]
    assert check["headers"] == asked["headers"]
    assert check["timeout"] == asked["timeout"]
    assert check["body"] == {
        "model": "deepseek-flash",
        "messages": [{"role": "system", "content": _check_instruction()},
                     {"role": "user", "content": [{"type": "text", "text": SAID}]}],
    }


def test_a_refused_text_answer_sends_the_same_conversation_again():
    http = Answers([SORRY, REFUSAL, calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.tool_calls == [LOOK]
    assert answer.failed is False and answer.refused is False
    assert len(http.calls) == 3
    assert http.calls[2] == http.calls[0]


@pytest.mark.parametrize("failure", [
    FakeResponse(status_code=500, text="iç hata"),
    FakeResponse({"choices": []}, text='{"choices": []}'),
    FakeResponse({"choices": [{"message": {"role": "assistant", "content": None}}]},
                 text='{"choices": [{"message": {"role": "assistant", "content": null}}]}'),
    requests.ConnectionError("Max retries exceeded with url: /chat/completions"),
], ids=["http-error", "malformed", "neither-words-nor-calls", "no-answer-at-all"])
def test_a_failed_request_sends_the_same_conversation_again(failure):
    http = Answers([failure, calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.tool_calls == [LOOK] and answer.failed is False
    assert len(http.calls) == 2
    assert http.calls[1] == http.calls[0]


def test_five_refused_text_answers_come_back_as_the_sentence_marked_as_a_refusal():
    """The screen draws a refusal and a technical failure as two different error cards (madde 425),
    so the box says which one it gave up on."""
    http = Answers([SORRY, REFUSAL] * 5 + [calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert len(http.calls) == 10
    assert answer.failed is True and answer.refused is True
    assert answer.text == SENTENCE
    assert answer.tool_calls == []


def test_five_technical_failures_come_back_in_their_own_words_and_not_as_a_refusal():
    busy = [FakeResponse(status_code=503, text=f"meşgul {n}") for n in range(1, 6)]
    http = Answers(busy + [calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert len(http.calls) == 5
    assert answer.failed is True and answer.refused is False
    assert answer.text == "DeepSeek HTTP 503\nmeşgul 5"
    assert answer.tool_calls == []


def test_a_last_try_that_failed_on_the_wire_is_not_a_refusal_after_refusals():
    lost = requests.ConnectionError("Max retries exceeded with url: /chat/completions")
    http = Answers([SORRY, REFUSAL] * 4 + [lost, calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert len(http.calls) == 9
    assert answer.failed is True and answer.refused is False
    assert answer.text == str(lost)


def test_without_a_key_nothing_is_sent_and_the_failure_is_technical():
    http = Answers([calling(LOOK)])

    answer = asking(http, api_key="").converse(HISTORY, TOOLS)

    assert http.calls == []
    assert answer.failed is True and answer.refused is False
    assert "DEEPSEEK_API_KEY" in answer.text


@pytest.mark.parametrize("answers, refused", [
    ([SORRY, REFUSAL] * 5, True),
    ([FakeResponse(status_code=503, text="meşgul")] * 5, False),
], ids=["refusal", "technical"])
def test_a_prompt_s_failure_says_whether_it_was_a_refusal_too(answers, refused):
    answer = asking(Answers(answers)).ask("talimat", "", [PHOTO])

    assert answer.failed is True
    assert answer.refused is refused
```

## Görev 2: Koşu — kırmızı, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde 16 kırmızı, hepsi `test_deepseek_box.py`'de — `converse`'i
çağıran on bir test (parametrelinin dördüyle on dört durum) `AttributeError: 'Box' object has no
attribute 'converse'`, ve `ask`'ın parametreli testinin iki durumu `AttributeError: 'Answer' object
has no attribute 'refused'`. Öteki her şey yeşil. İki vitest satırı bu çalışma ağacında başlayamaz —
`node_modules` yok; bu madde ekrana dokunmuyor.

- [ ] **Adım 2: Commit** — testler, spec ve bu plan, kırmızı hâliyle:

```powershell
git add docs/superpowers/specs/2026-10-06-queen-editor-m419-aracli-istek-testler-design.md docs/superpowers/plans/2026-10-06-queen-editor-m419-aracli-istek-testler-plan.md queen-editor/backend/tests/test_deepseek_box.py
git commit -m @'
test(queen-editor): Madde 419 red -- the box also carries a conversation with tools: they go to DeepSeek as they are, with no tools key when none are given; a tool call comes back whole and unchecked, words beside it included; a text answer is checked the way a prompt is; an error or a refusal sends the same conversation again within the same five tries; a failure says whether it was a refusal or technical, on both paths

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
