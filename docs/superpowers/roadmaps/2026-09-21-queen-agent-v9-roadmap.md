# QueenAgent — Yol Haritası v9

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queenagent-v9` · **Durum:** 0/2
**Öncesi:** [v8](2026-09-06-queen-agent-v8-roadmap.md) — kapandı ve `356d605` ile main'e alındı.
**Kaynak:** 253 kullanıcının 21 Eylül'deki sözlerinden doğdu, backlog'a hiç uğramadan. 254
[BACKLOG.md](../../../queen-agent/BACKLOG.md)'den geliyor ve girdisi oradan çıkar.

**Belge `feat/queen-editor-v6` dalında yazıldı** *(kullanıcı, 21 Eylül — "sen bu dalda oluştur
roadmapi sıkıntı yok")*. Başlıktaki dal koşunun dalı; yazıldığı yer başka.

**Neden ayrı belge.** İş [Queen Editor v7](2026-09-21-queen-editor-v7-roadmap.md)'nin 251. maddesine
bağlı — prompt'u QueenAgent yazıyor, videoyu queen-editor üretiyor. Kullanıcı ikisinin tek koşuda
birleşmesini değil, **ayrı belge ve ayrı dal** istedi *(21 Eylül — "Ayrı bir QueenAgent v9 yol
haritası. Kendi belgesi, kendi dalı (feat/queenagent-v9), ayrı koşulur.")*.

**Numara kimliktir, sıra değildir.** Sayaç iki aracın arasında ortak ilerliyor: v7 251 ve 252'yi
aldı, bu koşu 253'ten başlıyor.

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**İki maddenin de ayrıntısı yok.** Kullanıcıyla konuşulmadan spec yazılmaz — ne yapılacağı o
konuşmada belli olur, ve varılan karar maddenin satırına yazılır.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 253 | **Referanstan video üretimi için prompt'lar.** *(Kullanıcı, 21 Eylül — "queen agent içinde bir roadmap kaçta kaldıysa referanstan video üretimi adında promptları oluşturmalı o da çünkü".)* **Ayrıntılar kullanıcıyla konuşulacak.** | Konuşmada belirlenir. |
| 254 | **Compilation skill'i eklenecek.** *(Kullanıcı, 18 Eylül; backlog'dan.)* Skill seçicisine üçüncü bir satır girecek: **Compilation**. Bugün iki satır var — *Start a scenario* ve *Edit prompts* *(madde 101)*. **Kararlaşmadı: skill'in ne yaptığı** — kullanıcı yalnız adını verdi; neyi derlediği, girdisinin ve çıktısının ne olduğu konuşulmadı. **Başlamadan önce kullanıcıyla konuşulur.** **Değişen:** [domain/skills.py](../../../queen-agent/backend/features/workspace/domain/skills.py) *(`INSTRUCTIONS`)*, [domain/prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py) *(skill'in metni)*, [skills.js](../../../queen-agent/frontend/src/features/workspace/skills.js) *(`SKILLS`)*; ve bunları çivileyen testler — `test_skills.py`, `skills.test.js`, `SkillPicker.test.jsx`; `dist`. | Konuşmada belirlenir. |
