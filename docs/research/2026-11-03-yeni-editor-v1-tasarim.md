# Yeni editör — v1 mimari

Yeni editör, queen-editor'ın özelliklerini bir AI agent'ın rahatça kullanabileceği biçimde sunan
yeni bir uygulamadır. queen-editor'dan kod alınmaz; davranışı ve kuralları alınır.

## Yapı

```
Agent + MCP adaptörü ──┐
                       ├──► Core'un endpoint'leri ──► üretim, kuyruk, depo
UI ────────────────────┘
```

- **Core** yeteneklerini HTTP endpoint'leri olarak sunar. Bütün kurallar core'dadır.
- **UI** ve **agent** aynı endpoint'leri çağırır. UI'ın yapabildiği her şeyi agent da yapabilir.
- **MCP adaptörü** tek bir tool sunar; agent ona çağırmak istediği endpoint'lerin listesini verir
  (8. adım). Agent'ın yanında çalışır. Onu biz yazarız ve
  desteklenen harness'lar için ayarını biz veririz. Agent değişince core'da hiçbir şey değişmez.
- **Core'un adresini** kullanıcı her oturumda sohbette verir; agent onu sohbetin
  klasöründeki bir dosyaya yazar, adaptör oradan okur (10. adım).
- **UI** minimaldir: görmek, kare ve video silmek; ayrıntısı 9. adımda.

## Depo

Core veriye bir depo portu üzerinden ulaşır. Port projenin kayıtlarını anlatır, Drive'ın dosyalarını
değil; kalıcı silme yoktur, yalnız çöp. Böylece Drive'dan tek veritabanlı bir servise (ör.
Cloudflare D1 + R2) geçiş yalnız adaptör değişikliğidir (4. adım).

- Port bir yazmayı ancak depo kabul ettiğinde başarılı döner; depo reddederse hata, deponun kendi
  sözleriyle ekrana ulaşır.
- Testler bellek içi bir adaptörle koşar.

**Drive API adaptörü.** Drive'a mount ile değil API ile gidilir. Core Drive'a, Colab'ı açan hesabın
izniyle gider: notebook açılınca Colab'ın giriş penceresi onaylanır. Token saklanmaz. ComfyUI'nin
girdileri üretimden önce indirilir, çıktı sonra yüklenir.

## queen-editor dosyalarıyla uyum

v1, queen-editor'ın projelerini açmaz.

## Barındırma

Ayrıntısı 10. adımda.
