# Madde 72 — Grok Build varsayılan ve tek model · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 2, Madde 72 ·
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## İki satır değişiyor

| Nerede | Bugün | Olacak |
|---|---|---|
| `backend/config.py` · `XAI_MODEL` | `grok-4.3` | `grok-build-0.1` |
| `frontend/.../models.js` · `MODELS` | altı satır | bir satır: Grok Build |

Başka hiçbir şey. Kapsamı kullanıcı bu iki şeye daralttı *(26 Ağustos: "başka bir şey
istemiyorum")*.

## Söylenen ve devam edilen endişe

Grok Build'in penceresi **256k**; bugünkü varsayılan Grok 4.3'ünki **1M**. Yani pencere dörtte bire
iniyor, ve yol haritası uzun işlerde bağlamın 300-500k'ya çıktığını kaydediyor — doğruysa o işler
sığmaz ve cevap ortasında hata verir. Madde 71'in 72'den önce gelmesinin tek sebebi buydu.

Endişe sayılarıyla söylendi, kullanıcı yine de istedi, ve **karar kullanıcınındır**. Bu belge onu
kaydediyor çünkü sığmayan bir iş çıktığında sebebi burada yazılı olsun — ve 76'nın getirdiği sayı da
onu ekranda gösterecek. Fiyat da düşüyor: $1.25/$2.50 yerine $1/$2.

## Bilerek yapılmayan iki şey

**Model seçici kalkmıyor.** Tek satırla duruyor. Bir seçicinin tek seçenekle durması tuhaf ama
kullanıcının istediği bu, ve kaldırmak istendiğinde ayrı bir madde olur.

**Eski sohbetlerin kayıtlarındaki model adları temizlenmiyor.** İki sonucu var, ikisi de biliniyor:

- Bugün `grok-4.3` taşıyan bir sohbet **o modelle cevaplamaya devam ediyor** — `stream_answer`
  sohbetin kendi seçimini gönderiyor, ve o seçim yerinde duruyor.
- O sohbetin düğmesi artık ham id gösteriyor: `Grok 4.3` değil, `grok-4.3`. `modelName` listede
  olmayan bir id'yi olduğu gibi yazıyor, ve bu davranış zaten var — bir düğmenin hiçbir şey
  söylememesi ham id söylemesinden kötü olurdu.

İkincisi kayıp değil, kazanç: menüde karşılığı olmayan bir modeli **isimle** göstermek, o modelin
hâlâ seçilebilir olduğunu ima ederdi.

## Kırmızıya dönecek testler

**Arka uç — bir:**

1. `test_config.py` — varsayılan `grok-build-0.1`. Testin adı ve gerekçesi de değişiyor: bugünkü ad
   *"the cheap one with the long context"* diyor, ve uzun bağlam artık bu modelin özelliği değil.
   Yalan söyleyen bir ad testten uzun yaşar.

**Ön yüz — üç:**

2. `models.test.js` — liste tek satır.
3. `models.test.js` — `modelName("grok-4.3")` ham id döndürüyor. Bugünkü test aynı şeyi `grok-4.5`
   ile soruyor; `grok-4.3` ile sormak onu gerçek vakaya bağlıyor, çünkü kullanıcının diskinde bugün
   o id'yi taşıyan sohbetler **var**.
4. `ModelPicker.test.jsx` · **yeni** — menüde karşılığı olmayan bir model taşıyan sohbette
   işaretli satır **yok**. Bugün `grok-4.3` işaretli geliyor; yarın hiçbir satır işaretli
   olmamalı, çünkü Grok Build'i işaretlemek yalan olurdu.

**Ön yüz — üç tane daha, `App.test.jsx`'te.** Model *değiştirmeyi* sınayan üç test artık
sunulmayan bir modelden başlıyor ve düğmesinde **ham id** bekliyor: `grok-4.3`. Bugün orada
`Grok 4.3` yazıyor, yani üçü de kırmızı. Bunlar fixture göçünün parçası değil — beklentileri
gerçekten değişiyor.

Toplam **yedi kırmızı**: biri arka uçta, altısı ön yüzde.

## Fixture göçü — kırmızı değil, ama şart

Bir dizi test model adını *fixture* olarak kullanıyor: `grok-4.6` yazıp `Grok 4.6⌄` bekliyorlar.
Konuları model değil — ayaktaki sıra, menünün kapanması, Escape'in sırası, skill seçimi. Ama
`grok-4.6` listeden çıkınca hepsi `grok-4.6⌄` görüp düşer.

Bu yüzden fixture'lar **bu turda** `grok-build-0.1` / `Grok Build`'e geçiyor. İkisi de bugün
listede olduğu için bu düzenlemeler ne kırmızı ne yeşil — nötr. Uygulama turunda yapılsaydı bir
düzine testin birden düşmesi **gerçek bir kırılma gibi** okunurdu, ve 78'de öğrenilen ders tam
buydu: varsayılanlı bir alan test turunu sessiz geçer, ikinci turda konuşur.

Göçen dosyalar: `ModelPicker.test.jsx`, `App.test.jsx`, `ChatScreen.test.jsx`,
`ProjectScreen.test.jsx`.

**Model *değiştirmeyi* sınayan testlerin başlangıç noktası değişiyor.** Tek satırlı bir menüde
"başka bir modele geç" diye bir hareket yok. Yerine geçen şey daha doğrusu: sohbet artık
sunulmayan bir modelle (`grok-4.3`) başlıyor ve Grok Build'e geçiyor. Bu, kullanıcının diskinde
gerçekten olan durum.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `test_model_api.py` | Varsayılanı kendi enjekte ediyor, `config`'e bakmıyor |
| `Menu.test.jsx`, `Composer.test.jsx` | `"Grok 4.6"` orada rastgele bir metin; `MODELS`'a bakmıyorlar |
| `models.test.js` — bilinmeyen id ham gösterilir | Zaten doğru, ve artık daha çok işe yarıyor |
| `ModelPicker.jsx`, `ChatScreen.jsx`, `ProjectScreen.jsx`, `App.jsx` | Seçici kalıyor; hiçbiri açılmıyor |
| Arka uçtaki her şey `config.py` dışında | Sunucu `MODELS`'ı bilmiyor — liste metin, ve metin arayüzün |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — birlikte koşturulduğunda vitest bu makinede zaman aşımına düşüyor.

Arka uçta **3 failed, 442 passed**: biri bu maddenin, ikisi defterin dalı. Ön yüzde
**6 failed, 507 passed** — bir yeni testle toplam 513.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
