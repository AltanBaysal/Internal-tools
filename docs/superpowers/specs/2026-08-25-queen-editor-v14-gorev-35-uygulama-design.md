# v14 Görev 35 — Yazılmış ama gönderilmemiş metin geri dönüşte duruyor: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 24 Ağustos
**Öncesi:** [Görev 35 test spec'i](2026-08-25-queen-editor-v14-gorev-35-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 35

## Ne yeşile döndürülüyor

İki kırmızı test: yazılıp gönderilmemiş prompt ikinci mount'ta kutuda, ve aynı şey negatif, model,
varyant için de. Yanlarındaki iki tutucu yeşil kalmalı: hiç yazılmamışsa kutular kayıttan doluyor, ve
bir projenin taslağı ötekinde çıkmıyor.

## Değişikliğin şekli

Bugün dört kutu doğrudan kayıttan tohumlanıyor:

```jsx
const [prompts, setPrompts] = useState(settings.prompts);
```

Yarın aynı dört satır tek bir kaynaktan tohumlanıyor: o projenin taslağı varsa taslaktan, yoksa
kayıttan. Taslak modül seviyesinde, proje anahtarlı bir `Map`'te duruyor — koşunun **sekizinci**
deposu, kalıbı diğer yedisiyle aynı.

## Neden taslak kaydı yeniyor

İkisi arasında seçim gerektiğinde taslak kazanır: diske ulaşmamış olan odur, yani ikisinden yeni
olan. Kayıt yalnız *Kuyruğa ekle*'ye basılınca yazılıyor, ve taslak tam olarak o basıştan sonra
yazılmış olan şey demek.

## Tek okuma, dört kutu

Depo render sırasında dört kez sorulmuyor. Bir kez, mount'ta, tembel bir `useState` içinde
soruluyor; dört kutu o cevabın dört alanından doğuyor. Modül seviyesindeki bir depoyu her render'da
okumak, render'ı saf olmaktan çıkarırdı.

Normalleştirme de o tek yerde: `settings.model` boş olabiliyor ve `settings.variants` `null`
olabiliyor — kutular ise metin taşıyor. Bugün bu dönüşüm dört `useState` satırına dağılmış durumda;
taşındıktan sonra tek fonksiyonda toplanıyor ve davranışı değişmiyor.

## Yazan taraf: tek effect

Dört kutunun değeri değiştikçe taslak yazılıyor — dört setter'ın içinde değil, tek bir effect'te.
Sebebi: model kutusunun bir yazarı daha var. Renderer'ın listesi gelince boş model kutusu kendini
listenin ilkiyle dolduruyor (mevcut effect). Yazmayı setter'lara dağıtmak, unutulabilecek beş yer
demek olurdu.

Effect mount'ta da bir kez yazıyor. Zararsız: o an taslak, kutuların kayıttan aldığı değerin
aynısı.

## Gönderdikten sonra taslak silinmiyor

*Kuyruğa ekle* kaydı diske yazıyor ama panel sökülmüyor, ve o an taslak ile kayıt aynı metni
taşıyor. Silinecek bir fark yok.

## Yeni prop: `project`

`GeneratePanel` bugün `project` almıyor. Anahtarsız bir depo, bir projenin yarım prompt'unu ötekinde
gösterirdi. `SidePanel` bu değeri zaten elinde tutuyor ve komşusu `QueuePanel`'e zaten veriyor;
`GeneratePanel`'i çizen tek yer de o. Yani tek satırlık bir ekleme.

## Ömür

Bellekte. Sayfa yenilenince kutular yine kayıttan doluyor — diğer yedi depo ne kadar yaşıyorsa o
kadar. Kullanıcının kararı: taslak proje içinde ama kritik değil.

## Bilerek yapılmayan: proje değişimi koruması

`useProjectSettings` ve `useGeneration` bir `shownProject` ref'i taşıyor; buraya eşi eklenmiyor —
madde 34'teki gerekçenin aynısı. İki proje arasında geçmenin tek yolu proje listesinden geçmek, ve o
ekran `ProjectRoute`'u, dolayısıyla `SidePanel`'i ve bu paneli söküyor. Panel iki proje arasında hiç
ayakta kalmıyor. Onların ref'i taşımasının sebebi yanlış kaydı gösterip sonra yanlış projeye
kaydetmekti; burada en kötü ihtimal bayat bir taslak.

## Kapsam dışı

- **Test dosyası değişmiyor.** Bir önceki commit'te ne yazıldıysa o kalır.
- **Katman paneli** (`LayerPanel`) ve **detay sayfasının prompt kutuları** — gerekçeleri test
  spec'inde.

## Derlenmiş çıktı

Ön yüz kaynağı değiştiği için `dist` aynı commit'e girer (CLAUDE.md). Defter derlemiyor; itilmemiş
bir `dist` Colab'da görünmez.
