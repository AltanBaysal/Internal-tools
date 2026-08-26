# Madde 87 — Mesaj tek kapıdan girer, sohbeti sunucu yaratır · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 87 ·
**Üstüne geldiği:** [Madde 86](2026-08-26-queenagent-m86-skill-oturumun-kipi-uygulama-design.md) —
sohbetin durumunu söktü; bu madde sohbetin **kapısını** birleştiriyor.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## Bölünmüş olan şey

"Kullanıcı bir cümle söyledi" işi bugün iki isteğe bölünmüş:

- `POST /api/projects/<pid>/chats` — ilk cümle, sohbeti yaratır
- `POST /api/projects/<pid>/chats/<cid>/messages` — sonraki cümleler, ekler

Hangisinin çağrılacağını **frontend** seçiyor: bir bayrak (`drafting`) yüzünden gönderme işinin iki
ayrı yolu var. Sunucuda da iki use case aynı üç şeyi yapıyor — metni doğrula, mesajı yaz, kaydı
döndür.

Tek kapı kalır: frontend her zaman aynı yere gönderir, sohbet yoksa sunucu yaratır, varsa ekler.

## Adres

`POST /api/projects/<pid>/messages`, ve sohbetin id'si **gövdede**:

```json
{ "chat": "c8f3a91b2c04", "text": "...", "skill": "" }
```

İd yolda taşınamaz, çünkü boş olabilmesi gerekiyor ve boş bir yol parçası adresin kendisini
değiştirir. Gövde bunu doğal taşıyor: *"hangi sohbete"* sorusu, *"ne yazıldı"* sorusuyla aynı yerde
duruyor.

İki alternatif de reddedildi. `/chats`'i gönderme adresi yapmak ismi yalancı yapardı — o adres bir
sohbet listesi. Yolda isteğe bağlı bir parça (`/chats//messages`) ise boş id'yi adresin şekline
sızdırırdı.

## Boş id yaratır, tanınmayan id yaratmaz

Gövdedeki `chat` **boşsa** ya da hiç yoksa, sunucu sohbeti yaratır. **Doluysa ama diskte yoksa**
404 döner ve hiçbir şey yaratmaz.

Bu ayrım kasıtlı: "bulamadıysan yarat" kuralı bir yazım hatasını sessizce ikinci bir sohbete
çevirirdi, ve kullanıcı ilk sohbetini kaybettiğini ancak listeye bakınca fark ederdi.

## Hangi kural kalıyor

`start_chat` ölür; **`append_message` yaratmayı devralır.** Yol haritasının şikâyeti zaten ikisinin
aynı işi yapmasıydı, ve bir mesajın gelişi tek bir kural.

`append_message` iki şey daha alır: projeyi doğrulayabilmek için `project_store`, ve yaratacaksa
kullanacağı `new_id`. Boş bir `chat_id` yaratma dalını açar; dolu olan bugünkü yola gider.

**İkisi de sonda, varsayılanlı adlandırılmış parametre.** Konumsal olsalardı bugünkü her çağrı
kaymak zorunda kalırdı — `stream_answer`'ınki dahil, ki o yaratmayı hiç kullanmıyor. Sonda
durunca ekleyen çağıran hiçbir şey öğrenmiyor, yaratan çağıran ikisini veriyor. Varsayılanların
dürüstlüğü de burada: yalnız yaratma dalının ihtiyacı olan şeyler.

`stream_answer` cevabı yazarken aynı kuralı çağırmaya devam eder. Her zaman gerçek bir id verdiği
için yaratma dalına hiç girmez — dokunulmuyor.

## Yol haritasında fazla söz verilmiş bir yer

Madde 87 *"frontend'in ikinci gönderme yolu düşer"* diyor. **Düşmüyor** — düşen yalnız ayrı adres.

`startChat` gönderdikten sonra listeleri tazeliyor ve yeni adrese gidiyor; `send` iyimser balonu
koyup cevabı bekliyor. İkisi farklı işler, ve tek fonksiyona ancak **88**'den sonra inebilirler:
cevap aynı isteğin içine taşınıp yeni sohbetin id'si akışın ilk karesinde geldiğinde, geriye tek bir
akış kalıyor.

