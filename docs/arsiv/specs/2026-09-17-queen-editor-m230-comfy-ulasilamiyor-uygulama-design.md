# Madde 230 · ComfyUI'ye ulaşılamayınca ekran ne olduğunu ve log'u söyleyecek — uygulama turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m230-comfy-ulasilamiyor-testler-design.md)

## Kullanıcıdan gereken

Test turundakiyle aynı: hata tekrar ederse *Kopyala* ile alınmış hâli. Maddeyi beklemiyor.

## Ne değişiyor

| Katman | Dosya | Değişiklik |
|---|---|---|
| service | `comfy/errors.py` | `ComfyUnreachable(RuntimeError)`: adres, `requests`'in hatası ve log'un kuyruğundan mesajı kurar. `frame_level` taşımaz |
| service | `comfy/client.py` | `log_path` alır. Her HTTP çağrısı tek bir `_send`'den geçer, ve `requests.ConnectionError` orada `ComfyUnreachable`'a döner |
| kök | `config.py` | `COMFY_LOG = QE_COMFY_LOG`, varsayılanı defterdeki yol |
| kök | `main.py` | `ComfyClient(..., log_path=config.COMFY_LOG)` |
| defter | Flask hücresi | `"QE_COMFY_LOG": COMFY_LOG` *(test turuyla birlikte değil, bu turda)* |

**Neden tek bir `_send`:** bağlantı hatası beş çağrının hepsinde olabilir *(yükleme, gönderme,
bekleme, indirme, kesme)*. Sarmayı her birine ayrı yazmak, birini unutmak demek.

**Log okuma servis içinde kalıyor.** Log ComfyUI'nin kendi dosyası, yani `comfy/` servisinin bilgisi.
Özelliklerden hiçbiri onu bilmiyor. Son 30 satırı `deque` ile okunuyor, çünkü log uzun olabilir ve
yalnız kuyruğu gerekiyor. Bozuk bayt `replace` ile geçiyor: log'daki bir karakter hatayı
gizlememeli.

**Log yolu verilmezse** *(testler, yerel çalıştırma)* varsayılan boş bir yol. Açılamıyor, ve mesaj
bunu işletim sisteminin cümlesiyle söylüyor. Ayrı bir dal yok.

## Ön yüz

Değişmiyor. Duruş kartı mesajın ilk satırını değil `policy.stop_reason`'u başlık yapıyor. Mesajın
tamamı `RawOutput` kutusuna iniyor, ve kutunun **ilk satırı** `ComfyUI'ye bağlanılamadı — <adres>`.
*Kopyala* hepsini veriyor.
