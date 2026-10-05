# QueenAgent — Yol Haritası v10

**Tarih:** 2026-10-05 · **Koşu dalı:** `feat/queenagent-v10` · **Durum:** 0/1
**Öncesi:** [v9](2026-09-25-queen-agent-v9-roadmap.md) — 50/50 kapandı ve main'e birleşti.
**Kaynak:** v10-1 kullanıcının 5 Ekim'deki sözlerinden doğdu. Aynı iş queen-editor'de
[v9-3](2026-10-05-queen-editor-v9-roadmap.md).

**Tasarıma dokunan her madde tasarımcının listesine girer**, liste koşudan önce tasarımcıya gider,
ve koşu gelen yeni tasarımı kullanır — v9'daki kural. **Liste:** (1) kutunun denemelerinin ekranda
görünmesi — v10-1.

---

| # | İş | Bitti sayılır |
|---|---|---|
| v10-1 | `ALIGNED` **Agent'ın DeepSeek'e attığı her istek bir kara kutudan geçecek: hata ya da ret gelirse istek yeniden gönderilir.** *(Kullanıcı, 5 Ekim — "Deepseek kontrol katmanı ekle cevaba bak red ise tekrar gönder", "bu queen agenta da gidecek galiba iki modelede gideek gibi", "quuenagentıada roadmap aç onada yaz deepseek kontrol katmanı olayını".)* **İki araç için bir arada hizalandı**, queen-editor'ün [v9-3](2026-10-05-queen-editor-v9-roadmap.md)'ünde *(kullanıcı, 5 Ekim — "aynısı queen agenttada oluca")*: kutunun akışı, beş deneme, ve beşi de olmazsa dönen mesaj orada. **QueenAgent'ta:** agent'ın döngüsü isteğini kutuya atar, kutu ona her seferinde bir cevap döner — onaylanmış cevap, ya da beş denemeden sonra kutunun mesajı —, ve döngü kırılmaz *(kullanıcı — "yani agetna bir şye dönsün yoksa agentic döngü kırılır")*. **Cevap onaylanınca tek seferde görünür** *(kullanıcı, Claude'un önerisini seçerek — "evet zaten şuan adım adım yazma olayını ui da kapattık diye iliyorum bakarsın sen")*: bugün cevap gelirken canlı yazılıyor *([ChatScreen.jsx](../../../queen-agent/frontend/src/features/workspace/ChatScreen.jsx)'in `streamingText`'i)*; kutu cevabı onaylanınca tek parça verdiği için ekran o zamana kadar üç noktayı, sonra cevabın tamamını gösterir. **Denemeler ekranda görünür** *(kullanıcı — "queen agentta görünsünde")*: nasıl görüneceği tasarımcıdan gelir — yukarıdaki listede (1). **Kontrolün DeepSeek'e giden metni** queen-editor'ün v9-3b'sindekiyle aynı, ve QueenAgent'ın modele giden metinleri gibi **commit'lenmeden kalır**: kullanıcı VS Code'un Changes'inde okur, ve onayıyla commit'lenir *(kullanıcı, 30 Eylül — "commitleme yani ben onayı verince commitlenecek")*. | Agent'ın DeepSeek'e attığı her istek kutudan geçiyor. DeepSeek reddedince ya da HTTP hatası gelince istek yeniden gidiyor, ve denemeler ekranda tasarımın gösterdiği gibi görünüyor. Cevap onaylanınca tek seferde görünüyor. Beş deneme de başarısızsa döngü kırılmıyor: kutunun mesajı agent'a cevap olarak dönüyor — retse *"Model hata döndü, farklı şekilde dene"*, teknik hataysa hatanın kendi metni. |
