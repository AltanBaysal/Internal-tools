# Madde 352 — Dolan sohbette *burada devam et* · test turu

**Kaynak:** [yol haritasının 352'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — v9-1c;
kararları *v9-1 — Sohbet sınırı*: 28 Eylül'ün *aynı sohbette devam*'ı ve *yalnız sohbet dolunca*'sı,
29 Eylül'ün notları (`Continue here` onay istemez ve geri alınmaz; kırpılmış sohbet yeniden dolunca
bildirim yine çıkar). Tasarım: queen-design `queen-agent-v3` — `BEHAVIOUR.md`'nin *Full chat*'i,
`DESIGN-STANDARD.md`'nin `full` satırı ve *The gauge*'in son maddesi, `kit.css`'in `.full` kuralları,
`chat/index.html`'in `fullNotice` ve `continueHere`'i; tasarımcının roadmap'inde 140 ve 182.

**Kullanıcıdan gereken:** hiçbir şey. Davranış yol haritasında ve tasarımda yazılı; aşağıdaki
kararlar teknik.

## Bugün

Sunucu dolu sohbete gelen mesajı `400` ile reddediyor (`is_full`, 337), ve ekran bunu gönderdikten
sonra, ret kartıyla öğreniyor (349). Sohbetin kaydı dolu olduğunu söylemiyor. 345'in kırpma kapısı
(`POST …/chats/<c>/trim`) var, ama onu çağıran düğme yok.

## Olacak

**Sunucu söyler** *(FOUNDATION, Karar 4)*: `/chats/<id>` her zaman `full` taşır — `is_full`'un cevabı,
tasarımdaki adla. Kırpılmış sohbet dolu değildir, yeniden dolunca yine doludur; bunu `is_full`
biliyor (345'in `test_chat.py`'si), kayıt yalnız aktarır. Ekran hiçbir şey hesaplamaz.

**Bildirim yazma kutusunun yerinde**, sohbet dolar dolmaz — kayıt `full: true` dediği an, mesaj
reddedilmeden:

- `full__text`: `This chat is full.` (`full__line`) ve altında tasarımın cümlesi, *Continue here sends
  only the latest messages to the model; the older ones stay on screen.* (`full__detail`).
- `full__actions`: solda çember (`composer__gauge` içinde, dolu — `This chat is full`), sonra `ghost`
  `New chat` ve `ghost` `Continue here`.
- Kutunun şekli ve gölgesi (`.full`, tasarımın `kit.css`'i), ve kutu o dururken görünmez.

**`New chat`** kenar çubuğununkinin yaptığını yapar: projenin taslak sohbeti açılır.

**`Continue here`** onay istemeden 345'in kapısını çağırır, sonra sohbeti yeniden okur: kayıt
`full: false` der, bildirim gider, kutu gelir, ve bütün mesajlar ekranda kalır. **Dolu iken karşılanan
ret de gider** *(tasarımın `continueHere`'i — `holdRefused(null)`)*: o ret "sohbet dolu" diyordu, ve
artık doğru değil. Kapı reddederse sunucunun kendi sözü ekranda görünür — sürüm kapısının yolu.

### Kararlar

1. **Kutu kaldırılmaz, gizlenir** (`hidden`). Tasarım kutuyu kaldırıyor; ekranda aynı görünür, ama
   kaldırılan kutu içindeki taslağı da götürür. Cevap sürerken yazılan bir cümle, o cevap sohbeti
   doldurunca kaybolurdu — FOUNDATION'ın 1. ilkesi. Gizli kutu cümleyi tutar, ve `Continue here`'den
   sonra cümle yerinde. İkinci kazanç: 349'un Try again'i reddedilen cümleyi kutuya gönderttiriyor,
   ve kutu hep yerinde olunca o yol dolu sohbette de kırılmaz.
2. **Alanın adı `full`**, tasarımınki; `trimmed` ve `context`'in yanında.
3. **Kırpmadan sonra odak kutuya verilmez.** Tasarımın sayfası veriyor, ama ne yol haritası ne
   `BEHAVIOUR.md` ne `DESIGN-STANDARD.md` söylüyor; gizliden açılan kutuya odağı doğru anda vermek
   ayrı bir durum ister. Rapora açık nokta olarak yazılır.
4. **Kapının reddi `error`'a yazılır**, sürüm kapısı gibi (`useChat.version`): aynı kart, sunucunun
   sözü.

## Testler ne tutar

**`test_chats_api.py`** — kayıt:

| # | Ne |
|---|---|
| 1 | Tavanın altındaki sohbetin kaydı `full: false` |
| 2 | Dolu sohbetin kaydı `full: true` |
| 3 | Kırpılan sohbetin kaydı `full: false` |

**`ChatScreen.test.jsx`** — bildirim:

| # | Ne |
|---|---|
| 4 | Dolu sohbette `.chat__composer`'da bildirim: iki cümle; erişilebilir yazma kutusu ve Send yok |
| 5 | `full__actions`'ın sırası: çember (`This chat is full`) solda, sonra `New chat`, `Continue here`; ikisi `ghost` |
| 6 | `New chat` `onNewChat`'i, `Continue here` `onContinue`'yu çağırır |
| 7 | Dolmamış sohbette bildirim yok, kutu var |
| 8 | Kutuya yazılan cümle bildirimden sağ çıkar: dolunca gizlenir, dolmayınca aynı cümleyle döner |

**`workspace.css.test.js`** — şekli:

| # | Ne |
|---|---|
| 9 | `.full` kutunun şekli: 720 genişlik, 14 köşe, `14px 16px 10px` iç boşluk; `.full__line` 14, `.full__detail` 13 ve `#6b6259`; `.full__actions` sağa dayalı |

**`App.test.jsx`** — uçtan uca:

| # | Ne |
|---|---|
| 10 | Bildirimin `New chat`'i taslağı açar: `/p/p1/c/new` |
| 11 | `Continue here` `POST /api/projects/p1/chats/c1/trim` gönderir, sohbeti yeniden okur; bildirim gider, kutu gelir, mesajlar duruyor |
| 12 | Dolu iken karşılanan ret `Continue here`'le gider: cevap gelmedi, kayıt dolu dedi, Try again reddedildi; `Continue here`'den sonra kart yok |
| 13 | Reddedilen kırpma sunucunun sözünü gösterir |

## Tutmaz

- **Çizgiyi:** v9-1d'nin (357).
- **Kırpma kuralını ve yeniden dolmayı:** 345'in testleri tutuyor.
- **Ret cümlesini** (`…start a new chat to keep going`): bu maddenin işi değil; dolu sohbette kutu
  yokken ona yalnız düzeltmenin ✓'si ve Try again ulaşır, ve bildirim yanında durur.

## Nasıl görülür

CLAUDE.md'deki dört satır. queen-agent'ın iki süiti yeni testlerde kırmızı verir — #7 bugün de geçer
(bildirim yok), kilit olarak kalır; queen-editor'ün ikisi yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m352-dolu-sohbet-testler-plan.md).
