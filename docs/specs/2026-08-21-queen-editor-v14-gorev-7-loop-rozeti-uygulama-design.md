# v14 · Görev 7 — Galeride loop rozeti · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-7-loop-rozeti-testler-design.md) —
kararlar orada verildi ve commit edilmiş on üç test onları tarif ediyor.

## Değişen dosyalar

Zincirin dört halkası, dört dosya, artı rozetin kelimesi için beşinci.

### 1 · `domain/run_loop.py` — mod satıra yazılıyor

Üretilen katmanın satırına, işin modu varsa geçiyor:

```
record.append(project, {…, "createdAt": now(), **_mode_of(current)})
```

`_mock` değil, küçük bir yardımcı: `{"mode": production_mode.of(job)}` — ama yalnız işin kendi
alanı varsa. Hangi işlerin modu olduğu kuyruğun kuralı ve motor onu ikinci kez yazmıyor. Değer
`production_mode.of` ile okunuyor, çünkü render de aynı okumayı kullanıyor (`_end_for`) ve satırın
işi videonun ne olduğunu söylemek.

### 2 · `data/photo_record.py` — mod hücreye katlanıyor

`slots()` içinde, `error`'ın yanına: satırda dize bir `mode` varsa hücreye geçiyor. Sahte kayıt
(test turunda) zaten böyle yapıyor; bu, gerçeğin ona yetişmesi.

### 3 · `domain/usecases/list_frames.py` — kare `modes` alıyor

`_reasons` ile birebir aynı şekildeki `_modes(cells)`, ve iki `frames.append` çağrısında da yeni
alan. Boş harita da bir cevap: modu olmayan katmanlar haritada yok.

### 4 · `domain/copy_frame.py` — kopyalanan katman modunu götürüyor

`carry_layers`, taşıdığı her katman için karenin `modes` haritasına bakıyor ve varsa satıra
koyuyor. Kaynağı karenin kendisi, çünkü `carry_layers` zaten `layers` ve `prompts`'u oradan
okuyor — üçüncü bir yerden okumak, kopyanın kaynağını üçe bölerdi.

### 5 · `features/photo_generation/layer_words.js` — karonun kelimesi

`owned(frame)` süzgeçten sonra bir eşleme daha yapıyor: video satırının kelimesi, karenin
`modes.video`'su loop ise `"loop"` oluyor. Eşleme süzgecin **sonrasında**, yani patlamış bir katman
hiçbir kelime taşımıyor.

Küçük harf, çünkü komşuları "video" ve "ses". Kimlik `production_modes.js`'ten (`LOOP`) geliyor;
kelime burada, çünkü burası ekrandaki kelimelerin evi.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor.
