# QueenAgent — Yol Haritası v9

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queenagent-v9` · **Durum:** 0/7
**Öncesi:** [v8](2026-09-06-queen-agent-v8-roadmap.md) — kapandı ve `356d605` ile main'e alındı.
**Kaynak:** 4, 6 ve 7 kullanıcının 21 Eylül'deki sözlerinden doğdu. 5
[BACKLOG.md](../../../queen-agent/BACKLOG.md)'den geliyor; ne yaptığı aynı gün konuşuldu. 2 ve 3
kullanıcının 23 Eylül'deki sözlerinden doğdu, 1 de 24 Eylül'dekilerden.

**Numaralar 24 Eylül'de birer kaydı:** DeepSeek maddesi en başa, 1 olarak girdi *(kullanıcı — "ilk
madde olarak ekle, son değil")*. Bugünkü 2–7 o güne kadar 1–6'ydı; aşağıdaki alıntılarda geçen
numaralar söylendikleri günün numaraları.

**Belge `feat/queen-editor-v6` dalında yazıldı** *(kullanıcı, 21 Eylül — "sen bu dalda oluştur
roadmapi sıkıntı yok")*. Başlıktaki dal koşunun dalı; yazıldığı yer başka.

**Neden ayrı belge.** İş [Queen Editor v7](2026-09-21-queen-editor-v7-roadmap.md)'nin referans
maddelerine bağlı — prompt'u QueenAgent yazıyor, videoyu queen-editor üretiyor. Kullanıcı ikisinin
tek koşuda birleşmesini değil, **ayrı belge ve ayrı dal** istedi *(21 Eylül — "Ayrı bir QueenAgent v9
yol haritası. Kendi belgesi, kendi dalı (feat/queenagent-v9), ayrı koşulur.")*.

**Numaralar bu belgenin kendi numaraları — ortak sayacın değil.** *(Kullanıcı kararı, 21 Eylül.)*
**Gerçek numaralar koşu açılırken verilir**, ve o andan sonra kimlik onlardır. Sebebi
[v7](2026-09-21-queen-editor-v7-roadmap.md)'nin başlığında yazılı: aynı gün koşan bir yol haritası
madde eklemeye devam etti ve bu iki belgenin seçtiği aralıkları üç kez aldı.

**Koşulacak sıra bu dosyanın sırası.**

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**1 hepsinden önce koşulur** *(kullanıcı, 24 Eylül — "v9'un ilk adımı yap bunu")*: DeepSeek'e
ödeme yapılana kadar QueenAgent'ın DeepSeek modelleri çalışmıyor. **2 ondan sonra, ötekilerden önce
koşulur** *(kullanıcı, 23 Eylül — "madde 1 yap böylece diğer maddelerde queen agentta playwright
mcpyi kullanabiliriz")*: ötekiler Playwright MCP'yi kullanabilsin diye. **3 hemen ardından gelir**
*(kullanıcı, 23 Eylül — "evet")*: QueenAgent'ı tarayıcıda kullanmanın önünde bir engel varsa 4–7
başlamadan kalkar.

**4–7 21 Eylül'de konuşuldu ve dördü de kapandı.** 6 aynı gün bir kez daha ele alındı
*(kullanıcı — "yine ayrıca konuşuruz, direkt kapatma", ardından "alalım, tam hazır olsun
roadmapler")*: açık kalan tek yeri, skill'in referansları nereden bildiği, o konuşmada karara
bağlandı.

**4, 5–7'nin temeli.** 5 ve 6 onun formatına yazıyor, 7 o formatı düzenliyor.

**5 ve 6 skill seçicisine birer satır ekliyor**, yani aynı üç dosyaya dokunuyorlar. Hangisi önce
koşarsa ikincisi onun bıraktığı listeye eklenir; sıra bu yüzden önemli değil, ama ikisi aynı anda
koşulmaz.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 1 | `ALIGNED` **DeepSeek istekleri şimdilik OpenRouter'dan gidiyor.** *(Kullanıcı, 24 Eylül — "şu anda deepseek'e kredi yükleyemiyorum, deepseek isteğini şimdilik openrouter'a yönlendirebilir miyiz queenagent'ta?"; "bir vendor ile sınırlaman gerek yok deepseek'i"; ne kadar süreceğine: "şimdilik, biz deepseek'e ödeme yapana kadar, şu an çalışmıyor çünkü"; anahtara: "hazır, önceden de kullanmıştık, bulabilirsin bir yerden key'in nasıl olduğunu"; yerine: "v9'un ilk adımı yap bunu", "ilk madde olarak ekle, son değil".)* **Bugün** QueenAgent'ın DeepSeek modelleri DeepSeek'in kendi API'sine gidiyor, ve hesapta kredi olmadığı için cevap gelmiyor. **Olacak:** aynı modeller OpenRouter üzerinden cevap veriyor; menü aynı kalıyor, xAI modelleri değişmiyor. **Tek bir sağlayıcıya bağlanmıyor:** OpenRouter DeepSeek'i hangi sağlayıcıdan uygun bulursa oradan veriyor. **Bu, madde 149'dan bilerek bir ayrılış:** 149 aynı modelleri OpenRouter'dan **DeepInfra'ya sabitleyerek** sunmuştu, çünkü cevap veren sağlayıcının kullanım şartları geçerli ve en az birininki bu işi yasaklıyor *(`27ff05d3`)*. Sabitsiz yolda bir istek o sağlayıcıya düşüp reddedilebilir; kullanıcı sabitlememeyi seçti. 149'un yolu bugün kodda yok. **Anahtar 149'unki:** `OPENROUTER_API_KEY`, Colab Secrets'ta; kullanıcının anahtarı hazır. **Şimdilik:** DeepSeek'e ödeme yapılınca doğrudan API'ye dönüş ayrı bir madde. **Kullanıcıdan gereken:** anahtarın Colab Secrets'ta ve yerel çalıştırmada tanımlı olması. | Bir DeepSeek modeli seçilip yazılan mesaj OpenRouter'dan cevap alıyor; xAI modelleri bugünkü gibi çalışıyor. |
| 2 | `ALIGNED` **Playwright MCP bu depoda kullanılacak şekilde ayarlanacak.** *(Kullanıcı, 23 Eylül — "cihazda var bu repoda kullanmak için ayarlanmasını ekle tasklara ve queen agenta ekle".)* **Araç kullanıcı için değil, Claude için:** Claude QueenAgent'ı tarayıcıda kendisi açar, ekran görüntüsünü alır ve arayüzü kullanır. **Örnek [queen-design](../../../../queen-design/.mcp.json)** *(kullanıcı — "sen karar ver queen design ayarı yaptıysa kopyalayabilirsin kullanımı")*: orada aynı iş 22 Eylül'de yapıldı ve denendi. Buradan alınanlar: **ayar depoda durur**, yani depoyu çeken her makinede Claude aynı sunucuyu görür ve yalnız bir kez onaylar; **sürüm sabittir** *(`@latest` değil)*; **tarayıcı arka planda açılır**, pencere görünmez *(kullanıcı — "queen design gibi")*. Cihazda nasıl kurulu olduğu koşuda bulunacak *(kullanıcı — "araştırıp bulursun")*. | Claude Code yeniden açıldığında bu depoda Playwright araçları görünüyor, ve Claude bir sayfayı açıp ekran görüntüsünü alabiliyor. |
| 3 | `ALIGNED` **QueenAgent Playwright MCP ile kontrol edilebilecek.** *(Kullanıcı, 23 Eylül — "queen agent playwright mcp ile kontrol edilebilmek için düzenleme gerekiyorsa onu da ekle".)* **Ne için:** Claude QueenAgent'ı tarayıcıda açıp kullanıcının yerine kullanır ve bakar — *"tasarıma uyuyor mu, beklenen gibi çalışıyor mu"* *(kullanıcı)*. **Açılan QueenAgent bu bilgisayarda yerel olarak çalışanı**, Colab'daki değil *(kullanıcı — "1")*. **Gerçek AI çağrısı yapılabilir** *(kullanıcı — "gerçek ai çağrısı yapma yapabilirsin evet")*: skill denenirken xAI'a istek gider. Kullanmanın önünde bir engel varsa bu maddede kalkar; engel çıkmazsa madde düzenleme yapılmadan kapanır. | Claude yerel QueenAgent'ı Playwright ile açıp bir skill'i baştan sona çalıştırabiliyor ve sonucu ekranda görüyor. |
| 4 | **Sade senaryo formatı.** *(Kullanıcı, 21 Eylül — "yeni json yapısı yapabiliriz senaryo prompt şeklinde çok basit olan", "AI'a alan bırakalım tekte üretmesi için".)* **Bugün** QueenAgent'ın ürettiği her prompt **kod tarafından** kuruluyor: yapı dosyasının karakterleri, kıyafetleri ve mekânları aranıp diziliyor, `BREAK` konuyor, kalite zinciri başa ekleniyor *(`domain/build_prompts.py`)*. **Olacak:** ikinci ve sade bir format — sahneler, her sahnede `senaryo` ve `prompt`. `senaryo` kullanıcının okuması için; `prompt` modelin yazdığı prompt'un kendisi ve **olduğu gibi** listeye giriyor. **Kod hiçbir şey eklemiyor**, kalite etiketlerini de model yazıyor *(kullanıcı kararı, 21 Eylül — "sade yapıda ekstra kod eklemeyelim, kalite promptlarını direkt AI eklesin")*. **Bedeli yazıya geçiyor:** kalite zinciri koda tam da bu yüzden alınmıştı — model şemadan kopyalarken **iki model ailesini karıştıran bir zincir gerçek dosyalara ulaşmıştı** *(madde 110, 166)*. Risk bilerek geri alınıyor. **Start a scenario değişmiyor:** süreklilik zengin yapıyı istiyor, ve QueenAgent bundan sonra **iki formatlı** oluyor. | Sade formatta yazılmış bir dosyadan prompt listesi çıkıyor, prompt'lar dosyada yazdığı gibi; zengin format bugünkü gibi çalışmaya devam ediyor. |
| 5 | **Compilation skill'i.** *(Kullanıcı, 18 Eylül; backlog'dan. Ne yaptığı 21 Eylül'de konuşuldu.)* Skill seçicisine üçüncü satır. **Kullanıcıya iki şey sorar** — konunun ne olacağı ve **kaç sahne** istendiği — ve o kadar kareyi tek seferde üretir. **Süreklilik yoktur:** kareler birbirinin devamı değil, kadro kareden kareye değişir. Konu neyin görüneceğini belirler — *hastane* dendiyse hemşire, doktor, çalışanlar; *30 yaş üzeri gotik kızlar* dendiyse kareler onu taşır. **Her karenin kendi karakteri, tek kullanımlıktır:** tip kareler arasında tekrar etmez, kullanıcının istediği çeşitlilik oradan gelir. **4'ün sade formatına yazar**, yani prompt'u baştan sona model kurar — kalite etiketleri de, iki kişili bir karede `BREAK` de. *Start a scenario*'dan farkı tek cümlede: o **süreklilik** üretir, bu **çeşitlilik**. **Değişen:** [domain/skills.py](../../../queen-agent/backend/features/workspace/domain/skills.py) *(`INSTRUCTIONS`)*, [domain/prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py) *(skill'in metni)*, [skills.js](../../../queen-agent/frontend/src/features/workspace/skills.js) *(`SKILLS`)*; ve bunları çivileyen testler — `test_skills.py`, `skills.test.js`, `SkillPicker.test.jsx`; `dist`. | Konu ve sahne sayısı verilince o kadar sahne çıkıyor, her biri kendi kadrosuyla, ve dosya sade formatta. |
| 6 | **Referanstan video üretimi için prompt'lar — kendi skill'iyle.** *(Kullanıcı, 21 Eylül — "queen agent içinde bir roadmap kaçta kaldıysa referanstan video üretimi adında promptları oluşturmalı o da çünkü", ve "queen agent oluşturucak onun için skill ekleyeceğiz".)* Compilation'ın sorma biçimini ödünç alır — konu ve kaç sahne — ve **4'ün sade formatına** yazar. **Çıkardığı prompt H3'ün REF2VA biçiminde:** altı bölüm — `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` — ve referanslara etiketle atıf: `<Subject N>` *(referanstan soyutlanan görünen şey)*, `<Picture N>` *(kare çıpası)*, `<Video N>` *(kurgu, süreklilik, ritim)*, `<Audio N>` *(ses sinyali)*, tipe göre ayrı ve sıraya göre numaralı. **Kalite etiketi yok:** `score_9_up` SDXL'in dili, H3'ün altı bölümünde anlamsız kelime olur. **Tutarlılığı referans taşır, prompt değil** — karakteri ve mekânı prompt'a yazan yapıya bu yüzden gerek yok. **Kullanıcı elle de yazabilir**, fotoğraf prompt'larında olduğu gibi. **Referansları anlatan kendi dosyası olur.** QueenAgent havuzdaki dosyaları göremez — `IMG_2931.jpg` kimseye bir şey söylemez, referansın ne olduğunu yalnız kullanıcı bilir. Skill ilk seferde sorar, aldığı cevabı bir JSON'a yazar ve sonraki üretimlerde oradan okur; havuz değişince kullanıcı söyler, skill günceller. Dosya tipe göre üç liste tutar — fotoğraflar, videolar, sesler — ve **listedeki sıra etiketin numarasıdır**: `fotograflar`'ın üçüncüsü `<Picture 3>`, `videolar`'ın ilki `<Video 1>`. Ayrı bir numara alanı yoktur; olsaydı sıra ile numara bir gün çelişirdi. **Elle yazılıp denenen prompt'ların bulguları:** [2026-09-24-h3-referans-prompt-bulgulari.md](../research/2026-09-24-h3-referans-prompt-bulgulari.md) — madde koşulurken spec onu okur *(kullanıcı, 24 Eylül — "şu prompt hakkında öğrendiklerimizi queenagent koşusunu yaparken kullanalım", "kaybetmeyelim ilerlememizi")*. Oradan açık kalan: **stil bir seçenek olabilir** *(kullanıcı — "still bir seçenek olabilir")* — skill'in stili sorup sormayacağı koşuda konuşulacak. | Referanslı video için istenen prompt altı bölümü ve etiketleri taşıyarak çıkıyor; queen-editor'ün toplu prompt kutusuna olduğu gibi giriyor. |
| 7 | **Edit prompts sade formatı da düzenler.** *(Kullanıcı, 21 Eylül — "edit prompt zaten senaryo düzenliyor, o yüzden onu da düzeltiriz".)* **Bugün** *Edit prompts* prompt'u değil **yapıyı** düzeltiyor: karakteri, kıyafeti ya da mekânı değiştiriyor ve prompt oradan yeniden kuruluyor *(`domain/prompt.py`, `EDIT_PROMPTS`)*. **Olacak:** sade formatta düzeltilecek şey yapı değil, sahnenin kendi `senaryo` ve `prompt` metni. Zengin formattaki bugünkü davranışı aynen kalıyor. | Sade formatta yazılmış bir dosyada bir sahnenin prompt'u kullanıcının isteğiyle değişiyor, ve zengin formattaki düzenleme bugünkü gibi çalışıyor. |
