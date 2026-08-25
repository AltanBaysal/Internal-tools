# Madde 67 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-25-queenagent-m67-durdurma-uygulama-design.md](../specs/2026-08-25-queenagent-m67-durdurma-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

**1. `memory_stops.py` — kaydın gövdesi.** Üç yol da kilit altında; anahtar `(proje, sohbet)`.

**2. `stream_answer` — kaydı alır ve ona bakar.** Parametre zorunlu. Her parçadan **önce** bakılır;
işaretliyse yayma durur ve döngüden çıkılır. Ne söylendiyse yazılır ve mesaj durdurulmuş
işaretlenir. Saklanacak bir şey yoksa mesaj yazılmaz ama **sohbet yine de yayılır** — akış her zaman
kayıtla kapanır. Kayıt `finally` içinde temizlenir: cevap hataya düşse de bayrak kalmaz.

**3. `append_message` — `stopped` alır.** `calls` gibi, varsayılanı yanlış.

**4. `file_chat_store` — yazar ve okur.** `stopped` yalnız doğruyken yazılır; okurken yoksa yanlış.

**5. `routes.py` — uç nokta ve iki geçirme.** Blueprint bir parametre daha alır. `POST .../stop`
olmayan sohbette 404, varsa kaydı işaretler. `stream_answer`'a kayıt geçirilir. Mesajın JSON'una
`stopped` eklenir — diskin aksine **her zaman** var, tarayıcı alanın varlığını sınamak zorunda
kalmasın.

**6. `main.py` — tek kayıt kurulur** ve blueprint'e verilir.

**7. `test_chats_api.py`'nin `_client`'ı** kaydı geçirir. Test turunda bilerek ertelenmişti: imza
yokken geçirmek bütün API testlerini `TypeError`'a düşürürdü.

**8. `useChat` — `stop` ve `stopped`.** `stop` uç noktaya gider ve hâli kurar; otomatik istek
efekti hâle bakar; `send` hâli kaldırır.

**9. `App.jsx`** durdurmayı ekrana geçirir.

**10. `ChatScreen`** cevap akarken composer'ın alt satırına durdurma düğmesini koyar; durdurulmuş
mesaj kendi işaretini alır.

**11. `workspace.css`** — düğme ve işaret. Vurgu yok, kırmızı yok.

**12. İki suite koşulur · 13. `dist` derlenir · 14. Commit.**

## Beklenen yeşil

`python -m pytest queen-agent -q` → 417 · `npm test --prefix queen-agent/frontend` → 485.

**Otuz iki mekanik kırmızının hepsi dönmeli.** Dönmeyen olursa imza yüzünden değil, gerçekten
kırıldığı içindir — test turunun planı bu ayrımı yazmıştı, burası onun karşılığı.

## Bu turda yapılmayan

Durdurulan cevaba devam etmek · sohbetten çıkmanın turu bitirmesi · token sayacı *(Madde 68)*.
