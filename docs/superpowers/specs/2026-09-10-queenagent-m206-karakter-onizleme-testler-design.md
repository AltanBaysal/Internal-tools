# Madde 206 — karakter önizleme aracı kalkar · test turu

**Kaynak:** [yol haritasının Madde 206'sı](../plans/2026-09-06-queenagent-v8-roadmap.md).

## Ne kanıtlanacak

Madde `build_character_prompts` aracını kaldırıyor: bir karakteri, dosyadaki her kıyafetle, kare
dışında gösteren **önizleme**. Senaryonun çıktısına hiçbir şey katmıyor — yazdığı dosya
`build_prompts`'un listesine girmiyor, hiçbir kare ondan beslenmiyor — ve tarifi her istekte
gidiyor.

Bu turun işi, aracın **ve arkasındaki her şeyin** gittiğini gösteren testleri yazmak. Kod hâlâ
yerinde olduğu için hepsi **kırmızı** verecek.

205'in kalıbı sürüyor: bir kaldırma iki iddia taşır — ad `TOOL_SPECS`'te yok, **ve** o adı taşıyan
eski bir kayıt hâlâ gelebildiği için `run_tool` çökmek yerine cevap veriyor.

## Aracın kuyruğu

Araç yalnız kendi değil. Kaldırılınca çağıranı kalmayan üç şey daha var, ve her biri ayrı bir test
alıyor — çünkü her biri **duruyor bırakılabilirdi** ve bırakılmıyor:

| Ne | Neden gidiyor |
|---|---|
| `build_character_prompts` *(kurucu)* | Aracın çağırdığı tek şey buydu |
| `character_prompts_name` | Yalnız önizlemenin çıktı dosyasını adlandırıyordu |
| `naming.folded` | Tek çağıranı `character_prompts_name`'di — 205 `tools.py`'deki ötekini almıştı |

`naming.unique_name` **duruyor**: üç depo onu kullanıyor, ve bu maddeyle ilgisi yok.

## Yazılacak testler

### `test_tools.py` — aracın yokluğu

- **`test_the_character_preview_tool_is_gone`** — ad `TOOL_SPECS`'te geçmiyor, ve o adla yapılan
  bir çağrı `no tool called` diyor.
- **`test_no_tool_is_expected_to_write_a_character_preview`** — `WRITES_FILES` adı taşımıyor. Ayrı
  test: orası sohbetin kart çizdiği küme, ve orada kalan ölü bir ad, çağrılamayan bir araç için
  kart çizmeye hazır bir arayüz demek.
- **`test_the_character_preview_text_is_gone`** — `prompt` modülünde ne `BUILD_CHARACTER_PROMPTS`
  var ne de `BUILD_CHARACTER_PROMPTS_CHARACTER`. Metin, maddenin asıl kazancı: her istekte giden
  şey oydu.

### `test_modes.py` — kipin listesi

- **`test_no_mode_lets_the_character_preview_through`** — hiçbir kipin sormadan-koşanlar listesi
  adı taşımıyor.

  Listeye bakarak yazılıyor, `needs_permission` üzerinden değil: o fonksiyon tanımadığı bir araca
  `False` dönüyor, yani kalkmış bir ad üzerinden kurulan bir iddia hiçbir şey sormadan yeşil geçer.
  205 bu tuzağı kaydetti; bu test onun ikinci kez kurulmasını engelliyor.

### `test_build_prompts.py` — kurucu ve adı

- **`test_the_character_preview_constructor_is_gone`** — modülde ne `build_character_prompts` var
  ne `character_prompts_name`.
- **`test_the_folding_rule_goes_with_the_name_it_was_written_for`** — `naming` modülünde `folded`
  yok. Buraya yazılıyor çünkü tek çağıranı bu dosyadaydı; `unique_name`'in durduğu aynı testte
  söyleniyor ki kaldırmanın nerede durduğu görülsün.

### `test_skills.py` — akışın 2. adımı

- **`test_the_flow_no_longer_offers_a_look_at_one_character`** — akış metni adı hiç anmıyor.

  `test_no_instruction_names_a_tool_that_is_gone` bunu zaten yakalardı, ama **sonuç olarak**:
  o test cümlenin kalkmasını zorlar, sebebini söylemez. Cümlenin gitmesi 18 numaralı düzeltmenin
  kararıydı ve kendi testini hak ediyor.

## Bu turda yazılmayanlar

- **Ölecek testler silinmiyor.** `test_tools.py`'de beş, `test_build_prompts.py`'de yedi test bugün
  **yeşil**, çünkü kod yerinde. Silmek uygulama turunun işi; şimdi silmek, kırmızıyı görmeden
  yeşile boyamak olur.
- **`test_every_tool_is_declared_to_the_model`** bugün adı sayıyor ve bugün yeşil. Şema kalkınca
  kırmızıya döner ve orada düzeltilir.
- **`build_prompts`** ellenmiyor: listeyi kuran yol bu maddenin dışında.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
```

Yedi yeni test kırmızı, geri kalan süit yeşil. Kırmızı hâliyle commit edilir.
