# Madde 144 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-02-queen-editor-m144-form-uygulama-design.md](../specs/2026-09-02-queen-editor-m144-form-uygulama-design.md)
**Dal:** `feat/v6`
**Kırmızı commit:** `ffde8d1`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. CONFIG hücresinin başı yeniden yazılır.

`# === CONFIG ===` satırından `PHOTO_NOVAANIME` kutusuna kadar olan kısım:

```python
# === CONFIG ===
# Colab bu hücredeki #@param satırlarını sağdaki forma onay kutusu olarak, #@markdown satırlarını
# da aynı panele metin olarak çiziyor. Düz bir # yorumu forma HİÇ ulaşmıyor -- o yüzden kullanıcıya
# bakan her cümle #@markdown'da, kaynağı okuyana bakanlar burada.

#@markdown ### Üreticiler
#@markdown En az birini işaretle. Video ~39 GiB · ses ~9 GiB.
INSTALL_PHOTO = False  #@param {type:"boolean"}
INSTALL_VIDEO = False  #@param {type:"boolean"}
INSTALL_AUDIO = False  #@param {type:"boolean"}

#@markdown ---
#@markdown ### Fotoğraf modelleri
#@markdown Hepsi boş gelir — istediğini işaretle, hiçbirini seçmezsen defter durur.
#@markdown Grubun ortak dosyaları ~2 GiB; her model ~7 GiB daha, üçü birden ~23 GiB (T4'te dar).
#@markdown - **nova3DCG** — 3DCG / 2.5D
#@markdown - **novaOrange** — detaylı tenli anime
#@markdown - **novaAnime** — anime
# Why they come empty is not in the form, because it does not change the user's decision:
# /content dies with the runtime, so every model is fetched AGAIN on every startup. The cost is
# not one-off, and whoever needs to know that is whoever edits this notebook.
PHOTO_NOVA3DCG = False  #@param {type:"boolean"}
PHOTO_NOVAORANGE = False  #@param {type:"boolean"}
PHOTO_NOVAANIME = False  #@param {type:"boolean"}
```

**Dikkat edilecek üç şey:**

1. `PHOTO_*` ve `INSTALL_*` satırları **harfi harfine** aynı kalıyor — desen `=` öncesinde tam bir
   boşluk, `False` ile `#@param` arasında iki boşluk istiyor.
2. Kutu **sırası** değişmiyor: kontrol satırı `PHOTO_NOVA3DCG or PHOTO_NOVAORANGE or
   PHOTO_NOVAANIME` diyor ve testi beklediği satırı bu sırayla kuruyor.
3. `#@markdown ---` **başlıklardan sonra, ikinci başlıktan önce** — testi konumla ölçüyor.

→ Üç kırmızı da yeşile döner.

## B. Hücrenin geri kalanı ellenmez.

İki `assert`, Secrets okuması, GPU kontrolü, xAI yoklaması, çıktı satırları — hepsi olduğu gibi.

## C. Koşuldu: **739 yeşil, 0 kırmızı.**

`python -m pytest queen-editor -q` — üç kırmızının üçü döndü, tek seferde. CONFIG hücresini okuyan
beş bekçinin beşi de yeşil kaldı: `test_every_producer_has_a_checkbox_of_its_own`,
`test_every_photo_model_has_a_checkbox_of_its_own`, `test_every_photo_model_comes_switched_off`,
`test_choosing_photo_without_a_model_stops_the_notebook` *(sıraya duyarlı, ve sıra değişmedi)*,
`test_the_xai_probe_runs_in_config_not_after_the_downloads`.

Toplam 736'dan 739'a çıktı: üç yeni test, hepsi yeşil.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.**

**Takımın söyleyemediği şey duruyor:** satırların doğru yerde olduğu doğrulandı, forma nasıl
çizildiği değil. Onu yalnız Colab söyler.

## D. Yeşil commit.

`queeneditor.ipynb` ve bu turun iki belgesi.

`dist` derlenmiyor: ön yüz değişmiyor.

## Bilerek yapılmayanlar

**Ayrı hücre, `#@title`, kutu adları, kodun davranışı** — tasarımda gerekçeleri yazılı.

**Görüntünün doğrulanması** — takımın işi değil, Colab'ın.
