# Madde 130 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m130-kapanis-uygulama-design.md](../specs/2026-08-29-queenagent-m130-kapanis-uygulama-design.md)

## A. `skills.py`: kapanış cümlesi kurma paragrafının sonuna girer.

## B. Kelime tavanı kırıldı — **308 / 300** — ve kesim arandı.

Yol haritasının söylediği tam olarak oldu: *"bir cümle ancak bir cümle silinerek girer"*. İlk üç
aday kesilmedi, çünkü üçü de kilitli:

- *"rebuilt rather than patched"* — `test_a_change_goes_through_the_file_rather_than_the_prompt_list`
- *"do not assemble"* — `test_the_structured_instruction_forbids_assembling_a_prompt_by_hand`
- *"once, before the first write"* — `test_the_builder_fetches_the_schema_once`

Kilitli olmayan iki aday da kesilmedi, ama sebepleri kilit değil **davranış**: *"Fewer frames than
sentences"* yarım kalmış bir koşuyu sürdürme kuralı, ve *"the same framing and angle twice is one
picture twice"* doğrudan **Madde 111**. İkisini de pin tutmuyor, yani kesilseler sessizce
kaybolurlardı — bu planın kaydettiği şey de bu: **111'in cümlesi pinsiz duruyor.**

## C. Kesim üç yerden, üçü de tekrar — davranış kaybı yok.

1. Yeni cümle sıkıldı: *"...printed back into the chat, and the turn closes with the file's name
   rather than a list of what to do next"* → *"...printed back, and no menu of next steps closes
   the turn."*
2. *"Do not assemble a prompt or write the Python file by hand"* → *"Do not assemble a prompt by
   hand"*. Python dosyasını persona paragrafı zaten söylüyor *(`build_prompts` assembles)*, ve
   pin yalnız *"do not assemble"*e bakıyor.
3. *"Get the file right, call the builder -- and read_prompt_structure_schema once"* → *"Call
   read_prompt_structure_schema once"*. Kesilen yarım cümle, üstündeki paragrafın özetiydi.

## D. İki komut koşuldu: **633 yeşil**, frontend 568 yeşil, defter çifti bilinen kırmızı.

## E. Yeşil commit, ardından okuma kopyası.

## Bilerek yapılmayanlar: taban yönerge, akış metni, ön yüz, `dist`.
