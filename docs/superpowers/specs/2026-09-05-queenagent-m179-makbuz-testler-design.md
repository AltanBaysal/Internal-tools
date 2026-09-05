# Madde 179 · test turu — okunan dosya istekte bir kere durur

**Kaynağı:** [yol haritası](../plans/2026-09-05-queenagent-v7-roadmap.md), Madde 179. Arşiv dalının
*"Bekleyen"*inden geldi; kullanıcı 5 Eylül'de bu koşuya aldı. Koşunun son maddesi.

---

## Madde 129'un öldürdüğü bayatlık, tur içinde hayatta

129 şunu çözmüştü: bir okumanın sonucu yazıldığı yerde donuyordu, dosya ilerliyordu, mesaj
kalıyordu — model aynı dosyayı üç kere okuyordu. Kap adı tutuyor, içeriği her istekte **diskten**
okuyor.

Ama okuma aracının cevabı hâlâ **dosyanın tamamı**, ve o cevap turun sonuna kadar konuşmada duruyor.
Yani okuma raundundan sonra her istekte **iki kopya** gidiyor:

1. konuşmadaki `tool` mesajı — okunduğu andaki hâli, donmuş
2. kaptaki blok — şimdiki hâli, taze

Model aynı turda o dosyayı düzenlerse **ikisi ayrılıyor**, ve model hangisine bakacağına karar
vermek zorunda kalıyor. 129'un kovduğu şey, tek turun içine sığınmış.

## Ne oluyor

`read_file` bir **makbuz** döndürüyor:

```
bar-scene.json, 45 lines; it is in your opened files.
```

İçeriği yalnız kap taşıyor. Kabın başlığı artık kuralı da söylüyor: *"The last 5 files you opened…"*
— düşen dosyayı yeniden okumak bir cümleye mal oluyor, ve kap kendini onarıyor.

**Okuma gecikmiyor.** Bugün de içerik bir sonraki raundda görülüyor: kap istekle birlikte kuruluyor,
araç cevabı da bir sonraki raundda okunuyor. Değişen tek şey, iki kopyanın bir olması.

## Bedeli doğru okunsun

Kaldırılan kopya **konuşmanın içinde**, yani ikinci raunddan sonra **cache'li** olan. Kap her raund
tam fiyat gitmeye devam ediyor. **Kazanç para değil, çelişkinin gitmesi** — ve damganın küçülmesi
bunun yan etkisi.

## 131 ne oluyor

Numaralı satırlar **kalıyor**, ama artık yalnız kapta. `numbered()` yerinde; testleri okuma
aracından **fonksiyonun kendisine** taşınıyor.

`test_the_box_and_a_read_show_a_file_the_same_way` — 131'in *"tek biçim"* iddiası — tek taraflı
kalıyor: gösteren tek yer var, dolayısıyla iki biçim de yok. Test bunu söyleyecek şekilde yeniden
yazılıyor.

## `SYSTEM_PROMPT`

Okuma cümlesi içeriğin **nerede belirdiğini** söylüyor. Söylemezse model bir makbuz alıp dosyayı
görmediğini sanır ve yeniden okur — düzeltilen şeyin aynısını yapar.

---

## Çivilenen vak'alar

**Araç (5):** makbuz dosyayı ve satır sayısını söylüyor · içerik cevapta yok · olmayan dosya eski
cümlesini koruyor · kartın *"3 lines"*'ı değişmiyor · `numbered()` hâlâ sağa yaslı numaralıyor.

**İstek (3):** kabın başlığı beşi söylüyor · okumadan sonraki raund dosyayı **bir** kere taşıyor ·
aynı turda düzenlenen dosya istekte yalnız yeni hâliyle var.

**Metin (1):** `SYSTEM_PROMPT` içeriğin nerede belirdiğini söylüyor.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **11 kırmızı**, hepsi `queen-agent`'ta. Sayı yazılan vak'adan yüksek: kabın başlığı değişince
   `_box` yardımcısı da değişti, ve o yardımcıya dayanan **beş eski test** birden düştü. Yeni iddia
   değil, bir başlığın peşinden gelen düşüşler.
3. Öteki üç takım rakamlarını korudu: **589 · 739 · 591.** `dist` derlenmedi.
