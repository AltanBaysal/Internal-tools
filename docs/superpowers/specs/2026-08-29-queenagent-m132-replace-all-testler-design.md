# Madde 132 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 132
**Karşılaştırma:** [Claude Code tools reference](https://code.claude.com/docs/en/tools-reference)
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

Çapa birden çok kez geçiyorsa `_edit` reddediyor, ve modelin tek çıkışı çapayı büyütüp baştan
denemek. O baştan deneme bir raunt — büyüyen bağlamın tamamı bir kez daha — ve büyüyen çapa
üstelik daha çok çıktı token'ı.

Claude Code'da ret tek çıkış değil. Dokümanın cümlesi: *"Claude either supplies a longer string
with enough surrounding context to pin down one occurrence, **or sets `replace_all: true` to
replace them all**."* İkinci yol bizde yok, ve asıl işe yaradığı yer belli: bir harita girdisinin
adı gibi dosyanın her yerinde tekrarlanan bir metni değiştirmek *(113'ün "bir harita girdisi
değişince onu anan bütün kareler değişir" işi)*.

131 çapa seçmeyi kolaylaştırdı; bu madde seçilecek tek çapa olmadığında çıkışı açıyor.

## Yol

`edit_file` isteğe bağlı bir `replace_all` bayrağı alır.

- **Bayraksız:** bugünkü davranış. Bir kez geçiyorsa değişir, birden çok geçiyorsa reddedilir.
- **Bayrakla:** kaç kez geçiyorsa hepsi değişir.

Varsayılan **ret**, ve bu bir karar: sessizce hepsini değiştirmek, tek bir yeri düzeltmek isteyen
modele fark ettirmeden fazlasını yaptırırdı, ve o dosya kullanıcının *(FOUNDATION 1)*. Bayrak bir
niyet beyanı — model çokluğu bilerek istediğini söylüyor.

## Kurallar

- **Bulunamadıysa bayrak kurtarmaz.** Sıfır eşleşme, bayraklı da bayraksız da *"not in"*.
- **Boş `old` yine reddedilir.** Bayrak bir eşleşmeyi çoğaltır, yokluğu bir eşleşmeye çevirmez.
- **Sayı görünür.** Birden çok yer değiştiyse cevap ve kart kaç yer olduğunu söyler — model
  durumu okumadan bilir, ve beklediğinden fazlası değiştiyse orada görür.
- **Tek geçişte bayrak fark ettirmez.** Aynı cevap, aynı kart: `Edited`.

## Bu turun testleri

**Hepsi kırmızı doğmuyor.** Bugün `replace_all` okunmayan bir argüman, dolayısıyla onu yollayan
tek-geçişli ve bulunamayan yollar zaten bugünkü gibi davranıyor — o testler bekçi, ve uygulama
turunda yeşil kalmak zorundalar.

`test_tools.py` *(yeni)*:

- `test_replace_all_changes_every_occurrence` — **kırmızı**
- `test_replace_all_says_how_many_places_it_changed` — **kırmızı**
- `test_the_edit_tool_takes_the_flag_as_a_parameter` — **kırmızı**
- `test_the_edit_tool_tells_the_model_the_flag_is_there` — **kırmızı**
- `test_without_the_flag_a_text_that_repeats_is_still_refused` — bekçi
- `test_the_flag_does_not_rescue_a_text_that_is_not_there` — bekçi
- `test_the_flag_on_a_single_occurrence_reads_like_an_ordinary_edit` — bekçi

## Ayakta kalması gerekenler

`_edit`'in üç cevabı ve *"tam bir kez"* şartının bayraksız hâli, 131'in numaralı okuması ve
numarasız eşleşmesi, 125'in koşullu okuma cümlesi, 129'un kabı.

## Bilerek yapılmayanlar

`add_frames` 128'in. `offset`/`limit` ve okuma tavanı Kapsam dışı'nda. Ön yüz değişmiyor: bayrak
modelin, kullanıcının değil.
