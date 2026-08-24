# Galeri yavaşlığı — ölçüm, hüküm ve açık kaldıraçlar

**Başlangıç:** 2026-08-23 · **Ölçüm:** 2026-08-24, iki tur · **Kaynak:** İstek 1.1, yol haritası v14
madde 29

Bu belge "çok fotoğraf olunca uygulama kilitleniyor ve fotoğraflar çok yavaş iniyor" şikâyetinin
teşhisidir. Önce bütün mekanizmalar sayıldı, sonra zincir halka halka ölçüldü. Ölçüm, sıralamayı
tersine çevirdi: en alttaki aday suçlu çıktı.

Belge tek başına üç soruya cevap verir: **darboğaz nerede · nasıl ölçüldü · ne yapılacak.**

---

## 0 · Hüküm

**Darboğaz cloudflared'in taşıma protokolü — QUIC. Ölçüldü, ve ilacı da aynı koşuda ölçüldü.**

| | |
|---|---|
| Bugünkü boru | **~112 KB/s (≈0.9 Mbps)** — cloudflared varsayılanı QUIC, yani UDP üstü |
| Aynı tünel, `--protocol http2` | **10.01 MB/sn** — **90 kattan fazla** |
| Colab'ın dışarı çıkış ağı | **32.8 MB/sn** (tünelsiz 5 MB yükleme) — sağlam |
| Sebep | Colab'ın ağı UDP'yi kısıyor, TCP'yi kısmıyor |
| İlaç | Tek bayrak: `cloudflared tunnel --protocol http2 --url ...` |
| Pratik sonuç | 1.8 MB foto: **17.7 sn → 0.18 sn** |

Zincirin geri kalanı temiz (24 Ağustos, ikinci tur):

```
Drive → Colab        3.34 MB/sn   (soğuk; sıcak 572 MB/sn)   ✓
Colab içi Flask     41.68 MB/sn                              ✓
Colab → Cloudflare  32.80 MB/sn   (tünel devrede değilken)   ✓
Tünel, QUIC          0.11 MB/sn                              ✗  ← darboğaz
Tünel, HTTP/2       10.01 MB/sn                              ✓  ← ilaç
```

### Ölçümle elenenler

| Aday | Ölçüm | Karar |
|---|---|---|
| Drive FUSE mount'u | Soğuk 3.34 MB/sn, **sıcak 572 MB/sn** | Gerçek ama küçük. Önbellek çalışıyor |
| Flask / Werkzeug | Yerel dosya 41.68 MB/sn | Masum |
| Flask'ta kuyruk | `/api/health` boşken 1 ms → meşgulken 2 ms | **Kuyruk yok** |
| Tarayıcı önbelleği | İkinci istek 16 ms, `transferSize: 0` | **Çalışıyor** |
| CPU açlığı / GIL | Üretim dururken de aynı hız | Elendi |
| Tarayıcı bağlantı sınırı | Protokol `h2` | Elendi — h2'de 6-bağlantı sınırı yok |
| **Colab'ın çıkış ağı** | Tünelsiz 32.8 MB/sn yükleme, 132 MB/sn indirme | **Masum.** Kullanıcının baştan söylediği doğru çıktı |
| **Quick tunnel'ın kendisi** | Aynı quick tunnel, yalnız protokol değişti → 10 MB/sn | **Masum.** Named tunnel'a gerek yok |
| **Baytın büyüklüğü** | Aynı dosya iki protokolde 17.74 sn / 0.18 sn | Kaldıraç ama sebep değil |

### İki belirtinin açıklaması

**"Sunucuya ulaşılamadı" ve donma.** Boru fotoğraflarla dolunca API isteği
[api.js](../../../queen-editor/frontend/src/shared/api.js)'teki 10 saniyelik kesmeye takılıyor.
Sunucu ölmüyor — sırada bekliyor. Ekranın "kilitlendi" görünmesinin tek sebebi bu.

**"İkinci girişte de yavaş."** Tarayıcı önbelleği çalışıyor, ama **yarım kalan bir cevap önbelleğe
hiç yazılmıyor.** Fotoğraflar ilk seferde bitmediği için saklanacak bir şey oluşmuyor. Önbellek
kırık değil; ona verilecek tamamlanmış dosya yok.

> ### Ders: ölçmeden sıralama yazılmaz
>
> Bu teşhiste sıralama **iki kez** yanlış yazıldı. Önce CPU açlığı ve QUIC 1. sıraya kondu (Colab'ın
> ücretsiz katmanı ve 2 çekirdek varsayılmıştı — kullanıcı Pro kullanıyor). Sonra Drive mount'u 1.,
> Flask 2. sıraya çıktı. Tünel her iki listede de en alttaydı.
>
> Ölçüm üçünü de eledi ve en alttaki adayı doğruladı. İhtimaller ölçümden önce yazılabilir;
> **sıralama yazılamaz.**

---

## 1 · Ortam

| | |
|---|---|
| Colab | **Pro** — L4 ve A100, ikisinde de aynı yavaşlık |
| Kullanıcı | Türkiye · Drive'ın kendi arayüzü aynı hattan rahat akıyor |
| Colab makinesi | ABD (tipik) |
| Proje | 1 test projesi · 86 dosya · 81 fotoğraf · ortalama **1.81 MB** |
| Fotoğraf | düz 720p PNG |
| Tünel | `trycloudflare` quick tunnel, `--protocol` verilmiyor (varsayılan **QUIC**) |
| Sunucu | Flask geliştirme sunucusu (`app.run()`) |
| Dosyalar | Google Drive FUSE mount'unda, proje başına tek düz klasör |

