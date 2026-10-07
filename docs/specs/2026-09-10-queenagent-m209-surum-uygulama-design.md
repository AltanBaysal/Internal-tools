# Madde 209 — sürüm arayüzde görünür · uygulama turu

**Kaynak:** [test turunun tasarımı](2026-09-10-queenagent-m209-surum-testler-design.md).
**Test turu:** `e45391b` — üç dosya kırmızı.

## Ne yapılacak

Üç parça: bir sabit, çubuğun marka bloğunda bir satır, ve iki CSS kuralı.

```
QueenAgent
V8
```

## Sabit

```js
export const VERSION = "V8";
```

`shared/version.js`. Elle yazılır ve **yalnız bir koşu açılırken** değişir — derleme tarihi,
`package.json` sürümü ya da git etiketi değil. Üçü de başka bir ritme bağlı; koşu numarası bir
karar, ve kararın kaynağı bir dosyada durur.

Modül bir satırlık, ve deponun biçimi bu: `modes.js`, `models.js`, `railWidth.js` — bir olgu, bir
dosya. `shared/` altında çünkü sürüm uygulamanın, `workspace` özelliğinin değil.

## Marka bloğu bir sütun kazanır

Bugün blok bir **satır**: wordmark solda, katlama düğmesi `margin-left: auto` ile sağda. Sürüm
wordmark'ın **altına** ineceği için ad ile sürüm kendi sütununa alınır, ve düğme satırın sağında
kalır.

```jsx
<div className="sidebar__brand">
  <div className="sidebar__name">
    <span className="sidebar__wordmark">QueenAgent</span>
    <span className="sidebar__version">{VERSION}</span>
  </div>
  <Fold onToggle={onToggle} />
</div>
```

Katlanmış dal erken dönüyor, yani sürüm orada zaten çizilmiyor — ve testi bunu bundan sonra da
tutuyor.

## İki kural

`.sidebar__name` bir sütun; `.sidebar__version` deponun **not sesi** — `var(--muted)`, 11px,
ve harfler arası açıklık, çünkü iki karakterlik bir işaret adın altında sıkışık okunuyor.

Wordmark 21px; sürüm onun yarısından küçük olduğu için ikinci bir ad gibi değil, dipnot gibi
okunuyor.

## Derleme kuralı

CLAUDE.md: her iki araç da derlenmiş ön ucunu **gönderiyor**, ve notebook depoyu klonlayıp hiç
derlemiyor. Yani `npm run build --prefix queen-agent/frontend` koşar ve `dist` **aynı commit'e**
girer — yoksa ön uç değişikliği bitmiş sayılmaz ve notebook tarafında hiçbir şey değişmez.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

Süitin tamamı yeşil, ve uygulama açıldığında kenar çubuğunda `QueenAgent` yazısının altında `V8`
okunuyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-10-queenagent-m209-impl-plan.md).
