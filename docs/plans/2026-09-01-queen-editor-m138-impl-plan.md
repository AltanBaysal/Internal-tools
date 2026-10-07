# Madde 138 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-01-queen-editor-m138-break-uygulama-design.md](../specs/2026-09-01-queen-editor-m138-break-uygulama-design.md)
**Dal:** `feat/v6`
**Kırmızı commit:** `6246106`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `workflow_api.json` — `36`'nın sınıfı ve etiketi.

İki satır, 345 ve 347:

```json
    "class_type": "CLIPTextEncodeBREAK",
    "_meta": {
      "title": "CLIP Text Encode (Positive, BREAK)"
```

`inputs` bloğuna dokunulmuyor — `text` → `["39", 0]` ve `clip` → `["27", 1]` yerinde kalıyor, ve
zaten bir bekçi onları tutuyor.

Grafik ComfyUI'de açılıp yeniden export **edilmiyor**: aday düğümün girişleri ve çıkışı bugünküyle
aynı şekilde, ve yeniden export ilgisiz yerleri de yeniden yazıp diff'i okunmaz hâle getirirdi.

→ `test_the_positive_encoder_understands_break` yeşile döner.

## B. `queeneditor.ipynb` — `CUSTOM_NODES` listesine bir satır.

Foto bloğunun sonuna, `ComfyUI-KJNodes`'tan hemen sonra:

```python
    ("ComfyUI-ppm",               "https://github.com/pamparamm/ComfyUI-ppm.git"),             # CLIPTextEncodeBREAK -- the positive path splits on BREAK
```

Foto bloğunun sonunda, çünkü düğüm foto grafiğinin pozitif yolunda; video bloğu kendi yerinde
kalıyor.

→ `test_the_notebook_installs_the_encoder_the_graph_asks_for` yeşile döner.

## C. `queeneditor.ipynb` — markdown hücresindeki iki sayı.

Aynı defterin, listenin üstündeki markdown hücresi:

- Başlık: `## ComfyUI + Custom Node'lar (19)` → `(20)`
- Cümle: `ilk sekizi foto grafiği` → `ilk dokuzu foto grafiği`

Birincisi `test_the_notebook_says_how_many_custom_nodes_it_installs`'ın tuttuğu sayı — B adımından
sonra o bekçi kırmızıya düşer ve bu adım onu geri döndürür. İkincisi testle korunmuyor ama aynı
cümlenin aynı olgusu: sekiz kalırsa cümle yalan söyler.

## D. Koşuldu: **726 yeşil, 0 kırmızı.**

`python -m pytest queen-editor -q` — iki kırmızı döndü, üç bekçi yeşil kaldı *(sayı bekçisi B'den
sonra 20'yi listede görüp başlıkta 19 bulacaktı; C onu aynı commit içinde kapattı)*.

*Bu plan açılışta 727 diye yazmıştı — takımın toplamı 726, sayım bir fazlaydı. Sayı koşuya
uyduruluyor, tersi değil.*

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil**, kırmızı turdakiyle birebir aynı.
Ön yüz ellenmedi.

## E. Yeşil commit.

Grafik, defter, ve bu turun iki belgesi — **tek commit**. Tasarımın kuralı: ComfyUI kurulmamış bir
düğümü isteyen grafiği reddediyor, yani ikisini ayırmak her üretimin düştüğü bir commit yaratır.

`dist` yeniden derlenmiyor: ön yüz değişmiyor.

## Bilerek yapılmayanlar

**Adaptör, `model_groups.py`, negatif yol, ön yüz, `dist`** — hiçbiri ellenmiyor.

**Colab koşusu bu turun içinde değil.** Maddenin kabul kriteri —
[tasarımda](../specs/2026-09-01-queen-editor-m138-break-uygulama-design.md) yazılı: aynı prompt,
aynı seed, `36` iki sınıfla iki üretim; kareler aynıysa düğüm çalışmıyor, farklıysa böldü. Kullanıcı
koşuyor, ve tek kurulum yetiyor çünkü adaptör grafiği her render'da yeniden okuyor.
