# Madde 195 · test turu — düzenlenen mesaj sohbeti sürümler

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 195.

---

## Bugün ne oluyor

Sohbet düz bir mesaj listesi: `Chat.messages`, ve her tur sonuna bir mesaj ekliyor
*(`append_message`)*. Yanlış istenmiş bir mesajın geri alınması yok — ne değiştirilebiliyor, ne o
noktadan başka bir yola sapılabiliyor. Kalan cümle de sadece durmuyor: kap her turda konuşmanın
tamamını gönderiyor, yani yanlış cümle modele tekrar tekrar gidiyor.

## Ne kurulacak

Kullanıcı mesajında **Edit**. Cümle yazı kutusuna düşer, gönderilince o noktadan **yeni bir sürüm**
açılır ve tur oradan koşar. Mesajın altında `‹ 2/3 ›` — sürümler arasında gezilir, eski sürüm durur.

### Çizgi, ve nereden ayrıldığı

Bir sürüm, **ayrıldığı yer artı kendi mesajları**:

```
Version(id, parent, at, messages)
```

`parent` bir çizginin adı *(boş = sohbetin ilk çizgisi)*, `at` o çizginin **kaç mesajını tuttuğu**.
Gösterilen konuşma buradan türetiliyor: `çizgi(parent)[:at] + messages`. Nüsha yok — ayrılma
noktasına kadarki mesajlar hâlâ tek yerde duruyor, ve bir sürümün sürümü aynı kuralla zincir
hâlinde yürüyor.

`Chat` iki alan alıyor: `versions` ve `active`. `active` boşsa açık olan ilk çizgi, yani bugünkü
`messages`.

### Sohbeti okuyan her şey açık çizgiyi okur

Bugün `chat.messages`'ı okuyan yedi yer var: `last_activity`, `is_owed_an_answer`, `last_context`,
`context_box`, `stream_answer`'ın üç okuması, ve `append_message`'ın yazması. Hepsi **açık çizgiyi**
okuyacak — kapalı bir sürümdeki turlar ne kabın içine girer, ne tavana sayılır. Gönderilmeyen bir
şeyin bağlamı büyütmesi yanlış olurdu.

Başlık bunun dışında: *"başlık sohbeti başlatan mesaja aittir ve hiç kımıldamaz"* kuralı yerinde
kalıyor, yani ilk çizginin ilk mesajından geliyor ve sürüm açmak onu değiştirmiyor.

### `‹ 2/3 ›` hangi mesajın altında, ve neyin arasında

Bir sıradaki seçenekler, **o noktadan ayrılan çizgiler**: taban çizgi *(kendi mesajıyla devam eden)*
ve o noktada ondan ayrılan her sürüm. Sıra: önce taban, sonra sürümler doğdukları sırayla — bu sıra
`‹ 1/2 ›`'nin hangi yöne gittiğini belirleyen tek şey.

Her mesaj kendi seçeneklerini yanında taşıyor:

```json
"variants": { "index": 1, "of": 2, "versions": ["", "l2"] }
```

Tek seçenekli mesajda da duruyor *(`of: 1`)*: ön yüz eline geçenden çiziyor, ve gelip giden bir alan
her okuyucuya bir kontrol ekletir. Şerit `of > 1` iken çiziliyor.

### Kapı iki tane, ve ikisi de var olanın üstüne biniyor

**Sürüm açmak** bugünkü `POST /messages`'ın kendisi, bir alan fazlasıyla: `"from": 3` — *"açık
çizginin 3. mesajından itibaren yeni bir sürüm"*. Ayrı bir kapı, akışı ve reddedişleri ikinci kez
kurmak olurdu.

**Sürüm değiştirmek** yeni bir kapı: `POST /chats/<id>/version`, gövdesinde `{"version": "l2"}`.
`stop` ve `permission`'ın kardeşi. Bu kapı `routes.py`'nin *"bir sohbet yazıldıktan sonra hiçbir
şeyi değişmez"* yorumunu geçersiz kılıyor; yorum uygulama turunda düzeltilecek.

### Diskte

