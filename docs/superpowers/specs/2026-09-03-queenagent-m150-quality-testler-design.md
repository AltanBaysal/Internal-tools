# Madde 150 — Test turu tasarımı: `quality` kalkar

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** test *(kırmızı commit'lenir)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 150

---

## Ne çivileniyor

Yapı dosyasının `quality` alanı artık **hiçbir şeye yaramıyor**. `build_prompts` ve
`build_character_prompts` her zaman kodun kendi zincirini yazıyor, dosyada ne yazarsa yazsın.
Şema da alandan hiç söz etmiyor.

## Bugünkü davranış

`build_prompts.py` iki yerde aynı şeyi yapıyor:

```python
lead = [structure.get("quality") or DEFAULT_QUALITY, frame.get("people", "")]   # 51
quality = structure.get("quality") or DEFAULT_QUALITY                            # 97
```

Yani dosyanın alanı **kazanıyor**, kod yalnız alan yokken devreye giriyor. 150 bunu tersine
çeviriyor: kod her zaman kazanıyor, alan hiç okunmuyor.

`schema.py` de iki yerde alandan söz ediyor — 81-83. satırlardaki paragraf *("farklı bir zincir
gerekiyorsa `quality` yaz")* ve kitapçığın 3. kuralı *("kalite etiketi karenin alanına yazılmaz")*.

---

## Testlerin şekli

### 1. Ortak sabit tersine dönüyor

`test_build_prompts.py` bugün kendi uydurma zincirini kullanıyor:

```python
QUALITY = "score_9_up, masterpiece"
```

ve `_structure()` onu dosyaya yazıyor. Bundan sonra sabit **kodun zinciri** oluyor:

```python
from backend.features.workspace.domain.build_prompts import DEFAULT_QUALITY
QUALITY = DEFAULT_QUALITY
```

ve `_structure()` artık `quality` yazmıyor.

**Neden böyle:** dosyadaki onlarca `f"{QUALITY}, …"` iddiası olduğu gibi kalıyor, ama artık kodun
zincirini bekliyor. Tek satırlık bir değişiklik bütün dosyayı yeni davranışa çeviriyor, ve
iddiaların hiçbiri elle güncellenmiyor — güncellenseydi biri unutulur, ve unutulan yeşil kalırdı.

### 2. Tersine çevrilen test

Bugün `test_a_file_that_writes_its_own_quality_keeps_it` var ve şunu iddia ediyor:

```python
assert built.startswith(f"{QUALITY}, ")
assert DEFAULT_QUALITY not in built
```

Bu testin **iddiası ters dönüyor**, adı da: dosyanın kendi zinciri **yok sayılıyor**, promptta
kodunki duruyor.

Bu, koşunun tek gerçek davranış değişikliği — o yüzden kendi testi olarak duruyor, bir fixture
değişikliğinin yan etkisi olarak değil.

### 3. Yeni testler

- **Kendi zincirini yazan dosya yok sayılır** *(yukarıdaki, tersine çevrilmiş hâli)*.
- **Aynısı `build_character_prompts` için** — bugün yalnız *"alan yoksa koddan gelir"* testi var;
  *"alan varsa yine koddan gelir"* testi yok.
- **Alanın varlığı promptu hiç değiştirmiyor:** aynı yapı, biri `quality` alanlı biri alansız, aynı
  promptu üretiyor. Bu ikisini tek iddiada bağlayan test, alanın tamamen ölü olduğunu söyleyen tek
  cümle.
- **Şema `quality` kelimesini hiç geçirmiyor** — bugünkü *"şema zincirin nereden geldiğini söyler"*
  testi ters dönüyor.
- **Kitapçıkta kalite kuralı kalmıyor** — 3. kural gidiyor, ve bugünkü *"kitapçık var olan alanı
  anıyor"* testi de onunla.

### 4. Dokunulmayanlar

- `DEFAULT_QUALITY`'nin **içeriği** değişmiyor. Zincirin ne olduğu bu maddenin konusu değil; nereden
  geldiği konusu.
- Promptun **sırası** değişmiyor. Zincir yine en başta.
- `test_tools.py` ve `test_stream_answer.py`'deki `quality` taşıyan fixture'lar **duruyor** — onlar
  eski dosyaların temsilcisi, ve eski dosyanın bozulmaması bu maddenin sözü. Yalnız
  `test_tools.py`'nin *"yapı dosyasının anahtarları"* iddiası `quality`'yi beklemeyi bırakıyor.

---

## Kırmızının şekli

Testler yazıldığında **kod hâlâ eski**: `structure.get("quality") or DEFAULT_QUALITY`. O yüzden

- kendi zincirini yazan dosyanın yok sayıldığını söyleyen testler **düşer**,
- şemanın `quality` geçirmediğini söyleyen testler **düşer**,
- geri kalan onlarca test **yeşil kalır**, çünkü `_structure()` artık alanı yazmıyor ve kod zaten
  alan yokken `DEFAULT_QUALITY` kullanıyor.

Bu ayrım önemli: kırmızı sayısı az olacak, ve az olması doğru. Değişen davranış küçük; büyük olan
şey fixture'ın yer değiştirmesi, ve o zaten bugünkü kodla yeşil.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```

Kırmızılar yalnız yukarıda sayılanlar olmalı. Başka bir yerde kırmızı çıkarsa, fixture değişikliği
görmediğimiz bir yere dokunmuş demektir — ve o kırmızı bu maddenin değil, bulgu.
