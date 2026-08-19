# QueenAgent v4 Yol Haritası — Colab'da paylaşım

**Tarih:** 2026-08-20 · **Branch:** `fix/mira`
**Kaynak:** kullanıcı isteği — "arkadaşımla paylaşmak"; Colab, ve **derlenip commit'lensin**
(19–20 Ağustos kararı). Numaralar v3'ten devam eder (52'de bitti).
**Örnek:** [queen-editor/app.ipynb](../../../queen-editor/app.ipynb) — desen oradan alınır, ama
**birebir kopyalanmaz**; farklar Madde 57'de.

---

## Neden bu iş var

QueenAgent bugün yalnız kendi makinesinde çalışıyor. Arkadaşına vermenin iki yolu vardı: exe ya da
Colab. Colab seçildi, çünkü uygulamanın kendisi zaten ona göre biçilmiş — `QUEENAGENT_ROOT` ortam
değişkeniyle taşınıyor ([config.py:13](../../../queen-agent/backend/config.py#L13)), API anahtarı o
kökün altındaki `settings.json`'da yaşıyor, ve depoda çalışan bir Colab deseni (queen-editor) zaten
var. Exe ise `DIST_DIR`'i paketleme bilgisiyle kirletir, Windows'a çakılır, ve her değişiklikte elden
yeni bir dosya göndermeyi gerektirir.

## Sıranın mantığı

53-54-59 zemini kurar — defter, kendi temelini yalanlayan bir depoya yazılamaz, ve veri Drive'a
taşınmadan önce yazmanın orada güvenli olması gerekir. 55-57 defterin kendisi, hücre sırasıyla:
yapılandırma → klon → sunucu. 58 arkadaşının izleyeceği yolu yazar. Kullanıcının toplu testi en
sonda: **arkadaş gerçekten açar.**

*(59 sonradan yazıldı, o yüzden numarası büyük; koşudaki yeri Faz 1. Numaralar kaymaz — numara ne
zaman yazıldığını söyler, nerede koşulduğunu değil.)*

---

## Faz 1 — Zemin

### Madde 53 — FOUNDATION'ın iki kararı artık yanlış

- **Ne çalışır:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) **Karar 1** bugün "uygulama
  yalnız kullanıcının makinesinde çalışır… paylaşmak, henüz vermediğimiz bir karar gerektirir"
  diyor — karar verildi, yazılır. **Karar 3** "`dist/` commit'lenmez" diyor — değişti. İkisi de bu
  maddede düzeltilir, ve Karar 1 yereli **birincil** yol olarak korur: Colab eklenen bir yüzey,
  yerini alan değil.
  Aynı maddede [CLAUDE.md](../../../CLAUDE.md)'nin komut bloğu (queen-agent'ın dist'i hakkındaki
  cümle) ve [queen-agent/README.md](../../../queen-agent/README.md) düzeltilir.
- **Nasıl görülür:** iki belge, deponun bugünkü hâlini anlatıyor; hiçbiri defteri yalanlamıyor.

### Madde 54 — `dist` depoya girer ve girmiş kalır

- **Ne çalışır:** kök `.gitignore`'daki `dist/` kuralına queen-agent istisnası; `frontend/dist`
  commit'lenir. Kural: **kaynakla aynı commit'te derlenip commit'lenir** — queen-editor'ün kuralı,
  aynı sebeple (defter derlemez).
- **Nasıl görülür:** temiz bir klon `npm` çalıştırmadan `python main.py` ile açılıyor.

### Madde 59 — Yazma yarım kalmaz *(Faz 1'de koşar)*

