# Mira — Faz 6: Grok (Madde 13-14)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 5](2026-08-09-mira-faz-5-sohbet-ekrani-design.md)

**Kapsam:** `xai/` servisi (Madde 13) · mesaja gerçek cevap gelmesi (Madde 14).
**Kapsam dışı:** akış (Faz 7) · araçlar ve ajan döngüsü (Faz 8) · dosya (Faz 9).

---

## 1 · Doğrulanmış gerçekler

xAI dokümanından okundu, ezberden yazılmadı:

| | |
|---|---|
| Uç nokta | `POST https://api.x.ai/v1/chat/completions` |
| Kimlik | `Authorization: Bearer <anahtar>` |
| Gövde | OpenAI-uyumlu: `messages`, `tools`, `stream` |
| Cevap | `choices[].message` → `role`, `content`, `tool_calls` |
| Akış | `stream: true` → `data: {...}` satırları · metin `choices[0].delta.content` · bitiş `data: [DONE]` |
| Modeller | `grok-4.5`, `grok-4.3`, `grok-4.20-0309-reasoning`, `grok-4.20-0309-non-reasoning`, `grok-build-0.1`, `grok-4.20-multi-agent-0309` |

Varsayılan model **`grok-4.5`** ve `config.py`'de **tek satır**; değiştirmek bir satırlık iş.
Uç nokta da ayardan gelir (`XAI_BASE_URL`), çünkü testte sahte bir sunucuya çevrilebilmesi lazım.

## 2 · Neden `urllib`, neden `requests` değil

Servis stdlib'in `urllib.request`'ini kullanır. Gerekçe: tek bir POST ve bir SSE akışı için yeni bir
bağımlılık taşımak, kurulum adımı ve sürüm bakımı getirir; `urllib` ikisini de yapar ve Colab'da
olmadığımız için "zaten kurulu" avantajı da yok. Karar tersine dönerse tek dosya değişir — servis
sınırı tam olarak bunun için var.

## 3 · Servisin sözleşmesi

`XaiClient(api_key, model, base_url)`:

- `complete(messages, tools=None) -> dict` — asistan mesajını olduğu gibi döndürür (`content` ve
  varsa `tool_calls`). Faz 8 aynı metodu araçlarla çağıracak, o yüzden `tools` bugünden parametre.
- **Anahtar yoksa** `XaiNotConfigured` fırlatır. Uygulama yine açılır; yalnız cevap isteyen akış
  anlaşılır bir hata verir.
- HTTP hatasında `XaiFailed` fırlatır ve **sunucunun gerçek çıktısını taşır**: durum kodu + gövdenin
  kendisi. Uydurulmuş tek bir sebep yazılmaz — 401 "anahtar süresi doldu" demek değildir, yanlış
  model adı da 404 döndürür.

Servis **hiçbir ürün kavramı bilmez**: prompt yok, sohbet yok, dosya yok. Yalnız mesaj listesi alır,
asistan mesajı döndürür.

## 4 · Cevabın üretilmesi

Domain'e `Engine` portu girer: `complete(messages) -> dict`. `data/xai_engine.py` bunu servisle
gerçekler ve **sistem yönergesini** başa ekler.

**Cevap ayrı bir uç noktadan gelir:** `POST /api/projects/<pid>/chats/<cid>/answer`. Gövdesi yoktur —
sohbeti olduğu gibi alır ve cevabını üretir.

Gerekçe: mesaj iki yoldan doğuyor (yeni sohbetin ilki, var olan sohbetin devamı) ve cevabı gönderme
uç noktasının içine koymak, ilk mesajın cevabını başka bir yoldan istemeyi gerektirirdi — iki ayrı
cevap yolu. Tek bir `answer` uç noktası ikisini de karşılıyor. Faz 7'de akış eklendiğinde değişecek
yer de tek: burası.

Tarayıcının akışı her iki durumda aynı: **mesajı gönder, sonra cevabı iste.**

Sıra (Madde 14):

1. Kullanıcı mesajı **diske yazılır** (Faz 5'in `append_message`'ı ya da sohbeti kuran uç nokta).
2. `answer` çağrılır; sohbetin bütün mesajları motora gider.
3. Dönen metin `role="ai"` mesajı olarak **diske yazılır**.
4. Güncel sohbet döner.

Ekranda cevap beklenirken **üç yanıp sönen nokta** durur — tasarımın `typing` hâli. Sahte kısmi
cevap yoktur.

Motor patlarsa **kullanıcı mesajı diskte kalır** ve rota hatayı taşır: 502 + servisin gerçek satırı.
Tasarımın hata hâli tam olarak bunu istiyor — *"the user message stays"*.

**Sistem yönergesi `domain/prompt.py`'de.** Bir ürün davranışıdır, taşıma detayı değil; Faz 8'de
araçların ne zaman çağrılacağını da o dosya anlatacak.

## 5 · Katmanlar

| Katman | Ekleme |
|---|---|
| services | `xai/client.py` — `XaiClient`, `XaiNotConfigured`, `XaiFailed` |
| domain | `prompt.py` — sistem yönergesi · `ports.py` → `Engine` |
| domain/usecases | `answer_in_chat(chat_store, engine, project_id, chat_id, now)` |
| data | `xai_engine.py` — `Engine`'i servisle gerçekler |
| presentation | `POST …/messages` artık cevabı da üretir; `EngineFailed` → 502 |
| config | `XAI_MODEL`, `XAI_BASE_URL` |

`answer_in_chat` `append_message`'ı iki kez çağırır (biri kullanıcı, biri cevap) — kural kopyalanmaz.

## 6 · Testler

1. Anahtar yokken `XaiNotConfigured`.
2. HTTP 401 → `XaiFailed` ve mesajında **gövdenin kendisi** var.
3. Başarılı çağrı `choices[0].message`'ı döndürüyor.
4. İstek gövdesi `model` ve `messages` taşıyor; `tools` verilmediyse gövdede **yok**.
5. `answer_in_chat` cevabı sohbetin sonuna ekliyor ve diske yazıyor.
6. Motor patlarsa sohbet **hiç değişmiyor** ve `EngineFailed` çıkıyor.
7. Rota 502 döndürüyor ve gövdesinde servisin satırı var.
8. Sistem yönergesi motora giden listenin **başında** ve sohbette saklanmıyor; diskteki `ai` rolü
   xAI'ye `assistant` olarak gidiyor.
9. Ön yüz: mesaj gönderildikten sonra cevap isteniyor ve beklerken üç nokta çiziliyor.

Testlerde ağ yok: `XaiClient`'ın açtığı bağlantı bir sahteyle değiştirilir, `Engine` portu ise use
case testlerinde tamamen sahte.

## 7 · Kabul kriteri

`pytest` yeşil. Gerçek anahtarla: sohbete soru yaz → cevap gelir ve sayfa yenilenince durur; anahtarı
boz → kullanıcı mesajı durur, hata görünür.
