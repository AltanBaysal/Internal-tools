# v14 Görev 3 — Video ve sesin tohumunun kayda geçmesi: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı sekiz testi yeşile döndürmek: tohum modülü doğsun, motor
eksik tohumu seçip hem üreticiye hem kayda versin, bir işin üç denemesi tek tohum paylaşsın, ve ses
üreticisi tohum icat etmeyi bıraksın.

**Architecture:** Tohum seçimi tek yere iniyor — `run_loop`, işi üretime göndermeden hemen önce.
Orada olması zorunlu: sayının hem `producer.generate`'e hem `record.append`'e gitmesi gerekiyor ve
o ikisinin arasında duran tek yer burası. `seed.py` sayının aralığını tutuyor, `run_loop` ne zaman
sorulacağını.

**Tech Stack:** Python 3.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-3-tohum-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor** — bir istisna dışında ve o burada yazılı: üç var olan
  test üreticinin tohum olarak `None` aldığını iddia ediyor. Bu madde onu değiştirdiği için o
  iddiaların **yan bilgi** kısmı düşüyor; testlerin asıl söylediği (hangi prompt, hangi negatif,
  hangi model) aynen kalıyor.
- Yorumlar ve docstring'ler **İngilizce**.
- **Katman kuralı:** `seed.py` domain'de ve yalnız `random` import ediyor. `data/` katmanı tohum
  seçmiyor.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist/` **derlenmiyor**.
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `domain/seed.py` | tohumun aralığı | yaratılır |
| `domain/run_loop.py` | tohumun ne zaman seçileceği | `new_seed`, `chosen` |
| `data/mmaudio_generator.py` | ses üretimi | tohum portu kalkar |
| `backend/main.py` | bileşim kökü | iki lambda yerine tek fonksiyon |

---

### Task 1: Tohumun aralığı

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/seed.py`

**Interfaces:**
- Produces: `MAX`, `random_seed()`. Task 2 ve Task 4 buna dayanıyor.

- [ ] **Step 1: Modülü yaz**

```python
"""The number a render is reproducible by.

One range for the whole app: a photo job is planned in it (start_batch), and a layer job -- which
plans none -- is given one out of it when its turn comes. A seed is a seed wherever it was born, and
the same range written out in three files is how it stops being the same range.

The ceiling is torch's: manual_seed takes a long, and 2**31 - 1 is the width every graph and every
sampler in this app agrees on.
"""
import random

MAX = 2**31 - 1


def random_seed():
    return random.randint(0, MAX)
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_seed.py`'ın ikisi de yeşil. Beş motor testi ve ses testi hâlâ kırmızı.

---

### Task 2: Tohumu seçen an

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/run_loop.py`

**Interfaces:**
- Consumes: Task 1'in `random_seed`'i.
- Produces: `make_job(..., new_seed=seed.random_seed)`.

- [ ] **Step 1: Import'u ekle**

```python
from backend.features.photo_generation.domain import layers, policy, production_mode, queue, seed
```

- [ ] **Step 2: İmzaya parametreyi ekle**

```python
def make_job(runner, store, record, plan_store, producers, now, project,
             clock=time.monotonic, log=None, order_store=None, writers=None,
             new_seed=seed.random_seed):
```

ve docstring'e:

```
    `new_seed` is where a job with no seed of its own gets one. Chosen here rather than inside a
    producer because the number has to be written on the produced layer's row as well, and this is
    the only place standing between the render and that row. A default rather than a required
    argument: every caller reaches the queue through this function, and none of them has a reason to
    know about seeds.
```

- [ ] **Step 3: Seçilen tohumu işin ömrüne bağla**

```python
        attempts, holding, written, chosen = 0, None, None, None
```

ve iş değiştiğinde:

```python
            if name != holding:
                # A different job: its predecessor's attempts, written prompt and seed are not its
                # own.
                holding, attempts, written, chosen = name, 0, None, None
```

Tohum, denemelerin sayacıyla aynı satırda sıfırlanıyor. Ayrı bir yerde sıfırlansaydı ikinci deneme
başka bir tohumla giderdi ve "bu satırı tohumuyla bir daha üret" yalan olurdu.

- [ ] **Step 4: Tohumu seç ve iki yere birden ver**

`runner.report` çağrısının hemen üstüne:

```python
            if chosen is None:
                # A layer job is planned with no seed (queue_layer). Picked before the render, and
                # once per job rather than once per attempt.
                chosen = current["seed"] if current["seed"] is not None else new_seed()
```

Üreticiye:

```python
                data = producer.generate(prompt, current["negative"], chosen,
                                         current["model"], source=under,
                                         end=_end_for(current, store, slots, project, fid, under))
```

Kayda:

```python
            record.append(project, {"file": filename, "frame": fid, "layer": kind,
                                    "status": queue.DONE,
                                    "prompt": prompt, "negative": current["negative"],
                                    "seed": chosen, "createdAt": now()})
```

- [ ] **Step 5: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: beş motor testi yeşile döner. **Üç var olan test kırmızıya döner**: üreticiye giden
tohumun `None` olduğunu iddia ediyorlardı. Task 3 onları ele alıyor.

---

### Task 3: Artık doğru olmayan dört iddia

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`
- Modify: `queen-editor/backend/tests/test_producer_contract.py`

**Interfaces:** yok.

- [ ] **Step 1: Üç testin tohum iddiasını düşür**

Üçü de bir katman işinin üreticiye nasıl gittiğini sınıyor ve dörtlünün tamamını karşılaştırıyor:

