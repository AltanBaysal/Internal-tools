# v14 Görev 29 — Tünelin taşıma protokolü: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** İki test eklemek; ikisi de düşecek. Defter bu döngüde değişmiyor.

**Architecture:** İkisi de defterin metnini okuyor — biri tünel komutundaki bayrağı, öteki bayrağın
yanındaki sebebi arıyor. Yardımcılar (`_source`, `_cell`) dosyada zaten var, yenisi eklenmiyor.

**Tech Stack:** pytest.

**Tasarım:** [v14 Görev 29 test spec'i](../specs/2026-08-24-queen-editor-v14-gorev-29-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** Bu döngü yalnız test dosyasına dokunur. `app.ipynb` bu commit'te olduğu gibi
  kalır — bayrak yok, teşhis hücresi yerinde.
- **Kırmızı bırakılır.** `xfail`/`skip` yok; testler düpedüz düşer ve commit mesajı bunu söyler.
- Dil: test adları, docstring'ler ve commit mesajı **İngilizce**; assert mesajları **Türkçe**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `python -m pytest queen-editor -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` | defterin metninin ne söylemek zorunda olduğu | başlık açıklaması genişler + 2 test eklenir |

---

### Task 1: Dosyanın başlık açıklaması genişler

**Files:**
- Test: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

**Interfaces:**
- Consumes: yok.
- Produces: yok.

- [ ] **Step 1: Modül docstring'inin ilk paragrafını değiştir**

Bugünkü ilk satır dosyanın yalnız üretici gruplarını tuttuğunu söylüyor; dosya çoktan bundan
geniş. Yerine:

```python
"""What the notebook's text has to say.

The notebook is the only thing that installs, configures and serves this app, and none of that can
run here -- a Colab cell does not execute in pytest. What text can still answer is whether the
notebook still says the things it must: every counted file is named, each producer sits behind its
own switch, the outside world is probed before the heavy work, and the tunnel is opened the way
that measured fast.

The notebook is read, never run.
"""
```

- [ ] **Step 2: Takımın hâlâ yeşil olduğunu gör**

Run: `python -m pytest queen-editor -q`
Expected: 709 passed. Docstring değişikliği hiçbir testi etkilemez; bu adım yazım hatası içindir.

---

### Task 2: İki testi ekle ve kırmızıyı gör

**Files:**
- Test: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

**Interfaces:**
- Consumes: dosyanın mevcut `_cell(marker)` yardımcısı.
- Produces: implementasyon döngüsünün uyması gereken sözleşme — bayrak `["--protocol", "http2"]`
  biçiminde, argüman listesinde; sebep aynı hücrede ve içinde `QUIC` geçiyor.

- [ ] **Step 1: İki testi dosyanın sonuna ekle**

```python
def test_the_tunnel_is_opened_over_tcp_rather_than_quic():
    """cloudflared speaks QUIC by default, and QUIC rides on UDP. Colab's network throttles UDP and
    leaves TCP alone: on 2026-08-24 the same photo took 17.74 s over the default tunnel and 0.18 s
    over one started with this flag -- same machine, same minute, ninety times apart. Without it a
    gallery of 81 photos is unusable and nothing in the app explains why."""
    flask_cell = _cell("# === Start Flask")

    assert '"--protocol", "http2"' in flask_cell, \
        "cloudflared varsayılan QUIC ile açılıyor — Colab'ın ağı UDP'yi kısıyor"


def test_the_protocol_flag_says_what_it_is_standing_in_for():
    """One word in an argument list, and nothing about it says a default was overruled. A reader
    who cannot see what it replaced is a reader who deletes it as noise -- and the gallery goes
    ninety times slower with no error anywhere. The reason has to travel next to the flag."""
    flask_cell = _cell("# === Start Flask")

    assert "QUIC" in flask_cell, \
        "Bayrağın neyin yerine geçtiği yazılmamış — sebebi olmayan bayrak silinir"
```

- [ ] **Step 2: İkisinin de düştüğünü gör**

Run: `python -m pytest queen-editor -q`
Expected: 709 passed, 2 failed. Düşenler yukarıdaki iki test; ikisi de `AssertionError` ile düşmeli
— `NameError` ya da boş dönen `_cell` gibi bir yazım hatasıyla değil.

Doğrulama: hata mesajı Türkçe assert cümlesini göstermeli. Göstermiyorsa `_cell("# === Start Flask")`
yanlış hücreyi buluyordur.

---

### Task 3: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Defterin dokunulmadığını doğrula**

Run: `git status --short`
Expected: yalnız test dosyası ve `docs/superpowers` değişmiş. `queen-editor/app.ipynb` bu listede
**olmamalı** — varsa bayrak yanlışlıkla konmuştur, geri alınır.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for the tunnel that speaks TCP

THESE TWO TESTS FAIL ON PURPOSE. The flag is the next commit.

Two rounds of measurement walked the chain link by link and cleared every
suspect: Drive, Flask, the browser cache, the CPU, the queue, and Colab's own
egress, which turned out to move 32.8 MB/s with the tunnel out of the way. One
variable was left. cloudflared speaks QUIC by default, QUIC rides on UDP, and
Colab throttles UDP while leaving TCP alone -- the same photo took 17.74 s over
the default tunnel and 0.18 s over one opened with --protocol http2.

The flag is one word in an argument list and says nothing about the default it
overrules, so an editor who cannot see what it replaced deletes it as noise and
the gallery silently returns to ninety times slower. These two pin the flag and
pin the reason written beside it.

Text, not behaviour: a Colab cell does not run in pytest. What the ninety times
proves is in the research note; what these guard is that the line survives.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** A1 → Task 2'nin birinci testi · A2 → Task 2'nin ikinci testi · spec'in istediği
docstring genişlemesi → Task 1. Spec'te olup planda karşılığı olmayan madde yok.

**Ad tutarlılığı:** Testlerin beklediği metinler — `"--protocol", "http2"` argüman listesi biçiminde
ve aynı hücrede geçen `QUIC` kelimesi — implementasyon döngüsünün uyacağı sözleşme. O döngü bunları
veri olarak alır, yeniden karar vermez.

**Bilerek dışarıda:** hücre bölünmesi. Flask hücresinin bitmesi ve canlı log'un kendi hücresinde
durması bugün zaten böyle, dolayısıyla testi bu döngüde hiç düşmezdi — hiç düşmemiş test bir şey
kanıtlamıyor.

**Bilerek zayıf:** ikisi de metin okuyor, davranış çalıştırmıyor. Bayrağın gerçekten hızlandırdığını
söyleyen şey ölçümdür ve o yapıldı; bu testlerin işi bayrağın sessizce kaybolmasını engellemek.
