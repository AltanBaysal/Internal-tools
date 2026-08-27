# Madde 100 — Skill seçimi yenilemeden sonra hatırlanır · **uygulama turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 100 ·
**Turun birincisi:** [test turu](2026-08-28-queenagent-m100-hatirlama-testler-design.md) — yedi
kırmızı commit'lendi *(`527b378`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Kanca: `shared/remembered.js`

`useState`'in yerine geçiyor, aynı ikiliyi döndürüyor. Çağıran tarafta değişen tek şey adı.

İlk okuma `useState`'in **başlatıcısında**: bir kez, ilk çizimde. Gövdede okunsaydı her çizimde
diske gidilirdi, ve okuduğu şey zaten kendi yazdığı olurdu.

Yazma bir effect'te. Değer değiştiğinde yazılıyor, ve ilk çizimde de bir kez — okunanı geri yazmak
işe yaramıyor ama zararı da yok, ve *"ilk sefer atla"* diye bir bayrak tutmak bu kadarlık bir iş
için kendi başına bir hata kaynağı.

Depolamanın **her dokunuşu** `try` içinde. Depolaması kapalı bir tarayıcıda `localStorage`'a
erişmek okurken de yazarken de hata atıyor, ve kaybedilen tek şey hafıza: seçim o oturum boyunca
yine duruyor.

Anahtar `queenagent.` ile başlıyor. Aynı kaynağı paylaşan başka bir şeyin `skill` diye bir anahtar
yazma ihtimali uzak ama bedava da değil.

## Değeri boş dizge ile yokluğu ayırmak

`getItem` yazılmamış bir anahtar için `null` veriyor, ve yazılmış boş bir dizge için `""`. İkisi
ayrı şeyler: biri *"hiç seçilmedi"*, öteki *"seçildi ve bırakıldı"*. `kept ?? fallback` değil,
`kept === null ? fallback : kept` — ilki de doğru çalışırdı ama okuyan kişiye ayrımı söylemez.

## App

`useState(DEFAULT_MODE)` yerinde kalıyor; değişen tek satır skill'inki:

```js
const [lastSkill, setLastSkill] = useRemembered("skill", "");
```

Kip hatırlanmıyor, ve bu bir eksik değil: yenilemeden sonra edit'e dönüyor — izin verilen kipe —
yani hiçbir iş orada takılmıyor. Skill'inki tam tersi: unutulan skill sessizce yönergesiz bir tur.

## Madde 86 hâlâ yerinde

O maddenin derdi ikinci bir kaynaktı: ekranın gösterdiği ile isteğin taşıdığı ayrı yerlerden
gelirse ayrışırlar. Burada iki kaynak yok — App'in tuttuğu **tek** değer var, ve tarayıcı onun
doğduğu yer. Sunucu hâlâ bir seçim okumuyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Arka yüz | Sunucu bir seçim okumuyor *(Madde 86)* |
| `skills.js` | Liste değişmiyor; hatırlanan şey bir id |
| Kip seçicisi | Kapsam dışı, yukarıda |
| `SkillPicker` | Seçimi kimin tuttuğu onun sorunu değildi, hâlâ değil |

## Nasıl yeşil görülür

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

Yedi kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` aynı commit'te derleniyor — ön yüz değişikliği bunsuz bitmiş sayılmıyor.
