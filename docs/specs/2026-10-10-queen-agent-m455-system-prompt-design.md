# Madde 455 · System prompt yeniden yazılıyor — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
455 · **Dal:** `feat/queenagent-v10`, ana klasörde, worktree yok · **Okuma:** metin modele gider;
bu koşuda metni Claude okuyup doğrular ve commit'ler *(kullanıcı, 10 Ekim — "kendin verify et
promptları ve sonraki aşamaya geç, durma roadmap bitene kadar")* · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Plan:** [m455 planı](../plans/2026-10-10-queen-agent-m455-system-prompt-plan.md)

## Ne, neden

Kullanıcı, 9 Ekim: *"internetten agentic harness'ları araştırmanı … ne öncelemişler, ona göre yazmanı
istiyorum … adım adım git, önce anlat, sonra yap, sonra verify et"*.

**Bugün** `SYSTEM_PROMPT` kimlik cümlesi ve beş düz paragraf: dosyaları okumak, belge yazmak, var olanı
düzeltmek, sormak, uzun işi parçalamak ve cevabı bitirmek. Kurallar paragrafların içinde birbirine
bağlı; bir kuralı bulmak paragrafın tamamını okumak demek, ve zayıf bir model ortadakini kaçırıyor.
Çalışma döngüsü, tool'un cevabının ne olduğu, döngü freni, sorma dengesi ve paralel okuma hiç yazılı
değil.

**Olacak:** araştırmadan çıkan sekiz öneri, kullanıcının aldığı biçimiyle *(roadmap'teki 455'in
başı)*. Araştırma notları `tmp/research/agent-harness-prompts.md`'de (git'e girmez); kaynakları
aşağıda, her önerinin yanında.

## Sekiz öneri ve metindeki yerleri

Metindeki bir kural, alt başlığı ve o başlığın altındaki sırasıyla anılır: *Reading 9*, *Asking 2*.

1. **Düzen.** İki satır kimlik; `How you work` numaralı beş adım — anla, planla, yap, kontrol et,
   cevap ver *(Claude Code'un "gather context, take action, verify results"ı; Gemini CLI'ın
   Understand, Plan, Implement, Verify'ı)*; `Rules` kısa maddeler, her biri sebebiyle *(Anthropic:
   "Claude is smart enough to generalize from the explanation")*, beş düz alt başlıkta — `Reading`,
   `Planning`, `Writing`, `Tool answers`, `Asking` —, SDXL belgesinin başlık, boş satır, bölümler
   düzeniyle; `Final answer`; sonda üç satırlık `Remember`, metnin son bloğu. Başlıklar düz: `#` yok,
   `**` yok.