```python
    assert generator.calls == [("kamera yaklaşır", "", None, "")]
```

Tohum artık motorun seçtiği bir sayı, yani testin bilemeyeceği bir şey. Karşılaştırma tohumsuz
alanlara iniyor:

```python
    assert [(call[0], call[1], call[3]) for call in generator.calls] == [("kamera yaklaşır", "", "")]
```

Testlerin söylediği şey değişmiyor: prompt yazıldı, negatif boş, model seçilmedi. Düşen tek şey,
bugünden itibaren doğru olmayan bir yan bilgi.

- [ ] **Step 2: Sözleşme testinin `None` tohumunu değiştir**

`test_producer_contract.py`'daki `test_a_producer_with_no_end_frame_takes_the_argument_anyway`
MMAudio'yu `None` tohumla çağırıyor. Ses üreticisi eksik tohumu icat ederken bu doğruydu; artık
`torch.manual_seed`'in sahtesi `None` görüyor ve haklı olarak patlıyor. Gerçek bir tohum veriliyor:

```python
    # A real seed, because the sound engine no longer invents one: the loop picks it before the
    # render so the number can also be written on the produced layer's row.
    sound = MMAudioGenerator(Sampler(), ffmpeg, tmp_dir=str(tmp_path)).generate(
        "dalga sesi", "", 4242, source=("P0_0_V1_0.mp4", b"MP4"), end=("P1_0.png", b"PNG"))
```

Testin sınadığı şey `end`'in alınıp yok sayılması; tohum orada yalnız çağrının bir parçası.

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: yalnız ses testi kırmızı.

---

### Task 4: Ses üreticisinin bıraktığı port ve bileşim kökü

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/mmaudio_generator.py`
- Modify: `queen-editor/backend/main.py`

**Interfaces:**
- Produces: `MMAudioGenerator(sampler, ffmpeg, tmp_dir=None)`.

- [ ] **Step 1: Portu ve icat eden fonksiyonu kaldır**

`import random` ve `_random_seed` siliniyor. Kurucu:

```python
class MMAudioGenerator:
    def __init__(self, sampler, ffmpeg, tmp_dir=None):
        self._sampler = sampler
        self._ffmpeg = ffmpeg
        self._tmp_dir = tmp_dir
```

- [ ] **Step 2: Neden seçmediğini söyle**

`generate` gövdesinde, `if not source` kontrolünden sonra:

```python
        # The seed arrives with the job and this engine invents none. A sound job is planned without
        # one, so the loop picks it before the render -- there, because the number also has to be
        # written on the produced layer's line, and a seed chosen here could never reach it.
```

- [ ] **Step 3: Bileşim kökünü tek fonksiyona bağla**

`main.py`'de `import random` düşüyor, `seed` import'a giriyor:

```python
from backend.features.photo_generation.domain import layers, seed
```

ve iki `lambda: random.randint(0, 2**31 - 1)` `seed.random_seed` oluyor (`start_batch` ve
`regenerate`).

- [ ] **Step 4: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 5: Yeşil commit

- [ ] **Step 1: Yol haritasını işaretle**

3. maddenin **İş** hücresi ✅ ile başlar, sayaç `2/31` → `3/31`. Maddenin metni de düzeltilir:
"üç üreticinin de kullandığı tohumu geri döndürmesi" artık olan şeyi anlatmıyor — tohumu motor
seçiyor.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the seed a job was produced with is written down

A layer job is planned with no seed and until now that None travelled into the render:
the sound engine invented a number nothing could read back, and the video graph kept
its -1, which rgthree only randomises in the browser widget. Neither reached the row,
so no video and no sound could be produced again.

The loop picks the seed instead, just before the render, and hands the same number to
the producer and to the record. Once per job rather than once per attempt: it is reset
on the line that resets the attempt counter, so all three tries of one job share it and
the row names the number every one of them used.

MMAudio drops its seed port. Two places choosing a seed is two different answers, and
the one chosen down there could never be written down.

main.py drops two copies of the range in favour of the one in the domain.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört dosyasının dördü de bir task'ta. `seed.py` → Task 1; `run_loop.py`
→ Task 2; `mmaudio_generator.py` ve `main.py` → Task 4. Spec'in "bitti sayılır"ındaki üç var olan
test → Task 3.

**Tip tutarlılığı:** `new_seed` argümansız çağrılan bir callable, üç yerde de öyle: `make_job`'ın
varsayılanı, testlerin `lambda: 777`'si, `main.py`'nin `seed.random_seed`'i.

**Kontrol edilen tuzak:** `chosen` `None` ile karşılaştırılıyor, doğruluk değeriyle değil. `if not
chosen` yazılsaydı tohumu 0 olan bir iş her denemede yeni tohum alırdı — ve 0 aralığın içinde geçerli
bir tohum.

**Kontrol edilen tuzak 2:** tohum `runner.report`'un üstünde seçiliyor, `try` bloğunun içinde değil.
İçinde seçilseydi, düşen bir denemeden sonra `continue` ile dönen döngü `chosen`'ı korurdu — bu
doğru olurdu — ama prompt yazımıyla aynı bloğa girmesi, tohum seçiminin bir yazar hatasıyla
sıfırlanabilmesi demekti.

**Kontrol edilen tuzak 3:** `current["seed"] is not None` — foto işinin kendi tohumu korunuyor.
Koşulsuz `new_seed()` yazılsaydı plan dosyasındaki tohum sessizce çöpe gider ve aynı plandan iki
farklı resim çıkardı.
