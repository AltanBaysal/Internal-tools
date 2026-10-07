# Madde 172 · uygulama turu — şema uçar

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m172-sema-testler-design.md).
Commit `b0e6a8b` 21 vak'ayı çiviledi. Dilim 1'in son maddesi.

---

## Silinenler

- `schema.py` — modül. `STRUCTURE`, `RULEBOOK`, `SCHEMA` üçü birden.
- `read_prompt_structure_schema` — `TOOL_SPECS`'ten ve `run_tool`'dan. Kayıtlarda adı geçen eski bir
  tur yine cevap alıyor: *There is no tool called…* — silinen her aracın gittiği yol.
- `context_box.schema_was_read` ve `stream_answer`'ın kaba koyduğu şema bloğu. Kap **yalnız dosya**
  tutuyor, Madde 129'un kurduğu hâline dönüyor.
- `modes.READS` tek ada iniyor.

## Gelen

`SDXL_PROMPT_RULES`, ve **altı araç açıklamasının sonuna** ekleniyor: `add_` ve `update_` üçlüleri.

Metin dört paragraf: **biçim** *(İngilizce, etiket, artikel yok, yoğunluk)*, **sayı** *(karakterin
kendi girdisinde, `solo` orada değil)*, **ayrım** *(kıyafet karakterde değil, giysinin adını taşır,
bir girdi bir kişi; mekânda insan yok)*, **iki yasak** *(kalite zinciri, `or`)*.

**Ne yok:** JSON örneği, alan adları, hangi adın önce geldiği, action ve camera. Sonuncusu 176'nın,
ve bir test onun buraya sızmadığını bekliyor.

## Skill metinleri — yalnız ölen adın çıkması

İki cümle gitti. *Generate prompts+*: şema çağrısı yerine *"the shape is not yours to write; the
tools take what they need"*. *Start a scenario*: karakterler adımından şema cümlesi çıktı.

**Gerisi 178'de.** Metinler hâlâ `create_file`'ın iskeleti yazdığını, `add_frames`'i ve sahne listesi
dosyasını anlatıyor — Deneme 1 skill seçmeden koşuluyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **730 yeşil.** Kırmızıların 21'i de yeşile döndü.
3. Öteki üç takım rakamlarını korur. `dist` derlenmez.

## Koşarken çıkan üç kırmızı — üçü de skill testlerinde

**İkisi şemaya göre sıralanıyordu.** `test_the_flow_writes_the_plan_before_it_asks_anything` planın
şema çağrısından önce geldiğini ölçüyordu; artık bir sonraki adıma göre ölçüyor.
`test_the_structure_file_is_born_once`'ın şema yarısı şemayla birlikte gitti, doğum iddiası durdu.

**Üçüncüsü kelime tavanı:** yerine koyduğum cümle eskisinden **altı kelime uzundu** ve
*Generate prompts+* 306'ya çıktı, tavan 300. Cümle kısaltıldı — ve tavanın işi tam buydu: *"buradan
sonra bir cümle ancak bir cümle silinerek girer."* Bir madde metne dokunurken bunu ödemek zorunda.