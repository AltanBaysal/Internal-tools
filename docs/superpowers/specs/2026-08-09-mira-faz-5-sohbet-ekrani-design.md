# Mira — Faz 5: Sohbet ekranı (Madde 10-12)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 4](2026-08-09-mira-faz-4-sohbet-kaydi-design.md)

**Kapsam:** sohbet ekranı ve gönderme akışının bağlanması (Madde 10) · Home'dan otomatik proje +
sohbet (Madde 11) · iki sohbet listesi (Madde 12).
**Kapsam dışı:** cevap (Faz 6) · dosya rayı (Faz 9) · sohbet silme ve yeniden adlandırma (Faz 11-12).

---

## 1 · Sohbet ekranı (Madde 10)

Breadcrumb (`← proje adı` · `/` · sohbet başlığı) · mesaj sütunu · composer.

**Mesaj balonu:** kullanıcınınki sağa yaslı, `#EDE6DC` zeminli, köşeleri `14px 14px 4px 14px`.
Üstünde mono etiket. Mira'nınki sola yaslı ve balonsuz — tasarımın kuralı.

**Etiket "You · 11:04" olur.** Prototip kullanıcı adını bir prop'tan alıyordu; o prop ürüne girmedi
(Home'un selamlaması da sadece "Hi"). Adsız bir kullanıcıyı işaretlemenin İngilizce'deki karşılığı
"You"; boş bırakmak balonun kime ait olduğunu belirsizleştirirdi.

**Saat tarayıcıda üretilir.** Sunucu tam ISO damgasını verir, ekran `HH:MM`'e çevirir (Faz 4 kararı).

### Gönderme

Sohbet ekranındaki composer mesajı **var olan sohbete ekler**: `POST /api/projects/<pid>/chats/<cid>/messages`.
Bu fazda eklenen mesaj yalnız kullanıcının; cevap Faz 6'da aynı uç noktadan doğacak.

Kullanıcı balonu **anında** görünür: istek dönmeden ekrana yazılır ve dönen sohbetle değiştirilir.
Gerekçe tasarımın kendi cümlesi — *"The user bubble appears immediately."* Sunucu reddederse
(bilinmeyen sohbet, boş metin) iyimser balon geri alınır ve tek satır hata çıkar.

## 2 · Otomatik proje ve sohbet (Madde 11)

Home'dan gönderilen mesajın hedefi yok. Kural: **mesaj hem projeyi hem sohbeti açar.**

Tek uç nokta: `POST /api/chats` `{text}` → proje kurar, içinde sohbeti kurar, ikisini birden
döndürür. Kural **sunucudadır**; tarayıcının iki isteği arka arkaya atması, kuralı ön yüze taşımak ve
yarıda kalabilir bir işlem üretmek olurdu.

**Yeni projenin adı mesajdan gelir** — sohbet başlığıyla aynı kural (ilk 42 karakter). Proje ve
sohbetin aynı adı taşıması ilk anda tekrar gibi görünür; kabul ediyoruz, çünkü alternatifi
kullanıcıya `New project` adında bir kutu bırakmak ve onu elle düzeltmesini beklemek. Ad zaten
yeniden adlandırılabilir.

**Composer'ın mono etiketi burada doğar.** Faz 2'de bilerek boş bırakılmıştı; artık hedef belli:
Home'un etiketi `a new project` yazar. Bir projenin ekranındaki composer ise `the answer is saved as
a file` yazmaya devam eder — orada hedef zaten ekranın kendisi.

## 3 · Sohbet listeleri (Madde 12)

| Yer | Kaynak |
|---|---|
| Sidebar → **Recent chats** | `GET /api/chats` — bütün projelerin sohbetleri, yeniden eskiye |
| Proje ekranı → **Chats** | `GET /api/projects/<pid>/chats` (Faz 4'te yazıldı) |

Sidebar'ın listesi projeyi de taşır (`projectId`), çünkü tıklayınca gidilecek adres `/p/<pid>/c/<cid>`.
Açık sohbetin satırı işaretlidir (`#E5DFD5`).

Proje ekranındaki satır: başlık + göreli zaman (`2h ago`). **Göreli zaman tarayıcıda hesaplanır** —
sunucu ISO damgayı verir. Biçimlendirme sunum işidir ve "2 saat önce" bir saat sonra yanlış olur;
sunucudan gelseydi sayfa yenilenmeden bayatlardı.

## 4 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain/usecases | `append_message(chat_store, project_id, chat_id, text, now)` · `start_chat_in_new_project(project_store, chat_store, text, new_project_id, new_chat_id, now)` |
| domain/ports | `ChatStore.replace(project_id, chat)` |
| data | `FileChatStore.replace` (yazma zaten ortak) · `list_all()` — bütün projelerin sohbetleri |
| presentation | `POST /api/chats` · `POST /api/projects/<pid>/chats/<cid>/messages` · `GET /api/chats` |
| frontend | `ChatScreen.jsx` · `useChat.js` · `useRecentChats.js` · `relativeTime.js` |

`FileChatStore.list_all` proje dizinlerini kökten tarar. Proje listesini domain'den almaz — servis
katmanının dizin bilgisiyle yapabileceği bir iş, ve `feature ↛ feature` yasağı zaten aynı feature
içinde olduğumuz için burada devrede değil.

## 5 · Testler

1. `append_message` mesajı sona ekliyor, sohbetin başlığını değiştirmiyor.
2. Boş metin eklenmiyor (400).
3. Bilinmeyen sohbet 404.
4. `start_chat_in_new_project` projeyi ve sohbeti aynı adla kuruyor, ikisini birden döndürüyor.
5. `GET /api/chats` bütün projelerin sohbetlerini yeniden eskiye veriyor ve her satır `projectId`
   taşıyor.
6. Sohbet ekranı breadcrumb'ı, kullanıcı balonunu ve `You · HH:MM` etiketini çiziyor.
7. ISO damga `HH:MM` olarak çiziliyor.
8. Home'dan gönderilen mesaj `/p/<pid>/c/<cid>` adresine götürüyor.
9. Sohbet ekranından gönderilen mesaj balonu **istek dönmeden** gösteriyor.
10. Sunucu reddederse iyimser balon kayboluyor ve hata satırı çıkıyor.
11. Sidebar'daki Recent chats sohbetleri gösteriyor ve açık olanı işaretliyor.
12. Göreli zaman: az önce / saat / gün eşiklerini doğru yazıyor.

## 6 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda: Home'dan mesaj at → proje ve sohbet doğar, sohbet ekranına
düşülür, balon durur; yenile → mesaj yerinde; sidebar ve proje ekranı sohbeti listeler.
