# Madde 336 — Yalnız Queen Flash kalır · test turu

**Kaynak:** [yol haritasının 336'sı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-4a);
kararları *v9-4 — Model menüsü*'nde: DeepSeek'in 10 Eylül duyurusu — `deepseek-v4-pro` 14 Eylül'de
kapandı ve istekleri sessizce Flash'a gidiyor, `deepseek-v4-flash` artık bir takma ad, modelin
bugünkü adı `deepseek-flash`.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı, kararları yol haritasında.

## Ne kanıtlanacak

*Bitti sayılır:* cevaplar `deepseek-flash`'tan geliyor; *Queen Pro* hiçbir yerde seçilemiyor.

- **Arka uç yalnız `deepseek-flash`'ı biliyor.** `config.MODELS`'ta DeepSeek'ten tek satır kalır,
  `deepseek-flash`; iki eski ad tablodan çıkar. `grok-4.3`'ün satırı kalır — yorumu onu bilerek
  tutuyor. `DEFAULT_MODEL` ve `PROMPT_MODEL` `deepseek-flash`.
- **Eski sohbetler cevapsız kalmaz.** Diskteki mesajlar `deepseek-v4-flash` ya da `deepseek-v4-pro`
  diyor; `engine_for` ikisini de `deepseek-flash`'a düşürür — bilinmeyen bir adın bugünkü kuralı.
- **Ön uç yalnız Queen Flash'ı sunar.** `models.js`'in listesinde tek satır, id'si `deepseek-flash`;
  varsayılan da o. Seçici açılınca tek satır var, *Queen Flash*; *Queen Pro* yok. Yeni sohbetin ilk
  mesajı `model: "deepseek-flash"` taşır.

## Testler ne tutar, ne tutmaz

**Tutar:**

| Dosya | Ne |
|---|---|
| `backend/tests/test_config.py` | `MODELS`'un adları tam olarak `grok-4.3` ve `deepseek-flash`; `deepseek-flash`'ın adresi ve anahtarı; `DEFAULT_MODEL` ve `PROMPT_MODEL` `deepseek-flash`; `engine_for` bilineni kendisine, boşu, bilinmeyeni ve iki eski adı `deepseek-flash`'a çözer |
| `frontend/.../models.test.js` | listede tek id `deepseek-flash`, adı *Queen Flash*; varsayılan `deepseek-flash`; `modelName("deepseek-flash")` *Queen Flash* |
| `frontend/.../ModelPicker.test.jsx` | açık menünün satırları yalnız *Queen Flash*; satıra basmak `deepseek-flash`'ı verir; testlerin elindeki model `deepseek-flash` |
| `frontend/.../ChatScreen.test.jsx`, `ProjectScreen.test.jsx` | seçiciyi Pro'yla değil, menüde olmayan bir id'yle ya da Flash'la sınar; seçim `deepseek-flash` olarak yukarı gider |
| `frontend/src/App.test.jsx` | yeni sohbetin mesajı `deepseek-flash` taşır; seçici açılınca *Queen Pro* ekranda yok |

**Fiyatı değiştirmez:** satırın fiyat yazısı olduğu gibi tutulur — onu kaldırmak v9-4b'nin işi.

**Kayıt olan eski adlar kalır:** `test_stream_answer.py`, `test_file_chat_store.py` ve
`test_chats_api.py`'deki `deepseek-v4-*` adları diskteki ya da istekteki bir mesajın adı; o mesajlar
gerçekten var, ve testler adın olduğu gibi taşındığını tutuyor. `test_xai_engine.py` ve
`test_xai_client.py`'deki adlar da sahte istemcilerin anahtarı ya da tele giden bir ad örneği; hangi
adın bağlı olduğunu `test_config.py` tutar.

**Gerçek DeepSeek'e gidildiğini tutmaz:** o, anahtarla çalışan uygulamada görülür.

## Bu turda yazılmayanlar

- `config.py` ve `models.js` değişmez; uygulama turunda.
- `dist` derlenmez.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` ve `npm test --prefix
queen-agent/frontend` yeni iddiaları kırmızı verir; queen-editor'ün arka ucu 377'nin bilinen iki
kırmızısıyla kalır, ön ucu yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m336-yalniz-flash-testler-plan.md).
