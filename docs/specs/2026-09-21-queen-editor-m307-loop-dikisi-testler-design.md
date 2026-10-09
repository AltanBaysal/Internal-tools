# Madde 307 — Loop videonun dikişi, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** alındı. Yol
[ölçüm spec'inde](2026-09-21-queen-editor-m307-loop-dikisi-olcum-design.md) iki seçenekle soruldu;
kullanıcı kesim tarafını **kendi muhakemesiyle** eledi *(21 Eylül — "abi kesersek de loop olmaz,
mantıklı düşün, frameler tutmaz")*: klibin sonundan kare atmak son kareyi ilk kare olmaktan
çıkarır, yani loop'un kendisini bozar. **Prompt tarafı koşuluyor.**

## Sorun

Loop modunda ilk ve son kare aynı fotoğraf, yani **görüntü** dikişte uyuyor. Uymayan şey **hareket**:
model son kareye oturmak için yavaşlıyor, sonraki tekrar duruştan başlıyor, ve klibi beş kez yan yana
koyunca beş nabız gibi okunuyor.

## Yapılacak

Hareketi **döngüsel** yazdırmak: biten bir hareket değil, kendine dönen bir hareket — sallanma,
nefes, yürüyüş, saçın savrulup yerine gelmesi. Böyle bir hareket son kareye zaten **kendi ritmiyle**
varır; yavaşlama bir duruş gibi değil, dönüşün kendisi gibi okunur.

## Kip yazıcıya ulaşmıyor

Bugün `PromptWriter.write(prompts)` yalnız karenin sözlerini alıyor; **hangi kipte üretildiğini
bilmiyor**. Port bir alan daha alıyor: `write(prompts, mode)`. Üç yazıcı da alıyor, sesinki
kullanmıyor — üreticilerin `references`'ı gibi: **tek çağrı şekli**.

Loop kuralı **iki video yazıcısına da** giriyor: H3 ve WAN. Loop kipi ikisinde de var, ve kural
ikisinde de aynı cümle.

## Yazılacak testler

### `backend/tests/test_video_prompt_writer.py`

1. **`test_a_loop_video_is_asked_for_a_motion_that_returns`** — H3 talimatına loop kuralı ekleniyor.
2. **`test_a_plain_video_is_asked_for_nothing_extra`** — standart kipte talimat bugünküyle aynı.
3. **`test_wan_asks_for_the_same_returning_motion`** — WAN yazıcısı da.
4. **`test_the_loop_rule_says_what_it_wants_and_what_it_refuses`** — kural hem *"kendine dönen"*
   diyor, hem *"biten bir hareket değil"*.
5. **`test_the_sound_writer_takes_the_mode_and_ignores_it`** — tek çağrı şekli.

### `backend/tests/test_photo_usecases.py`

6. **`test_the_writer_is_told_which_mode_the_job_is_in`** — loop işinde yazıcıya loop geçiyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı. **Sonucu kullanıcı görecek:** klip üretilip beş
kez yan yana konduğunda nabız okunmuyorsa madde kapanır; okunuyorsa kesim tarafı kendi maddesi olur
*(ve o madde loop'un kendisini bozmadan nasıl kesileceğini çözmek zorunda)*.
