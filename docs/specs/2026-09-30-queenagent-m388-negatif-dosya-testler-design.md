# Madde 388 — Edit prompts olmayan negatif dosyayı söylemez — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 388 (Dalga 8). *Dayandığı
maddeler: 373 · v9-8e, 374 · v9-8f, 390.* Kullanıcı, 30 Eylül: *"bunlarıda düzelt"*. Satır: Edit
prompts'un kapanışı negatif dosyayı yalnız o dosya varken anıyor.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Aşağıdaki kararlar subagent'ın;
kullanıcı metinleri en sonda okur.

## Bugün ne var

- `THE_CHECKS`'in kapanışı, üç skill'in de sonunda: *"When the checks are done, close by naming the
  prompt file and the negative file, and saying they are ready."*
- Negatif dosyayı Check 4 yazar (`write_negative`, 373'ten beri). Start a scenario ve Improve Check 4'ü
  her zaman koşar, yani kapanışa gelindiğinde dosya hep var.
- Edit prompts'un `Step 4 -- the checks` adımı Check 4'ü yalnız senaryonun kadrosu değiştiyse koşturur:
  *"Check 4 runs only if your change touched the scenario's cast: ... Otherwise skip it."* 373'ten önce
  yazılmış bir senaryoda kadro değişmezse dosya hiç yazılmaz, ve kapanış olmayan bir dosyayı adıyla
  anar.
- Model projenin dosyalarının adlarını her turda görüyor (`FILES_HELD`), yani dosyanın var olup
  olmadığını bir araç çağırmadan bilir.

## Yaklaşımlar

1. **Paylaşılan kapanışa birkaç kelime** — *"and the negative file, if there is one"*. Üç skill'de de
   doğru okunur, ama Start a scenario ve Improve'da hiç doğmayan bir durumu anlatır: iki metne ölü
   kelime. Start a scenario 1025/1025'te; tavanı yalnız bu yüzden yükselir.
2. **Yalnız Edit prompts'un taşıdığı bir cümle, Check 4'ün koşulunun yanında** — *seçilen.* 374'ün
   kurduğu biçim bu: Check 4'ün koşulu editörün kendi adımında yazılı, çünkü akış ve Improve listeyi
   her zaman yazar, ve blok tek kalır (`THE_CHECKS`'in docstring'i; `test_after_an_edit_the_negative_is_written_again_only_if_the_cast_changed`
   `"runs only if" not in _checks()` diye tutuyor). Dosyanın yokluğu yalnız Check 4 atlanınca doğar,
   o yüzden cümle `Otherwise skip it.`'in hemen arkasında, aynı maddede durur. Akışın ve Improve'un
   metni değişmez.
3. **Kapanışı Check 4'ün içine almak ya da kapanışa kendi başlığını vermek** — 390'ın açık noktası 1.
   Maddenin ihtiyacından büyük bir yeniden yapı; yapılmaz.

## Ne değişiyor

1. **Edit prompts'un Step 4'ündeki Check 4 maddesi bir cümle alır**, `Otherwise skip it.`'in
   arkasına: *"If the scenario has no negative file, close by naming the prompt file alone."* Kipi
   kapanışın kendisiyle aynı (`close by naming`), biçimi 390'ın kurallarına uyar: madde içinde tam
   cümle, kısaltma yok, araç adı yok.
2. **Paylaşılan kapanış olduğu gibi kalır**: iki dosyayı da anar. 390'ın açık noktası 1'e (kapanışın
   madde olmayan bir paragraf oluşu) dokunulmaz.
3. **Tavan.** Edit prompts bugün 856 kelime (385'in tasarımındaki sayım, 390 kelime sayısını
   değiştirmedi); cümle 14 kelime ekler, 870 olur. Tavan 856'dan 870'e çıkar, gerekçesi 367, 370, 373,
   374 ve 385'in yazdığı yorumda. Akış 1025'te, Improve 700'ün altında, değişmeden kalır.

## Testler

`queen-agent/backend/tests/test_skills.py`, 374'ün bölümündeki Check 4 testinin arkasında (bölüm
Edit prompts'un Step 4'ünü soruyor):

- `test_after_an_edit_the_closing_names_the_negative_file_only_if_there_is_one` — Edit prompts'un
  kendi Step 4 parçasında (`_edits_checks_step()`) `no negative file` ve `the prompt file alone` var, ve
  cümle `Otherwise skip it`'ten sonra geliyor; varlığından sonra sorulan yokluk: `no negative file`
  paylaşılan `THE_CHECKS`'te yok, yani koşul editörün kendisinin — **kırmızı**.

Değişen mevcut test:

- `test_the_texts_stay_short_enough_to_be_read` — Edit prompts'un tavanı 870, gerekçesiyle — yeşil
  kalır.

`test_the_closing_names_the_negative_file_too` olduğu gibi kalır: paylaşılan kapanış iki dosyayı da
anmaya devam eder.
