# Madde 327 — İndirmede HF aynası dosya başına kapanabiliyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m327 test turu](2026-09-24-queen-editor-m327-aynasiz-indirme-testler-design.md),
`acf242e8`.

## Kod — yalnız `colab/downloads.py`

- **`MIRRORLESS = set()`**, `civitai_fetch`'in üstünde, `nodes.py`'nin `SKIPPED`'i gibi: modül
  düzeyinde bir küme ve üstünde neden var olduğunu söyleyen yorum — denenen dosyalar aynaya girmiyor
  *(madde 327)*, ve anahtar dosya adı, çünkü adres defterde duruyor. Boş başlıyor; ilk girdi 328'in.
  CODE-STANDARD'ın *"listeler defterde kalır"*ı indirilecek dosyaların listesi için — bu liste neyin
  indirileceğini değil, nasıl indirileceğini söylüyor, ve adres taşımıyor.
- **`civitai_fetch` önce dosyanın yerinde olup olmadığına bakıyor** — varsa `zaten var` deyip dönüyor,
  kimseye bir şey sormadan. Aynası açık dosya için bugünkünün aynısı: `hf_fetch`'in ilk satırı bu
  cümleyi aynı biçimde basıyordu. Aynası kapalı dosya için yoklamayı önlüyor: yoksa ikinci bir
  *Run all*'da yerinde duran dosya için Civitai'ye soru giderdi *(test turunun incelemesinde verilen
  karar)*. Bunu soran test yok.
- **Aynası kapalıysa** `hf_fetch` çağrılmıyor ve konsol bir satır basıyor:
  `<etiket>: aynası kapalı — Civitai'den aynasız iniyor (madde 327)`. Ardından bugünkü Civitai yolu:
  çerez, yoklama, `fetch`. **Yükleme yok.** Satır `fetch`'inki, özete giriyor.
- **Çerez cümlesi sebebi doğru söylüyor:** aynası açık dosyada bugünkü gibi `aynada yok`, kapalı
  dosyada `aynası kapalı` — gerisi aynı.
- `civitai_fetch`'in imzası değişmiyor; docstring 327'yi de anlatıyor.

## Defter ve dist

Defter değişmiyor *(kullanıcı — "Notebook'a hiçbir şey eklenmesin")*. Ekran değişmiyor; derlenecek bir
şey yok.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
