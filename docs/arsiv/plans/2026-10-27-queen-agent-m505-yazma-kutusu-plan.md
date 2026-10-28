# Madde 505 — Yazma kutusu büyür, plan

**Hedef:** Yazma kutusu yazı uzadıkça büyüyor, pencerenin %40'ında durup içinde kayıyor, gönderince
2 satıra dönüyor; dibi izleyen okur kutu büyürken son satırları görmeye devam ediyor.

**Spec:** [m505](../specs/2026-10-27-queen-agent-m505-yazma-kutusu-design.md)

## Kısıtlar

- Büyüme 504'ün `useGrowingField`'ı; ikinci bir ölçen parça yok.
- `40vh` stilde tek yerde, iki kutunun ortak kuralında.
- Önce test kırmızı, sonra kod.

### Görev 1: Hook genişlik değişince yeniden ölçer

**Dosyalar:** `queen-agent/frontend/src/shared/useGrowingField.js`, `useGrowingField.test.jsx`

- [ ] Testler (`ResizeObserver`, `requestAnimationFrame` sahte): genişliği değişen kutu yazısı aynıyken
  yeniden ölçülüyor; yalnız yüksekliği değişen kutu ölçülmüyor (kırmızı).
- [ ] Ölçüm `fit(element)`'e çıkar; `useLayoutEffect` `[field, value]` onu çağırır.
- [ ] `useEffect` `[field]`: kutuya `ResizeObserver`; `contentRect.width` son görülenden farklıysa
  sakla, 0 değilse `requestAnimationFrame(() => fit(element))`; temizlikte `disconnect` ve
  `cancelAnimationFrame`.

### Görev 2: Yazma kutusu

**Dosyalar:** `queen-agent/frontend/src/features/workspace/Composer.jsx`, `Composer.test.jsx`

- [ ] Test: taslak uzayınca uzuyor; gönderince `rows` boyuna dönüyor (kırmızı).
- [ ] `useGrowingField(field, draft)`; gizlenip gösterilen kutuyu hook'un genişlik gözlemi ölçüyor.

### Görev 3: Ortak sınır

**Dosyalar:** `queen-agent/frontend/src/features/workspace/workspace.css`, `workspace.css.test.js`

- [ ] Test: `max-height: 40vh`, `.msg__editing-input,\n.composer__input {` kuralında (kırmızı).
- [ ] `max-height: 40vh` `.msg__editing-input`'tan ortak kurala taşınır.

### Görev 4: Liste dibi izler

**Dosyalar:** `queen-agent/frontend/src/features/workspace/ChatScreen.jsx`, `ChatScreen.test.jsx`

- [ ] Testler (`ResizeObserver` sahte): liste kısalınca dibi izleyen okur dipte; yukarıdaki okur
  yerinde (kırmızı).
- [ ] `useEffect`, `[missing]`: listeye `ResizeObserver`, `following` ise `toBottom`; yoksa hiçbir şey.

### Görev 5: Dist, takımlar, yol haritası

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] `npm test --prefix queen-agent/frontend` — yeşil.
- [ ] `python -m pytest queen-agent -q` — dist testi dışında yeşil.
- [ ] Yol haritasında 505 ✅, başlık "4/5 bitti". Commit'i ana ajan atar.
