# Madde 193 · test turu — dosyanın üstünde kopyala düğmesi

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 193.

---

## Bugün ne oluyor

`build_prompts` promptları bir dosyaya yazıyor ve sohbete basmıyor *(Madde 130, ve o kural yerinde
kalıyor)*. Dosya `FilePanel`'de düz metin olarak açılıyor, ve prompt'u almanın tek yolu elle
seçmek — `.py` dosyasında satır satır, kaydırma çubuğunun içinde.

`Download` var, ama o diskin cevabı: kullanıcı prompt'u ComfyUI'ye yapıştıracak, indirilen bir
dosyayı açmayacak.

## Ne kurulacak

Başlıkta bir **kopyala ikonu** — `Refresh`'in yanında, aynı satırda. Basınca **dosyanın tamamı**
panoya gidiyor.

### Ekrandaki metin, diskteki değil — ve sebebi `Download`'unkinin tersi

`Download` **yeniden okuyor**, çünkü diske inen şeyin güncel olması gerekiyor. Kopyalama okuyamaz:
**pano bir kullanıcı hareketine veriliyor**, ve bir tarayıcı bir tık geç gelen yazmayı reddedebilir.
Yani yazma basışın kendisinden gitmek zorunda, `await`'ten sonra değil.

Bu bir taviz değil, çünkü Madde 192 az önce tam bunu kapattı: ekrandaki metin turun sonunda ve elle
basılan düğmede tazeleniyor. Ekranda duran şey artık güvenilir.

### Her dosyada, ve prompt başına düğme yok

`.py`'ye özel yapmanın sebebi yok; genel olunca plan da senaryo da kopyalanabiliyor.

Prompt başına düğme **bilerek** yapılmıyor, ve testi de var: Markdown bir dosya ekranda ayrıştırılmış
duruyor — `# Title` bir `<h1>`. Panoya giden şey **kaynağın kendisi**. Ön yüz `render_module`'ün
yazdığı şekli ikinci kez tanımaya kalkarsa, o okuyucu yazıcıdan ayrıldığı gün düğmeler yanlış metni
kopyalar.

### Cevabı kendi adında veriyor

Emsal queen-editor'de: `RawOutput` ve `PhotoDetail`'in `CopyButton`'ı. İkon kendi adıyla ve rengiyle
cevap veriyor, panele bir satır eklemiyor — başlığın yanında beliren bir kelime altındaki kutuyu
aşağı iter. QueenAgent'ın arayüzü İngilizce, yani `Copy` → `Copied` / `Could not copy`, ve 2.5
saniye sonra geri.

Kopyalanacak bir şey yokken **sönük ama duruyor**: gelip giden bir ikon başlığı seğirtir.

## Testler

### `FilePanel.test.jsx`

1. **kopyalanan şey dosyanın tamamı** — pano `file.text`'i alır.
2. **ekranda çizilen değil, kaynağın kendisi** — `# Title` bir `<h1>` olarak duruyorken panoya
   `# Title` gider. Maddenin asıl cümlesi bu.
3. **indiği söyleniyor** — düğmenin adı `Copied` olur.
4. **inmediği de söyleniyor** — pano reddederse `Could not copy`. Sessizlik, kullanıcının metni
   aldığına inanması demek.
5. **cevap panele satır eklemiyor** — `Copied` sayfada bir metin olarak yok; yalnız düğmenin adı.
6. **henüz gelmemiş dosyada kopyalanacak bir şey yok** — düğme kapalı, ve ekrandan kaybolmuyor.

### `App.test.jsx`

7. **dosya açılır, basılır, içerik panodadır** — maddenin *nasıl görülür*'ü, gerçek ekranda.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` ön yüzünde 7 kırmızı — düğme hiç yok, yani
hepsi `Unable to find role button with name Copy` diye düşüyor. Arka uçlar ve `queen-editor`
kımıldamıyor: **884 · 739 · 591** yerinde.
