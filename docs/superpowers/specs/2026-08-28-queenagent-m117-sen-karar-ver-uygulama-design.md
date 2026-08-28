# Madde 117 — *Sen karar ver* yalnız sorulduğu adımı kapatır · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 117 ve
[tur 1'in tasarımı](2026-08-28-queenagent-m117-sen-karar-ver-testler-design.md). Testler kırmızı
commit'te; bu tur onların tarif ettiği cümleleri yazar.

## Değişen tek yer

`skills.py` · `START_A_SCENARIO` · döngü paragrafı. Cevabın üç geliş yolunu sayan cümleler ile
*"When a step is approved"* cümlesi arasına, dördüncü yol olarak:

> A fourth way is a delegation -- you decide. It answers only the question that was asked: the
> flow chooses for that one step, shows what it chose, and the step still ends when the user
> approves it; the next step's question is asked as ever, because deciding one step is not
> authority over the flow. The plan writes a delegation with the name of the step it closed,
> never as a standing authority -- a fresh chat reads the plan and inherits exactly what is
> written there.

**Neden burası:** üç geliş yolunun hemen ardı, çünkü eksik olan dördüncü yol; ve *"When a step is
approved"* cümlesinin önü, çünkü devrin onayı kaldırmadığını söyleyen cümle onay kuralına yaslanır.

**Kip:** öteki cümleler gibi tasvir — *"this is how you do this job"* — emir değil; seçili kalan
skill'in *"thanks"* mesajında üretime başlamaması bu kipin gerekçesiydi ve bozulmuyor.

## Bilerek yapılmayanlar

- **`prompt.py` ellenmez** — skill'siz sohbette *"sen karar ver"* işin tamamını devreder ve bu
  doğru davranış.
- **prompt+ metni ellenmez** — kendi başına koşmak onun tasarımı *("asking is for names never
  settled, not for craft")*.
- **`modes.py` ve izin makinesi ellenmez** — sorun yetkinin ricayla değil metinle tutulmasında
  değildi; eksik olan tek cümleydi, kapsam cümlesi.
- **`dist` derlenmez** — ön yüz bu maddede yok.

## Beklenen yeşil

`test_skills.py`'ın üç yenisi dahil bütün suite; kalan iki kırmızı `test_notebook`'un ve dal
yaşadıkça bilinen kırmızı.
