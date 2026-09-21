# QueenAgent — Yol Haritası v9

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queenagent-v9` · **Durum:** 0/4
**Öncesi:** [v8](2026-09-06-queen-agent-v8-roadmap.md) — kapandı ve `356d605` ile main'e alındı.
**Kaynak:** 277, 279 ve 280 kullanıcının 21 Eylül'deki sözlerinden doğdu. 278
[BACKLOG.md](../../../queen-agent/BACKLOG.md)'den geliyor; ne yaptığı aynı gün konuşuldu.

**Belge `feat/queen-editor-v6` dalında yazıldı** *(kullanıcı, 21 Eylül — "sen bu dalda oluştur
roadmapi sıkıntı yok")*. Başlıktaki dal koşunun dalı; yazıldığı yer başka.

**Neden ayrı belge.** İş [Queen Editor v7](2026-09-21-queen-editor-v7-roadmap.md)'nin referans
maddelerine bağlı — prompt'u QueenAgent yazıyor, videoyu queen-editor üretiyor. Kullanıcı ikisinin
tek koşuda birleşmesini değil, **ayrı belge ve ayrı dal** istedi *(21 Eylül — "Ayrı bir QueenAgent v9
yol haritası. Kendi belgesi, kendi dalı (feat/queenagent-v9), ayrı koşulur.")*.

**Numara kimliktir, sıra değildir.** Sayaç iki aracın arasında ortak ilerliyor: queen-editor'ün v6
koşusu 249–261'i, [v7](2026-09-21-queen-editor-v7-roadmap.md) 262–276'yı aldı. Bu koşu **277'den**
başlıyor. **Belge iki kez yeniden numaralandı** *(21 Eylül)*: ilk hâli 253–254'ü, ikincisi 270–271'i
de kullanıyordu, ve v6 biz yazarken o numaraları aldı.

**Koşulacak sıra bu dosyanın sırası.**

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**Dördü de 21 Eylül'de konuşuldu ve dördü de kapandı.** 279 aynı gün bir kez daha ele alındı
*(kullanıcı — "yine ayrıca konuşuruz, direkt kapatma", ardından "alalım, tam hazır olsun
roadmapler")*: açık kalan tek yeri, skill'in referansları nereden bildiği, o konuşmada karara
bağlandı.

**277 ötekilerin temeli.** 278 ve 279 onun formatına yazıyor, 280 o formatı düzenliyor.

**278 ve 279 skill seçicisine birer satır ekliyor**, yani aynı üç dosyaya dokunuyorlar. Hangisi önce
koşarsa ikincisi onun bıraktığı listeye eklenir; sıra bu yüzden önemli değil, ama ikisi aynı anda
koşulmaz.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 277 | **Sade senaryo formatı.** *(Kullanıcı, 21 Eylül — "yeni json yapısı yapabiliriz senaryo prompt şeklinde çok basit olan", "AI'a alan bırakalım tekte üretmesi için".)* **Bugün** QueenAgent'ın ürettiği her prompt **kod tarafından** kuruluyor: yapı dosyasının karakterleri, kıyafetleri ve mekânları aranıp diziliyor, `BREAK` konuyor, kalite zinciri başa ekleniyor *(`domain/build_prompts.py`)*. **Olacak:** ikinci ve sade bir format — sahneler, her sahnede `senaryo` ve `prompt`. `senaryo` kullanıcının okuması için; `prompt` modelin yazdığı prompt'un kendisi ve **olduğu gibi** listeye giriyor. **Kod hiçbir şey eklemiyor**, kalite etiketlerini de model yazıyor *(kullanıcı kararı, 21 Eylül — "sade yapıda ekstra kod eklemeyelim, kalite promptlarını direkt AI eklesin")*. **Bedeli yazıya geçiyor:** kalite zinciri koda tam da bu yüzden alınmıştı — model şemadan kopyalarken **iki model ailesini karıştıran bir zincir gerçek dosyalara ulaşmıştı** *(madde 110, 166)*. Risk bilerek geri alınıyor. **Start a scenario değişmiyor:** süreklilik zengin yapıyı istiyor, ve QueenAgent bundan sonra **iki formatlı** oluyor. | Sade formatta yazılmış bir dosyadan prompt listesi çıkıyor, prompt'lar dosyada yazdığı gibi; zengin format bugünkü gibi çalışmaya devam ediyor. |
| 278 | **Compilation skill'i.** *(Kullanıcı, 18 Eylül; backlog'dan. Ne yaptığı 21 Eylül'de konuşuldu.)* Skill seçicisine üçüncü satır. **Kullanıcıya iki şey sorar** — konunun ne olacağı ve **kaç sahne** istendiği — ve o kadar kareyi tek seferde üretir. **Süreklilik yoktur:** kareler birbirinin devamı değil, kadro kareden kareye değişir. Konu neyin görüneceğini belirler — *hastane* dendiyse hemşire, doktor, çalışanlar; *30 yaş üzeri gotik kızlar* dendiyse kareler onu taşır. **Her karenin kendi karakteri, tek kullanımlıktır:** tip kareler arasında tekrar etmez, kullanıcının istediği çeşitlilik oradan gelir. **277'nin sade formatına yazar**, yani prompt'u baştan sona model kurar — kalite etiketleri de, iki kişili bir karede `BREAK` de. *Start a scenario*'dan farkı tek cümlede: o **süreklilik** üretir, bu **çeşitlilik**. **Değişen:** [domain/skills.py](../../../queen-agent/backend/features/workspace/domain/skills.py) *(`INSTRUCTIONS`)*, [domain/prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py) *(skill'in metni)*, [skills.js](../../../queen-agent/frontend/src/features/workspace/skills.js) *(`SKILLS`)*; ve bunları çivileyen testler — `test_skills.py`, `skills.test.js`, `SkillPicker.test.jsx`; `dist`. | Konu ve sahne sayısı verilince o kadar sahne çıkıyor, her biri kendi kadrosuyla, ve dosya sade formatta. |
| 279 | **Referanstan video üretimi için prompt'lar — kendi skill'iyle.** *(Kullanıcı, 21 Eylül — "queen agent içinde bir roadmap kaçta kaldıysa referanstan video üretimi adında promptları oluşturmalı o da çünkü", ve "queen agent oluşturucak onun için skill ekleyeceğiz".)* Compilation'ın sorma biçimini ödünç alır — konu ve kaç sahne — ve **277'nin sade formatına** yazar. **Çıkardığı prompt H3'ün REF2VA biçiminde:** altı bölüm — `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` — ve referanslara etiketle atıf: `<Subject N>` *(referanstan soyutlanan görünen şey)*, `<Picture N>` *(kare çıpası)*, `<Video N>` *(kurgu, süreklilik, ritim)*, `<Audio N>` *(ses sinyali)*, tipe göre ayrı ve sıraya göre numaralı. **Kalite etiketi yok:** `score_9_up` SDXL'in dili, H3'ün altı bölümünde anlamsız kelime olur. **Tutarlılığı referans taşır, prompt değil** — karakteri ve mekânı prompt'a yazan yapıya bu yüzden gerek yok. **Kullanıcı elle de yazabilir**, fotoğraf prompt'larında olduğu gibi. **Referansları anlatan kendi dosyası olur.** QueenAgent havuzdaki dosyaları göremez — `IMG_2931.jpg` kimseye bir şey söylemez, referansın ne olduğunu yalnız kullanıcı bilir. Skill ilk seferde sorar, aldığı cevabı bir JSON'a yazar ve sonraki üretimlerde oradan okur; havuz değişince kullanıcı söyler, skill günceller. Dosya tipe göre üç liste tutar — fotoğraflar, videolar, sesler — ve **listedeki sıra etiketin numarasıdır**: `fotograflar`'ın üçüncüsü `<Picture 3>`, `videolar`'ın ilki `<Video 1>`. Ayrı bir numara alanı yoktur; olsaydı sıra ile numara bir gün çelişirdi. | Referanslı video için istenen prompt altı bölümü ve etiketleri taşıyarak çıkıyor; queen-editor'ün toplu prompt kutusuna olduğu gibi giriyor. |
| 280 | **Edit prompts sade formatı da düzenler.** *(Kullanıcı, 21 Eylül — "edit prompt zaten senaryo düzenliyor, o yüzden onu da düzeltiriz".)* **Bugün** *Edit prompts* prompt'u değil **yapıyı** düzeltiyor: karakteri, kıyafeti ya da mekânı değiştiriyor ve prompt oradan yeniden kuruluyor *(`domain/prompt.py`, `EDIT_PROMPTS`)*. **Olacak:** sade formatta düzeltilecek şey yapı değil, sahnenin kendi `senaryo` ve `prompt` metni. Zengin formattaki bugünkü davranışı aynen kalıyor. | Sade formatta yazılmış bir dosyada bir sahnenin prompt'u kullanıcının isteğiyle değişiyor, ve zengin formattaki düzenleme bugünkü gibi çalışıyor. |
