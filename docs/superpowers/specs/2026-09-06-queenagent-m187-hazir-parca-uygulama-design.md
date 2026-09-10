# Madde 187 · uygulama turu — hazır prompt parçaları

**Kaynağı:** [test turu](2026-09-06-queenagent-m187-hazir-parca-testler-design.md), `8897279`'da
11 kırmızı.

---

## Üç yer

`prompt.py`'de eşleme ve iki metin, `tools.py`'de araç ve dalı, `modes.py`'de `READS`'in ikinci
üyesi. Başka hiçbir şey değişmiyor.

## Ne konuyor: yedi pozisyon

Kullanıcının verdiği örnek pozisyonlardı, ve **tohum olarak yalnız onlar** konuyor. Eşleme adla
anahtarlanmış, yani ileride başka bir tür parça — bir ışık kalıbı, bir kadraj — aynı kapıdan
girer; bugün varsaymak, kullanılmayacak bir şeyi gözden geçirilecek metinlerin arasına koymak
olurdu.

Her giriş `SDXL_PROMPT_RULES`'a uyuyor: kısa virgüllü parçalar, **sayı yok** *(sayı karakterin
kendi girişinin işi)*, **kalite etiketi yok** *(onu kod her promptun başına yazıyor)*, ve **kıyafet
yok** *(o bir outfit girişi)*. Üçü de testle tutuluyor.

## Anahtar `folded`, ve sebebi

`naming.folded` — *Cowgirl*, *cowgirl*, *COWGIRL POSITION* aynı yere düşüyor. Modelin bir raundu
büyük harfe ödemesi için sebep yok, ve o raunt bir şey de öğretmezdi.

Anahtarların kendisi de katlanmış hâlde yazılıyor: iki yazım kuralı — biri anahtar için, biri
arama için — ilk uyuşmazlıkta birbirini bulamayan bir eşleme demek.

## Cevabın üç hâli

| Ne soruldu | Cevap |
|---|---|
| bilinen bir ad | adı ve etiketleri |
| bilinmeyen bir ad | sorulan ad, ve **bilinenlerin listesi** |
| hiç ad yok | bilinenlerin listesi |

İkincisi `build_prompts`'un kalıbı: bir ıska, bilinenlerle birlikte cevaplanıyor. Üçüncüsü keşif
yolu — modelin *"elinde ne var"* diye sorması bir raunt, listeyi her isteğe bindirmek her raunt.

## `READS` ikiye çıkıyor

`read_file`'ın yanına. `modes.py`'nin bugünkü yorumu *"Madde 172'den beri tek"* diyor ve yarın
yanlış olacak — yorum kodla çeliştiğinde düzeltilen yorumdur.

Sonucu: araç **her kipte sormadan** koşuyor. Sorulacak bir şey yok; ne bir dosya açılıyor ne bir
şey yazılıyor, ve kullanıcının korunacağı bir taraf yok.

## Gösterdiğini kareye koymuyor

Cevap metin, ve orada bitiyor. Kareye koymak `update_frame`'in işi — bir araç iki iş yaparsa
hangisini yaptığı cevapta kaybolur, ve bu deponun fiil ayrımı zaten böyle.

**Madde 130 ile çelişmiyor:** o kural `build_prompts`'un **ürettiği** dosya için, ve dosya zaten
projede duruyor. Hazır parçanın dosyası yok; gösterilmezse hiçbir yerde görünmüyor.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 11 kırmızı kapanıyor; öteki üç takım kımıldamıyor.
