# Madde 184 · uygulama turu — karakterler önde, mekân sonda

**Kaynağı:** [test turu](2026-09-06-queenagent-m184-prompt-sirasi-testler-design.md), `c88279a`'da
22 kırmızı.

---

## Tek fonksiyon, tek döngü gövdesi

`build_prompts`'un kare döngüsü. Bugün iki parça kuruyor — `lead` ve arkadakilerin blokları — ve
mekân, action, kamera `lead`'in içinde. Yarın üç parça:

| Blok | İçi |
|---|---|
| açılış | kalite + kadronun ilki + kıyafetleri |
| her biri kendi bloğunda | kadronun geri kalanı, kişi kişi |
| kapanış | action, kamera, mekân |

`_block` değişmiyor: bir kimlik ve kıyafetlerinin komşuluğu bu maddenin dokunmadığı kural, ve zaten
tek yerde yazılı. `BREAK.join` ve **boş bloğun düşmesi** de değişmiyor — kapanış bloğunun boş
çıkabilmesi tam olarak o kuralın var oluş sebebi.

## `lead` adı gidiyor

Değişken bugün `lead` — *önde giden*. Öndelik artık bir ayrıcalık değil: kadronun ilki ile ikincisi
aynı şekli alıyor, aralarındaki tek fark sıra. Ad `opening`'e dönüyor, çünkü o blok artık *"lideri
taşıyan"* değil, *"zinciri açan"*.

Kimin önce geldiğini yine karenin kendi yazdığı sıra söylüyor — bunu söyleyen ikinci bir alan yok,
ve olmayacak.

## Yorum yeniden yazılıyor, yamalanmıyor

Döngünün başındaki yorum bugün *"mekân, action ve kamera aralarında oturur ki iki tarif birbirine
karışmasın"* diyor. Bu cümle yarın **yanlış** olacak, ve deponun kuralı yorumun kodla çelişmesini
yasaklıyor. Yerine yazılan şey: ayırmayı `BREAK` yapıyor, mesafe onun yanında zayıf ikinci bir
önlemdi, ve bedeli action'ın erken okunmasıydı — artı kapanış bloğunun neden kimseye ait olmadığı.

## Ölçülmemiş olan ölçülmemiş kalıyor

Tek kişilik karede action'ın öznesiz bir parçada kalması bir akıl yürütme, ölçüm değil; yol
haritası da öyle kaydetti. Kod bunu bir yoruma yazıyor ve bir denemede görülecek.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 22 kırmızı kapanıyor; öteki üç takım kımıldamıyor.
