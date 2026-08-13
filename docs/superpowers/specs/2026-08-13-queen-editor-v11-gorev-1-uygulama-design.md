# v11 Görev 1 — xAI anahtarı yoklaması: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-13-queen-editor-v11-gorev-1-testler-design.md) ·
commit `635d26c` (sekiz test kırmızı)

Bu spec, `635d26c`'deki sekiz testi yeşile çevirecek kodu tanımlıyor. Testlerin çiviledikleri —
`xai_probe`, `fatal=INSTALL_VIDEO`, `"xAI yanıtı"`, kırpma satırının tam metni — **sözleşme**;
burada yeniden karar verilmiyor, uyuluyor.

## Yoklama neyi yoklar

**Uygulamanın yapacağı çağrının aynısını.** Yoklama xAI'a `POST /v1/chat/completions` gönderir —
uygulamanın video prompt'u için gönderdiği isteğin ta kendisi, tek farkı bir kelimelik gövdesi.

Sebebi araştırıldı: xAI'ın API dokümanında anahtarı doğrulamaya yarayan ayrı bir uç nokta yok
(`/v1/api-key` yok, `/v1/models` yok; belgelenen tek GET'ler deferred-completion ve responses).
Yani "anahtarı yoklayan hafif bir uç nokta" seçilemiyor. Bu bir kayıp değil, kazanç: uygulamanın
kendi çağrısını yoklayınca üç şey birden sınanmış oluyor — anahtar, model adı, erişilebilirlik.
Yoklama geçtiyse uygulamanın çağrısı da geçer.

**Model adı ve adres CONFIG'den gelir.** Bugün ikisi de `backend/config.py`'nin varsayılanı
(`grok-4.3`, `https://api.x.ai/v1/chat/completions`). Yoklamanın bunları bilmesi gerektiğine göre
tek kaynak defter olur ve uygulamaya `QE_XAI_MODEL` / `QE_XAI_URL` ile geçer — `QE_COMFY_ROOT`'ta
dün yapılanın aynısı. `config.py`'deki değerler yerinde kalır: yerel koşunun yedeği onlar.

## Karar tablosu

| Yoklamanın gördüğü | Anlamı | INSTALL_VIDEO açık | kapalı |
|---|---|---|---|
| 2xx | Çağrı çalışıyor | geç | geç |
| başka herhangi bir kod | Uygulamanın çağrısı da düşecek | **dur**, xAI'ın gövdesiyle | uyar, geç |
| ağ hatası (timeout, DNS) | Anahtar hakkında delil yok | uyar, geç | uyar, geç |

"Sadece 401 kötüdür" kuralı yazılmadı ve yazılamazdı: 2026-08-13'te gelen cevap **400**
(`invalid-argument / Incorrect API key provided`) idi. Yoklama uygulamanın çağrısının aynısı olduğu
için kural sadeleşiyor — 2xx değilse uygulamanın çağrısı da düşecek demektir.

Ağ hatasının durdurmaması bilinçli: timeout anahtar hakkında bir şey söylemiyor, ve bilmediği bir
şey yüzünden koşuyu kesen bir kontrol, kontrol değil engeldir.

**Anahtar yoksa yoklama hiç yapılmaz** — bugünkü davranış korunur: "yok — video prompt yazılamaz"
yazar ve geçer. Foto koşusu anahtarsız çalışır, bu değişmiyor.

## Kırpma — iki yer, iki sebep

- **Defter, secret'ı okurken** (`(userdata.get(...) or "").strip()`): yapıştırma burada oluyor,
  temizlik de burada. Yoklama ile uygulamaya giden değer aynı olsun diye okunduğu anda temizleniyor.
- **İstemci, kendi header'ını kurarken** (`(api_key or "").strip()`): istemci header'ının biçiminden
  kendisi sorumlu — defterden gelmeyen bir çağıran da (yerel koşu, test) doğru header alsın.

Aynı bilginin iki kez yazılması değil: biri yapıştırmayı temizliyor, öteki kendi çıktısını garanti
ediyor. Ve yalnız ikincisi çalıştırılabilir bir testle sınanabiliyor.

Kırpmanın yan etkisi: boşluktan ibaret bir anahtar boş anahtara dönüşüyor, yani `NotConfigured`
yolu — "XAI_API_KEY yok, Colab Secrets'a ekle" — nihayet o vakayı da yakalıyor. Bugün tek boşluk
o cümleyi atlayıp kullanıcıyı xAI'ın 400'üne yolluyor.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `queen-editor/app.ipynb` — CONFIG | Anahtar kırpılarak okunur; `XAI_MODEL`/`XAI_URL` tanımlanır; `xai_probe` tanımlanır ve `xai_probe(XAI_API_KEY, fatal=INSTALL_VIDEO)` çağrılır |
| `queen-editor/app.ipynb` — Flask | `QE_XAI_MODEL` ve `QE_XAI_URL` de geçirilir |
| `queen-editor/backend/services/xai/client.py` | Anahtar `__init__`'te kırpılır |

`log()` kullanılamaz: yardımcılar hücresinde tanımlı ve CONFIG'den sonra çalışıyor. Yoklama düz
`print` ve `raise RuntimeError` ile konuşur — CONFIG'in geri kalanının zaten yaptığı gibi.

## Kapsam dışı

- **Uygulamanın kendi açılışında yoklama yapması.** Amaç indirmeden önce haber vermek; uygulama
  zaten ayağa kalktıktan sonra öğrenmek bugünkü durumdan farksız olurdu.
- **Anahtarın geçerlilik süresi, kota, model erişimi.** Yoklama "çağrı çalışıyor mu" der; xAI'ın
  cevabını yorumlamaz.
- EKSIKLER'deki xAI maddesi bu commit'te siliniyor mu: hayır. Onu kullanıcının Colab turu kapatır.

## Bitti sayılır

`python -m pytest queen-editor/backend/tests -q` → 592 geçen, 0 düşen. Sekiz testin sekizi de
yeşile döner ve hiçbiri değiştirilmemiş olur.
