# Madde 198 · test turu — akış karakterle başlar, plan işaretlenir

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 198.

---

## Bugün ne oluyor

`START_A_SCENARIO` **altı adım**: bağlam, plan, karakterler, mekânlar, sahneler, promptlar. İlk adım
186'nın kararıydı — planın açılış satırını model uydurmasın diye. Kullanılınca bedeli görüldü: iş
başlamadan cevaplanacak bir soru.

Planın işaretlenmesi de yazılı — *"An approved step's line in the plan is marked done with one
edit_file, never a rewrite"* — ama **işaretin biçimi hiçbir yerde tanımlı değil.** Model her turda
kendi işaretini uyduruyor, sonraki tur onu tanımıyor, ve planın bütün değeri *(taze bir sohbetin
nerede kalındığını okuması)* buharlaşıyor.

## Ne kurulacak

**Beş adım:** plan, karakterler *(+ kıyafetler)*, mekânlar, sahneler, promptlar. Bağlam sorusu yok;
planın açılış bağlam satırı da yok — model kendisine söylenmemiş şeyi yazmaz.

**`start_scenario` karakter adımına dönüyor** *(kullanıcı kararı, 8 Eylül)*, 186 öncesindeki yerine:
dosyanın adını veren şey bağlamdı ve o gitti.

**Adımlar kutulu yazılıyor** — `- [ ]` — ve onaylanan adımı **`mark_step_done`** işaretliyor.
`edit_file` ile serbest bir düzenleme değil: aynı çıkması gereken bir şeyi kod yapar
*(FOUNDATION 5)*, ve ancak o zaman bir sonraki sohbet işareti tanır.

### Aracın şekli

`mark_step_done(name, step)`. `name` planın adı *(`write_plan`'inkiyle aynı, `plan_name`'den
geçiyor)*, `step` adımın numarası.

- Kutusu boş olan satırı dolduruyor; **dosyanın geri kalanına dokunmuyor.**
- Zaten dolu bir adım: yazma yok, cevap *"zaten işaretli"* diyor.
- Olmayan bir adım ya da olmayan bir plan: cevap ne olduğunu söylüyor, ve **hata değil** — bu
  deponun bütün araçları ıskaladığında cevap veriyor, çökmüyor.
- **Modlarda:** `edit` sormadan koşuyor; `ask` ve `plan` soruyor. Plan modunun işi planlamak, adım
  kapatmak değil.

## Testler

### `test_skills.py`

1. **akış beş adım** — *"Five steps"*, ve *"Six steps"* metinde yok.
2. **bağlam sorusu yok** — *"what it is for"* geçmiyor.
3. **plan birinci adım.**
4. **`start_scenario` karakter adımında** — o paragrafta geçiyor.
5. **işaretleme aracın işi** — metin `mark_step_done` diyor, ve *"marked done with one edit_file"*
   artık geçmiyor.
6. **kelime tavanı yerinde** — 450, ve yükselmiyor *(var olan test)*.

### `test_prompt.py`

7. **`WRITE_PLAN` adımların kutulu yazılacağını söylüyor** — `- [ ]`.

### `test_tools.py`

8. **araç modele bildiriliyor** — `mark_step_done`, `TOOL_SPECS`'in listesinde.
9. **boş kutuyu dolduruyor** — yalnız o satır; ötekiler ve metnin geri kalanı olduğu gibi.
10. **zaten dolu bir adım yeniden yazılmıyor** — dosya bayt bayt aynı, cevap durumu söylüyor.
11. **olmayan adım** — cevap söylüyor, dosya kımıldamıyor.
12. **olmayan plan** — cevap söylüyor, ve çökmüyor.

### `test_modes.py`

13. **`edit` sormadan koşuyor**, `ask` ve `plan` soruyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` arka ucunda 12 kırmızı — `mark_step_done`
diye bir araç yok, akış hâlâ altı adım ve bağlam soruyor. Ön yüz ve `queen-editor` kımıldamıyor:
**641 · 739 · 591** yerinde.
