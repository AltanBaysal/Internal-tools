# QueenAgent — Yol Haritası v9

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queenagent-v9` · **Durum:** 0/2
**Öncesi:** [v8](2026-09-06-queen-agent-v8-roadmap.md) — kapandı ve `356d605` ile main'e alındı.
**Kaynak:** 253 kullanıcının 21 Eylül'deki sözlerinden doğdu, backlog'a hiç uğramadan. 254
[BACKLOG.md](../../../queen-agent/BACKLOG.md)'den geliyor ve girdisi oradan çıkar.

**Belge `feat/queen-editor-v6` dalında yazıldı** *(kullanıcı, 21 Eylül — "sen bu dalda oluştur
roadmapi sıkıntı yok")*. Başlıktaki dal koşunun dalı; yazıldığı yer başka.

**Neden ayrı belge.** İş [Queen Editor v7](2026-09-21-queen-editor-v7-roadmap.md)'nin referans
maddelerine bağlı — prompt'u QueenAgent yazıyor, videoyu queen-editor üretiyor. Kullanıcı ikisinin tek koşuda
birleşmesini değil, **ayrı belge ve ayrı dal** istedi *(21 Eylül — "Ayrı bir QueenAgent v9 yol
haritası. Kendi belgesi, kendi dalı (feat/queenagent-v9), ayrı koşulur.")*.

**Numara kimliktir, sıra değildir.** Sayaç iki aracın arasında ortak ilerliyor: queen-editor'ün v6
koşusu 249–252'yi aldı, bu koşu 253'ten başlıyor, ve
[Queen Editor v7](2026-09-21-queen-editor-v7-roadmap.md) 255'ten.

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**İki madde de spec'ten önce kullanıcıyla ayrıca konuşulur.** 253'ün satırındaki biçim 21 Eylül'deki
konuşmadan ve H3'ün kendi dokümanından geliyor — ama madde **kapanmadı**, kullanıcı ayrıca
konuşulacağını söyledi *(21 Eylül — "yine 253 ayrıca konuşuruz direkt kapatma")*. 254'ün ayrıntısı
ise hiç yok: kullanıcı yalnız adını verdi.

**İkisi de skill seçicisine satır ekliyor**, yani aynı üç dosyaya dokunuyorlar. Hangisi önce
koşarsa ikincisi onun bıraktığı listeye eklenir; sıra bu yüzden önemli değil, ama ikisi aynı anda
koşulmaz.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 253 | **Referanstan video üretimi için prompt'lar — kendi skill'iyle.** *(Kullanıcı, 21 Eylül — "queen agent içinde bir roadmap kaçta kaldıysa referanstan video üretimi adında promptları oluşturmalı o da çünkü", ve "queen agent oluşturucak onun için skill ekleyeceğiz".)* **Bugün** skill seçicisinde iki satır var — *Start a scenario* ve *Edit prompts* *(madde 101)* — ve QueenAgent'ın yazdığı video prompt'u düz metin. **Olacak:** referanslı video için üçüncü bir skill; çıkardığı prompt H3'ün REF2VA biçiminde. **Biçim, H3'ün kendi kuralı:** altı bölüm — `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` — ve referanslara etiketle atıf: `<Subject N>` *(referanstan soyutlanan görünen şey)*, `<Picture N>` *(kare çıpası)*, `<Video N>` *(kurgu, süreklilik, ritim)*, `<Audio N>` *(ses sinyali)*. Numaralar **tipe göre ayrı** ve **sıraya göre** verilir. **Kullanıcı da elle yazabilir** — fotoğraf prompt'larında olduğu gibi; skill yazmanın tek yolu değil, kolay yolu. **Kararlaşmadı:** skill'in girdisi — QueenAgent referans dosyalarını göremez, yalnız kaç tane ve hangi tipte olduğunu bilebilir; bunu kullanıcı mı söylüyor, yoksa queen-editor mü veriyor. **Madde kapanmadı:** spec'ten önce kullanıcıyla ayrıca konuşulur. | QueenAgent'tan referanslı video için istenen prompt altı bölümü ve etiketleri taşıyarak çıkıyor; queen-editor'ün toplu prompt kutusuna olduğu gibi giriyor. |
| 254 | **Compilation skill'i eklenecek.** *(Kullanıcı, 18 Eylül; backlog'dan.)* Skill seçicisine üçüncü bir satır girecek: **Compilation**. Bugün iki satır var — *Start a scenario* ve *Edit prompts* *(madde 101)*. **Kararlaşmadı: skill'in ne yaptığı** — kullanıcı yalnız adını verdi; neyi derlediği, girdisinin ve çıktısının ne olduğu konuşulmadı. **Başlamadan önce kullanıcıyla konuşulur.** **Değişen:** [domain/skills.py](../../../queen-agent/backend/features/workspace/domain/skills.py) *(`INSTRUCTIONS`)*, [domain/prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py) *(skill'in metni)*, [skills.js](../../../queen-agent/frontend/src/features/workspace/skills.js) *(`SKILLS`)*; ve bunları çivileyen testler — `test_skills.py`, `skills.test.js`, `SkillPicker.test.jsx`; `dist`. | Konuşmada belirlenir. |
