# v14 Görev 33 — Ekran bilmediğini söylemez: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** teşhis, aynı gün
**Öncesi:** [Görev 33 test spec'i](2026-08-24-queen-editor-v14-gorev-33-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 33

## Ne yeşile döndürülüyor

Üç kırmızı test: panel susar, sütun bayrağı taşır, ekran kabloyu kurar.

## İş bir kablo

Yeni bir kavram yok. `useGeneration` `known` bayrağını zaten tutuyor ve zaten döndürüyor; onu okuyan
kimse yok. Değişiklik üç dosyada birer satır ve panelde bir erken çıkış.

```
useGeneration (var)  →  ProjectScreen  →  SidePanel  →  QueuePanel
      known             (okumuyordu)     (taşımıyordu)   (sormuyordu)
```

## Panelin bilmediği hâli

Sunucu bu mount'ta konuşmadıysa panel kendi sütununda bir halka gösterir ve başka hiçbir şey
çizmez — tür kartları da, koşu kartı da, düğmeler de. 31'in fotoğraf paneline verdiği biçimin
aynısı: her panel kendi beklemesini kendi yerinde gösterir.

Erken çıkış, panelin tek hook'undan **sonra** durur. React'in kuralı: hook'lar koşulsuz koşar.

## Bayrağın varsayılanı yok

`QueuePanel` `known`'ı zorunlu alır. Varsayılan vermek — hangisi olursa olsun — unutulan bir kabloyu
sessizce kabul edilebilir bir hâle sokar, ve bu maddenin sebebi tam olarak sessizce unutulmuş bir
kablo.

## Kapsam dışı

- **Kuyruğun hatırlanması.** Durum canlı; eski bir sayı göstermek ayrı bir karar.
- **Galerinin hapları.** Borçlu bir katman ilk cevaptan önce *"bekliyor"*, sonra *"kuyrukta"*
  okunuyor. İkisi de "henüz üretilmedi" demek; aradaki fark bir söz veriş, kesin bir iddia değil.
  Düzeltmek üçüncü bir kelime tasarlamayı gerektirir ve o kelime bu koşuda kararlaştırılmadı.
- **`PhotoDetail`.** O da `useGeneration` kullanıyor ama kuyruk paneli yok; bayrağı okuyacağı bir
  yer de yok.
- **Test dosyaları değişmiyor.**

## Derlenmiş çıktı

Ön yüz kaynağı değiştiği için `dist` aynı commit'e girer.
