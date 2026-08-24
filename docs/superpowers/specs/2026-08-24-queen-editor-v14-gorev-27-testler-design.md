# v14 Görev 27 — Tünelin taşıma protokolü: TEST döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** [araştırma belgesi](../research/2026-08-23-queen-editor-galeri-yavasligi.md) §0
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 27

## Neyin testi yazılıyor

Galeri, çok fotoğraflı bir projede kullanılamaz hâle geliyordu: kareler saniyede ~112 KB ile
iniyor, bir fotoğraf 17 saniye sürüyor, boru dolunca arayüzün istekleri zaman aşımına düşüp
"sunucuya ulaşılamadı" veriyordu.

İki tur ölçüm zinciri halka halka eledi — Drive, Flask, tarayıcı önbelleği, CPU, kuyruk ve Colab'ın
çıkış ağı temiz çıktı. Geriye tek değişken kaldı:

| | Süre | Hız |
|---|---|---|
| Tünel, varsayılan (QUIC / UDP) | 17.74 sn | 0.11 MB/sn |
| **Aynı tünel, `--protocol http2` (TCP)** | **0.18 sn** | **10.01 MB/sn** |

Aynı makine, aynı dakika, aynı boyutta iki dosya; tek fark taşıma protokolü. Colab'ın ağı UDP'yi
kısıyor, TCP'yi kısmıyor.

**İlaç tek bayrak.** Bu döngü o bayrağın yerinde olduğunu sabitleyen testleri yazar; bayrağı
koymaz.

## Neden metin testi

Defter Colab'da koşuyor, burada değil. Bayrağın **etkisi** testle görülemez — 90 katı ölçen şey
Colab'daki teşhis koşusuydu ve hükmü araştırma belgesi taşıyor.

Testle görülebilecek tek şey **bayrağın orada olduğu**. Değeri şu: bayrak tek bir kelime ve ne
yaptığını kendi söylemiyor. Defteri düzenleyen biri onu farkında olmadan düşürürse galeri sessizce
90 kat yavaşlar ve sebebi kimse göremez. Test o düşüşü commit anında yakalar.

Bu, defterin metnini okuyan mevcut testlerle aynı cins ve aynı dosyada duruyor.

## Sabitlenecek iki şey

| # | Ne | Neden |
|---|---|---|
| **A1** | Flask hücresindeki cloudflared komutu `--protocol http2` taşıyor | Bayrağın kendisi. Düşerse galeri 90 kat yavaşlar |
| **A2** | Aynı hücre bayrağın **neden** orada olduğunu yazıyor | Bayrak sebebini söylemiyor. Sebep yazılı değilse bir sonraki okuyan onu gereksiz sanıp siler |

A2, deponun *"yorum NEDEN'i söyler"* ve *"sebep uydurulmaz"* kurallarının bu satırdaki karşılığı.
Aranan kelime **QUIC**: bayrak varsayılan olarak neyin yerine geçtiğini söylemeden anlamlı değil.

## Nerede duracak

`queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`.

Defteri metin olarak okuyan tek dosya bu ve gereken iki yardımcı (`_source`, `_cell`) orada zaten
var. İkinci bir dosya açmak yardımcıları kopyalamak olurdu.

**Dosyanın başlık açıklaması genişliyor.** Bugün *"defter panelin saydığını kuruyor"* diyor, oysa
dosya çoktan xAI yoklamasını, MMAudio'yu ve model ağacının yolunu da tutuyor. Tünel bayrağı da
girince açıklama iyice yanlış olur — depo kuralı gereği metin koda uydurulur.

## Kapsam dışı

- **Bayrak bu döngüde konmuyor.** `app.ipynb` bu commit'te değişmiyor.
- **Defterin hücre yapısı sabitlenmiyor.** Testler yalnız Flask hücresinin metnine bakıyor;
  hücrelerin nasıl bölündüğü bu maddenin konusu değil.
- **Teşhis hücresi commit'lenmedi.** Ölçüm aletiydi; defter ölçümden sonra eski hâline döndürüldü,
  kodu araştırma belgesi §6.1'de duruyor.
- **Hızın kaç kat arttığı yeniden ölçülmüyor** — kullanıcı kararı (24 Ağustos):
  *"hızlanması kesinse miktarını ölçmek önemli değil şimdilik, yine sorun yaşarsak ölçeriz"*.
