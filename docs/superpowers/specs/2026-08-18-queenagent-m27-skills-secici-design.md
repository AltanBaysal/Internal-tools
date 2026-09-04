# Madde 27 — Skills seçici arayüzü · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 27](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 33, 34, **67** · karar 1, 18 · [beceriler tasarım kararları](../research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Bu madde yalnız kaydeder

Beceri seçimi bu maddede **cevabı değiştirmez**. Yönergeler Madde 29 ve 30'un işi; burada kurulan
şey seçimin kendisi: düğme, menü, ve seçimin nereye yazıldığı. Bölünme bilerek — arayüz ile yönerge
ayrı ayrı yanlış olabilir, ikisini tek maddede karıştırmak hangisinin bozuk olduğunu gizlerdi.

---

## 2 · Altı beceri, altı etiket

Karar 18 üç beceri veriyordu; tasarım konuşması altıya çıkardı. Menü satırları (etiketler İngilizce
— QueenAgent'ın kuralı):

| Etiket | Menüdeki satır |
|---|---|
| Create scenario | A short outline, 10-15 sentences. |
| Create character prompt | SDXL character tags. Stays in the chat. |
| Split into shots | Turn the scenario into shots. Stays in the chat. |
| Generate prompts | Write every prompt in one piece. |
| Generate prompts+ | Build from parts, so a character never drifts. |
| Verify shots | Check the structure against the rules. |

Açıklamalar **ne yaptığını ve nerede bittiğini** söylüyor: "stays in the chat" satırları dosya
beklentisini baştan kesiyor, çünkü bu iki becerinin dosya yazmaması onların en şaşırtıcı yanı.

Tasarımın çizdiği dört seçenek (Web search, Deep research, Data & tables, Code) yer tutucuydu ve
karar 18'de düşmüştü; burada kayda geçiyor.

---

## 3 · Seçim iki yere birden yazılır

| Nerede | Ne | Neden |
|---|---|---|
| `Chat.skill` | sohbetin **şu anki** seçimi | başka sohbete gidip dönünce düğme aynı beceriyi göstersin (fark 34) |
| `Message.skill` | o mesajın **hangi beceriyle** gönderildiği | kayıt dürüst olsun: hangi turu hangi kural yönetti, geriye dönük değişmesin |

İkisi ayrı şeyler ve ikisi de gerekli. Yalnız `Chat.skill` olsaydı, beceriyi değiştirmek geçmiş
turların da o beceriyle üretilmiş gibi görünmesine yol açardı. Yalnız `Message.skill` olsaydı, boş
bir sohbette düğmenin ne göstereceği belirsiz kalırdı.

**Seçim mesajdan sonra durur** (§2b, tasarım kararları). Düzeltmeler aynı beceriyle devam ediyor.

**Seçiliye tekrar basmak temizler** — modelden farkı bu: bir model hep vardır, beceri olmayabilir.
Boş seçim ("hiçbir beceri") meşru ve varsayılan hâl.

Model gibi, ikisi de **boş olabilir** ve boş kalanlar diske yazılmaz; bugün diskte duran kayıtlar
göç istemeden okunur.

Değiştirme yolu modelinkiyle aynı uç nokta: `PATCH …/chats/<cid>`, gövdede `skill`. Uç nokta bugün
yalnız `model` anlıyor; **`model` ya da `skill`** anlar hâle gelir, ikisi de yoksa yine 400 —
"bir sohbet yeniden adlandırılamaz" kuralının kanıtı orada duruyor.

---

## 4 · Düğme composer'ın ayağında (karar 1)

Sıra karar 1'in verdiği sıra: **Skills · model · Send**. Madde 26 model düğmesini Send'in soluna
koymuştu; Skills onun soluna giriyor ve composer'ın ayağı son hâlini alıyor.

| Hâl | Düğme |
|---|---|
| seçim yok | "Skills" yazar, sönük durur |
| seçili | becerinin adını taşır ve **sıcak bir tonla** boyanır |

Sıcak ton `#f0e7de` (çipin zemini), yazı mürekkep. **Vurgu rengi değil** — tek vurgu kuralı: vurgu
birincil eylemi (Send) işaretler, bir durumu değil. Tasarım "sıcak bir ton" diyor, sayı vermiyor;
çipin zeminini seçmek yeni bir renk uydurmamak demek.

Menü Madde 25'in kutusu: mono `SKILLS` başlığı, altı satır, her satırın altında açıklaması, seçilide
`✓`. Genişlik 296px — composer ayağındaki menülerin ölçüsü, Madde 26 böyle kurdu.

---

## 5 · Esc sırası nihayet tamamlanıyor (fark 67)

Tasarımın sırası: **proje ⋯ menüsü → onay kutusu → Skills → model → açık panel.**

Bugün zincirin üçü App'in tek dinleyicisinde duruyor (⋯ → onay → panel). Model menüsü Madde 26'da
doğdu ama **açık/kapalı durumu `ModelPicker`'ın kendi içinde** — yani App onu göremiyor ve Esc ona
ulaşamıyor. Skills menüsü de aynı deseni tekrarlarsa zincirin iki halkası eksik kalır.

Bu maddede düzeltiliyor: **hangi seçicinin açık olduğu App'te tek bir değerde** durur
(`"model" | "skills" | null`). Üç şey birden çözülüyor:

1. Esc zinciri tamamlanır ve tek yerde kalır — Madde 25'in kuralı korunur.
2. "İki menü birbirini kapatır" bedavaya gelir: tek değer, iki hâl.
3. `ModelPicker` kendi durumundan kurtulur; iki seçici aynı deseni paylaşır.

Bu, Madde 26'nın bıraktığı bir borcun kapanması — o madde model menüsünü kurarken zincire
bakmamıştı, çünkü zincirin öteki halkası henüz yoktu.

---

## 6 · Katman denetimi

**Arka uç:** `domain/chat.py` (`Chat.skill`, `Message.skill`), `data/file_chat_store.py`,
`domain/usecases/set_chat_model.py` → adı ve kapsamı genişler, `domain/usecases/append_message.py`,
`domain/usecases/start_chat.py`, `presentation/routes.py`. Domain hâlâ hiçbir şeye bakmıyor; beceri
bir dize olarak geçiyor ve bu maddede **hiçbir yerde okunmuyor** — yalnız saklanıyor.

**Ön uç:** yeni `features/workspace/skills.js` (altı satır, metin), yeni `SkillPicker.jsx`,
`ModelPicker.jsx` (durumu dışarı çıkar), `ChatScreen.jsx`, `App.jsx`, `useChat.js`,
`useChatLists.js`, `workspace.css`.

`Menu` değişmiyor — başlık, açıklama ve `✓` Madde 26'da eklenmişti; ikinci çağıran onları hazır
buluyor. Menü desenini ortaklaştırmanın karşılığı burada ikinci kez ödeniyor.

---

## 7 · Kabul ölçütü

1. Composer'ın ayağında sırayla Skills · model · Send durur.
2. Skills düğmesi seçim yokken "Skills" yazar; menüde altı beceri ve açıklamaları vardır.
3. Bir beceri seçmek düğmeye adını verir ve sıcak tonla boyar; seçili satırda `✓` durur.
4. Seçiliye tekrar basmak seçimi temizler ve düğme "Skills"e döner.
5. Seçim sunucuya yazılır; mesaj gönderilince **seçili kalır**; başka sohbete gidip dönünce o
   sohbetin kendi seçimi görünür; yeniden başlatınca durur.
6. Gönderilen her mesaj hangi beceriyle gittiğini kendinde taşır.
7. Yeni sohbet, o oturumda en son seçilen beceriyle doğar.
8. Bir menü açıkken öteki menüye basmak birincisini kapatır.
9. Esc sırayla kapatır: ⋯ menüsü → onay kutusu → Skills → model → açık panel.
10. Beceri seçili olması cevabı **değiştirmez** — bu maddede yönerge yok.

## 8 · Risk

Sıcak tonun sayısı tasarımdan gelmiyor (çipin zemini alındı); Madde 35 gözü üstlenir. Esc zincirinin
sırası jsdom'da tam olarak sınanabiliyor — orada risk yok.
