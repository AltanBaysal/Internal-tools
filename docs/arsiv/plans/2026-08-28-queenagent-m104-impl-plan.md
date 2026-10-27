# Madde 104 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m104-taslak-isinlanmasi-uygulama-design.md](../specs/2026-08-28-queenagent-m104-taslak-isinlanmasi-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `useChat.js` — yükleme etkisinin erken dönüşü

```js
  useEffect(() => {
    if (!projectId || !chatId) return undefined;
```

olur:

```js
  useEffect(() => {
    // No chat at this address: the draft, or no chat screen at all. Dropped rather than kept -- a
    // held record is the chat that was left, the draft's first bubble lands on it, and the birth
    // then shows that transcript at the newborn's address (Madde 104).
    if (!projectId || !chatId) {
      setChat(null);
      setError(null);
      setMissing(false);
      return undefined;
    }
```

## B. Doğrulama ve kapanış

1. İki suite koşulur; 104'ün kırmızısı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `npm run build --prefix queen-agent/frontend` — `dist` kaynakla aynı commit'e girer.
3. Commit: kod + dist + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **`send`, `born`, `streamingInto`, tur sonu okuması ellenmez.**
- **Akış durumu sohbete anahtarlanmaz** — Madde 106.
- **Test dosyaları değişmez.**
