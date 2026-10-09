# Madde 348 — Mesajın altındaki notlar tek satırda · uygulama turu

**Kaynak:** [yol haritasının 348'i (v9-2e)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m348-mesaj-alti-testler-design.md) ve kırmızı commit'i
`d7159f52`. Tasarım: 139 — `DESIGN-STANDARD.md`'nin *The notes under a message*'ı, `shell.js`'in
`stamp`'i ve `liveStrip`'i, `kit.css`'in `.msg__stamp`'i.

**Kullanıcıdan gereken:** hiçbir şey.

## Yaklaşım

Üç yol vardı:

1. **`Stamp` çocuk alır** — sözlerinin `span`'ından sonra ona verilen neyse onu çizer. ChatScreen
   sorunun `MessageFoot`'unu `Stamp`'in içine koyar, `MessageFoot` kendi `div`'ini bırakıp parçalarını
   doğrudan verir. **Seçilen.** `Stamp` sürümü ve kalemi bilmez; kalemin kimde olacağına bugün olduğu
   gibi ChatScreen karar verir, ve 344'ün dosyaları yerinde kalır.
2. `Stamp` `standing`, `onVersion`, `onEdit` alır ve `MessageFoot`'u kendisi çağırır. `Stamp` bir
   sorunun ne olduğunu öğrenir; cevabın satırı da bu üç propu taşır — gereksiz bir bağ.
3. `Versions` ve kalem `Stamp.jsx`'e taşınır, `MessageFoot.jsx` silinir. Daha çok hareket, 344'ün
   bölüşünü bozar; kazancı yok.

## Değişenler

- **`Stamp.jsx`:** `Stamp({ at, usage, children })` — `div.msg__stamp` içinde önce sözlerin `span`'ı
  (saat, ölçülmüşse ` · N tokens` — sayının biçimi değişmez, `cached`/`missed` v9-2k'nin), sonra
  `children`. `at` yoksa bugünkü gibi hiçbir şey. `LiveStrip({ at, round, of, tokens })` — ilk `span`
  `at` varken `${clockTime(at)} · ` ile başlar; yoksa bugünkü gibi `round`'la.
- **`MessageFoot.jsx`:** `MessageFoot` `div.msg__foot`'u bırakır, bir fragment döner: `Versions`, sonra
  kalem. Boşken bugünkü gibi hiçbir şey çizmez — `Versions` null, kalem yok.
- **`ChatScreen.jsx`:** sorunun metninin altındaki `MessageFoot` bloğu kalkar, `Stamp`'in çocuğu olur
  (kalemin yorumu onunla taşınır); iki `LiveStrip`'e `at={askedAt}`. Sıra tasarımınki olur: metin,
  `Stopped`, dosya kartları, satır.
- **`workspace.css`:** `.msg__stamp`'e `display: flex`, `align-items: center`, `gap: 6px`;
  `.msg__stamp--live`'da yalnız `gap: 7px` kalır (flex artık satırın kendisinin); `.msg__foot` kuralı
  kalkar. Kalemin ve `.versions`'ın kuralları yerinde.

Kod dosyası eklenmez, silinmez: CODE-STANDARD'ın tabloları değişmez. Ön uç yalnız görünüşü değiştirir
(FOUNDATION, 4. karar); sunucuya dokunulmaz.

## Nasıl görülür

Dört satır, paralel, yeşil. Tarayıcıda: düzenlenmiş bir sorunun altında `11:04 ‹ 2/2 › ✎` tek satırda,
sağa yaslı; cevap sürerken satır `14:32 · round 2/16 · 3.4k tokens · ◌ Pondering…`.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m348-mesaj-alti-uygulama-plan.md).
