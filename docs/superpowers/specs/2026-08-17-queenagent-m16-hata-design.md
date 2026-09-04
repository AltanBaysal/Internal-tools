# Madde 16 — Hata dili · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 16](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 63 · sapma 81, 82 · repo kuralı "sebep uydurulmaz" · FOUNDATION ilke 1
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Kapsam kullanıcı kararıyla genişledi

Yol haritası bu maddeye üç iş veriyor. Kod okunurken dördüncüsü çıktı: **reddedilen mesajın metni
kayboluyor.** Composer gönderir göndermez temizleniyor, `useChat` iyimser balonu geri alıyor, geriye
kullanıcının cümlesinden hiçbir şey kalmıyor. FOUNDATION'ın **birinci** ilkesi — "hiçbir senaryo
kullanıcının yaptığı işi kaybettiremez" — bunu yasaklıyor.

Kullanıcıya soruldu, **Madde 16'ya katılmasına** karar verildi: reddedilen mesaj yolu zaten bu
maddede elden geçiyor, aynı yeri iki kez açmaya gerek yok.

---

## 1 · Sunucunun kendi cümlesi ekrana çıkar (sapma 82)

Bugün tarayıcının tek istek yolu gövdeyi atıp yerine yöntem, adres ve durum kodunu yazıyor: ekranda
"POST /api/… failed with 409" görünüyor, sunucunun yazdığı "a file by that name is back in the
project" hiçbir yere ulaşmıyor.

`api.js` bundan sonra gövdeyi okur:

| Gövde | Ekrana çıkan |
|---|---|
| `{"error": "…"}` | sunucunun cümlesi, olduğu gibi |
| JSON değil ama dolu | `HTTP 500: <gövde>` |
| boş | `HTTP 500` |

Üçünde de **sebep uydurulmuyor**: ne yazılıysa o okunuyor. Durum kodu ayrı alanda taşınmaya devam
ediyor — 404 bir hata satırı değil, bir ekran.

---

## 2 · Reddedilen mesaj ile ölen akış aynı dili konuşmaz (sapma 81)

Bugün ikisi de "Couldn't get a response." kartını çıkarıyor: hiç gönderilememiş bir mesaj, cevabı
alınamamış bir mesajın diliyle anlatılıyor.

Ayrılıyorlar:

- **Reddedilen mesaj** → mesaj sütununda **tek satır** hata, sunucunun cümlesiyle. "Try again" yok:
  tekrar denenecek bir istek yok, yazılacak bir cümle var.
- **Ölen akış** → bugünkü kart. Üstte "Couldn't get a response.", altında sunucunun gerçek sözleri,
  yanında "Try again".

`useChat` bu yüzden iki ayrı alan döndürüyor: `refused` ve `error`. Tek alanla ayrım ekranda
yapılamazdı — hangi yoldan geldiğini yalnız kanca biliyor.

**Tasarımın "The connection dropped." cümlesi alınmıyor** (fark 63, iki ifade birbirini tutmuyordu).
Bu repo kuralı: bir 409 "çerez süresi doldu" değildir, akışın ölmesi de "bağlantı koptu" değildir —
kötü bir anahtar ve yanlış bir model adı aynı kartı çıkarır.

---

## 3 · Reddedilen cümle kullanıcıya geri verilir (FOUNDATION ilke 1)

`send` hatayı kaydettikten sonra **yeniden fırlatır**; Composer metni kutuya geri koyar.

Sıra önemli: kutu gönderirken **hemen** temizlenir — balonun anında belirmesi tasarımın kendi
cümlesi — ve yalnız istek reddedilirse metin geri gelir. Sırayı ters çevirmek (başarıda temizle)
başarılı yolda metni isteğin süresi boyunca ekranda tutardı.

**Kullanıcı bu arada yeni bir şey yazdıysa üstüne yazılmaz:** geri koyma yalnız kutu boşsa olur.

---

## 4 · Bu maddenin dışında kalan

**Yüklenemeyen sohbet.** `useChat`'in yükleme hatası bugün hiçbir yere çizilmiyor: `chat` boş olduğu
için ekran iskelette kalıyor. Bu sapma 83'ün ailesinden ve yol haritasında **Madde 32**'ye yazılı.
Burada dokunulmuyor.

---

## 5 · Katman denetimi

`api.js` (paylaşılan istek yolu), `useChat.js` (kanca), `Composer.jsx` ve `ChatScreen.jsx` (sunum),
`App.jsx` (yeni alanın geçişi). Arka uç hiç değişmiyor — sunucu doğru cümleyi zaten yazıyordu,
görünmeyen tarafı tarayıcıydı.

---

## 6 · Kabul ölçütü

1. Sunucu `{"error": "…"}` döndürünce ekranda o cümle okunur, "failed with 409" değil.
2. JSON olmayan gövde `HTTP <kod>: <gövde>` olarak okunur; boş gövdede yalnız kod.
3. Reddedilen mesaj tek satır hata çıkarır, kart çıkmaz.
4. Ölen akış kartı çıkarır ve altında sunucunun sözleri durur; "connection dropped" hiçbir yerde
   geçmez.
5. Reddedilen mesajın metni composer'a geri gelir; kullanıcı yeni bir şey yazdıysa gelmez.

## 7 · Risk

`send`'in artık fırlatması, onu çağıran her yerin yakalaması gerektiği anlamına geliyor. Tek çağıran
Composer ve o yakalıyor; App'in `startChat`'i de aynı kutudan geçtiği için aynı korumayı bedavaya
alıyor.
