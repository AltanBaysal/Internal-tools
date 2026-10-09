# Madde 449 — Kopan bağlantıdan sonra Try again, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** sorunun sunucuya ulaştığı bir kopuşta Try again soruyu yeniden yazmaz, kayıttaki soruyu
cevaplatır; ulaşmadığı kopuşta bugünkü gibi metniyle gönderir.

**Yaklaşım:** önce testler, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m449](../specs/2026-10-09-queen-agent-m449-kopan-baglanti-design.md)

## Her yere geçerli kurallar

- Kod, yorum ve test adları İngilizce.
- Arka uç, `sse.js`, `ChatScreen.jsx`, `Composer.jsx` ve queen-editor değişmez.

---

## Görev 1: testler — `App.test.jsx`

- [ ] `stubTurn(server, ...streams)`: her POST sıradaki akışı alır, sonuncusu tekrarlanır; bugünkü
  çağrılar tek akışla aynı kalır.
- [ ] `droppingSse(first)`: ilk okumada `first`, ikincide `TypeError("network error")`.
- [ ] İlk olaydan sonra kopan akış: soru bir kez, kart *"network error"*, kutu boş; Try again
  `{chat: "c1", mode: "edit"}` gönderir; cevap gelir, soru yine bir kez.
- [ ] Taslakta kopan akış: adres `/p/p1/c/c1`'e geçer, Try again `{chat: "c1", mode: "edit"}`.
- [ ] Kopmadan önce gelen `error` olayı kartta kalır, *"network error"* görünmez.
- [ ] İlk olaydan önce düşen `fetch`: balon çıkar, kutuda cümle, Try again cümleyi metniyle gönderir.
- [ ] Kırmızı görülür (yeni yolun üç testi; dördüncüsü bugünkü davranışı tutar, yeşil).

## Görev 2: `useChat.js`

- [ ] `send`'de yerel `reached`, `chat` olayında doğru — sahiplik kapısından önce.
- [ ] `catch`: `reached` ise balon kalır, `setError((current) => current ?? failure.message)` turun
  sohbetindeyse, fırlatılmaz; değilse bugünkü kol. Yorumlar ikisinin nedenini söyler.
- [ ] `retry`'ın yorumu kopan turu anar. Testler yeşil.

## Görev 3: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
