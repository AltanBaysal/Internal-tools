# Madde 128 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 128
**Araştırma:** [2026-08-29-queenagent-arac-tasarimi-arastirma.md](../research/2026-08-29-queenagent-arac-tasarimi-arastirma.md)
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

Kare eklemek bugün `edit_file`'la yapılıyor *(prompt+ metni: "Add frames with edit_file in batches
of five")*, ve bir JSON dizisine eklemek aslında **ekleme değil araya sokma**: liste `]` ile
kapanıyor, yeni kare onun öncesine giriyor. Modelin tek yolu önceki karenin kuyruğunu çapa yapıp
virgülüyle beraber **geri yazmak** — yani diskte zaten duran metin `old`'da bir, `new`'da bir daha,
en pahalı token sınıfında. Beşerli ritimde senaryo başına beş çapa.

İkinci bedel çakışma: kareler birbirine benziyor, çapa iki karede birden geçebiliyor ve düzenleme
reddediliyor. 131 çapa seçmeyi kolaylaştırdı, 132 çakışmaya çıkış açtı — ama ikisi de çapanın
kendisini ortadan kaldırmıyor.

**Okuma bu maddenin derdi değil artık:** onu 129 çözdü. Kalan bu iki bedel, ve ikisi de ölçülmedi
*(kullanıcı kararıyla yine de koşuluyor — yol haritasında yazılı)*.

## Yol

`add_frames(name, frames)`. Kod yapı dosyasını okur, verilen kareleri `frames` listesinin sonuna
ekler, yazar. Çapa yok, *"tam bir kez"* şartı yok, konum yok — **modelin verdiği bir konum
olmadığı için yanlış veremiyor.**

`NotebookEdit`'in kalıbı: Anthropic da yapılandırılmış bir dosyaya satır numarasıyla değil **yapı
birimiyle** insert veriyor *(`cell_id`)*. Ve deponun kendi kalıbı — `build_prompts` ile
`build_character_prompts` aynı yolu yürüyor *(FOUNDATION 5: kararı kod verir)*.

## Kurallar

- **Doğrulama yok.** Araç ne verilirse ekler; şema doğrulaması `build_prompts`'un işi ve orada
  `BadStructure` ile duruyor. `_build`'ın ayrımı aynen: *"The structure is the model's; the prompts
  are the code's."*
- **Cevap iki sayı taşır:** kaç kare eklendi, dosya artık kaç kare tutuyor. Ekleme idempotent
  değil — aynı çağrı iki kez koşarsa kareler iki kez girer — ve ikinci sayı bunu modelin gözü
  önünde tutuyor.
- **Üç ret:** dosya yok · geçerli JSON değil · `frames` bir liste değil *(dosyada ya da
  argümanda)*. Üçü de `_build`'ın cümleleriyle aynı biçimde, ve sebep uydurulmadan — JSON hatası
  parser'ın kendi cümlesini taşıyor.
- **Boş liste bir iş değil:** sıfır kare eklemek dosyayı yazmaz, ve cevabı bunu söyler.
- **Yazım biçimi sabitlenir:** `indent=2`, `ensure_ascii=False`. İkincisi bir karar — Türkçe
  karakter taşıyan bir tarif `ı` yığınına dönerse kullanıcı kendi dosyasını okuyamaz, ve o
  dosya kullanıcının *(1. ilke)*.
- **Dosya doğmuyor.** `add_frames` var olanı değiştiriyor, yani `WRITES_FILES`'a girmiyor ve kart
  çıkmıyor — `edit_file`'ın kuralı.

## Bu turun testleri

`test_tools.py` *(yeni)*:

- `test_add_frames_appends_to_the_end_of_the_list` — **kırmızı**
- `test_add_frames_says_how_many_it_added_and_how_many_there_are_now` — **kırmızı**
- `test_add_frames_leaves_the_maps_alone` — **kırmızı**
- `test_add_frames_writes_readable_turkish_rather_than_escapes` — **kırmızı**
- `test_add_frames_refuses_a_file_that_is_not_there` — **kırmızı**
- `test_add_frames_carries_the_parsers_own_sentence_when_the_json_is_broken` — **kırmızı**
- `test_add_frames_refuses_a_structure_with_no_frames_list` — **kırmızı**
- `test_adding_nothing_writes_nothing` — **kırmızı**
- `test_add_frames_brings_no_file_into_being` — **kırmızı**
- `test_the_tool_list_carries_add_frames` — **kırmızı** *(mevcut sayım testi de değişiyor)*
- `test_calling_add_frames_twice_puts_the_frames_in_twice` — **kırmızı**, ve bilerek: tuzağı
  belgeleyen test, aracın cevabındaki ikinci sayı bunun için var

`test_skills.py`:

- `test_prompt_plus_adds_frames_with_the_tool_rather_than_an_edit` — **kırmızı**

## Ayakta kalması gerekenler

`edit_file` duruyor — var olan bir kareyi düzeltmek ve harita girdisi değiştirmek hâlâ onun işi
*(113'ün düzenleme yolu, ve 132'nin `replace_all`'ı tam da o harita işi için)*. `build_prompts`,
şema, 131'in numaralı okuması, 129'un kabı, prompt+'ın beşerli ritmi *(metinde kalıyor: uzun
cevabın sonunda kalite düşüyor, o yüzden model yine parça parça çağırıyor — ama artık aralarında
okumuyor)*.

## Bilerek yapılmayanlar

Kare silme ve araya sokma — istenmedi, ve FOUNDATION 3 gerçek bir istek olmadan özellik
yasaklıyor. Şema doğrulaması `build_prompts`'ta kalıyor. Ön yüz değişmiyor.
