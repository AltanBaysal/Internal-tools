# Madde 150 — Test turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m150-quality-testler-design.md) ·
**Tur:** test *(kırmızı commit'lenir)*

Yalnız testler. Bu turda `build_prompts.py` ve `schema.py`'ye **dokunulmuyor**.

---

## 1. `test_build_prompts.py` — ortak sabiti çevir

- Üstteki import'a `DEFAULT_QUALITY` eklenir.
- `QUALITY = "score_9_up, masterpiece"` → `QUALITY = DEFAULT_QUALITY`, ve neden böyle olduğu tek
  satırlık bir yorumla yazılır.
- `_structure()`'dan `"quality": QUALITY` satırı silinir.

**Beklenen:** bu üç değişiklikten sonra dosyadaki iddiaların neredeyse tamamı **yeşil** kalır.

## 2. `test_build_prompts.py` — düşen testleri çevir

- `test_a_structure_without_quality_gets_the_chain_from_code` — içindeki `del structure["quality"]`
  artık `KeyError` verir; satır gider, testin adı ve iddiası *"zincir hep koddan gelir"* olur.
- `test_a_file_that_writes_its_own_quality_keeps_it` → **`…_is_ignored`**. İddia ters döner: dosyanın
  zinciri promptta **yok**, kodunki **var**.
- `test_a_try_without_quality_gets_the_chain_from_code` — aynı `del` sorunu; aynı şekilde çevrilir.
- Boşluklu `quality=" score_9_up , "` testi — o test kırpmayı ölçüyordu ve artık kırpılacak bir alan
  yok. Kırpma iddiası **başka bir alana** taşınır *(`action`)*, çünkü ölçtüğü şey `_tags`'in
  davranışı ve o duruyor.
- `build_prompts({"quality": QUALITY})` çağrısı — *"karesi olmayan dosya"* testi. Anahtar anlamsız
  kaldığı için çıkarılır, test aynı şeyi ölçmeye devam eder.

## 3. `test_build_prompts.py` — yeni testler

- **`test_a_file_that_writes_its_own_quality_is_ignored`** *(yukarıda, çevrilmiş hâli)*
- **`test_a_try_ignores_the_files_own_quality`** — aynısı `build_character_prompts` için; bugün bu
  testin karşılığı yok.
- **`test_the_quality_field_changes_nothing`** — aynı yapı, biri alanlı biri alansız, **aynı**
  promptu üretiyor. Alanın ölü olduğunu söyleyen tek iddia.

## 4. `test_schema.py` — üç test

- `test_the_schema_says_where_the_quality_chain_comes_from` → **`test_the_schema_never_mentions_quality`**.
  Şema metninde `quality` kelimesi hiç geçmiyor.
- `test_the_example_carries_no_quality_field` — bugün yalnız örneğe bakıyor, yeni testin içinde
  kalıyor; çıkarılır, çünkü yeni test daha geniş olanı söylüyor.
- `test_the_rulebook_names_the_quality_field_that_actually_exists` → **kaldırılır**. Anlattığı kural
  kitapçıktan çıkıyor.
- **`test_the_rulebook_has_no_quality_rule`** eklenir — 3. kural gitmiş olmalı.

## 5. `test_tools.py` — iddia duruyor, yalnız sebebi yazılıyor

- *"`add_frames` haritalara dokunmuyor"* iddiasındaki `quality` **çıkarılmıyor**. Yazarken görüldü
  ki o iddia artık daha iyi bir şey ölçüyor: alan ölü olsa da araç onu **temizlemiyor**, eski
  dosyanın kopyası yerinde kalıyor. Bu maddenin sözü tam olarak bu, o yüzden kalıyor ve neden
  kaldığı bir yorumla yazılıyor.
- Aynı dosyadaki `quality` taşıyan fixture'lara da dokunulmuyor — eski dosyanın temsilcisi onlar.

## 6. Koş ve kırmızıyı gör

```
python -m pytest queen-agent -q
```

Kırmızı olmalı: 2. ve 3. adımdaki dört iddia, 4. adımdaki iki test. Başka yerde kırmızı çıkarsa
durup bakılır.

Diğer üç satır da koşulur — bu madde onlara dokunmuyor, yeşil kalmalılar.

## 7. Kırmızı commit'lenir

`test(m150): …` — mesajda hangi davranışın çivilendiği ve kırmızının neden az olduğu yazılır.
