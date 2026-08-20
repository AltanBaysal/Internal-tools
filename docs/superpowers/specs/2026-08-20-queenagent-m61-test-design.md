# Madde 61 · Tur 1 (test) — Tasarım

**Madde:** yeni — kullanıcı isteği, 20 Ağustos: "defteri düzgün adlandır, queen-editor'ünkiyle
karışıyor".
**Bu belgenin konusu:** defterin adını **ne tutacak**.

---

## Sorun

İki defter de `app.ipynb`. Colab bir defteri sekmede **yalnız dosya adıyla** gösteriyor, klasör
yolunu değil. İkisi açıkken hangisinin hangisi olduğu görülmüyor — ve yanlış defterde Run all'a
basmak, yanlış depoyu klonlayıp yanlış uygulamayı ayağa kaldırmak demek.

Bu, kodun söyleyemeyeceği bir sorun: iki dosya da kendi klasöründe tamamen doğru duruyor. Ancak
ikisi bir araya geldiğinde ortaya çıkıyor.

## Ad

`queenagent.ipynb`.

- **Tek kelime**, `QUEENAGENT_ROOT` ve `QUEENAGENT_PASSWORD` ile aynı yazım — ürün adı depoda zaten
  böyle bitişik yazılıyor.
- **Küçük harf**, `main.py` ve diğer kod dosyaları gibi. Büyük harfli adlar bu depoda belgelere
  ayrılmış (`README.md`, `FOUNDATION.md`).
- **Klasör adıyla birebir aynı değil** (`queen-agent`): tire yok, çünkü Colab'da okunan şey ürün
  adı, dizin adı değil.

## Testin sorması gereken

Defterin **yeni adda** olduğu. Bugünkü test dosyanın konumunu bir sabitte tutuyor; o sabit değişince
bütün defter testleri düşer — çünkü hepsi aynı dosyayı okuyor.

Bu, tek satırlık bir değişikliğin **on beş testi** birden kırmızıya çevirmesi demek. Bu iyi:
adlandırma, testlerin tamamının dayandığı zemin, ve zemin kayınca hepsinin bunu söylemesi doğru.

## queen-editor'ün defteri

**Dokunulmuyor.** O `app.ipynb` olarak kalıyor: bu madde QueenAgent'ın defterini ayırt edilebilir
kılmak için var, ve ikisini birden yeniden adlandırmak başka bir aracın kararına el atmak olurdu.
İkisinden birinin ayrışması karışıklığı zaten bitiriyor.

## Eski belgeler

`docs/superpowers/` altındaki madde spec ve planları eski adı taşımaya devam edecek. Onlar
yazıldıkları günün kaydı ve kasten eskiyorlar — deponun kuralı. Düzeltilecek olan yalnız **canlı**
olanlar: testin kendisi ve yürürlükteki yol haritası.
