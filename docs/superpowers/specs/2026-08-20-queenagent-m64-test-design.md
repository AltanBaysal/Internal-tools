# Madde 64 · Tur 1 (test) — Tasarım

**Madde:** yeni — `feat/queenagent-colab` main'e merge edildi (20 Ağustos, fast-forward).
**Bu belgenin konusu:** defterin **hangi daldan klonladığını** ne tutacak.

---

## Sorun

CONFIG hücresi bugün şunu diyor:

```python
BRANCH = "feat/queenagent-colab"
```

Gerekçesi yorumunda yazılı ve yazıldığı gün doğruydu: *"main bunu taşımıyor, ve olmayan bir dal
klon anında sebebi görünmeyen bir hatayla düşer."* Merge o cümleyi yalanladı — main artık taşıyor.

Bugün **çalışmaya devam ediyor**, çünkü dal hâlâ duruyor. Tehlike de bu: yanlışlık görünmüyor. Dal
silindiği gün defter `Remote branch feat/queenagent-colab not found` diyecek, ve o cümleyi okuyan
kişinin elinde bunun ne zaman ve neden yanlış hâle geldiğine dair hiçbir şey olmayacak.

Bir özellik dalı yaşamak için açılır; yayına çıkan iş main'de durur. Bir kullanıcının eline verilen
defterin özellik dalından klonlaması, geçici olanı kalıcı sanmaktır.

## Karar

`BRANCH = "main"`.

## Testin sorması gerekenler

İki ayrı şey, ve ikincisi birincisinden geniş:

1. **Defter main'den klonluyor.** Bir kararın kendisi — `XAI_MODEL`'in `grok-4.3`'e sabitlenmesi
   gibi, farkında olunmadan değişince kullanıcıyı vuran cinsten.

2. **Defter hiçbir özellik dalını işaret etmiyor.** Asıl kural bu. Bir madde koşulurken `BRANCH`'i
   geçici olarak kendi dalına çevirmek doğaldır; **öyle commit'lemek** değil. Birinci test yalnız
   `BRANCH` satırına bakar, bu ikincisi dosyanın tamamına bakar — yorum içinde unutulmuş bir dal
   adı da yakalanır.

İkisi de bugün gerçekten kırmızı: birincisi değer yanlış olduğu için, ikincisi dosyada `feat/`
geçtiği için.

## Bu maddenin dokunmadığı

`docs/superpowers/plans/2026-08-20-queenagent-m55-impl-plan.md`, `BRANCH`'in neden özellik dalı
olduğunu anlatıyor. **Dokunulmuyor:** yazıldığı günün kaydı, ve deponun kuralı onların kasten
eskimesi. Düzeltilecek olan yalnız canlı olanlar — defterin kendisi ve yürürlükteki yol haritası.
