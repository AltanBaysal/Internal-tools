# Madde 331 · H3'ün video prompt yazarı `dynv2` yazmıyor — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-24-queen-editor-m331-dynv2-yok-uygulama-design.md) ·
**Testler:** `ce03001a` · **Tur:** 2/2.

**Hedef:** `test_the_h3_instruction_never_asks_for_dynv2` yeşile dönüyor; başka hiçbir test değişmiyor.

## Görev 1 — talimat ve iki yorum

**Dosyalar:** `queen-editor/backend/features/photo_generation/data/xai_prompt_writer.py` *(37–66)*,
`queen-editor/backend/features/photo_generation/data/comfy_h3_video_generator.py` *(33)*.

- [ ] **Adım 1: talimatın yorumu.** 41–43. satırlar yerine:

```python
# dynv2, the word that wakes the Motion Booster lora, is not asked for either: the user adds it by
# hand to the prompts that want it (madde 331), and the producer moves it in front (246).
```

- [ ] **Adım 2: şablon.** `Write it like this:`'ın altındaki `dynv2.` satırı ve ardındaki boş satır
  gidiyor:

```
Write it like this:

integrated_multimodal_description: [Shot 1] <the motion>
```

- [ ] **Adım 3: kural.** `- dynv2. is the first line. Write it for most scenes. Leave it out only if
  the scene is calm or still.` satırı gidiyor; öteki üç kural aynen.

- [ ] **Adım 4: üreticinin yorumu.** `TRIGGER`'ın üstü:

```python
# Motion Booster's word, added by hand to the prompts that want it (madde 331).
```

- [ ] **Adım 5: dört satırı koş**, yazıldığı gibi ve paralel:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

- [ ] **Adım 6: işaret ve commit.** Yol haritasında 331 ✅, `Durum` 39/39; commit iki kaynak dosya,
  spec, bu plan ve yol haritası:

```
feat(m331): the H3 writer no longer asks for dynv2, the user adds it by hand; v7 at 39/39
```
