# Madde 114 — Şemanın örneği model sözlüğüyle yazılır · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m114-ornek-sozlugu-testler-design.md) —
dört kırmızı `188d212`'de.

## Değişen tek dosya: `schema.py`

**Örnekte üç değer.** İkinci karenin action'ı artikelini bırakıyor *(`standing by window`)*, iki
kamera da tag yazımına geçiyor: `medium shot, from above` ve `upper body, from side`. Örnek
öğretmen olduğu için düzeltme örneğin kendisinde; kurallar zaten yerindeydi.

**Düzyazıda sözlük.** Kamera paragrafındaki açı listesi `from side, from above, from behind,
looking at viewer` oluyor. Liste bir sözlük sayıyor — yanlış yazılan sözlük örneği tek başına
bırakır.

**Biçim paragrafına tek cümle.** *"never a sentence telling the story"*'nin hemen ardına:

> An article is not a tag, so it is dropped: sitting on couch, by window.

İki küçük örnek de doğru biçimde. Yanlış biçimi göstermek zayıf modelde onu kopyalatır — kural
yalnız olması gerekenle anlatılıyor.

## Neden kural değil örnek düzeliyor

7. kural artikeli zaten yasaklıyor ve düzyazı *"The example is the measure"* diyor. Kırık olan
öğretmendi: kuralı bir kez daha yazmak çelişkiyi çözmez, örneği kurala uydurmak çözer. Eklenen tek
cümle de yeni bir yasak değil — 7. kuralın biçimin öğretildiği yerde de duyulması.

## Değişmeyen

- **`build_prompts` ve `DEFAULT_QUALITY`.** Kod ne yazıldıysa onu basıyor; bu madde ne yazıldığıyla
  ilgili.
- **Skill metinleri.** Sözlük şemanın işi, ve şemayı iki skill de çekiyor.
- **`cowboy shot` girmiyor**, karakter değerlerinin üslubu duruyor *(§5c)*.

## Görülür hâli

Dört kırmızı yeşerir; şemanın öteki pinleri *(kamera yarımları, süpürme, yoğunluk, kural defteri)*
yerinde kalır. Ön yüz değişmiyor, `dist` derlenmiyor.
