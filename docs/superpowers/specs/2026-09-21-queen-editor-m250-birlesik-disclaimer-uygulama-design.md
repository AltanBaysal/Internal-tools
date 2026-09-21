# Madde 250 · Birleşik export'ta disclaimer ilk 1 dakika — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m250-birlesik-disclaimer-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

Tek dosya: `data/ffmpeg_video_exporter.py`. Domain'e, config'e ve wiring'e dokunulmuyor — birleşik
export'un disclaimer taşıyacağı bu maddenin kararı değil, maddenin kendisi; `merge()`'in bir bayrağa
ihtiyacı yok, çünkü onu bayraksız isteyen bir çağıran yok.

**`_stamp()` ikiye ayrılıyor.** Bugün videoyu alıp ffprobe'a soruyor, sonra filtreyi kuruyor.
`merge()` ölçüyü zaten elinde tutuyor *(her parçaya soruyor)*, yani ona ikinci bir ffprobe
gerekmiyor. Ölçüden filtre kuran kısım `_stamp_for(width, height)` olarak ayrılıyor; `_stamp(video)`
ise ffprobe'u koşup onu çağırıyor. İki çağıran, bir filtre — bindirme tek yerde tanımlı kalıyor.

**`merge()` `concat`'in üstüne biniyor.** Komut:

```
ffmpeg -y -f concat -safe 0 -i pieces.txt -i PNG \
  -filter_complex <_stamp_for(...)> -map [v] -map 0:a? \
  -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a copy TARGET
```

`-map 0:a?` sesi taşıyor ve `?` sessiz bir seti geçiyor; ses `copy` kalıyor, çünkü parçaların sesi
249'da zaten `aac`'ye yazıldı ve ikinci kez kodlamanın vereceği hiçbir şey yok. Ölçü kontrolü ve
`pieces.txt`'nin yazılıp silinmesi olduğu gibi duruyor.

## Bunun getirdiği ve götürdüğü

**Götürdüğü hız.** Birleşik export bugün hiçbir kareyi yeniden kodlamıyordu; artık birleşmiş akışı
bir kez kodluyor. Bedel kaçınılmaz — bindirme yeni bir görüntü — ve **bir kez** ödeniyor: parça
başına değil, birleşmenin kendi okumasında. Ölçülmüş bir sayı yok, ve buraya tahmin yazılmıyor.

**Getirdiği, ölçü kuralının hâlâ yerinde durması.** Farklı ölçüdeki parçalar birleştirmeyi yine
durduruyor. Bindirme kodlama getirdiği için *"kopyalama bozuk dosya yazar"* gerekçesi teknik olarak
zayıfladı, ama karar 218'in kararı: iki oranı tek dosyada birleştirmenin cevabı kullanıcının hiç
istemediği bir kırpma ya da bir bant olurdu. Madde onu değiştirmiyor.

## Bu turda değişen

- `backend/features/photo_generation/data/ffmpeg_video_exporter.py`: `_stamp()` ikiye ayrılıyor,
  `merge()`'in komutu bindirmeyi ve kodlamayı alıyor, modül başlığı ikinci kodlamayı söylüyor.

Başka hiçbir dosya değişmiyor; ön yüz ve `dist` bu maddede de yerinde.
