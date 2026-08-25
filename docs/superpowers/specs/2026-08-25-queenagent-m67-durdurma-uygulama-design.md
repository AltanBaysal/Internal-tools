# Madde 67 — Çalışan cevap durdurulur · **uygulama turu**

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 67 ·
**Önceki tur:** [test tasarımı](2026-08-25-queenagent-m67-durdurma-testler-design.md) — kırmızı
commit'lendi.
**Tur:** ikiden ikincisi.

---

## Durdurmanın yolu

İki istek, bir bellek kaydı:

1. Kullanıcı durdurma düğmesine basar; tarayıcı **ayrı bir istek** atar.
2. Rota kaydı işaretler ve döner. Cevabı taşıyan istek başka bir iş parçacığında akmaya devam
   ediyor — sunucu istekleri eşzamanlı karşılıyor, bu doğrulandı.
3. Akan döngü her parçadan önce kayda bakar. İşaretliyse yaymayı bırakır ve döngüden çıkar.
4. O ana kadar söylenen, doğan dosyalar ve yapılan çağrılarla birlikte diske yazılır ve mesaj
   **durdurulmuş** olarak işaretlenir.
5. Kayıt temizlenir — cevap nasıl bittiyse bitsin. Kalırsa bir sonraki cevap doğar doğmaz kesilir.

## Saklanacak bir şey yoksa

Tek kelime söylenmeden durdurulduysa mesaj yazılmaz: boş mesaj kuralı zaten bunu söylüyor ve
değişmiyor. Ama akış yine de **kaydı yollayarak biter** — sohbet olduğu gibi, değişmemiş hâliyle.
Tek şekil: akış her zaman kayıtla kapanır, tarayıcının "bitti mi, koptu mu" diye sormasına gerek
kalmaz.

Bunun bir sonucu var ve tarayıcı onu karşılamak zorunda: değişmemiş sohbetin son sözü hâlâ
kullanıcının, yani sohbet hâlâ cevap borçlu. Tarayıcı kendiliğinden yeniden isterdi. Bu yüzden
durdurma tarayıcıda bir **hâl** bırakır ve otomatik istek o hâl kalkana kadar susar — kullanıcı yeni
bir şey söylediğinde kalkar. Bugün hata hâlinin yaptığının aynısı.

## Kaydın kendisi

Bellekte, kilit altında, sohbet başına. `data/` katmanında bir sınıf ve `ports.py`'de karşılığı olan
bir protokol — depolarla aynı desen, aynı sebeple: domain neyin nasıl tutulduğunu bilmez.

Kompozisyon kökü tek bir tane kurar ve rotalara verir. Tek olması şart: iki kayıt, iki istek
birbirini bulamaz demek.

## Ekran

Tasarım bu koşuda kodu takip ediyor. Durdurma, composer'ın alt satırında, cevap akarken beliren bir
düğme. Vurgu rengi almaz — vurgu birincil eylemi işaretliyor ve o Send. Kırmızı da almaz: kendi
cevabını kesmek yıkıcı bir eylem değil, kırmızı silmeye ait.

Durdurulmuş bir cevap kendi işaretini taşır, çünkü yarım bir cümle işaretsiz durduğunda düşünmesi
biten bir modelden ayırt edilemiyor.

## `dist`

`useChat.js`, `App.jsx`, `ChatScreen.jsx` ve `workspace.css` ön yüz kaynağı: `frontend/dist` **aynı
commit'te** derlenip commit'lenir.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Arka uçta 51 kırmızının hepsi yeşile döner. **Otuz ikisi mekanikti** — imza değiştiği için
düşüyorlardı; dönmezlerse orada gerçek bir şey kırılmış demektir. Ön yüzde üç kırmızı yeşile döner.