```json
{ "title": ..., "createdAt": ..., "messages": [...],
  "versions": [{ "id": "l2", "parent": "", "at": 3, "messages": [...] }],
  "active": "l2" }
```

`versions` ve `active` ancak **varken** yazılıyor — boş liste diskte gürültü, ve `FileChatStore`'un
bütün alanları zaten böyle davranıyor. Sürümü olmayan bir sohbet bugünkü hâliyle okunur; göç yok.

## Testler

### `test_chat.py` — çizginin türetilmesi

1. **sürümsüz sohbet kendi mesajlarını okur** — `active_messages` bugünkü `messages`.
2. **sürüm, tabanın önü artı kendi mesajları** — `at`'ten sonrası atılır.
3. **sürümün sürümü zinciri yürür** — üç kademe.
4. **`active` bilinmeyen bir adı gösteriyorsa ilk çizgi okunur** — elle düzenlenmiş bir dosya
   çökmez.
5. **`is_owed_an_answer` açık çizgiye bakar** — kapalı çizgi cevaplanmış, açık olan değil.
6. **`last_context` açık çizgiye bakar** — kapalı çizgideki büyük tur tavana sayılmaz.
7. **`last_activity` açık çizginin son mesajıdır.**
8. **seçenekler: taban önce, sürümler doğuş sırasıyla**, ve açık olanın sırası doğru.
9. **ayrılma noktasından önceki mesajın tek seçeneği var** — `of: 1`.
10. **iki kez düzenlenen mesaj üç seçenekli olur** — aynı noktadan iki sürüm.

### `test_file_chat_store.py` — şema

11. **sürümler yazılır ve geri okunur** — `versions` ve `active` diskte.
12. **sürüm yoksa iki anahtar da yazılmaz.**
13. **bu maddeden önce yazılmış sohbet tek çizgi olarak okunur.**

### `test_append_message.py` — sürüm açmak

14. **`branch_at` yeni bir sürüm doğurur** — `parent` açık çizgi, `at` verilen sıra.
15. **yeni sürüm açık olan olur.**
16. **düzenlenen mesaj sürümün ilk mesajıdır** — eskisi kopyalanmaz.
17. **eski çizgi olduğu gibi kalır** — mesajları kımıldamaz.
18. **bir sürümün üstünden dallanmak o sürümden ayrılır** — `parent` açık sürümün adı.
19. **`branch_at` yokken mesaj açık çizginin sonuna gider**, ilk çizginin değil.
20. **boş metin sürüm açarken de reddedilir** — `EmptyMessage`.

### `test_chats_api.py` — kapılar

21. **GET açık çizgiyi verir**, ve her mesaj `variants` taşır.
22. **`from` ile gönderilen mesaj sürüm açar** — cevap yeni çizgiye yazılır.
23. **`POST /chats/<id>/version` açık sürümü değiştirir** — sonraki GET öteki çizgiyi verir.
24. **olmayan sürüm 404**, ve açık olan kımıldamaz.
25. **tavan açık çizgide ölçülür** — kapalı çizgideki büyük tur yeni turu engellemez.

### `ChatScreen.test.jsx` — ekran

26. **kullanıcı mesajında Edit var, cevapta yok.**
27. **Edit metni yazı kutusuna koyar.**
28. **`of > 1` olan mesajın altında `2/3` ve iki ok** *(`Previous version` / `Next version`)*.
29. **tek seçenekli mesajda şerit yok.**
30. **oka basmak sürümü çağırır** — hangi çizgiye geçileceğiyle.
31. **Edit'ten sonra gönderilen mesaj ayrılma sırasını taşır.**

### `App.test.jsx` — baştan sona

32. **ikinci mesaj düzenlenir, sohbet oradan devam eder, `‹ 1/2 ›` ile eskisine dönülür** ve eski
    cevap olduğu gibi durur.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. Arka uçta 25 kırmızı — `active_messages` ve `variants`
diye bir şey yok, `branch_at` bilinmeyen bir parametre, `/version` kapısı 404 veriyor. Ön yüzde 7:
`Unable to find role button with name Edit`. `queen-editor` kımıldamıyor: **739 · 591** yerinde.