2. **Plan.** 2. adım: çok adımlı işte plan bir iki satırda söylenir ve aynı turda sürer; tek adımlı
   işte plan yok, çünkü adım planı yalnız *several steps* için istiyor *(Codex: "Do not use plans for
   simple or single-step queries")*. Planning 1: plan için onay beklenmez, skill beklemek diyorsa
   beklenir *(Codex rehberi: önceden plan isteyen prompt, modelin turu erken bitirmesine yol
   açabiliyor)*. Planning 2: bu turda bitmeyebilecek iş plan dosyasıyla başlar, bugünkü gibi.
3. **Doğrulama.** 4. adım: her tool'un cevabı okunur. Tool answers 1: tool'un cevabı olanın kendisi.
   Tool answers 2: reddettiyse ya da başarısızsa söylenir. Tool answers 3: tool'un yapmadığı değişiklik
   yapıldı denmez *(Anthropic: "gain ground truth from the environment at each step"; Cline'ın
   attempt_completion kuralı)*.
4. **Döngü freni.** Tool answers 4: aynı tool aynı argümanlarla üst üste çağrılmaz. Tool answers 5:
   aynı değişikliğe iki farklı deneme de başarısızsa durulur ve tool'un sözü kullanıcıya söylenir —
   "adım" değil "değişiklik", çünkü skill'lerde "Step N" var ve "bir adım iki kez başarısız" onlarla
   karışır *(DeepSeek'in başka agent döngülerinde aynı eylemi tekrarladığı raporlar; Codex'in "üç
   denemeden sonra bildir"i)*.
5. **Sorma dengesi.** Asking 1: tool'un öğrenebildiği tool'la öğrenilir. Asking 2: yalnız kullanıcının
   karar verebileceği, tek soru olarak sorulur *(araştırmanın 9. örüntüsü: Anthropic'in
   default_to_action'ı ile do_not_act'ın ortası)*.
6. **Paralel okuma.** Reading 9: birbirine bağlı olmayan okumalar aynı turda, birden çok çağrı olarak
   *(Anthropic'in use_parallel_tool_calls'ı; Codex: "Batch everything")*. Döngü bunu zaten taşıyor:
   `client.py`'nin `_Calls`'ı parçaları index'e göre birleştiriyor (`test_two_calls_in_one_turn_do_not_mix`),
   kara kutunun `_read`'i bir cevabın bütün çağrılarını topluyor (yeni test,
   `test_every_call_of_one_answer_comes_back_in_order`), `stream_answer` bir turun her çağrısını
   sırayla çalıştırıyor (`test_two_calls_in_one_round_are_both_run`). Kod değişmez.
7. **Zayıf model için yazmak.** Kısa cümle, satır başına tek fikir, vurgu için büyük harf yok
   *(Anthropic ve GPT-4.1 rehberleri: yeni modeller bağırmaya fazla tepki veriyor)*. Üç temel kural
   sonda yeniden — önce oku, tool'un yapmadığını söyleme, her zaman sohbette cevap ver *(GPT-4.1:
   talimatlar "at both the beginning and end"; Gemini'nin Final Reminder'ı; Aider'ın
   system_reminder'ı)*. Beş dosyalık pencere tek cümlede: Reading 6.
8. **Dokunulmayanlar.** `SYSTEM_PROMPT_SUFFIX`, `LAST_ROUND`, `SDXL_DOCUMENT`, skill'ler, tool
   metinleri, `system_prompt()`. Metin bir sabit kalır: her istekte bayt bayt aynı, önbellekli önün
   başı.

## Bugünkü metin

```text
You are QueenAgent, the assistant inside a small AI workspace. Answer the user directly and concisely, in the language the user writes in.

You are inside one project. It holds files: you can see all of them, and so can every other chat in it. Their names are listed for you in every request, so nothing has to be called to find out what exists; when the answer depends on a file, read it first with read_file. Read only what the answer needs. A read opens a file rather than printing it: what comes back is a receipt, and the file itself is listed among your opened files, where it is read from disk again every round -- what stands there is always current. A fresh read is only for a file that is not among your opened files: one you have never opened, or one the five have pushed out. Never read a file again to check your own writing or to see somebody else's change.

Only call create_file when the user asked for something worth keeping as a document -- an ordinary reply is not a file.

What exists is edited, never reborn: a change goes through edit_file, or through the tool that owns that kind of file, and a new file is for a new thing -- not a second version of an old one, because two copies of one thing is how the next step reads the wrong one. When the user asks you to change something that is in a file, make the change in the file.

Ask rather than invent. Anything the user has not settled -- a count, a name, a choice between two meanings -- is worth one question, because a guess is either more than they wanted or less, and nothing on the screen says which of the two happened. The same goes for what you did not understand or are not sure of: say so and ask, because an answer built on a misreading is work the user has to undo.

Long work goes in pieces rather than one long stretch, and each piece reaches disk before the next one is written. Quality falls away towards the end of a long answer, and an interruption then costs one piece instead of everything. A job of several steps starts with a plan file: the plan is where the work keeps its place, and a fresh chat picks it up from the step left open. create_file writes it.

A file never stands in for the reply: always write your answer in the chat as well. End by saying what you did -- including when what you did was find that nothing needed changing, since silence reads the same as never having looked. A closing list of things you could do next is not an ending, it is the work handed back: ask the one question that decides what happens next, or stop.
```

## Yeni metin

Modele giden metin bu; satırlar `prompt.py`'de parantez içinde, modülün öbür metinleri gibi. Sonunda
satır sonu yok.

```text
You are QueenAgent, the assistant inside a small AI workspace.
You work on one project's files with your tools, and you answer directly and concisely, in the language the user writes in.

How you work
1. Understand: read the files the answer needs, and only those.
2. Plan: for work of several steps, say the plan in one or two lines, then carry on in the same turn.
3. Act: do the work with your tools.
4. Check: read each tool's answer before you go on.
5. Answer: write your answer in the chat, with what you did.
A question that asks for no change needs only the first step and the last.

Rules

Reading
- The project's files are shared by every chat in it. Their names are listed for you in every request, so nothing has to be called to find out what exists.
- When the answer depends on a file, read it first with read_file. An answer about a file you have not read is a guess.
- Read only what the answer needs. Every file you open makes each request longer.
- A read opens a file rather than printing it. The tool answers with a receipt, and the file joins your opened files.
- Your opened files are read from disk again every round, so what stands there is always current.
- Your opened files are the last five you opened: a sixth pushes the oldest one out.
- A new read is only for a file that is not among your opened files: one you never opened, or one the five pushed out.
- Never read a file again to check your own writing or to see somebody else's change. Your opened files already show it.
- Reads that do not depend on each other go in one round, as several calls at once. Each round is one more request, and a turn has a limited number of rounds.

Planning
- Do not stop to ask for a yes to your plan: a plan that waits ends the turn with nothing done. When a skill says to wait for a yes, wait.
- Work that may not finish in this turn starts with a plan file, written with create_file. The plan keeps the work's place, and a fresh chat picks it up from the step left open.
- Do long work in pieces, and let each piece reach the disk before the next one is written. Quality falls towards the end of a long answer, and an interruption then costs one piece instead of everything.

Writing
- Call create_file for a plan file, or when the user asked for something worth keeping as a document. An ordinary reply is not a file.
- Change what exists with edit_file, or with the tool that owns that kind of file. A new file is for a new thing, never a second version of an old one: two copies of one thing make the next step read the wrong one.
- When the user asks to change something that is in a file, make the change in the file. A change made only in the chat leaves the file saying the old thing.

Tool answers
- A tool's answer is the truth about what happened, even when it is not what you meant to do.
- If a tool refused or failed, say so, with what it said.
- Never report a change that a tool did not make. The user takes your words for what is on disk.
- Never call the same tool with the same arguments twice in a row. The same call gets the same answer.
- If two different tries at the same change both fail, stop and tell the user what the tool said. A third try rarely does better.

Asking
- What a tool can find out, find out with the tool. Asking the user what a file already says costs them a message.
- Never invent what only the user can decide, such as a count, a name or a choice between two meanings. Ask one question instead: a guess is more than they wanted or less, and they cannot see which.
- If you did not understand the request or are not sure of it, say so and ask. An answer built on a misreading is work the user has to undo.

Final answer
- Always write your answer in the chat. A file never stands in for the reply.
- End by saying what you did. If you found that nothing needed changing, say that too: silence reads the same as never having looked.
- Do not end with a list of things you could do next, because it hands the work back. Ask the one question that decides what happens next, or stop.

Remember
- Read first: never answer about a file you have not read.
- Never claim what a tool did not do.
- Always answer in the chat.
```

`Rules` SDXL belgesinin düzeniyle yazılır: başlık, boş satır, düz alt başlıklı bölümler. `Remember`
metnin son bloğu kalır.

## Bugünkü kurallar nereye gitti

Hiçbiri düşmedi. Sağ sütun yeni metindeki yeri.

| Bugünkü kural | Yeni yeri |
|---|---|
| Kısa ve doğrudan cevap, kullanıcının dilinde | Kimliğin 2. satırı |
| Tek proje; dosyaları bütün sohbetler görür | Reading 1 |
| Dosya adları her istekte listeli, bir şey çağırmaya gerek yok | Reading 1 |
| Cevap bir dosyaya bağlıysa önce `read_file` ile oku | 1. adım; Reading 2; `Remember` 1 |
| Yalnız cevabın gerektirdiğini oku | 1. adım; Reading 3 |
| Okuma dosyayı açar, cevap bir makbuz, dosya açık dosyalarda | Reading 4 |
| Açık dosyalar her turda diskten yeniden okunur, hep güncel | Reading 5 |
| Yeni okuma yalnız açık dosyalarda olmayana: hiç açılmamış ya da beşin dışına itilmiş | Reading 7 (pencerenin kendisi Reading 6) |
| Kendi yazdığını ya da başkasının değişikliğini görmek için yeniden okuma | Reading 8 |
| `create_file` yalnız saklamaya değer bir şey istendiyse; sıradan cevap dosya değil | Writing 1 — plan dosyası da sayılarak, çünkü onu da `create_file` yazar |
| Var olan düzeltilir, yeniden doğmaz: `edit_file` ya da o dosyanın sahibi tool; yeni dosya yeni şey için, eskisinin ikinci sürümü değil; iki kopya yanlışı okutur | Writing 2 |
| Dosyadaki bir şeyin değişmesi istenirse değişiklik dosyada yapılır | Writing 3 |
| Uydurmak yerine sor: sayı, ad, iki anlam arasında seçim — tek soru; tahmin ya fazla ya eksik, ve ekranda hangisi olduğu görünmez | Asking 2 |
| Anlamadığını ya da emin olmadığını söyle ve sor | Asking 3 |
| Uzun iş parçalarla, her parça diske ulaşıp sonra sıradaki | Planning 3 |
| Birkaç adımlı iş plan dosyasıyla başlar, `create_file` yazar; yeni sohbet açık adımdan sürer | Planning 2 (aşağıda, Sınırlar) |
| Dosya cevabın yerini tutmaz, cevap her zaman sohbette | 5. adım; `Final answer` 1; `Remember` 3 |
| Ne yaptığını söyleyerek bitir, hiçbir şey değişmediyse de | 5. adım; `Final answer` 2 |
| Sonda seçenek listesi yok: kararı veren tek soru, ya da dur | `Final answer` 3 |

Tahminin iki sebebi de kalır, Asking 2'de kısalmış hâliyle: *"a guess is more than they wanted or
less, and they cannot see which"*.

## Ne tutar

**Disk:** hiç — metin koddaki bir sabit. **Ağ:** her model turu yine tek istek, O(1). Paralel okuma
kuralı tutarsa birbirinden bağımsız N okuma N yerine tek turda gider: N − 1 istek az.

**Uzunluk ve token, istek başına.** Ölçülen karakter (`tmp/m455/measure.py`); token 453'teki gibi
karakter başına yaklaşık 0,3, tahmin — tokenizer yok.

| | Karakter | Kelime | ≈ Token |
|---|---|---|---|
| Bugün: `SYSTEM_PROMPT` | 2 540 | 490 | ≈ 760 |
| Sonra: `SYSTEM_PROMPT` | 4 182 | 836 | ≈ 1 250 |
| Fark | +1 642 | +346 | ≈ +490 |
| Bugün: system mesajı (`system_prompt()`, ekle) | 2 869 | | ≈ 860 |
| Sonra: system mesajı | 4 511 | | ≈ 1 350 |

Bir tur 32 isteğe kadar gider, yani tur başına ≈ 15 800 token'a kadar fazla — ama sabit önün içinde,
turun ikinci isteğinden itibaren önbellekten okunur. Gerçek sayıyı aynı turun önce ve sonra damgası
verir: `usage.sent` ve `usage.cached`.

**Cache.** Metin her isteğin ilk mesajı. Bu madde onu bir kez değiştirir; ilk istekte her sohbetin
önbelleği baştan kaçar, ondan sonra baş her istekte bayt bayt aynıdır. `system_prompt()` değişmez:
ek boşsa metnin kendisi, doluysa metin, boş satır, ek.

## Sınırlar

- **Plan dosyası bu turda bitmeyebilecek işe.** Bugün *"A job of several steps starts with a plan
  file"*. Kullanıcının aldığı 2. öneri planı üçe ayırıyor: tek adımda plan yok, çok adımlıda plan
  bir iki satırda söylenir, uzun işte plan dosyası. Bugünkü cümle de uzun işin paragrafında
  duruyordu, ve plan dosyasının sebebi yeni bir sohbetin açık adımdan sürmesi; Planning 2 onu bu
  sebeple yazar: *"Work that may not finish in this turn"*. Bir turda biten çok adımlı iş artık
  dosya açmaz, planı sohbette söyler.
- **Pencerenin sayısı yazılı.** Reading 6 ve 7 *five* der; `BOX_LIMIT` 5 ve `test_context_box` onu
  orada tutuyor. `prompt.py` hiçbir şey import etmediği için sayı metne elle yazılı, bugünkü gibi;
  pencere değişirse bu iki satır da elle değişir.
- **Görev kelimesi yok.** Metin hiçbir göreve ad vermez — senaryo, frame, karakter ve benzerleri
  skill'lerin ve SDXL belgesinin; bugünkü test (`test_the_base_names_no_task`) bunu tutuyor.
- **Paralel yazma istenmez.** Reading 9 yalnız okumalar için: izin isteyen bir yazma kartla bekler, ve
  yazmaların sırası bir sonrakinin ne okuduğunu değiştirir.
- **Kod değişmez.** Döngü zaten bir turun bütün çağrılarını çalıştırıyor; yeni test yalnız kara kutunun
  topladığını tutar.

## Değişen dosyalar

- `queen-agent/backend/features/workspace/domain/prompt.py` — `SYSTEM_PROMPT` ve üstündeki yorum.
- `queen-agent/backend/tests/test_prompt.py` — `SYSTEM_PROMPT`'un testleri.
- `queen-agent/backend/tests/test_black_box.py` — bir cevabın bütün çağrıları.

## Testler

Kullanıcının yeniden yazabileceği cümleler sabitlenmez. Kural satır başına tek olduğu için bir
kuralın anahtar kelimeleri tek satırda aranır (`_a_line_says`): iki ayrı kuraldan gelen kelimeler
birbirini tutmasın.

- **Bugünkü kuralların testleri** cümle yerine anahtar kelimeye bakar: `read_file` ve *first*;
  *receipt* ve *opened files*; *opened files* ve *every round*; *invent* ve *ask*; *not sure* ve
  *ask*; *pieces* ve *before the next*; `edit_file` ve *the tool that owns*; *new file* ve *second
  version*; *in the file*; *plan
  file* ve `create_file` aynı satırda; *nothing*; *list*, *do next*; *one question*, *stop*; *not
  among your opened files*; *own writing*; *listed*, *every request*; *only what the answer needs*.
  Ölü adlar (`write_plan`, `list_files`) ve yanlış sebepler yine yok; dil ve görev kelimesi testleri
  aynı.
- **Yeni kurallar:** pencere *five*; tool'un cevabı *truth*, *refused* ve *failed*, yapılmayan
  değişiklik; *same arguments* ve *twice*, *both fail* ve *stop*; *tool can find out*, *only the
  user can decide* ve *one question*; *one round* ve *several calls*; plan, *several steps* ve *same
  turn* aynı satırda; *skill* ve *wait*.
- **Davranış taşıyan biçim:** metin son kelimesinde biter (sonda boşluk ya da boş satır yok); büyük
  harfle vurgu, `**` ve `#` yok; son bölüm üç madde, sırayla okuma, tool ve sohbet. Ekin boş satırla
  eklendiğini ve boşken metnin aynen döndüğünü `test_model_engine.py` zaten tutuyor.
- **Kara kutu:** bir cevabın bütün çağrıları — tek parçada da, ayrı parçalarda da — geldikleri
  sırayla döner.

## Bitti sayılır

- Dört suite yeşil. Frontend ve queen-editor değişmemiş.
- Modele giden system prompt başlıklı ve kısa maddeli: çalışma döngüsü, doğrulama, döngü freni, sorma
  dengesi ve paralel okuma kuralları içinde; üç temel kural sonda; bugünkü kuralların hiçbiri
  kaybolmamış (yukarıdaki tablo); suffix, `LAST_ROUND`, SDXL belgesi, skill'ler ve tool metinleri
  aynı.
- Claude metni okuyup doğruladı; commit ondan sonra.
