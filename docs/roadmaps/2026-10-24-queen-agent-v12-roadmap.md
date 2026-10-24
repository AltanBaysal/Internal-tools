# QueenAgent — Yol Haritası v12

**Tarih:** 2026-10-24 · **Koşu dalı:** `feat/queenagent-v12` (koşu başlarken açılır) · **Durum:** 0/3 · hazırlanıyor; v12-1, v12-2 ve v12-3 hizalanmadı
**Öncesi:** [v11](2026-10-20-queen-agent-v11-roadmap.md) — 6/6 kapandı, 24 Ekim'de Queen Editor v10'la birlikte main'e birleşti.
**Kaynak:** v12-1, v12-2 ve v12-3 kullanıcının 24 Ekim'deki sözlerinden; backlog'a değil, doğrudan buraya
*(kullanıcı, 24 Ekim — "roadmape ekle direkt backloga değil")*. v12-3 için yeni bir yol haritası
açılmadı *(kullanıcı, 24 Ekim — "yeni roadmap açma buna")*.

**Numaralar:** maddeler v12-1, v12-2, … diye yazılır, ve koşu başlarken ortak sayaçtan koşu sırasıyla
numara alır; specler bu numaraları anar.

**Dalgalar:** v12-1 ve v12-2 ikisi de QueenAgent'ın frontend'ine dokunur ve ikisi de `dist`'i yeniden
kurar, bu yüzden aynı dalgada koşamaz. v12-3 yalnız modelin rehberine dokunur, ikisinden biriyle
aynı dalgada koşabilir.

---

| # | İş | Bitti sayılır |
|---|---|---|
| v12-1 | `UNALIGNED` · **Düzenlenen mesajın kutusu yazı uzadıkça büyür, ve yazının tamamı görünür.** *(Kullanıcı, 24 Ekim — "queen agentta chat baloncuğu içinde çok yazı vars genişlmeiyor editlerken hiç bir şey göremiyorsun".)* **Bugün** bir mesaj düzenlenirken balonun yerine iki satırlık bir yazı alanı açılıyor ve yazı uzasa da iki satır kalıyor; kullanıcı elle de büyütemiyor *([EditMessage.jsx](../../queen-agent/frontend/src/features/workspace/EditMessage.jsx), `rows={2}`; [workspace.css](../../queen-agent/frontend/src/features/workspace/workspace.css), `.msg__editing-input`'ta `resize: none`)*. Uzun bir mesaj düzeltilirken yazının ancak iki satırı görünüyor. | Uzun bir mesaj düzenlenmeye açılınca kutu yazının tamamını gösteriyor, ve yazıldıkça büyüyor. |
| v12-2 | `UNALIGNED` · **Mesaj yazılan kutu, ChatGPT'deki gibi yazı uzadıkça yukarı doğru büyür.** *(Kullanıcı, 24 Ekim — "ve mesaj atıacağın yerde çok text varsa genişlemiyor chat gpt gibi yine bir şey göremiyorsun".)* **Bugün** sohbetin altındaki yazma kutusu iki satır ve yazı uzasa da iki satır kalıyor *([Composer.jsx](../../queen-agent/frontend/src/features/workspace/Composer.jsx); [ChatScreen.jsx](../../queen-agent/frontend/src/features/workspace/ChatScreen.jsx)'te `rows={2}`; `.composer__input`'ta `resize: none`)*. ChatGPT'de kutu yazıyla birlikte bir yüksekliğe kadar büyüyor, ondan sonra kendi içinde kayıyor. **Hizalanırken konuşulacak:** kutunun en fazla ne kadar büyüyeceği. | Uzun bir yazı yazılınca kutu satır satır büyüyor; bir sınırdan sonra kendi içinde kayıyor ve sohbet görünür kalıyor. Mesaj gönderilince kutu yeniden küçülüyor. |
| v12-3 | `UNALIGNED` · **SDXL rehberi femboy bir karakterin etiketlerini bilir; LoRA eklenmez.** *(Kullanıcı, 24 Ekim — LoRA'yı sorduktan sonra — "eklenmesin sdxl promptinge gitsin öyle kurallar listemiz vardı işte ayna koyma vs vs gibi oraya gitsin tektik kelimesi olduğu bu task aç bunu".)* **Kaynak LoRA:** Civitai'de *femboysXL* *([model 289006](https://civitai.red/models/289006/femboysxl-femboyotoko-no-kotrap-concept-lora-92-dim))*: tek sürümü düz SDXL 1.0 için, ve tetik kelimeleri `1boy, otoko no ko, crossdressing, trap, yaoi, penis, testicles, androgynous`. Queen Editor'e eklenmiyor; kelimeleri buraya alınıyor. **Bugün** QueenAgent'ın SDXL rehberinde *([sdxl-prompt-writing.md](../../queen-agent/backend/features/workspace/skills/sdxl-prompt-writing.md))* "ayna koyma" gibi kurallar var, ama femboy bir karakterin nasıl yazılacağı yok. **İstenen:** rehbere bir kural girer — femboy bir karakterin girdisine bu etiketler yazılır. Nova ve DaSiWa Danbooru'nun etiketleriyle eğitilmiş Illustrious modelleri, bu yüzden etiketler LoRA olmadan da bir anlam taşır; ne kadar iyi çizildiği Colab denemesinde görülür. **Hizalanırken konuşulacak:** etiketlerin hangileri girer — `1boy`, `penis` ve `testicles` rehberin öbür kurallarıyla zaten yazılıyor, ve `yaoi` yalnız iki erkekli bir sahne için. | Hizalanınca yazılır. |
