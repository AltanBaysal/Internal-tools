# Madde 209 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-10-queenagent-m209-surum-uygulama-design.md](../specs/2026-09-10-queenagent-m209-surum-uygulama-design.md)
**Test turu:** `e45391b`.

**Amaç:** dört kırmızı kapansın, ve kenar çubuğunda `QueenAgent` yazısının altında `V8` okunsun.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- **`dist` aynı commit'e girer.** CLAUDE.md: notebook depoyu klonluyor ve hiç derlemiyor, yani
  derlenmemiş bir ön uç değişikliği bitmiş değil.
- **Sürüm elle yazılır.** Derleme tarihi, `package.json` sürümü ya da git etiketi değil — üçü de
  başka bir ritme bağlı.
- Commit mesajında çift tırnak yok; amend yok.

## Değişen dosyalar

| Dosya | Sorumluluğu |
|---|---|
| `queen-agent/frontend/src/shared/version.js` | yeni — hangi koşu çalışıyor, tek olgu |
| `queen-agent/frontend/src/features/workspace/Sidebar.jsx` | onu adın altında gösterir |
| `queen-agent/frontend/src/features/workspace/workspace.css` | sütun ve not sesi |
| `queen-agent/frontend/dist/**` | derlenmiş hâli |

---

## Görev 1 · Sabit

**Dosya:** `queen-agent/frontend/src/shared/version.js` *(yeni)*

- [ ] **1.1**

```js
/** Which run of QueenAgent this is (Madde 209).
 *
 * Written by hand, because it is a decision rather than a fact anything else already holds: a run
 * opens, the number moves, and nothing in a build or a commit knows that happened. The date the
 * bundle was built, the version in package.json and a git tag all answer other questions on other
 * rhythms, and none of them says V8.
 *
 * Its own module rather than a line inside the sidebar: the sidebar draws it, it does not own it,
 * and whoever opens the next run should find this without reading a component.
 */
export const VERSION = "V8";
```

**Kapanan test:** `version.test.js`'in biçim iddiası, ve `Sidebar.test.jsx`'in çözümlenmesi.

---

## Görev 2 · Çubuk

**Dosya:** `queen-agent/frontend/src/features/workspace/Sidebar.jsx`

- [ ] **2.1 — içeri alma**

`import Menu from "./Menu.jsx";` satırının üstüne, alfabetik sırayla:

```jsx
import { VERSION } from "../../shared/version.js";
import Menu from "./Menu.jsx";
```

- [ ] **2.2 — marka bloğu**

```jsx
      <div className="sidebar__brand">
        {/* The name and the run number are one block so the version sits under the wordmark rather
            than beside it: the brand row itself is a row, and the fold button lives at its end. */}
        <div className="sidebar__name">
          <span className="sidebar__wordmark">QueenAgent</span>
          <span className="sidebar__version">{VERSION}</span>
        </div>
        <Fold onToggle={onToggle} />
      </div>
```

Katlanmış dal **açılmaz**: erken dönüyor, yani sürüm orada zaten çizilmiyor.

**Kapanan testler:** `the sidebar says which run this is`, `folded, the version folds with the name`.

---

## Görev 3 · İki kural

**Dosya:** `queen-agent/frontend/src/features/workspace/workspace.css`

- [ ] **3.1**

`.sidebar__wordmark` kuralının hemen altına:

```css
/* The name and the run number, stacked: the brand row above is a row, and the fold button ends it. */
.sidebar__name {
  display: flex;
  flex-direction: column;
}

/* The wordmark's footnote rather than a second name: the repo's note voice, and small enough that
   the eye reads it after the name. Letter-spaced because two characters set solid under a 21px
   name read as a smudge. */
.sidebar__version {
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 1.2px;
}
```

**Kapanan test:** `the version sits under the name and reads as a note`.

---

## Görev 4 · Süit, derleme, commit

- [ ] **4.1 — ön uç:** `npm test --prefix queen-agent/frontend` → tamamı yeşil.
- [ ] **4.2 — arka uç:** `python -m pytest queen-agent -q` → 923 yeşil.
- [ ] **4.3 — derleme:** `npm run build --prefix queen-agent/frontend`.
- [ ] **4.4 — commit**, kaynak ve `dist` birlikte:

```
feat(m209): the sidebar says which run this is
```

---

## Görev 5 · Yol haritası

- [ ] **5.1**

209 satırı `kapandı` olur ve hash'ini alır. Koşunun kapanış paragrafı: **yirmi maddenin hepsi**
kapandı.

- [ ] **5.2 — commit**

```
docs(v8): 209 closes, and with it the run
```

---

## Kendi kontrolü

- **Spec'in her parçası bir göreve düşüyor mu?** Sabit → 1; marka bloğu → 2; iki kural → 3;
  derleme kuralı → 4.3.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** `VERSION` *(1.1'de doğuyor, 2.1'de okunuyor)*, `.sidebar__name` ve
  `.sidebar__version` *(2.2'de çiziliyor, 3.1'de stillenip testte tutuluyor)*.
- **Test turunun beklediği dizgeler:** `flex-direction: column`, `color: var(--muted)`,
  `font-size: 11px` — üçü de 3.1'de yazılı.
