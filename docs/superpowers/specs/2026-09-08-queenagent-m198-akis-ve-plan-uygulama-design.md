# Madde 198 · uygulama turu — akış karakterle başlar, plan işaretlenir

**Kaynağı:** [test turu](2026-09-08-queenagent-m198-akis-ve-plan-testler-design.md), ve onun
kaynağı [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 198.

Kırmızı: arka uçta 13.

---

## `prompt.py`

- **`START_A_SCENARIO`:** *"Six steps"* → *"Five steps"*; 1. adım *(bağlam)* siliniyor ve kalanlar
  bir yukarı kayıyor. Planın *"opens with one line of context"* cümlesi de gidiyor — soru sorulmuyorsa
  o satır yine bir tahmin olurdu. `start_scenario`'nun cümlesi karakter adımına taşınıyor.
  İşaretleme cümlesi `edit_file` yerine **`mark_step_done`** diyor.
- **`WRITE_PLAN`:** adımların `- [ ]` ile yazılacağını söylüyor — biçim metinde, çünkü aracın
  doldurabilmesi için önce o biçimde doğması gerekiyor.
- **Yeni metinler:** `MARK_STEP_DONE`, `MARK_STEP_DONE_NAME`, `MARK_STEP_DONE_STEP`, ve aracın cevap
  cümleleri araçların kendi kalıbında.
- **Kelime tavanı:** 450 yerinde ve yükselmiyor — bir adım silindi, bir cümle kısaldı.

## `tools.py`

`mark_step_done(name, step)`. `plan_name(safe_name(name))` ile dosyayı buluyor; yoksa cevap adı
söylüyor. Satırları geziyor, `- [ ] <step>.` ile başlayanı bulup kutuyu dolduruyor:

- **yalnız o satır** yazılıyor, gerisi bayt bayt aynı;
- zaten dolu olan için yazma yok, cevap durumu söylüyor;
- olmayan adım için de cevap — bu deponun bütün araçları ıskaladığında cevap veriyor.

Kart yok *(`created=None`)*: dosya zaten vardı, `edit_file`'ın kuralı.

## `modes.py`

`mark_step_done` yalnız `edit`'in sormadan koştuğu listede. `plan`'ın işi planı yazmak; bir adımı
kapatmak o modun işi değil.

## Yeşilin nasıl görüleceği

Dört sabit satır. Arka uçta 933, ve ön yüz ile `queen-editor` yerinde: **641 · 739 · 591**. `dist`
yok — bu madde ön yüze dokunmuyor.
