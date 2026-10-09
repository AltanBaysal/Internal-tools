# Madde 230 · ComfyUI'ye ulaşılamayınca ekran ne olduğunu ve log'u söyleyecek — test turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hata tekrar ederse ekrandaki hatanın *Kopyala* ile alınmış hâli. **Maddeyi beklemiyor:** maddenin
işi, o kopyanın sebebi taşımasını sağlamak.

## Bugün ne oluyor

Bir video işinin ComfyUI'ye ilk isteği `upload_image`. ComfyUI dinlemiyorsa `requests` bir
`ConnectionError` fırlatıyor *(`services/comfy/client.py`)*. Bu hata `frame_level` taşımıyor, yani
`policy` onu **koşunun** hatası sayıyor: aynı kare 3 kez deneniyor, sonra kuyruk duruyor. Duruş
kartında `Aynı kare 3 kez denendi — üretim durduruldu` yazıyor, altındaki `RawOutput` kutusunda
`requests`'in ham cümlesi duruyor, ve *Kopyala* onu tamamen veriyor *(`QueuePanel.splitReason`)*.

İki eksik var:
1. **Ne olduğunu söyleyen cümle yok.** `HTTPConnectionPool(host='127.0.0.1', port=8188): Max retries
   exceeded…` bir geliştiriciye bile ilk okumada bir şey söylemiyor.
2. **Sebep kayboluyor.** ComfyUI'nin neden durduğunu yalnız kendi log'u söyler
   *(`/content/comfyui.log`)*. Oturum kapanınca log da gidiyor.

## Ne olacak

`ComfyClient` bağlantı kurulamadığında `requests`'in hatasını **tek bir mesaja** çeviriyor:

```
ComfyUI'ye bağlanılamadı — http://127.0.0.1:8188
<requests'in kendi cümlesi, olduğu gibi>
--- comfyui.log · son 30 satır ---
<log'un son 30 satırı>
```

- **İlk satır** ne olduğunu söylüyor, ve sebep uydurmuyor: bağlanılamadığı gerçek, nedeni değil.
- **Ham cümle** hiç değiştirilmeden kalıyor.
- **Log'un son 30 satırı** o anda okunuyor. Dosya okunamazsa bunu yolu ve işletim sisteminin kendi
  cümlesiyle söylüyor. Bu durum işi ayrıca durdurmuyor, çünkü asıl hata bağlantının kendisi.

Mesaj duruş kartının kutusuna olduğu gibi iniyor. Kutu katlıyor, *Kopyala* **hepsini** veriyor
*(kullanıcı: "hatayı tamamen saklama")*. Ön yüzde bu yüzden hiçbir şey değişmiyor.

**Log'un yolunu defter veriyor.** `COMFY_LOG` zaten CONFIG'de. Flask hücresi onu `QE_COMFY_LOG` ile
geçiriyor, ve `config.py`'de yerel çalıştırma için bir varsayılan kalıyor, öteki yollar gibi.

**Bağlantı hatası hâlâ koşunun hatası.** Kare suçlu değil. Bu ayrım değişmiyor: sarılan hata
`frame_level` taşımıyor.

## Araştırma: ComfyUI hazır dedikten sonra neden durabilir

Kullanıcıdan gelen bilgi şu: hücre hata vermedi, yani ComfyUI 90 saniye içinde `/system_stats`'a cevap
verdi. Hata oturumun başında çıktı, ve ComfyUI elle başlatılınca düzeldi. Koddan ve defterden okunan
**adaylar** aşağıda. Hiçbiri sebep diye yazılmıyor. Her birinin log'da nasıl görüneceği yazılıyor,
çünkü bu maddeyle gelen log'lar ayrımı yapacak.

| Aday | Neden mümkün | `comfyui.log`'da nasıl görünür |
|---|---|---|
| **Python'un kendi çöküşü** | Bir custom node ilk istekte ya da model yüklerken istisna fırlatıp süreci düşürebilir | Son satırlarda bir `Traceback` |
| **Dışarıdan öldürülme** *(ör. sistem belleği biterse Linux'un OOM killer'ı)* | Video grafiği iki büyük SmoothMix modelini yüklüyor. SIGKILL alan bir süreç hiçbir şey yazamaz | Log **bir cümlenin ortasında ya da sessizce** bitiyor, traceback yok |
| **Hazır dedikten sonra yeniden başlama** | ComfyUI-Manager ve bazı paketler ilk açılışta bağımlılık kurup ComfyUI'yi yeniden başlatabiliyor. O arada port kapalı kalır | Log'da **ikinci bir açılış** bölümü |
| **Hücrenin yeniden çalıştırılması** | ComfyUI hücresi önce `pkill -f 'python main.py'` çalıştırıyor | Log'un baştan yazılmış olması *(dosya `"w"` ile açılıyor)* |

**Elenen:**
- **Flask'ın ComfyUI'yi öldürmesi.** Flask hücresinin `pkill` kalıpları `backend.main` ve `cloudflared`,
  ComfyUI'nin komut satırına uymuyor.
- **Kernel'in yeniden başlaması.** Flask da aynı kernel'in alt süreci. O ölmediğine göre kernel de
  yeniden başlamamış.

Koddan düzeltilebilecek bir aday şu an **yok**, çünkü hangisinin olduğu bilinmiyor. Bu madde onu
bilinir kılıyor. Log hangisini gösterirse, düzeltme kendi maddesi olarak gelir.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Bağlanılamayınca mesajın ilk satırı `ComfyUI'ye bağlanılamadı — <adres>` | **kırmızı** |
| 2 | `requests`'in kendi cümlesi mesajda olduğu gibi duruyor | **kırmızı** |
| 3 | Log'un son 30 satırı mesajda, daha eskisi değil | **kırmızı** |
| 4 | Log okunamazsa mesaj bunu yoluyla söylüyor, ve bağlantı hatası yine çıkıyor | **kırmızı** |
| 5 | Aynısı ComfyUI'yi bekleyen `GET /history` için de geçerli, yalnız yükleme için değil | **kırmızı** |
| 6 | Sarılan hata karenin hatası sayılmıyor | **kırmızı** *(sınıf yok)* |
| 7 | Defter log'un yolunu `QE_COMFY_LOG` ile geçiriyor | **kırmızı** |

## Bu turda değişen

Yalnız testler: `test_comfy_client.py` *(1–6)*, `test_notebook_installs_the_producer_groups.py` *(7)*.
