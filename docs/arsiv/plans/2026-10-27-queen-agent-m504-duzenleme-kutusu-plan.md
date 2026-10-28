# Madde 504 — Düzenleme kutusu büyür, plan

**Hedef:** Düzenlenen sorunun kutusu sohbetin genişliğinde açılıyor, yazısı kadar uzun; yazdıkça
büyüyor, pencerenin %40'ında duruyor ve içinde kayıyor.

**Spec:** [m504](../specs/2026-10-27-queen-agent-m504-duzenleme-kutusu-design.md)

## Kısıtlar

- Büyüme tek parça: `shared/useGrowingField.js`; 505 yazma kutusuna aynısını bağlar.
- Yazma kutusu (`Composer`) bu maddede değişmez.
- Üst sınır CSS'te (`max-height: 40vh`), en alt sınır `rows`.
- Önce test kırmızı, sonra kod.

### Görev 1: Hook'un testleri kırmızı

**Dosya:** `queen-agent/frontend/src/shared/useGrowingField.test.jsx` (yeni)

- [ ] `scrollHeight`, `clientHeight` (`Element.prototype`) ve `offsetHeight` (`HTMLElement.prototype`)
  getter'ları `vi.spyOn` ile bildirilir; `afterEach` geri alır.
- [ ] Kutu yazısı kadar uzun, kenarlıklar dahil: 120 + (50 − 48) → `122px`.
- [ ] Yazı değişince yeniden ölçülür: uzar, kısalır.
- [ ] `scrollHeight` 0 → yükseklik `auto` kalır.
- [ ] `scrollHeight` okunurken `overflowY` `"hidden"`, sonra `""`.
- [ ] `npm test --prefix queen-agent/frontend -- useGrowingField` — kırmızı (dosya yok).

### Görev 2: Hook

**Dosya:** `queen-agent/frontend/src/shared/useGrowingField.js` (yeni)

- [ ] `useGrowingField(field, value)`: `useLayoutEffect`, `[field, value]`. `height = "auto"` →
  `overflowY = "hidden"` → `scrollHeight` ve kenarlığı oku → `overflowY = ""` → `scrollHeight` 0
  değilse `height = scrollHeight + offsetHeight − clientHeight`.
- [ ] Görev 1'in testleri yeşil.

### Görev 3: Düzenleme kutusu

**Dosyalar:** `queen-agent/frontend/src/features/workspace/EditMessage.jsx`, `EditMessage.test.jsx`

- [ ] Test: açılışta kutunun yüksekliği yazısının boyu (kırmızı).
- [ ] `useRef` ile `field`, `useGrowingField(field, draft)`, `ref={field}`; `rows={2}` kalır.

### Görev 4: CSS

**Dosyalar:** `queen-agent/frontend/src/features/workspace/workspace.css`, `workspace.css.test.js`

- [ ] Test: `.msg__editing` `width: 100%`, `max-width: 78%` yok; `.msg__editing-input`
  `max-height: 40vh` (kırmızı).
- [ ] `.msg__editing`: `max-width: 78%` → `width: 100%`, yorum kullanıcının 27 Ekim kararını söyler.
- [ ] `.msg__editing-input`: `max-height: 40vh`.

### Görev 5: Dist, takımlar, yol haritası

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] `npm test --prefix queen-agent/frontend` — yeşil.
- [ ] `python -m pytest queen-agent -q` — dist testi dışında yeşil (commit'e kadar beklenen).
- [ ] Yol haritasında 504 ✅, başlık "3/5 bitti". Commit'i ana ajan atar.
