# Madde 128 · Tur 2 (uygulama) — Tasarım

**Testler:** [2026-08-29-queenagent-m128-add-frames-testler-design.md](2026-08-29-queenagent-m128-add-frames-testler-design.md)
**Kırmızı commit'ler:** `f1b6017` *(aracın kendisi)*, `29c7096` *(izin kapısı)*
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Ne yazılıyor

Üç dosya.

### 1. `tools.py` · `_add_frames`

Sıra önemli, ve her adım bir reddi karşılıyor: dosya var mı → geçerli JSON mü → argüman liste mi →
dosyanın `frames`'i liste mi → liste boş mu. Beşi de geçilirse `frames.extend(coming)` ve yazım.

Üst düzey JSON bir sözlük değilse *(bir liste, bir sayı)* `.get` çağrılmıyor: `frames` `None`
kalıyor ve *"no frames list"* reddine düşüyor. Bir `AttributeError` modele hiçbir şey anlatmazdı.

**Doğrulama yok.** Ne verilirse ekleniyor; şema doğrulaması `build_prompts`'ta, `BadStructure` ile.
`_build`'ın ayrımı: *"The structure is the model's; the prompts are the code's."*

**Yazım `indent=2, ensure_ascii=False`.** İkincisi 1. ilke: kullanıcı bu dosyayı açıp elle
düzeltiyor, ve `ı` duvarı okuyamadığı bir dosya demek.

**Cevap iki sayı taşır.** `Added 2 frames to scene.json; it holds 4 now.` İkincisi tuzağı görünür
tutuyor — ekleme idempotent değil, ve aynı çağrı iki kez koşarsa sayı bunu söylüyor.

`WRITES_FILES`'a **girmiyor**: var olan bir dosyayı değiştiriyor, yani kart çıkmıyor. `edit_file`'ın
kuralı.

### 2. `modes.py` · edit kipi sormadan koşar

`_WITHOUT_ASKING[EDIT]`'e giriyor. Ask ve plan kipinde kapı duruyor — dosyayı değiştiren bir araç,
ve konum vermemesi onu yazmayan bir araç yapmıyor.

### 3. `skills.py` · prompt+ araca geçiyor

*"Add frames with edit_file in batches of five, each on disk before the next"* →
*"Add frames with add_frames, in batches of five"*.

**Beşerli ritim kalıyor.** Sebebi çapa değildi: uzun cevabın sonunda kalite düşüyor, o yüzden model
yine parça parça çağırıyor — ama artık parçalar arasında okumuyor.

***"each on disk before the next"* düşüyor**, çünkü o cümle `edit_file` içindi: bir sonraki çapanın
tutması için önceki partinin diskte olması gerekiyordu. Araçla bu kendiliğinden.

Metin kısalıyor, ve 130'un kelime tavanı oradan açılıyor *(123'ün kuralı: bir cümle ancak bir cümle
silinerek girer)*.

## Değişmeyen

`edit_file` — var olan bir kareyi düzeltmek ve harita girdisi değiştirmek hâlâ onun işi, ve 132'nin
`replace_all`'ı tam da o harita işi için. `build_prompts`, şema, 131'in numaralı okuması, 129'un
kabı, prompt+'ın şema çağrısı ve elle-kurma yasağı.

## Bilerek yapılmayanlar

Kare silme ve araya sokma. Şema doğrulaması. Ön yüz — `dist` derlenmiyor.
