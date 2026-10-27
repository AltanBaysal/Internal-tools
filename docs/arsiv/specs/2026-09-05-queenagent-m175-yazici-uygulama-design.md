# Madde 175 · uygulama turu — tek soruluk yol

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m175-yazici-testler-design.md).
Commit `ee7a2e6` 27 kırmızı bıraktı.

---

## Üç katman

**`XaiClient.write_once(messages)`** — `_request`'in akışsız yarısı. `tools` yok, `stream` yok,
`stream_options` yok. Cevap `{"text", "spent"}`: `choices[0].message.content` ve `_spent(payload)`.
Aynı `_spent`, akışta bir kareden okuduğu şeyi burada gövdenin kendisinden okuyor — iki servisin iki
şeklini bilen tek fonksiyon, ikinci bir kopyası yok.

`spent` her zaman sözlük *(`or {}`)*: çağıran bunu bir toplama ekliyor, ve havaya göre değişen bir
şekil, çağıranın her seferinde sormak zorunda kaldığı şekildir.

**`XaiEngine.write_once(system, user)`** — `self._clients[self._prompt_writer]`. `_chosen`
kullanılmıyor: burada seçilecek bir şey yok, rol sabit. `_for_xai` de kullanılmıyor — o `SYSTEM_PROMPT`'u
her isteğin başına koyuyor, ve buradaki sistem promptu çağıranın.

**`Engine.write_once`** — portta ilan. Docstring cevabın şeklini yazıyor, çünkü Protocol'ün gövdesi
yok ve şekli söyleyen tek yer orası.

## `complete` sökülüyor

Üç katmandan da. `XaiClient.complete` gövdesinin yarısı `write_once`'a geçiyor *(istek, hata
sarmalayıcıları)*, yarısı gidiyor *(mesajın tamamını döndürmek)*.

## `run_tool(..., engine=None)`

Beşinci parametre, ve bugün hiçbir dal ona bakmıyor. `ToolResult` beşinci alanını alıyor:
`spent`, varsayılan `None`. `namedtuple`'ın `defaults` üçlüsü dörtlü oluyor.

## `config.PROMPT_MODEL` ve `main.py`

`PROMPT_MODEL = "grok-build-0.1"`, `DEFAULT_MODEL`'in hemen altında ve kendi gerekçesiyle: biri eski
kaydın düştüğü yer, öteki bir rol. `main.py` üçüncü adı geçiriyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **781 yeşil**, ilk koşuda, tek kırmızı çıkmadan. 27'nin hepsi döndü; 770'ten farkın 11 olması,
   silinen iki testin *(`test_streaming_is_prepared_the_same_way`, artık ilkinin aynısı; ve modelin
   çağrıyla gitmediğini söyleyen ölü koruma)* çıkmasından.
3. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.
