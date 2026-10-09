# Madde 455 — System prompt, plan

> **Koşum:** ana klasörde, `feat/queenagent-v10` dalında, worktree yok, **commit'lenmeden** ve hiçbir
> şey stage edilmeden — metni Claude okuyup doğrular, commit ana agent'ındır. Adımlar `- [ ]` ile
> işaretlenir.

**Hedef:** `SYSTEM_PROMPT` araştırmadan çıkan sekiz öneriyle yeniden yazılır: iki satır kimlik,
numaralı çalışma adımları, sebepli kısa kurallar, `Final answer`, sonda üç satırlık `Remember`.
Bugünkü kuralların hiçbiri düşmez.

**Yaklaşım:** önce test, kırmızı görülür, sonra metin. Dosyalar Edit ve Write ile değişir.

**Spec:** [m455](../specs/2026-10-10-queen-agent-m455-system-prompt-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları İngilizce; spec ve plan Türkçe.
- `SYSTEM_PROMPT_SUFFIX`, `system_prompt()`, `LAST_ROUND`, `SDXL_DOCUMENT`, skill'ler, tool metinleri,
  frontend ve queen-editor'e dokunulmaz.
- Metinde görev kelimesi (senaryo, frame, karakter, prompt …) ve *English* yok.
- `git add`, commit, stash yok. Geçici dosyalar `tmp/m455/`'te.

---

## Görev 0: Ölçüm

- [ ] `tmp/m455/measure.py`: `SYSTEM_PROMPT`'un ve `system_prompt()`'un karakteri, kelimesi, tahmini
  token'ı; metnin kendisi `before.txt`'e.

## Görev 1: Testler — `test_prompt.py`, `test_black_box.py`

- [ ] `_a_line_says(*words)`: bir kuralın kelimeleri tek satırda aranır.
- [ ] Bugünkü kuralların testleri cümle yerine anahtar kelimelere bakar (spec'in Testler bölümü);
  ölü adlar, yanlış sebepler, dil ve görev kelimesi testleri aynı kalır.
- [ ] Yeni: pencere *five*; tool'un cevabı, ret ve başarısızlık, yapılmayan değişiklik; aynı
  argümanlar, iki başarısız deneme; tool'un öğrenebildiği, tek soru; paralel okuma; plan çok adımlı
  işte ve aynı turda, skill'in istisnası; yeni dosya ikinci sürüm değil.
- [ ] Yeni: metin son kelimesinde biter; büyük harfle vurgu, `**`, `#` yok; son bölüm üç madde —
  okuma, tool, sohbet. Ekin birleşmesi `test_model_engine.py`'de.

## Görev 1b: Reviewer'ın bulguları

- [ ] A1, B1, B2 (HOLD): yeni dosya cümlesi geri; iki farklı deneme; skill beklemek diyorsa bekle.
- [ ] A2, A3, B3, C1 – C3, D: tahminin iki sebebi; bu turda bitmeyebilecek iş plan dosyasıyla;
  `create_file` plan dosyası için de; `Rules` beş alt başlıkta; adımlar *Check* ve *Answer*; tek
  adım cümlesi çıkar; yorum düzelir.
- [ ] F1: ekin birleşmesini soran test silinir.
- [ ] `test_black_box.py`: bir cevabın bütün çağrıları sırayla döner.
- [ ] Çalıştır: yeni kurallar kırmızı.

## Görev 2: Metin — `prompt.py`

- [ ] `SYSTEM_PROMPT` spec'teki metinle; üstündeki yorum düzeni ve sebebini söyler, spec'i anar.
- [ ] Çalıştır: yeşil.

## Görev 3: Ölçüm ve spec

- [ ] `measure.py after`; spec'in uzunluk tablosu ölçülen sayılarla, spec'teki iki metin
  `before.txt` ve `after.txt` ile bayt bayt aynı.

## Görev 4: Dört suite

- [ ] `python -m pytest queen-agent -q`; `npm test --prefix queen-agent/frontend`;
  `python -m pytest queen-editor -q`; `npm test --prefix queen-editor/frontend` — birer birer.
- [ ] `git status`: yalnız spec, plan, `prompt.py`, `test_prompt.py`, `test_black_box.py`.
