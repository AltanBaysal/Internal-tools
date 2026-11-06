# Yeni editör — 7. Üretim ve kuyruk

Üretimin, kuyruğun ve export'un nasıl çalıştığı.

## Hatalar ve süreler

- **ComfyUI çökerse:** ComfyUI cevap vermezse core 45 sn bekler, sonra ComfyUI'yi kendisi yeniden
  başlatır (~90 sn); kesilen iş baştan denenir. Aynı iş yeniden başlatmadan
  sonra da ComfyUI'yi düşürürse ya da ComfyUI açılamazsa kuyruk durur. Durmanın nedeni ComfyUI'nin
  kendi sözüdür (log'unun ilgili satırları); agent onu projenin `queue/wait`'inden ve `queue`'sundan görür
  ve kullanıcıya söyler. ComfyUI'nin işe verdiği hata (ör. geçersiz prompt) da kuyruğu durdurur;
  neden yine ComfyUI'nin kendi sözüdür, iş sıranın başında bekler (2. adım). queen-editor'da ComfyUI'yi yalnız notebook başlatıyordu (madde 433); yeni
  core onu kendisi başlatıp yeniden başlatabilir.
- **Takılan üretim:** fotoğraf 5 dakika, video 10 dakika; birlikte üretilen varyantlarda süre
  varyant sayısıyla çarpılır. Süre dolunca üretim durdurulur, kuyruk durur, iş sıranın
  başında bekler; neden ComfyUI'nin son sözüdür. Sınır olmazsa takılan tek bir üretim kuyruğu sonsuza kadar tutar.
  queen-editor'da fotoğraf 15, video 30 dakikaydı.
- **Core yeniden başlayınca:** core ComfyUI'yi başlatır ve cevap vermesini bekler (~90 sn, madde
  433), sonra çalıştırdığı projenin kuyruğu kendiliğinden sürer. Bu sırada kuyruk "ComfyUI açılıyor" der. Kuyruk yeniden
  başlamadan önce durdurulmuşsa durmuş kalır.
- **İptal:** ComfyUI'nin durdurma komutu o an çalışanı durdurur, hangi iş olduğunu sormaz. Bu yüzden
  iptal gelince core önce sıradaki işi başlatmaz; ComfyUI'ye durdurmayı yalnız iptal edilen iş hâlâ
  çalışıyorsa gönderir; ComfyUI durunca kuyruk sürer. Durdurma başka bir işe çarpmaz; bedeli iptalde
  birkaç saniyelik beklemedir.

## Sıra ve maliyet

- **Model geçişi:** fotoğraf ile video arasında geçiş modeli yeniden yükletir; kullanıcıya göre bu
  10–15 saniye sürer. Bedeli küçük olduğu için core ya da model listesi bunu ayrıca söylemez; sırayı agent
  kurar. Colab'da ölçülecek.
- **Süreler:** iş kaydı yalnız üretim süresini tutar; agent onu `GET /projects/{p}/jobs/{id}`'de, kullanıcı
  UI'da kartta görür. Üretim süresi modelin çalıştığı süredir (ComfyUI'ye gidişten sonucun
  gelişine); kuyrukta bekleme, Drive ve yarıda kalan denemeler girmez. Birlikte üretilen varyantlarda
  süre varyant sayısına bölünür (madde 405, 411). Ayrıntılı süreler (üretim, Drive'dan indirme,
  Drive'a yükleme, toplam) log'a yazılır, debug ve analiz için. Agent'ın context'i gereksiz
  sayılarla dolmaz. Log Colab'ın diskindedir ve 5 dakikada bir Drive'a da gider (10. adım).

## Yarışlar

- Bir iş biterken silme, iptal ya da proje silme: dosya önce yüklenir, sonra kaydedilir; aradaki
  silme temiz kazanır, silinen proje geri gelmez (madde 513, 519, 523). Nasıl: 4. adım.
- Bu Colab'da çalışan boş bir kuyruğa ya da boştaki bir Colab'dan verilen iş hemen başlar; onu
  çalıştıracak biri hep vardır (madde 511).
- **Kuyruğun bütün sırası verilirken** (`PATCH /projects/{p}/queue`) o arada başlamış ya da bitmiş işler
  atlanır, geri kalan sıra uygulanır; cevap atlananları söyler (madde 480, 481). Eksik ya da hiç var
  olmamış iş yine hatadır. Karelerin bütün sırası (`PATCH /projects/{p}/frames`) bu yarışa girmez: kareler iş
  verildiği an sıraya girdiği için biten iş sırayı değiştirmez.

## Export

- **Aynı anda bir export,** Colab başına. Biri sürerken istenen ikinci export "şu an başka bir
  export sürüyor: `<kimlik>`" hatasıyla döner; agent onu `GET /projects/{p}/exports/{id}/wait` ile bekler. Neden:
  birleşik export her klibin çözücüsünü açık tutar, bellek klip sayısıyla büyür; Colab'da 2 vCPU
  var ve bellek ComfyUI'yle paylaşılır.
- **İlerleme:** kuyruğun ilerlemesi kalan iş sayısıdır; projenin `queue`'sundaki bekleyen işlerden
  sayılır, ayrıca tutulmaz. Export ve tek bir işin kendi ilerlemesi gösterilmez; yalnız "sürüyor"
  görünür.
- **`/wait` en çok 90 sn bekler:** Colab'ın tüneli ~100 sn sessiz kalan isteği keser (madde 518).
  Süre dolunca "henüz bitmedi" döner, çağıran yeniden bekler.
- Yarım export: başarısız olan ya da core yeniden başlayınca yarıda kalan export, yazdıklarını geri
  alır (madde 94). Nasıl: 4. adım.
- ffmpeg tuzakları: her klibin sesi görüntü uzunluğunda kesilir (521); sesi olmayan klibe sessizlik
  eklenir (286); kare hızı birleşik çıktıya verilir, kliplere değil (478); ffprobe çıktısı JSON
  okunur (288); birleşik dosyanın adı kliplerinkiyle çakışmaz (474).
- **Kodlama işlemcidedir.** Ekran kartıyla kodlama sonraya kaldı (bkz. Sonraya kalanlar).
