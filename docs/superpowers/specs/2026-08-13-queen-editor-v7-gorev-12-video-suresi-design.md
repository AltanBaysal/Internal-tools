# Görev 12 — Video süresi tek yerden gelsin

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 4

## Sorun

Bir videonun kaç saniye sürdüğü iki yerde yazılı: video grafiğinde `PrimitiveFloat` node `178`
("Duration (Seconds)") = 5, ve export özetinde `VIDEO_SECONDS = 5`. Bugün tutuyorlar. Grafik
değişirse export, olmayan bir süreyi söylemeye devam eder — ve kimse fark etmez, çünkü iki sayı da
kendi başına doğru görünür.

## Kararlar

1. **Grafik tek kaynaktır.** Süre orada ayarlanıyor; export onu okur, kendi kopyasını tutmaz.
2. **Domain grafiği tanımaz.** Süreyi soran şey bir port: export özeti "bir video kaç saniye"
   sorusunu sorar, cevabı verenin ComfyUI grafiği olduğunu bilmez. Node numarası, video
   üreticisinin — grafiği tanıyan tek dosyanın — kendi bilgisi olarak kalır.
3. **Süre node'u, grafiğin doğrulanan node'ları arasına girer.** Diğer üçü gibi: yoksa grafik
   değişmiştir ve bunu render anında değil, yükleme anında duymak gerekir.
4. **Ondalık süre de doğru cevaplanır.** Grafikteki alan bir ondalık sayı; 5 yerine 7.5 yazıldığında
   export'un söylediği toplam da ondalıklı olmalı. Sayıyı tam sayıya yuvarlamak, ikinci bir
   kopyanın kendisi kadar sessiz bir yalan olurdu.

## Testler

- Video üreticisi, süreyi grafikten okur.
- Süre node'u olmayan bir grafik, eksik node'u söyleyerek reddedilir.
- Export özeti, kendisine verilen süreyi kullanır — sabiti değil.
- Toplam süre, video sayısı çarpı o süre.

## Öz eleştiri

- *Grafiği her özet için yeniden okumak pahalı değil mi?* — Özet, export ekranı açılırken bir kez
  isteniyor; grafik de repodan gelen küçük bir dosya, Drive'dan değil. Karşılığı, iki sayının
  sessizce ayrışması.
- *Süre bir gün kullanıcı ayarı olursa?* — O zaman bu port başka bir yerden cevaplanır ve export
  yine değişmez. Portun asıl kazancı bu.
