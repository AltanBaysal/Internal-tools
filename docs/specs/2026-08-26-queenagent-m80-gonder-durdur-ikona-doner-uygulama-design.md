# Madde 80 — Gönder ve durdur düğmesi ikon taşır · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m80-gonder-durdur-ikona-doner-testler-design.md) ·
**Testler:** `a9c6a95` — ön yüzde 9 kırmızı.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## Düğmenin üstü değişiyor, altı değil

`Composer`'ın tek düğmesi bugün kelime taşıyor; iki işaret alıyor:

| | Akmıyorken | Akarken |
|---|---|---|
| Üstündeki | `↑` | `⏹` |
| Adı | `action` (`Send` / `Start`) | `Stop` |
| Kapalı mı | Taslak boşsa evet | Hayır, hiçbir zaman |
| Basınca | `submit` | `onStop` |

Alt üç satır 79'un getirdiği hâliyle duruyor, tek harfi değişmiyor. Yeni olan yalnız ilk satır ve
adın nereye yazıldığı.

## Ad nereye gidiyor

Kelime kalkınca düğmenin **erişilebilir adı** da onunla kalkardı. `aria-label` onu taşıyor, `title`
fareyle bekleyene aynı kelimeyi veriyor. `aria-label` varken ad hesabı düğmenin içindekine hiç
bakmıyor — yani işaretin ada karışması diye bir şey yok, ve işareti gizlemek için ayrıca bir şey
yapmaya gerek yok.

İkisi de deponun kendi kalıbı: `.sidebar__add` (`+`) `aria-label` taşıyor, `.row-x` (`×`) ikisini
birden.

**Ad hâlâ üç ayrı kelime.** Proje ekranı `Start`, sohbet `Send`, akan cevap `Stop`. İşaret ikiye
indi ama ad indirilmedi: ok aynı ok, ama açtığı şey sohbet mi cevap mı, farklı sorular.

## Şekli

`.composer__send` sabit kare oluyor: `32px` × `32px`, ortalanmış tek işaret, `padding` yok.

- **Neden sabit:** iki işaret aynı yeri kaplamalı. `↑` ile `⏹` doğal genişlikleri farklı, ve düğme
  onlara göre büyüyüp küçülseydi cevap akmaya başladığında ayaktaki üç denetim yerinden oynardı.
- **Neden kare, daire değil:** `workspace.css.test.js` her denetimin `--radius-control` ile
  yuvarlandığını tutuyor. Bu dilde daire yalnız nokta demek — `.dots__dot` 6px, `.offline__dot` 7px,
  ve başka daire yok.
- **Neden 32:** yanındaki seçicilerle aynı boy, ayak hizasını bozmuyor.

Yazı için konmuş iki satır gidiyor: `font-weight: 500` (bir işaretin ağırlığı yok) ve `font-size:
13.5px` yerine `16px` (kelime için doğru olan ölçü, tek işaret için küçük kalıyor).

Kapalı hâlin rengi, vurgu, `hover` — hiçbiri değişmiyor.

## Dokunulmayan

- **`submit`, `onKeyDown`, taslak kuralları.** Bu madde düğmenin üstündeki şey hakkında.
- **`ChatScreen`, `ProjectScreen`, `App`.** Üçü de `Composer`'a `action` veriyor ve o `action` hâlâ
  aynı kelime; ad oradan geliyor, yani geçen şey değişmedi.
- **Başka hiçbir düğme.** `Try again`, `New chat`, onay kutusu — hepsi kelime.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** Ön yüzde **507**, hepsi yeşil. Arka uçta **2 failed, 442 passed** — ikisi
defterin dalı, ve deneme bitip defter `main`'e çevrilince ikisi de yeşile döner.

**Bu maddenin asıl sınavı düşmeyen testler.** `Composer.test.jsx`'in düğmeyi `{ name: "Send" }` ile
bulan on testi, `App.test.jsx`'in `Start`'a ve `Stop`'a basan ikisi, 67'nin iki durdurma testi —
hepsi dokunulmadan yeşil kalmalı. Biri düşerse ad gerçekten kaybolmuş demektir, ve o zaman kod
düzelir, test değil.

`dist` **kaynağıyla aynı commit'te** derleniyor.
