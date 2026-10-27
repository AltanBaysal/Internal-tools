# Madde 421 — Queen AI'ın H3 metninde uzunluk yok, test turunun planı

> **Koşum:** bu oturumda, satır satır, ana klasörde (`feat/queen-editor-v9`). Testler yazılır, dört
> satır koşulur, yeni testlerin kırmızısı görülür. **Commit yok:** değişiklik 422'yle birlikte
> kullanıcının Changes'inde okunur.

**Hedef:** Queen AI'ın H3 metninin hiçbir modda uzunluk söylemediğini, ve uzunluğu düşen iki cümlenin
geri kalanının yerinde durduğunu anlatan iki test.

**Yaklaşım:** `test_video_prompt_writer.py`'nin H3 testleri gibi: yazar sahte Queen AI'la sorulur, ve
giden sistem mesajının bütünü sınanır; cümleler talimattan birebir okunur.

**Araçlar:** pytest, `re`.

**Spec:** [m421 test turu](../specs/2026-10-06-queen-editor-m421-h3-uzunluk-yok-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; kullanıcının gördüğü metin (assert mesajı) Türkçe.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.
- Hiçbir test ağa çıkmaz.

---

## Görev 1: `backend/tests/test_video_prompt_writer.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_video_prompt_writer.py`

- [ ] **Adım 1: `re`'yi içe aktar** — dosyanın başında, `importlib.util`'den sonra:

```python
import importlib.util
import os
import re
```

- [ ] **Adım 2: `test_the_h3_text_says_what_to_do_without_a_scenario`'dan sonra, `_loop_rule`'dan
  önce 421'in deseni ve iki testi.**

```python
# --- Madde 421: the H3 text says no length -------------------------------------------------------

# A length said in seconds: a number -- in figures or in words -- before "second(s)" or "sec(s)", or
# the word "seconds" on its own. "one to four sentences" is a count of sentences and "the second
# photo" an order, so neither is one.
LENGTH = re.compile(r"\b(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven"
                    r"|twelve)[\s-]*(?:seconds?|secs?)\b|\bseconds\b", re.IGNORECASE)


def test_the_h3_text_says_no_length_in_any_mode():
    """The user's words (v9-1, 5 Ekim): "bence videoda uzunluk belirtemyelim h3 te olur mu bu kritik
    bir bilg idğeil gerekirse geri getirirz". How long the video runs is the project's choice alone
    (madde 422). Asked of what the writer actually sends, so no rule appended to the text can bring a
    length back."""
    _instruction, writer = _h3()
    client = FakeQueenAI()

    for mode in ("standard", "loop", "linked"):
        writer(client).write({"photo": "kırmızı elbiseli kadın"}, mode, source=PHOTO, end=NEXT,
                             scene=THRONE)

    for sent, _words, _pictures in client.calls:
        said = LENGTH.findall(sent)
        assert said == [], f"H3 metni hâlâ bir uzunluk söylüyor: {said}"


def test_the_two_sentences_that_said_a_length_keep_the_rest_of_their_words():
    """Madde 421 takes the length out and nothing else: the context still says what H3 makes, and the
    rule still says how far to write -- to the end of the video, however long the project makes
    it."""
    instruction, _writer = _h3()

    assert "- H3 makes a video, with sound, from a photo.\n" in instruction
    assert "from the first frame to the end of the video.\n" in instruction
```

## Görev 2: Koşu — kırmızı

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde 2 kırmızı, ikisi de `test_video_prompt_writer.py`'de —
`test_the_h3_text_says_no_length_in_any_mode` (*four seconds* bulundu) ve
`test_the_two_sentences_that_said_a_length_keep_the_rest_of_their_words` (cümleler bugünkü hâliyle).
Öteki her şey yeşil; iki frontend satırı bu maddeden etkilenmez.

- [ ] **Adım 2: Commit yok.** Testler, spec ve bu plan çalışma ağacında commit'siz kalır; 422'yle
  birlikte kullanıcının onayını bekler.
