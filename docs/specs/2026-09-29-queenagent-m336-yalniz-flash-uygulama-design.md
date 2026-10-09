# Madde 336 — Yalnız Queen Flash kalır · uygulama turu

**Kaynak:** [yol haritasının 336'sı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-4a);
[test turunun spec'i](2026-09-29-queenagent-m336-yalniz-flash-testler-design.md) ve onun commit'lenmiş
kırmızı testleri.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

İki dosya, ikisi de birer tablo. Model id'si FOUNDATION'ın 6. kararındaki gibi bir turun girdisi;
değişen yalnız hangi id'lerin var olduğu.

- **`backend/config.py`**
  - `MODELS`'ta DeepSeek'in iki satırı (`deepseek-v4-flash`, `deepseek-v4-pro`) yerine tek satır:
    `deepseek-flash`, aynı adres ve aynı anahtar. Satırın yorumu nedenini söyler: DeepSeek'in 10 Eylül
    duyurusu — Pro kapandı ve Flash'la cevaplanıyor, eski Flash adı bir takma ad.
  - `grok-4.3`'ün satırı ve yorumu olduğu gibi kalır.
  - `DEFAULT_MODEL` ve `PROMPT_MODEL` `deepseek-flash`. `DEFAULT_MODEL`'in yorumundaki *ikisinin
    ucuzu* cümlesi bugüne döner: bestecinin sunduğu tek model.
  - `DEEPSEEK_API_KEY`'in yorumu *bestecinin üç satırı*ndan söz ediyor; Madde 177'den beri yanlıştı,
    bugün satır bir. Yorum gerçeğe döner: iki anahtarın ikisi de bir satırı besliyor.
  - `engine_for` değişmez: tabloda olmayan id zaten varsayılana düşüyor, ve diskteki eski adlar
    artık tabloda olmayan id'ler.
- **`frontend/src/features/workspace/models.js`**
  - `MODELS` tek satır: `{ id: "deepseek-flash", name: "Queen Flash", detail: "$0.22 / $0.66 per 1M" }`.
    Fiyat yazısına dokunulmaz — v9-4b'nin.
  - `DEFAULT_MODEL` `deepseek-flash`.
  - Dosyanın baş yorumu bugüne döner: bir model, neden bir; *Queen Flash ve Queen Pro* yerine *Queen
    Flash*; *bunlar arasında seçmek bir fiyat sorusu* cümlesi — seçilecek iki şey yok artık — düşer,
    fiyatın kaynağı kalır.

**Değişmeyenler:** `ModelPicker.jsx` (tek satırlık menüyü aynı kodla çizer; seçiciyi v9-4b kaldırır),
`main.py` (tablodan kurar), `xai_engine.py` (bilinmeyen id varsayılana), FOUNDATION'ın 6. kararı
(tablo ve liste hâlâ modellerin ve fiyatlarının yeri), CODE-STANDARD'ın tabloları (dosya eklenmiyor,
silinmiyor).

## Eski sohbetler

Diskteki bir mesaj `deepseek-v4-pro` ya da `deepseek-v4-flash` diyorsa, `stream_answer` o adı
motora taşır; motor o adla bir istemci bulamaz ve varsayılana — `deepseek-flash`'a — döner.
`engine_for` de aynısını yapar. Kayıt olduğu gibi kalır: mesaj kendi adını taşımaya devam eder.

## Açık risk

Yol haritasının v9-10 bulgusu: belgeye göre Flash'ta düşünme modu varsayılan olarak açık, ve araçlı
isteklerde `reasoning_content` geri gönderilmezse API 400 dönebilir; eski ad `deepseek-v4-flash`
farklı davranıyor olabilir. Testler gerçek DeepSeek'e gitmiyor, bu yüzden bunu göremez. Gerçek
anahtarla, araç kullanan bir turda görülür — raporda koşucuya söylenir.

## Nasıl görülür

CLAUDE.md'deki dört satır: queen-agent'ın iki süiti yeşil, queen-editor'ün arka ucu 377'nin bilinen
iki kırmızısıyla, ön ucu yeşil. `dist` bu dalda derlenmez: koşucu birleştirirken derler.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m336-yalniz-flash-uygulama-plan.md).
