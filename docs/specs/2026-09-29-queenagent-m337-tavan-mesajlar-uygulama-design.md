# Madde 337 — Tavan ve gösterge yalnız sohbetin mesajlarını ölçer · uygulama turu

**Kaynak:** [yol haritasının 337'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m337-tavan-mesajlar-testler-design.md); kırmızı
`1a8ac566`.

## Ne yazılır

Dört üretim dosyası, hepsi arka uçta. Kural `domain/`'de kalır *(FOUNDATION, Karar 4)*: tavan da ölçü
de sunucunun; ekran gelen sayıyı çizer.

**[chat.py](../../queen-agent/backend/features/workspace/domain/chat.py)**

- **`last_context` yerine `chat_size(chat)`:** açık satırdaki mesajların metninin harf sayısı × 3 ÷ 10,
  aşağı yuvarlanır. Açık satır, çünkü modele giden o *(Madde 195)*. Açıklaması neden yalnız metin
  sayıldığını — kutu yeni sohbette de aynı, kullanıcının sözü — ve neden tahmin olduğunu söyler.
- **`is_full`** `chat_size`'ı okur. `CONTEXT_CEILING` 50.000 kalır; açıklamasının ilk satırı artık
  *ne kadar gönderir* değil, *mesajları ne kadar büyüyebilir* der.
- **`Usage.context` silinir**, yorumuyla. Kalan üç alanın açıklaması doğru kalıyor.

Tam sayı aritmetiği, `0,3` yerine `× 3 // 10`: kayan nokta 50.000'in sınırında yuvarlama hatasıyla
bir harf kaydırabilir, tam sayı kaydırmaz.

**[stream_answer.py](../../queen-agent/backend/features/workspace/domain/usecases/stream_answer.py)**

- Turun faturası üç sayıyla toplanır; son turun büyüklüğünü koyan dördüncü argüman ve Madde 133'ün
  yorumu kalkar.
- Aracın kendi isteğinin eklendiği yerde `spent.context` ve *context'e dokunulmaz* cümlesi kalkar.

**[file_chat_store.py](../../queen-agent/backend/features/workspace/data/file_chat_store.py)**

- Yazarken `context` anahtarı yazılmaz; okurken okunmaz. Anahtarla yazılmış eski sohbetler zaten
  alan alan okunuyor: anahtar yok sayılır, ve sohbet bir sonraki yazılışında düşer. Göç yok.

**[routes.py](../../queen-agent/backend/features/workspace/presentation/routes.py)**

- `_chat_json`'da `context.sent` artık `chat_size(chat)`. Anahtar `sent` kalır — ön uç ve 343'ün
  göstergesi onu okuyor, ve yeniden adlandırmak ekranı aynı şeyi söylemek için yeniden kurar.
  Yorum bunu, Madde 133 yerine 337 ile söyler.
- Kapının reddi ve cümlesi değişmez: kapı `is_full`'u soruyor, ve dolu sohbetin bildirimi 352'nin
  (v9-1c).

## Yazılmayanlar

- **Ön uç:** sayı sunucudan geliyor; `ContextGauge.jsx` 343'ün, dokunulmaz. `dist` derlenmez.
- **Mesaj başına ölçü alanı ya da kırpma:** v9-1b'nin. `chat_size` açık satırı okuyor; kırpılan
  mesajları dışarıda bırakmak v9-1b'nin işi.
- **CODE-STANDARD ve FOUNDATION:** dosya eklenmiyor, çıkmıyor; tablolar aynı.

## Nasıl görülür

CLAUDE.md'deki dört satır: `python -m pytest queen-agent -q` yeşile döner, 932 test. queen-editor'ün
arka ucunda yalnız 377'nin iki kırmızısı kalır; ön uçlar yeşil.

**Tarayıcıda** (Claude'un): bir sohbette çok araç çağıran bir tur ya da büyük bir dosyayı okutan bir
tur çemberi büyütmüyor; çemberin payı yalnız yazılanlarla artıyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m337-tavan-mesajlar-uygulama-plan.md).
