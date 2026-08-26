# Madde 80 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m80-gonder-durdur-ikona-doner-uygulama-design.md](../specs/2026-08-26-queenagent-m80-gonder-durdur-ikona-doner-uygulama-design.md)
**Kırmızı testler:** `a9c6a95` — ön yüzde 9.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

### 1. `Composer.jsx` — düğme kelime yerine işaret taşır

Dosyanın başına, `foot` açıklamasının yanına iki sabit:

```jsx
// The two marks the one button wears. Written here rather than inline: the running state picks
// between them, and a reader should see both at once to know it is a pair.
const SEND = "↑";
const STOP = "⏹";
```

Düğmenin kendisi:

```jsx
<button
  type="button"
  className={live ? "composer__send composer__send--ready" : "composer__send"}
  disabled={!live}
  /* The word is gone from the face, so the name is written where it can still be read: aria-label
     for a screen reader, title for a mouse resting on it. With aria-label set, the name is not
     computed from what is inside, so the mark cannot leak into it. */
  aria-label={running ? "Stop" : action}
  title={running ? "Stop" : action}
  /* Split above submit rather than inside it: submit owns the draft's rules and has no
     reason to learn about stopping. */
  onClick={running ? onStop : submit}
>
  {running ? STOP : SEND}
</button>
```

`live`, `ready`, `submit`, `onKeyDown` — hiçbirine dokunulmuyor.

Dosyanın başındaki açıklamada `Send` diyen iki cümle var. İkisi de doğruluğunu koruyor
*(`action` hâlâ kelime, ayaktaki sıra hâlâ Skills · model · gönder)* ama artık ekranda o kelime
görünmediği için ikincisi *"Send"* yerine gönderme düğmesinden söz edecek şekilde düzeltiliyor —
**CLAUDE.md:** bir açıklama yalnız bugün doğru olanı söyler.

*Yeşile döner:* `Composer.test.jsx`'in beş kırmızısı, `ChatScreen.test.jsx`'in ikisi,
`ProjectScreen.test.jsx`'in biri. Sekiz.

### 2. `workspace.css` — `.composer__send` sabit kare olur

```css
/* An icon rather than a word, so the box stops being as wide as its label. Fixed, because the two
   marks are not the same width and the row would shift the moment an answer started running. The
   size is the pickers' beside it. */
.composer__send {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-control);
  font-family: inherit;
  font-size: 16px;
  line-height: 1;
  background: #e5dfd5;
  color: #a79e93;
  cursor: not-allowed;
}
```

Giden üç satır: `padding: 8px 16px` (kare kendi ölçüsünü söylüyor), `font-weight: 500` (bir
işaretin ağırlığı yok), `font-size: 13.5px` → `16px` (kelime ölçüsü tek işaret için küçük).

`.composer__send--ready` ve `:hover` **olduğu gibi kalıyor**.

*Yeşile döner:* `workspace.css.test.js`'in bir kırmızısı — dokuzuncu.
*Yeşil kalır:* aynı dosyanın `--radius-control` testi, ve `app.css.test.js`'in `--accent-hover`
testi.

### 3. `dist` derlenir

`npm run build --prefix queen-agent/frontend`, kaynakla **aynı commit'e**.

## Beklenen yeşil

Ön yüzde **507**. Arka uçta **2 failed, 442 passed** — ikisi defterin dalı.

**Bu maddenin asıl sınavı düşmeyen testler:**

| Ne | Kaç | Neyi kanıtlıyor |
|---|---|---|
| `Composer.test.jsx` — `draw()`'a dayananlar | 10 | Ad `Send` olarak duruyor |
| `App.test.jsx` — `Start` ve `Stop`'a basanlar | 2 | Ad uçtan uca duruyor |
| `ChatScreen.test.jsx` — 67'nin durdurma testleri | 2 | Durdurma çalışıyor |
| `NoProjectsScreen.test.jsx` — orada `Send` yok | 1 | Düğme kaçmadı |

Biri düşerse ad gerçekten kaybolmuş demektir, ve o zaman **kod düzelir, test değil**.

## Bilerek yapılmayanlar

- **`action` prop'u kalkmıyor.** Kelime ekrandan gitti ama addan gitmedi: proje ekranı `Start`,
  sohbet `Send` diyor, ve ikisi farklı şeyler açıyor.
- **İşareti gizleyen bir sarmalayıcı yok.** `aria-label` varken ad hesabı içeriye bakmıyor; `span`
  ile `aria-hidden` eklemek hiçbir şeyi değiştirmezdi.
- **`ChatScreen`, `ProjectScreen`, `App` açılmıyor.** Üçü de `action` veriyor ve o değişmedi.
- **Başka düğmeye dokunulmuyor.** `Try again`, `New chat`, onay kutusu — hepsi kelime kalıyor.
