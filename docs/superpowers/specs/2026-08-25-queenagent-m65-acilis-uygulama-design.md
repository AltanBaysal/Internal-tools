# Madde 65 — Açılış taslak sohbete düşer · **uygulama turu**

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 65 ·
**Önceki tur:** [test tasarımı](2026-08-25-queenagent-m65-acilis-testler-design.md) — beş test
`f9d687e`'de kırmızı commit'lendi.
**Tur:** ikiden ikincisi. Bu belge, commit'lenmiş testlerin tarif ettiği kodu tarif eder.

---

## Testlerin istediği

Beş test tek bir cümleyi farklı yerlerinden tutuyor: **çatal, proje ekranı yerine o projenin taslak
sohbetine göndersin.** Dördü adresi (`/p/p1/c/new`), biri o adreste seçicinin çalıştığını istiyor,
biri de proje ekranının sidebar'dan hâlâ açıldığını.

Beşi de bugün aynı sebeple düşüyor: çatal `/p/p1` diyor. Yani yeşile dönmeleri için değişmesi
gereken tek bir karar var.

## Değişiklik

`queen-agent/frontend/src/App.jsx` — çatalın gittiği adres. Bugün `/p/<proje>`, olacağı
`/p/<proje>/c/new`. Yanına, **neden** oraya gittiğini söyleyen bir yorum: proje ekranının yazma
kutusu skill ve model seçici taşımıyor, o yüzden oraya inen kullanıcı bir mesaj göndermeden
seçicilere ulaşamıyor.

Bu kadar. Taslak ekranı, adresi, seçicileri ve taslakta yapılan seçimin nasıl tutulduğu zaten var
ve hiçbirine dokunulmuyor.

## Neden bu yol

İki alternatif elendi:

- **Proje ekranına inip oradan yönlendirmek.** İki sıçrama, ve ikincisi geçmişe düşerse geri tuşu
  proje ekranına takılır. Çatalın zaten tek bir `replace`'i var; ikinciyi eklemek onu bozar.
- **`/p/<proje>` adresinin kendisini taslak sohbet olarak çizmek.** Proje ekranını erişilemez
  kılardı — kullanıcının kararı ise onun ayrı bir kapı olarak kalması.

Kalan yol çatalın hedefini değiştirmek, ve çatal zaten "bir ekran seç ve oraya geç" için var.

## Dokunulmayanlar

- **`replace` kalır.** Çatal geçmişe yazılmaz; testlerden biri bunu tutuyor.
- **Proje yokken hiçbir şey değişmez.** Liste boşken çatal `/`'da kalır ve boş ekran çizilir.
- **Sidebar'ın proje satırı** proje ekranını açmaya devam eder.
- **"+ New chat" düğmesi** zaten taslak adresine gidiyordu; aynı kalır. Açılışın oraya inmesi onu
  gereksiz kılmıyor: bir sohbetin içindeyken taze bir taslağa dönmenin yolu odur.
- **Arka uç.** Bu madde sunucuya hiç dokunmuyor.

## `dist`

`App.jsx` ön yüz kaynağı, yani `frontend/dist` **aynı commit'te** yeniden derlenip commit'lenir.
FOUNDATION'ın 3. kararı bunu söylüyor ve `test_dist_is_committed.py` aksini reddediyor. Derlenmemiş
bir commit, defterin klonladığı depoda boş sayfa demek.

## Nasıl yeşil görülür

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

Ön yüzün beş kırmızısı yeşile döner, geri kalan 471 test yeşil kalır. Arka uç 384'te durur —
değişmediği için değişmemesi gerekiyor.

Gerileme kalkanı olarak duran iki test bu turda önem kazanıyor: **proje yokken `/`'da kalınması** ve
**çatalın geçmişe yazılmaması.** İkisi de bu maddenin sessizce kırabileceği şeyler, ve ikisi de
yeşil kalmak zorunda.
