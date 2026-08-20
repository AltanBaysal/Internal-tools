# Madde 61 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m61-test-design.md](../specs/2026-08-20-queenagent-m61-test-design.md)
— tur ikiye ayrı bir tasarım belgesi yok: yeniden adlandırmada tasarlanacak ikinci bir şey yok,
ve adın **neden bu ad olduğu** o belgede zaten yazılı. İkinci bir belge onu tekrar ederdi, ki
deponun kuralı bunu yasaklıyor.

**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adımlar

1. **`git mv queen-agent/app.ipynb queen-agent/queenagent.ipynb`** — `mv`, sil-ve-yaz değil: git
   dosyanın aynı dosya olduğunu görsün, geçmişi kopmasın.

2. **Yürürlükteki yol haritası** — `2026-08-20-queenagent-v4-colab-roadmap.md` içindeki `app.ipynb`
   geçişleri yeni ada çevrilir, ve Madde 61 kayda eklenir.

## Dokunulmayanlar, ve neden

- **queen-editor'ün `app.ipynb`'si.** Bu madde QueenAgent'ın defterini ayırt edilebilir kılmak
  için var; ikisini birden yeniden adlandırmak, başka bir aracın kararına el atmak olurdu. Birinin
  ayrışması karışıklığı zaten bitiriyor.
- **Madde 53, 55, 56, 57'nin spec ve planları.** Eski adı taşımaya devam edecekler. Onlar
  yazıldıkları günün kaydı ve kasten eskiyorlar — deponun kuralı. Bugün yazılmış olmaları bunu
  değiştirmiyor; kayıt kayıttır.
- **`queen-agent/README.md`.** Defterin adını hiç anmıyor, çünkü Madde 53'te bilerek anmamıştık —
  o zaman dosya yoktu. Adı yazacak yer Madde 58, ve orada doğru ad yazılacak.

## Beklenen yeşil

Yirmi iki defter testinin yirmi ikisi. Toplam **383**.

## Kapanış denetimi

- `queen-agent/` altında `app.ipynb` kalmamış.
- Defter hâlâ dört hücre ve geçerli JSON — testler zaten bunu soruyor.
