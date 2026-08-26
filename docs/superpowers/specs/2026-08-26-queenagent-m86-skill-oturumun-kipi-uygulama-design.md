# Madde 86 — Skill sohbetin değil oturumun kipi olur · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 86 ·
**Turun birincisi:** [test turu](2026-08-26-queenagent-m86-skill-oturumun-kipi-testler-design.md) —
dokuz kırmızı commit'lendi *(`04674a8`)*.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz; commit'lenmiş dokuz kırmızı
yeşile döner.

---

## Bir alan, dört katman

Silinen şey tek bir alan, ama dört katmana yayılmış: `Chat` dataclass'ında bir satır, mağazada bir
yazma ve bir okuma, HTTP'de bir uç ile bir alan, ön yüzde bir çağrı ile bir prop.

Kırmızıların dokuzu bu dört katmanı tarıyor. Yeşile dönmek için her katmanda tam olarak bir şey
gidiyor — hiçbirinde yerine bir şey konmuyor.

## Arka uç

**Alan.** `Chat.skill` gider. `Message.skill` **kalır** — turu yöneten şey o, ve `_conversation`
onu okumaya devam ediyor.

**Doğuş.** `start_chat` `skill` parametresini almaya devam eder ve onu **yalnız mesaja** yazar.
Parametre kalıyor çünkü isteğin taşıdığı şey o; giden yalnız `Chat(...)` çağrısındaki ikinci
kullanımı.

**Mağaza.** Yazarken sohbet düzeyindeki `skill` bloğu gider; okurken `raw.get("skill", "")` satırı
gider. Diskteki eski anahtar okunmadan kalır ve sohbet bir daha yazıldığında düşer — göç yazılmıyor,
82'nin `model` anahtarında olduğu gibi.

**Uç.** `patch_chat` tamamen gider, importuyla birlikte. Adres GET'te durduğu için Flask PATCH'e 405
diyor; bunu yazan bir kod yok, uç olmadığında olan şey bu.

**Kural.** `set_chat_skill.py` silinir. `ChatStore.replace` **kalır** — `append_message` kullanıyor.

**Tel.** `_chat_summary`'deki `"skill"` alanı gider. Alan orada durduğu için hem sohbet listesinden
hem de tek sohbetten aynı anda düşüyor: tek düzenleme, iki yüzey.

## Ön yüz

**Çağrı.** `useChat`'in `choose`'u gider, döndürdüğü nesneden de. `patchJson` importu da gider:
bu kancada onu kullanan başka yer yok *(bakıldı)*.

**Oturum.** `App.chooseSkill` gider. Sohbet ekranının `onSkillChange`'i doğrudan `setLastSkill`
olur — taslak ekranın bugün zaten olduğu şey. İki ekran arasındaki fark ortadan kalkıyor, ve
`drafting ? ... : ...` üçlüsü tek isme iniyor.

**Prop.** `ChatScreen` `skill`'i **prop olarak** alır ve `SkillPicker`'a onu verir. `App` ona
`lastSkill`'i geçer. `chat={drafting ? { ...DRAFT, skill: lastSkill } : chat.chat}` sadeleşir:
`DRAFT` artık bir skill taşımıyor, çünkü taşıdığı yer prop oldu.

Bu, `ProjectScreen`'in ilk günden beri yaptığı şey. İki ekran aynı kalıba geliyor.

## Bir yorum düzeltiliyor

`ChatScreen`'deki *"The skill does belong to the chat on the server, so the screen asks and App
sends"* cümlesi 86'dan sonra yanlış. Yerine ne olduğunu söyleyen bir cümle geçer — çatışan bir
yorum, koda uyacak şekilde düzeltilir.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `Message.skill`, `instruction_for`, `_conversation`, `stream_answer` | Yönergeyi mesajdan alıyorlardı, almaya devam ediyorlar |
| `SkillPicker`, `Menu`, `skills.js`, `skills.py` | Seçici kalıyor *(kullanıcı kararı)*; kalkan yalnız seçimin nerede hatırlandığı |
| `ProjectScreen` | Skill'i zaten prop olarak alıyor; bu turda satırı bile değişmiyor |
| `post_chat` ve `post_message`'ın `skill` alanı | Mesaja yazılmaya devam ediyor; iki kapıyı birleştirmek 87'nin işi |
| Proje PATCH'i (`/api/projects/<id>`) | Ad değiştirme başka bir uç |
| `ChatStore.replace` | `append_message` kullanıyor |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

Dokuz kırmızı yeşile döner. **İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi,
defterdeki `BRANCH` bir özellik dalını gösterdiği için düşüyor — çalışma ağacındaki ayrı bir
değişiklik, ve bu turda ona dokunulmuyor.

`dist` bu turda **derlenir ve aynı commit'e girer**: ön yüz değişiyor, ve defter derlemiyor.
