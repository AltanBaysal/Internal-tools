# Madde 177 · test turu — besteci iki satır

**Kaynağı:** [yol haritası](../plans/2026-09-05-queenagent-v7-roadmap.md), Madde 177. Dilim 3'ün
ilk maddesi, ve koşunun ön yüze dokunan tek yeri.

Bu tur **yalnız testleri** yazıyor ve kırmızı commit'liyor. `dist` derlenmiyor — kaynak
değişmiyor.

---

## Ne oluyor

Menüde üç satır var: **Grok Build**, **DeepSeek Flash**, **DeepSeek Pro**. İkiye iniyor:

| id | Menüde görünen |
|---|---|
| `deepseek-v4-flash` | **Queen Flash** *(varsayılan)* |
| `deepseek-v4-pro` | **Queen Pro** |

Grok satırı gidiyor. Kullanıcının kararı: *"Grok bir seçenek değil, config.py'de bir rol."* 175 onu
oraya koydu; burada listeden çıkıyor.

## Adlar yalnız arayüzde

`config.MODELS`'in anahtarı **sağlayıcıya giden addır** — `client.py` `payload = {"model":
self._model, ...}` diye gönderiyor. Yani `deepseek-v4-flash` kalmak zorunda; değişen tek şey
`models.js`'in o id'nin yanına yazdığı ad.

Kullanıcının kararı: *"sadece UI'da Queen Pro veya Queen Flash yazması yeter, gerisi senin işin."*

`config.MODELS`'in Grok satırı da **kalıyor** — 175 onu kullanıyor, ve bir satırın menüde olmaması
ile bağlanmamış olması iki ayrı şey.

## Varsayılan iki yerde birden

`models.js`'in `DEFAULT_MODEL`'i **ve** `config.py`'ninki `deepseek-v4-flash` oluyor. İkisi ayrı
sorulara cevap veriyor — biri boş bir düğmenin ne yazacağına, öteki modelsiz bir kaydın hangi
adrese gideceğine — ama ikisinin de cevabı aynı olmalı, yoksa ekranda Flash yazarken istek Grok'a
giderdi.

## Eskiden Grok seçilmiş bir mesaj

`modelName` bugün zaten doğru şeyi yapıyor: bilinmeyen id kendini söylüyor. Grok satırı listeden
çıkınca eski bir mesajın düğmesi *"grok-build-0.1"* yazacak — bir ad değil bir kimlik, ve **bu
doğru:** o mesaj gerçekten onunla cevaplandı, ve uydurulmuş bir ad kaydı yanlış okurdu. Madde 72'nin
düşen beş modeli için konmuş kural, ilk kez gerçek bir kayda uğruyor.

## Dokunulan testler

`models.test.js` *(üç satır, adlar, varsayılan, iki `modelName`)*, `ModelPicker.test.jsx`
*(`grok-build-0.1` ile kurulan beş test)*, `ChatScreen.test.jsx`, `ProjectScreen.test.jsx`,
`App.test.jsx` *(besteci ayağının metnini birebir ölçen testler)*, ve `test_config.py`'nin
varsayılanı.

`Composer.test.jsx` ve `Menu.test.jsx` **dokunulmuyor:** oradaki *"Grok 4.5"* bir model değil, bir
düğme metni örneği — o testler bir modelin adını değil, bir ayağın nasıl çizildiğini ölçüyor.

---

## Çivilenen vak'alar

**`models.js` (6):** iki satır · adlar ve fiyatlar · varsayılan Flash · bilinen id adını söylüyor ·
boş id varsayılanın adını · **yalnız rol olan model kendi kimliğini söylüyor.**

**Ön yüz (5):** düğme Queen Flash yazıyor · menü iki satır listeliyor · seçili satır işaretli ·
seçim id'yi geçiriyor · besteci ayağının metni.

**Arka uç (2):** `config.DEFAULT_MODEL` Flash · modelsiz kayıt Flash'a düşüyor. Ve **bir yasak:**
`config.MODELS`'in Grok satırı yerinde duruyor.

## Kod da bir şey öğreniyor: işaretin düğmeyle anlaşması

`ModelPicker`'ın bugünkü satırı `MODELS.find(...)?.id ?? DEFAULT_MODEL` — tanımadığı bir id'yi
varsayılana çeviriyor. Bugüne kadar bunun görülebileceği bir durum yoktu; **Grok listeden çıkınca
oluyor:** düğme *"grok-build-0.1"* yazarken menü Queen Flash'ı işaretlerdi, ve kullanıcı bu sohbetin
onunla cevaplandığını sanırdı.

Modülün kendi ilkesi zaten *"işaret ile düğme aynı şeyi söylemeli"*. Satır `model || DEFAULT_MODEL`
oluyor: boş id varsayılanı işaretliyor, tanınmayan id hiçbir şeyi.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **30 kırmızı:** 28'i `queen-agent/frontend`, 2'si `queen-agent`. Öteki iki takım rakamlarını
   korudu: **739 · 591.**
3. `dist` **derlenmiyor** — bu tur kaynağa dokunmuyor. Uygulama turunda aynı commit'te derleniyor.
