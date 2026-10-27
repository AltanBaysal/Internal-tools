# Madde 130 · Tur 2 (uygulama) — Tasarım

**Testler:** [2026-08-29-queenagent-m130-kapanis-testler-design.md](2026-08-29-queenagent-m130-kapanis-testler-design.md)
**Kırmızı commit:** `4c88ca2` · **Dal:** `feat/queenagent-m123-skill-rewrite`.

## Ne yazılıyor

Tek dosya, tek cümle: `skills.py`, `GENERATE_PROMPTS_PLUS`.

Cümle **kurma paragrafının sonuna** giriyor — `build_prompts` çağrısının hemen ardına — çünkü
anlattığı şey o çağrının bitişi:

> The built file is the answer: its prompts are never printed back into the chat, and the turn
> closes with the file's name rather than a list of what to do next.

Üç iş birden görüyor: dosyanın cevap olduğunu söylüyor *(geri okumaya gerek yok)*, promptların
basılmayacağını söylüyor, ve menüyü kapatıyor. Üçü tek cümlede, çünkü tavan var.

**Sonda değil ortada durması bir karar.** Metnin son paragrafı 113'ün düzenleme yolu, ve kapanış
cümlesi oraya girseydi *"bir şikâyet geldiğinde de basma"* gibi okunurdu — oysa kural kurma
turunun kapanışı hakkında.

## Kelime tavanı

300, ve `test_the_texts_stay_short_enough_to_be_read` tutuyor. Yer 128'in kısalttığı cümleden
geliyor. Tavan tutmazsa çıkacak cümle bu turda seçilir ve burada yazılır — 123'ün kuralı: bir
cümle ancak bir cümle silinerek girer.

## Değişmeyen

Taban yönerge *(112 zaten orada ve doğru)*, akış metni *(118 kendi kapanışını yazdı)*, prompt+'ın
şema çağrısı, `add_frames` cümlesi ve beşerli ritmi, elle-kurma yasağı, 113'ün `edit_file` yolu.

## Bilerek yapılmayanlar

Ön yüz, `dist`. Bu madde modelin okuduğu bir metne dokunuyor, ekrana çıkan hiçbir şeye değil.
