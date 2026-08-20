# QueenAgent v4 Yol Haritası — Colab'da paylaşım

**Tarih:** 2026-08-20 · **Branch:** `feat/queenagent-colab`
**Kaynak:** kullanıcı isteği — "arkadaşımla paylaşmak"; Colab, **derlenip commit'lensin**, veri
**Drive'da**. Numaralar v3'ten devam eder (52'de bitti).
**Örnek:** [queen-editor/app.ipynb](../../../queen-editor/app.ipynb) — desen oradan alınır.

---

## Neden bu iş var

QueenAgent bugün yalnız kendi makinesinde çalışıyor. Colab seçildi çünkü uygulama zaten ona göre
biçilmiş: `QUEENAGENT_ROOT` ortam değişkeniyle taşınıyor
([config.py:13](../../../queen-agent/backend/config.py#L13)), API anahtarı o kökün altındaki
`settings.json`'da yaşıyor, tek üçüncü parti bağımlılık Flask (xAI transportu bile stdlib
[urllib](../../../queen-agent/backend/services/xai/client.py)), ve depoda çalışan bir Colab deseni
zaten var. Exe'nin güncelleme maliyeti — her değişiklikte elden yeni dosya — tek başına diğer her
şeyi bastırıyor.

## Araştırmanın değiştirdiği karar *(20 Ağustos)*

İlk taslak adresi **Colab'ın kendi kernel proxy'sinden** vermeyi öneriyordu: yalnız defteri açan
oturuma açık, uygulamaya giriş yazmadan. Yazmadan önce araştırıldı ve **bu yol kapalı çıktı.**

- **Kök yolları sorun değilmiş.** Resmî proxy yol öneki değil **alt alan adı** veriyor
  (`https://<id>-<port>-colab.googleusercontent.com/`), yani uygulama kökte durur ve `/api/...`
  tutar.
- **Ama POST çalışmıyor.** [colabtools#3925](https://github.com/googlecolab/colabtools/issues/3925):
  proxy üzerinden POST `500 (Not Allowed)` dönüyor, aynı uygulama ngrok/cloudflared ile çalışıyor,
  konu açık. Google resmî proxy'yi GET'e daraltmış.

QueenAgent'ta proje açmak POST, mesaj göndermek POST, cevap istemek POST, ayar PATCH, silme DELETE.
Yani **cloudflared** — queen-editor'ün seçimi. Bedeli: link herkese açık, ve o bedel ödenmiyor
(aşağıda, "bilerek yapılmayanlar").

*Akış (SSE) artık risk değil: cloudflared akışı taşır, ve kullanıcı "mesajlar akmak zorunda değil,
direkt gelebilir" dedi. Drive'ın yavaşlığı da kabul edildi.*

## Sıra

**54 → 53 → 59** zemini kurar: `dist` depoya girer, belgeler bunu yazar, ve yazma yarım kalmaz
hâle gelir. Bu üçü bitmeden defter yazılamaz — defter, kendi temelini yalanlayan bir depoya
yazılamaz. **55 → 56 → 57** defterin kendisi, hücre sırasıyla. **58** arkadaşının yolunu yazar.
Kullanıcının toplu testi en sonda.

*54, 53'ten önce koşuldu: Madde 53 FOUNDATION'a "`dist` commit'lenir" yazıyor, ve bunu `dist`
gerçekten commit'lenmeden yazmak belgeyi bir commit boyunca yalancı yapardı.*

*(59 sonradan yazıldı, o yüzden numarası büyük; koşudaki yeri Faz 1. Numaralar kaymaz — numara ne
zaman yazıldığını söyler, nerede koşulduğunu değil. Madde 60 vardı ve **düştü**; aşağıya bak.)*

---

## Faz 1 — Zemin

### Madde 53 — FOUNDATION'ın iki kararı artık yanlış

- **Ne çalışır:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) **Karar 1** bugün "uygulama
  yalnız kullanıcının makinesinde çalışır… paylaşmak, henüz vermediğimiz bir karar gerektirir"
  diyor — karar verildi. **Karar 3** "`dist/` commit'lenmez" diyor — değişti. İkisi de düzeltilir,
  ve Karar 1 yereli **birincil** yol olarak korur: Colab eklenen bir yüzey, yerini alan değil.
  Aynı maddede [CLAUDE.md](../../../CLAUDE.md)'nin komut bloğu ve
  [queen-agent/README.md](../../../queen-agent/README.md) düzeltilir.
- **Nasıl görülür:** iki belge deponun bugünkü hâlini anlatıyor; hiçbiri defteri yalanlamıyor.

### Madde 54 — `dist` depoya girer ve girmiş kalır

- **Ne çalışır:** kök `.gitignore`'daki `dist/` kuralına queen-agent istisnası; `frontend/dist`
  commit'lenir. Kural: **kaynakla aynı commit'te derlenip commit'lenir** — queen-editor'ünkiyle
  aynı, aynı sebeple (defter derlemez).
- **Nasıl görülür:** temiz bir klon `npm` çalıştırmadan `python main.py` ile açılıyor.

### Madde 59 — Yazma yarım kalmaz

- **Ne çalışır:** [store.py:27](../../../queen-agent/backend/services/store/store.py#L27) tek yazma
  yolu ve dosyayı **yerinde kesip** yeniden yazıyor. Yerel diskte pencere mikrosaniye; Drive FUSE'da
  bir I/O hatası ya da runtime'ın ortada ölmesi `<chat>.json`'ı yarım bırakır ve o sohbet gider —
  FOUNDATION'ın 1. ilkesiyle ("kullanıcının emeği kutsaldır") çarpışan tek yer. `write_text` geçici
  bir dosyaya yazıp `os.replace` ile üstüne geçer. Atomik ilkel Store'da zaten var: `move` kullanıyor.
- **Nasıl görülür:** yazma ortasında patlayan bir Store eski dosyayı **olduğu gibi** bırakıyor — ne
  yarım ne boş. Drive'da `os.replace`'in aynı bağlama içinde çalıştığı da burada görülür.
- **Yerelde de doğru:** Drive onu yalnızca *sık* hâle getiriyor.

### ~~Madde 60 — Parola kapısı~~ *(düştü, 20 Ağustos)*

Yazıldı, çalıştı, ve **kullanıcı kararıyla geri alındı.** Kaydı burada duruyor çünkü "neden parola
yok" sorusunun bir cevabı olmalı.

Neydi: `QUEENAGENT_PASSWORD` kuruluysa HTTP Basic ile tek bir kapı, kurulu değilse kapı hiç yok.
Neden düştü: her ziyarette parola sormanın bedeli, kimseye verilmemiş rastgele bir adresin riskinden
yüksek bulundu.

Yerine geçen koruma, adresin rastgele ve tek oturumluk olması — ve bunun **ince** olduğu
[FOUNDATION](../../../queen-agent/FOUNDATION.md) Karar 1'de yazılı. Bir gün fikir değişirse iş
küçük: `create_app` içinde tek bir `before_request`, ve arayüzde sıfır değişiklik.

---

## Faz 2 — Defter

### Madde 55 — CONFIG: önce Drive, sonra her şey

- **Ne çalışır:** `queen-agent/app.ipynb`'nin ilk kodu tek bir CONFIG hücresi. Drive **ilk** bağlanır
  (izin penceresi ilk saniyede çıksın). Kök: `MyDrive/queenAgent` — queen-editor'ün `queenEditor`
  klasörünün kardeşi, adı CONFIG'de tek yerde (`DRIVE_FOLDER`). `GITHUB_TOKEN` Colab Secrets'tan
  okunur; yoksa ne yapılacağını söyleyen bir `assert` ile durulur — **yüksek sesle**, ve sebep
  uydurulmadan.
  xAI anahtarı **burada yok**: uygulamanın kendi Settings ekranına girilir ve Drive'daki
  `settings.json`'a düşer — bir kere, sonsuza kadar. queen-editor'den bilerek ayrılan yer.
- **Nasıl görülür:** Secrets boşken hücre ne yapılacağını söyleyerek duruyor; doluyken Drive kökünü
  basıyor.

### Madde 56 — Klon, bağımlılık, ve derlenmiş arayüzün kontrolü

- **Ne çalışır:** `AltanBaysal/Internal-tools` özel bir depo → token'lı klon (sil-ve-yeniden-klonla).
  Token kabuğa, log'a ve hata metnine sızmaz; başarısızlıkta git'in kendi stderr'i maskelenmiş
  basılır. Ardından `pip install -q flask` — Colab'da zaten kurulu olduğu için anında döner, ama
  defter "Colab'da vardır" varsayımına sessizce yaslanmaz. Sonra
  `queen-agent/frontend/dist/index.html` **aranır**: yoksa hücre durur — unutulmuş bir derleme
  burada görünsün, boş sayfa olarak değil.
- **Nasıl görülür:** `dist` commit'lenmemiş bir dalda hücre "derlenmiş arayüz yok" diyerek duruyor.

### Madde 57 — Sunucu kalkar, link basılır

- **Ne çalışır:** `main.py` arka planda başlar; ortamdan `QUEENAGENT_ROOT` geçer. `/api/health`
  90 sn yoklanır, cevap gelmezse sunucunun kendi log'unun son satırları basılıp durulur. Sonra
  **cloudflared** tüneli açılır ve link basılır. Hücre açık kalır (`tail -f`), yoksa Colab
  runtime'ı boşta sayar.
- **Nasıl görülür:** hücre bir link basıyor, link açılıyor, bir soru sorulup cevap alınıyor.
- **Kararın kaydı:** kernel proxy denenmedi bile — POST'u taşımadığı araştırmayla saptandı (yukarı
  bak). cloudflared'in bedeli linkin herkese açık olması, ve bu bedel **ödenmiyor**: düşen Madde
  60'a bak. Linkin yanına bir uyarı basılır — kime verildiyse o kişi uygulamanın tamamına giriyor.

---

## Faz 3 — Kapanış

### Madde 58 — Arkadaşının yolu, ve Drive'da ne olduğu

- **Ne çalışır:** defterin ilk markdown hücresi ve `queen-agent/README.md` sırayı adım adım söyler:
  defteri Colab'a yükle → 🔑 Secrets'a `GITHUB_TOKEN` ekle → Run all → Drive iznini ver → linke gir
  → **Settings'e kendi xAI anahtarını yaz**. Türkçe, çünkü okuyan bir insan.

  Aynı yerde **Drive'da ne olduğu** anlatılır. Yapı zaten var, uydurulmuyor — yazılıyor, ki klasöre
  bakan biri ne gördüğünü bilsin:

  ```
  MyDrive/queenAgent/
    settings.json          ← xAI anahtarı
    trash/                 ← silinen projelerin tamamı
    p<12 hex>/             ← bir proje
      project.json         ← adı ve doğduğu an
      chats/<id>.json      ← bir sohbet, mesajlarıyla
      files/               ← modelin ürettiği dosyalar
      trash/               ← bu projeden silinen sohbet ve dosyalar
  ```

  Dört uyarı da burada, çünkü hiçbiri koddan anlaşılmaz:
  1. **Link parolasızdır — kime verilirse o kişi her şeye girer.** Anahtarı harcayabilir, bütün
     dosyaları okuyabilir. Adres rastgele ve oturumluk, koruma bundan ibaret. Bu, birinci sırada
     yazılır.
  2. **Aynı klasöre iki oturum bakmasın** — uygulamada kilit yok.
  3. **Çalışırken klasörü Drive web arayüzünden karıştırma** — Drive aynı klasörde aynı adlı iki
     dosyaya izin verir, FUSE birini seçmek zorunda kalır.
  4. **xAI anahtarı Drive'da düz metin.** Yerelde de öyle, ama Drive'da Google'a senkronlanır.
- **Nasıl görülür:** daha önce hiç açmamış biri, sormadan sonuna kadar gidiyor; Drive klasörüne
  bakınca ne olduğunu anlıyor.

---

## Bilerek yapılmayanlar

- **Hiçbir giriş yok** *(kullanıcı kararı, 20 Ağustos)*. Ne parola ne hesap: linki tutan her şeye
  giriyor. Düşen Madde 60'a ve FOUNDATION Karar 1'e bakılsın — orada bunun ince bir koruma olduğu
  yazılı, ki bir gün fikir değişirse sebep aranmasın.
- **Defter derlemiyor.** Madde 54 bunun için var: `npm ci` her oturumda ~1.5 dakika.
- **Ortak çalışma yok.** Herkes kendi Drive'ında kendi kökünü taşır.
- **Yerel yol değişmiyor.** `python main.py` bugünkü gibi.
- **Drive'ın yavaşlığı için bir şey yapılmıyor** *(kullanıcı kararı)*. Her kayıt dosyanın tamamının
  yüklenmesi ve rayın her açılışta dosya başına `mtime` sorması ölçülmüş bir sorun değil; FOUNDATION
  3 ölçülmemişi optimize etmeyi yasaklıyor. Rahatsız ederse kendi maddesi olur.
- **Akış için bir şey yapılmıyor** *(kullanıcı kararı)*. Cevabın kelime kelime gelmesi kritik değil.

## Kapanış

Maddeler durmadan spec → plan → test → uygulama ile gider. Defter **çalıştırılarak değil okunarak**
test edilir — `.ipynb`'nin JSON'u ayrıştırılıp hücrenin ne yaptığı sorulur; desen
[queen-editor'ün defter testi](../../../queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py).
Kullanıcının toplu testi en sonda: defter açılır ve bir tur atılır.
