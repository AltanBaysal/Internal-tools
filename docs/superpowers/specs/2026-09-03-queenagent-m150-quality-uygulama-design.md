# Madde 150 — Uygulama turu tasarımı: `quality` kalkar

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** uygulama *(yeşile götürür)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 150 ·
[test turu tasarımı](2026-09-03-queenagent-m150-quality-testler-design.md)

---

## Kırmızıda duran beş test

```
test_a_file_that_writes_its_own_quality_is_ignored
test_the_quality_field_changes_nothing
test_a_try_ignores_the_files_own_quality
test_the_schema_never_mentions_quality
test_the_rulebook_has_no_quality_rule
```

İlk üçü `build_prompts.py`'yi, son ikisi `schema.py`'yi bekliyor.

---

## `build_prompts.py` — iki satır ve bir yorum

İki yerde aynı ifade duruyor:

```python
lead = [structure.get("quality") or DEFAULT_QUALITY, frame.get("people", "")]   # 51
quality = structure.get("quality") or DEFAULT_QUALITY                            # 97
```

İkisi de `DEFAULT_QUALITY` oluyor. `structure` artık `quality` diye bir alan **okumuyor**.

Ve sabitin üstündeki yorum bugün şunu söylüyor:

> *A scenario that needs a different one writes quality in its own file and this steps aside.*

Bu cümle artık **yalan**, o yüzden düzeltiliyor — kod ile çelişen yorumun düzeltilmesi bu deponun
kuralı. Yerine ne yazıldığı önemli: zincirin neden kodda olduğu *(Madde 110'un sebebi)* duruyor,
kapının neden kapandığı ekleniyor.

## `schema.py` — bir paragraf ve bir kural

**1. Paragraf gidiyor** *(81-83)*: *"Kalite zinciri bu dosyada değil… farklı bir zincir gerekiyorsa
`quality` yaz."* Cümlenin ikinci yarısı artık olmayan bir kapıyı tarif ediyor, birinci yarısı da
modelin bilmesine gerek olmayan bir şeyi anlatıyor. İkisi birden gidiyor — çünkü *"şunu yazma"*
diye bırakılan bir cümle, yazılabilecek bir alan olduğunu öğretir.

**2. Kitapçığın 3. kuralı gidiyor**: *"Kalite etiketleri karenin kendi alanlarına yazılmaz."*

## Numaralar kaymıyor, 3 boş kalıyor

Kitapçık 1'den 14'e numaralı. 3 çıkınca liste **1, 2, 4, 5, …** diye gidiyor.

**Neden kaydırmıyoruz:** numaralar var oldukları için anılıyorlar — dokuz test, birkaç kod yorumu ve
geçmiş commit mesajları kurala numarasıyla atıf yapıyor *("Rule 8 banned it in outfits")*.
Kaydırmak, hepsini sessizce başka bir kurala işaret eder hâle getirir.

**Emsali deponun kendinde:** Madde 142 açıldı, aynı gün düşürüldü, ve numarası tutuldu. Düşen bir
şeyin numarası boş kalır; bu kitapçık için de aynı.

## Dokunulmayanlar

- `DEFAULT_QUALITY`'nin **içeriği**. Zincirin ne olduğu bu maddenin konusu değil.
- Promptun sırası. Zincir yine en başta, `people` yine hemen ardında.
- `tools.py` — hiçbir araç `quality` yazmıyor ya da silmiyor. Eski dosyadaki alan yerinde kalıyor,
  yalnız okunmuyor.
- Frontend. Yapı dosyasını çizen panel alanların adını bilmiyor, ham JSON gösteriyor.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```

Beş kırmızı yeşile dönmeli, başka hiçbir şey değişmemeli. Diğer üç satır da koşulur.