---

## 2 · Kullanıcının gözlemleri

| # | Gözlem | Ölçüm ne dedi |
|---|---|---|
| G1 | 10 kare 5 dakikada yükleniyor | ✅ Doğrulandı — 112 KB/s'te beklenen |
| G2 | Tek kare bazen 2-3 dakika | ✅ Ölçüldü: 152 sn (boru paylaşımdayken) |
| G3 | Fotoğrafın yarısı gelip öteki yarısı yavaş doluyor | ✅ Akış yavaş, bekleme değil: TTFB 4 sn, indirme 148 sn |
| G4 | Model üretmesi indirmekten hızlı | ✅ Doğru ama sebep değil (G8'e bak) |
| G5 | Aynı görseller Drive arayüzünde hızlı | ✅ Drive mount kullanmıyor, CDN'den küçük kopya veriyor |
| G6 | Kilitlenen sekme: uygulama, defter değil | ✅ Colab hücresi teorisi elendi |
| G7 | "Sunucuya ulaşılamadı" çıkıyor | ✅ 10 sn'lik kesme; boru dolunca tetikleniyor |
| G8 | **Üretim dururken de tamamen aynı hızda** | ✅ CPU ve GIL adaylarını tek başına öldürdü |
| G9 | İkinci girişte de yavaş; ~120 fotoğrafta sistem kırılıyor | ✅ Önbellek çalışıyor ama yarım dosya saklanmıyor |
| G10 | Hep böyleydi | ✅ Mimaride, sonradan bozulan bir şey değil |
| G11 | Kare sayısı arttıkça kötüleşiyor | ✅ Sabit kapasiteye daha çok bayt |

---

## 3 · Ölçüm sonuçları — ham

Yorumsuz, olduğu gibi. Sohbet kaybolsa da sayılar burada durur.

### 3.1 Sunucu tarafı (Colab, defterin teşhis bloğu)

```
ÖLÇÜM · proje: test · 86 dosya · 81 foto · ort 1.81 MB
S2  mount, soğuk (3 dosya) :     2.94 sn |   1.91 MB/sn
S3  mount, sıcak (aynıları):     0.01 sn | 542.34 MB/sn
S4  yerel disk (aynıları)  :     0.00 sn | 4950.14 MB/sn
S5  Flask ← Drive dosyası  :     0.98 sn |   1.84 MB/sn
S5b Flask ← yerel dosya    :     0.00 sn |  54.00 MB/sn
S6  /api/health boşken     :        1 ms
S6  /api/health meşgulken  :        2 ms
S7  tünel ← Drive dosyası  :    19.02 sn |   0.11 MB/sn
OKUMA
[!] Mount, yerel diskin 2597 katı — darboğaz Drive'da
[ ] FUSE önbelleği çalışıyor
[ ] Flask'ın Drive üstü payı küçük (0.3x)
[ ] Flask yerel dosyada hızlı (54 MB/sn)
[ ] Flask paralel cevaplıyor (1.9x)
[!] Tünelin Colab bacağı pay alıyor (19.5x)
```

> `[!] Mount ... 2597 katı` satırı teknik olarak doğru ama yanıltıcı: oran büyük çünkü yerel disk
> çok hızlı, mutlak değer 1.91 MB/sn ve kabul edilebilir. Eşik tabanlı okumanın sınırı burada
> görünüyor — oran tek başına yeterli değil, mutlak değer de bakılmalı.

### 3.2 Tarayıcı tarafı (Türkiye, uygulama sekmesi)

```
dosya: P21_1.png
T1  TTFB: 4062 ms | indirme: 147863 ms | toplam: 151937 ms | 2.00 MB
T4  protokol: h2
T2  ikinci istek: 16 ms | transferSize: 0 (ONBELLEKTEN)
T3  /api/health bosken: 3436 ms | fotograf inerken: 4096 ms | oran: 1.2x
--- OKUMA ---
[!] Akis baskin — boru dar (tunel/hat)
[ ] Tarayici onbellegi calisiyor
[ ] API fotograftan etkilenmiyor
```

> T3'teki "boşken 3436 ms" **kirli**: o sırada galeri arka planda fotoğraf indiriyordu, yani boru
> boş değildi. Aynı sebeple 1.2x oranı da bir şey kanıtlamıyor. Sunucu tarafındaki S6 (1 ms → 2 ms)
> temiz ölçümdür ve Flask'ta kuyruk olmadığını söyler.

### 3.3 Paralellik testi (tarayıcı) — en kritik ölçüm

```
TEK      : 17.9 sn | 111.9 KB/sn
4 PARALEL: 70.1 sn | 116.5 KB/sn toplam
>>> 1.0x
```

**Dört akış, tek akışla aynı toplamı veriyor.** Boru akış başına değil, **toplamda** sınırlı. Bunun
iki sonucu var: gerçek tavan 112 KB/s, ve **eşzamanlı indirme sayısını artırmak hiçbir şey
kazandırmaz.**

### 3.4 İkinci tur — soru: suç ağda mı, tünel yazılımında mı? (24 Ağustos)

Birinci tur darboğazı *cloudflared ↔ Cloudflare edge* segmentine kadar götürdü ama o segment iki
parçadan oluşuyordu. İkinci tur ikisini birbirinden ayırdı.

```
ÖLÇÜM · proje: test · 86 dosya · 81 foto · ort 1.81 MB
S2  mount, soğuk (3 dosya)      :     1.68 sn |    3.34 MB/sn
S3  mount, sıcak (aynıları)     :     0.01 sn |  571.67 MB/sn
S4  yerel disk (aynıları)       :     0.00 sn | 5501.83 MB/sn
S5  Flask ← Drive dosyası       :     0.58 sn |    3.09 MB/sn
S5b Flask ← yerel dosya         :     0.01 sn |   41.68 MB/sn
S6  /api/health boşken          :        1 ms
S6  /api/health meşgulken       :        2 ms
S8  Colab → CF edge (TÜNELSİZ)  :     0.15 sn |   32.80 MB/sn
S9  Colab ← CF edge (indirme)   :     0.19 sn |  132.20 MB/sn
S7  tünel, QUIC (varsayılan)    :    17.74 sn |    0.11 MB/sn
S10 tünel, --protocol http2     :     0.18 sn |   10.01 MB/sn
S14 iki tünel aynı anda, TOPLAM :    15.39 sn |    0.23 MB/sn
S18 video: 0 dosya (yok)
S18 ses  : 0 dosya (yok)
OKUMA
[ ] Colab'ın çıkış ağı sağlam (32.80 MB/sn) — dar segment cloudflared'de
[!] Hat sağlam (132.2 MB/sn indirme) — darlık yalnız yükleme yönünde
[!] HTTP/2 tüneli QUIC'ten 97.5 KAT hızlı — bayrak çözüyor
```

**S7 ile S10 aynı makinede, aynı dakikada, aynı boyutta iki dosyayla koştu.** Tek fark taşıma
protokolü. 17.74 saniye ile 0.18 saniye arasındaki farkı açıklayacak başka değişken yok.

**S8 turun asıl sorusunu kapattı.** Colab'dan Cloudflare'e tünel devrede değilken 5 MB gitmesi
0.15 saniye sürüyor. Colab'ın ağı dar değil; dar olan cloudflared'in UDP üstünden konuşması.

> ### İkinci ders: sessizce düşen ölçüm sonuç gibi görünür
>
> Bu turun ilk koşusunda dört ölçüm bozuktu ve ikisi **sayı üretti**, yani hata gibi görünmedi:
>
> - **S14** iki tünelden çekiyordu; biri düştü, kalan bacağın baytı "toplam" diye bölündü ve
>   "tavan tünel başına, kısma var" gibi okunacak bir 2.0x çıktı. Üstteki çıktıda da o satır
>   duruyor — **geçersizdir**, http2 bacağı anında bitip QUIC bacağı 15 saniye sürdüğü için doğdu.
> - **S11**, Colab'dan Drive'a 5 MB yazıp 197 MB/sn ölçmüştü. O sayı ağ değil FUSE tamponuydu;
>   `fsync` baytları Google'a itmiyor. Ölçüm tamamen kaldırıldı.
>
> S8/S9 (403) ve S10 (DNS) ise açıkça hata verdi, yani zararsızdı. **Tehlikeli olan patlamayan
> ölçümdür.** Düzeltme: her bileşik ölçüm parçalarının hepsinin döndüğünü doğrulamadan sayı
> basmıyor.

---

## 4 · Bunun ne kadar anormal olduğu

Bağımsız bir hız testinde ngrok 1.10 MB/s, Cloudflare Tunnel 0.84 MB/s ölçülmüş. Biz QUIC'le
**112 KB/s** alıyorduk — tipik bir Cloudflare tünelinin **7'de biri**.

İki şüpheli vardı: **varsayılan QUIC taşıması** ve **quick tunnel'ın kendisi**. İkinci tur birincisini
suçlu, ikincisini masum buldu: aynı quick tunnel, yalnız `--protocol http2` ile, **10 MB/sn** veriyor
— yani yukarıdaki bağımsız ölçümlerin de üstünde. Sorun Cloudflare'in ürününde değil, Colab'ın
ağının UDP'ye davranışındaydı.

---

## 5 · Kaldıraçların ölçüm sonrası hâli

| # | Kaldıraç | Durum |
|---|---|---|
| **K1** | `--protocol http2` (cloudflared) | ✅ **Ölçüldü ve kazandı: 90 kat.** Tek satır, bedava. Uygulanacak olan bu |
| **K2** | Named tunnel (kullanıcının alan adı var) | ❌ **Gereksiz.** Quick tunnel http2 ile 10 MB/sn veriyor; suç tünel ürününde değildi |
| **K3** | Colab'ın kendi proxy'si | ❌ **Çalışmıyor.** `serve_kernel_port_as_window` Colab'ın kendi uyarısıyla bozuk, iframe hiçbir şey döndürmedi. K1 varken zaten gereksiz |
| **K4** | Başka sağlayıcı (Pinggy, zrok, ngrok ücretli) | ❌ **Gereksiz.** Aylık ücretin karşılığı olan hız K1'de bedava duruyor |
| **K5** | Baytı küçültmek (WebP, küçük önizleme) | ⏸ **Kritik yolda değil.** Ölçülemedi (PIL renk kipi). K1'den sonra hâlâ değerliyse kendi maddesiyle açılır |

### Kullanıcının itirazı ve nasıl karşılandığı

> *"Çözüm daha az şey göndermek değil. Video detayına baktığımda 2 dakika bekleyemem. Tüneli
> çözmemiz gerekiyor."*

Haklıydı ve tünel çözüldü. Önizleme galeriyi kurtarıp detay ekranını kurtaramazdı: 112 KB/s'te bir
video dakikalarca inerdi. K1 boruyu 90 kat açtığı için detay ekranı da düzeliyor — **bayt azaltmak
artık bir zorunluluk değil, bir iyileştirme.**

### Kalan bilinmeyen

**Detay ekranının gerçek maliyeti hâlâ ölçülmedi.** S18 test projesinde hiç video ve ses bulamadı
(0 dosya), yani *"video 20-50 MB"* bugüne kadar hep tahmindi ve tahmin olarak kalıyor. Videolu bir
projede tekrar bakılmalı.

### Maliyet notu

Cloudflare Tunnel **Temmuz 2026'dan beri tamamen ücretsiz, bant genişliği sınırı yok.** Bir şey
satın alınmasına gerek yok — ve ölçümden sonra alan adı bağlamaya bile gerek kalmadı.

---

## 6 · Teşhis takımı

Ölçümü tekrarlamak gerekirse. Tarayıcı scriptleri burada duruyor; sunucu tarafı defterden
sökülüyor ve **git geçmişinde** kalıyor, çünkü kodun kopyası belgede tutulursa eskiyen o olur.

### 6.1 Sunucu tarafı

Ölçüm sırasında `queen-editor/app.ipynb`'de kendi hücresinde koşan blok. **Hiç commit'lenmedi** —
ölçüm aletiydi, defter ölçümden sonra eski hâline döndürüldü — bu yüzden tek kopyası burada.
Tekrar gerekirse Flask hücresinden sonra kendi hücresine yapıştırılır; `link`, `APP_PORT`,
`APP_DIR` ve `DRIVE_ROOT` o hücrelerden gelir.

Ölçtükleri: S2/S3 (mount soğuk/sıcak), S4 (yerel disk), S5/S5b (Flask ← Drive / ← yerel), S6
(Flask'ta kuyruk var mı), S7 (tünel QUIC), S8/S9 (Colab ↔ Cloudflare, tünelsiz), S10 (tünel
http2), S14 (iki tünel aynı anda), S16/S17 (WebP ve 320px boyutu), S18 (video/ses dosyaları).
Dış `try/except` sayesinde patlasa da uygulama açık kalıyor; 8'den az fotoğraflı projede kendini
atlıyor.

```python
# === TEŞHİS (geçici ölçüm aleti — commit'lenmez) ===
import socket, subprocess, time, os, re, urllib.request

# speed.cloudflare.com, urllib'in varsayılan User-Agent'ına 403 döndü; tarayıcı kimliğiyle isteniyor.
TARAYICI_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/124.0 Safari/537.36")


def _teshis(tunel):
    import glob, io, shutil, threading, itertools
    from urllib.parse import quote, urlparse

    adaylar = [(p, len(glob.glob(os.path.join(DRIVE_ROOT, p, "*.png"))))
               for p in os.listdir(DRIVE_ROOT) if os.path.isdir(os.path.join(DRIVE_ROOT, p))]
    if not adaylar or max(n for _, n in adaylar) < 8:
        print("Teşhis atlandı: en az 8 fotoğraflı bir proje yok")
        return
    proje = max(adaylar, key=lambda x: x[1])[0]
    fotolar = sorted(glob.glob(os.path.join(DRIVE_ROOT, proje, "*.png")))

    def oku(yollar):
        t = time.time()
        n = 0
        for y in yollar:
            with open(y, "rb") as f:
                n += len(f.read())
        return time.time() - t, n

    def cek(url, zaman=600, ua=False):
        istek = urllib.request.Request(url, headers={"User-Agent": TARAYICI_UA} if ua else {})
        t = time.time()
        with urllib.request.urlopen(istek, timeout=zaman) as r:
            n = len(r.read())
        return time.time() - t, n

    def hiz(sn, b):
        return (b / 1e6 / sn) if sn > 0 else 0.0

    def foto_url(taban, yol):
        return f"{taban}/photos/{quote(proje)}/{quote(os.path.basename(yol))}"

    APP = f"http://127.0.0.1:{APP_PORT}"
    tum = glob.glob(os.path.join(DRIVE_ROOT, proje, "*"))
    ort = sum(os.path.getsize(f) for f in fotolar) / len(fotolar)

    # --- Zincir: mount → yerel disk → Flask → kuyruk ---
    A = fotolar[:3]
    s2, n2 = oku(A)                                     # mount, soğuk
    s3, _ = oku(A)                                      # mount, sıcak: FUSE önbelleği çalışıyor mu
    gec = "/content/_teshis"
    shutil.rmtree(gec, ignore_errors=True)
    os.makedirs(gec)
    for y in A:
        shutil.copy(y, gec)
    s4, _ = oku(sorted(glob.glob(gec + "/*.png")))      # aynı baytlar, yerel diskten
    s5, n5 = cek(foto_url(APP, fotolar[3]))             # Flask ← Drive
    buyuk = max(glob.glob(f"{APP_DIR}/frontend/dist/assets/*"), key=os.path.getsize)
    s5b, n5b = cek(f"{APP}/assets/{os.path.basename(buyuk)}")   # Flask ← yerel dosya

    s6_bos = min(cek(f"{APP}/api/health")[0] for _ in range(3))
    dur = threading.Event()
    sira = itertools.cycle(fotolar[4:])

    def yukleyici():
        while not dur.is_set():
            try:
                cek(foto_url(APP, next(sira)))
            except Exception:
                return

    for _ in range(2):
        threading.Thread(target=yukleyici, daemon=True).start()
    time.sleep(3)
    s6_mesgul = max(cek(f"{APP}/api/health")[0] for _ in range(3))
    dur.set()
    time.sleep(1)
    shutil.rmtree(gec, ignore_errors=True)

    # --- S16/S17: bayt kaldıracı — ağ yok, yalnız yeniden kodlama ---
    s16 = s17 = olcu = None
    try:
        from PIL import Image
        im = Image.open(fotolar[0])
        im.load()
        olcu = im.size
        # WebP yalnız RGB/RGBA yazıyor; ilk koşu bu yüzden unsupported image mode ile düştü.
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.mode else "RGB")
        kap = io.BytesIO()
        im.save(kap, "WEBP", quality=82)
        s16 = kap.tell()
        kucuk = im.copy()
        kucuk.thumbnail((320, 320))
        kap = io.BytesIO()
        kucuk.save(kap, "WEBP", quality=80)
        s17 = kap.tell()
    except Exception as e:
        print(f"S16/S17 ölçülemedi: {type(e).__name__}: {e}")

    # --- S18: detay ekranının gerçek maliyeti ---
    videolar = [f for f in tum if f.lower().endswith((".mp4", ".webm", ".mov"))]
    sesler = [f for f in tum if f.lower().endswith((".mp3", ".wav", ".m4a", ".flac"))]

    # Colab → Google yönü buradan ölçülmüyor: Drive mount'una yazmak FUSE'un tamponuna yazmaktır,
    # fsync bile baytları Google'a itmiyor — ilk koşu 197 MB/sn dedi, ki o ağ değil önbellek.

    # --- S8/S9: Colab ↔ Cloudflare, cloudflared devrede DEĞİLKEN ---
    s8 = s9 = None
    try:
        veri = b"x" * (5 * 1024 * 1024)
        istek = urllib.request.Request("https://speed.cloudflare.com/__up", data=veri,
                                       method="POST", headers={"User-Agent": TARAYICI_UA})
        t = time.time()
        urllib.request.urlopen(istek, timeout=300).read()
        s8 = time.time() - t
    except Exception as e:
        print(f"S8 ölçülemedi: {type(e).__name__}: {e}")
    try:
        s9, _ = cek("https://speed.cloudflare.com/__down?bytes=26214400", zaman=300, ua=True)
    except Exception as e:
        print(f"S9 ölçülemedi: {type(e).__name__}: {e}")

    # --- S7: temel çizgi, uygulamanın kendi tüneli (varsayılan QUIC) ---
    s7 = n7 = None
    try:
        s7, n7 = cek(foto_url(tunel, fotolar[4]))
    except Exception as e:
        print(f"S7 ölçülemedi: {type(e).__name__}: {e}")

    # --- S10: aynı dosya, --protocol http2 ile açılmış ikinci tünelden ---
    s10 = n10 = s14 = n14 = None
    h2 = h2link = None
    try:
        h2log = "/content/cloudflared_h2.log"
        h2 = subprocess.Popen(
            ["/content/cloudflared", "tunnel", "--protocol", "http2",
             "--url", f"http://127.0.0.1:{APP_PORT}"],
            stdout=open(h2log, "w"), stderr=subprocess.STDOUT)
        for _ in range(40):
            time.sleep(1)
            m = re.search(r"https://[-\w.]+trycloudflare\.com", open(h2log).read())
            if m:
                h2link = m.group(0)
                break
        if not h2link:
            print("S10: http2 tüneli 40 sn içinde link vermedi")
        else:
            # Log'da link görünmesi adın DNS'te olduğu anlamına gelmiyor: ilk koşu taze adrese
            # Name or service not known ile düştü. Ad çözülene kadar beklenir.
            konak = urlparse(h2link).hostname
            for _ in range(60):
                try:
                    socket.getaddrinfo(konak, 443)
                    break
                except socket.gaierror:
                    time.sleep(1)
            else:
                print(f"S10: {konak} 60 sn içinde DNS'te görünmedi")
                h2link = None
        if h2link:
            s10, n10 = cek(foto_url(h2link, fotolar[5]))
    except Exception as e:
        print(f"S10 ölçülemedi: {type(e).__name__}: {e}")
        h2link = None

    # --- S14: iki tünelden aynı anda. Toplam tekin katıysa tavan tünel başınadır. ---
    if h2link and s7 is not None:
        try:
            gelen = []

            def paralel_cek(taban, yol):
                try:
                    gelen.append(cek(foto_url(taban, yol))[1])
                except Exception as e:
                    print(f"S14 bacağı düştü ({taban[:40]}...): {type(e).__name__}: {e}")

            isler = [threading.Thread(target=paralel_cek, args=(tunel, fotolar[6])),
                     threading.Thread(target=paralel_cek, args=(h2link, fotolar[7]))]
            t = time.time()
            for j in isler:
                j.start()
            for j in isler:
                j.join()
            # Tek bacak dönerse bu bir toplam değil, tek tünel ölçümüdür — ilk koşu tam da böyle
            # yanıltmıştı. Eksikse sayı hiç basılmıyor.
            if len(gelen) == 2:
                s14, n14 = time.time() - t, sum(gelen)
            else:
                print(f"S14 geçersiz: iki bacaktan {len(gelen)} tanesi döndü")
        except Exception as e:
            print(f"S14 ölçülemedi: {type(e).__name__}: {e}")

    if h2 is not None:
        h2.terminate()      # yalnız burada açılan tünel; pkill uygulamanınkini de öldürürdü

    # === Rapor ===
    print("=" * 74)
    print(f"ÖLÇÜM · proje: {proje} · {len(tum)} dosya · {len(fotolar)} foto · ort {ort/1e6:.2f} MB")
    print("=" * 74)
    print(f"S2  mount, soğuk (3 dosya)      : {s2:8.2f} sn | {hiz(s2, n2):7.2f} MB/sn")
    print(f"S3  mount, sıcak (aynıları)     : {s3:8.2f} sn | {hiz(s3, n2):7.2f} MB/sn")
    print(f"S4  yerel disk (aynıları)       : {s4:8.2f} sn | {hiz(s4, n2):7.2f} MB/sn")
    print(f"S5  Flask ← Drive dosyası       : {s5:8.2f} sn | {hiz(s5, n5):7.2f} MB/sn")
    print(f"S5b Flask ← yerel dosya         : {s5b:8.2f} sn | {hiz(s5b, n5b):7.2f} MB/sn")
    print(f"S6  /api/health boşken          : {s6_bos*1000:8.0f} ms")
    print(f"S6  /api/health meşgulken       : {s6_mesgul*1000:8.0f} ms")
    if s8 is not None:
        print(f"S8  Colab → CF edge (TÜNELSİZ)  : {s8:8.2f} sn | {5/s8:7.2f} MB/sn")
    if s9 is not None:
        print(f"S9  Colab ← CF edge (indirme)   : {s9:8.2f} sn | {25/s9:7.2f} MB/sn")
    if s7 is not None:
        print(f"S7  tünel, QUIC (varsayılan)    : {s7:8.2f} sn | {hiz(s7, n7):7.2f} MB/sn")
    if s10 is not None:
        print(f"S10 tünel, --protocol http2     : {s10:8.2f} sn | {hiz(s10, n10):7.2f} MB/sn")
    if s14 is not None:
        print(f"S14 iki tünel aynı anda, TOPLAM : {s14:8.2f} sn | {hiz(s14, n14):7.2f} MB/sn")
    if s16 is not None:
        print(f"S16 fotoğraf {olcu[0]}x{olcu[1]} PNG        : {ort/1e6:7.2f} MB "
              f"→ WebP {s16/1e6:.2f} MB ({ort/max(s16,1):.1f}x)")
        print(f"S17 aynı fotoğraf 320px WebP    : {s17/1024:7.0f} KB ({ort/max(s17,1):.0f}x)")
    print(f"S18 video: {len(videolar)} dosya"
          + (f" · toplam {sum(os.path.getsize(f) for f in videolar)/1e6:.1f} MB"
             f" · en büyük {max(os.path.getsize(f) for f in videolar)/1e6:.1f} MB"
             if videolar else " (yok)"))
    print(f"S18 ses  : {len(sesler)} dosya"
          + (f" · toplam {sum(os.path.getsize(f) for f in sesler)/1e6:.1f} MB" if sesler else " (yok)"))

    print("=" * 74)
    print("OKUMA")

    def hukum(kosul, evet, hayir):
        print(("[!] " + evet) if kosul else ("[ ] " + hayir))

    # Yerel disk çoğu zaman 0.00 sn ölçülüyor, o yüzden oran değil hızın kendisi okunuyor.
    hukum(hiz(s2, n2) < 1.0,
          f"Mount soğukta yavaş ({hiz(s2, n2):.2f} MB/sn) — Drive halkası pay alıyor",
          f"Mount soğukta idare ediyor ({hiz(s2, n2):.2f} MB/sn)")
    hukum(s3 >= 0.3 * s2, f"FUSE önbelleği işlemiyor ({s3/max(s2,1e-9):.1f}x)",
          "FUSE önbelleği çalışıyor")
    hukum(hiz(s5, n5) < 0.5 * hiz(s2, n2),
          f"Flask, Drive üstüne kendi payını ekliyor ({hiz(s5, n5):.2f} MB/sn)",
          f"Flask'ın Drive üstü payı küçük ({hiz(s5, n5):.2f} MB/sn)")
    hukum(hiz(s5b, n5b) < 5,
          f"Flask yerel dosyada bile yavaş ({hiz(s5b, n5b):.1f} MB/sn) — servis katmanı",
          f"Flask yerel dosyada hızlı ({hiz(s5b, n5b):.0f} MB/sn)")
    hukum(s6_mesgul > 5 * s6_bos, f"KUYRUK FLASK'TA ({s6_mesgul/max(s6_bos,1e-9):.0f}x)",
          f"Flask paralel cevaplıyor ({s6_mesgul/max(s6_bos,1e-9):.1f}x)")
    if s7 is not None:
        hukum(s7 > 3 * s5, f"Tünel zinciri {s7/max(s5,1e-9):.0f} kat yavaşlatıyor",
              f"Tünelin payı küçük ({s7/max(s5,1e-9):.1f}x)")
    if s8 is not None:
        hukum(5/s8 < 0.5,
              f"Colab'ın çıkış ağı da yavaş ({5/s8:.2f} MB/sn) — suç tünel yazılımında değil",
              f"Colab'ın çıkış ağı sağlam ({5/s8:.2f} MB/sn) — dar segment cloudflared'de")
    if s9 is not None:
        hukum(25/s9 > 5, f"Hat sağlam ({25/s9:.1f} MB/sn indirme) — darlık yalnız yükleme yönünde",
              f"İndirme de yavaş ({25/s9:.1f} MB/sn) — hattın kendisi dar")
    if s10 is not None and s7 is not None:
        hukum(s7 > 2 * s10,
              f"HTTP/2 tüneli QUIC'ten {s7/max(s10,1e-9):.1f} KAT hızlı — bayrak çözüyor",
              f"HTTP/2 ile QUIC arasında anlamlı fark yok ({s7/max(s10,1e-9):.1f}x)")
    if s14 is not None and s7 is not None:
        hukum(hiz(s14, n14) > 1.7 * hiz(s7, n7),
              f"İki tünelin toplamı tekin {hiz(s14,n14)/max(hiz(s7,n7),1e-9):.1f} katı — "
              f"tavan TÜNEL BAŞINA, yani kısma var ve birden çok tünel bir seçenek",
              f"Toplam tekle aynı ({hiz(s14,n14)/max(hiz(s7,n7),1e-9):.1f}x) — tavan MAKİNE BAŞINA")
    if s16 is not None and s7 is not None:
        print(f"[ ] Bayt: bugünkü tünel hızıyla bir fotoğraf {ort/1e6/max(hiz(s7,n7),1e-9):.0f} sn; "
              f"WebP'yle {s16/1e6/max(hiz(s7,n7),1e-9):.0f} sn, "
              f"320px önizlemeyle {s17/1e6/max(hiz(s7,n7),1e-9):.1f} sn")
    print("=" * 74)


try:
    _teshis(link)
except Exception as e:
    print(f"Teşhis atlandı: {type(e).__name__}: {e}")
```

### 6.2 Tarayıcı tarafı — tam ölçüm

Galeri açıkken, en az bir fotoğraf yüklendikten sonra F12 → Console. (Chrome ilk seferde
`allow pasting` yazmanı ister.)

```js
(async () => {
  const L = [], p = s => { L.push(s); console.log(s); };
  const ms = x => `${Math.round(x)} ms`;
  performance.setResourceTimingBufferSize(500);

  const img = [...document.querySelectorAll('img')].map(i => i.src).find(s => s.includes("/photos/"));
  if (!img) { console.log("Galeri ekraninda calistir — yuklenmis bir fotograf yok"); return; }
  p(`dosya: ${decodeURIComponent(img.split('/').pop())}`);

  // Govde okunmadan zamanlama kaydi olusmuyor: fetch sadece basliklarda cozuluyor.
  const cek = async (url, mod) => {
    const t0 = performance.now();
    const r = await fetch(url, mod ? { cache: mod } : undefined);
    const b = await r.arrayBuffer();
    const sure = performance.now() - t0;
    await new Promise(res => setTimeout(res, 200));
    return { sure, bayt: b.byteLength, e: performance.getEntriesByName(url).pop() };
  };

  performance.clearResourceTimings();
  const a = await cek(img, "reload");
  let ttfb = null, akis = null;
  if (a.e) {
    ttfb = a.e.responseStart - a.e.requestStart;
    akis = a.e.responseEnd - a.e.responseStart;
    p(`T1  TTFB: ${ms(ttfb)} | indirme: ${ms(akis)} | toplam: ${ms(a.sure)} | ${(a.bayt/1e6).toFixed(2)} MB`);
    p(`T4  protokol: ${a.e.nextHopProtocol || "(bos)"}`);
  } else {
    p(`T1  toplam: ${ms(a.sure)} | ${(a.bayt/1e6).toFixed(2)} MB  (zamanlama kaydi yok)`);
  }

  const b = await cek(img);
  const ts = b.e ? b.e.transferSize : -1;
  p(`T2  ikinci istek: ${ms(b.sure)} | transferSize: ${ts} (${ts === 0 ? "ONBELLEKTEN" : "YINE AGDAN"})`);

  const saglik = async () => { const t = performance.now(); await (await fetch("/api/health")).text(); return performance.now() - t; };
  let bos = Infinity; for (let i = 0; i < 3; i++) bos = Math.min(bos, await saglik());
  const inen = cek(img, "reload");
  let mesgul = 0; for (let i = 0; i < 3; i++) mesgul = Math.max(mesgul, await saglik());
  await inen;
  p(`T3  /api/health bosken: ${ms(bos)} | fotograf inerken: ${ms(mesgul)} | oran: ${(mesgul/Math.max(bos,0.001)).toFixed(1)}x`);

  p("--- OKUMA ---");
  if (ttfb !== null) p(ttfb > 2*akis ? "[!] Bekleme baskin — sunucu gec basliyor"
    : akis > 2*ttfb ? "[!] Akis baskin — boru dar (tunel/hat)" : "[ ] Bekleme ve akis dengeli");
  p(ts === 0 ? "[ ] Tarayici onbellegi calisiyor" : "[!] Onbellek calismiyor — her giris sifirdan");
  p(mesgul > 5*bos ? "[!] Kilit yeniden uretildi — API fotografin arkasinda bekliyor" : "[ ] API fotograftan etkilenmiyor");
  try { copy(L.join("\n")); p("(sonuc panoya kopyalandi)"); } catch {}
})();
```

**T3 için uyarı:** galeri arka planda indirirken ölçme, sayı kirlenir. Sunucu tarafındaki S6 temiz
karşılığıdır.

### 6.3 Tarayıcı tarafı — paralellik

Tek soruyu cevaplar: tavan akış başına mı, toplam mı?

```js
(async () => {
  const ler = [...document.querySelectorAll('img')].map(i => i.src).filter(s => s.includes("/photos/")).slice(0, 4);
  if (ler.length < 2) { console.log("En az 2 yuklu fotograf lazim — biraz kaydir"); return; }
  const cek = async u => { const t = performance.now(); const r = await fetch(u, {cache:"reload"}); const b = await r.arrayBuffer(); return {sn:(performance.now()-t)/1000, mb:b.byteLength/1e6}; };
  const a = await cek(ler[0]);
  console.log(`TEK   : ${a.sn.toFixed(1)} sn | ${(a.mb/a.sn*1000).toFixed(1)} KB/sn`);
  const t = performance.now();
  const c = await Promise.all(ler.map(cek));
  const sn = (performance.now()-t)/1000, mb = c.reduce((s,x)=>s+x.mb,0);
  console.log(`${ler.length} PARALEL: ${sn.toFixed(1)} sn | ${(mb/sn*1000).toFixed(1)} KB/sn toplam`);
  console.log(`>>> ${(mb/sn/(a.mb/a.sn)).toFixed(1)}x  (1.0 = boru toplam sinirli, 3-4 = paralellik ise yariyor)`);
})();
```

---

## 7 · Bu ölçümün kodda değiştirdikleri

Teşhis sırasında ortaya çıkan, yavaşlıktan bağımsız iki bulgu. İkisi de düzeltme turuna aittir,
burada yalnız kayıt altına alınıyor.

**7.1 · Kuyruğun tavanı sızdırıyor.**
[TileImage.jsx](../../../queen-editor/frontend/src/features/photo_generation/TileImage.jsx): karo
görüş alanından çıkınca `useEffect` temizliği bileti düşürüyor ve kuyrukta yer açılıyor — ama
`granted` geri alınmadığı için `src` duruyor ve tarayıcı indirmeye devam ediyor. Yani kaydırılan her
karo, indirmesi sürerken yerini bırakıyor; tavan kâğıt üstünde 2, pratikte daha büyük.

Ölçüm bunun zararsız olduğunu gösterdi (boru toplamda sınırlı, paralellik bir şey değiştirmiyor) ama
kod yine de söylediğini yapmıyor.

**7.2 · Tavanın gerekçesi yanlış yazılmış.**
[image_queue.js](../../../queen-editor/frontend/src/shared/image_queue.js) *"tarayıcı 6 bağlantı
açar"* diyor. Bu HTTP/1.1'in kuralı; ölçüm protokolün **h2** olduğunu gösterdi ve orada tek bağlantı
üzerinde çok akış var. Fren işe yaramış olabilir ama yorumun yazdığı sebepten değil. Repo kuralı
gereği yorum koda uydurulmalı: sebep uydurulmaz.

---

## 8 · Kaynaklar

**Cloudflare tüneli**
- [cloudflared #895 — QUIC, HTTP/2'den yavaş (Cloudflare desteğiyle doğrulanmış)](https://github.com/cloudflare/cloudflared/issues/895)
- [Quick Tunnels — geçici, garantisiz, 200 eşzamanlı istek sınırı](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/)
- [Cloudflare Tunnel throughput şikâyetleri (3-4 Mbps)](https://community.cloudflare.com/t/cloudflare-tunnel-is-slow-while-lets-encrypt-isnt-need-help-on-optimisation/637218)
- [QUIC is not Quick Enough over Fast Internet (%45'e varan kayıp)](https://arxiv.org/html/2310.09423v2)
- [ngrok / Cloudflare Tunnel / Pinggy hız karşılaştırması](https://www.localcan.com/blog/ngrok-vs-cloudflare-tunnel-vs-localcan-speed-test-2025)
- [Zero Trust planları ve fiyatlandırma](https://www.cloudflare.com/plans/zero-trust-services/)

**Colab ve Drive**
- [colabtools #1096 — Drive'dan yavaş okuma/yazma](https://github.com/googlecolab/colabtools/issues/1096)
- [colabtools #1691 — okuma hızında 300 kat dalgalanma](https://github.com/googlecolab/colabtools/issues/1691)
- [colabtools #1020 — mount'tan indirme kotası aşımı](https://github.com/googlecolab/colabtools/issues/1020)
- [colabtools #4738 — proxyPort 403 sorunu](https://github.com/googlecolab/colabtools/issues/4738)
- [Drive API kullanım sınırları](https://developers.google.com/workspace/drive/api/guides/limits)

**Flask / Werkzeug**
- [Werkzeug geliştirme sunucusu üretim için değil](https://testdriven.io/blog/what-is-werkzeug/)
