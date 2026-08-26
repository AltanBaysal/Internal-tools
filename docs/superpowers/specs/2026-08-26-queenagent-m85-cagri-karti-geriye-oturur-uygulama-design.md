# Madde 85 — Çağrı kartı geriye oturur · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 85 ·
**Test turu:** [testler spec'i](2026-08-26-queenagent-m85-cagri-karti-geriye-oturur-testler-design.md) ·
commit `77f706f`, **2 kırmızı**.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder.

---

## Ne kırmızı

| Nerede | Kaç |
|---|---|
| `workspace.css.test.js` | 2 |

Tek dosya değişiyor: `workspace.css`. `ChatScreen.jsx` açılmıyor — davranış değişmiyor, yalnız iki
renk.

## Dört satır

| Kural | Bugün | Yarın |
|---|---|---|
| `.tool-calls__handle` · `background` | `var(--surface)` | `#f4efe7` |
| `.tool-calls__summary` · `color` | `var(--ink)` | `var(--muted)` |
| `.tool-call` · `background` | `var(--surface)` | `#f4efe7` |
| `.tool-call__head` · `color` | `var(--ink)` | `var(--muted)` |

`.tool-call__outcome` zaten `var(--muted)` — dokunulmuyor. `.tool-calls__chevron` de öyle.

## Renk nereden geliyor

`#f4efe7` uydurulmadı: bugün `.file-card--selected`'ın zemini, ve deponun en açık tonu. Sayfa
`--canvas` `#f7f5f1`, yani bu ton sayfadan **bir tık aşağıda**. `--surface` `#fffdfa` ise sayfadan
yukarıda.

Yön farkı işin tamamı: yukarıdaki bir zemin kartı kaldırıyor, aşağıdaki oturtuyor.

**Neden bir değişken değil:** bu deponun bir ton için değişken açma eşiği bir kullanım değil.
`#ede6dc` *(baloncuk)*, `#f0e7de` *(uzantı rozeti)*, `#d9d0c3` *(kart hover kenarlığı)* — hepsi ham
yazılı. Aynı ton iki yerde geçiyor olacak, ve ikisi bağımsız kararlar: seçili dosya kartının tonu
değişirse çağrı kartınınki değişmek zorunda değil.

## Metnin tek tona inmesi

Başlık `var(--muted)` olunca sonuçla aynı renge geliyor, ve kart tek düz tona iniyor.

Kullanıcının verdiği ölçü bu — *"`Stopped` yazısı gibi"* — ve `Stopped` tam olarak öyle: tek ton,
mono, gri. Bilerek kabul edilen bir sonuç.

Ayırt etme işi renkten yere geçiyor: başlık solda ve uzarsa üç noktayla kesiliyor, sonuç sağda ve
yerini koruyor. İkisi de `flex` kuralı, ve ikisi de duruyor.

## 84'ün iskeleti duruyor

Kenarlık `1px solid var(--line)`, köşe `12px`, sınır `340px`, iç boşluk `11px 14px`, `fadeIn`,
tutamağın `cursor: pointer`'ı ve hover'ı — hiçbiri değişmiyor. 84'ün iki stil testi bu turda da
yeşil kalıyor.

## Yorumlar

`.tool-calls`'un üstündeki yorum bir cümle kazanıyor: ışığın neden dosya kartından ayrıştığı. Bugün
*"bir kayıt silik olmak zorunda değil"* diyor ve bu doğru kalıyor; eklenen şey, **silik olmasa da
öne çıkmadığı** — çünkü açtığı bir şey yok.

`.tool-call`'un üstündeki *"nothing to press, because it opens nothing"* cümlesi zaten bunu
söylüyor; renk artık onu tekrarlıyor.

## Kapsam dışı

- **Davranış.** `ChatScreen.jsx` açılmıyor.
- **İskelet.** Kenarlık, köşe, genişlik, iç boşluk, animasyon.
- **Dosya kartı.** Bir kapı; parlak kalıyor. Ayrışan çağrı kartı.
- **`Stopped` satırı.** Ölçü o.
- **Arka uç.**

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** Arka uçta **2 failed, 430 passed** — ikisi defterin dalı. Ön yüzde
**507 passed**, kırmızı yok.

`dist` bu turda **derlenip aynı commit'e giriyor**: `workspace.css` bir ön yüz kaynağı.
