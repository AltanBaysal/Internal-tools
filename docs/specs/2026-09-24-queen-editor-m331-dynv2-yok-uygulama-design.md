# Madde 331 — H3'ün video prompt yazarı `dynv2` yazmıyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m331 test turu](2026-09-24-queen-editor-m331-dynv2-yok-testler-design.md), `ce03001a`.

## `xai_prompt_writer.py` — `H3_VIDEO_INSTRUCTION`

- Şablonun ilk satırı `dynv2.` ve ardındaki boş satır gidiyor; şablon
  `integrated_multimodal_description: [Shot 1] <the motion>` ile açılıyor.
- Kuralların ilki *("dynv2. is the first line. …")* gidiyor. Öteki üç kural aynen.
- Talimatın üstündeki yorumun `dynv2` cümleleri doğru olanı söylüyor: yazar tetiği yazmıyor, kullanıcı
  istediği prompt'a elle ekliyor *(madde 331)*, ve nereye gittiği üreticinin işi *(246)*.

## `comfy_h3_video_generator.py` — yalnız yorum

`TRIGGER`'ın üstündeki *"the writer decides whether a scene gets it (madde 246)"* artık yanlış. Yeni
hâli: kelimeyi kullanıcı elle yazıyor *(madde 331)*. Kod değişmiyor — elle yazılan `dynv2`'yi öne
almak aynı iş.

## Değişmeyen

WAN yazarı, loop kuralı, üretici kodu, Motion Booster, Referanstan. Ekran ve dist değişmiyor.

## Bitti sayılır

Dört test satırı yeşil, `skip` / `xfail` yok.
