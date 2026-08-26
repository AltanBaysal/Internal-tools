# Madde 86 — Skill sohbetin değil oturumun kipi olur · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 86 ·
**Üstüne geldiği:** [Madde 82](2026-08-26-queenagent-m82-model-secimi-sokulur-testler-design.md) —
model seçimini söktü, skill'i *"orada gerçekten bir seçim var"* diyerek bıraktı. Bu madde o cümleyi
sınıyor: seçim gerçek, ama seçimin **sunucuda saklanması** gerçek değil.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## Sökülen şey

Skill seçimi bugün sunucuya yazılıyor: sohbet kaydında bir `skill` alanı, onu yazan bir PATCH ucu,
bir `set_chat_skill` use case'i, ve ön yüzde bir `choose` çağrısı.

Ama **cevap yolu o alanı hiç okumuyor.** Turu yöneten yönerge `_conversation`'da mesajın kendi
`skill`'inden geliyor — gönderim anında yazılan değerden. Sohbetteki alan yalnız seçicinin ne
göstereceğini söylüyor.

Yani bir HTTP ucu, bir kural ve bir disk alanı, tek işi bir açılır menünün başlığını hatırlamak olan
bir zincir kuruyor.

## Yerine ne geliyor

Hiçbir şey. Seçim `App.lastSkill`'de zaten yaşıyor ve gönderilen her mesaja zaten yazılıyor —
Madde 86 ikinci kaynağı siliyor, birinciye dokunmuyor.

Sonuç: skill artık **sohbetin değil oturumun** kipi. Sekmeyi kapatana kadar seçili kalır, sohbetten
sohbete geçer, ve her mesaja hangi yönergeyle konuşulduğunu yazar.

## Yanında kapanan hata

Bugün seçici sohbetin kaydını gösteriyor *(`ChatScreen`, `chat.skill`)*, gönderim ise oturumun son
seçimini yolluyor *(`App.lastSkill`)*. İkisi ayrıştığı an ekranda bir şey yazıyor, isteğe başka bir
şey gidiyor.

Ayrışmanın en kolay yolu: sayfayı yenile, skill'i olan eski bir sohbeti aç, hiçbir şeye dokunmadan
mesaj gönder. Seçici *"Verify prompts"* diyor, isteğin gövdesi `skill: ""` taşıyor.

Tek kaynak kalınca hata ortadan kalkıyor — yazılacak bir senkron yok, çünkü senkronlanacak ikinci
bir yer yok.

## Bedeli, ve neden kabul edildi

Yenilemeden sonra seçici boş başlıyor, ve bir sohbette seçilen skill ötekine de geçiyor. İkisi de
*(kullanıcı kararı, 26 Ağustos)* kabul edildi.

Tarayıcı hafızasına da yazılmıyor: sildiğimiz karmaşıklığı başka bir yere taşımak olurdu.

## Eski kayıtlar

Diskteki sohbetlerin JSON'unda `"skill": "verify-prompts"` duruyor. **Okuyan kalmıyor** — alan
domain'den çıkınca mağaza onu görmüyor bile. Göç yazılmıyor: sohbet bir daha yazıldığında anahtar
kendiliğinden düşüyor. Madde 82'nin `model` anahtarında olduğu gibi.

## Silinen testler

Bir davranış giderken testi de gider. Silinenler kayıp değil — sildikleri şey artık yok:

| Nerede | Ne |
|---|---|
| `test_set_chat_skill.py` | **dosya tamamen** — kural yok |
| `test_chats_api.py` | `..._the_skill_can_be_changed_and_cleared` · `..._a_patch_carrying_only_a_model_is_refused` — ikisi de PATCH'e dayanıyor |
| `test_chats_api.py` | `..._a_chat_is_born_with_the_skill_it_was_sent`'in sohbete bakan yarısı; mesaja bakan yarısı kalıyor |
| `test_chat.py` | `..._a_chat_still_carries_its_skill` — tersine döner |
| `test_file_chat_store.py` | `..._the_skill_a_chat_selected_is_written_and_read_back` |
| `test_file_chat_store.py` | `..._a_chat_written_before_skills_existed_still_reads` — `chat.skill`'e bakmayı bırakır, mesaja bakar |
| `test_start_chat.py` | iki testin `chat.skill` satırları; `chat.messages[0].skill` satırları kalıyor |
| `App.test.jsx` | `picking a skill writes it to the chat it was picked in` |
| `ChatScreen.test.jsx` | `a chat with a skill selected says which one` — prop'a döner |

## Kırmızıya dönecek testler

Silmek kırmızı üretmez. Kırmızıyı **yokluğu tutan** testler üretir.

**Arka uç — dört:**

1. `Chat` dataclass'ında `skill` diye bir alan **yok**. *(`test_chat.py`, bugünkü testin tersi.)*
2. Sohbetin JSON'u üst düzeyde `skill` anahtarı **taşımıyor** — mesajınki duruyor.
3. Sohbete atılan bir PATCH **405**. Uç kalkıyor ama aynı adres GET'te duruyor, yani Flask'in cevabı
   404 değil "bu adres bu yöntemi tanımıyor". *(82'de `/api/model` tamamen gitmişti ve 404'tü; buradaki
   fark bilerek yazılıyor.)*
4. Diskte üst düzey `"skill"` taşıyan eski bir kayıt okunuyor ve o alan **hiç doğmuyor**; aynı
   kayıttaki mesajın skill'i okunmaya devam ediyor.

**Ön yüz — beş:**

5. Sohbet ekranında skill seçmek **hiçbir istek atmıyor**.
6. Kaydında skill yazan bir sohbet açılıyor ve seçici **boş** — kaydı değil oturumu gösteriyor.
7. Bir sohbette seçilen skill, başka bir sohbete geçilince **seçili kalıyor**.
8. `ChatScreen` skill'i **prop olarak** alıyor, `chat`'ten okumuyor — `ProjectScreen` bugün zaten
   öyle alıyor, iki ekran aynı kalıba geliyor.
9. **Bugünkü hatanın kendisi:** seçicide yazan ne ise, gönderilen mesajın `skill`'i o. Kaydında
   skill olan bir sohbet açılıp hiçbir şeye dokunmadan mesaj gönderiliyor, ve ekranda yazan ile
   istekte giden aynı şey oluyor.

Toplam **dokuz kırmızı**.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `SkillPicker`, `Menu`, `skills.js` | Seçici kalıyor *(kullanıcı kararı)* — kalkan şey seçimin nerede hatırlandığı |
| `Message.skill` | Kayıt hangi turun hangi yönergeyle konuştuğunu söylemeye devam eder; geçmiş yalan söylemez |
| `instruction_for`, `_conversation`, `stream_answer` | Yönergeyi mesajdan alıyorlardı, almaya devam ediyorlar |
| `post_chat` ve `post_message`'ın `skill` alanı | Mesaja yazılmaya devam ediyor; iki kapıyı birleştirmek 87'nin işi |
| `ChatStore.replace` | `append_message` kullanıyor, ölü kalmıyor |
| Proje PATCH'i (`/api/projects/<id>`) | Ad değiştirme başka bir uç ve duruyor — silinen yalnız sohbetinki |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

İkisi de koşar; her birinin kırmızısı kendi çağrısını düşürür, hiçbiri ötekini maskelemez.

Sayılar bu turda **düşüyor**: silinen test eklenenden çok. Kesin toplam koşulunca yazılır — bir
sökme turunda silinen testin sayısını önden kestirmek, kestirmenin kendisini doğrulanacak bir şey
yapar.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
