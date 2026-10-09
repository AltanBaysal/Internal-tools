# Madde 109 — Kıyafet giyenin olur · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m109-kiyafet-testler-design.md) — üç kırmızı
`6ba91fc`'de.

## Üç dokunuş, hepsi `schema.py`

**1 · Düzyazı.** Kıyafet paragrafının sonuna, paylaşma cümlesinin hemen ardına: bir girdi **tek
kişiyi giydirir** — tuttuğu metin, adını anan herkese olduğu gibi kopyalanır, dolayısıyla farklı
giyinen iki kişi **iki ayrı girdidir**. İkisini tek girdide toplamaya çalışan bir metin — *"or"*,
*"for the man"*, *"for the woman"* — erkeğe elbiseyi, kadına pantolonu giydirir.

Cümle paylaşma kuralını iptal etmiyor: aynı kıyafeti giyen iki karakter hâlâ tek girdiyi anar.
Kalkan şey, **tek girdinin iki farklı kıyafeti anlatması**.

**2 · Kural defteri, sekizinci kural.** İki kişiyi kapsayan tek kıyafet girdisi ihlaldir; adını
anan herkes bütün metni alır, o yüzden kıyafet takımı başına bir girdiye bölünür.

**3 · Örnek.** İkinci bir karakter *(`deniz`)*, üçüncü bir kıyafet *(`ceket`)* ve ikinci bir kare:
`"people": "1boy, 1girl"`, iki karakter, her biri kendi kıyafetiyle. Kuralı cümleyle anlatmak zayıf
modelde yetmiyor — kopyalanan şey örnek.

Kamera değeri `"upper body, from the side"` — *"shot"* kelimesi girmiyor *(sweep testi)*, ve kamera
çeşitliliği **111**'in işi, burada kural yazılmıyor.

## Değişmeyen

`build_prompts` *(K26: kod adı ne buluyorsa onu basar)*, `quality` alanı *(110)*, kalan yedi kural.

## Görülür hâli

Üç kırmızı yeşerir, başka test kırılmaz *(defter çifti hariç)*. Ön yüz değişmiyor, `dist`
derlenmez.
