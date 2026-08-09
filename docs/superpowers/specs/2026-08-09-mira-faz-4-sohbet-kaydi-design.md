# Mira — Faz 4: Composer ve sohbet kaydı (Madde 8-9)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 3](2026-08-09-mira-faz-3-proje-ekrani-design.md)

**Kapsam:** composer'ın bütün taslak kuralları (Madde 8) · sohbetin ve ilk mesajın diske yazılması,
uç noktalarıyla (Madde 9).
**Kapsam dışı:** sohbet ekranı ve gönderme akışının bağlanması (Madde 10) · cevap (Faz 6).

---

## 1 · Composer kuralları (Madde 8)

`ComposerShell` kabuk olmaktan çıkıp **kontrollü** bir bileşen olur.

| Kural | Davranış |
|---|---|
| Boş taslak | Buton `disabled`, pasif görünüm (`#E5DFD5`, `not-allowed`) |
| Yalnız boşluk | Boş sayılır — `trim()` sonrası karar verilir |
| Enter | Gönderir |
| Shift+Enter | Satır atlar, göndermez |
| Öneri baloncuğu | Taslağı **doldurur**, göndermez |
| Gönderdikten sonra | Taslak temizlenir |

Taslak `App` seviyesinde değil, composer'ın **kendi içinde** tutulur: taslak hiçbir ekranın
kaydettiği bir şey değil, kutunun anlık hâli. Dışarıya yalnız `onSubmit(text)` çıkar.

**`onSubmit` bu fazda bağlanmaz.** Bileşen onu isteğe bağlı alır; verilmediğinde Enter ve buton
hiçbir şey yapmaz. Bağlanması Madde 10'un işi, çünkü gönderilen mesajın gideceği ekran orada doğuyor.
Kuralların hepsi bileşen testinde kanıtlanabiliyor, yani madde kendi başına kapanıyor.

## 2 · Sohbet kaydı (Madde 9)

### Diskteki şekli

`<project-id>/chats/<chat-id>.json`:

| Alan | Ne |
|---|---|
| `title` | İlk mesajdan türetilir; **saklanır**, çünkü Madde 27'de kullanıcı değiştirebilecek |
| `createdAt` | ISO 8601 |
| `messages` | `[{role, at, text}]` — `role` `user` veya `ai`, `at` ISO 8601 |

**`at` tam bir zaman damgasıdır, `11:04` değil.** Tasarım ekranda `11:04` gösteriyor ama biçimlendirme
bir sunum işidir (FOUNDATION, Karar 4): sunucu gerçeği yazar, tarayıcı okunacak hâle getirir. Ters
yapılırsa aynı damgadan tarih türetmek imkânsız hâle gelirdi.

**Çözünürlük milisaniyedir, saniye değil.** Damga aynı zamanda **sıranın kaynağı**: aynı saniyede
kurulan iki sohbetin damgası eşit olsa sıra rastgele id'ye kalır ve liste her okunuşta başka türlü
gelebilir. Aynı kusur proje listesini de vuruyordu; düzeltme ikisini birden kapatıyor.

Sohbet id'si projeninki gibi opak: `c` + 12 haneli onaltılık.

### Başlık kuralı

İlk mesajın kırpılmış hâlinin **ilk 42 karakteri**; daha uzunsa 42 karakter + `…`. Tam 42 karakterde
üç nokta **eklenmez** — kesilen bir şey yok.

### Kurallar

- Sohbet **ilk mesajla birlikte** doğar; boş sohbet diye bir şey yoktur.
- Boş ya da yalnız boşluktan oluşan metin **reddedilir** (400).
- Bilinmeyen proje **404**.
- Mesaj, sohbet dosyasına **yazılmadan** hiçbir şey döndürülmez: kullanıcının yazdığı şey her koşulda
  önce diske düşer.

### Uç noktalar

| Uç nokta | Ne |
|---|---|
| `POST /api/projects/<pid>/chats` `{text}` | Sohbeti ilk mesajıyla kurar, sohbeti döndürür (201) |
| `GET /api/projects/<pid>/chats` | Projenin sohbetleri, **yeniden eskiye** |
| `GET /api/projects/<pid>/chats/<cid>` | Tek sohbet, mesajlarıyla |

Liste **yeniden eskiye** sıralanır — projelerin tersine. Gerekçe tasarımın kendisi: "Recent chats" ve
proje ekranındaki liste en son konuşulanı üstte gösteriyor. Proje listesi kurulma sırasını koruyor
çünkü orada "en son" diye bir kavram yok.

Liste yanıtı **mesajları taşımaz** — yalnız `id`, `title`, `createdAt` ve son hareket zamanı. Tek
sohbetin uç noktası mesajları verir. Gerekçe: liste ekranı mesajları çizmiyor, göndermek boşuna.

## 3 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain | `chat.py` — `Chat` ve `Message` veri sınıfları · `chat_title(text)` kuralı |
| domain/ports | `ChatStore`: `add(project_id, chat)`, `list_for(project_id)`, `get(project_id, chat_id)` |
| domain/usecases | `start_chat(chat_store, project_store, project_id, text, new_id, now)` |
| data | `FileChatStore` — `chats/<id>.json` şemasını bilen tek yer |
| presentation | üç rota |

`start_chat` projenin varlığını `project_store.get` ile doğrular: sohbetin sahibi olmayan bir proje
altında dosya oluşmaz.

## 4 · Testler

1. Başlık 42 karakterde kesiliyor ve `…` alıyor; kısa metin olduğu gibi kalıyor; tam 42'de nokta yok.
2. Sohbet ilk mesajıyla birlikte diske düşüyor ve yeni bir depo örneği aynı mesajı okuyor.
3. Boş metin reddediliyor, dosya oluşmuyor.
4. Bilinmeyen proje 404.
5. Liste yeniden eskiye geliyor.
6. Liste mesajları taşımıyor, tek sohbet taşıyor.
7. Composer: boş taslakta buton pasif; yalnız boşlukta da pasif.
8. Composer: Enter gönderiyor, Shift+Enter göndermiyor.
9. Composer: öneri taslağı dolduruyor, göndermiyor.
10. Composer: gönderdikten sonra taslak boşalıyor.
11. Composer: `onSubmit` verilmediğinde Enter hiçbir şey yapmıyor ve çökmüyor.

## 5 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda görülen: boş kutuda buton pasif, yazınca canlanır, öneriye
tıklayınca kutu dolar ve hiçbir yere gidilmez, Shift+Enter satır atlar.
