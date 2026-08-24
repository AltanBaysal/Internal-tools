# v14 Görev 29 — Tünelin taşıma protokolü: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** İki kırmızı testi yeşile döndürmek — defterin tüneli TCP üstünden açsın.

**Architecture:** Tek dosya, tek hücre. Tünel çağrısına bir bayrak ve üstüne tek satır sebep girer.
Aynı defterin CONFIG hücresindeki dal adı bu koşunun dalına çevrilir; ikisi de "defteri bu koşunun
gerçeğine uydurmak" olduğu için aynı commit'te.

**Tech Stack:** Jupyter notebook (Colab), cloudflared, pytest.

**Spec:** [v14 Görev 29 implementasyon spec'i](../specs/2026-08-24-queen-editor-v14-gorev-29-uygulama-design.md)

## Global Constraints

- **Test dosyasına dokunulmuyor.** Kırmızı commit'te ne yazıldıysa o kalır; testi koda uydurmak
  turun anlamını yok eder.
- Değişen tek dosya: `queen-editor/app.ipynb`.
- Defter JSON'dur: **NotebookEdit ile düzenlenir.** `Edit` bu dosyayı reddeder, kabuk üzerinden
  düzenlenmez.
- Bayrak **iki ayrı dize** olarak yazılır: `"--protocol", "http2"`.
- Yorumda `QUIC` **büyük harfle** geçer — A2 birebir bunu arıyor.
- Dil: defterdeki yorumlar **İngilizce**, commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `python -m pytest queen-editor -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/app.ipynb` · Flask hücresi | uygulamayı kurar ve dışarı açar | tünel çağrısı + tek satır sebep |
| `queen-editor/app.ipynb` · CONFIG hücresi | koşunun neyi nereden klonlayacağı | dal adı + iki satır sebep |

Tek dosya olduğu için iki hücre tek görevde birleşiyor: ayrı görevler ayrı commit ister, oysa bunlar
birlikte anlam taşıyor.

---

### Task 1: Defter bu koşunun gerçeğine uyar

**Files:**
- Modify: `queen-editor/app.ipynb` — `# === Start Flask (background) + cloudflared tunnel ===` ve
  `# === CONFIG ===` hücreleri

**Interfaces:**
- Consumes: kırmızı testlerin sözleşmesi — `"--protocol", "http2"` argüman listesi biçiminde, ve
  aynı hücrede geçen `QUIC`.
- Produces: yok.

- [ ] **Step 1: Flask hücresinde tünel çağrısını değiştir**

Hücrede `tunlog = "/content/cloudflared.log"` satırını bul. Onu izleyen `subprocess.Popen(...)`
çağrısı, araya giren yorumla birlikte şu hâle gelir:

```python
tunlog = "/content/cloudflared.log"
# --protocol http2: Colab throttles the default QUIC. Same photo, 17.74 s -> 0.18 s.
subprocess.Popen(["/content/cloudflared", "tunnel", "--protocol", "http2",
                  "--url", f"http://127.0.0.1:{APP_PORT}"],
                 stdout=open(tunlog, "w"), stderr=subprocess.STDOUT)
```

Hücrenin geri kalanı — Flask'ın başlatılması, sağlık yoklaması, linkin beklenmesi, canlı log —
olduğu gibi kalır.

- [ ] **Step 2: CONFIG hücresinde dal adını değiştir**

Bugünkü satır:

```python
BRANCH       = "main"                       # released work lands here; a dev run points this at its own branch
```

Yerine:

```python
# The notebook and the code it clones are one thing: the clone cell asserts on files this run
# added, so a branch without them stops before anything installs. Back to main once this lands.
BRANCH       = "feat/queen-editor-v4"       # released work lands in main; a dev run points here
```

- [ ] **Step 3: İki testin de yeşile döndüğünü gör**

Run: `python -m pytest queen-editor -q`
Expected: **711 passed.**

Düşen kalırsa: `test_the_tunnel_is_opened_over_tcp_rather_than_quic` hâlâ kırmızıysa bayrak tek
dize olarak yazılmıştır (`"--protocol http2"`), ikiye ayır.
`test_the_protocol_flag_says_what_it_is_standing_in_for` kırmızıysa yorumdaki `QUIC` küçük harfle
yazılmıştır.

---

### Task 2: Yeşili doğrula ve commit'le

- [ ] **Step 1: Yalnız defterin değiştiğini doğrula**

Run: `git status --short`
Expected: `queen-editor/app.ipynb` ve `docs/superpowers` değişmiş.
`queen-editor/backend/tests/...` bu listede **olmamalı** — varsa test koda uydurulmuştur, geri
alınır ve Task 1'e dönülür.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/app.ipynb docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the tunnel speaks TCP

Green. The gallery was unusable because cloudflared opens its tunnel over QUIC
unless told otherwise, and Colab throttles that transport. Nothing in the app
was at fault: Drive, Flask, the cache, the CPU and the queue all measured
clean, and Colab moves 32.8 MB/s once the tunnel is out of the way.

One flag. The same photo: 17.74 s before, 0.18 s after. The measurement is in
docs/superpowers/research/2026-08-23-queen-editor-galeri-yavasligi.md

The branch name travels with it. The clone cell asserts on files this run
added and main does not carry them yet, so the notebook as committed could not
open at all -- which is also why this line has to go back to main once the run
lands there.
EOF
git log --oneline -1
```

---

### Task 3: Yol haritasında maddeyi işaretle

- [ ] **Step 1: 29. maddeyi ✅ yap, sayacı ilerlet**

`docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md`:
- Madde 29'un **İş** hücresi `✅ **Galeri çok fotoğrafta...**` diye başlar.
- Başlıktaki `**Durum:** 26/30` → `**Durum:** 27/30`.

Yol haritasının kendi kuralı: iki tur bitip takım yeşile dönünce madde işaretlenir. Ekranda
görülecek olan Colab turunda görülür.

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md
git commit -F - <<'EOF'
docs(queen-editor): item 29 is done in code, and waits for the tour

Both tours are in and the suite is green. What the tour still has to say is
whether a gallery of a hundred photos now fills at a speed a person calls fast
-- the flag is measured, the experience is not.
EOF
```

## Self-Review

**Spec kapsamı:** A1 → Task 1 Step 1'in argüman listesi · A2 → aynı adımın yorumu · spec'in dal adı
bölümü → Task 1 Step 2 · spec'in doğrulama bölümü → Task 1 Step 3 ve Task 2 Step 1 · spec'in
"kapsam dışı"ndaki ön yüz maddesi → Task 2 Step 1'in `git status` kontrolü. Spec'te olup planda
karşılığı olmayan madde yok.

**Ad tutarlılığı:** Testlerin beklediği iki metin — `"--protocol", "http2"` ve `QUIC` — Task 1'de
birebir aynı biçimde yazılıyor. Plan bunları yeniden karar konusu yapmıyor, kırmızı commit'ten veri
olarak alıyor.

**Yakalanan iki tuzak:** bayrağın tek dize yazılması ve `QUIC`'in küçük harfle yazılması. İkisi de
sessiz hata değil — testler düşer — ama sebebi görünmez, o yüzden Step 3'te adıyla yazılı.

**Bilerek testi yok:** dal adı. Sabitleyen bir test main'e inerken kaçınılmaz olarak kırılır; yanlış
şeyi korur, doğru işi engellerdi. Yerine, satırın kendi yorumu geri dönmesi gerektiğini söylüyor.