- **Ne çalışır:** [store.py:27](../../../queen-agent/backend/services/store/store.py#L27) bugün tek
  yazma yolu ve dosyayı **yerinde kesip** yeniden yazıyor. Yerel diskte pencere mikrosaniye; Drive
  FUSE'da bir I/O hatası ya da runtime'ın ortada ölmesi `<chat>.json`'ı yarım bırakır ve o sohbet
  gider — FOUNDATION'ın 1. ilkesiyle ("kullanıcının emeği kutsaldır") doğrudan çarpışan tek yer.
  `write_text` geçici bir dosyaya yazıp `os.replace` ile üstüne geçer. Atomik ilkel zaten Store'da:
  `move` onu kullanıyor.
- **Nasıl görülür:** yazma ortasında patlayan bir Store, eski dosyayı **olduğu gibi** bırakıyor —
  ne yarım ne boş. Drive'da `os.replace`'in aynı bağlama içinde çalıştığı da bu maddede görülür.
- **Neden Drive'a özel değil:** yerelde de doğru olan şey; Drive onu yalnızca *sık* hâle getiriyor.

---

## Faz 2 — Defter

### Madde 55 — CONFIG: önce Drive, sonra her şey

- **Ne çalışır:** `queen-agent/app.ipynb`'nin ilk kodu tek bir CONFIG hücresi. Drive **ilk** bağlanır
  (izin penceresi ilk saniyede çıksın), `QUEENAGENT_ROOT` `MyDrive/<DRIVE_FOLDER>`'a bakar
  (`QueenAgent`), `GITHUB_TOKEN` Colab Secrets'tan okunur ve yoksa ne yapılacağını söyleyen bir
  `assert` ile durur. Eksik olan **yüksek sesle** söylenir ve sebep uydurulmaz.
  xAI anahtarı **burada yok**: uygulamanın kendi Settings ekranına girilir ve Drive'daki
  `settings.json`'a düşer — bir kere, sonsuza kadar. Bu queen-editor'den bilerek ayrılan yer.
- **Nasıl görülür:** Secrets boşken hücre ne yapılacağını söyleyerek durur; doluyken Drive kökünü
  basar.

### Madde 56 — Klon: sil ve yeniden klonla

- **Ne çalışır:** `AltanBaysal/Internal-tools` **özel** bir depo, o yüzden token'lı klon. Token
  kabuğa, log'a ve hata metnine sızmaz (argüman listesi + maskeleme). Başarısızlıkta git'in kendi
  stderr'i basılır. Klondan sonra `queen-agent/frontend/dist/index.html` **aranır**: yoksa hücre
  durur — unutulmuş bir derleme burada görünsün, boş sayfa olarak değil.
- **Nasıl görülür:** `dist` commit'lenmemiş bir dalda hücre "derlenmiş arayüz yok" diyerek duruyor.

### Madde 57 — Sunucu kalkar, ve adresi Colab oturumuna kapalıdır

- **Ne çalışır:** `main.py` arka planda başlar, `QUEENAGENT_ROOT` ortamdan geçer, `/api/health`
  90 sn boyunca yoklanır, cevap gelmezse sunucunun kendi log'unun son satırları basılıp durulur.
  Hücre açık kalır, yoksa Colab runtime'ı boşta sayar.

  **Burada queen-editor'den ayrılıyoruz.** O, `cloudflared` ile **herkese açık** bir
  `trycloudflare.com` adresi basıyor. QueenAgent'ta giriş/parola yok ve anahtar kullanıcının
  kendisinin: linki bulan, onun anahtarını harcar ve dosyalarını okur. Bu yüzden adres
  **Colab'ın kendi kernel proxy'siyle** verilir (`serve_kernel_port_as_window` /
  `kernel.proxyPort`) — yalnız defteri açan oturuma açıktır, ve uygulamaya auth yazmayı
  gerektirmez.

  **Bu maddenin kanıtlaması gereken şey:** QueenAgent cevabı **SSE ile** akıtıyor. Kernel proxy'nin
  akışı bozmadan taşıdığı görülmeli. Taşımıyorsa karar `cloudflared`'e döner — ama o zaman defter
  linkin herkese açık olduğunu **açıkça söyler**, ve bu ayrı bir karar olarak yazılır.
- **Nasıl görülür:** hücre bir adres basıyor, adres açılıyor, bir soru soruluyor ve cevap
  **kelime kelime** akıyor (tek parça hâlinde değil).

---

## Faz 3 — Kapanış

### Madde 58 — Arkadaşının izleyeceği yol yazılır

- **Ne çalışır:** defterin ilk markdown hücresi ve `queen-agent/README.md`, sırayı adım adım
  söyler: defteri Colab'a yükle → 🔑 Secrets'a `GITHUB_TOKEN` ekle (fine-grained, yalnız bu depo,
  `Contents: read`) → Run all → Drive iznini ver → linke gir → **Settings'e kendi xAI anahtarını
  yaz**. Türkçe, çünkü okuyan bir insan.

  Üç şey de burada söylenir, çünkü hiçbiri koddan anlaşılmaz ve üçü de Drive'ın kendi doğasından
  geliyor:
  1. **Aynı klasöre iki oturum bakmasın.** Uygulamada kilit yok; defteri iki kere açmak ya da aynı
     klasörü paylaşmak, iki sunucunun aynı dosyaya yazması demek.
  2. **Çalışırken klasörü Drive'ın web arayüzünden karıştırma.** Drive aynı klasörde aynı adlı iki
     dosyaya izin verir; FUSE hangisini göstereceğini seçmek zorunda kalır.
  3. **xAI anahtarı Drive'da düz metin** (`settings.json`). Yerelde de öyle, ama Drive'da Google'a
     senkronlanır ve web arayüzünde görünür. Arkadaşının kendi anahtarı, ama bilerek koysun.
- **Nasıl görülür:** daha önce hiç açmamış biri, sormadan sonuna kadar gidiyor.

---

## Bilerek yapılmayanlar

- **Uygulamaya giriş/parola eklenmiyor.** Madde 57'nin kapalı adresi bu ihtiyacı ortadan kaldırıyor;
  auth eklemek ayrı ve büyük bir iş.
- **Defter derlemiyor.** Madde 54 bunun için var: `npm ci` her oturumda ~1.5 dakika ve arkadaşının
  ödeyeceği bir bedel.
- **Ortak çalışma yok.** Her arkadaş kendi Drive'ında kendi kökünü taşır; tek bir kök paylaşmak
  ayrı bir tasarım.
- **Yerel yol değişmiyor.** `python main.py` bugünkü gibi çalışır.
- **Yazma hızı için bir şey yapılmıyor.** Drive'da her kayıt dosyanın tamamının yüklenmesi demek ve
  sohbet uzadıkça JSON büyüyor. Ölçülmüş bir sorun değil, ve FOUNDATION 3 ölçülmemiş bir sorunu
  optimize etmeyi yasaklıyor. Yavaşlık görülürse ayrı bir madde olur.
- **Kilit eklenmiyor.** Tek kullanıcı tek oturum varsayımı duruyor; kural Madde 58'de yazılıyor.

## Kapanış

Maddeler durmadan spec → plan → test → uygulama ile gider. Defter **çalıştırılarak değil okunarak**
test edilir — `.ipynb`'nin JSON'u ayrıştırılıp hücrenin ne yaptığı sorulur; desen
[queen-editor'ün defter testi](../../../queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py).
Kullanıcının toplu testi en sonda: arkadaş defteri açar ve bir tur atar.
