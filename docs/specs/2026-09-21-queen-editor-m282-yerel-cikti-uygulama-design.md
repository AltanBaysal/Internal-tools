# Madde 282 · Birleşmiş dosya yerel diskte bitecek — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m282-yerel-cikti-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**`run_export`'un birleşik dalı iki adım oluyor:** birleştirme hedefi `cutting` klasörü — yani
`/tmp` — ve iş dönünce `store.copy_export(...)` dosyayı Drive'daki export klasörüne alıyor.
Sıra koddan okunuyor: kopyalama `merge()` döndükten sonraki satır.

**`copy_export` store'a geliyor**, ve `copy_photo`'nun usulünü izliyor: geçici bir ada kopyalanıp
`os.replace` ile üstüne taşınıyor. **Sebep Drive'ın yavaşlığı** — yarı yazılmış bir hedefin
görülme penceresi burada gerçek, ve `os.replace` *(rename değil)* Windows'ta da var olan bir hedefi
kabul ediyor, yani iki işletim sistemi aynı davranıyor.

**`copy_photo`'nun *"zaten varsa dokunma"* dalı buraya gelmiyor:** o dal iki modun aynı dakikada
aynı fotoğrafı istemesi için vardı; birleşmiş dosyayı yazan tek bir koşu var, ve aynı modun ikinci
koşusu `ExportRunner` tarafından zaten reddediliyor.

**Exporter'a dokunulmuyor.** Ona verilen hedef bir yol; Drive diye bir şey bilmiyor ve
bilmeyecek.

**Temizlik kendiliğinden geliyor:** `cutting` klasörü zaten iş sonunda siliniyor *(235)*, ve
birleşmiş dosya artık onun içinde — yani yerel kopya arkada kalmıyor. Düşen bir koşuda da aynı
temizlik koşuyor *(madde 94)*.

## Bunun getirdiği

**Drive'a tek seferde tek dosya yazılıyor**, akış hâlinde değil. Kazanç ölçülmedi ve buraya sayı
yazılmıyor; dayanak Colab'ın bilinen davranışı.

**Yan fayda, bedava:** iş sürerken Drive'daki klasör boş kalıyor. Yarım bir mp4 orada hiç
görünmüyor — madde 94'ün *"yarım export bitmiş gibi görünür"* kuralı bir adım daha sağlam.

**Bedeli, açıkça:** birleşmiş dosya bir kez `/tmp`'ye, bir kez Drive'a yazılıyor — yerel diskte
geçici olarak dosya boyu kadar yer gerekiyor. Colab'ın yerel diski onlarca GB, ve parçalar zaten
orada duruyor *(235)*.

## Bu turda değişen

- `domain/usecases/run_export.py`: birleşik dal yerel hedefe birleştiriyor, sonra kopyalıyor.
- `data/photo_store.py`: `copy_export` geldi.
