# Madde 357 — Kırpılmış sohbette çizgi · test turu

**Kaynak:** [yol haritasının 357'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — v9-1d;
kararları *v9-1 — Sohbet sınırı*: 29 Eylül'ün *tasarımdan* paragrafı (kırpılmış sohbette modele
gitmeyen mesajları bir çizgi ayırır) ve 28 Eylül'ün *kırpılan mesajlar ekranda kalır*'ı. Tasarım:
queen-design `queen-agent-v3` — `BEHAVIOUR.md`'nin *Trimmed chat*'i, `DESIGN-STANDARD.md`'nin
`trimmed` satırı, `kit.css`'in `.trimmed` kuralları, `chat/index.html`'in `TRIMMED_LINE`'ı ve `fill`'i;
tasarımcının roadmap'inde 147 ve 182 (`sticky` kaldı).

**Kullanıcıdan gereken:** hiçbir şey. Davranış yol haritasında ve tasarımda yazılı; aşağıdaki
kararlar teknik.

## Bugün

Sunucu kırpmayı yapıyor ve kaydında söylüyor (345): `/chats/<id>` her zaman `trimmed` taşır — açık
satırın başında modele artık gitmeyen mesajların sayısı, yani modelin okumaya başladığı mesajın
sırası; hiç kırpılmamışsa `0`. `Continue here` kırpar ve kaydı yeniden okur (352). Ekran `trimmed`'ı
okumuyor: kırpılmış sohbet kırpılmamış gibi görünüyor.

## Olacak

**Sunucu söyler, ekran çizer** *(FOUNDATION, Karar 4)*: çizginin yeri kaydın `trimmed`'ı, ekran hiçbir
şey hesaplamaz.

- `trimmed` sıfırdan büyükse, `chat__column`'da `trimmed` sıradaki mesajın hemen önünde bir `p.trimmed`:
  `Messages above this line are no longer sent to the model`. Tek çizgi — kayıt tek sayı taşır.
- `trimmed` `0` ise ya da kayıtta yoksa çizgi yok.
- Görünüşü tasarımın `kit.css`'i: DM Mono 11.5, `#6b6259`, iki 1px `--line` çizgisinin ortasında,
  `8px 0` iç boşluk; **eski mesajlar okunurken `chat__scroll`'un alt kenarında bekler** — `position:
  sticky; bottom: 0` — ve altından kayan yazı görünmesin diye zemini `--canvas`.

### Kararlar

1. **Yapışıklık CSS'le, ve kilidi CSS testinde.** jsdom yerleşim yapmaz, `sticky`'nin davranışını
   ölçemez; test kuralın yazılı olduğunu tutar, davranışı tarayıcıda Claude görür (yol haritasının
   *Koşu* paragrafı — tarayıcı subagent'ta değil).
2. **`msg--trimmed` eklenmez.** Tasarım çizginin üstündeki mesajlara bu sınıfı veriyor, ama `kit.css`'te
   onu seçen tek kural yok: ekranda hiçbir şey değiştirmez, ve satırın *Bitti sayılır*'ı istemiyor.
   Çizmeyen bir sınıf ölü parça *(FOUNDATION, 3. ilke)*. Rapora açık nokta olarak yazılır.
3. **Düzeltme sürerken çizgi kaydın söylediği yerde kalır.** Bir soru düzeltilince ekran, cevap gelene
   kadar eski kaydın `trimmed`'ını taşır; yeni satırın kırpılıp kırpılmadığını kural bilir, ve o kural
   sunucuda (345). Rapora açık nokta olarak yazılır.

## Testler ne tutar

**`ChatScreen.test.jsx`** — çizgi:

| # | Ne |
|---|---|
| 1 | Kırpılmış sohbette (`trimmed: 2`, dört mesaj) `chat__column`'da tek `.trimmed`, tasarımın cümlesiyle; önündeki kardeş ikinci mesaj, arkasındaki üçüncü |
| 2 | `trimmed: 0` olan ve `trimmed` taşımayan kayıtta çizgi yok |

**`workspace.css.test.js`** — görünüşü:

| # | Ne |
|---|---|
| 3 | `.trimmed`: `position: sticky`, `bottom: 0`, zemini `var(--canvas)`, `var(--font-mono)`, `11.5px`, `#6b6259`, `padding: 8px 0`, `display: flex` |
| 4 | `.trimmed::before, .trimmed::after`: `border-top: 1px solid var(--line)` |

**`App.test.jsx`** — uçtan uca:

| # | Ne |
|---|---|
| 5 | Dolu sohbette çizgi yok; `Continue here`'den sonra çizgi `First answer.`'ın turuyla ikinci `go on` arasında — 352'nin `stubFullChat`'i, kırpma kaydı `trimmed: 2` yapar |

## Tutmaz

- **Kırpma kuralını ve `trimmed`'ın sayısını:** 345'in testleri tutuyor.
- **Bildirimi ve `Continue here`'in kapısını:** 352'nin testleri.

## Nasıl görülür

CLAUDE.md'deki dört satır. queen-agent'ın ön uç süiti yeni testlerde kırmızı verir — #2 bugün de
geçer (çizgi yok), kilit olarak kalır; arka uç ve queen-editor'ün ikisi yeşil. Kırmızı hâliyle commit
edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m357-kirpma-cizgisi-testler-plan.md).
