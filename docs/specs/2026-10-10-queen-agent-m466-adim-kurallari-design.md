# Madde 466 · Adım kuralları tek sözlükle — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
466 · **Dal:** `feat/queenagent-v10`, ana klasörde, worktree yok · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Plan:** [m466 planı](../plans/2026-10-10-queen-agent-m466-adim-kurallari-plan.md)

## Ne, neden

Kullanıcı system prompt'ta neyin kötü olduğunu sordu; Claude'un listesi
[tmp/system-prompt-v10-review.md](../../tmp/system-prompt-v10-review.md)'de. Kullanıcı 1, 2, 6 ve 13'ü
seçti *(kullanıcı, 10 Ekim — "tamam düzelt bekliyorum")*. Dördü de 465'in sorununa dokunuyor: model
planın adımlarını atlıyor.

1. **Tek sözlük (6).** How you work aynı döngüye *Understand / Act / Check* diyordu, 465'in Planning
   satırı *gather context, take action, verify results*. Zayıf bir model bunları iki ayrı kural
   sanabilir. Adımlar 465'in sözleriyle adlanır:
   - `1. Gather context: read the files the answer needs, and only those.`
   - `3. Take action: do the work with your tools.`
   - `4. Verify results: read each tool's answer before you go on.`

   2. (Plan) ve 5. (Answer) adımlar ile listenin altındaki satır aynı kalır.
2. **Biten adım plan dosyasında işaretlenir (1).** Yeni sohbet planı kalınan adımdan alır, ama hangi
   adımda kalındığını yalnız dosya söyleyebilir; hiçbir kural adımı işaretlemeyi söylemiyordu. Planning'e,
   *"Work that may not finish in this turn starts with a plan file"* satırının hemen altına:
   - `- When a step of a plan file is done, mark it done in the file with edit_file before you start the next step.`
3. **Soru turu bitirir (2).** Model soruyu cevabın ortasına koyup devam edebilir, ya da sorup yarım
   işi bırakabilir. Asking'in sonuna:
   - `- A question ends your turn: do what you can first, then ask it last.`
4. **En sık bozulan kural sonda da söylenir (13).** Zayıf model metnin başını ve sonunu en iyi
   hatırlar. Remember'a dördüncü satır:
   - `- Finish a plan's step before you start the next.`
5. **Start a scenario aynı şeyi söyler.** Akışın 1. adımı nerede kalındığını dosyalardan okuyordu;
   2. değişiklikten sonra taban adımları işaretletiyor, ve iki metin iki ayrı şey söylerdi. 1. adımın
   cümlesi:
   - Önce: `The files of the project show how far the work got.`
   - Sonra: `The plan's marked steps show how far the work got, and the files of the project confirm it.`

   Aynı adımda, boş kutunun biçiminin yanına bitmiş adımın biçimi girer:
   `A done step reads - [x] 1. write the plan.` Madde 198, yalnız boş kutu yazılıyken modelin kendi
   işaretini uydurduğunu ve sonraki turun onu tanımadığını bulmuştu; ilerleme artık işaretlerden
   okunduğu için işaretin biçimi de yazılı.

   Başka skill metni ilerlemeyi dosyalardan okumuyor ya da adımın işaretlenmediğini söylemiyor:
   Edit prompts ve Improve plan yazmıyor.

Python dizgileri dosyanın üslubuyla satırlara bölünür; modele giden metinde her kural tek satırdır
(Madde 455).

## Düzeltme 11'i ve Madde 203'ü geri almak

2. ve 5. değişiklik, Eylül'de çekilen bir kuralı açıkça geri getiriyor.

- **Düzeltme 11** *(9 Eylül, [metin düzeltmeleri](../2026-09-09-queenagent-metin-duzeltmeleri.md))*
  nerede kalındığını kutulardan dosyalara taşımıştı. Gerekçe: işaretlemek modelin atlayabileceği bir
  işti, ve atlandığında "ilk boş kutu" hep 1. adımı gösterip akışı baştan başlatıyordu.
- **Madde 203** *(10 Eylül,
  [spec](2026-09-10-queenagent-m203-adim-araci-testler-design.md))* bunun üstüne kutuyu dolduran
  aracı kaldırdı, ve akışın kapanış maddesi *"tümüyle düşer"* dedi: hiçbir tur kutuyu doldurmuyordu.
- **Şimdi** *(kullanıcı, 10 Ekim — "işaretlesin model sıkıntı yok, şu an model daha güçlü")*: model
  adımı `edit_file`'la işaretler, ilerleme işaretlerden okunur. Gerekçe, kullanıcının sözüyle, modelin
  artık daha güçlü olması.
- **Düzeltme 11'in korumasından kalan:** dosyalar doğrulama olarak duruyor. Bir işaret atlanırsa
  proje dosyaları işin gerçekte nereye vardığını yine gösteriyor.
- `mark_step_done` geri gelmiyor. İşaretleme kuralı tabanda duruyor, her skill'le birlikte gidiyor;
  akış hiçbir araç adı vermiyor, böylece iki metin farklı şey söyleyemiyor.

## Sınırlar

- `prompt.py`'de yalnız `SYSTEM_PROMPT` ve `START_A_SCENARIO`'nun 1. adımındaki tek cümle değişir.
  Modele giden başka hiçbir metin, frontend ve queen-editor değişmez.
