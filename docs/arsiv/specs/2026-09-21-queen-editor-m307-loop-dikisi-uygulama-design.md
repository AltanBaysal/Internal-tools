# Madde 307 — Loop videonun dikişi, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m307 test turu](2026-09-21-queen-editor-m307-loop-dikisi-testler-design.md),
`6c0defcb` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** karar alındı *(prompt tarafı)*. Sonucu kullanıcı koşunun sonunda görecek.

## Port

`PromptWriter.write(prompts, mode)` — üç yazıcı da alıyor, sesinki kullanmıyor. Üreticilerin
`references`'ı ile aynı kural: **kuyruğun tek çağrı şekli var.**

## Kural tek cümle, iki yazıcıda

`LOOP_RULE` bir kere yazılıyor ve iki video talimatının sonuna ekleniyor. İçeriği:

- klip arka arkaya çalınacak, ve son kare ilk karedir;
- **kendine dönen** bir hareket yaz — sallanma, nefes, adımın geri gelmesi, saçın yerine oturması;
- **biten** bir hareket yazma: bitişe yaklaşırken duran bir hareket, tekrarda duruş gibi okunur.

Talimatın kendisi değişmiyor, sonuna ekleniyor: standart kipte bugünkü metnin **aynısı** gidiyor,
ve bunu bir test tutuyor.

## Döngü

`run_loop` yazıcıyı çağırırken işin kipini de veriyor — `production_mode.of(current)`, zaten elinde.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. Maddenin gerçek ölçüsü kullanıcının gözü: klip beş kez
yan yana konduğunda nabız okunmuyorsa kapanır.
