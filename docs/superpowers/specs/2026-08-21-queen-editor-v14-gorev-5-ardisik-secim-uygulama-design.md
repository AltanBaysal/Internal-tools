# v14 · Görev 5 — Sonrakine bağla ardışık seçim istiyor · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-5-ardisik-secim-testler-design.md) —
kararlar orada verildi ve commit edilmiş altı test onları tarif ediyor.

## Değişen dosya

Tek dosya: **`features/photo_generation/LayerPanel.jsx`**.

**`neighbours(frames, chosen)`** — modül seviyesinde saf bir fonksiyon. Seçilen kimliklerin
galerideki konumları kesintisiz bir dizi mi? Konumları toplayıp en büyükten en küçüğü çıkarıyor ve
seçim sayısıyla karşılaştırıyor: `max - min + 1 === count`. Sıralamaya gerek yok, ve kimliği
galeride bulunmayan bir seçim (silinmiş kare) sayıya girmiyor.

Bileşenin dışında, çünkü hiçbir şeye bağlı değil ve testi ekranı kurmadan da düşünülebilir olmalı.

**`ModeRow`** bir `disabled` alıyor — `ScopeRow`'un zaten taşıdığı şeklin aynısı: imleç `default`,
saydamlık 0.4, kenar `--border`.

**Kapanma koşulu** panelde: kapsam "Seçili kareler" **ve** seçim bitişik değil. Kapsam
"Videosu olmayanlar" iken kapalı değil — o küme doğası gereği dağınık.

**Sebep satırı** kapanan seçeneğin altında, `Note` ile, `--ink-3` renginde. Tehlike rengi yok:
kapanan bir seçenek bir arıza değil, bir kural.

**Modun düşmesi** bir `useEffect` ile: bağla seçiliyken kapanma koşulu doğduğunda `STANDARD`'a
dönüyor. Render sırasında düzeltmek yerine efektle, çünkü değişen şey dışarıdan gelen bir prop ve
düzeltme bir durum yazımı.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor.