87'de iki çağıran duruyor ve **aynı kapıya vuruyorlar.** Kazanç sunucuda: bir uç, bir kural.

## Yanında düşenler

| Ne | Nerede |
|---|---|
| `post_chat` ucu | `routes.py` |
| `start_chat` use case'i ve dosyası | `domain/usecases/start_chat.py` |
| `post_message` ucunun adresi | `routes.py` — kural kalıyor, yol değişiyor |
| `startChatInProject`'in adresi | `useChatLists.js` — fonksiyon kalıyor, gövdesi değişiyor |

## Silinen testler

| Nerede | Ne |
|---|---|
| `test_start_chat.py` | **dosya tamamen** — kural ölüyor; iddiaları `test_append_message.py`'ye taşınıyor |
| `test_chats_api.py` | Eski iki kapıyı sınayan testler yeni kapıya yazılıyor: yaratma, boş metnin reddi, bilinmeyen projenin 404'ü, bilinmeyen sohbetin 404'ü, mesajın skill'i |

## Kırmızıya dönecek testler

**Arka uç — `test_chats_api.py`, yedi:**

1. Tek kapı **yaratır**: `chat` verilmeden gönderilen cümle 201 döner, sohbetin tek mesajı o
   cümledir, ve başlığı ondan gelir.
2. Tek kapı **ekler**: aynı adrese `chat` ile gönderilen cümle 200 döner, mesaj sayısı ikiye çıkar,
   başlık değişmez.
3. Eski yaratma ucu **yok**: `POST .../chats` → **405**. Adres GET'te duruyor, o yüzden 404 değil.
4. Eski ekleme ucu **yok**: `POST .../chats/<cid>/messages` → **404**. O adreste başka yöntem
   kalmıyor, yani kural tamamen gidiyor.
5. Tanınmayan bir `chat` → **404**, ve projede hiçbir sohbet doğmuyor.
6. Boş metin → **400**, `chat` verilse de verilmese de.
7. Tanınmayan proje → **404**.

**Arka uç — `test_append_message.py`, iki:**

8. `chat_id` boşken kural sohbeti yaratır: verilen `new_id`'yi kullanır, başlığı cümleden alır, ve
   mesajı skill'iyle yazar.
9. `chat_id` boşken boş metin yine reddedilir.

**Ön yüz — `App.test.jsx`, iki:**

10. Taslaktaki ilk cümle `/messages`'a gidiyor ve gövdesinde `chat` **yok**.
11. Bir sohbetteki cevap aynı adrese gidiyor ve gövdesinde sohbetin id'si **var**.

Toplam **on bir kırmızı**.

## Fixture bu turda taşınmıyor

`_started` bugün eski yaratma ucunu çağırıyor ve o dosyadaki testlerin çoğu ondan geliyor. Bu turda
**dokunulmuyor** — yeni kapı henüz yok, taşımak seksen testi aynı anda düşürür ve turun on bir
gerçek kırmızısı görünmez olur. 82'nin turunda öğrenilen şey bu.

Yeni kapının testleri kendi çağrılarını yazar. `_started` ve doğrudan eski kapıya giden testler
uygulama turunda, kodla birlikte taşınır.

Aynı sebeple `start_chat.py` bu turda **silinmiyor**: olmayan bir modülü import eden bir test dosyası
pytest'in toplama aşamasını düşürür. `test_start_chat.py` silinir, modül uygulama turunda gider.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `/answer` ve `/stop` adresleri | Sohbet id'sini yolda taşımaya devam ediyorlar; 88 ile 90'ın işi |
| `stream_answer` | `append_message`'ı gerçek bir id ile çağırıyor, yaratma dalına girmiyor |
| `Message.skill` ve `instruction_for` | 86'da yerleşti, değişmiyor |
| Taslak ekran | Duruyor; kalkan şey onun hangi uca gideceğine karar vermesi |
| Sohbetin başlığı ve 42 karakterlik kesme | Aynı kural, yalnız başka bir fonksiyonun içinde |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi, defterdeki `BRANCH` bir özellik dalını
gösterdiği için düşüyor.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
