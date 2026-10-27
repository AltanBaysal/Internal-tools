# Madde 356 — Açık dosya da çekilerek genişler · uygulama turu

**Kaynak:** [yol haritasının 356'sı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2o);
[test turunun spec'i](2026-09-29-queenagent-m356-acik-dosya-genisligi-testler-design.md) ve onun
kırmızı commit'i (`4aca3d1b`). Tasarım: `queen-agent-v3`'ün 158'i ve 177'si.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

Genişliğin sahibi zaten tek: App'in `railWidth`'i ve `resizeRail`'i (Madde 50). Kural değişmez —
`railWidthFor` `220`'nin altını katlama, `560`'ın üstünü `560` sayar —, ve App'e dokunulmaz.
Değişen, panelin okurken o genişliği okuması ve kenarını vermesi.

**`FileRail.jsx`**

- `railStyle` okurken de genişliği yazar, katlı olsa bile: okurken panel tutulan genişliktedir, ve
  katlılık dosya kapanınca görünür. Genişlik verilmediyse yine stylesheet'inki; katlı ve okumuyorken
  yine şerit.
- `railClass` çekilirken `rail--dragging`'i okurken de ekler: `rail rail--open rail--dragging`.
- Okuma dalı da `onResize` verildiyse `Grip`'i çizer, `FilePanel`'in önünde. Aynı `Grip`, aynı hesap,
  aynı `onResize`; `setDragging` aynı durum.
- Baştaki yorumlar bugünü söyler: tutma yeri artık listenin değil panelin; `railStyle`'ın "while a
  document is open the width belongs to the document" cümlesi düşer.

İki dal tek dala birleştirilmez: okuma dalı bir `FilePanel`, liste dalı başlık satırı ve liste, ve
aralarındaki ortak parça bir satır — `Grip`. Birleştirmek iki dalın koşullarını iç içe sokardı.

**`workspace.css`**

- `.rail--open`'dan `width: 560px` kalkar: `.rail`'in `320`'si çekilene kadar geçer, App'in inline
  genişliği çekilince. Yorumu bugünü söyler.
- `.rail__grip`'e `z-index: 1`, nedeniyle: `.reader`'ın `fadeIn`'i (opacity) onu tutma yeriyle aynı
  boyama katmanına alır, ve sonraki kardeş olarak tutma yerini örter (tasarımın 177'si).

**`railWidth.js`** — `MAX_RAIL_WIDTH`'in yorumu bugünü söyler: panelin en genişi, liste de açık dosya
da.

**Proje ekranının paneli** (`.panel`, `560`) değişmez: yanında liste yok (tasarımın 158'i).

## Dokunulmayanlar

- **CODE-STANDARD'ın hareket paragrafı** (379'un): "the only motion that is not a fade is the rail's
  width" hâlâ doğru — yeni bir hareket gelmiyor; okuyan panel de aynı `width 220ms`'le açılıp
  kapanıyor.
- **`APP-BUGS.md`'nin 45'i ve 46'sı** bu maddenin değil. 46'ya dair: okurken `220`'nin altına
  çekilince tutma yeri kalkmıyor (okuyucu duruyor), yani sürükleme sürüyor ve bırakınca bitiyor;
  tasarım orada sürüklemeyi katlanınca bitiriyor. Fark yalnız katlandıktan sonra fareyi geri
  çekmekte: panel yine katlı kalır, genişlik yeni değeri alır. Yazılmadı.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

CLAUDE.md'deki dört satır; dördü de yeşil. Tarayıcıda: dosya listenin genişliğinde açılır, sol
kenarında imleç `↔`, çekince genişler ya da daralır, `←`'dan sonra liste aynı genişlikte.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m356-acik-dosya-genisligi-uygulama-plan.md).
