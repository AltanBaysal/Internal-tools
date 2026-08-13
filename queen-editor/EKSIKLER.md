# Eksikler

Bulunan her şey buraya. Düzeltmek ayrı iş — burası sadece liste.

Önceki 12 madde [v7 yol haritası](../docs/superpowers/plans/2026-08-13-queen-editor-v7-roadmap.md)
oldu ve kapandı. 2026-08-13 Colab turunda bulunan altı madde
[v11](../docs/superpowers/plans/2026-08-13-queen-editor-v11-roadmap.md) ile kapandı. Aşağıda kalanlar
**kurulumla ilgili üç madde** — onları ancak yeni bir Colab turu kapatabilir — ve **kararı sana
kalan iki şey.**

## Claude

- **Galeri karoları tam boy PNG çekiyor.** Bir kare ~1.5–2.5 MB; ilk açılışta ekrandaki 8 karo
  tünelden ~15 MB indiriyor. Karolar için küçük önizleme üretmek gerek — ne zaman üretilecek,
  nereye yazılacak, adı ne olacak, kare değişince ne olacak: kendi tasarımını ister.
- **Başarısız karede hover'la karartma iniyor.** Fare gelince kareyi örten koyu katman ve ortasında
  "Tekrar dene". Bu tasarımın kendi kararı; "hover'da kart ortalanıyor" derken bunu mu kastettin,
  yoksa etiketin köşe atlaması mıydı (o düzeltildi)?

## Sen

- **Fotoğraf üreticisini kuramıyorum.** "Kur"a basınca satır şunu diyor: *"Fotoğraf üreticisi
  kurulu değil. HTTP Error 403: Forbidden"*.
- **Video üreticisini de kuramıyorum.** Aynı cümle: *"Video üreticisi — HTTP Error 403:
  Forbidden"*.
- **Ses üreticisini kuramıyorum.** "Kur"a basınca satır şunu diyor: *"MMAudio kütüphanesi kuruldu
  ama bu süreçte görünmüyor — uygulamayı yeniden başlat."*

Bu üçü uygulamadaki "Kur" düğmesine basmakla ilgiliydi; o yol kapandı, kurulum artık Colab
defterinde ve seçtiğin üreticiler iniyor. Yani bunları kapatacak olan şey bir düzeltme değil, bir
tur: defteri çalıştırıp üç üreticinin de kurulu göründüğünü görmek.
