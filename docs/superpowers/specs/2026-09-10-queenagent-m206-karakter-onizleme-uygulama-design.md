# Madde 206 — karakter önizleme aracı kalkar · uygulama turu

**Kaynak:** [test turu](2026-09-10-queenagent-m206-karakter-onizleme-testler-design.md) ve
[yol haritasının Madde 206'sı](../plans/2026-09-06-queenagent-v8-roadmap.md).

Yedi test kırmızı commit edildi *(`df6f581`)*. Bu tur onları yeşile çeviren kodu yazıyor —
yazarak değil, silerek.

## Nereden ne kalkıyor

### `tools.py`

| Yer | Ne |
|---|---|
| import | `build_character_prompts` ve `character_prompts_name` |
| `WRITES_FILES` | `"build_character_prompts"` girdisi |
| `TOOL_SPECS` | aracın şeması, iki parametresiyle |
| `run_tool` | `if name == "build_character_prompts"` dalı |
| gövde | `_try_character` işleyicisi |

### `build_prompts.py`

`build_character_prompts` *(kurucu)*, `character_prompts_name` *(çıktının adı)*, ve artık çağıranı
kalmayan `folded` import'u.

`build_prompts`, `render_module`, `prompts_name`, `cast_of` ve bütün özel yardımcılar **duruyor**:
listeyi kuran yol bu maddenin dışında.

### `naming.py`

`folded` gider. Tek çağıranı `character_prompts_name`'di; ötekini 205 `tools.py`'den almıştı.

**Modülün başlığı da düzelir.** Bugün *"The tools use it when the model asks for a name"* diyor, ve
bu cümle 205'ten beri yanlış: `tools.py` bu modülden bir şey almıyor. Kalan tek kural
`unique_name`, ve onu üç depo çağırıyor.

### `modes.py`

EDIT listesindeki `"build_character_prompts"` girdisi.

### `prompt.py`

`BUILD_CHARACTER_PROMPTS` ve `BUILD_CHARACTER_PROMPTS_CHARACTER`; `START_A_SCENARIO`'nun 2.
adımındaki *"Offer build_character_prompts as a look at one character; carry on if declined."*
cümlesi.

> Cümle giderken satır sonu kaybolmamalı: kalkan parçanın `\n`'i bir önceki parçaya taşınır,
> yoksa 2. adım 3. adımla aynı paragrafta birleşir.

## Ölen testler

Kod gidince iddiası kalmayanlar. Kırmızıya döndükleri için değil, **konusu kalmadığı** için
siliniyorlar.

### `test_tools.py`

- `test_every_tool_is_declared_to_the_model` — silinmiyor, **kısalıyor**: ad ve Madde 98'i anan
  yorumu kümeden çıkar.
- `test_trying_a_character_writes_a_file_named_after_both`
- `test_trying_a_character_reports_a_born_file`
- `test_trying_a_character_nobody_knows_writes_nothing`
- `test_a_character_try_says_how_many_prompts_it_wrote`
- Madde 135'in bölümü *(üç test)*: önizlemenin promptları geri vermesi, `1 prompt` sayması, ve
  dosyayı yine de yazması.

### `test_build_prompts.py`

`_tried` ve `_try_name` yardımcıları, ve onlara yaslanan sekiz test *(önizlemenin `BREAK`
taşımaması, kıyafet başına bir prompt, kıyafetsiz dosya, zincirin koddan gelmesi, dosyanın kendi
kalitesinin yok sayılması, bilinmeyen karakter, ve adlandırmanın iki testi)*.

### `test_modes.py`

`WRITES` listesindeki ad.

## Ne kaybolmuyor

- **Kıyafetsiz bir karakterin nasıl kurulduğu** `build_prompts`'un kendi testlerinde duruyor
  *(`test_a_character_with_no_outfit_is_just_the_identity`)*.
- **Zincirin koddan geldiği** `test_the_quality_chain_always_comes_from_code` ve
  `test_a_files_own_quality_chain_is_ignored` ile duruyor.
- **Bilinmeyen bir adın ne dediği** `test_an_unknown_character_names_the_frame_the_name_and_what_is_known`
  ile duruyor — kare numarasıyla, ki bu asıl yol.

Yani önizleme yolunun testlerinden hiçbiri **tek** kanıt değildi; hepsinin ikizi kare yolunda var.

## Kullanıcı ne görecek

Bir karakteri tek başına görmek isterse ajan girdisini okuyup gösterir, dosya yazmadan.
Senaryonun çıktısı değişmez: bu araç zaten ona girmiyordu.

## Doğrulama

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Yedi kırmızı yeşile döner, silinen testlerle birlikte toplam düşer, başka hiçbir şey kırmızıya
dönmez. Frontend ellenmiyor.
