# Eksikler

Bulunan her şey buraya. Düzeltmek ayrı iş — burası sadece liste.

Önceki 12 madde [v7 yol haritası](../docs/superpowers/plans/2026-08-13-queen-editor-v7-roadmap.md)
oldu ve kapandı. Aşağıdakiler o koşudan artan, **kararı sana kalan** iki şey.

## Claude

- **Galeri karoları tam boy PNG çekiyor.** Bir kare ~1.5–2.5 MB; ilk açılışta ekrandaki 8 karo
  tünelden ~15 MB indiriyor. Karolar için küçük önizleme üretmek gerek — ne zaman üretilecek,
  nereye yazılacak, adı ne olacak, kare değişince ne olacak: kendi tasarımını ister.
- **Başarısız karede hover'la karartma iniyor.** Fare gelince kareyi örten koyu katman ve ortasında
  "Tekrar dene". Bu tasarımın kendi kararı; "hover'da kart ortalanıyor" derken bunu mu kastettin,
  yoksa etiketin köşe atlaması mıydı (o düzeltildi)?

## Sen

- **Fotoğraf üreticisini kuramıyorum.** "Kur"a basınca satır şunu diyor: *"Fotoğraf üreticisi
  kurulu değil. HTTP Error 403: Forbidden"*.
- **Video üreticisini de kuramıyorum.** Aynı cümle: *"Video üreticisi — HTTP Error 403:
  Forbidden"*.
- **"Foto kuyrukta" yazısı yanlış köşede.** Şu an karenin sol altında; sol üstte olması lazımdı.
- **Ses üreticisini kuramıyorum.** "Kur"a basınca satır şunu diyor: *"MMAudio kütüphanesi kuruldu
  ama bu süreçte görünmüyor — uygulamayı yeniden başlat."*
- **Video panelindeki açıklama kalksın:** *"Video prompt'u otomatik: LLM her fotonun kendi
  prompt'undan yazar. Detayda okunur, düzenlenir."*
- **Video prompt'u yazılamıyor, üretim duruyor.** Kuyruk şunu diyor: *"Aynı kare 3 kez denendi —
  üretim durduruldu / xAI HTTP 400 / `{"code":"invalid-argument","error":"Incorrect API key
  provided. You can obtain an API key from https://console.x.ai."}`"*. Anahtar Colab Secrets'ta yok
  mu, yanlış mı, yoksa uygulamaya yanlış mı geçiyor — üçü de mümkün, bakılmadı.
- **Üretim durduğu hâlde kareler "video kuyrukta" diyor.** Yukarıdaki hata kuyruğu durduruyor ama
  karelerin etiketi hâlâ sırada bekliyormuş gibi duruyor.
- **Video panelinde seçili kare sayısı artmıyor.** Galeride kare seçiyorum, video panelindeki sayı
  yerinde kalıyor.
- **Seçimi kaldırınca ✓ halkaları kalıyor.** Kareleri seçip sonra seçimi kaldırıyorum: alttaki
  çubuk ("Tümünü seç" vb.) kayboluyor, ama karelerin üstündeki yuvarlaklar duruyor. Kafa
  karıştırıyor — seçim sürüyor mu bitti mi anlaşılmıyor.
