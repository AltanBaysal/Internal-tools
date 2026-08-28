# Madde 124 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 124
**Dal:** `feat/queenagent-m123-skill-rewrite` — kullanıcı onayı 29 Ağustos.

## Sorun

xAI'ın prefix cache'i otomatik ama isabet oranını `x-grok-conv-id` başlığı büyütüyor
(docs.x.ai): aynı kimlikle gelen istekler aynı cache'e yönlenir. QueenAgent'ın istekleri
başlıksız gidiyor — client `_request` yalnız Authorization ve Content-Type gönderiyor — ve
Colab denemesinde `cached` sayıları bunun bedelini gösterdi.

## Yol

Kimlik sohbetin kendisidir: `stream_answer` motora `conversation_id=chat_id` söyler, Engine
port'u ve `XaiEngine` onu aşağı taşır, `XaiClient.stream` boş olmayan kimliği
`x-grok-conv-id` başlığı olarak gönderir. `complete` yolu ellenmez: üretimde çağıranı yok.

## Bu turun testleri (dördü de kırmızı doğar)

- `test_xai_client.py` · `test_a_stream_names_the_conversation_it_belongs_to`:
  `stream(MESSAGES, conversation_id="c1")` isteği `X-grok-conv-id: c1` taşır.
- `test_xai_client.py` · `test_an_empty_conversation_id_sends_no_header`:
  `conversation_id=""` ile başlık hiç gitmez.
- `test_xai_engine.py` · `test_the_conversation_id_travels_down_to_the_client`:
  motor kimliği çeviri yapmadan client'a geçirir.
- `test_stream_answer.py` · `test_the_engine_is_told_which_chat_is_asking`:
  koşulan turda motorun gördüğü kimlik sohbetin id'sidir.

## Fake'ler

`FakeClient`, `ScriptedEngine` ve API testlerindeki fake engine'ler `conversation_id=""`
parametresini bu turda kazanır (kaydeder, davranış değiştirmez): imzayı ikinci turda
değiştirmek testleri koda uydurmak olurdu.

## Bilerek yapılmayanlar

`complete`'e kimlik eklenmez; kod bu turda ellenmez; ölçüm (cached artışı) kullanıcının
Colab denemesinindir.
