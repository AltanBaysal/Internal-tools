# Madde 134 · Tur 2 (uygulama) — Plan

**Testler:** [2026-08-29-queenagent-m134-plan-geri-okuma-testler-design.md](../specs/2026-08-29-queenagent-m134-plan-geri-okuma-testler-design.md)
**Kırmızı commit:** `6a0011a`

## A. `skills.py` · akışın 1. adımı hangi planı kastettiğini söyler.

*"A plan already there is that memory"* → *"A plan already there when the chat opened is that
memory"*. Dört kelime, ve tek işi zaman belirtmek: model kendi az önce yazdığını bu cümlenin
konusu sanmasın.

Yasak eklenmedi. 125'in koşullu okuma cümlesi zaten doğruydu; onu geçersiz kılan bu satırdı, ve
düzelen o.

## B. Kelime tavanı bir kelimeyle kırıldı — **451 / 450** — ve bir kesim yapıldı.

Dört kelime girdi, biri geri verilmek zorundaydı. Kesim aynı cümlenin içinden: *"so a fresh chat
**reading it** inherits the work"* → *"so a fresh chat inherits the work"*. İki kelime, ve
davranış kaybı yok — bir sonraki cümle zaten *"read it and carry on"* diyor, yani okumayı ikinci
kez söylüyordu. Pinler *("opens with one line of context"*, *"inherits the work")* ikisi de
yerinde.

## C. İki komut koşuldu: **639 yeşil**, frontend 568 yeşil, defter çifti bilinen kırmızı.

## D. Yeşil commit, ardından okuma kopyası.

## Bilerek yapılmayanlar: taban yönerge, prompt+, araç tanımları, ön yüz, `dist`.
