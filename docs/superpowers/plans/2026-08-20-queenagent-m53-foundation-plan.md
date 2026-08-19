# Madde 53 — FOUNDATION'ın iki kararı · Plan

**Tasarım:** [2026-08-20-queenagent-m53-foundation-design.md](../specs/2026-08-20-queenagent-m53-foundation-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Tek tur.** Test turu yok ve sebebi tasarımda yazılı: değişen üç şey de düzyazı, ve düzyazıyı tutan
bir test kelimeyi tutar. Bu, kuralın atlandığı anlamına gelmiyor — atlanamayacağı için açıkça
yazıldığı anlamına geliyor.

---

## Değişiklikler

**1. `queen-agent/FOUNDATION.md` — Karar 1**

Başlık "The app runs on the user's own machine" → makine **ve** paylaşıldığında Colab. Gövde:
yerel birincil kalır ve GPU gerekçesi korunur; kararı değiştiren şeyin paylaşmak olduğu ve
alternatifin elden gönderilen bir exe olduğu; uygulamanın zaten defterin istediği şekilde olduğu
(`QUEENAGENT_ROOT`, anahtar kökün altında, tek bağımlılık Flask). Sonuç cümlesi **kural kipinde**:
adres herkese açık bir tünel olduğu için parolasız sunulamaz. Kernel proxy'nin neden elendiği tek
cümle.

**2. `queen-agent/FOUNDATION.md` — Karar 3**

"`dist/` commit'lenmez" → commit'lenir, **kaynağıyla aynı commit'te**. Gerekçe: geliştirici ile
çalışma ortamı artık aynı makine değil (Karar 1). Sonuç: bir frontend değişikliği `dist` yeniden
derlenip eklenmeden bitmiş sayılmaz, ve `test_dist_is_committed.py` bunu reddeder.

**3. `CLAUDE.md` — komut bloğu**

Bugün queen-agent'ı "dist commit'lenmez, önce derle" diye, queen-editor'ü istisna diye anlatıyor.
İkisi aynı kurala geldiği için blok yeniden düzenlenir: iki derleme satırı birlikte ve kural bir kere;
QueenAgent'ın yerel koşusu ayrı ve **birincil** olarak; queen-editor'ün yerel koşusunun olmadığı
notu korunur.

**4. `queen-agent/README.md`**

Derleme satırına "yalnız kaynak değişince gerekiyor" notu, ve bundle'ın neden commit'lendiğini
söyleyen kısa bir paragraf — FOUNDATION'ın iki kararına bağlanarak. **`app.ipynb` anılmaz.**

**5. `queen-agent/CODE-STANDARD.md` — satır 12** *(plan yazıldıktan sonra bulundu)*

Plan dört belge saymıştı, yanlış saymış: CODE-STANDARD da "`dist/` is not committed" diyor. Aracın
bağlayıcı kurallarından biri, ve orada bırakılması bu maddenin ortadan kaldırmak için var olduğu
çelişkinin ta kendisi olurdu. FOUNDATION Karar 3'e bağlanarak düzeltilir.

## Doğrulama

- Takım koşulur: **358**, değişmemeli. Kod değişmiyor; koşmanın sebebi, değişmediğini görmek.
- Beş belgede de "dist is not committed" benzeri bir kalıntı kalmamalı.
- README'de var olmayan bir dosya adı geçmemeli.
- `docs/superpowers/` altındaki eski planlarda kalan geçişlere **dokunulmaz**: onlar yazıldıkları
  günün kaydı ve kasten eskiyorlar.

## Bilerek yapılmayan

- FOUNDATION'ın diğer kararlarına dokunulmuyor. Karar 5 ("tek kök, `QUEENAGENT_ROOT`") Colab'da da
  aynen doğru — kök Drive'a bakıyor, kural değişmiyor.
- Parola kapısı yazılmıyor; bu madde onu yalnız **gerektiriyor**. Yazan Madde 60.
