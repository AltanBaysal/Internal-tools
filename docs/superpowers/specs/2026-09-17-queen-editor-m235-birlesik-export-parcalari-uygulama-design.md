# Madde 235 · Birleşik export parçalarını Drive'a bırakmaz — uygulama turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m235-birlesik-export-parcalari-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Tasarım

**Depo** *(`DrivePhotoStore`)* yeni bir kapı açıyor: `make_pieces_dir()`, makinenin kendi geçici
klasöründe *(`tempfile.mkdtemp`)* boş bir klasör açıp yolunu veriyor. Yolu yalnız depo biliyor,
CODE-STANDARD'ın katman kuralına göre: dosyanın nerede durduğu data katmanının işi. Kaldırması için
yeni bir şeye gerek yok, `remove_dir` zaten var.

**Kullanım durumu** *(`run_export`)* iki yerde değişiyor:

- Parçaların yazılacağı klasör moda göre seçiliyor: birleşikte `make_pieces_dir()`, ayrıda bugünkü
  export klasörü. Döngünün kendisi aynı kalıyor.
- Birleştirme bittikten sonra çalışma klasörü kaldırılıyor. Yarım kalan koşu — hata ya da iptal —
  export klasörünün yanında onu da kaldırıyor, çünkü Colab oturumu bitene kadar orada kalmasının
  kimseye faydası yok.

Fotoğraflar iki modda da Drive'a yazılıyor, değişen bir şey yok.

**Neden alt klasör değil de geçici klasör:** iki export aynı anda koşabiliyor ve dakikaya kadar
adlandırılmış aynı export klasörünü paylaşıyorlar. Parçalar Drive'a hiç uğramayınca birleşiğin
silmesi ayrının dosyalarına dokunamıyor — FOUNDATION 1, kullanıcının işi kutsal.

`pieces.txt` birleştirmenin hedefinin yanına yazılıp siliniyor, bugünkü gibi: tek satırlık bir
dosya, ve Drive'a yazılan asıl yük parçalardı.

## Bu turda değişen

`photo_store.py` ve `run_export.py`. Ön yüz değişmiyor.
