# Madde 77 — Seçiciler proje ekranına iner, açılış eskiye döner · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 77 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder.

---

## Ne kanıtlanacak

Madde 65'in teşhisi doğruydu: **proje ekranının yazma kutusunda skill ve model seçici yok**, o yüzden
ilk cümle yazılmadan hiçbir şey seçilemiyordu. Çözümü yanlıştı: açılışı taslak sohbete kaçırmak,
proje ekranının eksiğini kapatmıyor — sadece o ekranı görünmez kılıyor.

İki iddia:

1. **Açılış proje ekranına dönüyor.** Uygulama ilk projenin ekranına düşüyor, taslak sohbete değil.
2. **Seçiciler orada.** Proje ekranının yazma kutusunda skill ve model seçilebiliyor, ve seçilen
   şey **başlayan sohbete gerçekten geçiyor**.

İkincisinin ikinci yarısı maddenin asıl işi. Düğmenin adının değişmesi bir görüntü; sohbetin o
skill'le doğması davranış.

## Bugün ne var

`ProjectScreen` yazma kutusunu `foot`suz çiziyor — yalnız `Start` düğmesi. `ChatScreen` ise
`SkillPicker` ve `ModelPicker`'ı `foot` içinde taşıyor. Yani gereken parça hazır ve iki ekranda da
aynı: eksik olan onu ikinci ekrana da vermek.

Seçilen değerlerin gideceği yer de hazır: `App` oturum boyunca `lastSkill` ve `lastModel` tutuyor,
ve `startChat` ikisini `startChatInProject`'e geçiriyor. Taslak sohbet zaten bu yolu kullanıyor —
proje ekranı aynı yola bağlanıyor, ikinci bir yol açılmıyor.

## Karara bağlananlar

**Aynı iki seçici, aynı sıra.** `Skills · model · Start`. `ChatScreen`'in sırası `Skills · model ·
Send`; iki ekranda farklı sıra, aynı işi iki kez öğrenmek demek.

**Seçim oturumun, sohbetin değil.** Proje ekranında henüz bir sohbet yok, yani yazılacak bir kayıt
da yok. Seçim `App`'in oturum değerine düşüyor — taslak sohbetin bugün yaptığının aynısı, aynı
sebeple.

**Hangi menünün açık olduğu yine `App`'in.** Escape'i tek bir dinleyici sahipleniyor ve yalnız
gördüğünü kapatabiliyor. İkinci bir yerde tutmak, iki menünün birbirini kapatmasını bozar.

**65'in testleri silinmiyor, çevriliyor.** Beşi de hâlâ gerçek sorular soruyor — açılış nereye
düşüyor, tarihe yazılıyor mu, tanınmayan adres nereye gidiyor. Değişen yalnız doğru cevap. Silmek,
o soruların hiç sorulmamış olması olurdu.

**Sidebar'ın maliyeti tersine dönüyor.** 65 "proje ekranı hâlâ sidebar'dan açılıyor mu" diye
soruyordu. Artık proje ekranı açılışın kendisi; sorulacak olan **taslak sohbetin hâlâ ulaşılabilir
olduğu** — sidebar'daki `New chat` düğmesiyle.

## Yazılacak testler

### `ProjectScreen.test.jsx` — dört test

Yazma kutusunun altı `Skills`, model ve `Start`'ı bu sırayla taşıyor. Seçilen skill yukarı
veriliyor, ekranda tutulmuyor. Seçilen model de öyle. Açık olan menü, ekrana söylenen menü — kendi
kararı değil.

### `App.test.jsx` — beş çevrilen, bir yeni

**Çevrilenler.** Açılış ilk projenin **ekranına** düşüyor. Tanınmayan bir adres (`/settings`) de
oraya düşüyor. Fork tarihe yazılmıyor — adres artık `/p/p1`. Sunucuya `settings` sorulmuyor — iddia
aynı, beklenen ekran değişiyor. Ve *"hiçbir şey yazmadan skill seçilebiliyor"* — maddenin asıl
sorusu, artık **proje ekranında** soruluyor.

**Yeni: seçilen skill başlayan sohbete geçiyor.** Proje ekranında bir skill seçiliyor, bir cümle
yazılıp `Start`'a basılıyor, ve sunucuya giden istek o skill'i taşıyor. Görüntüyle davranışı
ayıran tek test bu.

**Sidebar testi tersine dönüyor:** proje ekranından `New chat` ile taslak sohbete hâlâ
gidilebiliyor.

## Kapsam dışı

`ChatScreen`'in seçicileri *(duruyor, dokunulmuyor)* · taslak sohbet ekranı *(duruyor, sidebar'dan
açılıyor)* · seçimin diske yazılması *(sohbetin kendi kaydı zaten sunucuda; bu oturumun başlangıç
değeri)* · model listesinin sadeleşmesi *(Madde 72)* · arka uç *(tek satır değişmiyor)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Arka uç bu maddeden etkilenmiyor; bugünkü iki kırmızısı defterin dalı yüzünden ve kullanıcının
kendi isteği.

Ön yüzde kırmızı iki gruptan geliyor: proje ekranının dört yeni testi *(seçiciler henüz yok)* ve
`App`'in çevrilen testleri *(açılış hâlâ taslak sohbete düşüyor)*. Yeni bir ad doğmuyor —
`SkillPicker` ve `ModelPicker` var, ve `Composer` `foot`u zaten alıyor.
