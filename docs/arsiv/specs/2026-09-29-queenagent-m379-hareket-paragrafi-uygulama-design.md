# Madde 379 — CODE-STANDARD'ın hareket paragrafı yalnız bugünü anlatır · uygulama turu

**Kaynak:** [yol haritasının 379'u](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), ve
[test turunun spec'i](2026-09-29-queenagent-m379-hareket-paragrafi-testler-design.md). Karar
kullanıcının, 29 Eylül: "Kural kalksın, paragraf yalnız bugünkü durumu anlatsın."

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

Kod değişmez; bir paragraf ve üç yorum değişir. `dist` derlenmez: CSS'teki yorumlar derlenmiş
pakete girmez, ve kaynakta başka bir şey değişmiyor.

### 1. CODE-STANDARD.md'nin paragrafı

Bugün:

> `shared/app.css` owns the colour variables, the radii, the focus ring and the two keyframes — a
> 140–220ms `fadeIn` and the three dots' `blink`. A component never writes its own focus outline and
> never invents a third animation. The only motion that is not a fade is the rail's width. The accent
> `--accent` marks the primary action and nothing else.

Olacak:

> `shared/app.css` owns the colour variables, the radii, the focus ring and the two keyframes every
> surface shares: `fadeIn`, an opacity fade, and `blink`, which pulses the three dots and the loading
> skeleton. A component never writes its own focus outline. `features/workspace/workspace.css` holds
> `msg-spin`, the spinner's turn — on the live row, the loading file list and a chat that is opening —
> and the transitions: the sidebar and the rail fold by their width, and a message's edit pencil fades
> in. The accent `--accent` marks the primary action and nothing else.

Neden böyle:

- **Yasak yok** — "never invents a third animation" gider *(kullanıcı)*. Odak halkası cümlesi kalır:
  o hareketle ilgili değil, ve 379 ona dokunmuyor.
- **Her animasyon nerede duruyor, ve neyi hareket ettiriyor.** İki dosya, üç keyframe, üç geçiş.
- **Süreler yazılmaz.** "140–220ms" gider: sayı dosyada, ve belge onu kopyalarsa eskir *(CLAUDE.md —
  "a doc names the file instead")*. Bant `app.css.test.js`'te tutuluyor.
- Paragraf CODE-STANDARD'ın geri kalanıyla aynı dilde ve boyda kalır; 353'ün değiştirdiği `trash/`
  satırına dokunulmaz.

### 2. `.rail__head--still`'in yorumu (`workspace.css`)

Bugün: "While a document is being read there is nothing to fold, so the heading is a label again." —
yanlış: okuma sırasında rail `FilePanel`'i gösterir, bu sınıfı değil. Sınıfı yalnız `FileRail.jsx`
kullanıyor, `foldedByWidth` doğruyken: kabuk ikisine yetmeyince rail katlanır, ve şerit açılacak yer
bulamaz. Olacak:

> Folded because the shell has no room for both (FileRail's `foldedByWidth`): the strip has nowhere
> to open into, so the heading is a label rather than a button.

### 3. Kaldırılan kuralı söyleyen iki yorum daha

Kural kalkınca ikisi de yanlış kalıyor; CLAUDE.md'ye göre bir yorum yalnız bugün doğru olanı söyler.

- **`app.css`, keyframe'lerin üstü:** "The only motion the design allows: a 140-220ms opacity fade,
  and the rail's width transition. One name, and it says what it does -- an element that has been
  laid out never moves." Olacak: "Shared by every surface: an opacity fade, and the pulse of the three
  dots and the loading skeleton. Neither moves anything -- an element that has been laid out stays
  where it was put." Bu, `app.css.test.js`'in "app.css's keyframes change opacity and move nothing"
  testinin söylediği.
- **`workspace.css`, `.rail`'in üstü:** "Width is the one thing the design lets move." cümlesi
  silinir; yorumun ilk cümlesi kalır. Genişlikle katlanmayı paragraf ve `.rail--collapsed`'ın yorumu
  zaten söylüyor.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. Test turunun iki kırmızısı yeşile döner: paragraf `` `msg-spin` ``
diyor, ve `never invents` ile `The only motion` artık yok. Öteki testler değişmez ve yeşil kalır.
