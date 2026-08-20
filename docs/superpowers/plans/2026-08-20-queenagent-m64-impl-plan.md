# Madde 64 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m64-test-design.md](../specs/2026-08-20-queenagent-m64-test-design.md)
— tur ikiye ayrı bir tasarım belgesi yok: tasarlanacak ikinci bir şey yok, ve `main`'in **neden**
doğru dal olduğu o belgede yazılı. İkinci bir belge onu tekrar ederdi, ki deponun kuralı bunu
yasaklıyor.

**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adımlar

1. **`queen-agent/queenagent.ipynb`**, NotebookEdit ile (Edit değil: dosya JSON). CONFIG hücresinde
   `BRANCH = "main"`, ve üstündeki iki satırlık gerekçe yeniden yazılır. Bugünkü gerekçe
   *"main bunu taşımıyor"* diyor; yerine **neden main olduğu** geçer — çünkü bir sonraki okuyanın
   sorusu bu olacak, ve cevabı kodun kendisinde yok.

2. **Yürürlükteki yol haritası.** Madde 64 eklenir, ve Madde 58'in "merge'den sonra `BRANCH` main'e
   çevrilecek" satırı yapıldı olarak işaretlenir. Roadmap başlığındaki `**Branch:**` satırı
   **kalır** — koşunun hangi dalda yapıldığını söylüyor ve o hâlâ doğru; merge edildiği not
   düşülür.

## Bilerek yapılmayan

- **`docs/superpowers/plans/2026-08-20-queenagent-m55-impl-plan.md`.** `BRANCH`'in neden özellik
  dalı olduğunu anlatıyor ve öyle kalıyor: yazıldığı günün kaydı, kasten eskiyor.
- **`dist`.** Arayüzde tek satır değişmiyor, yani yeniden derlemenin bir anlamı yok — derleme
  yalnız kaynağı değişince commit'lenir.

## Beklenen yeşil

Tur 1'in iki kırmızısı. Backend **384**, arayüz **474**'te kalır.

## Kapanış denetimi

- Depoda `feat/queenagent-colab` yalnız `docs/superpowers/` altında geçiyor — orası kayıt.
- CONFIG hücresi çalıştığında `✓ Dal: main` basıyor.
