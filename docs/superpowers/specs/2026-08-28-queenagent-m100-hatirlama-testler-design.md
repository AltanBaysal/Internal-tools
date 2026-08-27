# Madde 100 — Skill seçimi yenilemeden sonra hatırlanır · **test turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 100 ·
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod bir sonraki turda.

---

## Ne değişiyor

Skill seçimi bugün oturumun bir değeri *(Madde 86)*, ve sayfa yenilenince kayboluyor. Beş adımlık
bir akışın ortasında bu, bir sonraki mesajın yönergesiz gitmesi demek — ve ekranda bunu söyleyen
hiçbir şey yok. Seçim tarayıcıda hatırlanıyor.

**Madde 86'nın korktuğu geri gelmiyor.** O maddenin derdi ikinci bir kaynaktı: ekranın gösterdiği
ile isteğin taşıdığı ayrı yerlerden gelirse ayrışırlar. Burada hatırlanan şey **o değerin kendisi**
— App'in tuttuğu tek değer, yalnız yeniden doğarken diskten okunuyor.

## Neyin adı ne

| Ad | Nerede | Ne |
|---|---|---|
| `useRemembered(name, fallback)` | `shared/remembered.js` | `useState`'in yerine geçen, tarayıcıda kalan |

Depolamanın **her dokunuşu** sarmalanıyor. Depolaması kapalı bir tarayıcı ya da özel bir pencere
okurken de yazarken de hata atıyor, ve kaybedilen tek şey hafıza — uygulama yine çiziliyor.

## Kapsam dışı: kip

Kip hatırlanmıyor. Yol haritası skill diyor, ve kipin unutulmasının bir bedeli yok: yenilemeden
sonra edit'e dönüyor, yani izin verilen kipe — hiçbir iş orada takılmıyor. Skill'inki tam tersi:
unutulan skill sessizce yönergesiz bir tur demek.

## Test kurulumunun değişmesi

`test-setup.js` her testten sonra depolamayı da temizliyor. Bugün yalnız DOM temizleniyor, ve
hatırlanan bir değer aynı dosyadaki sonraki testlere sızardı — `App.test.jsx`'te skill seçen testler
zaten var, ve bugüne kadar hiçbiri iz bırakmıyordu.

## Kırmızılar

### A · `shared/useRemembered.test.jsx` — kanca *(yeni dosya)*

1. Hiçbir şey yazılmamışsa gelen cevap varsayılan.
2. Yazılan değer bir sonraki doğuşta geri geliyor.
3. Değiştirmek onu yazıyor.
4. Okumayı reddeden bir tarayıcı varsayılanı alıyor — patlamıyor.
5. Yazmayı reddeden bir tarayıcı uygulamayı düşürmüyor.

### B · `App.test.jsx` — seçim

6. Bir skill seçilip uygulama yeniden doğuyor, ve düğme o skill'i söylüyor.
7. Yeniden doğduktan sonra gönderilen mesaj o skill'le gidiyor.

**Seçimi bırakmak burada sorulmuyor.** Asıl tuzak orada: `null` ile `""` ayrı şeyler, ve ikisini
karıştıran bir okuma kullanıcının *"bunu bırak"*ını her yenilemede geri alır. Ama bu ekranda boş
seçim ile seçimsizlik **aynı düğmeyi** çiziyor — kod ne yaparsa yapsın iddia düşmez, ve düşemeyen
bir test gürültüdür. Üçüncü kırmızı ikisinin ayrıldığı yerde: kancanın kendi testinde, varsayılanı
boş dizge olmayan bir çağrıyla.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Arka yüz | Sunucu bir seçim okumuyor *(Madde 86)*; hatırlama tarayıcının kendi işi |
| `skills.js` | Liste değişmiyor; hatırlanan şey bir id |
| Kip seçicisi | Kapsam dışı, yukarıda |

## Nasıl kırmızı görülür

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

Ön yüzde yedi kırmızı — kancadan 5, `App.test.jsx`'ten 2. Arka yüz bu turdan etkilenmiyor; oradaki
iki kırmızı `test_notebook`'un, ve defterin `BRANCH`'i koşu bitince `main`'e dönecek.
