# Madde 111 — Kamera tek tipten çıkar · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 111.
**Gözlenen** *(28 Ağustos)*: on karelik senaryonun yedisi düz `medium shot` çıktı — on sahne, tek
kadraj.

## Sebep

- **Şema kameranın neyden yapıldığını söylemiyor.** `camera` diye bir alan var, örnekte bir değer
  duruyor, ama değerin iki karardan oluştuğu *(ne kadarı görünüyor + nereden bakılıyor)* hiçbir
  yerde yazmıyor. Zayıf model tek örneği kalıp alıyor.
- **prompt+ çeşitliliği istemiyor.** Kamera *"this skill's own work"* diyor, ama komşu karelerin
  birbirinden ayrışması gerektiğini söyleyen bir cümle yok.

*(109 örneğe ikinci bir kamera değeri getirdi — o kadarı kalıbı kırmaya yetmiyor, kural lazım.)*

## Testler

### `test_schema.py` — bir yeni

Kameranın iki parçası yazılı: `"how much of the body"` ve `"where it is looking from"`.

### `test_skills.py` — bir yeni

prompt+ komşu karelerin ayrışmasını istiyor: `"the same framing and angle"` ve `"differ in at
least one"`.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_schema.py` | 1 |
| `test_skills.py` | 1 |

Defter çifti bu maddenin değil.

## Bilerek yapılmayanlar

- **Koda kamera listesi girmez** — `build_prompts` ne yazıldıysa onu basar *(K26)*.
- **Sabit bir kamera sırası dayatılmaz** — kural *"aynı ikiliyi arka arkaya tekrarlama"*, bir
  rotasyon değil.
- **"shot" süpürme testleri korunur:** yeni metinlerde kelime yalnız `medium shot` olarak geçebilir.
- **`dist` derlenmez.**
