# Madde 102 — Ekran sorar · **uygulama turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [izin tasarımı](2026-08-28-queenagent-izin-tasarimi-design.md) — ve onun kaynağı
[v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Blok 6, Madde 102 ·
**Turun birincisi:** [test turu](2026-08-28-queenagent-m102-ekran-testler-design.md) — on üç
kırmızı commit'lendi *(`5732e38`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Kart: `PermissionCard.jsx`

Kendi dosyasında, `FileCard` ve `ConfirmDialog` gibi. Aracın adı, argümanlar, iki düğme, bir kutu.

Sebep kutusunun metni **kartın kendi anlık durumu** — `Composer`'ın taslağı nasıl orada duruyorsa
öyle. Yukarı yalnız bitmiş cümle çıkıyor, ve yalnız Deny'la.

Argümanlar `<pre>` içinde, ham. Ayrıştırma `run_tool`'un işi; ikinci bir ayrıştırıcı ilk
değişiklikte ondan ayrışır — ve göremediği bir yazmayı onaylamak zaten hiçbir şeyi onaylamamak.

`onAllow?.()` açıkça çağrılıyor, `onClick={onAllow}` değil: ikincisi yukarı bir tıklama olayı
gönderirdi, ve onayın taşıyacağı hiçbir şey yok.

## Bekleyen soru: `useChat`

Bir alan daha — `permission`, ya `{tool, args}` ya null — ve bir işlev: `answer(allowed, reason)`.

Kare `arguments` diyor, kart `args`. Çeviri burada oluyor çünkü `arguments` bir modülün içinde
prop olarak ayrıştırılamıyor; dilin kuralı.

Cevap **doğduğu sohbete** gidiyor: `streamingInto` neyse o, yoksa adresteki. İlk mesajıyla doğan
bir sohbette adres henüz boş, ve orada sorulan bir soru `chats/null` kapısını çalardı.

Tur nasıl biterse bitsin `permission` sıfırlanıyor — akan metnin ve kartların gittiği yerde.
Kalsaydı, cevaplanmadan biten bir turun sorusu bir sonraki turun üstünde asılı kalırdı.

## Kip: App

`useChat` kipten habersiz, ve öyle kalıyor. Onayı o gönderiyor, seçiciyi App kaydırıyor — ikisi tek
düğmenin altında bağlanıyor. Seçicinin değeri oturumun *(Madde 86)*, ve oturum App'in.

`modes.js` iki ad taşıyor artık: `EDIT`, ve ondan türeyen `DEFAULT_MODE`. İki ad çünkü iki sebep —
biri onayın vardığı kip, öteki uygulamanın başladığı kip; bugün aynı değer.

Ask'ın açıklaması da değişiyor. *"Nothing is written"* Madde 99'dan önce doğruydu; şimdi yazma
duruyor ve soruyor, ve satırın eskisi kullanıcıyı olmayan bir hata aramaya gönderir.

## Yer: ChatScreen

Kart transkriptin sonunda, doğan dosya kartlarının ardında. Turun **durduğu yer** orası: yazı akıyor
ya da noktalar dönüyor, ve altında soru duruyor.

Gönder düğmesine dokunulmuyor. Kart dururken tur çalışıyor sayılıyor, yani düğme zaten Stop — ve
bekleyişin çıkış kapısı da o.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Arka yüz | 99'da bitti |
| `Composer` | `running` zaten doğru; üçüncü bir düğmeye gerek yok |
| `sse.js` | İzin karesi ötekiler gibi bir kare; nabız zaten düşüyor |
| `ProjectScreen` | İlk kare sohbeti adlandırınca adres sohbete geçiyor, ve kart orada |

## Nasıl yeşil görülür

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

On üç kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` aynı commit'te derleniyor — defter bu depoyu klonluyor ve hiç derlemiyor, yani ön yüz
değişikliği bunsuz bitmiş sayılmıyor.
