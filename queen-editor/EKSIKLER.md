# Eksikler

Bulunan her şey buraya. Düzeltmek ayrı iş — burası sadece liste.

Aşağıdaki 12 madde [v7 yol haritası](../docs/superpowers/plans/2026-08-13-queen-editor-v7-roadmap.md)
oldu.

## Claude

- **Ses üreticisi yanlış tip döndürüyor.** `MMAudioGenerator.generate` `(ad, bayt)` veriyor, oysa
  sözleşme yalnız bayt (`run_loop.py:156` dosyayı kendi adlandırıyor). İlk ses işi düşer.
  Testler yakalamadı: hiçbir test üreticiyi döngüyle birlikte koşmuyor.
- **Video süresi iki yerde:** grafta node `178` = 5 sn, export'ta `VIDEO_SECONDS = 5`. Bugün
  tutuyor; graf değişirse export yanlış süre gösterir.

- **Galeri karoları tam boy PNG çekiyor.** Bir kare ~1.5–2.5 MB; ilk açılışta ekrandaki 8 karo
  tünelden ~15 MB indiriyor. Karolar için küçük önizleme üretmek gerek — v7 Görev 8'in
  taşıyabileceğinden büyük iş, senin kararın.

## Sen

- **Notebook hiç model indirmemeli.** Bütün indirmeler uygulama açıldıktan sonra kurulum
  ekranından. Şu an notebook fotoğrafı (`CIVITAI_MODELS`, `GROUPS["photo"]` boş) ve MMAudio
  modelini indiriyor — ikisi de kurulmamış gelecek.
- **Yan bar açık ikona tekrar tıklayınca kapanmalı.** Üret vb. açıkken aynı ikona basınca panel
  komple kapansın, tuval genişlesin — kod editörlerindeki gibi.
- **Kur'a basınca anında geri bildirim yok.** Video üreticisinde tepki gecikmeli geliyor, arada ne
  olduğu belli değil. Tıklar tıklamaz durum görünmeli.
- **Fotoğraflar çok yavaş yükleniyor.** Uygulama açılışında galeri geç doluyor.
- **Her geçişte yükleme baştan başlıyor.** Detayda da bekliyor, galeriye dönünce de fotoğraflar
  yeniden yükleniyor.
- **Kurulum çubuğu gerçeği göstermiyor.** "Video üreticisi / kuruluyor… bitince bu kart kaybolur"
  kartındaki progress bar indirmeyle eşleşmiyor — kaldıralım.
- **Kuyruğa eklenen kare ~1 dakika ekrana düşmüyor.** "Eklendi" diyor ama görünmüyor, insan bir
  daha basıyor. Eklenir eklenmez listede olmalı.
- **Fotoğraf üretimi hiç çalışmıyor.** `ComfyPhotoGenerator.generate() got an unexpected keyword
  argument 'source'` → aynı kare 3 kez denenip üretim duruyor. Üretici sözleşmeye uymuyor
  (yukarıdaki ses hatasının aynısı, bu sefer fotoğrafta).
- **"Foto kuyrukta" yazısı okunmuyor.** Çok soluk, daha beyaz olmalı.
- **Kare hover'da yerinden oynuyor.** Üstüne gelince kart garip biçimde ortalanıyor; yerinde
  kalmalı.
