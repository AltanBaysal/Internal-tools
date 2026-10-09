# Madde 383 — Grok ve xAI anahtarı kalkar · test turu

**Kaynak:** [yol haritasının 383'ü](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), Dalga 7.
Kullanıcı, 30 Eylül: *"kalksın"*. 358'den beri her tur `config.DEFAULT_MODEL`'e, yani DeepSeek'e
gidiyor; tabloda `grok-4.3` satırı, ortamda ve notebook'ta `XAI_API_KEY` boşuna duruyor.

**Kullanıcıdan gereken:** hiçbir şey. Aşağıdaki adlandırma ve kapsam kararları teknik; koşu
kuralları gereği onları bu tur veriyor.

## Bitti sayılır

QueenAgent `XAI_API_KEY` olmadan açılıyor ve notebook onu sormuyor; QueenAgent'ın kodunda,
notebook'unda ve kendi belgelerinde (README, FOUNDATION, CODE-STANDARD, BACKLOG) Grok da xAI de
geçmiyor. `docs/` altındaki tarihî belgeler (roadmap, spec, plan) yazıldığı gibi kalır.

## Kararlar

**Taşıyıcı ve motor kalır, adları değişir.** `services/xai/client.py` bugün DeepSeek'i de taşıyan,
OpenAI uyumlu bir sohbet taşıyıcısı; giden Grok, bir modeli çağırma yeteneği değil. Yeni adlar ne
olduklarını söyler:

| Bugün | Yarın |
|---|---|
| `backend/services/xai/client.py` | `backend/services/model/client.py` |
| `XaiClient`, `XaiFailed`, `XaiNotConfigured` | `ModelClient`, `ModelFailed`, `ModelNotConfigured` |
| `backend/features/workspace/data/xai_engine.py` | `backend/features/workspace/data/model_engine.py` |
| `XaiEngine`, `ROLE_FOR_XAI`, `_for_xai` | `ModelEngine`, `ROLE_FOR_MODEL`, `_for_model` |
| `tests/test_xai_client.py`, `tests/test_xai_engine.py` | `tests/test_model_client.py`, `tests/test_model_engine.py` |

**Sohbet kimliği de gider.** `conversation_id` port'tan (`Engine.stream`) motora, motordan
taşıyıcıya iniyor ve tek bir iş görüyor: yalnız x.ai adresine `x-grok-conv-id` başlığını koymak.
DeepSeek'e hiç gönderilmiyor. Grok gidince bu yol hiçbir şey taşımayan bir parametre olur; yol
bütünüyle kalkar — port, motor, taşıyıcı ve `stream_answer`'ın `conversation_id=chat_id`'si.

**OpenAI uyumlu biçimler kalır.** Taşıyıcı, önbellek sayısını iki biçimde okuyor (iç içe
`prompt_tokens_details.cached_tokens` ve DeepSeek'in düz `prompt_cache_hit_tokens`'ı) ve bir araç
çağrısını hem tek parça hem parça parça birleştiriyor. İkisi de xAI'nin değil, konuştuğu protokolün
biçimleri; kod kalır, yorumlar protokolün adıyla konuşur.

**Tablo kalır, tek satırla.** FOUNDATION'ın 6. kararı hangi modellerin var olduğunu `config.py`'nin
tablosuna veriyor; tablo `deepseek-flash` satırıyla kalır.

## Testler ne tutar

1. **Süpürme (yeni: `tests/test_retired_provider.py`).** `queen-agent/` altındaki her dosyanın hem
   yolu hem içeriği `grok`, `xai` ve `x.ai`'yi (büyük-küçük harf ayırmadan) taşımaz. Dışarıda
   kalanlar: `frontend/dist` ve `node_modules` (üretilmiş), `__pycache__` ve noktayla başlayan
   klasörler (diskte kalan artık), `package-lock.json` (bir bütünlük özetinde harfler rastlantıyla
   yan yana geliyor), ve testin kendi dosyası — aradığı sözcükleri yazmadan arayamaz. Bugün kırmızı.
2. **Tablo (`test_config.py`).** `set(config.MODELS) == {"deepseek-flash"}`; satırın adresi ve
   anahtar adı; tablodaki her satır `engine_for`'dan geçer — bir satırın adını verdiği anahtar
   sabiti `config.py`'de yoksa uygulama açılışta düşer, bunu açılıştan önce bu test görür. Grok
   satırını koruyan iki test ve `XAI_API_KEY`'in iki testi silinir; anahtarın boşken boş dize olduğu
   iddiası `DEEPSEEK_API_KEY`'e taşınır.
3. **Notebook (`test_notebook.py`).** Notebook Secrets'tan tam olarak iki ad okur:
   `{"GITHUB_TOKEN", "DEEPSEEK_API_KEY"}`. xAI'nin üç testi silinir; anahtar değerinin basılmadığı
   kilit yalnız `DEEPSEEK_API_KEY` üzerinde kalır. Bugün kırmızı.
4. **Port (`test_ports.py`).** Yeni adlarla (`ModelEngine`, `ModelClient`) okunur; ve `Engine`,
   `ModelEngine`, `ModelClient`'in `stream`'i `conversation_id` almaz. Bugün kırmızı (import).
5. **Taşıyıcı (`test_model_client.py`, `git mv` ile).** Yeni adlar; örnek adres
   `https://api.deepseek.com`, model `deepseek-flash`. Sohbet başlığının üç testi silinir.
   Yorumlar xAI'yi değil protokolü anar.
6. **Motor (`test_model_engine.py`, `git mv` ile).** Yeni adlar; kimliğin taşıyıcıya indiği test
   silinir; sahte istemcinin `stream`'i `conversation_id` almaz.
7. **Sahte motorlar.** `test_stream_answer.py`, `test_chats_api.py`, `test_files_api.py`,
   `test_last_activity.py`, `test_pin_archive.py`, `test_projects_api.py`'deki sahte motorların
   `stream`'i port'la aynı imzayı taşır: `conversation_id` yok. `stream_answer` bugün onu
   geçirdiğinden bu dosyaların tur çalıştıran testleri kırmızıya döner.
   `test_the_engine_is_told_which_chat_is_asking` silinir.
8. **Adsız örnekler.** Eski bir kaydın modelini temsil eden `grok-4.3` örnekleri
   (`test_chats_api.py`, `test_file_chat_store.py`, `ChatScreen.test.jsx`) yine artık adı olan
   `deepseek-v4-pro` olur — anlamları değişmez. `Composer.test.jsx` ve `Menu.test.jsx`'teki
   `Grok 4.x` etiketleri `Flash`/`Pro` olur; `sse.test.js`'teki hata metni
   `the model answered 401: bad key` olur. `test_permissions.py` ve `test_stops.py`'de xAI'yi anan
   iki yorum modelin bağlantısını anar.

## Bu turda yazılmayanlar

Uygulama kodu, `main.py`, `config.py`, notebook ve belgeler uygulama turunda değişir. Ön yüz kodu
değişmez; `dist` yalnız bir test dosyası değiştiği için yeniden derlenmez.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` kırmızı: süpürme, tablo, notebook,
port ve taşıyıcı/motor dosyaları (import), ve sahte motoru değişen dosyaların tur çalıştıran
testleri. Ön yüz ve queen-editor süitleri yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-30-queenagent-m383-grok-kalkar-testler-plan.md).
