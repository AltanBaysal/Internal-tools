# Madde 255 · Export ekranı disclaimer adımını söyleyecek — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m255-disclaimer-adimi-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**Tek satır:** `ExportScreen.jsx`'te `merging` durumunun cümlesi `"birleştiriliyor…"` yerine
`"Disclaimer ekleniyor…"` oluyor. Koşul, durum listesi, canlı nokta, sayaç dalı — hiçbiri
değişmiyor.

**Neden ikinci bir cümle değil:** düğmenin içinde tek satır var, ve kullanıcının sorusu *"şu anda
ne yapılıyor"*du. Adım gerçekten iki iş yapıyor *(birleştirme + bindirme)*, ve ikisinden **süreyi
yiyen** söyleniyor: bindirme kodlama demek *(250)*, ve 259'dan sonra kodlanan çerçeve
`1920 × 1080`. Birleştirmenin kendisi `concat` kopyası kadar hızlı olan taraf.

**Neden arka uca dokunulmuyor:** adımın kendisi zaten arkadan geliyor — `run_export`
`state="merging"` bildiriyor — ve o ad doğruyu söylüyor. Değişen tek şey o durumun **ekranda
hangi cümleyle göründüğü**, ve bu sunum işi *(CODE-STANDARD)*. Bir durum adını cümleye çevirmek
tarayıcının işi; kuralın kendisi arkada kalıyor *(FOUNDATION 4)*.

**Yorum düzeliyor:** `merging` dalının yanındaki açıklama artık adımın neden disclaimer'la
anıldığını söylüyor.

## Bunun getirdiği

**Kazanç sıfır saniye**, ve buna rağmen şikâyetin yarısı: kullanıcı beş dakikayı bekledi ve
ekranın söyleyecek bir şeyi yoktu. *(Araştırmanın K6'sı — en ucuz kaldıraç.)*

**Yüzde yok**, ve neden olmadığı yol haritasında duruyor: süre ölçülmedi, ve yüzde exporter'ın
ffmpeg'i bekleme biçimini değiştirirdi. Ölçüm dakikaları gösterirse yüzde kendi maddesi olur.

## Ön yüz kuralı

`frontend/dist/` **aynı commit'te** yeniden build'leniyor. Defter depoyu klonluyor ve hiçbir şey
build etmiyor *(FOUNDATION 3)*: build'siz bir commit, Colab'da eski ekranı servis eder ve maddenin
ekranda hiçbir karşılığı olmaz.

## Bu turda değişen

- `frontend/src/features/photo_generation/ExportScreen.jsx`: `merging` durumunun cümlesi ve
  yanındaki yorum.
- `frontend/dist/`: yeniden build.
