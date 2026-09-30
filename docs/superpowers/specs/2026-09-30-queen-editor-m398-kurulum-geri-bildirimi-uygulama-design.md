# Madde 398 — Ses motorunun kurulum hücresi geri bildirim veriyor, implementasyon turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m398 test turu](2026-09-30-queen-editor-m398-kurulum-geri-bildirimi-testler-design.md),
`2458fdde` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## `colab/console.py` — `run` yeniden yazılıyor

İmza aynı: `run(cmd, label, cwd=None, timeout=3600)`. Komut `subprocess.Popen` ile başlıyor:

- **stderr stdout'a katılıyor** *(`stderr=subprocess.STDOUT`)*: tek boru, iki akış yazıldığı sırayla.
- **Ortamda `PYTHONUNBUFFERED=1`** *(`env={**os.environ, …}`)*: `pip` bir Python programı, ve Python
  bir boruya yazarken satırlarını komut bitene ya da tampon dolana kadar tutuyor; bu değişkenle her
  satırı yazdığı an veriyor.
- **Çıktıyı `_echo` okuyor**, ayrı bir iş parçacığında: boruyu
  `io.TextIOWrapper(pipe, newline="", errors="replace")` ile satır satır okuyor, her parçayı geldiği
  an `print(parça, end="", flush=True)` ile hücreye basıyor, ve boş olmayan son beş satırı sağ
  boşlukları kırpılmış olarak `collections.deque(maxlen=5)`'te tutuyor.
  - `newline=""` satırbaşını olduğu gibi bırakıyor: curl'ün ilerleme satırı Colab'da yerinde
    güncelleniyor. `Popen`'in kendi `text=True`'su satırbaşını satır sonuna çeviriyor, o yüzden boru
    ikili açılıp sarmalanıyor.
  - `errors="replace"`: yerel kodlamanın okuyamadığı bir bayt `�` oluyor. Hata fırlatsa okuyucu
    ölür, boru dolar, ve komut süresi dolana kadar yazamadan bekler.
- **Ana iş parçacığı `proc.wait(timeout=timeout)` ile bekliyor.** Süre dolarsa
  `RuntimeError(f"{label}: timeout ({timeout}s)")`, bugünkü cümle.
- **`finally`: `proc.kill()`, `proc.wait()`, sonra `_echo`'nun bitmesi bekleniyor.** `kill` bitmiş
  bir komuta dokunmuyor *(`wait` dönüş kodunu yazdı, `Popen` bitmiş komuta sinyal göndermiyor)*, ve
  ikinci `wait` öldürülen komutu topluyor, bugünkü `subprocess.run` gibi; süresi dolan ya
  da kullanıcının hücreyi durdurmasıyla yarıda kalan komutu durduruyor — bugünkü `subprocess.run`
  da her hata yolunda komutu öldürüyordu, ve durdurulan bir `pip` arkada sürerse hücrenin yeniden
  çalıştırılması aynı ortama ikinci bir `pip` salar. `_echo`'nun beklenmesi çıktının sonunu hatadan
  ve dönüşten önce basıyor.
- **Çıkış kodu sıfır değilse** `RuntimeError(f"{label}: exit {kod}\n<son satırlar>")` — son beş
  satır, alt alta. Bugün hata stderr'in ya da stdout'un son beş satırını söylüyordu; iki akış artık
  tek, satırlar onun sonu.
- **`run` artık çıktıyı geri vermiyor.** Hiçbir çağıran okumuyordu *(`nodes.py`, `downloads.py`,
  defter)*, ve çıktı ekranda.
- `shell=isinstance(cmd, str)` bugünkü gibi.

**Neden okuyucu ayrı bir iş parçacığında:** süre. Borudan okumak komut yazana kadar bekliyor; hiçbir
şey yazmadan takılan bir komutu süresinde durduran `wait(timeout)`. Okuma ana iş parçacığında olsaydı
süreyi bir zamanlayıcı tutacak, ve komutun zamanlayıcıyla mı kendiliğinden mi öldüğünü ayrı bir
işaret söyleyecekti. `select` ile beklemek Windows'ta borularla çalışmıyor, ve takım orada da koşuyor.
Başka bir iş parçacığından basılan satır Colab'da hücreye gidiyor: o iş parçacığını başlatan hücre
çalışırken başka hücre yok.

**Yorumlar:** `run`'ın docstring'i neden stderr'in katıldığını, neden `PYTHONUNBUFFERED` verildiğini
ve neden `kill`'in her çıkışta çağrıldığını söylüyor; `_echo`'nunki neden `newline=""` ve
`errors="replace"` olduğunu.

## Defter

**Ses motoru hücresi *(`791a750a`)*:** klondan önce `log("MMAudio klonlanıyor…")`, `pip`'ten önce
`log("MMAudio kuruluyor…")`; `pip`'in komutu `["pip", "install", "-e", "."]` — `-q` çıkıyor. Satırın
saati aşamanın başladığı an: kullanıcı neyin ne zamandan beri sürdüğünü oradan okuyor, ve komutun
kendi çıktısı altından akıyor. Kod hücresinde yorum yok, yalnız bölüm başlıkları. Hücre NotebookEdit
ile bütün olarak yazılıyor; `git diff` yalnız bu üç satırı göstermeli.

**Değişmeyen:** custom node'ların `pip install -q`'su *(`colab/nodes.py`)* — madde ses motorunun
`pip`'ini adlandırıyor, ve `run` düzelince node'lar da ne söylüyorlarsa canlı söylüyor; ComfyUI
hücresinin `!` satırları; ağırlık hücresi *(`4449c5a7`)*; CODE-STANDARD — `console.py`'yi zaten
sayıyor, ve `run`'ın nasıl bastığını kod söylüyor.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. Defter 29.000 karakter tavanının altında kalır.
