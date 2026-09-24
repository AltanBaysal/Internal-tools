# QueenAgent — Yol Haritası v9

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queenagent-v9` · **Durum:** 0/1
**Öncesi:** [v8](2026-09-06-queen-agent-v8-roadmap.md) — kapandı ve `356d605` ile main'e alındı.
**Kaynak:** 334 kullanıcının 24 Eylül'deki sözlerinden doğdu.

**Numaralar 24 Eylül'de birer kaydı:** DeepSeek maddesi en başa, 1 olarak girdi *(kullanıcı — "ilk
madde olarak ekle, son değil")*. Bugünkü 2–7 o güne kadar 1–6'ydı; aşağıdaki alıntılarda geçen
numaralar söylendikleri günün numaraları.

**2 ve 3 koşulmadan backlog'a döndü** *(kullanıcı, 24 Eylül — "Playwringi backloga koy şimdilik gerek
yok")*: Playwright MCP'nin bu depodaki ayarı ve QueenAgent'ın onunla kontrolü, konuşulan kararlarıyla
birlikte [BACKLOG.md](../../../queen-agent/BACKLOG.md)'de. Numaraları boş kaldı — alıntılardaki
numaralar kaymasın diye.

**4, 6 ve 7 de koşulmadan backlog'a döndü** *(kullanıcı, 24 Eylül — "bunları backloga al")*, **5
de ardından** *("o da backloga gitsin abi")* — 5 4'ün sade formatına yazıyordu. Sade senaryo formatı,
compilation skill'i, referanstan video prompt'ları ve *Edit prompts*'un sade formatı düzenlemesi,
konuşulan kararlarıyla birlikte [BACKLOG.md](../../../queen-agent/BACKLOG.md)'de. Numaraları da boş
kaldı.

**Belge `feat/queen-editor-v6` dalında yazıldı** *(kullanıcı, 21 Eylül — "sen bu dalda oluştur
roadmapi sıkıntı yok")*. Başlıktaki dal koşunun dalı; yazıldığı yer başka.

**Neden ayrı belge.** İş [Queen Editor v7](2026-09-21-queen-editor-v7-roadmap.md)'nin referans
maddelerine bağlı — prompt'u QueenAgent yazıyor, videoyu queen-editor üretiyor. Kullanıcı ikisinin
tek koşuda birleşmesini değil, **ayrı belge ve ayrı dal** istedi *(21 Eylül — "Ayrı bir QueenAgent v9
yol haritası. Kendi belgesi, kendi dalı (feat/queenagent-v9), ayrı koşulur.")*.

**Numara koşu açılırken verildi: 1 → 334.** Belge yazılırken kendi numaralarını taşıyordu, ortak
sayacınkini değil *(kullanıcı kararı, 21 Eylül)*; yukarıda geçen 2–7 o numaralar. Sebebi
[v7](2026-09-21-queen-editor-v7-roadmap.md)'nin başlığında yazılı: aynı gün koşan bir yol haritası
madde eklemeye devam etti ve bu iki belgenin seçtiği aralıkları üç kez aldı.

**Koşulacak sıra bu dosyanın sırası.**

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**334 hepsinden önce koşulacaktı** *(kullanıcı, 24 Eylül — "v9'un ilk adımı yap bunu")*: DeepSeek'e
ödeme yapılana kadar QueenAgent'ın DeepSeek modelleri çalışmıyor.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 334 | `ALIGNED` **DeepSeek istekleri şimdilik OpenRouter'dan gidiyor.** *(Kullanıcı, 24 Eylül — "şu anda deepseek'e kredi yükleyemiyorum, deepseek isteğini şimdilik openrouter'a yönlendirebilir miyiz queenagent'ta?"; "bir vendor ile sınırlaman gerek yok deepseek'i"; ne kadar süreceğine: "şimdilik, biz deepseek'e ödeme yapana kadar, şu an çalışmıyor çünkü"; anahtara: "hazır, önceden de kullanmıştık, bulabilirsin bir yerden key'in nasıl olduğunu"; yerine: "v9'un ilk adımı yap bunu", "ilk madde olarak ekle, son değil".)* **Bugün** QueenAgent'ın DeepSeek modelleri DeepSeek'in kendi API'sine gidiyor, ve hesapta kredi olmadığı için cevap gelmiyor. **Olacak:** aynı modeller OpenRouter üzerinden cevap veriyor; menü aynı kalıyor, xAI modelleri değişmiyor. **OpenRouter'da yalnız DeepSeek'in kendisine gidiyor** *(kullanıcı, 25 Eylül — "Deepeseki direkt deepsekiin kendin kullanalım open routerda deepseke biz ödeme yapan kadar olur mu", ardından "yap devam")*: istek başka bir sağlayıcıya geçmiyor, DeepSeek cevap vermezse hata görünüyor. Bu, 24 Eylül'deki *"bir vendor ile sınırlaman gerek yok"* kararının yerine geçiyor. Madde 149'un yolu *(`27ff05d3`, DeepInfra'ya sabitli; bugün kodda yok)* sağlayıcısı DeepSeek olarak geri geliyor, gerekçesiyle birlikte: cevap veren sağlayıcının kullanım şartları geçerli, en az birininki bu işi yasaklıyor, ve DeepSeek'inkiler bugün doğrudan API'de geçerli olanlarla aynı. **Model: iki menü satırı da `deepseek/deepseek-v4.1-flash`** — DeepSeek'in kendi API'si 14 Eylül'den beri iki satıra da V4.1 Flash ile cevap veriyordu *(kullanıcı, 25 Eylül — "şuan deepsek 4.1 flasj kullanıyoruz")*. OpenRouter'da DeepSeek'in fiyatı kendi API'siyle aynı: $0.15 giriş / $0.60 çıkış *(OpenRouter'ın model sayfası, 25 Eylül)*. **Anahtar 149'unki:** `OPENROUTER_API_KEY`, Colab Secrets'ta; kullanıcının anahtarı hazır. **Şimdilik:** DeepSeek'e ödeme yapılınca doğrudan API'ye dönüş ayrı bir madde. **Kullanıcıdan gereken:** anahtarın Colab Secrets'ta ve yerel çalıştırmada tanımlı olması. | Bir DeepSeek modeli seçilip yazılan mesaj OpenRouter'dan cevap alıyor; xAI modelleri bugünkü gibi çalışıyor. |
