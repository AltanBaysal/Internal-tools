# Madde 398 — Ses motorunun kurulum hücresi geri bildirim veriyor, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Deneme kullanıcının, koşunun sonunda: Colab'da ses motoru hücresini
çalıştırıp aşama satırlarını ve `pip`'in akan çıktısını görmek.

## Bugün ne oluyor

Ses motorunun kütüphane hücresi *(`791a750a`)* MMAudio'yu `git clone` ile klonluyor ve
`pip install -e . -q` ile kuruyor, ikisi de [colab/console.py](../../../queen-editor/colab/console.py)'deki
`run` ile. `run` komutu `subprocess.run(..., capture_output=True)` ile çalıştırıyor: çıktı iş bitene
kadar tutuluyor ve ekrana hiç basılmıyor — yalnız komut başarısız olursa son beş satırı hataya
giriyor. Hücre başlarken de bir şey yazmıyor, ve kurulum 30 dakikaya kadar *(`timeout=1800`)* sessiz
sürebiliyor. `run`'ı custom node kurulumu *(`colab/nodes.py` — git, pip)* ve indirmeler
*(`colab/downloads.py` — curl, aria2c)* de kullanıyor; onların çıktısı da iş bitene kadar görünmüyor.
`run`'ın bugün hiçbir testi yok.

## Kural

**(1) `run` komutun çıktısını geldiği anda hücreye basıyor**, komut bitmeden. `pip` bir Python
programı, ve Python bir boruya yazarken satırlarını tamponda tutuyor — komut bitene ya da tampon
dolana kadar. Satır, komut kendisi flush etmese de geliyor: takılırsa neyin üstünde takıldığı görünür.

**(2) Komutun hata akışı da aynı yere, yazıldığı sırayla geliyor.** git, pip ve curl ilerlemelerini ve
hatalarını stderr'e yazıyor; neyin üstünde takıldığı iki akışın sırasından okunuyor.

**(3) Satırbaşı (`\r`) satırbaşı olarak kalıyor.** curl'ün ilerleme satırı kendini `\r` ile yeniden
yazıyor; Colab onu yerinde günceller. Satır sonuna çevrilirse iki saatlik bir indirme saniyede bir
yeni satır basar.

**(4) Bugünkü gibi — bu iki kural yeniden yazılırken korunuyor:** başarısız komut hatasında etiketini,
çıkış kodunu ve komutun kendi son satırlarını söylüyor, sebep uydurmuyor *(NOTEBOOK-STANDARD §2)*;
süreyi aşan komut durduruluyor, ve hata etiketini ve süreyi söylüyor.

**(5) Ses motoru hücresi her aşamayı başlarken bir satırla söylüyor** — klon ve pip: her `run`
çağrısının hemen önünde bir `log` satırı. Metin testte sabitlenmiyor; *"MMAudio kuruluyor…"* gibi
bir satırı uygulama turu yazıyor.

**(6) Ses motorunun `pip`'ine `-q` verilmiyor**: `pip`'in kendi çıktısı akıyor.

**Değişmeyen:** `run`'ı çağıran öteki yerler kendi komutlarıyla kalıyor — custom node'ların
`pip install -q`'su da; madde ses motorunun `pip`'ini adlandırıyor, ötekiler `run` düzelince ne
söylüyorlarsa canlı söylüyor. ComfyUI hücresinin `!pip` satırları IPython'un kendi kabuk komutları:
`run`'dan geçmiyor, çıktıları zaten akıyor. MMAudio'nun ağırlık hücresi *(`4449c5a7`)* `run`
kullanmıyor.

## Nasıl kanıtlanıyor

`run`'ın testleri gerçek bir komut çalıştırıyor: `sys.executable` ile başlayan küçük bir Python
programı, git'in, pip'in ve curl'ün yerine. Ağ yok. Canlılık bir el sıkışmayla gösteriliyor: program
bir satır yazıp testin bir işaret dosyası yaratmasını bekliyor, ve test o dosyayı ancak satırı
konsolda görünce yaratıyor. Çıktıyı sonuna kadar tutan bir `run`'da program işareti hiç görmüyor.
Zamana bakan bir test *(satırın saatini komutun bitişiyle karşılaştırmak)* hem yavaş hem kırılgan
olurdu; `subprocess`'i sahteleyen bir test de davranışı değil kodun biçimini sorardı.

## Yazılacak testler

### `test_colab_console.py` — yeni; koşularak

1. **Komutun satırı, komut sürerken konsola geliyor** — program `first` yazıyor, flush etmeden;
   sonra işaret dosyasını 5 sn'ye kadar bekliyor, görürse `seen`, göremezse `not seen` yazıyor. Test
   `sys.stdout`'un yerine, `first`'ü görünce işaret dosyasını yaratan bir konsol koyuyor. Konsolun
   satırları `["first", "seen"]`.
2. **Hata akışı aynı yere, sırasıyla geliyor** — program `one`'ı stdout'a, `two`'yu stderr'e,
   `three`'yi stdout'a yazıyor; konsolun *(`capsys`, out)* satırları `["one", "two", "three"]`.
3. **Satırbaşı korunuyor** — program stderr'e bayt olarak `10%\r50%\r100%\n` yazıyor; konsolda
   `10%\r50%\r100%\n` aynen var.
4. **Başarısız komut kendi son satırlarını söylüyor** *(bekçi)* — program `line 1` … `line 8`
   yazıp 2 ile çıkıyor; `RuntimeError`, mesajında etiket, `exit 2` ve `line 8` var, `line 1` yok.
5. **Süreyi aşan komut durduruluyor** *(bekçi)* — program 60 sn uyuyor, `timeout=1`;
   `RuntimeError`, mesajında etiket ve `timeout` var, ve `run` 30 sn dolmadan dönüyor.

Program satırlarını bayt ya da `print` ile yazıyor; Windows'ta `print`'in `\r\n`'si satırlara
`splitlines` ile bölündüğü için testleri değiştirmiyor. 3'teki bayt yazımı bu yüzden: orada `\r`'nin
kendisi soruluyor.

### `test_notebook_installs_the_producer_groups.py` — defter, okunarak

6. **Ses motoru hücresi her aşamayı başlarken söylüyor** — `# === Ses motoru — MMAudio kütüphanesi ===`
   hücresinde her `run(` satırının önündeki satır bir `log(` satırı.
7. **Ses motorunun `pip`'i susturulmuyor** — aynı hücrenin `run(["pip", "install", …])` komutunda
   `"-q"` yok.

**Değişen — yok.**

**Bekçiler, bugün de yeşil:** `test_colab_nodes.py` ve `test_colab_downloads.py` — `run`'ı kendi
sahteleriyle değiştiriyorlar, ve `run`'ın imzası aynı kalıyor;
`test_the_sound_box_installs_the_library_not_just_a_weight_file`,
`test_the_freshly_installed_library_is_reachable_from_the_running_kernel`,
`test_every_name_the_notebook_imports_from_its_code_exists`; `test_notebook_stays_readable.py` —
defter iki satır uzuyor; ve `test_requirements.py` — `backend/` altındaki her üst düzey import'u pip'in
kuracağı bir paket sayıyor, o yüzden yeni dosya `colab.console`'u öteki `colab` testleri gibi bir
fixture'da import ediyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest'inde yalnız 1, 2, 3, 6 ve 7 kırmızı — 1 programın 5
sn'lik beklemesinden sonra. 4 ve 5 bugün de yeşil: `run`'ın bugünkü davranışını, yeniden yazılırken
korunsun diye tutuyorlar. Öteki üç satır yeşil.
