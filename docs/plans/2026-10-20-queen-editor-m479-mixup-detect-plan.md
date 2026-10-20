# Madde 479 — Ajan karışmaları bulur, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** ajanın üçüncü okuyan aracı `check_frame`, bir karenin fotoğrafını prompt'uyla kendi
isteğinde karşılaştırır ve sohbete kararı kelimelerle döndürür; talimat karışma kontrolünü ve üç
gruplu listeyi söyler; QueenAgent'ın kuralları kopya olarak girer.

**Spec:** [m479](../specs/2026-10-20-queen-editor-m479-mixup-detect-design.md)

**Araçlar:** pytest, vitest.

## Her yere geçerli kurallar

- Yorumlar, docstring'ler ve modele giden metinler **İngilizce**; adımların cümleleri Türkçe.
- Dosyalar Read / Edit / Write ile değişir. Kabuk yalnız pytest, npm ve git status / diff için.
- Testler gerçek bir modeli çağırmaz: sahte kutu `converse` ve `ask`'i listeden cevaplar.
- İki suite birer birer koşulur. Frontend değişmez, `dist` yeniden kurulmaz.

---

## Görev 1: testler (`backend/tests/test_agent_answer.py`)

- [ ] `FakeBox` `ask`'i öğrenir: `checks` listesinden cevaplar, sorulanı `checked`'e yazar.
- [ ] `Project` resimleri bir sözlükten alır (varsayılan bugünkü `P0_0.png`).
- [ ] Araç listesi testi üç ada döner.
- [ ] Yeni testler: kontrol talimatı (kurallar + iş + suffix) + `Prompt: …` + tek resim soruluyor,
  "Frame N: <karar>" dönüyor, sohbete resim girmiyor; adım soru sorulduğu anda sohbette; videolu,
  fotoğrafı başarısız, fotoğrafsız ve prompt'suz kare okunmuyor, sorulmuyor, adımsız; başarısız
  videolu kare kontrol ediliyor; diskte olmayan resim sorulmuyor; okunamayan resim (`OSError`)
  karenin satırı; ret karenin satırı, teknik hata soruyu bitiriyor; bir turun iki çağrısı arasında
  durdurma ikinciyi göndermiyor.
- [ ] `test_composition_root.py`: ajanın testi `check_frame` çağrısını da taşır — kontrol isteği,
  ret kontrolü, sohbete dönen karar; araç listesi üç ad.
- [ ] Kırmızı.

## Görev 2: talimat (`backend/features/agent/domain/prompt.py`)

- [ ] `INSTRUCTION`: Context'e `check_frame`; *Checking for mix-ups* bölümü.
- [ ] `CHECK_FRAME`, `MIXUP_CHECK` (karar biçimi `OK` / `MIXED:` / `UNSURE:`), `MIXUP_RULES`
  (QueenAgent'ın Step 5, 7, 8, 9, 10 Context'leri, kopya; neyin bırakıldığı yorumda).

## Görev 3: araç, döngü, port

- [ ] `tools.py`: `TOOLS`'a `check_frame`; adlar `TOOLS`'tan; `_nothing_to_compare`, `_check`,
  `_look`, `QueenAIFailed`; `run_tool(ask, …)` `(adım, iş)` döner.
- [ ] `answer_question.py`: her çağrıdan önce `run.stopped()`, adım işten önce, `QueenAIFailed` →
  `run.fail`; `run_tool`'a `box.ask`.
- [ ] `ports.py`: `QueenAI.ask`.
- [ ] Yeşil.

## Görev 4: Bitiş

- [ ] `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.
- [ ] `git status` / `git diff` ile değişen dosyaları gözden geçir.
