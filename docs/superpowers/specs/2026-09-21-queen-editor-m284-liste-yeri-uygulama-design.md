# Madde 284 · `pieces.txt` parçaların yanında duracak — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m284-liste-yeri-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**Tek satır:** listenin klasörü `os.path.dirname(target)` olmaktan çıkıp
`os.path.dirname(pieces[0])` oluyor. Liste parçaların okuma sırası, ve ait olduğu şeyin yanında
duruyor.

**`pieces` boş olamaz**, ve bu kontrol eklenmiyor: boş bir sette `sizes[0]` çoktan patlıyordu, ve
`run_export` kare yoksa birleştirmeye hiç gelmiyor. Olmayan bir durum için yazılan bir koruma, her
sonraki düzenlemede ödenir *(bu deponun style kuralı)*.

**Değişmeyen:** listenin biçimi *(`file '<yol>'`, tek tırnak `concat`'in kendi kaçışı)*, silinmesi
*(`finally`)*, ve adı.

## Bunun getirdiği

Hedef bir gün yine Drive'a dönerse liste onu takip etmiyor. **Bugün belirti yoktu** — 282 hedefi
`/tmp`'ye almıştı — ve bu madde belirtiyi değil **kuralı** düzeltiyor: bir testle çivili, yani
dönüş de mümkün değil.

## Bu turda değişen

- `data/ffmpeg_video_exporter.py`: listenin yazıldığı klasör.