- `SYSTEM_PROMPT`'un üstündeki yorum aynı kalır: "the core rules again at the very end" diyor ve
  kural sayısı vermiyor, yani hâlâ doğru.
- Yeni satırlarda görev kelimesi yok, büyük harfle vurgu yok, metin yine Remember'la bitiyor
  (`test_the_base_names_no_task`, `test_nothing_is_shouted`, `test_the_text_ends_on_its_last_word`).
  Akış 1823 kelime, sınırı 1830.
- Testler cümleyi değil, metinlerin ne üzerinde anlaştığını tutar:
  - How you work'ün numaralı adımları ve Planning'in döngü satırı aynı üç evreyi adlandırır. Evreler
    testte bir kez yazılı (`LOOP`) ve kullanıcının üç sözünü sözü sözüne tutar: *gather context*,
    *take action*, *verify results*. Biri yalnız bir yerde yeniden adlanırsa test kırılır. Numaralı
    bir satırda `. ` yoksa adım adı boş çıkar ve test bir assertion'la kırılır, hatayla değil.
  - Planning'in bir satırı biten adımı plan dosyasında `edit_file`'la işaretlemeyi söyler.
  - Asking'in bir satırı sorunun turu bitirdiğini ve en son geldiğini söyler.
  - Remember sonda okumayı, tool'un yapmadığını iddia etmemeyi, sohbette cevap vermeyi ve adımı
    bitirmeden sonrakine geçmemeyi tekrarlar.
  - Akışın 1. adımının bir satırı ilerlemeyi işaretli adımlardan okur ve proje dosyalarını anar
    (`test_where_the_work_stopped_is_read_off_the_plans_marks`, eski
    `test_where_the_work_stopped_is_read_off_the_files`'ın yerine).
  - Akış ne `mark_step_done`'ı ne `edit_file`'ı anar; tabanın bir satırı plan dosyasının adımını
    `edit_file`'la işaretler (`test_a_step_is_marked_with_edit_file_by_the_base`, eski
    `test_no_step_is_ticked_off_the_plan_at_all`'ın yerine; 126'nın ve 198'in dersi yorumunda kalır).
- `test_the_three_core_rules_close_the_text` Remember'da tam üç satır olmasını ve satırların sırasını
  bekliyordu. Adı `test_the_core_rules_close_the_text` oldu, sayıyı ve sırayı değil kuralları
  soruyor; beşinci bir kural onu kırmaz.
- Testlere bir bölümü başlığıyla bulan `_section` yardımcısı girdi. 465'in testi bölümü kendi içinde
  arıyordu; aynı işi yaptığı için o da bu yardımcıyı kullanıyor, sorduğu şey değişmedi.
- `test_skills.py`'de iki yorum, çekilen kurala yaslandığı için düzeldi:
  `test_a_delegation_answers_only_the_question_that_was_asked` ve
  `test_every_review_is_written_to_a_file_of_its_own`.

## Maliyet

Disk ve ağ yok: metinler modülde sabit.

**Token.** `SYSTEM_PROMPT` 4485 karakterden 4736'ya, 896 kelimeden 948'e çıkıyor: 251 karakter, 52
kelime. Üç yeni satır 230 karakter, adım adları 21. Akışın 1. adımı 15 kelime uzuyor. Her isteğe kabaca
55–65 token, Start a scenario seçiliyken birkaç token daha ekler (gerçek tokenizer'la sayılmadı).

**Önbellek.** `SYSTEM_PROMPT` her sohbetin önbelleğe alınan önekinin başında durur. Bu yüzden yeni
metinle devam eden her sohbet bir kez ıskalar ve bütün önekini baştan önbelleğe yazar. Sonraki
isteklerde önek yine önbellekten okunur.

**Tur.** İşaretlemenin bedeli, plan dosyası olan işlerde her adım için:

- **Bir okuma.** `create_file` dosyayı açık dosyalara koymuyor, yalnız `read_file` koyuyor; `edit_file`
  ise diskteki metni harfi harfine istiyor. Yani işaret çoğu kez planın önce okunmasını, o da açık
  dosyaların beş yerinden birini istiyor. Plan açık kaldıkça sonraki işaretler yeniden okumaz, ama
  beş yer dolunca plan düşer ve yeniden okunur.
- **Bir `edit_file` çağrısı.** İşaret ancak adımın sonuçları doğrulandıktan sonra dürüst. Bu yüzden
  adımın son çağrısıyla aynı round'a giremez; sonraki adımın ilk çağrılarıyla ya da kendi round'unda
  gider. Bir turun round'u sınırlı.
- **Start a scenario her çalışmada öder.** Akış her çalışmada bir plan dosyası yazıyor, yani on adımın
  her biri bir işaret: kabaca on okuma ve on yazma.
- **Ask ve Plan modunda bir izin kartı.** Bu iki modda `edit_file` izin istiyor, yani her işaret
  kullanıcının önüne bir kart çıkarıyor.

Bu bedel, yeni sohbetin doğru adımdan devam etmesi için ödeniyor; kullanıcı bunu kabul etti.

## Ne zaman biter

- Modele giden system prompt'ta bu dört değişiklik ve akışın 1. adımındaki cümle sözü sözüne var;
  başka metin değişmedi.
- Yeni testler önce kırmızı, sonra yeşil; dört suite yeşil.
