# Madde 307 — Loop videonun dikişi: ölçüm ve yol seçimi

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 0/2 — yol seçilmeden test yazılmaz.

## Kullanıcıdan gereken

**Bir karar, ve bir ölçüm.** Yol haritası bu maddeyi böyle açtı: *"madde ölçümle başlar, ve o ölçüm
kullanıcının kartındadır."* GPU kullanıcıda, ve dikişin göze nasıl göründüğü ancak orada görülür.

## Sorun

Loop modunda videonun **ilk ve son karesi aynı fotoğraf** *(`run_loop.py` — `end = source`)*, yani
dikişte **görüntü** uyuyor. Uymayan şey **hareket**: model son kareye oturmak için yavaşlıyor,
sonraki tekrar duruştan başlıyor. Klibi elle beş kez arka arkaya koyunca beş nabız gibi okunuyor.

*(Kullanıcı, 21 Eylül — "video üretici tempoyu kestiği için çok belirgin oluyor".)*

## İki yol, ve ikisinin bedeli

**A — Prompt tarafı.** Loop modunda hareketi **döngüsel** yazdırmak: biten bir hareket değil, kendine
dönen bir hareket *(sallanma, nefes, yürüyüş, saç savrulması)*. Bugün prompt'u yazan model **kipi
hiç bilmiyor** — `PromptWriter.write(prompts)` yalnız fotoğrafın sözlerini alıyor. Kip yazıcıya
geçirilince talimat loop için ayrı bir cümle kazanır.

*Bedeli:* yok. Hiçbir kare atılmıyor, hiçbir şey kırpılmıyor.
*Riski:* tek başına yetmeyebilir — yavaşlama H3'ün son kareye oturma zorunluluğundan geliyor.

**B — Kesim tarafı.** Klibin sonundaki yavaşlama karelerini atmak *(ffmpeg, N kare)*.

*Bedeli:* klip kısalıyor, ve **son kare artık ilk kare değil** — yani dikişte küçük bir görüntü
atlaması doğabilir. Kullanıcının kabul cümlesi ikisini birden istiyor: *"dur-kalk görünmüyor, ve
dikişte görüntü atlaması da yok."*
*Bilinmeyeni:* kaç kare. Bu **ölçüm**, ve kullanıcının kartında.

**A + B.** Döngüsel hareket, atlamayı A'nın kendisi küçültür; sonra gerekiyorsa küçük bir kesim.

## Önerilen sıra

**Önce A.** Ölçüm istemiyor, hiçbir şey kaybettirmiyor, ve B'nin riskini de azaltıyor: hareket zaten
döngüselse, sondan birkaç kare atmak görüntüde atlama yaratmaz. Kullanıcı A'lı bir klibi beş kez
yan yana koyup bakar; hâlâ nabız varsa B ölçülür ve kendi turunda eklenir.

## Bitti sayılır

Kullanıcı kararı verir; seçilen yol iki turla koşulur.
