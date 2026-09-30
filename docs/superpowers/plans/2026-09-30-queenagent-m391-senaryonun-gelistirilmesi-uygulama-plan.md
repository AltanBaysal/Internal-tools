# Madde 391 — Senaryonun geliştirilmesi · uygulama turu planı

> **30 Eylül güncellemesi.** Bu plan ilk taslağı yazdı; kullanıcı okuyup metni değiştirdi. Değişenler
> [uygulama spec'inin](../specs/2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-uygulama-design.md)
> başında, bugünkü metin `prompt.py`'de. Güncelleme kullanıcıyla satır satır, doğrudan yazıldı; testler
> sonunda bir kez koşuldu.

> **Ajanlar için:** bu plan satır satır, bu oturumda yürütülür (superpowers:executing-plans'ın
> biçimiyle); adımlar `- [ ]` kutularıyla.

**Amaç:** `START_A_SCENARIO`'ya 5. adımdan sonra üç kontrol adımını yazmak, kapanışı 8. adıma taşımak,
açılışın sayısını düzeltmek; çalışma ağacındaki 18 kırmızıyı yeşile getirmek.

**Yapı:** Yalnız `prompt.py`. Metin tek sabit olarak kalır; yeni cümlelerin hepsi o sabitin içinde, ait
oldukları adımda. Skill metinlerinin üstündeki yorumun tavanla ilgili son cümlesi düzelir.

**Araçlar:** Python, pytest.

**Spec:** [2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-uygulama-design.md](../specs/2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-uygulama-design.md)

## Genel kısıtlar

- Dört test satırı, yazıldığı gibi, paralel; borulanmaz, süzülmez, daraltılmaz.
- Testlere dokunulmaz; hiçbir test susturulmaz.
- Ayrı sabit yok; araç açıklaması, öteki skill, `WRITE_FRAME_SYSTEM_PROMPT` değişmez.
- Metnin biçimi: `Step N -- title` başlıkları, `- ` madde işaretleri, çıplak snake_case araç adları,
  ` -- `, kullanıcının sözleri çift tırnakta, kısaltma yok, metin satır sonuyla bitmez. Kaynak satırları
  dosyanın geri kalanı gibi 100 sütunun altında.
- **Commit yok.**

---

### Görev 1: Metin ve yorum

**Dosya:**
- Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` — skill yorumu (166 – 168) ve
  `START_A_SCENARIO` (199 – 244)
- Test: `queen-agent/backend/tests/test_skills.py` (test turunda yazıldı, değişmez)

- [ ] **Adım 1: Yorumun son cümlesi**

```python
# Since Madde 123 each opens as a persona and a word cap in the tests keeps it short: five runs of
# patches had doubled the texts, and a weak model stops reading the middle. From here a sentence
# enters only by deleting one, or by a written decision that raises the cap -- the test keeps each
# one beside it.
```

- [ ] **Adım 2: Açılışın sayısı**

```python
    "prompts, in one flow, walking the user through eight steps in order, by asking.\n"
```

- [ ] **Adım 3: 5. adımın sonu ve 6 – 8. adımlar** — 5. adımın kapanış madde işaretinin yerine:

```python
    "Step 5 -- the prompts\n"
    "- Fill the waiting frames with write_missing_actions, then write the list with "
    "build_prompts.\n"
    "- This step waits for no approval. Go on to Step 6 in the same turn.\n"
    "\n"
    "Step 6 -- one moment\n"
    "- Where a frame's scene or action tells more than one moment, bring it down to one moment, "
    "or split it into one frame per moment.\n"
    "- To bring it down, give update_frame the new scene and an empty action. To split it, bring "
    "it down to its first moment, then write the other moments with add_scene, before the next "
    "frame.\n"
    "- Then fill those frames with write_missing_actions.\n"
    "- Call build_prompts again if you changed anything, then say which frames you changed and "
    "what. If nothing needed changing, say so in a line.\n"
    "- This step waits for no approval. Go on to Step 7 in the same turn.\n"
    "\n"
    "Step 7 -- visible parts\n"
    "- Read the camera angle in each frame's action. A part of somebody the angle hides must not "
    "be in that frame's prompt, or the model draws it anyway or puts it on somebody else.\n"
    "- For such a frame, write a second entry of only what shows, with add_character or "
    'add_outfit, named for it, as in "man body no face" or "dress from behind". If one is '
    "already there, use it.\n"
    "- Give update_frame the frame's cast with that entry in place of the whole one. Somebody the "
    "angle does not show at all leaves that frame's cast. The whole entries stay as they are.\n"
    "- Call build_prompts again if you changed anything, then say which frames you changed and "
    "what. If nothing needed changing, say so in a line.\n"
    "- This step waits for no approval. Go on to Step 8 in the same turn.\n"
    "\n"
    "Step 8 -- can it be drawn\n"
    "- Read the prompts build_prompts wrote. The image model is very weak: can it produce each "
    "one as it is written?\n"
    "- Where a part cannot be produced as written, simplify it where it comes from, and keep the "
    "moment: the action with update_frame, or an entry with update_character, update_outfit or "
    "update_location.\n"
    "- Call build_prompts again if you changed anything, then say which frames you changed and "
    "what. If nothing needed changing, say so in a line.\n"
    "- This step waits for no approval. Close by naming the file and saying it is ready. Do not "
    "print the prompts back, offer nothing, and ask nothing: this is the last word."
)
```

- [ ] **Adım 4: Dört satırı paralel koş, yeşili gör**

`npm test --prefix queen-agent/frontend` arka planda; özeti kendi çıktı dosyasından okunur.

Beklenen: `python -m pytest queen-agent -q` 986 geçti, 0 kırmızı; öteki üç süit yeşil (836, 1160, 749).
Kelime tavanı kırmızıysa pytest gerçek sayıyı gösterir; spec'teki 799 yanlış sayılmış demektir —
metin kısalır, tavan test turunun kararıdır.

- [ ] **Adım 5: Commit yok.** Değişiklik çalışma ağacında kalır; kullanıcı Changes'ten okur.
