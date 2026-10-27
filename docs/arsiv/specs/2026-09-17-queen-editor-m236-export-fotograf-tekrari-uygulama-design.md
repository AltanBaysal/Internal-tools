# Madde 236 · Export her fotoğrafı bir kez yazar — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m236-export-fotograf-tekrari-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Tasarım

`run_export`'un döngüsü yazdığı fotoğraf dosyalarının adlarını bir kümede tutuyor; bir kare
fotoğrafını kümede bulursa kopyalamıyor. Numara kareden geliyor, yani ilk kullanan kare fotoğrafı
kendi numarasıyla yazdırıyor ve sonrakiler hiçbir şey yazdırmıyor.

Karşılaştırma **dosya adıyla**: kopya kare kaynağının dosyasını gösteriyor, yani aynı resim aynı ad
demek. İçerik karşılaştırmak — boyut, özet — aynı cevabı çok daha pahalıya verirdi, üstelik Drive
üstünden.

Videoların döngüsü değişmiyor: kopya karenin videosu kendi dosyası ve dizideki yerini koruyor.

`copy_photo`'nun "zaten orada" dalı kalıyor: o, aynı klasöre yazan iki export modunu koruyor, bu
küme ise tek koşunun içindeki tekrarı. İkisi farklı soru.

## Bu turda değişen

Yalnız `run_export.py`. Ön yüz değişmiyor.
