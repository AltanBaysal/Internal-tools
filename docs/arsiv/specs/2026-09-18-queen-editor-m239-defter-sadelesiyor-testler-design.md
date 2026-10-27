# Madde 239 · Defter sadeleşiyor — test turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Ölçü maddenin satırında *(kullanıcı, 18 Eylül)*: kod hücrelerindeki bütün yorumlar ve
docstring'ler gidiyor, yalnız `# === … ===` bölüm başlıkları kalıyor. `#@markdown` ve `#@param`
satırları Colab'ın formu olduğu için, Türkçe markdown hücreleri de kurulum talimatı olduğu için
kalıyor.

## Bugün ne oluyor

`queeneditor.ipynb`'yi Read aracı bir kerede okuyabiliyor, ama sınırın hemen altından: 238'de defter
25.071 token'la sınırı aşmıştı, kullanıcının elle sildiği iki yorum bloğu onu 25.000'in altına
indirdi. Deftere dokunan bir sonraki madde onu yeniden aşar. Hiçbir şey defterin boyutunu tutmuyor.

## Ne olacak

**Bir test defterin boyutunu tutuyor.** Token burada sayılamıyor, o yüzden bütün hücrelerin
kaynağındaki karakter sayısı onun yerine geçiyor. Oran bugünkü defterden ölçülüyor: Read'in
okuduğu yaklaşık 25.000 token, testin saydığı karakter sayısına denk.

**Tavan, bugünkü boyutun %60'ı:** defter bugün 48.527 karakter, tavan **29.000** — aşağı yukarı
15.000 token, sınırın rahat altı. Sayı testte bir
sabit olarak duruyor. Onu yükseltmek bilinçli bir karar olur, fark edilmeden olmaz.

**Mesaj Türkçe ve ne yapılacağını söylüyor:** defterin kaç karakter olduğunu, tavanı ve
yorumların sadeleşmesi gerektiğini.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Defterin hücre kaynakları toplamı tavanı geçmiyor | **kırmızı** |

## Bu turda değişen

Yalnız yeni bir test dosyası: `test_notebook_stays_readable.py`.
