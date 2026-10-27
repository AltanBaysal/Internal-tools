# Madde 418 — Kutunun ret kontrolü, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır, madde 418'in kendi dalında. Testlere dokunulmaz.

**Hedef:** Test turunun kırmızı testlerini kodla yeşile çevirmek — testlerin anlattığı kadar, fazlası
değil.

**Yaklaşım:** Kutunun `try`'ının içinde, asıl cevaptan sonra aynı istemciye ikinci bir `complete`:
kontrolün metni sistem mesajı, cevap sözler. Yalnız tam olarak `APPROVED` geçirir; ret ve iki isteğin
hatası aynı beş denemeden düşer; sonda son denemenin türü konuşur.

**Spec:** [m418 uygulama turu](../specs/2026-10-06-queen-editor-m418-ret-kontrolu-uygulama-design.md)
· [m418 test turu](../specs/2026-10-06-queen-editor-m418-ret-kontrolu-testler-design.md)

**Test turunun kırmızısı** (`e7d57e4c`): queen-editor `19 failed, 1296 passed` — kutunun değişen beşi,
418'in on testi (parametreliyle), kapı testinin dört durumu · queen-agent `989 passed` · iki vitest
satırı başlayamadı: `'vitest' is not recognized` — bu çalışma ağacında `node_modules` yok.

## Her yere geçerli kurallar

- Kod, yorum, docstring İngilizce; kullanıcının gördüğü metin Türkçe. Yorum neden'i söyler.
- CODE-STANDARD: kutu bir servis, hiçbir özelliği bilmez — suffix'i de, video'yu da.
- Cümle harfi harfine: `Model hata döndü, farklı şekilde dene.`
- Yalnız `box.py` değişir.

---

## Görev 1: `services/deepseek/box.py`

**Dosya:** Değiştir: `queen-editor/backend/services/deepseek/box.py`

**Üretir:** `CHECK_INSTRUCTION` (str), `REFUSED` (str); `Box(client).ask(system, text="", images=())
-> Answer` aynı imzayla. `TRIES` ve `Answer` aynen.

- [ ] **Adım 1: Dosyanın tamamı.**

```python
"""The black box every request to Queen AI goes through (madde 416, 418).

The caller asks once and always gets an Answer back, never an exception. A request that came back
with an HTTP error, a malformed or an empty answer, or no answer at all is sent again as it was, up
to five tries in all. An answer that did come is checked before it goes back: its text is sent to
DeepSeek word for word, in a request of its own, and only an approval lets it through -- a refusal
sends the request again the way an error does, out of the same five tries (madde 418). When every
try failed, the Answer is marked as a failure and says what the last try met: the refusal sentence,
or the error's own text. It never raises because a caller that loops -- an agent -- must not be
broken by the service (v9-3): what to do with the failure is the caller's call.

What one try is lives in client.py; this file decides how many there are and what comes back.
"""
from dataclasses import dataclass

TRIES = 5

# What the check is told; its words are the answer alone. English, because it is written for the
# model. It speaks of an answer to some request and of nothing of this tool's, because QueenAgent's
# box is to send the same text word for word (v10-1b). It asks whether the answer is a refusal and
# nothing more: a check that judged the content would refuse what the writers are asked for. The box
# reads one word back, so the text asks for one word.
CHECK_INSTRUCTION = """
You check an answer that a language model gave to a request.

Context
- You are given the answer alone, word for word. You are not given the request.
- An answer is a refusal when the model does not do what was asked: it says it cannot or will not, it apologizes instead of answering, or it gives a warning or a lecture instead of the answer.

Rules
- Judge only whether the answer is a refusal. Never judge whether the answer is good, true or allowed.
- Adult, explicit or violent content in the answer is not a refusal.
- If the answer is a refusal, write REFUSAL. Otherwise write APPROVED.
- Write only the one word. No quotes, no explanations.
"""

# What the caller is told when the last try was refused -- the owner's sentence (v9-3). A technical
# failure is told in its own words, because they say what went wrong; a refusal's words leave the
# caller nothing to do but ask another way.
REFUSED = "Model hata döndü, farklı şekilde dene."


@dataclass(frozen=True)
class Answer:
    """The model's text, or -- when `failed` -- why the box gave up, in the service's own words."""

    text: str
    failed: bool = False


class Box:
    def __init__(self, client):
        self._client = client

    def ask(self, system, text="", images=()):
        """The client's question, asked until an answer passes the check or five tries have failed.

        A try is the question and, when an answer came, its check; a refusal and an error of either
        request each spend one. Every failure is tried again, a missing key included: the client
        refuses that one before anything is sent, so its tries cost nothing, and one rule is simpler
        than a list of the exceptions worth a second try.
        """
        for _ in range(TRIES):
            try:
                answer = self._client.complete(system, text, images)
                # Only the one word lets an answer through: anything else, a check that will not
                # judge included, has approved nothing (v9-3).
                if self._client.complete(CHECK_INSTRUCTION, answer) == "APPROVED":
                    return Answer(answer)
                said = REFUSED
            except Exception as exc:
                said = str(exc)
        # Every try rewrites `said`, so what the caller is told is the last try's.
        return Answer(said, failed=True)
```

## Görev 2: Koşu — yeşil, commit

- [ ] **Adım 1: Dört satır**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: iki pytest satırı yeşil — queen-editor `1315 passed`, queen-agent `989 passed`. İki vitest
satırı bu çalışma ağacında başlayamaz — `node_modules` yok; bu madde ekrana dokunmuyor.

**Koşuldu:** queen-editor `1315 passed` · queen-agent `989 passed` · iki vitest satırı:
`'vitest' is not recognized`.

- [ ] **Adım 2:** Fark FOUNDATION, CODE-STANDARD ve *Bitti sayılır*'a karşı okunur.

- [ ] **Adım 3: Commit** — kod, uygulama spec'i ve bu plan:

```powershell
git add queen-editor/backend/services/deepseek/box.py docs/specs/2026-10-06-queen-editor-m418-ret-kontrolu-uygulama-design.md docs/plans/2026-10-06-queen-editor-m418-ret-kontrolu-uygulama-plan.md
git commit -m @'
feat(queen-editor): 418 -- the box in services/deepseek has every answer checked by DeepSeek: the answer goes word for word, in a request of its own, with a new check text asking for one word, and only APPROVED lets it through; a refusal or an error of either request spends one of the same five tries and sends the request again unchanged; when all five failed the box returns the refusal sentence if the last try was refused and the error's own text if it was technical, so a run whose Queen AI keeps refusing stops as today with that sentence on the error line

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
