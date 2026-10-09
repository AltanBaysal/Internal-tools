# Madde 328 — H3'e Mystic XXX LoRA'sı, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m328 test turu](2026-09-24-queen-editor-m328-mystic-lora-testler-design.md),
`cff9c38f`.

Ad beş yerde aynı dize: `MysticXXX_MMH3-V4.safetensors`. Üretici değişmiyor — yığına hiç
dokunmuyor, LoRA'lar grafiğin içinde.

## Grafikler — iki H3 export'u

- `2678`'in `stack_data`'sında **yuva 1** doluyor: `"lora"` `"None"`'dan dosyanın adına dönüyor. Yuvanın
  `str`'i zaten 1, `vs` ve `as` da 1; başka hiçbir şey değişmiyor. Yuva 1, çünkü Motion Booster'ın
  hemen ardındaki boş yuva o — yuva 2'nin gücü 0.7, orası bir alan daha değiştirirdi.
- JSON dizesi kendi biçiminde kalıyor *(boşluksuz, kaçışlı tırnak)*: fark tek yuva.

## `model_groups.H3_VIDEO`

- Motion Booster'ın ardına `{"folder": "loras", "name": "MysticXXX_MMH3-V4.safetensors"}`. Üstündeki
  yorum *("yığının JSON'unda, model taraması göremiyor")* artık iki satırı anlatıyor; çoğula dönüyor.

## Defter — `CIVITAI_H3`

- Motion Booster'ın ardına tek satır: `(3266628, LORA, "MysticXXX_MMH3-V4.safetensors", "H3 Mystic
  XXX")`. Etiket Motion Booster'ınkinin kalıbında *("H3 Motion Booster")*; konsolda ve özet
  tablosunda bu okunuyor. Yorum yok — defterin kod hücreleri yalnız bölüm başlığı taşıyor.
- **Giriş hücresi:** *"`CIVITAI_COOKIE` yalnız aynada henüz olmayan bir dosya için"* artık doğru değil
  — aynası kapalı dosya da çerezle iniyor. Cümle *"aynada henüz olmayan ya da aynası kapalı bir
  dosya için"* oluyor, README'nin aynı satırı gibi.
- **Disk tahmini değişmiyor:** 148 MB, H3'ün `37` GiB'ının yuvarlamasında; test de metin de
  değişmesini istemiyor.
- **Tavan:** satır ~75 karakter; `test_the_notebook_stays_well_under_what_the_tools_can_read`
  yeşil kalmalı. Kalmazsa satır kısaltılmaz, durulup sorulur — tavanı yükseltmek bir karar
  *(testin kendi sözü)*.

## `colab/downloads.py` — `MIRRORLESS`

- `MIRRORLESS = {"MysticXXX_MMH3-V4.safetensors"}`, girdinin üstünde neden orada olduğunu söyleyen
  bir satır: H3'ün Mystic XXX LoRA'sı, kullanıcı denerken *(madde 328)*. 327'nin yorumu değişmiyor.

## README

İki satır artık doğru değil:

- **`CIVITAI_COOKIE`** — *"once everything is mirrored a run needs none"*: aynasız bir dosya aynaya
  hiç girmiyor, yani H3 koşusu çerezi her zaman istiyor. Cümle `MIRRORLESS`'i dosyasıyla anıyor —
  listeyi kopyalamıyor, çünkü kopya eskir *(CLAUDE.md, Style)*.
- **`HF_TOKEN`** — *"mirrors the Civitai files"*: artık `MIRRORLESS`'tekiler hariç.

`VIDEO_H3 (~37 GiB)` değişmiyor.

## Değişmeyen

Üretici, video prompt'unun yazıcısı *(tetik kelimesi yok)*, ekran. Derlenecek bir şey yok.

## Bitti sayılır

Dört test satırı yeşil — defterin tavan testi dahil; kod, spec ve plan tek commit.
