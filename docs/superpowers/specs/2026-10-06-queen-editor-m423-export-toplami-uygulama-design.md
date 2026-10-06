# Madde 423 — Export'un toplamı her videonun kendi uzunluğundan, uygulama turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 423 · v9-1c · **Tur:** 2/2 — kod.
**Üstüne kurulduğu:** [m423 test turu](2026-10-06-queen-editor-m423-export-toplami-testler-design.md)
— kararlar, elenen yollar ve bilinen sonuçlar orada. Kırmızı suite: `477bdcdb`, 7 kırmızı.

## Yaklaşımlar

- **Seçilen — uzunluk galeri kartından geçer.** Özet bugün galeriden okuyor (`list_frames` →
  `exportable`), "hangi karenin videosu var" sorusunun her yerde tek cevabı olsun diye. Videonun
  uzunluğu da aynı yoldan gelir: katlanış → kart → özet. Kopya kare kaynağının kartından taşıdığı
  için (`copy_frame._carry`), kartın haritası kopyaya da gerekiyor.
- **Elenen — özetin kaydın katlanışını ayrıca okuması:** kartta harita olmazdı, ama özet aynı
  soruya galerinin yanında ikinci bir okumayla cevap verirdi; ve kopya yine kartın haritasını
  isterdi.

## Birimler — hepsi değişen, yeni dosya yok

- **`data/photo_record.py` — `slots`:** satırın `seconds`'ı sayıysa hücreye `"seconds"` olarak
  girer, `renderSeconds` gibi; sayı olmayan ya da hiç olmayan satırın hücresinde anahtar yok.
  Belgesi beşinci alanı söyler.
- **`domain/ports.py` — `PhotoRecord.slots`'un belgesi:** `"seconds"` — yalnız seçilen uzunlukta
  üretilen videoda, ne kadar sürdüğü.
- **`domain/usecases/list_frames.py` — `card`:** `"lengths": _per_layer(cells, "seconds")`.
  `_per_layer`'ın belgesi kullanıcılarının sorusuna *"ne kadar sürdüğü"*nü ekler.
- **`domain/copy_frame.py` — `CARRIED`:** `("lengths", "seconds")`; yorumu kopyanın neden taşıdığını
  söyler — aynı video export'ta iki uzunlukla sayılmasın.
- **`domain/usecases/export_summary.py`:** her videonun uzunluğu kartının `lengths["video"]`'ı; yoksa
  `seconds()`. `seconds()` bugünkü gibi bir kez sorulur. Toplam bunların toplamı. Modül belgesi ve
  fonksiyonun belgesi doğru olanı söyler: uzunluk ölçülmez, her video yapıldığı uzunluktadır;
  satırı söylemeyen oturumun grafiğiyle sayılır, ve satır hangi modelin yaptığını söylemediği için
  başka bir oturumun modelinin yaptığı video bu oturumunkiyle sayılır.
- **`data/comfy_h3_video_generator.py` — `seconds()`'ın belgesi:** *"The export summary quotes it
  for every video"* artık doğru değil; satırı uzunluk söylemeyen her video.
- **`main.py` — özetin bağlantısındaki yorum:** grafiğin uzunluğu grafiğiyle yapılan videonun;
  seçilen uzunlukta yapılan kendi satırında söyler. Bağlantı aynı.

**Değişmeyen:** özetin imzası ve cevabı; kapı; döngü ve 422'nin satırı; üreticilerin kodu;
frontend ve `dist`.

## Doğrulama

Dört satır. Test turunun 7 kırmızısı yeşile döner; öteki her şey yeşil kalır.
