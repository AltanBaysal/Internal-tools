# Madde 134 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 134
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun ve kök neden

Sekizinci denemede akış planı `write_plan` ile yazdı, ve **hemen ardından aynı dosyayı
`read_file` ile geri okudu**. 125 tanımı koşullu yapmıştı; tur onu az önce yazmıştı, yani şart
sağlanmıyordu.

**Kök neden metinde bulundu** *(koşuda, Blok 9 kuralı)*. Akışın 1. adımı iki cümleyi yan yana
koyuyor:

> A chat's first turn opens with write_plan ... **A plan already there is that memory: read it**
> and carry on from the step it left open.

Model birinciyi yaptı, ve ikinciye geldiğinde bir plan gerçekten *"already there"* idi — kendi az
önce yazdığı. Cümle *"bu sohbetten önce duran bir plan"* demek istiyor ve bunu hiçbir yerde
söylemiyor.

Blok 10'un kalıbı: yasak eklenmiyor, **çelişki kaldırılıyor**. Cümle hangi planı kastettiğini
söyler.

## Yol

*"A plan already there"* → *"A plan already there when the chat opened"*. Dört kelime, ve zaman
belirtiyor: kendi yazdığın bu değil.

## Kurallar

- **Taban ve araç tanımları ellenmiyor.** 125'in koşullu cümlesi doğru; yanlış olan onu geçersiz
  kılan skill metni.
- **Planın hafıza olması duruyor.** Yarım kalan iş yeni sohbetten sürüyor, ve o sohbet planı
  okuyor — kalkan yalnız kendi yazdığını okumak.
- **Kelime tavanı bir bekçi.** Akış 450 kelimeyle sınırlı; dört kelime giriyorsa tavan da tutmalı.

## Bu turun testleri

`test_skills.py`:

- `test_the_flow_reads_a_plan_it_found_rather_than_one_it_just_wrote` — **kırmızı**
- `test_the_texts_stay_short_enough_to_be_read` — bekçi
- `test_the_flow_opens_with_a_plan` *(mevcut pin: "first turn opens with write_plan")* — bekçi

## Ayakta kalması gerekenler

125'in koşullu okuma cümlesi, 126'nın tek dokunuşlu işaretlemesi, 117'nin plana yazdığı devir
kaydı, 120'nin bağlam satırı, ve akışın 1. adımının onay beklememesi.

## Bilerek yapılmayanlar

Taban yönerge, prompt+, araç tanımları. 133 ile 135 ayrı maddeler.
