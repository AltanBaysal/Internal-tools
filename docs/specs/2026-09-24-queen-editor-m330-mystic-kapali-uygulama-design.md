# Madde 330 — H3 videoları Mystic XXX'siz, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m330 test turu](2026-09-24-queen-editor-m330-mystic-kapali-testler-design.md),
`876704fe`.

İki yerde değişiklik var: grafiklerin yığını ve panelin grubu. Üretici değişmiyor — yığına hiç
dokunmuyor. Defter değişmiyor — Mystic inmeye devam ediyor.

## Grafikler — iki H3 export'u

- `2678`'in `stack_data`'sında Mystic'in yuvası öteki boş yuvaların biçimine dönüyor:
  `{"on":true,"lora":"None","str":1,"vs":1,"as":1}`. Değişen iki alan: `"lora"` ve `"str"` *(0.5 → 1)*.
  `"on":false` değil — yükleyicinin onu dinleyip dinlemediği bilinmiyor, `"None"` ise 213'ten beri
  hiçbir şey yüklemiyor *(test turu, Kural)*.
- Motion Booster'ın yuvası ve öteki on yuva olduğu gibi. JSON dizesi kendi biçiminde kalıyor
  *(boşluksuz, kaçışlı tırnak)*: dosya başına fark tek yuva.

## `model_groups.H3_VIDEO`

- Mystic'in satırı çıkıyor. Grafik onu artık yüklemiyor; grupta kalsa, diskinde Mystic olmayan bir
  makinede panel H3'ü "kurulu değil" derdi.
- Üstündeki yorum *("The lora stack's two, …")* artık bir satırı anlatıyor. 328'den önceki hâline
  dönüyor, çünkü o tek LoRA için yazılmıştı: *"Inside the lora stack's JSON, where a scan for model
  names cannot see it."*

## Değişmeyen — bilerek

- **Defter:** `CIVITAI_H3`'teki Mystic satırı kalıyor; H3 seçen koşu dosyayı indirmeye devam ediyor.
  Geri dönüşün ucuz yolu bu *(satır — "geri istenirse defter değişmeden açılıyor")*: yığına ve gruba
  bir satır, defter aynı.
- **`colab/downloads.py`:** `MIRRORLESS`'te Mystic'in adı ve yorumu *("H3's Mystic XXX lora, while the
  user tries it (madde 328)")* kalıyor. Yorum doğru: dosya hâlâ iniyor, hâlâ aynasız, ve Mystic hâlâ
  denemede — kalıp kalmayacağı belli değil, aynaya girmeme sebebi de bu. Yorum dosyanın yüklendiğini
  söylemiyor.
- **README:** Mystic'i anmıyor. `CIVITAI_COOKIE` satırı *(aynasız dosya çerezle iner)* doğru kalıyor —
  H3 koşusu Mystic'i hâlâ çerezle indiriyor.
- **Disk tahmini:** dosya indiği için değişmiyor.
- Üretici, video prompt'unun yazıcısı, ekran. Derlenecek bir şey yok.

## Taranan — Mystic'in yüklendiğini söyleyen yer kalmıyor

`queen-editor`'da testler dışında Mystic'i anan dört yer var: iki grafik *(bu tur boşaltıyor)*, grup
*(bu tur çıkarıyor)*, defterin satırı ve `MIRRORLESS` *(ikisi de indirmeyi anlatıyor, yüklemeyi değil)*.
Belgelerde Mystic'i anan yerler tarihli spec'ler, planlar ve yol haritaları — tarih, dokunulmuyor;
bir de `collab-toolbox`'ın kendi H3 denemesinin notu, başka aracın.

## Bitti sayılır

Dört test satırı yeşil, `skip` / `xfail` yok; grafikler, grup, spec ve plan tek commit.
