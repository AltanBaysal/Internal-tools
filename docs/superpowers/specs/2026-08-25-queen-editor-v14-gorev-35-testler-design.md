# v14 Görev 35 — Yazılmış ama gönderilmemiş metin geri dönüşte duruyor: TEST döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 24 Ağustos
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 35

## Sorun

Fotoğraf üret panelinin dört kutusu — model, prompt listesi, negatif prompt, varyant — açıldığında
proje kaydından bir kez dolduruluyor ve o andan sonra yazılan her şey yalnız bileşenin kendi
state'inde duruyor. Diske yalnız *Kuyruğa ekle*'ye basılınca geçiyor.

Bir kareye bakmak bütün proje ekranını değiştiriyor; React artık var olmayan bir bileşenin state'ini
atıyor. Geri dönen kullanıcı kutuda en son **gönderdiği** metni buluyor, yazdığını değil.

## Ne test ediliyor

Panel sökülüp yeniden kurulduğunda, yazılmış ama gönderilmemiş metnin kutuda durduğu. Yani madde
35'in "bitti sayılır" cümlesinin ta kendisi.

Bu döngüde **kod değişmiyor.** Testler yazılır, kırmızı görülür, kırmızı commit'lenir.

## Dört kutunun dördü birden

Ayırmak için sebep yok: hepsi tek formun parçası, hepsi aynı anda kayboluyor, ve hepsi aynı satırdan
— `useState(settings.…)` — doğuyor. Birini hatırlayıp ötekini unutmak, kullanıcının yarım kalmış
işini yarım hatırlamak olurdu.

## Deponun şekli — ve neden testin bunu bilmesi gerekiyor

Uygulama döngüsünde koşunun sekizinci deposu doğacak: modül seviyesinde, proje anahtarlı, bellekte.
Testler deponun içini hiç okumuyor — gördükleri tek şey ikinci mount'ta kutuların ne yazdığı. Ama
deponun **modül seviyesinde** duracak olması testin kurulumunu bugünden değiştiriyor.

## Bugün eksik olan: taze modül

`GeneratePanel.test.jsx` bugün dosyanın başında bir kez `import GeneratePanel` diyor. Depo modül
seviyesinde doğduğu anda, bir testin yazdığı bir sonrakinin başlangıcı olur — ve testlerin beşi
kutulara yazıyor, biri de "hiç kaydedilmemiş proje 2 ile açılır" diyor. O test, kendinden önce
çalışan birinin bıraktığı 4'ü görürdü.

Bu yüzden test dosyası, testlerin ikisi yeşile dönmeden önce bile, **test başına taze modül**
düzenine geçiyor: `vi.resetModules()` ve dinamik `import()`. Bu, `useModels`, `useProducers` (madde
32) ve `SidePanel` (madde 34) için aynı sebeple yapılanın aynısı. Bu dosyada `vi.mock` yok, dolayısıyla
`resetModules` gerçekten yeniden kuruyor ve `clearAllMocks` gerekmiyor.

**Mevcut 29 testin hiçbirinin cümlesi değişmiyor** — yalnız modülün nereden geldiği değişiyor.

## Yeni prop: `project`

Depo anahtarsız kalırsa bir projenin taslağı ötekinde çıkar. `GeneratePanel` bugün `project`
almıyor; `SidePanel` onu zaten elinde tutuyor ve komşusu `QueuePanel`'e zaten veriyor. Testler bu
prop'u bugünden geçiriyor: yardımcıya bir varsayılan eklenir, bir test de başka bir proje adıyla
çağırır.

## Yazılacak testler

Dördü de `GeneratePanel.test.jsx`'te, kendi `describe` bloğunda.

| | Test | Bugün |
|---|---|---|
| 1 | Yazılıp gönderilmeyen prompt ikinci mount'ta kutuda | **kırmızı** |
| 2 | Negatif, model ve varyant da öyle | **kırmızı** |
| 3 | Hiç yazılmamışsa kutular kayıttan doluyor | yeşil — tutucu |
| 4 | Başka bir projenin taslağı bu projede çıkmıyor | yeşil — tutucu |

Tutucuların ikisi de bugün yeşil ve yeşil kalmalı. 3'ü düşürmek, hiç yazmamış bir kullanıcıya başka
birinin metnini göstermek olur; 4'ü düşürmek, bir projenin prompt'unu ötekine taşımak.

## Kapsam dışı

- **Diske yazmak.** Kullanıcının kararı: taslak proje içinde ama kritik değil, sayfa kapanınca
  sıfırlanır. Diğer yedi depo ne kadar yaşıyorsa o kadar.
- **Katman paneli** (`LayerPanel`). Kendi kutuları var ama madde 35 fotoğraf panelini söylüyor.
- **Detay sayfasının prompt kutuları.** Orada yazı başka bir kareye geçilince ölüyor (madde 76) ve
  bu bilerek öyle: o kutular karelere ait, bu form tek bir projeye.
- **Kod.** Bu döngü yalnız test.

## Derlenmiş çıktı

Bu döngüde ön yüz **kaynağı** değişmiyor, yalnız test dosyası. `dist` tazelenmiyor.
