# Uzun hata metni ekranı kilitlemesin: TEST döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3` · **Döngü:** 1/2
**Bu döngüde kod yazılmıyor** — yalnız testler, ve takım kırmızı commit'leniyor.

## Ne oldu

2026-08-14 Colab turunda video modelleri kurulu değilken kuyruğa video işi girdi ve ComfyUI dört
düğümü birden reddetti. Motor bunu kuralı gereği ham hâliyle bastı — ~60 satır JSON. Kuyruk paneli
`overflow: hidden`, hata bloğunun ise tavanı yok; metin *"Kaldığı yerden devam et"* ve *"Kuyruğu
boşalt"* düğmelerini panelin dışına itti ve oraya kaydırılamadı. Yani kullanıcı ne devam edebildi ne
kuyruğu boşaltabildi.

Aynı sınırsızlık `StatusErrorCard`'da da var ve o uygulama geneli — bugün kilitlemedi diye yarın
kilitlemeyeceği anlamına gelmiyor.

## Ham metin kısaltılmıyor

Repo kuralı: *"hata mesajında sebep uydurma, komutun ya da servisin gerçek çıktısını bas."* Bu
görev o kuralı bozmuyor. Metin **katlanıyor**, silinmiyor: tamamı ekranda duruyor, yalnız kendi
kutusunun içinde kayıyor ve tek tuşla panoya alınabiliyor.

## Hangi davranış doğru sayılacak

**Ham çıktı kendi kutusunda durur.** Sabit tavanlı (~5 satır), kendi içinde dikey kayan, mono bir
kutu. Kutunun boyu metnin uzunluğundan bağımsız — kart ne kadar uzun hata alırsa alsın aynı yeri
kaplar.

**Kutunun altında Kopyala vardır.** Kopyalanan şey kutunun gösterdiği metnin aynısı. Basınca düğme
kısa süre *"Kopyalandı"* der.

**Pano reddederse sessiz kalınmaz.** Tarayıcı izni vermezse ya da pano yoksa düğme *"Kopyalanamadı"*
der. Sessizce yutmak, kullanıcıya kopyaladığını sanmasına yol açardı; metin kutuda seçilebilir
durduğu için elle almak hâlâ mümkün.

**Kuralın kendi cümlesi kutunun dışında kalır.** Motorun yazdığı hata iki parça: önce kuralın
cümlesi (*"Aynı kare 3 kez denendi — üretim durduruldu"*), sonra servisin çıktısı. Cümle normal bir
satır olarak durur, kutuya yalnız çıktı girer — okunacak olan cümle, katlanacak olan çıktı.

**Panel de taşınca kayar.** Yan panel bugün `overflow: hidden`; içerik sığmazsa dikey kayacak.
Yatay kayma yok — madde 107 pencerenin yana kaymamasını şart koşuyor.

**Tek parça, iki kullanıcı.** Kutuyu çizen ortak bir bileşen yazılır; kuyruk panelinin "Üretim
durdu" kartı ve `StatusErrorCard` onu kullanır. Aynı hata iki yerde iki türlü davranmaz.

## jsdom'un söyleyemeyeceği

jsdom kaydırma yapmaz: bir kutunun gerçekten kaydığını sınayamayız. Sınanabilen şey, kutunun
kaydıracak kuralı taşıdığıdır (`maxHeight` + `overflowY`). v12'nin sürükleme dersi tam da buydu ve
bu spec onu saklamıyor: **"kayıyor mu" sorusunun cevabı Colab turundadır.** Testlerin işi, kuralın
yerinde olduğunu ve bir daha sessizce kaybolmayacağını garanti etmek.

## Yazılacak testler

### `shared/RawOutput.test.jsx` — yeni dosya, kutunun kendisi

1. **Uzun çıktı kendi kutusunda kalıyor.** Yüz satırlık metin verilir; kutu `overflowY: auto` ve bir
   `maxHeight` taşır.
2. **Kopyala, gösterdiğinin aynısını panoya yazıyor.** Pano taklit edilir; düğmeye basılınca
   `writeText` kutunun metniyle çağrılır.
3. **Kopyalanınca söylüyor.** Basıştan sonra düğme *"Kopyalandı"* der.
4. **Pano reddederse söylüyor.** `writeText` reddedince düğme *"Kopyalanamadı"* der.

### `features/photo_generation/QueuePanel.test.jsx` — durdu kartı

5. **Uzun hata düğmeleri kaçırmıyor.** Duran bir koşu, 60 satırlık `job.error` ve bekleyen iş ile
   çizilir; ham çıktı kutuda, *"Kuyruğu boşalt"* ve *"Kaldığı yerden devam et"* hâlâ belgede.
6. **Kuralın cümlesi kutunun dışında.** İlk satır düz metin olarak görünür; kutu yalnız ondan
   sonrasını tutar.

### `shared/StatusErrorCard.test.jsx` — yeni dosya, ortak kart

7. **O da aynı kutuyu kullanıyor.** `raw` verilen kart, ham metni kutunun içinde çizer.

## Kırmızı ne olacak

Yedisi de geçmiyor ama ikisi iki ayrı şekilde:

- **1–4 hiç koşmuyor.** `RawOutput.jsx` yok, dolayısıyla `RawOutput.test.jsx` yüklenemiyor; vitest
  onu **düşen dosya** olarak raporluyor ve içindeki dört test toplanmadığı için sayıya bile
  girmiyor.
- **5–7 koşuyor ve düşüyor.** Üçü de bugünkü sınırsız bloğa bakıp kutu arıyor ve bulamıyor.

Yani takım "3 düşen test + 1 yüklenemeyen dosya" diyecek, "7 düşen" değil. Commit mesajı bunu
olduğu gibi söyler — sayı şişirmek, sonradan yeşile dönen şeyin ne olduğunu bulanıklaştırır.

## Kapsam dışı

- **"Video üreticisi kurulu değil" tek cümlesi.** Asıl çözüm o: uygulama diski okuyup üreticinin
  eksik olduğunu biliyor, ve motorun tam bu durum için bir `waiting` hâli var; ikisi bağlanırsa
  kullanıcı 60 satır JSON yerine tek cümle görür ve kuyruk durmaz, bekler. Ayrı iş, ayrı koşu.
- **Hatanın nasıl üretildiği.** `policy` ve `run_loop` değişmiyor.
- **Kesme/kısaltma.** Ham metin olduğu gibi duruyor.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` üç düşen test ve bir yüklenemeyen dosya veriyor, hepsi
ham çıktının kutusuyla ilgili; geri kalan takım yeşil. Commit kırmızı gidiyor ve mesajı bunu
söylüyor.
