# Madde 418 — Kutunun ret kontrolü, test turunun planı

> **Koşum:** bu oturumda, satır satır, madde 418'in kendi dalında. Testler yazılır, dört satır
> koşulur, yeni testlerin kırmızısı görülür, ve kırmızı hâliyle commit'lenir.

**Hedef:** Kutunun her düzgün cevabı ayrı bir istekle, birebir DeepSeek'e kontrol ettirdiğini; yalnız
onayın geçirdiğini; ret ve kontrolün kendi hatasında asıl isteğin aynen yeniden gittiğini; hepsinin
416'nın beşinden düştüğünü; beşi de olmazsa son denemenin türüne göre cümlenin ya da hatanın kendi
metninin döndüğünü; ve hep reddeden bir Queen AI'da üretimin cümleyle bugünkü yoldan durduğunu anlatan
testler.

**Yaklaşım:** 416'nın testleri gibi: kutu gerçek istemciyle ve `Answers`'la — kontrolün isteği de aynı
listeden cevap alır; zincir `test_photo_usecases`'in sahteleri ve `resume_batch`'le; `main.py`'nin
kurduğu yazarlar `requests.post` sahteyle değiştirilerek.

**Araçlar:** pytest (`parametrize`, `monkeypatch`).

**Spec:** [m418 test turu](../specs/2026-10-06-queen-editor-m418-ret-kontrolu-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; kullanıcının gördüğü metin Türkçe.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.
- Hiçbir test ağa çıkmaz.
- `CHECK_INSTRUCTION` kullanıldığı yerde içe aktarılır: toplanamayan bir modül pytest'in bütün
  oturumunu durdurur.
- Cümle testlerde harfi harfine durur: `Model hata döndü, farklı şekilde dene.`

**Arayüz — uygulama turunun vereceği:**
- `backend/services/deepseek/box.py`: `CHECK_INSTRUCTION` (str). `Box(client).ask(system, text="",
  images=()) -> Answer` aynen; her düzgün cevaptan sonra `client.complete(CHECK_INSTRUCTION, cevap)`,
  ve yalnız tam olarak `APPROVED` cevabı geçirir.
- `Answer(text, failed=False)` aynen.

---

## Görev 1: `backend/tests/test_deepseek_box.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_deepseek_box.py`

- [ ] **Adım 1: Modül belgesi, içe aktarmalar ve sabitler.** Belge 418'i anar; `import pytest`
  `import requests`'in üstüne; `PHOTO`'nun altına:

```python
"""The box every request to Queen AI goes through (madde 416), and the check it puts every answer
through (madde 418).

Tried with the real one-request client underneath, so the failures the box sees are the very ones the
client raises: the server answers each request with the next of a list -- the check's request among
them -- and the box is asked once.

The box is imported where it is used rather than at the top: a module that cannot be imported would
fail collection, and pytest stops the whole session on a collection error.
"""
import pytest
import requests
```

```python
PHOTO = ("P0_0.png", b"PNGDATA")

# What the check says of an answer it lets through, and of one it does not (madde 418).
APPROVED = answering("APPROVED")
REFUSAL = answering("REFUSAL")
# A model declining, in the words DeepSeek uses.
SORRY = answering("I'm sorry, I can't help with that.")
# What the box tells its caller when the last try was refused (v9-3), letter for letter.
SENTENCE = "Model hata döndü, farklı şekilde dene."
```

- [ ] **Adım 2: `asking`'in altına kontrolün metnini okuyan yardımcı.**

```python
def _check_instruction():
    from backend.services.deepseek.box import CHECK_INSTRUCTION
    return CHECK_INSTRUCTION
```

- [ ] **Adım 3: 416'nın düzgün cevap bekleyen beş testi kontrolün onayını da bekler.**

```python
def test_a_good_answer_comes_back_as_it_is_once_the_check_approves_it():
    http = Answers([answering(" she turns "), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns"
    assert answer.failed is False
    # The answer's request, then its check: nothing more.
    assert len(http.calls) == 2


def test_an_http_error_sends_the_same_request_again():
    http = Answers([FakeResponse(status_code=500, text="iç hata"), answering("she turns"),
                    APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    # The same request, word for word and picture for picture: nothing about it was wrong.
    assert len(http.calls) == 3
    assert http.calls[1] == http.calls[0]
    assert http.calls[0]["body"]["messages"][1]["content"][0]["type"] == "image_url"


def test_a_malformed_answer_sends_the_request_again():
    http = Answers([FakeResponse({"choices": []}, text='{"choices": []}'),
                    answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 3


def test_an_empty_answer_sends_the_request_again():
    http = Answers([answering("   "), answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 3


def test_no_answer_at_all_sends_the_request_again():
    """No internet, a timeout: the owner's technical errors (v9-3) are tried again like an HTTP
    one."""
    http = Answers([requests.ConnectionError("Max retries exceeded with url: /chat/completions"),
                    answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 3
```

Altı, yedi, sekiz ve dokuzuncu testler aynen: hiçbirinde cevap gelmiyor, yani kontrol de yok.

- [ ] **Adım 4: Dosyanın sonuna 418'in testleri.**

```python
# --- Madde 418: the check ------------------------------------------------------------------------

def test_the_answer_is_checked_word_for_word_in_a_request_of_its_own():
    """The owner's words (v9-3): the text that came back goes to DeepSeek as it is, in a request of
    its own, to be checked. The check is shown the answer alone -- not the request, not the
    pictures."""
    said = ("integrated_multimodal_description: [Shot 1] she turns\n\n"
            "overall_soundscape: Silk rustles. No one speaks.")
    http = Answers([answering(said), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == said and answer.failed is False
    asked, check = http.calls
    assert check["url"] == asked["url"]
    assert check["headers"] == asked["headers"]
    assert check["timeout"] == asked["timeout"]
    assert check["body"] == {
        "model": "deepseek-flash",
        "messages": [{"role": "system", "content": _check_instruction()},
                     {"role": "user", "content": [{"type": "text", "text": said}]}],
    }


@pytest.mark.parametrize("verdict", ["REFUSAL", "I'm unable to review this content."],
                         ids=["refusal", "the-check-s-own-words"])
def test_anything_but_the_approval_sends_the_same_request_again(verdict):
    """Only an approval lets an answer through -- the owner's "onay verirse ... yoksa tekrardan
    istek atıyoruz". Anything else the check says, a check that will not judge included, is a
    refusal, and the request goes again as it was."""
    http = Answers([SORRY, answering(verdict), answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 4
    assert http.calls[2] == http.calls[0]


def test_an_error_of_the_check_itself_is_a_try_and_the_request_goes_again():
    http = Answers([answering("she turns"), FakeResponse(status_code=503, text="meşgul"),
                    answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 4
    assert http.calls[2] == http.calls[0]


def test_five_refusals_come_back_as_the_sentence_after_ten_requests():
    """The box never raises, refused or not: a caller that loops must not be broken by it (v9-3).
    A refusal is not passed on in the model's words -- the caller is told to ask another way."""
    http = Answers([SORRY, REFUSAL] * 5 + [answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert len(http.calls) == 10
    assert answer.failed is True
    assert answer.text == SENTENCE


def test_errors_and_refusals_spend_the_same_five_tries_and_a_last_refusal_says_the_sentence():
    http = Answers([FakeResponse(status_code=503, text="meşgul")] * 4
                   + [SORRY, REFUSAL, answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert len(http.calls) == 6
    assert answer.failed is True
    assert answer.text == SENTENCE


def test_a_last_try_that_failed_on_the_wire_comes_back_in_its_own_words_after_refusals():
    """The last try's kind decides what the caller is told: a technical failure in its own words,
    even after four refusals -- here the check's own error."""
    http = Answers([SORRY, REFUSAL] * 4
                   + [answering("she turns"), FakeResponse(status_code=503, text="meşgul"),
                      answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert len(http.calls) == 10
    assert answer.failed is True
    assert answer.text == "DeepSeek HTTP 503\nmeşgul"


def test_the_check_text_asks_for_the_word_the_box_waits_for():
    text = _check_instruction()

    assert "APPROVED" in text and "REFUSAL" in text


def test_the_check_text_speaks_of_an_answer_to_a_request_and_nothing_of_queen_editor_s():
    """QueenAgent's box will send the same text word for word (v10-1b), where the answer is an
    agent's reply rather than a video prompt."""
    text = _check_instruction().lower()

    assert "video" not in text and "prompt" not in text


def test_a_run_whose_queen_ai_keeps_refusing_stops_as_today_with_the_sentence():
    """Madde 418 as its done-sentence says it: a refusal is never written on the card. The run
    loop's three attempts each hold the box's five tries of an answer and its check, and when they
    are spent the run stops the way it always did -- with the box's sentence on the error line, and
    the job still owed."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    store.files["0_a.png"] = b"PNGDATA"
    http = Answers([SORRY, REFUSAL] * 15)
    runner, generator = sync_runner(), FakeGenerator()

    resume_batch(runner, store, record, plan_store, {layers.VIDEO: generator}, lambda: "t",
                 "düğün", writers={layers.VIDEO: H3VideoPromptWriter(asking(http))})

    assert len(http.calls) == 30
    state = runner.status()
    assert state["status"] == "error"
    assert state["error"] == f"Aynı kare 3 kez denendi — üretim durduruldu\n{SENTENCE}"
    assert generator.calls == []
    assert record.written_prompts("düğün") == {}
    assert [row for row in record.rows if row.get("layer") == "video"] == []
```

## Görev 2: `backend/tests/test_composition_root.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_composition_root.py`

- [ ] **Adım 1: 416'nın kapı testi kontrolün onayını da bekler** — adı aynı, dört durumu aynı:

```python
def test_every_queen_ai_prompt_goes_through_the_box(import_main, monkeypatch, video_model, kind):
    """Madde 416 and 418: H3's, WAN's and the sound's writer, as main.py wires them, have a failed
    request sent again and the answer checked -- four HTTP errors, then the fifth try's answer and
    the check's approval, and that answer is the prompt. requests.post is the one the client sends
    with, so no request leaves this machine."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "k-1")
    main = import_main(video_model)
    http = Answers([FakeResponse(status_code=500, text="iç hata")] * 4
                   + [answering("she turns"), answering("APPROVED")])
    monkeypatch.setattr(requests, "post", http.post)

    written = main._writers[kind].write({"photo": "kırmızı elbiseli kadın",
                                         "video": "kadın dönüyor"},
                                        "standard", source=PHOTO, scene="")

    assert written == "she turns"
    assert len(http.calls) == 6
```

## Görev 3: Koşu — kırmızı, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde kırmızı — `test_deepseek_box.py`'de 416'nın değişen beşi ve
418'in on biri (parametreliyle); `test_composition_root.py`'nin kapı testinin dört durumu. Öteki her
şey yeşil. İki vitest satırı bu çalışma ağacında başlayamaz — `node_modules` yok; bu madde ekrana
dokunmuyor.

- [ ] **Adım 2: Commit** — testler, spec ve bu plan, kırmızı hâliyle:

```powershell
git add docs/specs/2026-10-06-queen-editor-m418-ret-kontrolu-testler-design.md docs/plans/2026-10-06-queen-editor-m418-ret-kontrolu-testler-plan.md queen-editor/backend/tests/test_deepseek_box.py queen-editor/backend/tests/test_composition_root.py
git commit -m @'
test(queen-editor): Madde 418 red -- the box has every answer checked by DeepSeek word for word in a request of its own, and only an approval lets it through; a refusal or the check's own error sends the request again within the same five tries; five failed tries return the refusal sentence when the last was a refusal and the error's own text when it was technical; a run whose Queen AI keeps refusing stops as today with that sentence on the error line

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
