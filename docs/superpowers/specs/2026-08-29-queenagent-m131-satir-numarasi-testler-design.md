# Madde 131 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 131
**Karşılaştırma:** [text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) ·
[Claude Code tools reference](https://code.claude.com/docs/en/tools-reference)
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

`read_file` ham metin döndürüyor, yani model dosyayı satır numarası olmadan görüyor. `edit_file`'ın
çapası *diskte tam bir kez geçmek* zorunda, ve model bir metnin kaç kez geçtiğini ancak gözüyle
tarayarak kestiriyor. Kareler birbirine benzediği için kestirim tutmuyor: `_edit` *"appears 3
times"* diyor, model çapayı büyütüp baştan deniyor, ve o baştan deneme bir raunt — yani büyüyen
bağlamın tamamı bir kez daha.

Claude Code'un `Read`'i `cat -n` biçiminde dönüyor ve aynı şartı taşıyan `Edit` ile birlikte
çalışıyor. Eksik olan şart değil, şartın etrafındaki kolaylık.

## Yol

Okuma numaralı döner, **ve 129'un kabı da aynı biçimde.** İkisi ayrılırsa aynı dosya modelin
önünde iki ayrı şekilde durur ve model hangisine bakacağını bilemez — kap zaten okumanın yerini
aldığı için asıl biçim onunki.

Biçim `cat -n`: numara altı karakterlik alana sağa yaslanır, ardından bir sekme, sonra satır.
Claude Code'un `Read`'inin verdiği biçim bu, ve kullanıcının sözü — *"kesinlikle claude gibi
olsun"*.

## Kurallar

- **Ne numaralanır:** diskteki dosyaların içeriği — `read_file`'ın sonucu ve kabın dosya blokları.
- **Ne numaralanmaz:** **şema.** Numara çapa seçmek için var, ve şemaya çapa yazılmıyor: o bir
  dosya değil, uygulamanın tek metni. `read_prompt_structure_schema`'nın sonucu da kaptaki şema
  bloğu da ham kalır.
- **Eşleşme değişmez.** `_edit` diskteki ham içerikte arar. Numaralı görünüm modele gösterilen
  şey, diskte duran şey değil.
- **Köprü araç tanımında:** `edit_file`'ın açıklaması çapayı yazarken numara önekinin atılacağını
  söyler. Claude Code'un Edit'i de bunu tanımında söylüyor — bağ kodda değil, modele söylenen
  cümlede.
- **Boş dosya boş döner.** Sıfır satır, sıfır numara: `1` yazan bir satır olmayan bir şeyi var
  gösterirdi.
- **Sayım değişmez.** `outcome` gerçek satırları sayar *(`counted`)*, numaralı metnin uzunluğunu
  değil.

## Bu turun testleri

**Hepsi kırmızı doğmuyor, ve bu bilerek.** Davranışın değiştiği yerler kırmızı; değişmemesi
gereken yerler bekçi olarak yeşil doğuyor — numaralamanın bozabileceği beş şeyi tutuyorlar, ve
uygulama turunda yeşil kalmak zorundalar. *(123'ün kalıbı: mevcut davranışı pin testleri tutar,
kırmızıyı yeni olan verir.)*

`test_tools.py` *(yeni)*:

- `test_a_read_hands_back_numbered_lines` — **kırmızı**
- `test_the_numbers_are_right_aligned_so_the_text_starts_in_one_column` — **kırmızı**
- `test_the_edit_tool_tells_the_model_to_drop_the_numbers` — **kırmızı**
- `test_an_empty_file_reads_as_nothing_rather_than_a_first_line` — bekçi
- `test_the_outcome_still_counts_the_lines_it_read` — bekçi
- `test_the_schema_is_handed_back_unnumbered` — bekçi
- `test_an_edit_matches_the_disk_and_not_the_numbered_view` — bekçi

`test_tools.py` *(değişen)*: `test_reading_gives_the_contents` artık numaralı hâli bekler —
**kırmızı**. Davranış değiştiği için testi de değişiyor, ve bu turun işi tam olarak bu.

`test_stream_answer.py` *(yeni)*:

- `test_the_box_numbers_the_lines_it_shows` — **kırmızı**
- `test_the_box_and_a_read_show_a_file_the_same_way` — bekçi *(bugün ikisi de ham olduğu için
  zaten aynı; testin işi değişimden sonra da aynı kalmalarını tutmak)*

## Ayakta kalması gerekenler

129'un kabı ve tazeliği, 127'nin adlar satırı, 93'ün sırası, 124'ün önbellek anahtarı,
`_edit`'in *"tam bir kez"* şartı ve üç cevabı *(bulunamadı · N kez geçiyor · düzenlendi)*. Ve
`test_the_schema_reaches_the_box_too` yeşil kalır — şema numaralanmadığı için.

## Bilerek yapılmayanlar

`offset` ile `limit` ve okumanın tavanı bu maddenin işi değil — ölçü yok, ve Kapsam dışı'na
yazıldı. `replace_all` 132'nin, `add_frames` 128'in. Disk şeması değişmiyor: numaralar
gösterilirken doğuyor, hiçbir yere yazılmıyor.

## Bilinen bedel

Numaralar kaba da girdiği için her raunda satır başına ~2 token biniyor, ve kap isteğin
kuyruğunda — yani önbelleklenmiyor. Beş dosyalık dolu bir kapta raunt başına birkaç yüz token.
Karşılığı kaçınılan her çakışma retinin bir tam raunt olması. **Bedeli biliniyor ve kabul edildi**
*(kullanıcı kararı, 29 Ağustos)*; hangisinin ağır bastığı 128'den sonraki denemede okunur.
