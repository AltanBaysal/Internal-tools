# Madde 210 · Bağlantı metinleri — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-13-queen-editor-m210-baglanti-metinleri-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı `8774414`'te. Bu tur 120 dosyanın bağlantı metnini düzeltir; teste dokunulmaz.

## Adımlar

**1 · Tek geçiş, hedefe göre eşleme.** `docs/` altındaki her markdown dosyasında, hedefi bir yol
haritası olan her bağlantı bulunur; hedefin adından sürümü çözülür; metindeki eski numara o hedefin
eşlemesine göre değişir. Eşleme tablosu [spec'te](../specs/2026-09-13-queen-editor-m210-baglanti-metinleri-uygulama-design.md).

Değişim **yalnız köşeli parantezin içinde** olur — gövde cümlelerine dokunulmaz. `adıyla` geçen
metinler atlanır.

**2 · Takım koşulur.** Kırmızı yeşile döner:

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**3 · Tökezleyen metinler elle düzeltilir.** Numara bölüm adıyla birlikte girince sözcük sırası
bozulan iki kalıp çıktı; ikisi de düzeltildi *(9 dosya)*. Çivi bunları göremez çünkü numara doğru;
geçiş sonrası değişen satırlar okunur ve düzeltilir.

**4 · Yeşil commit'lenir.**

## Değişen dosyalar

`docs/superpowers/specs/` ve `plans/` altında 120 dolayında belge, artı queen-editor v4 yol
haritasının bir satırı. Kod, test ve `dist` değişmiyor.
