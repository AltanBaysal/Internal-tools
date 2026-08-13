# Backlog — Queen Editor

Bilerek ertelenmiş işler. Her maddenin yanında **neden beklediği** yazar; sebebi olmayan madde
buraya girmez.

**Bu bir bulgu listesi değil.** Colab turunda çıkan hatalar bir sonraki yol haritasını açar
(`docs/superpowers/plans/`), buraya yazılmaz. Buraya yazılan şey, "bunu gördük ve şimdilik
yapmamaya karar verdik" olanıdır.

Bir madde kapanınca **silinir** — kapandığını commit'ler zaten anlatıyor.

## Sıradaki büyük işler

Kullanıcının söylediği sırayla. Üçü de kendi tasarımını ister; buradaki satırlar yalnız işin ne
olduğunu ve elde ne olduğunu tutuyor.

- **Looplu video üretme.** Başı sonuna bağlanan, kesintisiz dönen video. Grafik hazır ve kanıtlı:
  `collab-toolbox/loop_maker/comfy_ui.ipynb` (Wan 2.1 VACE). Queen Editor onu kod olarak değil
  bilgi olarak devralır — kendi üreticisini yazar.
- **Fotoğrafı bağlamalı video.** Bugünkü video tek fotoğraftan üretiliyor (I2V). Bu, kareleri
  birbirine bağlayan video — biri bitip öteki başlarken arası üretilen. *Netleşmesi gereken:*
  "bağlamak" iki kare arasını mı doldurmak, yoksa bir karenin videosunu bir sonrakinin fotoğrafına
  mı bağlamak.
- **Üretme hızı.** Bugün ne kadar sürdüğü ölçülüyor ama kimse bakmıyor: motor her kare için
  `⏱ <dosya> · render <n> sn · drive <n> sn` satırı yazıyor — GPU'nun payı ile Drive'a yazmanın
  payı zaten ayrı. Yani iş, önce o satırları toplamak, sonra hangisinin büyük olduğuna göre karar
  vermek.

## Kararı sende

- **Galeri karoları tam boy PNG çekiyor.** Bir kare ~1.5–2.5 MB; ilk açılışta ekrandaki 8 karo
  tünelden ~15 MB indiriyor. Karolar için küçük önizleme gerek — ama ne zaman üretilecek, nereye
  yazılacak, adı ne olacak, kare değişince ne olacak: hepsi kendi tasarımını ister.
- **Başarısız karede hover karartması.** Bugün var ve çalışıyor: fareyi getirince kareyi örten koyu
  katman ve ortasında "Tekrar dene". Soru duruyor — *"hover'da kart ortalanıyor"* derken bunu mu
  kastetmiştin? Değilse neyi kastettiğin.

## Kararı verdik, sırası gelmedi

- **Detay sayfası yalnız kendi katmanını göstersin.** Bugün açık sekmenin *altındaki* katmanlar da
  görünüyor — video sekmesinde fotoğrafın dosya adı ve fotoğrafın prompt'u da yazıyor. Bu bir hata
  değil, madde 75'in kararı: "bu neyden yapıldı" görünsün diye. Karar değişiyor.

  Kalacak olan: **Sıra `n / m`** ve **kartın kendi adı** (galerideki karonun altında yazan ad).
  Gidecek olan: katman başına açılan dosya adı satırları (`Foto` / `Video` / `Ses`) ve alttaki
  katmanların prompt kutuları.

  *Uygulayan bilsin:* video prompt'u çoğu zaman boş (LLM'in yazması bekleniyor), yani alttakiler de
  gidince sekme boş bir sayfaya dönüşebilir — o boşluğun ne diyeceğine karar vermek işin parçası.
  Ayrıca hiç üretilmemiş karede ad bugün *"Dosya adı (planlanan)"* diye etiketleniyor; tek satıra
  inince o ayrım korunacak mı, sorulacak.

- **Video paneli yanlış sebebi söylüyor.** Seçtiğin kareler henüz üretilmemişse panel *"Tüm
  karelerin videosu var — üretilecek bir şey yok"* diyor. Sebep o değil: seçilenlerin daha
  fotoğrafı yok. (2026-08-14'te bulundu, o gün "boş ver" dendi — cümle küçük, yanılttığı an dar.)
- **Detaydaki Foto / Video / Ses sekmeleri ayrılsın.** Bugün bitişikler: aradaki `-1` piksel onları
  tek bir parçaya çeviriyor, kararı madde 73 — *"üç ayrı hap değil, üç durumu olan tek denetim"*.
  Karar değişiyor, aralarına boşluk girecek. *Uygulayan bilsin:* ayrılınca "hangisi açık" bilgisini
  taşıyan tek şey renk kalıyor (bugün bitişiklik de taşıyordu), dolayısıyla açık sekmenin ayırt
  edilebilirliğine bir kez daha bakmak gerekir.

- **Sesin tohumu kayda geçmiyor.** Ses üreticisi eksik tohumu kendisi seçiyor ama satıra `None`
  yazılıyor, yani bir ses satırından yeniden üretilemiyor. Video da bugün böyle. Düzeltmek
  üreticinin kullandığı tohumu geri döndürmesini, yani üç üreticinin de port'unu değiştirmeyi
  gerektirir.

## Colab turuna bağlı

- **Sürükleme gerçekten düzeldi mi.** v12 karoyu basıştan önce sürüklenebilir yaptı; teşhis
  çıkarımdı, burada tarayıcı yok. Kart hâlâ kalkmıyorsa sıradaki şüpheli karonun içindeki bağlantı
  ve resmin `draggable={false}` zinciri — o zaman resmin üstünden değil **karonun kenarından**
  sürüklemeyi dene, ikisini ayırt eder.
