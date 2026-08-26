# Madde 84 — Tool call'lar karta döner ve tek kapının arkasına girer · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 84 ·
**Test turu:** [testler spec'i](2026-08-26-queenagent-m84-tool-callar-karta-doner-testler-design.md) ·
commit `17a5b21`, **14 kırmızı**.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder.

---

## Ne kırmızı

| Nerede | Kaç |
|---|---|
| `ChatScreen.test.jsx` | 12 |
| `workspace.css.test.js` | 2 |

Arka uçta hiçbir şey kırmızı değil ve olmayacak: kayıt 66 ile 78'in bıraktığı gibi duruyor.

## `ToolCalls` durum tutan bir bileşen oluyor

Bugün saf bir çizim fonksiyonu: aldığı listeyi satır satır basıyor. Artık kendi açık/kapalı
durumunu tutuyor.

```jsx
function ToolCalls({ calls, running }) {
  const [open, setOpen] = useState(false);
  if (!calls?.length) return null;
  const summary = `⏺ ${calls.length} step${calls.length === 1 ? "" : "s"}`;
  const last = calls[calls.length - 1];
  return (
    <div className="tool-calls">
      <button
        type="button"
        className="tool-calls__handle"
        aria-expanded={open}
        onClick={() => setOpen((shown) => !shown)}
      >
        <span className="tool-calls__summary">
          {running && !open ? headOf(last) : summary}
        </span>
        <span className="tool-calls__chevron">{open ? "⌃" : "⌄"}</span>
      </button>
      {open
        ? calls.map((call, index) => (
            <div className="tool-call" key={`${call.tool}-${call.target}-${index}`}>
              <span className="tool-call__head">{headOf(call)}</span>
              {call.outcome ? (
                <span className="tool-call__outcome">{call.outcome}</span>
              ) : null}
            </div>
          ))
        : null}
    </div>
  );
}
```

`headOf` bugün satır içinde kurulan metnin adı olur — `⏺ tool(target)`, konusu yoksa parantezsiz.
İki yerde okunuyor artık *(tutamak ve kart)*, ve iki yerde okunan bir ifadenin adı olur.

**Durum bileşenin kendi içinde, `App`'te değil.** Skill menüsü `App`'te duruyor çünkü Escape onu
sabit bir sırada kapatıyor; bu liste bir katman değil, sohbetin içinde duran bir kart yığını. Escape
onu kapatmıyor, yani yukarı taşınacak bir sebep yok.

**Her mesaj kendi durumunu tutuyor**, çünkü döngü her mesaj için ayrı bir `ToolCalls` çiziyor. Yeni
gelen cevabın anahtarı yeni, yani durumu da yeni: kapalı doğuyor. Sayfa yenilenince hepsi kapalı.
Bu, *"bitince sadece mesaj gözüksün"* kuralının bedava gelen hâli.

## `running` nereden geliyor

Üç çağrı yeri var ve ikisi akan tur:

| Nerede | `running` |
|---|---|
| Saklanmış mesajın döngüsü | verilmiyor — tur bitmiş |
| Akan kutu | `running` |
| Bekleyen kutu | `running` |

Yani hangi kutunun çizdiği zaten hangi durumda olduğunu söylüyor; ekstra bir bayrağa ya da bir
geçişi izleyen efekte gerek yok.

## Stil: bir kart iskeleti, iki kere

`.tool-call` ile `.tool-calls__handle` aynı iskeleti giyiyor — dosya kartınınkini: `var(--surface)`,
`1px solid var(--line)`, `12px` köşe, `11px 14px` iç boşluk, `340px` sınır, `10px` aralık.

Ayıran tek şey basılabilirlik:

| | `.tool-calls__handle` | `.tool-call` |
|---|---|---|
| Etiket | `<button>` | `<div>` |
| `cursor` | `pointer` | yok |
| `:hover` | kenarlık koyulaşıyor | yok |

`.tool-calls` kabının aralığı `2px`'ten `8px`'e çıkıyor — `.file-cards` neyse o. İki piksel satırlar
içindi; kartlar nefes ister.

**Metnin hiyerarşisi dosya kartından geliyor:** başlık `var(--ink)`, sonuç `var(--muted)` — tıpkı
`.file-card__name` ile `.file-card__hint` gibi. Her ikisi de mono 11.5px kalıyor.

Başlık uzunsa üç noktayla kesiliyor *(`overflow: hidden` · `text-overflow: ellipsis` ·
`white-space: nowrap`)*, sonuç kesilmiyor — dosya kartındaki iş bölümünün aynısı: uzayan ada isim,
sabit kalan yere not.

## 78'in kuralı değişmiyor, varsayımı değişiyor

78 şunu yazmıştı: *"vurgu birincil eylemi işaretler, ve olmuş bir adım basılacak bir şey değil"*.
Kural aynen duruyor ve kodda görünür hâlde: çağrı kartı `<div>`, imleci yok, hover'da oynamıyor, ve
vurgu rengi taşımıyor.

Değişen şey o kuralın yanındaki sessiz varsayım — *bir kayıt silik olmalı*. Olmak zorunda değil. Bir
kayıt kenarlıklı bir kutuda da durabilir ve basılamaz kalabilir.

Stil dosyasındaki yorum bu yüzden yeniden yazılıyor: kuralı koruyor, varsayımı bırakıyor.

## `⎿` gidiyor

O işaret *"üstündekinin sonucu"* diyordu. Kartın sınırı artık aynı şeyi söylüyor. `⏺` kalıyor —
adımın kendi işareti, ve tutamakta da o duruyor.

## Kapsam dışı

- **Arka uç.** Tek satır değişmiyor.
- **Ne kaydedildiği.** 66 ile 78'in kararı.
- **Açık/kapalının hatırlanması.** Ne diske ne tarayıcıya yazılıyor.
- **Escape.** Sırasına girmiyor; `fark 67`'nin dörtlü sırası dörtte kalıyor.
- **`createdFiles` ve dosya kartları.** Ödünç alınan iskelet onların; kendilerine dokunulmuyor.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** Arka uçta **2 failed, 430 passed** — ikisi defterin dalı. Ön yüzde
**505 passed**, kırmızı yok.

`dist` bu turda **derlenip aynı commit'e giriyor**.
