# v14 · Görev 18 — Fotoğraf varyant varsayılanı 4 → 2 · **test turu**

**Kaynak:** yol haritası 18. madde · İstek 8.

> *"Üretim panelinde bir prompt'tan kaç kare üretileceğinin varsayılanı 4; 2 olacak. Katman
> panelindeki varyant değişmiyor. Listedeki en küçük iş."*

## Varsayılan tek bir yerde

Aranınca çıkan tek sayı `GeneratePanel.jsx`'te:

```js
  const [variants, setVariants] = useState(
    settings.variants === null ? "4" : String(settings.variants),
  );
```

Arka uçta varsayılan **yok**: `start_batch` 1–26 arası bir tam sayı istiyor ve verilmezse
reddediyor; `settings_store` hiç kaydedilmemiş projeye `variants: null` diyor. Yani sayıyı seçen
tek yer panelin kendisi, ve değişecek olan tek satır bu.

## Verilen kararlar

### 1 · Değişen yalnız hiç kaydedilmemiş hâl

Kutu, projenin kayıtlı sayısını okuyor; varsayılan yalnız o sayı **yokken** devreye giriyor. 4 ile
kaydedilmiş bir proje 4 ile açılmaya devam ediyor — kullanıcının kendi seçimini geriye dönük
değiştirmek istenen şey değil, ve İstek 8 varsayılandan söz ediyor.

### 2 · Katman paneli sabit kalıyor

`LayerPanel` kendi kutusunu `"1"` ile açıyor ve bu maddede kımıldamıyor. İsteğin ikinci cümlesi
bunu ayrıca söylüyor, dolayısıyla bir test de ayrıca söylüyor: iki panelin varsayılanı iki ayrı
karar.

### 3 · Bayat bir yorum düzeltiliyor

`start_batch.py`'nin son yorumu *"panelin kendi '12 prompt × 4 varyant' satırı"*ndan söz ediyor. O
satır panelde artık yok — `GeneratePanel` testlerinden biri onun doğmadığını zaten ölçüyor — ve 4
de varsayılan olmaktan çıkıyor. Yorumun **neden**'i doğru (onay kartı sunucunun saydığını yazar,
panelin çarpımını değil); yanlış olan örneği. Uygulama turunda düzeltiliyor.

## Kapsam dışı

- **Kayıtlı ayarların taşınması.** Hiçbir projenin kayıtlı sayısına dokunulmuyor.
- **1–26 aralığı** ve kutunun kendi kuralları — 16. maddede ve daha öncesinde karara bağlandı.

## Yazılacak testler

### `GeneratePanel.test.jsx` — 2 yeni

| # | Ne diyor |
|---|---|
| 1 | Hiç kaydedilmemiş projede kutu 2 ile açılıyor |
| 2 | Kayıtlı bir sayı varsayılanı yeniyor |

### `LayerPanel.test.jsx` — 1 yeni

| # | Ne diyor |
|---|---|
| 3 | Katman panelinin kutusu 1 ile açılmaya devam ediyor |

**Toplam 3 yeni test: 475 → 478.**

## Doğuştan yeşil iki test

2 ve 3 bugün de geçiyor. İkisi de bu maddenin **dokunmadığı** şeyi tutuyor: biri kullanıcının
kendi kaydettiği sayıyı, öteki katman panelinin kendi varsayılanını. Bir satırlık bir değişikliğin
sızabileceği iki yer bunlar, ve sızmadığını söyleyen şey onlar.

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de **1 kırmızı** duruyor. Testler kırmızı commit
ediliyor.
