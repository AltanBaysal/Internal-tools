# Madde 107 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 107
**Testler kırmızı commit'te (7666334).** Bu tur yalnız `prompt.py` ve `skills.py` metinlerine dokunur.

## Cümleler

**Taban (prompt.py):** "Having seen a file earlier..." cümlesi gider; yerine okuma sınırı gelir:
read_file cevabın gerek duyduğu dosya içindir ve fazlasına değmez; taze okuma yalnız başkasının
değiştirmiş olabileceği dosya için, kendi yazdığını doğrulamak için asla — yazdığın, yazıldığı
gibi diskte.

**Akış, adım 1:** açılış hamleleri sohbetin ilk turuna bağlanır: "A chat's first turn opens with
list_files, then write_plan; later turns carry on from what the chat already knows."

**Akış, adım 2:** şema bir kez, doğumdan önce: "Call read_prompt_structure_schema once, before
the birth; later edits do not fetch it again." Doğum cümlesi olduğu gibi kalır.

**Prompt+:** "before writing anything" → "once, before the first write".

## Tavan dengesi

Akışa ~+20 kelime girer; karşılığında silinenler: "An answer arrives four ways." cümlesi (sayım
zaten ardından sıralanıyor) ve adım 1 ile döngü paragrafında kısaltmalar. Prompt+'a +2 girer;
iki kelime başka yerden kırpılır. Ölçüyü tavan testi verir; pin cümlesi asla kırpılmaz.

## Ayakta kalması gerekenler

Tur 1 tasarımındaki liste: `read it first`, görev kelimesi yasağı, write_plan'ın şemadan önce
gelişi, şemanın `born once`tan önce gelişi, tüm eski pinler, 450/300 tavanları.

## Bilerek yapılmayanlar

Kod değişmez; şema, defter, dist ellenmez; okuma kopyası bu maddelerin sonunda topluca güncellenir.
