# Madde 110 — Kalite etiketleri koddan gelir · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 110.
**Sebep:** `quality` bugün dosyanın alanı, yani modelin yazdığı şey — ve model onu şemadaki
örnekten kopyalıyor. Örnekteki dizi iki ayrı model ailesinin karışımı olduğu için her senaryo o
karışımı taşıyor. Zincir senaryodan senaryoya değişmiyor: koda iner.

**Kullanıcı kararı** *(28 Ağustos)*: *"hep aynı olur, prompttan çıkarıp otomatik jsona atalım"* —
yazmayan model yanlış zincir de yazamaz.

## Kural

- Dosya `quality` taşımıyorsa kod kendi zincirini promptun başına koyar.
- Dosya kendi zincirini yazmışsa **o kullanılır** — kod kenara çekilir.
- Varsayılan zincir kullanıcının kendi çalışan promptundan gelir
  *([araştırma belgesi §5c](../research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md))*,
  ve tek bir yerde durur.

## Testler

### `test_build_prompts.py` — ikisi ölçü değişimi, biri yeni

- `test_a_structure_without_quality_still_builds` → alan yokken **varsayılan zincirle** başlıyor
  *(bugün hiç kalite yok — kırmızı)*.
- `test_a_try_without_quality_still_builds` → aynısı `build_character_prompts` için.
- **Yeni:** dosyanın kendi zinciri varsayılanın yerine geçiyor.

### `test_schema.py` — biri ölçü değişimi, ikisi yeni

- Alan listesi parametresinden `quality` çıkar — örnek artık o alanı göstermiyor.
- **Yeni:** örnekte `"quality"` alanı yok.
- **Yeni:** düzyazı zincirin koddan geldiğini ve alanın ne zaman yazılacağını söylüyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_build_prompts.py` | 3 *(2 ölçü değişimi + 1 yeni)* |
| `test_schema.py` | 2 yeni · parametre listesi değişimi kırmızı vermez |

Defter çifti bu maddenin değil.

## Bilerek yapılmayanlar

- **Kod yazılmaz** — `DEFAULT_QUALITY` tur 2'de doğar; testler onu **test içinde** import eder,
  yoksa dosyanın toplanması çöker ve turun öteki kırmızıları görünmez olur.
- **Kural defterinin 3. maddesi ellenmez** — kalitenin karede tekrarı hâlâ ihlal.
- **`dist` derlenmez.**
