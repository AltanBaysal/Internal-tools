# Madde 156 — test turu planı

**Spec:** [m156 sayım testler design](../specs/2026-09-03-queenagent-m156-sayim-testler-design.md)

Bu tur yalnız test yazar. Kod ikinci turda.

## 1. `test_build_prompts.py` — fikstüre türlü bir harita eklenir

Dosyanın `_structure()` fikstürü düz metin karakterler taşıyor ve **öyle kalıyor**: sayılmayan
girdinin kanıtı o. Türlü girdileri veren ayrı bir yardımcı giriyor:

```python
def _kinds(**people):
    """Characters written the way set_character writes them (Madde 154), kind and tags together."""
```

Çağrısı `_kinds(aylin="girl", deniz="boy")` gibi; metinleri `AYLIN`/`DENIZ` sabitlerinden alır, yani
var olan assertion'lar aynı kelimeyle okunur.

## 2. Sayım testleri yazılır

Spec'in 1–11 numaraları, sırayla, `test_build_prompts.py`'nin sonundaki prompt testlerinin yanına.
Her biri tek bir şey söyler:

- tekil, ikili, çoğul *(iki türde birden)*
- sıranın sabitliği — karenin kendi sırası ters iken bile `1boy, 1girl`
- yerin sabitliği — kalitenin ardında, liderin önünde
- sayılmayanlar — türsüz girdi, tanınmayan tür, boş kare
- yazılı `people`'ın kazanması
- önizlemede sayı olmaması

## 3. Var olan iki test güncellenir

- `test_a_character_written_with_a_kind_still_builds` — beklenen prompta `1girl` girer. Yorumu da
  düzelir: *"the kind is for counting"* artık gelecek zaman değil.
- Başka bir prompt testinin fikstürü türlü değil, o yüzden hiçbiri kaymıyor. **Koşturup doğrulanır**
  — düz metin fikstürünün sayıya dokunmadığı bir varsayım, ve kırmızının hangi testlerde olduğu bunu
  söyler.

## 4. `test_schema.py` düzenlenir

- Parametre listesinden `people` çıkar.
- `test_the_example_shows_two_people_in_different_clothes`'un çivisi iki ayrı kıyafete kayar.
- `test_the_rulebook_has_a_sixth_rule_about_the_count` yerini
  `test_the_rulebook_has_no_count_rule`'a bırakır.
- `test_the_schema_never_shows_a_people_field` eklenir — tırnaklı biçime vurur.

## 5. Koşulur ve kırmızı görülür

CLAUDE.md'nin dört satırı, **sırayla** *(paralel koşturmak queen-agent frontend'inde
`test-setup.js`'i düşürüyor — m150'de görüldü)*:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-agent` kırmızı *(yeni sayım ve şema testleri + notebook'un bilinen iki kırmızısı)*,
diğer üç satır yeşil.

## 6. Kırmızı commit'lenir

`test(m156): …` — mesajda çift tırnak yok.
