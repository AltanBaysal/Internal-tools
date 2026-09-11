# Madde 210 — sürüm kaydı · uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-11-queen-editor-m210-surum-kaydi-uygulama-design.md) ·
**Madde:** [v5 yol haritası](2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `queen-editor/SURUMLER.md` yazılır.** Üç bölüm:

- **Güncel sürüm** — tek satır, tek dal adı: `feat/queen-editor-v5`. Testin aradığı *Güncel* sözcüğü
  bu satırda geçer ve dosyada başka hiçbir dal adı o satıra girmez.
- **Sürümler ve koşuları** — beş sürüm, on dört belge. Her satır belgenin **dosya adını** taşır,
  çünkü test dosya adını arıyor ve bir belgeye adıyla gidiliyor; başlıklar tekrar ediyor, adlar
  etmiyor.
- **Ne yanlış gitti** — koşan roadmap'e madde eklenecek yerde yeni roadmap açılması. Kayıt bunu
  taşımazsa aynı soru aynı cevabı alır.

v2 satırı dal adı yerine **bilinmiyor** der ve ölçümü yanına koyar: belgeyi ekleyen commit `01344b0`,
`feat/queen-editor-v1`'in geçmişinde duruyor ama bu orada yazıldığını kanıtlamıyor.

**2 · `CLAUDE.md`'nin cümlesi düzelir.** Bugün *"one file per run, highest `vN` current"* diyor;
bu sabahki yanlış cevap oradan çıktı. Yerine geçen kural iki şey söyler: **bir sürüm bir daldır ve o
dalın tek yol haritası olur**, ve güncel sürüm tool'un kendi kaydından okunur. Cümlenin uzunluğu
artmıyor — CLAUDE.md kural söyler, olgu tutmaz.

**3 · Üçüncü iddia dürüst bilinmeyeni kabul eder.** `test_version_record.py`'deki
`test_the_record_and_each_roadmap_name_the_same_branch`: başlığında dal adı olmayan bir belge, ancak
kayıttaki satırı `bilinmiyor` diyorsa geçer. Sessiz kalan belge hâlâ kırmızı.

Testin yorumu neden gevşediğini söyler, yoksa bir sonraki okuyan onu kaçamak sanır.

**4 · Takım koşulur.**

```bash
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: arka uç **745 yeşil**, ön yüz 591 yeşil ve değişmemiş.

**5 · Yeşil commit edilir**, ve yol haritasının 210 satırı ✅ ile işaretlenip sayaç 1/7'ye çekilir.

## Dokunulmayanlar

- Eski on üç belgenin metni ve adları.
- `dist` — bu madde ön yüze hiç dokunmuyor.
- QueenAgent'ın kendi sürüm kaydı.
