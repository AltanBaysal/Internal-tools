# Madde 72 — Grok Build varsayılan ve tek model · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m72-grok-build-tek-model-testler-design.md) ·
**Testler:** `cac7d39` — arka uçta 1, ön yüzde 6 kırmızı.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## İki dosya

### `backend/config.py`

`XAI_MODEL`'in varsayılanı `grok-build-0.1` oluyor, ve üstündeki gerekçe onunla birlikte. Bugünkü
gerekçe *"yarı fiyat ve iki katı bağlam"* diyor; ikisi de artık doğru değil — fiyat gerçekten
düşüyor ama bağlam dörtte bire iniyor, ve bu bilinerek seçildi.

Yorumun bugünü söylemesi şart: *bir açıklama yalnız bugün doğru olanı söyler* **(CLAUDE.md)**. Yeni
hâli fiyatı da pencereyi de yazıyor, ve pencerenin kabul edilmiş bir bedel olduğunu.

### `frontend/.../models.js`

`MODELS` tek satıra iniyor:

```js
export const MODELS = [{ id: "grok-build-0.1", name: "Grok Build", detail: "$1 / $2 per 1M · 256k" }];
```

Dosyanın başındaki üç paragraf da değişiyor. Bugün orada duran şeyler — hangi modellerin sunulduğu,
`grok-4.5`'in neden dışarıda bırakıldığı, tasarımın var olmayan model adları yazdığı — hepsi altı
satırlık bir liste hakkındaydı. Tek satır kalınca söylenecek şey başka: **neden bir tane**, ve
sunulmayan bir id'nin ham gösterilmesinin neden artık daha çok işe yaradığı.

`modelName`'in kendisine dokunulmuyor. Zaten doğru davranıyor — listede olmayan id'yi olduğu gibi
yazıyor — ve bu madde onu istisnadan kurala çeviriyor: kullanıcının diskindeki her eski sohbet
şimdi o yoldan geçiyor.

## Bunun ekranda görüneni

| Nerede | Ne olur |
|---|---|
| Yeni sohbet | Grok Build ile açılır |
| Menü | Tek satır, işaretli |
| `grok-4.3` taşıyan eski sohbet | Düğmede `grok-4.3` yazar, menüde hiçbir satır işaretli değildir |
| O sohbete yazılan yeni mesaj | Hâlâ `grok-4.3`'e gider — kayıt temizlenmedi |

Son satır kullanıcının kararı *(26 Ağustos: "başka bir şey istemiyorum")*. O sohbeti Grok Build'e
almanın yolu duruyor: menüyü açıp tek satıra basmak.

## Dokunulmayan

- **`ModelPicker.jsx`.** Seçici kalıyor. Tek satırla duruyor, ve bu kullanıcının kendi kararı.
- **`stream_answer.py`.** Sohbetin kendi seçimini göndermeye devam ediyor.
- **`routes.py`, `file_chat_store.py`.** Sunucu `MODELS`'ı hiç bilmiyor: liste metin, ve metin
  arayüzün.
- **Diskteki hiçbir kayıt.** Göç yok, temizlik yok.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** Ön yüzde **513**, hepsi yeşil. Arka uçta **2 failed, 443 passed** — ikisi
defterin dalı, ve deneme bitip defter `main`'e çevrilince ikisi de yeşile döner.

**Düşmemesi gerekenler:** `Menu.test.jsx` ile `Composer.test.jsx`'in `"Grok 4.6"` yazan testleri —
o metin orada rastgele, ve o iki bileşen `MODELS`'ı hiç görmüyor. `test_model_api.py`'nin ikisi de:
varsayılanı kendileri enjekte ediyorlar. Biri düşerse liste sızmış demektir.

`dist` **kaynağıyla aynı commit'te** derleniyor.
