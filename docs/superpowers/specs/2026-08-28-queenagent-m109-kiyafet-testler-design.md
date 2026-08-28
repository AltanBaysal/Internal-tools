# Madde 109 — Kıyafet giyenin olur · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 109.
**Gözlenen** *(28 Ağustos)*: iki karakterli senaryoda model tek `outfits` girdisi yazdı ve ikisine
birden verdi —

```
"evening_date": "elegant evening wear, button-up shirt with dark pants for man, black dress for woman"
```

Kod bu metni **adını anan herkese aynen** basıyor *(`build_prompts`, K26'nın çizgisi)*, dolayısıyla
beşinci karede erkeğin üstünde siyah elbise, kadının üstünde gömlek-pantolon var; üstelik `for man`
ve `or` görüntü modeline anlamsız kelime olarak gidiyor.

## Sebep

Şema *"bir kıyafet giyene göre değil giysiye göre adlandırılır, çünkü iki karakter aynısını
giyebilir"* diyor — yani **paylaşmayı** teşvik ediyor. Farklı giyinen iki kişinin **iki ayrı
girdi** istediğini hiçbir cümle söylemiyor, ve tek örnek tek karakterli.

## Testler — `test_schema.py`, üç yeni

1. **Bir girdi bir kişiyi giydirir:** düzyazıda `"dresses one person"` ve `"two entries"`.
2. **Kural defterinde sekizinci kural:** `"8."` ve `"for the man"` — iki kişiyi tek girdide
   toplamak ihlal.
3. **Örnek bunu gösteriyor:** ikinci bir kare var — `'"people": "1boy, 1girl"'` ve ikinci
   karakterin adı `deniz` örnekte geçiyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_schema.py` | 3 |

Defter çifti bu maddenin değil.

## Bilerek yapılmayanlar

- **Kod yazılmaz** — `build_prompts` değişmiyor, iş şemanın metninde.
- **`quality` alanına dokunulmaz** *(110)*, **kamera kuralı yazılmaz** *(111)*.
- **`dist` derlenmez** — ön yüz değişmiyor.
